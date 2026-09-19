#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
方案C Step 3 自动化测试脚本
测试智能匹配引擎、参考音频数据库和完整流程V2
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_matcher import PortraitMatcher
from portrait_to_tts_config import generate_tts_params
from reference_database import ReferenceDatabase


class TestReporter:
    """测试报告生成器"""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def add_result(self, test_name, passed, details=""):
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "time": datetime.now().strftime("%H:%M:%S")
        })
    
    def generate_report(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        report = []
        report.append("=" * 70)
        report.append("方案C Step 3 自动化测试报告")
        report.append("=" * 70)
        report.append(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总耗时: {(datetime.now() - self.start_time).total_seconds():.1f}秒")
        report.append("")
        report.append(f"总计: {total} 个测试")
        report.append(f"通过: {passed} [PASS]")
        report.append(f"失败: {failed} [FAIL]")
        report.append(f"通过率: {passed/total*100:.1f}%")
        report.append("")
        report.append("-" * 70)
        report.append("测试结果详情:")
        report.append("-" * 70)
        
        for i, result in enumerate(self.results, 1):
            status = "[PASS] 通过" if result['passed'] else "[FAIL] 失败"
            report.append(f"\n{i}. [{status}] {result['test']}")
            report.append(f"   时间: {result['time']}")
            if result['details']:
                report.append(f"   详情: {result['details']}")
        
        report.append("")
        report.append("=" * 70)
        
        if failed == 0:
            report.append("结论: [PASS] 所有测试通过！")
        else:
            report.append(f"结论: [FAIL] {failed}个测试失败，需要修复")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def test_1_preset_portraits(reporter):
    """测试1: 预设画像匹配测试"""
    print("\n" + "=" * 70)
    print("测试1: 预设画像匹配测试")
    print("=" * 70)
    
    test_cases = [
        ("中年男中音", "Ethan", "536d3a5e000945adb7038665781a4aca"),
        ("青年女高音", "Sarah", "933563129e564b19a115bedd57b7406a"),
        ("中年男低音", "Adrian", "bf322df2096a46f18c579d0baa36f41d"),
        ("青年女中音", "Selene", "b347db033a6549378b48d00acb0d06cd"),
        ("青年男高音", "Energetic Male", "802e3bc2b27e49c2995d23ef70e6ac89")
    ]
    
    matcher = PortraitMatcher()
    all_passed = True
    
    for portrait, expected_name, expected_id in test_cases:
        result = matcher.match_reference(portrait)
        
        if result and result['name'] == expected_name and result['reference_id'] == expected_id:
            print(f"  [PASS] {portrait} -> {result['name']} (confidence: {result['confidence']})")
            reporter.add_result(f"预设画像-{portrait}", True, 
                              f"匹配: {result['name']}, 置信度: {result['confidence']}")
        else:
            print(f"  [FAIL] {portrait} -> 预期: {expected_name}, 实际: {result['name'] if result else 'None'}")
            reporter.add_result(f"预设画像-{portrait}", False,
                              f"预期: {expected_name}, 实际: {result['name'] if result else 'None'}")
            all_passed = False
    
    return all_passed


def test_2_custom_portraits(reporter):
    """测试2: 自定义角色描述测试"""
    print("\n" + "=" * 70)
    print("测试2: 自定义角色描述测试")
    print("=" * 70)
    
    test_cases = [
        ("成熟稳重的老年男性声音，音色沧桑厚重", "male", "old"),
        ("活泼可爱的年轻女孩声音，音色甜美明亮", "female", "young"),
        ("深沉磁性的中年大叔声音", "male", "middle_aged"),
        ("温柔优雅的成熟女性声音", "female", None),
        ("阳光帅气的少年声音", "male", "young")
    ]
    
    matcher = PortraitMatcher()
    passed_count = 0
    
    for desc, expected_gender, expected_age in test_cases:
        result = matcher.match_reference(desc)
        
        if result:
            features = result.get('extracted_features', {})
            gender_match = features.get('gender') == expected_gender
            age_match = expected_age is None or features.get('age_group') == expected_age
            
            if gender_match and age_match:
                print(f"  [PASS] {desc[:20]}... -> {result['name']} (confidence: {result['confidence']})")
                reporter.add_result(f"自定义-{desc[:15]}...", True,
                                  f"匹配: {result['name']}, 置信度: {result['confidence']}")
                passed_count += 1
            else:
                print(f"  [WARN] {desc[:20]}... -> {result['name']} (特征不匹配)")
                reporter.add_result(f"自定义-{desc[:15]}...", False,
                                  f"特征不匹配: {features}")
        else:
            print(f"  [FAIL] {desc[:20]}... -> 未找到匹配")
            reporter.add_result(f"自定义-{desc[:15]}...", False, "未找到匹配")
    
    accuracy = passed_count / len(test_cases) * 100
    print(f"\n  匹配准确率: {accuracy:.0f}% ({passed_count}/{len(test_cases)})")
    
    return accuracy >= 80


def test_3_tts_params(reporter):
    """测试3: TTS参数生成测试"""
    print("\n" + "=" * 70)
    print("测试3: TTS参数生成测试")
    print("=" * 70)
    
    test_portraits = ["中年男中音", "青年女高音", "中年男低音"]
    all_passed = True
    
    for portrait in test_portraits:
        params = generate_tts_params(portrait)
        
        has_reference_id = 'reference_id' in params and params['reference_id'] is not None
        has_reference_name = 'reference_name' in params and params['reference_name']
        
        if has_reference_id and has_reference_name:
            print(f"  [PASS] {portrait} -> reference_id: {params['reference_id'][:16]}..., name: {params['reference_name']}")
            reporter.add_result(f"TTS参数-{portrait}", True,
                              f"reference_id: {params['reference_id'][:16]}...")
        else:
            print(f"  [FAIL] {portrait} -> 缺少reference_id或reference_name")
            reporter.add_result(f"TTS参数-{portrait}", False,
                              f"reference_id: {params.get('reference_id')}, name: {params.get('reference_name')}")
            all_passed = False
    
    return all_passed


def test_4_alternatives(reporter):
    """测试4: 备选推荐测试"""
    print("\n" + "=" * 70)
    print("测试4: 备选推荐测试")
    print("=" * 70)
    
    test_cases = [
        "中年男性声音",
        "年轻女性",
        "低沉男声"
    ]
    
    matcher = PortraitMatcher()
    all_passed = True
    
    for desc in test_cases:
        alternatives = matcher.get_alternatives(desc, top_n=3)
        
        if len(alternatives) == 3:
            # 检查置信度是否递减
            decreasing = all(alternatives[i]['confidence'] >= alternatives[i+1]['confidence'] 
                           for i in range(len(alternatives)-1))
            
            if decreasing:
                print(f"  [PASS] {desc} -> 3个备选，置信度递减")
                for i, alt in enumerate(alternatives, 1):
                    print(f"     {i}. {alt['name']} (confidence: {alt['confidence']})")
                reporter.add_result(f"备选推荐-{desc[:10]}", True,
                                  f"3个备选，置信度递减")
            else:
                print(f"  [WARN] {desc} -> 3个备选，但置信度未递减")
                reporter.add_result(f"备选推荐-{desc[:10]}", False,
                                  f"置信度未递减")
                all_passed = False
        else:
            print(f"  [FAIL] {desc} -> 返回{len(alternatives)}个备选（预期3个）")
            reporter.add_result(f"备选推荐-{desc[:10]}", False,
                              f"返回{len(alternatives)}个备选")
            all_passed = False
    
    return all_passed


def test_5_database_search(reporter):
    """测试5: 数据库搜索功能测试"""
    print("\n" + "=" * 70)
    print("测试5: 数据库搜索功能测试")
    print("=" * 70)
    
    db = ReferenceDatabase()
    
    # 测试特征搜索
    features = {"gender": "male", "age_group": "middle_aged"}
    matches = db.search_by_features(features)
    
    if len(matches) > 0:
        print(f"  [PASS] 特征搜索: 找到{len(matches)}个匹配")
        reporter.add_result("数据库搜索-特征", True, f"找到{len(matches)}个匹配")
    else:
        print(f"  [FAIL] 特征搜索: 未找到匹配")
        reporter.add_result("数据库搜索-特征", False, "未找到匹配")
        return False
    
    # 测试关键词搜索
    keywords = ["清亮", "甜美"]
    matches = db.search_by_keywords(keywords)
    
    if len(matches) > 0:
        print(f"  [PASS] 关键词搜索: 找到{len(matches)}个匹配")
        reporter.add_result("数据库搜索-关键词", True, f"找到{len(matches)}个匹配")
    else:
        print(f"  [FAIL] 关键词搜索: 未找到匹配")
        reporter.add_result("数据库搜索-关键词", False, "未找到匹配")
        return False
    
    # 测试分类浏览
    male_refs = db.list_by_category(gender="male")
    if len(male_refs) > 0:
        print(f"  [PASS] 分类浏览: 男声{len(male_refs)}个")
        reporter.add_result("数据库搜索-分类", True, f"男声{len(male_refs)}个")
    else:
        print(f"  [FAIL] 分类浏览: 未找到男声")
        reporter.add_result("数据库搜索-分类", False, "未找到男声")
        return False
    
    return True


def test_6_statistics(reporter):
    """测试6: 数据库统计信息测试"""
    print("\n" + "=" * 70)
    print("测试6: 数据库统计信息测试")
    print("=" * 70)
    
    db = ReferenceDatabase()
    stats = db.get_statistics()
    
    if stats['total_count'] >= 6:
        print(f"  [PASS] 总计: {stats['total_count']}个reference")
        print(f"     按性别: {stats['by_gender']}")
        print(f"     按年龄段: {stats['by_age_group']}")
        print(f"     按音高: {stats['by_voice_type']}")
        reporter.add_result("数据库统计", True, f"{stats['total_count']}个reference")
        return True
    else:
        print(f"  [FAIL] 总计: {stats['total_count']}个（预期>=6）")
        reporter.add_result("数据库统计", False, f"{stats['total_count']}个")
        return False


def main():
    print("=" * 70)
    print("方案C Step 3 自动化测试")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    reporter = TestReporter()
    
    # 运行所有测试
    results = []
    
    results.append(("测试1: 预设画像匹配", test_1_preset_portraits(reporter)))
    results.append(("测试2: 自定义角色描述", test_2_custom_portraits(reporter)))
    results.append(("测试3: TTS参数生成", test_3_tts_params(reporter)))
    results.append(("测试4: 备选推荐", test_4_alternatives(reporter)))
    results.append(("测试5: 数据库搜索", test_5_database_search(reporter)))
    results.append(("测试6: 数据库统计", test_6_statistics(reporter)))
    
    # 生成报告
    print("\n" + "=" * 70)
    report = reporter.generate_report()
    print(report)
    
    # 保存报告到文件
    report_file = "test_report_step3.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已保存到: {report_file}")
    
    # 打印摘要
    print("\n" + "=" * 70)
    print("测试摘要:")
    print("=" * 70)
    for test_name, passed in results:
        status = "[PASS] 通过" if passed else "[FAIL] 失败"
        print(f"  {status} {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    print(f"\n总计: {total_passed}/{total_tests} 通过")
    
    if total_passed == total_tests:
        print("\n[PASS] 所有测试通过！方案C Step 3验证成功！")
        print("\n下一步:")
        print("  1. 等待方案B音频生成完成")
        print("  2. 运行完整训练流程")
        print("  3. 测试5个声模的变声效果")
    else:
        print(f"\n[WARN] {total_tests - total_passed}个测试失败，需要修复")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
