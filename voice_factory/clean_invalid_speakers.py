#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理无效的声模训练数据
清除 speaker_0001 到 speaker_0021 的所有训练产物
"""

import os
import shutil
from pathlib import Path

def clean_invalid_speakers():
    """清理无效的 speaker 训练数据"""
    rvc_logs_dir = Path(r"W:\rvc\logs")
    rvc_weights_dir = Path(r"W:\rvc\assets\weights")
    fish_voice_factory_dir = Path(r"w:\fish-speech-1.5.1\voice_factory")
    
    print("="*70)
    print("🧹 清理无效声模训练数据")
    print("="*70)
    
    # 清理范围：speaker_0001 到 speaker_0021
    speakers_to_clean = [f"speaker_{i:04d}" for i in range(1, 22)]
    
    cleaned_count = 0
    
    # 1. 清理 RVC logs 目录
    print("\n📁 清理 RVC logs 目录...")
    for speaker in speakers_to_clean:
        speaker_dir = rvc_logs_dir / speaker
        if speaker_dir.exists():
            try:
                shutil.rmtree(speaker_dir)
                print(f"  ✅ 已删除: {speaker_dir}")
                cleaned_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败 {speaker}: {e}")
    
    # 2. 清理 RVC weights 目录中的对应文件
    print("\n📁 清理 RVC weights 目录...")
    if rvc_weights_dir.exists():
        for speaker in speakers_to_clean:
            weight_file = rvc_weights_dir / f"{speaker}.pth"
            if weight_file.exists():
                try:
                    weight_file.unlink()
                    print(f"  ✅ 已删除: {weight_file}")
                except Exception as e:
                    print(f"  ❌ 删除失败 {weight_file}: {e}")
    
    # 3. 清理 voice_factory 中的中间产物
    print("\n📁 清理 voice_factory 中间产物...")
    for sub_dir in ["outputs", "enhanced", "filtered", "voice_database"]:
        dir_path = fish_voice_factory_dir / sub_dir
        if dir_path.exists():
            for speaker in speakers_to_clean:
                speaker_subdir = dir_path / speaker
                if speaker_subdir.exists():
                    try:
                        shutil.rmtree(speaker_subdir)
                        print(f"  ✅ 已删除: {speaker_subdir}")
                    except Exception as e:
                        print(f"  ❌ 删除失败 {speaker_subdir}: {e}")
    
    # 4. 清理数据库记录
    print("\n📁 清理数据库记录...")
    db_path = fish_voice_factory_dir / "trained_voices_db.json"
    if db_path.exists():
        try:
            import json
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
            
            original_count = db.get('total_count', 0)
            
            # 保留不在清理范围内的声模
            db['trained_voices'] = [
                voice for voice in db['trained_voices'] 
                if voice.get('id') not in speakers_to_clean
            ]
            db['total_count'] = len(db['trained_voices'])
            
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ 数据库已更新: {original_count} -> {db['total_count']} 条记录")
        except Exception as e:
            print(f"  ❌ 数据库清理失败: {e}")
    
    print(f"\n📊 清理完成:")
    print(f"   共清理 {cleaned_count} 个 speaker 目录")
    print(f"   清理范围: speaker_0001 ~ speaker_0021")
    print(f"   剩余有效声模: 0 个（从零开始）")
    print()
    print("✅ 无效训练数据已完全清除！")
    print("💡 现在可以重新开始声模工厂训练流程")
    print("="*70)


if __name__ == "__main__":
    clean_invalid_speakers()
