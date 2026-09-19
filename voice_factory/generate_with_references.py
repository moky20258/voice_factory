#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用Fish Audio预设声音重新生成训练数据
方案B：使用真实的reference_id来生成不同的声音特征
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# API配置
API_URL = "http://127.0.0.1:8080/v1/tts"

# 定义5个不同的声模画像和对应的reference_id
# 这些reference_id来自Fish Audio官方预设声音
PORTRAITS = [
    {
        "name": "中年男中音",
        "description": "成熟稳重的中年男性声音，音色浑厚温暖",
        "reference_id": "536d3a5e000945adb7038665781a4aca",  # Ethan - 男性声音
        "speaker_id": None  # 将动态分配
    },
    {
        "name": "青年女高音",
        "description": "清亮甜美的年轻女性声音，音色明亮活泼",
        "reference_id": "933563129e564b19a115bedd57b7406a",  # Sarah - 女性声音
        "speaker_id": None
    },
    {
        "name": "中年男低音",
        "description": "深沉厚重的中年男性声音，音色低沉磁性",
        "reference_id": "bf322df2096a46f18c579d0baa36f41d",  # Adrian - 男性声音
        "speaker_id": None
    },
    {
        "name": "青年女中音",
        "description": "温柔知性的年轻女性声音，音色柔和亲切",
        "reference_id": "b347db033a6549378b48d00acb0d06cd",  # Selene - 女性声音
        "speaker_id": None
    },
    {
        "name": "青年男高音",
        "description": "明亮活力的年轻男性声音，音色清朗阳光",
        "reference_id": "802e3bc2b27e49c2995d23ef70e6ac89",  # Energetic Male - 活力男性声音
        "speaker_id": None
    }
]

# 文本目录
TEXT_DIR = "texts"
OUTPUT_DIR = "outputs"
META_DIR = "metadata"

# 每个speaker生成30句
LINES_PER_SPEAKER = 30

# 采样参数（保持稳定，主要靠reference_id区分声音）
TEMPERATURE = 0.75
TOP_P = 0.85
REPETITION_PENALTY = 1.15


def get_next_available_speaker_id():
    """获取下一个可用的speaker ID"""
    import re
    
    max_id = 0
    
    # 检查 RVC logs 目录
    rvc_logs = Path(r"W:\rvc\logs")
    if rvc_logs.exists():
        for item in os.listdir(rvc_logs):
            match = re.match(r'speaker_(\d+)', item)
            if match:
                max_id = max(max_id, int(match.group(1)))
    
    # 检查 outputs 目录
    outputs_dir = Path(OUTPUT_DIR)
    if outputs_dir.exists():
        for item in os.listdir(outputs_dir):
            match = re.match(r'speaker_(\d+)', item)
            if match:
                max_id = max(max_id, int(match.group(1)))
    
    return max_id + 1


def load_texts():
    """加载texts目录下的所有文本"""
    texts = []
    
    if not os.path.exists(TEXT_DIR):
        print(f"[ERROR] 文本目录不存在: {TEXT_DIR}")
        return texts
    
    for file in sorted(os.listdir(TEXT_DIR)):
        if file.endswith(".txt"):
            path = os.path.join(TEXT_DIR, file)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
                if content:
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    texts.extend(lines)
    
    print(f"[OK] 加载文本数量: {len(texts)}")
    return texts


def generate_audio_with_reference(text, reference_id, output_path, retries=3):
    """使用reference_id生成音频"""
    
    payload = {
        "text": text,
        "reference_id": reference_id,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "repetition_penalty": REPETITION_PENALTY,
        "format": "wav",
        "chunk_length": 200
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                # 保存音频文件
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"  [WARN] API返回错误: {response.status_code}, {response.text[:100]}")
                
        except Exception as e:
            print(f"  [WARN] 请求失败 (尝试 {attempt+1}/{retries}): {e}")
            time.sleep(2)
    
    return False


def generate_speaker_audio(portrait, texts, speaker_id):
    """为单个声模生成音频"""
    
    portrait_name = portrait["name"]
    reference_id = portrait["reference_id"]
    
    print(f"\n{'='*70}")
    print(f"[INFO] 生成声模: {portrait_name} (speaker_{speaker_id:04d})")
    print(f"[INFO] 参考声音ID: {reference_id}")
    print(f"[INFO] 描述: {portrait['description']}")
    print(f"{'='*70}")
    
    # 创建输出目录
    speaker_dir = os.path.join(OUTPUT_DIR, f"speaker_{speaker_id:04d}")
    os.makedirs(speaker_dir, exist_ok=True)
    
    # 保存metadata
    meta_path = os.path.join(META_DIR, f"speaker_{speaker_id:04d}.json")
    os.makedirs(META_DIR, exist_ok=True)
    
    metadata = {
        "speaker": f"speaker_{speaker_id:04d}",
        "portrait": portrait_name,
        "description": portrait["description"],
        "reference_id": reference_id,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "params": {
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "repetition_penalty": REPETITION_PENALTY
        }
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 生成音频
    generated_count = 0
    for i in range(LINES_PER_SPEAKER):
        if i >= len(texts):
            print(f"  [WARN] 文本不足，已生成 {generated_count} 句")
            break
        
        text = texts[i]
        output_file = os.path.join(speaker_dir, f"{i:04d}.wav")
        
        # 如果文件已存在，跳过
        if os.path.exists(output_file):
            print(f"  [SKIP] {i:04d}.wav 已存在")
            generated_count += 1
            continue
        
        print(f"  [{i+1}/{LINES_PER_SPEAKER}] 生成 {i:04d}.wav...")
        
        if generate_audio_with_reference(text, reference_id, output_file):
            generated_count += 1
        else:
            print(f"  [ERROR] 生成失败: {i:04d}.wav")
        
        # 避免请求过快
        time.sleep(0.5)
    
    print(f"\n[OK] {portrait_name} 生成完成: {generated_count}/{LINES_PER_SPEAKER} 句")
    return generated_count


def main(auto_confirm=False):
    print("=" * 70)
    print("方案B：使用Fish Audio预设声音重新生成训练数据")
    print("=" * 70)
    print()
    print("计划:")
    for i, portrait in enumerate(PORTRAITS, 1):
        print(f"  {i}. {portrait['name']} - {portrait['description']}")
        print(f"     Reference ID: {portrait['reference_id']}")
    print()
    print("注意:")
    print("  - 每个声模生成30句音频")
    print("  - 使用不同的reference_id确保声音特征不同")
    print("  - 总共约需 15-30 分钟")
    print()
    
    if not auto_confirm:
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
    else:
        print("[AUTO] 自动确认模式，开始执行...")
        print()
    
    # 加载文本
    texts = load_texts()
    if len(texts) < LINES_PER_SPEAKER * len(PORTRAITS):
        print(f"[ERROR] 文本不足！需要 {LINES_PER_SPEAKER * len(PORTRAITS)} 句，实际 {len(texts)} 句")
        return
    
    # 为每个声模分配speaker_id（先获取一个基础ID，然后递增）
    base_id = get_next_available_speaker_id()
    for i, portrait in enumerate(PORTRAITS):
        portrait["speaker_id"] = base_id + i
        print(f"[INFO] {portrait['name']} -> speaker_{portrait['speaker_id']:04d}")
    
    print()
    
    # 生成音频
    total_generated = 0
    for i, portrait in enumerate(PORTRAITS, 1):
        print(f"\n{'='*70}")
        print(f"进度: {i}/{len(PORTRAITS)}")
        print(f"{'='*70}")
        
        count = generate_speaker_audio(
            portrait,
            texts[(i-1)*LINES_PER_SPEAKER : i*LINES_PER_SPEAKER],
            portrait["speaker_id"]
        )
        total_generated += count
        
        print(f"\n[OK] 已完成 {i}/{len(PORTRAITS)} 个声模")
    
    print(f"\n{'='*70}")
    print(f"[SUMMARY] 生成完成！")
    print(f"[SUMMARY] 总计生成: {total_generated} 句音频")
    print(f"[SUMMARY] 声模数量: {len(PORTRAITS)} 个")
    print(f"{'='*70}")
    print()
    print("下一步: 运行完整的训练流程 (DSP增强 -> 质量筛选 -> RVC训练)")


if __name__ == "__main__":
    main(auto_confirm=True)
