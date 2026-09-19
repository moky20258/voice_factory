#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
方案B: 批量训练5个声模（使用已生成的音频）
从outputs目录读取已生成的150句音频，进行DSP增强和RVC训练
"""

import os
import sys
import time
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_to_voice_model import run_dsp_enhancement, run_quality_filter, prepare_rvc_training_data, train_rvc_model


# 5个声模配置
SPEAKERS = [
    {
        "id": "speaker_0024",
        "name": "中年男中音",
        "reference": "Ethan",
        "description": "成熟稳重的中年男性声音，音色浑厚温暖"
    },
    {
        "id": "speaker_0025",
        "name": "青年女高音",
        "reference": "Sarah",
        "description": "清亮甜美的年轻女性声音，音色明亮活泼"
    },
    {
        "id": "speaker_0026",
        "name": "中年男低音",
        "reference": "Adrian",
        "description": "深沉厚重的中年男性声音，音色低沉磁性"
    },
    {
        "id": "speaker_0027",
        "name": "青年女中音",
        "reference": "Selene",
        "description": "温柔知性的年轻女性声音，音色柔和亲切"
    },
    {
        "id": "speaker_0028",
        "name": "青年男高音",
        "reference": "Energetic Male",
        "description": "明亮活力的年轻男性声音，音色清朗阳光"
    }
]

VOICE_FACTORY_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(VOICE_FACTORY_DIR, "outputs")
RVC_DIR = r"W:\rvc"


def train_single_speaker(speaker_config, epochs=300, auto_confirm=False):
    """训练单个声模"""
    speaker_id = speaker_config["id"]
    speaker_name = speaker_config["name"]
    reference = speaker_config["reference"]
    description = speaker_config["description"]
    
    print("\n" + "="*70)
    print(f"开始训练: {speaker_name} ({speaker_id})")
    print(f"参考声音: {reference}")
    print(f"描述: {description}")
    print("="*70)
    
    start_time = time.time()
    
    # 步骤1: 检查音频是否已生成
    audio_dir = os.path.join(OUTPUTS_DIR, speaker_id)
    if not os.path.exists(audio_dir):
        print(f"[ERROR] 音频目录不存在: {audio_dir}")
        return False
    
    wav_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    if len(wav_files) == 0:
        print(f"[ERROR] 音频目录为空: {audio_dir}")
        return False
    
    print(f"\n[1/4] 检查音频文件...")
    print(f"  找到 {len(wav_files)} 个音频文件")
    
    # 步骤2: DSP增强处理
    print(f"\n[2/4] DSP 增强处理...")
    try:
        enhanced_dir = run_dsp_enhancement(audio_dir)
        enhanced_count = len([f for f in os.listdir(enhanced_dir) if f.endswith('.wav')])
        print(f"[OK] DSP 增强完成: {enhanced_count} 个音频")
    except Exception as e:
        print(f"[ERROR] DSP 增强失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 步骤3: 质量筛选（可选，如果文件占用问题则跳过）
    print(f"\n[3/4] 质量筛选...")
    try:
        filtered_dir = run_quality_filter(enhanced_dir)
        filtered_count = len([f for f in os.listdir(filtered_dir) if f.endswith('.wav')])
        print(f"[OK] 质量筛选完成: {filtered_count} 个音频")
    except Exception as e:
        print(f"[WARN] 质量筛选跳过（直接使用DSP增强后的音频）: {e}")
        filtered_dir = enhanced_dir
        filtered_count = enhanced_count
    
    # 步骤4: 准备RVC训练数据
    print(f"\n[4/4] 准备 RVC 训练数据...")
    try:
        rvc_data_dir = prepare_rvc_training_data(filtered_dir, speaker_id)
        print(f"[OK] 已复制 {filtered_count} 个音频到 {rvc_data_dir}")
    except Exception as e:
        print(f"[ERROR] 准备RVC数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 步骤5: 训练RVC模型
    print(f"\n[5/5] 训练 RVC 模型...")
    print(f"  Epochs: {epochs}")
    print(f"  音频数量: {filtered_count}")
    print(f"  预计耗时: 20-40 分钟")
    
    if not auto_confirm:
        confirm = input("  开始训练？(y/n): ").strip().lower()
        if confirm != 'y':
            print("[CANCEL] 跳过此声模")
            return False
    
    try:
        model_path = train_rvc_model(rvc_data_dir, speaker_id, epochs)
        print(f"[OK] RVC 模型训练完成")
        print(f"  模型路径: {model_path}")
    except Exception as e:
        print(f"[ERROR] RVC 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] {speaker_name} 训练完成！")
    print(f"  总耗时: {elapsed/60:.1f} 分钟")
    print(f"  模型路径: W:\\rvc\\logs\\{speaker_id}\\")
    
    return True


def main(auto_confirm=False):
    print("="*70)
    print("方案B: 批量训练5个声模")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("训练计划:")
    for i, speaker in enumerate(SPEAKERS, 1):
        print(f"  {i}. {speaker['name']} ({speaker['id']})")
        print(f"     参考: {speaker['reference']}")
        print(f"     描述: {speaker['description']}")
    print()
    print("注意:")
    print("  - 每个声模约需 30-60 分钟")
    print("  - 总共约需 2.5-5 小时")
    print("  - Epochs: 300（安全值，避免posterior collapse）")
    print()
    
    if not auto_confirm:
        confirm = input("是否开始训练？(y/n): ").strip().lower()
        if confirm != 'y':
            print("[CANCEL] 已取消训练")
            return
    else:
        print("[AUTO] 自动确认模式，开始训练...")
        print()
    
    success_count = 0
    fail_count = 0
    
    for i, speaker in enumerate(SPEAKERS, 1):
        print(f"\n{'='*70}")
        print(f"进度: {i}/5")
        print(f"{'='*70}")
        
        try:
            success = train_single_speaker(speaker, epochs=300, auto_confirm=auto_confirm)
            if success:
                success_count += 1
            else:
                fail_count += 1
        except KeyboardInterrupt:
            print(f"\n[INTERRUPT] 训练被用户中断")
            break
        except Exception as e:
            fail_count += 1
            print(f"\n[ERROR] 训练异常: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n当前进度: {i}/5")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        
        # 如果不是最后一个，等待一下
        if i < len(SPEAKERS):
            print(f"\n等待10秒后开始下一个声模...")
            time.sleep(10)
    
    # 总结
    print("\n" + "="*70)
    print("批量训练完成！")
    print("="*70)
    print(f"  总计: 5")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print()
    
    if success_count > 0:
        print("成功的声模:")
        for speaker in SPEAKERS:
            speaker_id = speaker["id"]
            model_path = f"W:\\rvc\\logs\\{speaker_id}\\G_300.pth"
            if os.path.exists(model_path):
                print(f"  [OK] {speaker['name']} ({speaker_id})")
                print(f"       模型: {model_path}")
    
    print()
    print("下一步:")
    print("  1. 使用 RVC GUI 测试变声效果")
    print("  2. 使用实时变声功能测试")
    print("  3. 验证5个声模的声音是否有明显区别")
    print("="*70)
    
    end_time = datetime.now()
    print(f"\n结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="方案B: 批量训练5个声模")
    parser.add_argument("--auto-confirm", action="store_true", help="自动确认，无需手动输入")
    parser.add_argument("--epochs", type=int, default=300, help="训练轮数（默认300）")
    
    args = parser.parse_args()
    
    main(auto_confirm=args.auto_confirm)
