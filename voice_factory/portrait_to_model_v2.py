#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人物画像到声模完整流程 V2
集成智能匹配引擎和reference_id支持
从角色描述到完整声模训练的端到端自动化
"""

import os
import sys
import json
import argparse
from typing import Optional
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_matcher import PortraitMatcher
from portrait_to_tts_config import get_portrait_info, generate_tts_params
from portrait_to_voice_model import (
    get_next_speaker_id,
    run_dsp_enhancement,
    run_quality_filter,
    prepare_rvc_training_data,
    train_rvc_model
)


def generate_audio_with_reference(portrait: str, speaker_id: int, texts: list, output_dir: str = "outputs") -> str:
    """
    使用reference_id生成TTS音频
    
    Args:
        portrait: 人物画像描述
        speaker_id: speaker ID
        texts: 文本列表
        output_dir: 输出目录
    
    Returns:
        str: 生成的音频目录路径
    """
    print(f"\n[1/6] 生成TTS音频（使用reference_id）...")
    
    # 获取TTS配置（包含reference_id）
    tts_config = generate_tts_params(portrait)
    reference_id = tts_config.get('reference_id')
    reference_name = tts_config.get('reference_name', 'Unknown')
    
    if not reference_id:
        print(f"[ERROR] 未找到reference_id，无法生成音频")
        print(f"[HINT] 请检查portrait_to_tts_config.py中的映射配置")
        return None
    
    print(f"  画像: {portrait}")
    print(f"  Reference: {reference_name} ({reference_id[:8]}...)")
    print(f"  Speaker ID: speaker_{speaker_id:04d}")
    print(f"  音频数量: {len(texts)} 句")
    
    # 创建输出目录
    speaker_dir = os.path.join(output_dir, f"speaker_{speaker_id:04d}")
    os.makedirs(speaker_dir, exist_ok=True)
    
    # 保存metadata
    meta_path = os.path.join("metadata", f"speaker_{speaker_id:04d}.json")
    os.makedirs("metadata", exist_ok=True)
    
    metadata = {
        "speaker": f"speaker_{speaker_id:04d}",
        "portrait": portrait,
        "reference_id": reference_id,
        "reference_name": reference_name,
        "description": tts_config.get('description', ''),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params": {
            "temperature": tts_config['temperature'],
            "top_p": tts_config['top_p'],
            "repetition_penalty": tts_config['repetition_penalty']
        }
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 生成音频（调用generate_with_references.py的逻辑）
    import requests
    import time
    
    API_URL = "http://127.0.0.1:8080/v1/tts"
    generated_count = 0
    
    for i, text in enumerate(texts):
        output_file = os.path.join(speaker_dir, f"{i:04d}.wav")
        
        # 如果文件已存在，跳过
        if os.path.exists(output_file):
            print(f"  [SKIP] {i:04d}.wav 已存在")
            generated_count += 1
            continue
        
        print(f"  [{i+1}/{len(texts)}] 生成 {i:04d}.wav...")
        
        payload = {
            "text": text,
            "reference_id": reference_id,
            "temperature": tts_config['temperature'],
            "top_p": tts_config['top_p'],
            "repetition_penalty": tts_config['repetition_penalty'],
            "format": "wav",
            "chunk_length": 200
        }
        
        try:
            response = requests.post(API_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                with open(output_file, "wb") as f:
                    f.write(response.content)
                generated_count += 1
            else:
                print(f"  [ERROR] API返回错误: {response.status_code}")
                
        except Exception as e:
            print(f"  [ERROR] 请求失败: {e}")
        
        # 避免请求过快
        time.sleep(0.5)
    
    print(f"[OK] TTS音频生成完成: {generated_count}/{len(texts)} 句")
    return speaker_dir


def load_texts(count: int = 30) -> list:
    """加载训练文本"""
    text_dir = "texts"
    texts = []
    
    if not os.path.exists(text_dir):
        print(f"[ERROR] 文本目录不存在: {text_dir}")
        return texts
    
    for file in sorted(os.listdir(text_dir)):
        if file.endswith(".txt"):
            path = os.path.join(text_dir, file)
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
                if content:
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    texts.extend(lines)
    
    # 只取需要的数量
    texts = texts[:count]
    print(f"[OK] 加载文本数量: {len(texts)}")
    return texts


def portrait_to_voice_model_v2(portrait: str, texts: list = None, epochs: int = 300) -> dict:
    """
    从人物画像到声模的完整流程 V2
    
    Args:
        portrait: 人物画像描述
        texts: 文本列表（可选，默认加载30句）
        epochs: 训练轮数
    
    Returns:
        dict: 训练结果
    """
    print("=" * 70)
    print("人物画像到声模完整流程 V2")
    print("=" * 70)
    print(f"画像: {portrait}")
    print()
    
    # 0. 智能匹配reference_id
    print("[0/6] 智能匹配reference_id...")
    matcher = PortraitMatcher()
    match_result = matcher.match_reference(portrait)
    
    if match_result:
        print(f"  匹配成功: {match_result['name']}")
        print(f"  Reference ID: {match_result['reference_id']}")
        print(f"  置信度: {match_result['confidence']}")
        print(f"  原因: {match_result['reason']}")
    else:
        print(f"  [WARN] 未找到匹配的reference_id，将使用默认配置")
    
    # 加载文本
    if texts is None:
        texts = load_texts(30)
    
    if not texts:
        print("[ERROR] 没有可用的训练文本")
        return None
    
    # 获取speaker_id
    speaker_id = get_next_speaker_id()
    speaker_name = f"speaker_{speaker_id:04d}"
    
    print(f"\n[INFO] Speaker ID: {speaker_name}")
    
    # 1. 生成TTS音频
    audio_dir = generate_audio_with_reference(portrait, speaker_id, texts)
    if not audio_dir:
        print("[ERROR] TTS音频生成失败")
        return None
    
    # 2. DSP增强处理
    enhanced_dir = run_dsp_enhancement(audio_dir)
    
    # 3. 质量筛选
    filtered_dir = run_quality_filter(enhanced_dir)
    
    # 4. 准备RVC训练数据
    rvc_data_dir = prepare_rvc_training_data(filtered_dir, speaker_name)
    
    # 5. 训练RVC模型
    model_path = train_rvc_model(rvc_data_dir, speaker_name, epochs)
    
    # 6. 生成训练报告
    result = {
        "speaker_id": speaker_name,
        "portrait": portrait,
        "reference_id": match_result['reference_id'] if match_result else None,
        "reference_name": match_result['name'] if match_result else None,
        "match_confidence": match_result['confidence'] if match_result else None,
        "audio_count": len(texts),
        "model_path": model_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print("\n" + "=" * 70)
    print("训练完成！")
    print("=" * 70)
    print(f"Speaker ID: {speaker_name}")
    print(f"画像: {portrait}")
    if match_result:
        print(f"Reference: {match_result['name']} ({match_result['reference_id']})")
        print(f"匹配置信度: {match_result['confidence']}")
    print(f"模型路径: {model_path}")
    print("=" * 70)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="人物画像到声模完整流程 V2")
    parser.add_argument("--portrait", type=str, required=True, help="人物画像描述")
    parser.add_argument("--texts", type=str, default=None, help="文本文件路径（可选）")
    parser.add_argument("--epochs", type=int, default=300, help="训练轮数")
    parser.add_argument("--auto-confirm", action="store_true", help="自动确认")
    
    args = parser.parse_args()
    
    print(f"画像: {args.portrait}")
    print(f"训练轮数: {args.epochs}")
    print()
    
    if not args.auto_confirm:
        response = input("是否开始训练？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    # 运行完整流程
    result = portrait_to_voice_model_v2(args.portrait, epochs=args.epochs)
    
    if result:
        print("\n[OK] 训练成功完成！")
    else:
        print("\n[ERROR] 训练失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
