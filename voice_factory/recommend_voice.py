"""
声模推荐系统 - 查询脚本
功能：
- 输入：任意音频文件（用户录音）
- 输出：Top N 最相似的声模
- 支持：实时查询、批量查询、相似度分析
"""

import os
import sys
import json
import numpy as np
import argparse
from pathlib import Path

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# =========================
# 路径配置
# =========================
VOICE_FACTORY_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_DIR = os.path.join(VOICE_FACTORY_DIR, "embeddings")
VOICE_DB_DIR = os.path.join(VOICE_FACTORY_DIR, "voice_database")
ENHANCED_DIR = os.path.join(VOICE_FACTORY_DIR, "enhanced")
FILTERED_DIR = os.path.join(VOICE_FACTORY_DIR, "filtered")


def load_recommender():
    """加载推荐系统"""
    try:
        import faiss
    except ImportError:
        print("❌ 请先安装 FAISS:")
        print("   pip install faiss-cpu")
        return None, None, None
    
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
    except ImportError:
        print("❌ 请先安装 Resemblyzer:")
        print("   pip install resemblyzer")
        return None, None, None
    
    # 加载 FAISS 索引
    index_path = os.path.join(VOICE_DB_DIR, "faiss_index.bin")
    speaker_list_path = os.path.join(VOICE_DB_DIR, "speaker_list.json")
    
    if not os.path.exists(index_path) or not os.path.exists(speaker_list_path):
        print("❌ 数据库文件不存在")
        print("   请先运行: python complete_pipeline.py")
        return None, None, None
    
    index = faiss.read_index(index_path)
    
    with open(speaker_list_path, "r", encoding="utf-8") as f:
        speaker_list = json.load(f)
    
    # 加载声纹模型
    encoder = VoiceEncoder()
    
    print("✅ 推荐系统加载成功")
    print(f"📊 声模数量: {len(speaker_list)}")
    print()
    
    return index, speaker_list, encoder


def extract_audio_embedding(audio_path, encoder):
    """从音频文件提取 embedding"""
    try:
        from resemblyzer import preprocess_wav
    except ImportError:
        print("❌ 请先安装 Resemblyzer")
        return None
    
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None
    
    try:
        # 预处理音频
        wav = preprocess_wav(audio_path)
        # 提取 embedding
        embedding = encoder.embed_utterance(wav)
        return embedding
    except Exception as e:
        print(f"❌ 提取 embedding 失败: {e}")
        return None


def query_voice(index, speaker_list, encoder, audio_path, top_k=5):
    """查询最相似的声模"""
    print("=" * 70)
    print(f"🔍 查询音频: {os.path.basename(audio_path)}")
    print("=" * 70)
    
    # 提取 embedding
    print("📥 提取声纹特征...")
    embedding = extract_audio_embedding(audio_path, encoder)
    
    if embedding is None:
        print("❌ 提取失败")
        return None
    
    print("✅ 提取成功")
    print()
    
    # 搜索
    query_embedding = embedding.reshape(1, -1).astype(np.float32)
    distances, indices = index.search(query_embedding, top_k)
    
    # 显示结果
    print(f"📊 Top {top_k} 推荐结果:")
    print("-" * 70)
    
    results = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx < len(speaker_list):
            speaker = speaker_list[idx]
            similarity = 1.0 / (1.0 + dist)
            
            # 获取 speaker 信息
            speaker_info = get_speaker_info(speaker)
            
            result = {
                "rank": i + 1,
                "speaker": speaker,
                "distance": float(dist),
                "similarity": float(similarity),
                "info": speaker_info
            }
            results.append(result)
            
            print(f"  {i+1}. {speaker}")
            print(f"     距离: {dist:.4f}")
            print(f"     相似度: {similarity:.2%}")
            print(f"     音频数: {speaker_info['audio_count']}")
            print(f"     参数: temp={speaker_info['temperature']}, "
                  f"top_p={speaker_info['top_p']}, penalty={speaker_info['repetition_penalty']}")
            print()
    
    return results


def get_speaker_info(speaker_name):
    """获取 speaker 的详细信息"""
    info = {
        "audio_count": 0,
        "temperature": "N/A",
        "top_p": "N/A",
        "repetition_penalty": "N/A"
    }
    
    # 统计音频数量
    enhanced_path = os.path.join(ENHANCED_DIR, speaker_name)
    if os.path.exists(enhanced_path):
        info["audio_count"] = len([f for f in os.listdir(enhanced_path) if f.endswith(".wav")])
    
    # 读取 metadata
    meta_path = os.path.join(VOICE_FACTORY_DIR, "metadata", f"{speaker_name}.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            params = meta.get("params", {})
            info["temperature"] = params.get("temperature", "N/A")
            info["top_p"] = params.get("top_p", "N/A")
            info["repetition_penalty"] = params.get("repetition_penalty", "N/A")
    
    return info


def batch_query(index, speaker_list, encoder, audio_dir, top_k=5):
    """批量查询目录下的所有音频"""
    print("=" * 70)
    print("🔍 批量查询模式")
    print("=" * 70)
    
    audio_files = [f for f in os.listdir(audio_dir) 
                   if f.endswith((".wav", ".mp3", ".flac"))]
    
    if len(audio_files) == 0:
        print(f"❌ 没有找到音频文件: {audio_dir}")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件")
    print()
    
    all_results = []
    
    for audio_file in audio_files:
        audio_path = os.path.join(audio_dir, audio_file)
        print(f"\n{'='*70}")
        print(f"📄 处理: {audio_file}")
        print(f"{'='*70}")
        
        results = query_voice(index, speaker_list, encoder, audio_path, top_k)
        if results:
            all_results.append({
                "audio": audio_file,
                "results": results
            })
    
    # 保存结果
    output_path = os.path.join(VOICE_FACTORY_DIR, "query_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n💾 查询结果已保存: {output_path}")
    
    return all_results


def list_all_speakers(speaker_list):
    """列出所有可用声模"""
    print("=" * 70)
    print("📋 所有可用声模")
    print("=" * 70)
    print()
    
    for speaker in sorted(speaker_list):
        info = get_speaker_info(speaker)
        print(f"  {speaker}")
        print(f"    音频数: {info['audio_count']}")
        print(f"    参数: temp={info['temperature']}, "
              f"top_p={info['top_p']}, penalty={info['repetition_penalty']}")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="声模推荐系统 - 查询最相似的声模",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询单个音频
  python recommend_voice.py audio.wav

  # 查询并返回 Top 10
  python recommend_voice.py audio.wav --top 10

  # 批量查询目录下所有音频
  python recommend_voice.py --batch ./recordings

  # 列出所有可用声模
  python recommend_voice.py --list
        """
    )
    
    parser.add_argument("audio", nargs="?", help="音频文件路径")
    parser.add_argument("--top", "-k", type=int, default=5, help="返回 Top N 结果 (默认: 5)")
    parser.add_argument("--batch", "-b", type=str, help="批量查询目录")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有声模")
    
    args = parser.parse_args()
    
    # 加载推荐系统
    index, speaker_list, encoder = load_recommender()
    
    if index is None:
        return
    
    # 列出所有声模
    if args.list:
        list_all_speakers(speaker_list)
        return
    
    # 批量查询
    if args.batch:
        batch_query(index, speaker_list, encoder, args.batch, args.top)
        return
    
    # 单个查询
    if args.audio:
        query_voice(index, speaker_list, encoder, args.audio, args.top)
        return
    
    # 没有参数，显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()
