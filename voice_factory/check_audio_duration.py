"""
检查音频时长和训练数据质量
"""

import os
import subprocess
import numpy as np
import sys

# 设置 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

VOICE_FACTORY_DIR = os.path.dirname(os.path.abspath(__file__))
ENHANCED_DIR = os.path.join(VOICE_FACTORY_DIR, "enhanced")
RVC_LOGS_DIR = r"W:\rvc\logs"

def get_audio_duration(audio_path):
    """获取音频时长（秒）"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
            capture_output=True, text=True, timeout=5
        )
        return float(result.stdout.strip())
    except:
        return 0

def check_speaker_audios(speaker_name, sample_size=5):
    """检查单个 speaker 的音频"""
    speaker_path = os.path.join(ENHANCED_DIR, speaker_name)
    
    if not os.path.exists(speaker_path):
        return None
    
    audio_files = [f for f in os.listdir(speaker_path) if f.endswith(".wav")]
    
    if len(audio_files) == 0:
        return None
    
    # 随机采样检查
    import random
    sample_files = random.sample(audio_files, min(sample_size, len(audio_files)))
    
    durations = []
    for audio_file in sample_files:
        audio_path = os.path.join(speaker_path, audio_file)
        duration = get_audio_duration(audio_path)
        durations.append(duration)
    
    return {
        "speaker": speaker_name,
        "total_audios": len(audio_files),
        "sample_durations": durations,
        "avg_duration": np.mean(durations),
        "min_duration": np.min(durations),
        "max_duration": np.max(durations)
    }

def main():
    print("=" * 70)
    print("📊 音频时长检查")
    print("=" * 70)
    print()
    
    speakers = sorted([d for d in os.listdir(ENHANCED_DIR) 
                       if os.path.isdir(os.path.join(ENHANCED_DIR, d))])
    
    print(f"🔍 检查 {len(speakers)} 个 speaker 的音频时长...\n")
    
    all_results = []
    total_audios = 0
    
    for speaker in speakers:
        result = check_speaker_audios(speaker)
        if result:
            all_results.append(result)
            total_audios += result["total_audios"]
            print(f"  {speaker}:")
            print(f"    音频数: {result['total_audios']}")
            print(f"    平均时长: {result['avg_duration']:.2f} 秒")
            print(f"    时长范围: {result['min_duration']:.2f} - {result['max_duration']:.2f} 秒")
            print()
    
    # 统计
    avg_durations = [r["avg_duration"] for r in all_results]
    overall_avg = np.mean(avg_durations)
    
    print("=" * 70)
    print("📈 总体统计")
    print("=" * 70)
    print(f"  总音频数: {total_audios}")
    print(f"  平均时长: {overall_avg:.2f} 秒")
    print(f"  最短音频: {min([r['min_duration'] for r in all_results]):.2f} 秒")
    print(f"  最长音频: {max([r['max_duration'] for r in all_results]):.2f} 秒")
    print()
    
    # 评估训练有效性
    print("=" * 70)
    print("💡 RVC 训练有效性评估")
    print("=" * 70)
    print()
    
    if overall_avg < 2:
        print("⚠️ 警告：音频时长过短！")
        print()
        print("问题：")
        print("  - RVC 训练需要至少 2-3 秒的音频")
        print("  - 过短的音频无法提取有效的声学特征")
        print("  - 训练效果会很差")
        print()
        print("建议：")
        print("  1. 重新生成音频，使用更长的文本（10-20 字）")
        print("  2. 或者合并多个短音频为长音频")
        print("  3. 过滤掉 < 2 秒的音频")
        print()
        return False
    elif overall_avg < 4:
        print("⚠️ 音频时长偏短，但可以训练")
        print()
        print("说明：")
        print("  - 2-4 秒的音频可以训练，但效果一般")
        print("  - 建议增加音频时长到 5-10 秒")
        print("  - 或者使用更多音频数量补偿")
        print()
        print("当前配置：")
        print(f"  - 每个 speaker: ~{total_audios // len(speakers)} 个音频")
        print(f"  - 平均时长: {overall_avg:.2f} 秒")
        print(f"  - 总时长: {total_audios * overall_avg / 60:.1f} 分钟")
        print()
        print("建议：")
        print("  ✅ 可以开始训练，但要有心理准备效果可能不理想")
        print("  ✅ 训练后如果效果差，需要重新生成更长音频")
        print()
        return True
    else:
        print("✅ 音频时长合适，可以训练！")
        print()
        print("说明：")
        print(f"  - 平均时长 {overall_avg:.2f} 秒，符合 RVC 训练要求")
        print(f"  - 每个 speaker 约 {total_audios // len(speakers)} 个音频")
        print(f"  - 总训练数据约 {total_audios * overall_avg / 60:.1f} 分钟")
        print()
        print("建议：")
        print("  ✅ 可以直接开始训练")
        print("  ✅ 建议使用 GPU 加速")
        print("  ✅ 训练 Epoch 建议 200-300")
        print()
        return True

if __name__ == "__main__":
    main()
