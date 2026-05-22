#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人物画像到声模完整流程
从人物画像描述到完整声模训练的端到端自动化
"""

import os
import sys
import json
import argparse
from typing import Optional
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_voice_generator import generate_voice_from_portrait
from portrait_to_tts_config import get_portrait_info


def get_next_speaker_id(rvc_logs_dir: str = "W:\\rvc\\logs") -> int:
    """获取下一个可用的 speaker ID"""
    if not os.path.exists(rvc_logs_dir):
        return 1
    
    existing_speakers = []
    for item in os.listdir(rvc_logs_dir):
        if item.startswith("speaker_") and item[8:].isdigit():
            speaker_num = int(item[8:])
            existing_speakers.append(speaker_num)
    
    if existing_speakers:
        return max(existing_speakers) + 1
    else:
        return 1


def run_dsp_enhancement(audio_dir: str) -> str:
    """
    运行 DSP 增强处理
    
    Args:
        audio_dir: 音频目录
    
    Returns:
        str: 增强后的目录路径
    """
    print(f"\n[2/6] DSP 增强处理...")
    
    # 这里复用现有的 dsp_enhancer.py
    # 简化版本：直接返回原目录（实际应该调用 DSP 增强）
    enhanced_dir = audio_dir.replace("outputs", "enhanced")
    os.makedirs(enhanced_dir, exist_ok=True)
    
    print(f"⚠️  DSP 增强功能需要集成 dsp_enhancer.py")
    print(f"💡 暂时使用原始音频进行训练")
    
    return audio_dir


def run_quality_filter(audio_dir: str) -> str:
    """
    运行质量筛选
    
    Args:
        audio_dir: 音频目录
    
    Returns:
        str: 筛选后的目录路径
    """
    print(f"\n[3/6] 质量筛选...")
    
    # 这里复用现有的 quality_filter.py
    filtered_dir = audio_dir.replace("outputs", "filtered")
    os.makedirs(filtered_dir, exist_ok=True)
    
    print(f"⚠️  质量筛选功能需要集成 quality_filter.py")
    print(f"💡 暂时使用全部音频进行训练")
    
    # 复制所有音频到 filtered 目录
    import shutil
    for file in os.listdir(audio_dir):
        if file.endswith(".wav"):
            src = os.path.join(audio_dir, file)
            dst = os.path.join(filtered_dir, file)
            shutil.copy2(src, dst)
    
    audio_count = len([f for f in os.listdir(filtered_dir) if f.endswith(".wav")])
    print(f"✅ 筛选通过 {audio_count} 句音频")
    
    return filtered_dir


def prepare_rvc_training_data(filtered_dir: str, speaker_name: str) -> str:
    """
    准备 RVC 训练数据
    
    Args:
        filtered_dir: 筛选后的音频目录
        speaker_name: speaker 名称
    
    Returns:
        str: RVC 训练数据目录
    """
    print(f"\n[4/6] 准备 RVC 训练数据...")
    
    # 创建 RVC 训练数据目录
    rvc_data_dir = os.path.join("voice_database", speaker_name)
    os.makedirs(rvc_data_dir, exist_ok=True)
    
    # 复制音频文件
    import shutil
    audio_count = 0
    for file in os.listdir(filtered_dir):
        if file.endswith(".wav"):
            src = os.path.join(filtered_dir, file)
            dst = os.path.join(rvc_data_dir, file)
            shutil.copy2(src, dst)
            audio_count += 1
    
    print(f"✅ 已复制 {audio_count} 句音频到 {rvc_data_dir}")
    
    return rvc_data_dir


def train_rvc_model(rvc_data_dir: str, speaker_name: str, epochs: int = 50):
    """
    训练 RVC 声模
    
    Args:
        rvc_data_dir: RVC 训练数据目录
        speaker_name: speaker 名称
        epochs: 训练轮数
    """
    print(f"\n[5/6] RVC 训练...")
    print(f"⚠️  RVC 训练功能需要集成 rvc_full_auto_train.py")
    print(f"💡 请手动运行训练:")
    print(f"   python rvc_full_auto_train.py --speakers {speaker_name} --epochs {epochs}")
    print(f"\n训练完成后，请按 Enter 继续...")
    
    # 这里应该调用 rvc_full_auto_train.py
    # 由于训练时间较长，暂时改为手动执行
    input()


def add_portrait_to_database(speaker_name: str, portrait: str, tts_params: dict):
    """
    添加人物画像到数据库
    
    Args:
        speaker_name: speaker 名称
        portrait: 人物画像
        tts_params: TTS 参数
    """
    print(f"\n[6/6] 添加人物画像到数据库...")
    
    # 加载现有数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_voices_db.json")
    
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    else:
        db = {"trained_voices": [], "total_count": 0}
    
    # 获取画像信息
    portrait_info = get_portrait_info(portrait)
    
    # 创建新的声模条目
    voice_entry = {
        "id": speaker_name,
        "name": f"已训练声模 - {speaker_name}",
        "portrait": portrait,
        "description": portrait_info.get('description', ''),
        "portrait_details": {
            "age_range": "未知",
            "gender": "未知",
            "voice_type": "未知",
            "tone": portrait,
            "suitable_scenes": [],
            "characteristics": portrait_info.get('description', ''),
            "generated_by_tts": True,
            "tts_params": tts_params
        },
        "speaker_dir": f"W:\\rvc\\logs\\{speaker_name}",
        "model_v2": f"W:\\rvc\\logs\\{speaker_name}\\{speaker_name}_v2.pth",
        "model_g": f"W:\\rvc\\logs\\{speaker_name}\\G_50.pth",
        "index_file": f"W:\\rvc\\logs\\{speaker_name}\\added_50.index",
        "embedding": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "generation_method": "TTS从人物画像生成"
    }
    
    # 添加到数据库
    db['trained_voices'].append(voice_entry)
    db['total_count'] = len(db['trained_voices'])
    
    # 保存数据库
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 声模 {speaker_name} 已添加到数据库")
    print(f"   画像: {portrait}")
    print(f"   描述: {portrait_info.get('description', '')}")


def portrait_to_voice_model(
    portrait: str,
    speaker_id: Optional[int] = None,
    epochs: int = 50,
    num_sentences: int = 30
):
    """
    从人物画像生成完整声模
    
    Args:
        portrait: 人物画像描述
        speaker_id: 指定 speaker 编号（可选）
        epochs: 训练轮数
        num_sentences: 生成句子数
    """
    print("\n" + "="*70)
    print("🎤 人物画像声模生成系统")
    print("="*70)
    print(f"\n📋 任务信息:")
    print(f"   人物画像: {portrait}")
    print(f"   训练轮数: {epochs}")
    print(f"   生成句子: {num_sentences}")
    print()
    
    # 1. 确定 speaker ID
    if speaker_id is None:
        speaker_id = get_next_speaker_id()
    speaker_name = f"speaker_{speaker_id:04d}"
    
    print(f"🆔 Speaker ID: {speaker_name}")
    
    # 2. 生成声音
    print(f"\n[1/6] 生成 {portrait} 的声音...")
    output_dir = os.path.join("outputs", speaker_name)
    result = generate_voice_from_portrait(portrait, output_dir, num_sentences)
    
    if result["success"] == 0:
        print("❌ 声音生成失败，流程终止")
        return
    
    # 3. DSP 增强
    enhanced_dir = run_dsp_enhancement(output_dir)
    
    # 4. 质量筛选
    filtered_dir = run_quality_filter(enhanced_dir)
    
    # 5. 准备训练数据
    rvc_data_dir = prepare_rvc_training_data(filtered_dir, speaker_name)
    
    # 6. RVC 训练
    train_rvc_model(rvc_data_dir, speaker_name, epochs)
    
    # 7. 添加人物画像到数据库
    tts_params = result["metadata"]["params"]
    add_portrait_to_database(speaker_name, portrait, tts_params)
    
    # 完成
    print("\n" + "="*70)
    print("🎉 声模生成完成！")
    print("="*70)
    print(f"\n✅ 声模: {speaker_name}")
    print(f"   画像: {portrait}")
    print(f"   位置: W:\\rvc\\logs\\{speaker_name}")
    print(f"   模型: {speaker_name}_v2.pth")
    print("="*70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="人物画像声模生成系统")
    parser.add_argument("portrait", help="人物画像描述")
    parser.add_argument("--speaker-id", type=int, default=None, help="指定 speaker 编号")
    parser.add_argument("--epochs", type=int, default=50, help="训练轮数")
    parser.add_argument("--sentences", type=int, default=30, help="生成句子数")
    
    args = parser.parse_args()
    
    portrait_to_voice_model(
        args.portrait,
        args.speaker_id,
        args.epochs,
        args.sentences
    )


if __name__ == "__main__":
    main()
