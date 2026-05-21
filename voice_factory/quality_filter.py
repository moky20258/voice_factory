"""
Fish Speech 音频质量筛选器（第二阶段）
功能：
- 使用 faster-whisper 进行 ASR 反识别
- 计算 WER (词错误率) 评估发音准确度
- 检测重复、崩坏音频
- 自动生成质量评分报告
- 可配置阈值自动分类/删除低质量音频
"""

import os
import json
import re
import shutil
from pathlib import Path
from tqdm import tqdm
from faster_whisper import WhisperModel
from datetime import datetime

# =========================
# 配置参数
# =========================
OUTPUT_DIR = "outputs"
META_DIR = "metadata"
REPORT_DIR = "reports"
FILTERED_DIR = "filtered"

# Whisper 模型配置
WHISPER_MODEL_SIZE = "base"  # 可选: tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"  # 可选: cpu, cuda
WHISPER_COMPUTE_TYPE = "int8"  # 可选: int8, int16, float16, float32

# 质量阈值配置
WER_THRESHOLD_GOOD = 0.15  # WER < 15% 为优质
WER_THRESHOLD_ACCEPT = 0.30  # WER < 30% 为可接受
REPETITION_THRESHOLD = 0.5  # 重复度 > 50% 标记为重复

# 分类目录
QUALITY_GOOD = "good"  # 优质
QUALITY_ACCEPT = "acceptable"  # 可接受
QUALITY_POOR = "poor"  # 低质量
QUALITY_REPEAT = "repeated"  # 重复


def load_ground_truth_texts():
    """加载原始文本作为 ground truth"""
    texts_dir = "texts"
    all_texts = []
    
    if not os.path.exists(texts_dir):
        print(f"⚠️ 文本目录不存在: {texts_dir}")
        return all_texts
    
    for file in sorted(os.listdir(texts_dir)):
        if file.endswith(".txt"):
            path = os.path.join(texts_dir, file)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
                if content:
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    all_texts.extend(lines)
    
    print(f"✅ 加载 ground truth 文本: {len(all_texts)} 句")
    return all_texts


def load_audio_files():
    """加载所有生成的音频文件"""
    audio_files = []
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"❌ 输出目录不存在: {OUTPUT_DIR}")
        return audio_files
    
    for speaker_dir in sorted(os.listdir(OUTPUT_DIR)):
        speaker_path = os.path.join(OUTPUT_DIR, speaker_dir)
        
        if not os.path.isdir(speaker_path):
            continue
        
        for audio_file in sorted(os.listdir(speaker_path)):
            if audio_file.endswith(".wav"):
                audio_files.append({
                    "speaker": speaker_dir,
                    "file": audio_file,
                    "path": os.path.join(speaker_path, audio_file)
                })
    
    print(f"✅ 加载音频文件: {len(audio_files)} 个")
    return audio_files


def find_best_matching_text(asr_text, ground_truths):
    """在 ground truth 中找到最匹配的文本"""
    if not asr_text or len(asr_text.strip()) < 3:
        return None
    
    # 简单匹配：查找包含关系
    asr_text_lower = asr_text.lower().strip()
    
    best_match = None
    best_score = 0
    
    for gt in ground_truths:
        gt_lower = gt.lower().strip()
        
        # 计算匹配度 - 使用更宽松的策略
        # 1. 完全包含匹配
        if asr_text_lower in gt_lower or gt_lower in asr_text_lower:
            score = 0.8
            if score > best_score:
                best_score = score
                best_match = gt
            continue
        
        # 2. 字符级别 Jaccard 相似度
        if len(asr_text_lower) > 0 and len(gt_lower) > 0:
            asr_chars = set(asr_text_lower)
            gt_chars = set(gt_lower)
            intersection = asr_chars & gt_chars
            union = asr_chars | gt_chars
            
            if len(union) > 0:
                jaccard = len(intersection) / len(union)
                # 如果相似度超过 40%，认为是匹配的
                if jaccard > 0.4 and jaccard > best_score:
                    best_score = jaccard
                    best_match = gt
    
    return best_match


def calculate_wer(reference, hypothesis):
    """
    计算 Word Error Rate (WER)
    WER = (S + D + I) / N
    S: 替换数, D: 删除数, I: 插入数, N: 参考词数
    """
    # 简化的 WER 计算（基于字符级别）
    ref_chars = set(reference.lower())
    hyp_chars = set(hypothesis.lower())
    
    if len(ref_chars) == 0:
        return 1.0
    
    # 计算差异
    intersection = ref_chars & hyp_chars
    union = ref_chars | hyp_chars
    
    if len(union) == 0:
        return 0.0
    
    # Jaccard 距离作为 WER 的近似
    wer = 1.0 - (len(intersection) / len(union))
    
    return wer


def detect_repetition(text):
    """检测文本中的重复模式"""
    if not text or len(text) < 10:
        return 0.0
    
    # 检测连续重复（如：啊啊啊啊）
    repeat_pattern = re.compile(r'(.)\1{3,}')
    continuous_repeats = len(repeat_pattern.findall(text))
    
    # 检测词组重复
    words = text.split()
    if len(words) < 4:
        return 0.0
    
    # 计算重复词比例
    word_count = len(words)
    unique_words = len(set(words))
    repetition_ratio = 1.0 - (unique_words / word_count)
    
    # 综合评分
    repetition_score = (continuous_repeats * 0.5 + repetition_ratio * 0.5)
    
    return min(repetition_score, 1.0)


def run_asr(audio_path, model):
    """使用 Whisper 进行语音识别"""
    try:
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language="zh",
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
            )
        )
        
        # 合并所有片段
        full_text = ""
        for segment in segments:
            full_text += segment.text
        
        return full_text.strip(), info.language
    except Exception as e:
        print(f"\n❌ ASR 失败: {audio_path}, 错误: {e}")
        return "", ""


def evaluate_audio_quality(asr_text, ground_truth_text, audio_path):
    """评估单条音频的质量"""
    # 1. 检测空输出
    is_empty = len(asr_text) < 5
    
    if is_empty:
        return {
            "wer": 1.0,
            "repetition": 0.0,
            "is_empty": True,
            "quality_score": 0.0,
            "quality_label": "empty"
        }
    
    # 2. 检测重复
    repetition = detect_repetition(asr_text)
    
    if repetition > REPETITION_THRESHOLD:
        return {
            "wer": 1.0,
            "repetition": repetition,
            "is_empty": False,
            "quality_score": 0.0,
            "quality_label": "repeated"
        }
    
    # 3. 计算 WER（如果有 ground truth）
    if ground_truth_text:
        wer = calculate_wer(ground_truth_text, asr_text)
        
        # 根据 WER 分类
        if wer < WER_THRESHOLD_GOOD:
            quality_score = 1.0 - wer
            quality_label = "good"
        elif wer < WER_THRESHOLD_ACCEPT:
            quality_score = 0.7 - (wer - WER_THRESHOLD_GOOD)
            quality_label = "acceptable"
        else:
            quality_score = max(0.0, 0.3 - (wer - WER_THRESHOLD_ACCEPT) * 0.5)
            quality_label = "poor"
    else:
        # 没有 ground truth 时，基于其他指标评估
        # 如果 ASR 能识别出内容，说明音频基本可用
        # 根据文本长度和重复度给一个基础评分
        text_length_score = min(len(asr_text) / 50.0, 1.0)  # 50字以上满分
        quality_score = (text_length_score * 0.7 + (1.0 - repetition) * 0.3)
        
        # 分类：没有 ground truth 时默认标记为 acceptable
        if quality_score > 0.6:
            quality_label = "good"
        elif quality_score > 0.3:
            quality_label = "acceptable"
        else:
            quality_label = "poor"
        
        wer = 0.0  # 无 ground truth 时不计算 WER
    
    quality_score = max(0.0, min(1.0, quality_score))
    
    return {
        "wer": wer,
        "repetition": repetition,
        "is_empty": False,
        "quality_score": quality_score,
        "quality_label": quality_label
    }


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 Fish Speech 音频质量筛选器")
    print("=" * 60)
    
    # 创建报告目录
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(FILTERED_DIR, exist_ok=True)
    
    # 加载 ground truth
    ground_truths = load_ground_truth_texts()
    
    if len(ground_truths) == 0:
        print("⚠️ 无 ground truth，将仅检测重复和空输出")
    
    # 加载音频文件
    audio_files = load_audio_files()
    
    if len(audio_files) == 0:
        print("❌ 没有找到音频文件，请先运行 generate.py")
        return
    
    # 加载 Whisper 模型
    print(f"\n📥 加载 Whisper 模型: {WHISPER_MODEL_SIZE} ({WHISPER_DEVICE})")
    print("⏳ 首次加载会下载模型，请稍候...")
    
    try:
        model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE
        )
        print("✅ Whisper 模型加载成功")
    except Exception as e:
        print(f"❌ Whisper 模型加载失败: {e}")
        print("💡 请检查网络连接或更换较小的模型 (tiny)")
        return
    
    # 开始评估
    print(f"\n🚀 开始质量评估: {len(audio_files)} 个音频")
    print("=" * 60)
    
    results = []
    quality_stats = {
        "good": 0,
        "acceptable": 0,
        "poor": 0,
        "repeated": 0,
        "empty": 0
    }
    
    for audio_info in tqdm(audio_files, desc="评估进度"):
        speaker = audio_info["speaker"]
        audio_file = audio_info["file"]
        audio_path = audio_info["path"]
        
        # 运行 ASR
        asr_text, detected_lang = run_asr(audio_path, model)
        
        # 查找匹配的 ground truth
        ground_truth = find_best_matching_text(asr_text, ground_truths)
        
        # 评估质量
        quality = evaluate_audio_quality(asr_text, ground_truth, audio_path)
        
        # 记录结果
        result = {
            "speaker": speaker,
            "file": audio_file,
            "path": audio_path,
            "asr_text": asr_text,
            "ground_truth": ground_truth,
            "detected_language": detected_lang,
            **quality
        }
        
        results.append(result)
        quality_stats[quality["quality_label"]] += 1
        
        # 分类到不同目录
        quality_label = quality["quality_label"]
        target_dir = os.path.join(FILTERED_DIR, quality_label, speaker)
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件到对应目录
        target_path = os.path.join(target_dir, audio_file)
        shutil.copy2(audio_path, target_path)
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📊 质量评估报告")
    print("=" * 60)
    
    total = len(results)
    print(f"📈 总音频数: {total}")
    print(f"✅ 优质 (WER < {WER_THRESHOLD_GOOD*100:.0f}%): {quality_stats['good']} ({quality_stats['good']/total*100:.1f}%)")
    print(f"⚠️ 可接受 (WER < {WER_THRESHOLD_ACCEPT*100:.0f}%): {quality_stats['acceptable']} ({quality_stats['acceptable']/total*100:.1f}%)")
    print(f"❌ 低质量: {quality_stats['poor']} ({quality_stats['poor']/total*100:.1f}%)")
    print(f"🔁 重复: {quality_stats['repeated']} ({quality_stats['repeated']/total*100:.1f}%)")
    print(f"⭕ 空输出: {quality_stats['empty']} ({quality_stats['empty']/total*100:.1f}%)")
    
    # 按 speaker 统计
    print("\n📋 各 Speaker 质量分布:")
    speaker_stats = {}
    for result in results:
        speaker = result["speaker"]
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {"good": 0, "acceptable": 0, "poor": 0, "repeated": 0, "empty": 0}
        
        label = result["quality_label"]
        speaker_stats[speaker][label] += 1
    
    for speaker in sorted(speaker_stats.keys()):
        stats = speaker_stats[speaker]
        good_rate = (stats["good"] + stats["acceptable"]) / sum(stats.values()) * 100
        print(f"  {speaker}: 优质率 {good_rate:.1f}% "
              f"(优质:{stats['good']}, 可接受:{stats['acceptable']}, "
              f"低质量:{stats['poor']}, 重复:{stats['repeated']})")
    
    # 保存详细报告
    report_path = os.path.join(REPORT_DIR, f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "quality_stats": quality_stats,
            "speaker_stats": speaker_stats,
            "results": results
        }, f, indent=4, ensure_ascii=False)
    
    print(f"\n💾 详细报告已保存: {report_path}")
    
    # 生成优质音频列表
    good_audios = [r for r in results if r["quality_label"] in ["good", "acceptable"]]
    good_list_path = os.path.join(REPORT_DIR, f"good_audios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(good_list_path, "w", encoding="utf-8") as f:
        f.write("# 优质和可接受的音频列表\n")
        f.write(f"# 总计: {len(good_audios)} 个\n\n")
        
        for audio in sorted(good_audios, key=lambda x: x["quality_score"], reverse=True):
            f.write(f"{audio['speaker']}/{audio['file']} "
                    f"(WER: {audio['wer']:.3f}, 评分: {audio['quality_score']:.3f})\n")
    
    print(f"💾 优质音频列表: {good_list_path}")
    
    # 给出建议
    print("\n" + "=" * 60)
    print("💡 建议:")
    
    if quality_stats['good'] / total < 0.5:
        print("⚠️ 优质率较低，建议:")
        print("   - 降低 temperature (0.6-0.7)")
        print("   - 提高 repetition_penalty (1.2-1.3)")
        print("   - 检查文本质量")
    
    if quality_stats['repeated'] > 0:
        print(f"⚠️ 检测到 {quality_stats['repeated']} 个重复音频，建议提高 repetition_penalty")
    
    if quality_stats['empty'] > 0:
        print(f"⚠️ 检测到 {quality_stats['empty']} 个空输出，建议检查 API 状态")
    
    print(f"\n✅ 优质音频已复制到: {os.path.abspath(os.path.join(FILTERED_DIR, QUALITY_GOOD))}")
    print(f"✅ 可接受音频已复制到: {os.path.abspath(os.path.join(FILTERED_DIR, QUALITY_ACCEPT))}")
    print("=" * 60)


if __name__ == "__main__":
    main()
