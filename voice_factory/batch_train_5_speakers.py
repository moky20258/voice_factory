#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量训练5个新声模
从零开始，训练5个不同的人物画像声模
"""

import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_to_voice_model import portrait_to_voice_model

# 定义5个不同的声模画像
def get_next_available_speaker_id():
    """获取下一个可用的speaker ID（检查RVC logs和outputs目录）"""
    import re
    
    max_id = 0
    
    # 检查 RVC logs 目录
    rvc_logs = r"W:\rvc\logs"
    if os.path.exists(rvc_logs):
        for item in os.listdir(rvc_logs):
            match = re.match(r'speaker_(\d+)', item)
            if match:
                max_id = max(max_id, int(match.group(1)))
    
    # 检查 outputs 目录
    outputs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    if os.path.exists(outputs_dir):
        for item in os.listdir(outputs_dir):
            match = re.match(r'speaker_(\d+)', item)
            if match:
                max_id = max(max_id, int(match.group(1)))
    
    return max_id + 1

PORTRAITS = [
    "中年男中音",    # 成熟稳重的中年男性声音
    "青年女高音",    # 清亮甜美的年轻女性声音  
    "中年男低音",    # 深沉厚重的中年男性声音
    "青年女中音",    # 温柔知性的年轻女性声音
    "青年男高音",    # 明亮活力的年轻男性声音
]

def main(auto_confirm=False):
    print("="*70)
    print("批量训练5个新声模")
    print("="*70)
    print()
    print("训练计划:")
    for i, portrait in enumerate(PORTRAITS, 1):
        print(f"  {i}. {portrait}")
    print()
    print("注意:")
    print("  - 每个声模约需 30-60 分钟")
    print("  - 总共约需 2.5-5 小时")
    print("  - 请确保 Fish Speech API 已启动")
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
    
    for i, portrait in enumerate(PORTRAITS, 1):
        # 为每个声模获取新的ID
        speaker_id = get_next_available_speaker_id()
        
        print()
        print("="*70)
        print(f"开始训练第 {i}/5 个声模: {portrait} (speaker_{speaker_id:04d})")
        print("="*70)
        
        try:
            portrait_to_voice_model(
                portrait=portrait,
                speaker_id=speaker_id,  # 使用新分配的ID
                epochs=300,       # 训练300轮（安全值）
                num_sentences=30  # 生成30句音频
            )
            success_count += 1
            print()
            print(f"成功: {portrait} 训练成功！")
        except KeyboardInterrupt:
            print()
            print(f"训练被用户中断")
            break
        except Exception as e:
            fail_count += 1
            print()
            print(f"训练失败: {portrait}")
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print(f"当前进度: {success_count + fail_count}/5")
        print(f"   成功: {success_count}")
        print(f"   失败: {fail_count}")
    
    print()
    print("="*70)
    print("批量训练完成！")
    print("="*70)
    print(f"  总计: 5")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print()
    print(f"模型位置: W:\\rvc\\logs\\speaker_XXXX\\")
    print("使用 RVC GUI 或实时变声测试新训练的声模")
    print("="*70)


if __name__ == "__main__":
    main()
