#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复版的预处理脚本 - 不使用 multiprocessing"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import traceback

# 切换到 RVC 目录
os.chdir("W:\\rvc")
sys.path.insert(0, "W:\\rvc")

from scipy import signal
import librosa
import numpy as np
from scipy.io import wavfile

from infer.lib.audio import load_audio
from infer.lib.slicer2 import Slicer

# 参数
inp_root = "W:\\rvc\\logs\\speaker_0001\\input_wavs"
sr = 40000
exp_dir = "W:\\rvc\\logs\\speaker_0001"
per = 3.7

print(f"输入目录: {inp_root}")
print(f"采样率: {sr}")
print(f"输出目录: {exp_dir}")
print()

# 创建输出目录
gt_wavs_dir = os.path.join(exp_dir, "0_gt_wavs")
wavs16k_dir = os.path.join(exp_dir, "1_16k_wavs")
os.makedirs(gt_wavs_dir, exist_ok=True)
os.makedirs(wavs16k_dir, exist_ok=True)

# 初始化 slicer
slicer = Slicer(
    sr=sr,
    threshold=-42,
    min_length=1500,
    min_interval=400,
    hop_size=15,
    max_sil_kept=500,
)

# 滤波器
bh, ah = signal.butter(N=5, Wn=48, btype="high", fs=sr)

# 参数
overlap = 0.3
tail = per + overlap
max_val = 0.9
alpha = 0.75

def norm_write(tmp_audio, idx0, idx1):
    """归一化并写入文件"""
    tmp_max = np.abs(tmp_audio).max()
    if tmp_max > 2.5:
        print(f"  [FILTER] {idx0}-{idx1} 音频过大: {tmp_max:.2f}")
        return False
    
    tmp_audio = (tmp_audio / tmp_max * (max_val * alpha)) + (
        1 - alpha
    ) * tmp_audio
    
    # 保存 40k
    wavfile.write(
        os.path.join(gt_wavs_dir, f"{idx0}_{idx1}.wav"),
        sr,
        tmp_audio.astype(np.float32),
    )
    
    # 重采样到 16k
    tmp_audio_16k = librosa.resample(tmp_audio, orig_sr=sr, target_sr=16000)
    wavfile.write(
        os.path.join(wavs16k_dir, f"{idx0}_{idx1}.wav"),
        16000,
        tmp_audio_16k.astype(np.float32),
    )
    
    return True

# 获取所有文件
wav_files = sorted([f for f in os.listdir(inp_root) if f.endswith(".wav")])
print(f"找到 {len(wav_files)} 个 wav 文件")
print()

# 逐个处理
success_count = 0
fail_count = 0
skip_count = 0

for idx0, name in enumerate(wav_files):
    path = os.path.join(inp_root, name)
    
    try:
        # 加载音频
        audio = load_audio(path, sr)
        
        # 高通滤波
        audio = signal.lfilter(bh, ah, audio)
        
        # 分割音频
        idx1 = 0
        for audio_chunk in slicer.slice(audio):
            i = 0
            while True:
                start = int(sr * (per - overlap) * i)
                i += 1
                if len(audio_chunk[start:]) > int(tail * sr):
                    tmp_audio = audio_chunk[start : start + int(per * sr)]
                    if norm_write(tmp_audio, idx0, idx1):
                        success_count += 1
                    else:
                        skip_count += 1
                    idx1 += 1
                else:
                    tmp_audio = audio_chunk[start:]
                    if norm_write(tmp_audio, idx0, idx1):
                        success_count += 1
                    else:
                        skip_count += 1
                    idx1 += 1
                    break
        
        print(f"[{idx0+1}/{len(wav_files)}] {name} -> {idx1} 个片段")
        
    except Exception as e:
        fail_count += 1
        print(f"[{idx0+1}/{len(wav_files)}] {name} -> 失败: {e}")

print()
print("="*70)
print("预处理完成!")
print(f"  成功: {success_count}")
print(f"  失败: {fail_count}")
print(f"  跳过: {skip_count}")
print()
print(f"输出目录:")
print(f"  0_gt_wavs: {len(os.listdir(gt_wavs_dir))} 个文件")
print(f"  1_16k_wavs: {len(os.listdir(wavs16k_dir))} 个文件")
print("="*70)
