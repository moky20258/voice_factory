"""
Fish Speech DSP 增强器（STEP 3）
功能：
- 对优质音频进行 DSP 处理扩库
- Pitch Shift（变调）：创建不同音高变体
- Formant Shift（共振峰）：改变年龄感/男女感
- Speaking Rate（语速）：0.9x, 1.1x
- EQ（均衡器）：模拟不同麦克风/空间
- 自动从 filtered/good 和 filtered/acceptable 读取音频
- 自动生成扩库后的音频和 metadata
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# =========================
# 配置参数
# =========================
FILTERED_DIR = "filtered"
ENHANCED_DIR = "enhanced"
META_DIR = "metadata"
ENHANCED_META_DIR = "metadata_enhanced"

# 创建目录
os.makedirs(ENHANCED_DIR, exist_ok=True)
os.makedirs(ENHANCED_META_DIR, exist_ok=True)

# DSP 增强配置
DSP_CONFIGS = {
    # Pitch Shift（音高调整，半音）
    "pitch": [-3, -2, 2, 3],
    
    # Formant Shift（共振峰，改变年龄感）
    "formant": [0.85, 0.9, 1.1, 1.15],
    
    # Speaking Rate（语速）
    "rate": [0.9, 1.1],
    
    # EQ 预设（模拟不同环境）
    "eq": {
        "studio": "equal=f=1000:t=h:w=2:g=-3",  # 录音室
        "warm": "equal=f=200:t=h:w=1:g=2,equal=f=5000:t=h:w=2:g=-2",  # 温暖
        "bright": "equal=f=3000:t=h:w=2:g=3,equal=f=200:t=h:w=1:g=-2",  # 明亮
    }
}


def check_ffmpeg():
    """检查 FFmpeg 是否可用"""
    # 尝试刷新 PATH
    import sys
    if sys.platform == 'win32':
        import subprocess
        # 从注册表获取最新 PATH
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                system_path, _ = winreg.QueryValueEx(key, "Path")
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                user_path, _ = winreg.QueryValueEx(key, "Path")
            os.environ['PATH'] = system_path + ";" + user_path
        except:
            pass
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ FFmpeg 已安装")
            return True
        else:
            print("❌ FFmpeg 不可用")
            return False
    except FileNotFoundError:
        print("❌ 未找到 FFmpeg")
        print("💡 请安装 FFmpeg:")
        print("   - Windows: winget install ffmpeg")
        print("   - 或下载: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ FFmpeg 检查失败: {e}")
        return False


def get_source_audios():
    """获取优质和可接受的音频"""
    source_audios = []
    
    # 从 good 和 acceptable 目录读取
    for quality_type in ["good", "acceptable"]:
        quality_path = os.path.join(FILTERED_DIR, quality_type)
        
        if not os.path.exists(quality_path):
            print(f"⚠️ 目录不存在: {quality_path}")
            continue
        
        for speaker_dir in os.listdir(quality_path):
            speaker_path = os.path.join(quality_path, speaker_dir)
            
            if not os.path.isdir(speaker_path):
                continue
            
            for audio_file in os.listdir(speaker_path):
                if audio_file.endswith(".wav"):
                    source_audios.append({
                        "speaker": speaker_dir,
                        "file": audio_file,
                        "path": os.path.join(speaker_path, audio_file),
                        "quality": quality_type
                    })
    
    print(f"✅ 加载源音频: {len(source_audios)} 个")
    return source_audios


def apply_pitch_shift(input_path, output_path, semitones):
    """应用音高偏移"""
    # 使用 rubberband 或 soundtouch
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", f"rubberband=pitch={2**(semitones/12)}",
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False


def apply_formant_shift(input_path, output_path, factor):
    """应用共振峰偏移"""
    # 通过改变采样率实现简单的共振峰效果
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", f"asetrate=44100*{factor},aresample=44100",
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False


def apply_rate_change(input_path, output_path, rate):
    """应用语速变化"""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", f"atempo={rate}",
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False


def apply_eq(input_path, output_path, eq_preset):
    """应用均衡器"""
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-af", eq_preset,
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False


def enhance_audio(audio_info, dsp_type, dsp_value, output_dir):
    """对单个音频应用 DSP 增强"""
    input_path = audio_info["path"]
    speaker = audio_info["speaker"]
    file = audio_info["file"]
    
    # 生成输出文件名
    base_name = Path(file).stem
    if dsp_type == "pitch":
        suffix = f"_pitch{dsp_value:+d}"
    elif dsp_type == "formant":
        suffix = f"_formant{dsp_value:.2f}"
    elif dsp_type == "rate":
        suffix = f"_rate{dsp_value:.2f}x"
    elif dsp_type == "eq":
        suffix = f"_eq_{dsp_value}"
    
    output_file = f"{base_name}{suffix}.wav"
    output_path = os.path.join(output_dir, output_file)
    
    # 应用 DSP
    success = False
    if dsp_type == "pitch":
        success = apply_pitch_shift(input_path, output_path, dsp_value)
    elif dsp_type == "formant":
        success = apply_formant_shift(input_path, output_path, dsp_value)
    elif dsp_type == "rate":
        success = apply_rate_change(input_path, output_path, dsp_value)
    elif dsp_type == "eq":
        success = apply_eq(input_path, output_path, dsp_value)
    
    if success:
        return {
            "original": file,
            "enhanced": output_file,
            "dsp_type": dsp_type,
            "dsp_value": dsp_value,
            "path": output_path
        }
    else:
        return None


def load_original_metadata(speaker_name):
    """加载原始 speaker 的 metadata"""
    meta_path = os.path.join(META_DIR, f"{speaker_name}.json")
    
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return None


def main():
    """主函数"""
    print("=" * 70)
    print("🎛️ Fish Speech DSP 增强器")
    print("=" * 70)
    
    # 检查 FFmpeg
    if not check_ffmpeg():
        print("\n❌ 请先安装 FFmpeg")
        return
    
    # 获取源音频
    source_audios = get_source_audios()
    
    if len(source_audios) == 0:
        print("❌ 没有找到源音频，请先运行质量筛选")
        return
    
    print(f"\n🚀 开始 DSP 增强: {len(source_audios)} 个源音频")
    print("=" * 70)
    
    # 统计
    total_enhanced = 0
    total_failed = 0
    enhanced_metadata = []
    
    # 对每个音频应用多种 DSP
    for audio_info in tqdm(source_audios, desc="DSP 增强进度"):
        speaker = audio_info["speaker"]
        speaker_enhanced_dir = os.path.join(ENHANCED_DIR, speaker)
        os.makedirs(speaker_enhanced_dir, exist_ok=True)
        
        # 加载原始 metadata
        original_meta = load_original_metadata(speaker)
        
        # 1. Pitch Shift
        for pitch in DSP_CONFIGS["pitch"]:
            result = enhance_audio(audio_info, "pitch", pitch, speaker_enhanced_dir)
            if result:
                total_enhanced += 1
                result["original_metadata"] = original_meta
                enhanced_metadata.append(result)
            else:
                total_failed += 1
        
        # 2. Formant Shift
        for formant in DSP_CONFIGS["formant"]:
            result = enhance_audio(audio_info, "formant", formant, speaker_enhanced_dir)
            if result:
                total_enhanced += 1
                result["original_metadata"] = original_meta
                enhanced_metadata.append(result)
            else:
                total_failed += 1
        
        # 3. Rate Change
        for rate in DSP_CONFIGS["rate"]:
            result = enhance_audio(audio_info, "rate", rate, speaker_enhanced_dir)
            if result:
                total_enhanced += 1
                result["original_metadata"] = original_meta
                enhanced_metadata.append(result)
            else:
                total_failed += 1
        
        # 4. EQ
        for eq_name, eq_preset in DSP_CONFIGS["eq"].items():
            result = enhance_audio(audio_info, "eq", eq_name, speaker_enhanced_dir)
            if result:
                total_enhanced += 1
                result["original_metadata"] = original_meta
                enhanced_metadata.append(result)
            else:
                total_failed += 1
    
    # 保存增强 metadata
    meta_file = os.path.join(
        ENHANCED_META_DIR,
        f"enhanced_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_source": len(source_audios),
            "total_enhanced": total_enhanced,
            "total_failed": total_failed,
            "dsp_configs": DSP_CONFIGS,
            "enhanced_audios": enhanced_metadata
        }, f, indent=4, ensure_ascii=False)
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📊 DSP 增强报告")
    print("=" * 70)
    print(f"📈 源音频数: {len(source_audios)}")
    print(f"✅ 增强成功: {total_enhanced}")
    print(f"❌ 增强失败: {total_failed}")
    print(f"📁 输出目录: {os.path.abspath(ENHANCED_DIR)}")
    print(f"📄 Metadata: {os.path.abspath(meta_file)}")
    
    # 扩库倍数
    expansion_factor = total_enhanced / len(source_audios) if len(source_audios) > 0 else 0
    print(f"🔢 扩库倍数: {expansion_factor:.1f}x")
    print(f"📊 总计音频: {len(source_audios) + total_enhanced} (原始 + 增强)")
    
    # 按 speaker 统计
    print("\n📋 各 Speaker 增强统计:")
    speaker_stats = {}
    for meta in enhanced_metadata:
        # 从路径提取 speaker
        speaker = meta["path"].split(os.sep)[-2]
        if speaker not in speaker_stats:
            speaker_stats[speaker] = 0
        speaker_stats[speaker] += 1
    
    for speaker in sorted(speaker_stats.keys()):
        count = speaker_stats[speaker]
        print(f"  {speaker}: {count} 个增强音频")
    
    print("\n" + "=" * 70)
    print("💡 下一步建议:")
    print("=" * 70)
    print()
    print("1. 试听增强后的音频，选择最佳变体")
    print("2. 使用增强音频训练 RVC 模型")
    print("3. 提取声纹 embedding 建立数据库")
    print("4. 结合原始音频和增强音频扩库")
    print()
    print("=" * 70)
    print("🎉 DSP 增强完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
