"""
RVC 批量训练脚本
使用方法:
    python rvc_batch_train.py --speakers speaker_0001 speaker_0002
    python rvc_batch_train.py --all  # 训练所有 speaker
"""

import os
import subprocess
import argparse

RVC_DIR = r"W:\rvc"
VOICE_FACTORY_DIR = r"W:\fish-speech-1.5.1\voice_factory"

def train_speaker(speaker_name):
    """训练单个 speaker"""
    print(f"\n🎓 训练 {speaker_name}...")
    
    # 调用 RVC 训练命令
    # 注意：这里需要根据 RVC 的实际 API 调整
    cmd = [
        "python", "infer-web.py",
        "--train",
        "--exp_dir", speaker_name,
        "--pretrain", "pretrained/f0G40k.pth",
        "--gpus", "0",
        "--batch_size", "8",
        "--total_epoch", "200"
    ]
    
    # 这里只是示例，实际需要使用 RVC 的训练 API
    print(f"   训练命令: {' '.join(cmd)}")
    print(f"   请在 RVC WebUI 中手动启动训练")
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--speakers", nargs="+", help="要训练的 speaker 列表")
    parser.add_argument("--all", action="store_true", help="训练所有 speaker")
    
    args = parser.parse_args()
    
    if args.all:
        # 获取所有 speaker
        logs_dir = os.path.join(RVC_DIR, "logs")
        speakers = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]
    else:
        speakers = args.speakers
    
    for speaker in speakers:
        train_speaker(speaker)

if __name__ == "__main__":
    main()
