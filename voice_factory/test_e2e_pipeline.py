#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
方案C Step 3: 端到端完整流程测试
测试从角色描述到完整声模的一键生成流程
"""

import os
import sys
import time
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_matcher import PortraitMatcher
from portrait_to_model_v2 import portrait_to_voice_model_v2


# 测试用例
TEST_CASES = [
    {
        "name": "测试1: 预设画像-中年男中音",
        "portrait": "中年男中音",
        "expected_reference": "Ethan",
        "expected_gender": "male",
        "expected_age": "middle_aged",
        "epochs": 10,  # 测试用少量epoch
        "auto_confirm": True
    },
    {
        "name": "测试2: 预设画像-青年女高音",
        "portrait": "青年女高音",
        "expected_reference": "Sarah",
        "expected_gender": "female",
        "expected_age": "young",
        "epochs": 10,
        "auto_confirm": True
    },
    {
        "name": "测试3: 自定义描述-老年男性",
        "portrait": "成熟稳重的老年男性声音，音色沧桑厚重",
        "expected_reference": None,  # 自动匹配
        "expected_gender": "male",
        "expected_age": "old",
        "epochs": 10,
        "auto_confirm": True
    },
    {
        "name": "测试4: 自定义描述-年轻女孩",
        "portrait": "活泼可爱的年轻女孩声音，音色甜美明亮",
        "expected_reference": None,
        "expected_gender": "female",
        "expected_age": "young",
        "epochs": 10,
        "auto_confirm": True
    },
    {
        "name": "测试5: 自定义描述-中年大叔",
        "portrait": "深沉磁性的中年大叔声音",
        "expected_reference": None,
        "expected_gender": "male",
        "expected_age": "middle_aged",
        "epochs": 10,
        "auto_confirm": True
    }
]


def test_matching_only():
    """仅测试智能匹配（不训练）"""
    print("="*70)
    print("方案C Step 3: 智能匹配测试")
    print("="*70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    matcher = PortraitMatcher()
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'='*70}")
        print(f"{test_case['name']}")
        print(f"{'='*70}")
        print(f"输入: {test_case['portrait']}")
        
        # 测试智能匹配
        result = matcher.match_reference(test_case['portrait'])
        
        if result:
            print(f"匹配结果:")
            print(f"  Reference: {result['name']}")
            print(f"  ID: {result['reference_id'][:16]}...")
            print(f"  置信度: {result['confidence']}")
            print(f"  提取特征: {result.get('extracted_features', {})}")
            
            # 验证匹配结果
            gender_match = result.get('extracted_features', {}).get('gender') == test_case['expected_gender']
            age_match = result.get('extracted_features', {}).get('age_group') == test_case['expected_age']
            
            if test_case['expected_reference']:
                ref_match = result['name'] == test_case['expected_reference']
            else:
                ref_match = True  # 自定义描述不检查具体reference
            
            passed = gender_match and age_match and ref_match
            
            if passed:
                print(f"  [PASS] 匹配验证通过")
            else:
                print(f"  [FAIL] 匹配验证失败")
                if not gender_match:
                    print(f"    性别不匹配: 预期={test_case['expected_gender']}, 实际={result.get('extracted_features', {}).get('gender')}")
                if not age_match:
                    print(f"    年龄段不匹配: 预期={test_case['expected_age']}, 实际={result.get('extracted_features', {}).get('age_group')}")
            
            results.append({
                "test": test_case['name'],
                "passed": passed,
                "reference": result['name'],
                "confidence": result['confidence']
            })
        else:
            print(f"  [FAIL] 未找到匹配")
            results.append({
                "test": test_case['name'],
                "passed": False,
                "reference": None,
                "confidence": 0
            })
    
    # 总结
    print("\n" + "="*70)
    print("智能匹配测试总结")
    print("="*70)
    
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print(f"总计: {total} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    print()
    
    for result in results:
        status = "[PASS]" if result['passed'] else "[FAIL]"
        print(f"  {status} {result['test']}")
        if result['reference']:
            print(f"       Reference: {result['reference']} (confidence: {result['confidence']})")
    
    print("="*70)
    
    return passed == total


def test_full_pipeline(test_case_index=0, dry_run=False):
    """测试完整流程（仅运行指定的测试用例）"""
    test_case = TEST_CASES[test_case_index]
    
    print("\n" + "="*70)
    print(f"方案C Step 3: 端到端完整流程测试")
    print("="*70)
    print(f"测试用例: {test_case['name']}")
    print(f"角色描述: {test_case['portrait']}")
    print(f"训练Epochs: {test_case['epochs']} (测试用)")
    print(f"自动确认: {test_case['auto_confirm']}")
    print()
    
    if dry_run:
        print("[DRY RUN] 仅显示计划，不实际执行")
        print()
        print("预期流程:")
        print("  [1/6] 智能匹配reference_id...")
        print("  [2/6] 生成TTS音频（使用reference_id）...")
        print("  [3/6] DSP 增强处理...")
        print("  [4/6] 质量筛选...")
        print("  [5/6] 准备 RVC 训练数据...")
        print("  [6/6] 训练 RVC 模型...")
        print()
        print("预期输出:")
        print("  - 生成30句TTS音频")
        print("  - DSP增强后的音频")
        print("  - RVC训练数据")
        print("  - RVC模型文件 (G_10.pth)")
        return True
    
    try:
        start_time = time.time()
        
        # 调用完整流程V2
        result = portrait_to_voice_model_v2(
            portrait=test_case['portrait'],
            epochs=test_case['epochs'],
            auto_confirm=test_case['auto_confirm']
        )
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print("端到端测试完成")
        print("="*70)
        print(f"总耗时: {elapsed/60:.1f} 分钟")
        print(f"结果: {result}")
        print("="*70)
        
        return result.get('success', False)
        
    except KeyboardInterrupt:
        print("\n[INTERRUPT] 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*70)
    print("方案C Step 3: 端到端完整流程测试")
    print("="*70)
    print()
    print("测试计划:")
    print("  1. 智能匹配测试（5个用例）- 快速验证")
    print("  2. 完整流程测试（1个用例）- 端到端验证")
    print()
    print("注意:")
    print("  - 完整流程测试将实际训练RVC模型")
    print("  - 使用10个epoch进行快速测试")
    print("  - 预计耗时: 5-10分钟")
    print()
    
    # 步骤1: 智能匹配测试
    print("开始步骤1: 智能匹配测试")
    matching_passed = test_matching_only()
    
    if not matching_passed:
        print("\n[WARN] 智能匹配测试未全部通过，但仍可继续完整流程测试")
    
    # 步骤2: 完整流程测试
    print("\n")
    response = input("是否继续完整流程测试？(y/n/dry_run): ").strip().lower()
    
    if response == 'y':
        print("\n开始步骤2: 完整流程测试")
        # 测试第一个用例（中年男中音）
        full_passed = test_full_pipeline(test_case_index=0, dry_run=False)
        
        if full_passed:
            print("\n[PASS] 端到端完整流程测试通过！")
            print("\n下一步:")
            print("  1. 使用更多epoch（300）训练完整模型")
            print("  2. 测试5个不同声模的变声效果")
            print("  3. 验证声音区分度")
        else:
            print("\n[FAIL] 端到端完整流程测试失败")
            print("\n请检查:")
            print("  1. Fish Speech API是否运行")
            print("  2. RVC训练环境是否正常")
            print("  3. 磁盘空间是否充足")
    
    elif response == 'dry_run':
        print("\n开始步骤2: 完整流程测试（Dry Run）")
        test_full_pipeline(test_case_index=0, dry_run=True)
    
    else:
        print("\n[CANCEL] 跳过完整流程测试")
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="方案C Step 3: 端到端完整流程测试")
    parser.add_argument("--matching-only", action="store_true", help="仅测试智能匹配")
    parser.add_argument("--full-pipeline", type=int, help="测试完整流程（指定测试用例索引）")
    parser.add_argument("--dry-run", action="store_true", help="仅显示计划，不实际执行")
    
    args = parser.parse_args()
    
    if args.matching_only:
        test_matching_only()
    elif args.full_pipeline is not None:
        test_full_pipeline(args.full_pipeline, args.dry_run)
    else:
        main()
