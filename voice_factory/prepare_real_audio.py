"""
准备真实音频用于RVC训练
功能: 将单个音频文件转换为RVC训练格式
"""

import os
import sys
import io
import subprocess
import shutil

# 设置 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 路径配置
FISH_SPEECH_DIR = r"W:\fish-speech-1.5.1"
VOICE_FACTORY_DIR = os.path.join(FISH_SPEECH_DIR, "voice_factory")
RVC_DIR = r"W:\rvc"
FFMPEG_PATH = os.path.join(FISH_SPEECH_DIR, "ffmpeg.exe")

# 输入音频
INPUT_AUDIO = r"W:\voice\0602001.mp3"

def get_audio_duration(audio_path):
    """获取音频时长(秒)"""
    try:
        cmd = [FFMPEG_PATH, "-i", audio_path, "-f", "null", "-"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        for line in result.stderr.split('\n'):
            if 'Duration' in line:
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                parts = time_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        return 0
    except Exception as e:
        print(f"⚠️ 获取时长失败: {e}")
        return 0

def get_next_speaker_id():
    """获取下一个可用的speaker编号"""
    logs_dir = os.path.join(RVC_DIR, "logs")
    if not os.path.exists(logs_dir):
        return 1
    
    existing = []
    for d in os.listdir(logs_dir):
        if d.startswith("speaker_"):
            try:
                num = int(d.split("_")[1])
                existing.append(num)
            except:
                pass
    
    return max(existing, default=0) + 1

def main():
    print("=" * 70)
    print("🎤 准备真实音频用于RVC训练")
    print("=" * 70)
    print()
    
    # 检查输入文件
    if not os.path.exists(INPUT_AUDIO):
        print(f"❌ 输入音频不存在: {INPUT_AUDIO}")
        return
    
    print(f"📁 输入音频: {INPUT_AUDIO}")
    
    # 获取音频时长
    duration = get_audio_duration(INPUT_AUDIO)
    print(f"📊 音频时长: {duration:.2f} 秒 ({duration/60:.2f} 分钟)")
    
    # 智能推荐训练参数
    if duration < 300:  # < 5分钟
        epochs = 50
        print(f"📈 推荐训练轮数: {epochs} epochs (音频较短)")
    elif duration < 600:  # 5-10分钟
        epochs = 80
        print(f"📈 推荐训练轮数: {epochs} epochs")
    else:  # > 10分钟
        epochs = 100
        print(f"📈 推荐训练轮数: {epochs} epochs (音频充足)")
    
    print()
    
    # 获取下一个speaker编号
    speaker_id = get_next_speaker_id()
    speaker_name = f"speaker_{speaker_id:04d}"
    
    print(f"🆔 声模ID: {speaker_name}")
    print()
    
    # 创建RVC实验目录
    rvc_speaker_dir = os.path.join(RVC_DIR, "logs", speaker_name)
    input_wavs_dir = os.path.join(rvc_speaker_dir, "input_wavs")
    
    os.makedirs(input_wavs_dir, exist_ok=True)
    print(f"📂 创建目录: {input_wavs_dir}")
    
    # 转换音频格式
    output_wav = os.path.join(input_wavs_dir, "0001.wav")
    
    print(f"🔄 转换音频格式...")
    print(f"   m4a → wav (40kHz, mono, 16-bit)")
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-i", INPUT_AUDIO,
        "-ar", "40000",
        "-ac", "1",
        "-sample_fmt", "s16",
        output_wav
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        print(f"❌ 音频转换失败")
        print(result.stderr)
        return
    
    if not os.path.exists(output_wav):
        print(f"❌ 输出文件不存在")
        return
    
    file_size = os.path.getsize(output_wav) / 1024 / 1024
    print(f"✅ 音频转换成功: {file_size:.2f} MB")
    print(f"   输出: {output_wav}")
    print()
    
    # 生成训练说明
    print("=" * 70)
    print("✅ 音频准备完成!")
    print("=" * 70)
    print()
    print("📋 下一步: 运行RVC训练")
    print()
    print("方法1: 使用全自动训练脚本 (推荐)")
    print(f'  cd {VOICE_FACTORY_DIR}')
    print(f'  W:\\rvc\\runtime\\python.exe rvc_full_auto_train.py --speakers {speaker_name} --epochs {epochs}')
    print()
    print("方法2: 使用RVC WebUI手动训练")
    print(f"  1. 运行: W:\\rvc\\go-web.bat")
    print(f"  2. 浏览器打开: http://localhost:7897")
    print(f"  3. 点击'训练'标签")
    print(f"  4. 实验名称: {speaker_name}")
    print(f"  5. 点击'一键训练'")
    print()
    print("=" * 70)
    print()
    
    # 保存训练参数
    param_file = os.path.join(VOICE_FACTORY_DIR, f"train_params_{speaker_name}.txt")
    with open(param_file, 'w', encoding='utf-8') as f:
        f.write(f"speaker_name={speaker_name}\n")
        f.write(f"epochs={epochs}\n")
        f.write(f"batch_size=8\n")
        f.write(f"audio_duration={duration:.2f}\n")
        f.write(f"input_audio={INPUT_AUDIO}\n")
    
    print(f"💾 训练参数已保存: {param_file}")
    print()

if __name__ == "__main__":
    main()
