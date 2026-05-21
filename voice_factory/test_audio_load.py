#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 RVC 的音频加载功能"""

import sys
import io

# 修复 Windows GBK 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os

# 切换到 RVC 目录
os.chdir("W:\\rvc")
sys.path.insert(0, "W:\\rvc")

from infer.lib.audio import load_audio

# 测试音频
test_audio = "W:\\rvc\\logs\\speaker_0001\\input_wavs\\0001_formant0.85.wav"

print(f"测试音频: {test_audio}")
print(f"文件存在: {os.path.exists(test_audio)}")
print()

try:
    # 尝试加载音频
    audio = load_audio(test_audio, 40000)
    print(f"[OK] 音频加载成功!")
    print(f"   音频长度: {len(audio)} 采样点")
    print(f"   音频时长: {len(audio)/40000:.2f} 秒")
except Exception as e:
    print(f"[ERROR] 音频加载失败: {e}")
    import traceback
    traceback.print_exc()
