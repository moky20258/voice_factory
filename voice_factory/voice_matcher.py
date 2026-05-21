#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声模匹配引擎
根据目标声音特征，匹配最合适的预训练声模
"""

import os
import sys
import json
import numpy as np


class VoiceModelMatcher:
    """声模匹配器"""
    
    def __init__(self, db_path=None):
        """
        初始化匹配器
        
        Args:
            db_path: 声模数据库路径
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_models_db.json")
        
        self.db_path = db_path
        self.voice_models = []
        self.matching_weights = {}
        
        # 加载数据库
        self._load_database()
    
    def _load_database(self):
        """加载声模数据库"""
        if not os.path.exists(self.db_path):
            print(f"❌ 声模数据库不存在: {self.db_path}")
            return
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.voice_models = data.get('voice_models', [])
        self.matching_weights = data.get('matching_weights', {})
        
        print(f"✅ 已加载 {len(self.voice_models)} 个预训练声模")
    
    def match_voice_model(self, target_features, top_n=3):
        """
        匹配最合适的声模
        
        Args:
            target_features: 目标声音特征（来自 analyze_voice.py）
            top_n: 返回前 N 个匹配结果
        
        Returns:
            list: 匹配的声模列表（按匹配度排序）
        """
        if not self.voice_models:
            print("❌ 声模数据库为空")
            return []
        
        # 计算每个声模的匹配度
        matches = []
        
        for model in self.voice_models:
            score = self._calculate_similarity(target_features, model)
            matches.append({
                'model': model,
                'score': score,
                'match_details': self._get_match_details(target_features, model)
            })
        
        # 按分数排序
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:top_n]
    
    def _calculate_similarity(self, target_features, model):
        """
        计算目标声音与声模的相似度（0-100）
        
        Args:
            target_features: 目标声音特征
            model: 声模信息
        
        Returns:
            float: 相似度分数
        """
        weights = self.matching_weights
        total_score = 0.0
        total_weight = 0.0
        
        # 1. F0 均值匹配（权重 40%）
        if 'f0_mean' in weights and weights['f0_mean'] > 0:
            f0_score = self._calculate_f0_similarity(
                target_features.get('f0_mean', 150),
                model['voice_characteristics']['f0_mean']
            )
            total_score += f0_score * weights['f0_mean']
            total_weight += weights['f0_mean']
        
        # 2. F0 范围匹配（权重 20%）
        if 'f0_range' in weights and weights['f0_range'] > 0:
            range_score = self._calculate_range_similarity(
                target_features.get('pitch_range', 150),
                model['voice_characteristics']['f0_range_max'] - model['voice_characteristics']['f0_range_min']
            )
            total_score += range_score * weights['f0_range']
            total_weight += weights['f0_range']
        
        # 3. 性别匹配（权重 15%）
        if 'gender' in weights and weights['gender'] > 0:
            gender_score = self._calculate_gender_similarity(
                target_features.get('estimated_gender', 'unknown'),
                model['voice_characteristics']['gender']
            )
            total_score += gender_score * weights['gender']
            total_weight += weights['gender']
        
        # 4. 频谱质心匹配（权重 15%）
        if 'spectral_centroid' in weights and weights['spectral_centroid'] > 0:
            spectral_score = self._calculate_spectral_similarity(
                target_features.get('spectral_centroid_mean', 1500),
                model['voice_characteristics']['spectral_centroid_mean']
            )
            total_score += spectral_score * weights['spectral_centroid']
            total_weight += weights['spectral_centroid']
        
        # 5. 音色类型匹配（权重 10%）
        if 'voice_type' in weights and weights['voice_type'] > 0:
            voice_type_score = self._calculate_voice_type_similarity(
                target_features.get('age_range', 'unknown'),
                model['voice_characteristics']['age_range']
            )
            total_score += voice_type_score * weights['voice_type']
            total_weight += weights['voice_type']
        
        # 归一化
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0
    
    def _calculate_f0_similarity(self, target_f0, model_f0):
        """
        计算 F0 相似度
        
        Args:
            target_f0: 目标 F0 均值
            model_f0: 声模 F0 均值
        
        Returns:
            float: 相似度（0-100）
        """
        # 使用高斯相似度
        diff = abs(target_f0 - model_f0)
        sigma = 50.0  # 标准差
        
        similarity = np.exp(-(diff ** 2) / (2 * sigma ** 2)) * 100
        
        return max(0, min(100, similarity))
    
    def _calculate_range_similarity(self, target_range, model_range):
        """
        计算音域范围相似度
        
        Args:
            target_range: 目标音域
            model_range: 声模音域
        
        Returns:
            float: 相似度（0-100）
        """
        diff = abs(target_range - model_range)
        sigma = 100.0
        
        similarity = np.exp(-(diff ** 2) / (2 * sigma ** 2)) * 100
        
        return max(0, min(100, similarity))
    
    def _calculate_gender_similarity(self, target_gender, model_gender):
        """
        计算性别相似度
        
        Args:
            target_gender: 目标性别
            model_gender: 声模性别
        
        Returns:
            float: 相似度（0-100）
        """
        if target_gender == model_gender:
            return 100.0
        else:
            return 20.0  # 性别不同但仍可训练，只是匹配度低
    
    def _calculate_spectral_similarity(self, target_spectral, model_spectral):
        """
        计算频谱质心相似度
        
        Args:
            target_spectral: 目标频谱质心
            model_spectral: 声模频谱质心
        
        Returns:
            float: 相似度（0-100）
        """
        diff = abs(target_spectral - model_spectral)
        sigma = 500.0
        
        similarity = np.exp(-(diff ** 2) / (2 * sigma ** 2)) * 100
        
        return max(0, min(100, similarity))
    
    def _calculate_voice_type_similarity(self, target_type, model_type):
        """
        计算音色类型相似度
        
        Args:
            target_type: 目标音色类型
            model_type: 声模音色类型
        
        Returns:
            float: 相似度（0-100）
        """
        # 简单的类型映射
        type_hierarchy = {
            'adult_deep': ['adult_deep', 'adult_normal'],
            'adult_normal': ['adult_normal', 'adult_deep', 'adult_high'],
            'adult_high': ['adult_high', 'adult_normal', 'female_normal'],
            'female_normal': ['female_normal', 'adult_high', 'female_high'],
            'female_high': ['female_high', 'female_normal']
        }
        
        if target_type == model_type:
            return 100.0
        elif model_type in type_hierarchy.get(target_type, []):
            return 70.0
        else:
            return 30.0
    
    def _get_match_details(self, target_features, model):
        """
        获取匹配详情
        
        Args:
            target_features: 目标声音特征
            model: 声模信息
        
        Returns:
            dict: 匹配详情
        """
        details = {}
        
        # F0 对比
        target_f0 = target_features.get('f0_mean', 150)
        model_f0 = model['voice_characteristics']['f0_mean']
        f0_diff = target_f0 - model_f0
        
        details['f0'] = {
            'target': target_f0,
            'model': model_f0,
            'difference': f0_diff,
            'match': 'excellent' if abs(f0_diff) < 20 else 'good' if abs(f0_diff) < 50 else 'fair'
        }
        
        # 性别对比
        target_gender = target_features.get('estimated_gender', 'unknown')
        model_gender = model['voice_characteristics']['gender']
        
        details['gender'] = {
            'target': target_gender,
            'model': model_gender,
            'match': 'exact' if target_gender == model_gender else 'different'
        }
        
        # 音域对比
        target_range = target_features.get('pitch_range', 150)
        model_range = model['voice_characteristics']['f0_range_max'] - model['voice_characteristics']['f0_range_min']
        
        details['pitch_range'] = {
            'target': target_range,
            'model': model_range,
            'difference': target_range - model_range
        }
        
        return details
    
    def print_match_report(self, matches, target_features):
        """
        打印匹配报告
        
        Args:
            matches: 匹配结果列表
            target_features: 目标声音特征
        """
        print("\n" + "="*70)
        print("🎯 声模匹配报告")
        print("="*70)
        
        print(f"\n📊 目标声音特征:")
        print(f"   平均 F0: {float(target_features.get('f0_mean', 150)):.2f} Hz")
        print(f"   音域范围: {float(target_features.get('pitch_range', 150)):.2f} Hz")
        print(f"   推测性别: {target_features.get('estimated_gender', 'N/A')}")
        print(f"   频谱质心: {float(target_features.get('spectral_centroid_mean', 1500)):.2f} Hz")
        
        print(f"\n🏆 推荐声模（共 {len(matches)} 个）:")
        print("-"*70)
        
        for i, match in enumerate(matches, 1):
            model = match['model']
            score = match['score']
            details = match['match_details']
            
            print(f"\n{i}. {model['name']} (ID: {model['id']})")
            print(f"   匹配度: {score:.1f}%")
            print(f"   描述: {model['description']}")
            print(f"   预训练模型: {model['pretrained_G']}")
            
            # 显示匹配详情
            f0_match = details['f0']['match']
            gender_match = details['gender']['match']
            
            print(f"   F0 对比: {details['f0']['target']:.1f} Hz → {details['f0']['model']:.1f} Hz ({f0_match})")
            print(f"   性别对比: {details['f0']['target']} → {details['gender']['model']} ({gender_match})")
            
            # 训练建议
            rec = model['training_recommendations']
            print(f"   建议训练: {rec['min_epochs']}-{rec['max_epochs']} epochs")
            print(f"   最低音频要求: {rec['min_audio_minutes']} 分钟")
            
            # 标签
            if model.get('tags'):
                print(f"   标签: {', '.join(model['tags'])}")
        
        print("\n" + "="*70)
        
        # 返回最佳匹配
        if matches:
            best_match = matches[0]['model']
            print(f"\n✅ 推荐使用: {best_match['name']}")
            print(f"   pretrained_G: {best_match['pretrained_G']}")
            print(f"   pretrained_D: {best_match['pretrained_D']}")
        
        return matches[0] if matches else None
    
    def get_recommended_epochs(self, match_result, audio_duration_seconds):
        """
        根据匹配结果和音频时长推荐训练 epoch 数
        
        Args:
            match_result: 匹配结果
            audio_duration_seconds: 音频总时长（秒）
        
        Returns:
            int: 推荐的 epoch 数
        """
        if not match_result:
            return 50  # 默认值
        
        model = match_result['model']
        score = match_result['score']
        rec = model['training_recommendations']
        
        # 基于匹配度调整
        if score >= 80:
            # 高匹配度，使用最小 epoch
            recommended = rec['min_epochs']
        elif score >= 60:
            # 中等匹配度，使用中间值
            recommended = (rec['min_epochs'] + rec['max_epochs']) // 2
        else:
            # 低匹配度，需要更多训练
            recommended = rec['max_epochs']
        
        # 基于音频时长调整
        audio_minutes = audio_duration_seconds / 60
        
        if audio_minutes >= 30:
            # 充足数据，可以减少 epoch
            recommended = int(recommended * 0.8)
        elif audio_minutes < 10:
            # 数据不足，需要更多 epoch
            recommended = int(recommended * 1.3)
        
        # 确保在合理范围内
        recommended = max(rec['min_epochs'], min(rec['max_epochs'], recommended))
        
        return recommended


def match_voice(target_audio_or_features, top_n=3, print_report=True):
    """
    便捷函数：匹配声模
    
    Args:
        target_audio_or_features: 目标音频路径或特征字典
        top_n: 返回前 N 个匹配
        print_report: 是否打印报告
    
    Returns:
        tuple: (最佳匹配, 所有匹配列表)
    """
    # 如果传入的是文件路径，先提取特征
    if isinstance(target_audio_or_features, str):
        if os.path.isfile(target_audio_or_features):
            from analyze_voice import extract_voice_features
            features = extract_voice_features(target_audio_or_features)
        elif os.path.isdir(target_audio_or_features):
            from analyze_voice import analyze_directory
            result = analyze_directory(target_audio_or_features)
            features = result.get('average_features', {})
        else:
            print(f"❌ 路径不存在: {target_audio_or_features}")
            return None, []
    else:
        features = target_audio_or_features
    
    # 创建匹配器
    matcher = VoiceModelMatcher()
    
    # 匹配声模
    matches = matcher.match_voice_model(features, top_n=top_n)
    
    if not matches:
        print("❌ 未找到匹配的声模")
        return None, []
    
    # 打印报告
    if print_report:
        best_match = matcher.print_match_report(matches, features)
    else:
        best_match = matches[0] if matches else None
    
    return best_match, matches


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="声模匹配工具")
    parser.add_argument("target", help="目标音频文件或目录")
    parser.add_argument("-n", "--top-n", type=int, default=3, help="返回前 N 个匹配结果")
    parser.add_argument("--no-report", action="store_true", help="不打印详细报告")
    parser.add_argument("--json", help="输出 JSON 结果到文件")
    
    args = parser.parse_args()
    
    best_match, all_matches = match_voice(args.target, top_n=args.top_n, print_report=not args.no_report)
    
    # 输出 JSON
    if args.json and all_matches:
        result = {
            'best_match': {
                'id': best_match['model']['id'],
                'name': best_match['model']['name'],
                'score': best_match['score'],
                'pretrained_G': best_match['model']['pretrained_G'],
                'pretrained_D': best_match['model']['pretrained_D']
            },
            'all_matches': [
                {
                    'id': m['model']['id'],
                    'name': m['model']['name'],
                    'score': m['score']
                }
                for m in all_matches
            ]
        }
        
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 匹配结果已保存: {args.json}")
