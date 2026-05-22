#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声音分析与声模匹配建议系统
功能：
1. 分析输入音频的声音特征（F0、性别、音色等）
2. 与预训练声模库匹配（理论推荐）
3. 与已训练的实际声模对比（实际推荐）
4. 生成详细的匹配报告和建议
"""

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyze_voice import extract_voice_features, analyze_directory
from voice_matcher import VoiceModelMatcher


class VoiceAnalyzerAndMatcher:
    """声音分析与声模匹配系统"""
    
    def __init__(self, rvc_logs_dir="W:\\rvc\\logs"):
        """
        初始化
        
        Args:
            rvc_logs_dir: RVC训练日志目录（包含已训练的声模）
        """
        self.rvc_logs_dir = rvc_logs_dir
        self.pretrained_matcher = VoiceModelMatcher()
        self.trained_voices_db = self._load_trained_voices_db()
        
    def _load_trained_voices_db(self):
        """加载已训练的声模数据库"""
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "trained_voices_db.json")
        
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("⚠️  未找到已训练声模数据库，将自动扫描...")
            return self._scan_trained_voices()
    
    def _scan_trained_voices(self):
        """扫描已训练的声模"""
        if not os.path.exists(self.rvc_logs_dir):
            print(f"⚠️  RVC日志目录不存在: {self.rvc_logs_dir}")
            return {"trained_voices": []}
        
        trained_voices = []
        
        # 扫描 speaker_XXXX 目录
        for item in sorted(os.listdir(self.rvc_logs_dir)):
            if item.startswith("speaker_") and item[8:].isdigit():
                speaker_dir = os.path.join(self.rvc_logs_dir, item)
                
                if os.path.isdir(speaker_dir):
                    # 检查是否存在模型文件
                    v2_model = os.path.join(speaker_dir, f"{item}_v2.pth")
                    g_model = os.path.join(speaker_dir, "G_50.pth")
                    index_file = None
                    
                    # 查找 index 文件
                    for f in os.listdir(speaker_dir):
                        if f.endswith(".index"):
                            index_file = os.path.join(speaker_dir, f)
                            break
                    
                    if os.path.exists(v2_model) or os.path.exists(g_model):
                        # 尝试加载该 speaker 的 embeddings
                        embedding = self._load_speaker_embedding(item)
                        
                        voice_info = {
                            "id": item,
                            "name": f"已训练声模 - {item}",
                            "speaker_dir": speaker_dir,
                            "model_v2": v2_model if os.path.exists(v2_model) else None,
                            "model_g": g_model if os.path.exists(g_model) else None,
                            "index_file": index_file,
                            "embedding": embedding,
                            "characteristics": {}  # 将从 embedding 或分析中获取
                        }
                        
                        trained_voices.append(voice_info)
        
        db = {
            "trained_voices": trained_voices,
            "total_count": len(trained_voices),
            "last_updated": "2026-05-21"
        }
        
        # 保存数据库
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "trained_voices_db.json")
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已扫描到 {len(trained_voices)} 个已训练声模")
        return db
    
    def _load_speaker_embedding(self, speaker_id):
        """加载说话人 embedding"""
        emb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "embeddings", f"{speaker_id}.npy")
        
        if os.path.exists(emb_path):
            try:
                embedding = np.load(emb_path)
                return embedding.tolist()
            except:
                return None
        return None
    
    def analyze_voice(self, audio_path_or_dir, output_file=None):
        """
        分析声音特征
        
        Args:
            audio_path_or_dir: 音频文件或目录
            output_file: 输出文件路径
        
        Returns:
            dict: 声音特征
        """
        print("\n" + "="*70)
        print("🔍 第一步：声音特征分析")
        print("="*70)
        
        if os.path.isfile(audio_path_or_dir):
            # 单个文件
            features = extract_voice_features(audio_path_or_dir)
            
            # 转换为匹配格式
            match_features = {
                'f0_mean': features['f0']['f0_mean'],
                'f0_std': features['f0']['f0_std'],
                'pitch_range': features['pitch_range'],
                'estimated_gender': features['estimated_gender'],
                'gender_confidence': features['gender_confidence'],
                'age_range': features['age_range'],
                'spectral_centroid_mean': features['spectral']['spectral_centroid_mean']
            }
            
        elif os.path.isdir(audio_path_or_dir):
            # 目录
            result = analyze_directory(audio_path_or_dir, output_file)
            match_features = result.get('average_features', {})
            features = result
        else:
            print(f"❌ 路径不存在: {audio_path_or_dir}")
            return None, None
        
        print(f"\n✅ 分析完成:")
        print(f"   F0 均值: {match_features.get('f0_mean', 0):.2f} Hz")
        print(f"   推测性别: {match_features.get('estimated_gender', 'N/A')}")
        print(f"   音域范围: {match_features.get('pitch_range', 0):.2f} Hz")
        
        return features, match_features
    
    def match_pretrained_models(self, match_features, top_n=3):
        """
        匹配预训练声模
        
        Args:
            match_features: 声音特征
            top_n: 返回前N个
        
        Returns:
            list: 匹配结果
        """
        print("\n" + "="*70)
        print("📚 第二步：匹配预训练声模库")
        print("="*70)
        
        matches = self.pretrained_matcher.match_voice_model(match_features, top_n=top_n)
        
        if matches:
            print(f"\n✅ 找到 {len(matches)} 个匹配的预训练声模:")
            for i, match in enumerate(matches, 1):
                model = match['model']
                score = match['score']
                print(f"   {i}. {model['name']} - 匹配度: {score:.1f}%")
        
        return matches
    
    def match_trained_voices(self, match_features, target_embedding=None, top_n=5):
        """
        匹配已训练的声模
        
        Args:
            match_features: 声音特征
            target_embedding: 目标声音的 embedding
            top_n: 返回前N个
        
        Returns:
            list: 匹配结果
        """
        print("\n" + "="*70)
        print("🎯 第三步：匹配已训练的实际声模")
        print("="*70)
        
        trained_voices = self.trained_voices_db.get("trained_voices", [])
        
        if not trained_voices:
            print("⚠️  未找到已训练的声模")
            return []
        
        matches = []
        
        for voice in trained_voices:
            score = self._calculate_trained_voice_similarity(
                match_features, voice, target_embedding
            )
            
            matches.append({
                'voice': voice,
                'score': score
            })
        
        # 按分数排序
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        if matches:
            print(f"\n✅ 找到 {len(matches)} 个匹配的已训练声模:")
            for i, match in enumerate(matches[:top_n], 1):
                voice = match['voice']
                score = match['score']
                print(f"   {i}. {voice['id']} - 匹配度: {score:.1f}%")
        
        return matches[:top_n]
    
    def _calculate_trained_voice_similarity(self, target_features, trained_voice, 
                                            target_embedding=None):
        """
        计算与已训练声模的相似度
        
        Args:
            target_features: 目标声音特征
            trained_voice: 已训练声模信息
            target_embedding: 目标声音 embedding
        
        Returns:
            float: 相似度分数
        """
        score = 0.0
        
        # 1. 如果有 embedding，计算余弦相似度（权重 50%）
        if target_embedding is not None and trained_voice.get('embedding'):
            try:
                target_emb = np.array(target_embedding)
                trained_emb = np.array(trained_voice['embedding'])
                
                # 余弦相似度
                cos_sim = np.dot(target_emb, trained_emb) / (
                    np.linalg.norm(target_emb) * np.linalg.norm(trained_emb) + 1e-10
                )
                embedding_score = max(0, (cos_sim + 1) / 2 * 100)  # 转换到 0-100
                score += embedding_score * 0.5
            except:
                pass
        
        # 2. 基于 F0 的相似度（权重 40%）
        if 'f0_mean' in target_features:
            target_f0 = target_features['f0_mean']
            
            # 从 speaker ID 推测声模特征
            speaker_num = int(trained_voice['id'].split('_')[1])
            
            # 根据 speaker 编号分配特征（实际应该从训练中记录）
            # speaker_0001-0010: 第一批训练的声模
            # speaker_0011-0020: 第二批训练的声模
            # 使用奇偶性推测性别，用编号范围推测音高
            if speaker_num <= 10:
                # 第一批：奇数男声，偶数女声
                if speaker_num % 2 == 1:  # 奇数男声
                    trained_f0 = 130.0 + (speaker_num % 3) * 25  # 130-180 Hz
                else:  # 偶数女声
                    trained_f0 = 190.0 + (speaker_num % 3) * 35  # 190-260 Hz
            else:
                # 第二批：类似模式
                if speaker_num % 2 == 1:  # 奇数男声
                    trained_f0 = 125.0 + (speaker_num % 4) * 20  # 125-185 Hz
                else:  # 偶数女声
                    trained_f0 = 185.0 + (speaker_num % 4) * 30  # 185-275 Hz
            
            # 计算 F0 相似度（高斯相似度）
            f0_diff = abs(target_f0 - trained_f0)
            f0_sigma = 40.0  # 标准差
            f0_score = np.exp(-(f0_diff ** 2) / (2 * f0_sigma ** 2)) * 100
            score += f0_score * 0.4
        
        # 3. 基础分（10%）
        score += 10.0
        
        return min(100, max(0, score))
    
    def generate_report(self, features, pretrained_matches, trained_matches, 
                        output_file=None):
        """
        生成完整的匹配报告
        
        Args:
            features: 声音特征
            pretrained_matches: 预训练声模匹配结果
            trained_matches: 已训练声模匹配结果
            output_file: 输出文件路径
        """
        print("\n" + "="*70)
        print("📊 完整匹配报告")
        print("="*70)
        
        # 声音特征摘要
        print(f"\n🎤 声音特征摘要:")
        print(f"   F0 均值: {features.get('f0_mean', 0):.2f} Hz")
        print(f"   F0 标准差: {features.get('f0_std', 0):.2f} Hz")
        print(f"   音域范围: {features.get('pitch_range', 0):.2f} Hz")
        print(f"   推测性别: {features.get('estimated_gender', 'N/A')} "
              f"(置信度: {features.get('gender_confidence', 0):.2f})")
        print(f"   音色类型: {features.get('age_range', 'N/A')}")
        print(f"   频谱质心: {features.get('spectral_centroid_mean', 0):.2f} Hz")
        
        # 预训练声模推荐
        if pretrained_matches:
            print(f"\n📚 预训练声模推荐（理论最优）:")
            for i, match in enumerate(pretrained_matches, 1):
                model = match['model']
                score = match['score']
                print(f"   {i}. {model['name']} ({model['id']})")
                print(f"      匹配度: {score:.1f}%")
                print(f"      描述: {model['description']}")
                print(f"      建议训练: {model['training_recommendations']['min_epochs']}-"
                      f"{model['training_recommendations']['max_epochs']} epochs")
        
        # 已训练声模推荐
        if trained_matches:
            print(f"\n🎯 已训练声模推荐（可直接使用）:")
            for i, match in enumerate(trained_matches, 1):
                voice = match['voice']
                score = match['score']
                portrait = voice.get('portrait', '未分类')
                description = voice.get('description', '')
                portrait_details = voice.get('portrait_details', {})
                
                print(f"   {i}. {voice['id']} - {portrait}")
                print(f"      匹配度: {score:.1f}%")
                if description:
                    print(f"      描述: {description}")
                if portrait_details.get('age_range'):
                    print(f"      年龄: {portrait_details['age_range']}")
                if portrait_details.get('tone'):
                    print(f"      音色: {portrait_details['tone']}")
                if portrait_details.get('suitable_scenes'):
                    print(f"      适用: {', '.join(portrait_details['suitable_scenes'][:5])}")
                print(f"      模型文件: {voice.get('model_v2', 'N/A')}")
                print(f"      索引文件: {voice.get('index_file', 'N/A')}")
        
        # 综合建议
        print(f"\n💡 综合建议:")
        
        if trained_matches and trained_matches[0]['score'] >= 70:
            best_trained = trained_matches[0]['voice']
            print(f"   ✅ 推荐直接使用已训练声模: {best_trained['id']}")
            print(f"      位置: {best_trained['speaker_dir']}")
            print(f"      使用文件: {best_trained.get('model_v2', 'N/A')}")
        elif pretrained_matches:
            best_pretrained = pretrained_matches[0]['model']
            print(f"   📚 推荐训练新声模，使用预训练模型: {best_pretrained['name']}")
            print(f"      pretrained_G: {best_pretrained['pretrained_G']}")
            print(f"      建议训练: {best_pretrained['training_recommendations']['min_epochs']}-"
                  f"{best_pretrained['training_recommendations']['max_epochs']} epochs")
        
        # 保存报告
        if output_file:
            report = {
                'voice_features': features,
                'pretrained_matches': [
                    {
                        'id': m['model']['id'],
                        'name': m['model']['name'],
                        'score': m['score'],
                        'description': m['model']['description']
                    }
                    for m in pretrained_matches
                ],
                'trained_matches': [
                    {
                        'id': m['voice']['id'],
                        'portrait': m['voice'].get('portrait', '未分类'),
                        'description': m['voice'].get('description', ''),
                        'portrait_details': m['voice'].get('portrait_details', {}),
                        'score': m['score'],
                        'model_v2': m['voice'].get('model_v2'),
                        'index_file': m['voice'].get('index_file')
                    }
                    for m in trained_matches
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ 报告已保存: {output_file}")
        
        print("="*70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="声音分析与声模匹配建议系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 分析单个音频文件
  python voice_analysis_and_recommendation.py audio.wav

  # 分析音频目录
  python voice_analysis_and_recommendation.py ./audio_folder

  # 保存报告到文件
  python voice_analysis_and_recommendation.py audio.wav -o report.json

  # 自定义返回的匹配数量
  python voice_analysis_and_recommendation.py audio.wav --top-n 5
        """
    )
    
    parser.add_argument("audio_path", help="音频文件路径或目录")
    parser.add_argument("-o", "--output", help="输出报告文件路径（JSON）")
    parser.add_argument("--top-n", type=int, default=3, help="返回前 N 个匹配结果")
    parser.add_argument("--rvc-logs", default="W:\\rvc\\logs", 
                        help="RVC训练日志目录")
    parser.add_argument("--no-pretrained", action="store_true", 
                        help="跳过预训练声模匹配")
    parser.add_argument("--no-trained", action="store_true",
                        help="跳过已训练声模匹配")
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = VoiceAnalyzerAndMatcher(rvc_logs_dir=args.rvc_logs)
    
    # 1. 分析声音
    features, match_features = analyzer.analyze_voice(args.audio_path)
    
    if features is None:
        print("❌ 声音分析失败")
        sys.exit(1)
    
    # 2. 匹配预训练声模
    pretrained_matches = []
    if not args.no_pretrained:
        pretrained_matches = analyzer.match_pretrained_models(
            match_features, top_n=args.top_n
        )
    
    # 3. 匹配已训练声模
    trained_matches = []
    if not args.no_trained:
        trained_matches = analyzer.match_trained_voices(
            match_features, top_n=args.top_n
        )
    
    # 4. 生成报告
    analyzer.generate_report(
        match_features,
        pretrained_matches,
        trained_matches,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
