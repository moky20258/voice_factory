#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试 preprocess.py 的完整流程"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os

# 切换到 RVC 目录
os.chdir("W:\\rvc")
sys.path.insert(0, "W:\\rvc")

from infer.lib.audio import load_audio
from infer.lib.slicer2 import Slicer
from scipy import signal
import numpy as np
from scipy.io import wavfile

# 参数
inp_root = "W:\\rvc\\logs\\speaker_0001\\input_wavs"
exp_dir = "W:\\rvc\\logs\\speaker_0001"
sr = 40000

print(f"输入目录: {inp_root}")
print(f"输出目录: {exp_dir}")
print()

# 创建输出目录
gt_wavs_dir = os.path.join(exp_dir, "0_gt_wavs")
wavs16k_dir = os.path.join(exp_dir, "1_16k_wavs")
os.makedirs(gt_wavs_dir, exist_ok=True)
os.makedirs(wavs16k_dir, exist_ok=True)

# 列出所有 wav 文件
wav_files = [f for f in os.listdir(inp_root) if f.endswith(".wav")]
print(f"找到 {len(wav_files)} 个 wav 文件")
print(f"前3个文件: {wav_files[:3]}")
print()

# 测试处理第一个文件
if len(wav_files) > 0:
    test_file = wav_files[0]
    test_path = os.path.join(inp_root, test_file)
    
    print(f"测试处理: {test_file}")
    
    try:
        # 加载音频
        audio = load_audio(test_path, sr)
        print(f"  [1/4] 音频加载成功: {len(audio)} 采样点")
        
        # 高通滤波
        bh, ah = signal.butter(N=5, Wn=48, btype="high", fs=sr)
        audio = signal.lfilter(bh, ah, audio)
        print(f"  [2/4] 高通滤波完成")
        
        # 音频分割
        slicer = Slicer(
            sr=sr,
            threshold=-42,
            min_length=1500,
            min_interval=400,
            hop_size=15,
            max_sil_kept=500,
        )
        
        chunks = list(slicer.slice(audio))
        print(f"  [3/4] 音频分割: {len(chunks)} 个片段")
        
        # 保存第一个片段
        if len(chunks) > 0:
            chunk = chunks[0]
            # 归一化
            tmp_max = np.abs(chunk).max()
            if tmp_max > 2.5:
                print(f"  [SKIP] 音频过大: {tmp_max}")
            else:
                max_val = 0.9
                alpha = 0.75
                chunk = (chunk / tmp_max * (max_val * alpha)) + (1 - alpha) * chunk
                
                # 保存 40k
                out_path = os.path.join(gt_wavs_dir, "test_0.wav")
                wavfile.write(out_path, sr, chunk.astype(np.float32))
                print(f"  [4/4] 保存到: {out_path}")
                
                # 重采样到 16k
                import librosa
                chunk_16k = librosa.resample(chunk, orig_sr=sr, target_sr=16000)
                out_path_16k = os.path.join(wavs16k_dir, "test_0.wav")
                wavfile.write(out_path_16k, 16000, chunk_16k.astype(np.float32))
                print(f"  [4/4] 保存到: {out_path_16k}")
                
                print(f"\n[SUCCESS] 预处理成功!")
                print(f"  检查目录:")
                print(f"    {gt_wavs_dir}: {len(os.listdir(gt_wavs_dir))} 个文件")
                print(f"    {wavs16k_dir}: {len(os.listdir(wavs16k_dir))} 个文件")
        
    except Exception as e:
        print(f"\n[ERROR] 处理失败: {e}")
        import traceback
        traceback.print_exc()
