#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查训练音频和声模特征"""
import os
from pathlib import Path

enhanced_dir = Path("w:/fish-speech-1.5.1/voice_factory/enhanced")
speakers = ["speaker_0024", "speaker_0025", "speaker_0026", "speaker_0027", "speaker_0028"]

print("=" * 70)
print("检查声模训练数据")
print("=" * 70)

for speaker in speakers:
    speaker_dir = enhanced_dir / speaker
    if not speaker_dir.exists():
        print(f"\n[ERROR] {speaker}: 目录不存在")
        continue
    
    wav_files = sorted([f for f in os.listdir(speaker_dir) if f.endswith('.wav')])
    print(f"\n[DIR] {speaker}: {len(wav_files)} 个音频文件")
    
    # 检查文件大小
    if wav_files:
        sizes = [os.path.getsize(speaker_dir / f) for f in wav_files[:3]]
        print(f"   前3个文件大小: {[f'{s/1024:.1f}KB' for s in sizes]}")
        
        # 检查文本内容
        text_file = Path(f"w:/fish-speech-1.5.1/voice_factory/texts/{speaker}_0001.txt")
        if text_file.exists():
            content = text_file.read_text(encoding='utf-8').strip()
            lines = [l for l in content.split('\n') if l.strip()]
            print(f"   训练文本: {len(lines)} 句")
            if lines:
                print(f"   示例: {lines[0][:50]}...")

print("\n" + "=" * 70)
print("检查RVC训练日志")
print("=" * 70)

rvc_logs = Path("W:/rvc/logs")
for speaker in speakers:
    log_dir = rvc_logs / speaker
    if log_dir.exists():
        # 检查训练轮数
        pth_files = sorted(log_dir.glob("*.pth"))
        print(f"\n[OK] {speaker}:")
        print(f"   模型文件: {len(pth_files)} 个")
        
        # 检查是否有训练日志
        train_log = log_dir / "train.log"
        if train_log.exists():
            content = train_log.read_text(encoding='utf-8', errors='ignore')
            # 查找最后的epoch
            import re
            epochs = re.findall(r'epoch:\s*(\d+)', content)
            if epochs:
                print(f"   训练轮数: {epochs[-1]} epochs")
