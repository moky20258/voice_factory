#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声音分析与声模匹配系统 - 演示脚本
展示系统的完整功能和输出效果
"""

import os
import sys
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_analysis_and_recommendation import VoiceAnalyzerAndMatcher


def demo_single_file():
    """演示1: 分析单个音频文件"""
    print("\n" + "="*70)
    print("📌 演示1: 分析单个音频文件")
    print("="*70)
    
    # 使用测试音频
    test_audio = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "enhanced", "speaker_0001", "0001_formant0.85.wav"
    )
    
    if not os.path.exists(test_audio):
        print(f"⚠️  测试音频不存在: {test_audio}")
        return
    
    print(f"\n🎵 测试音频: {test_audio}\n")
    
    # 创建分析器
    analyzer = VoiceAnalyzerAndMatcher()
    
    # 分析声音
    features, match_features = analyzer.analyze_voice(test_audio)
    
    if features is None:
        print("❌ 分析失败")
        return
    
    # 匹配预训练声模
    pretrained_matches = analyzer.match_pretrained_models(match_features, top_n=3)
    
    # 匹配已训练声模
    trained_matches = analyzer.match_trained_voices(match_features, top_n=3)
    
    # 生成报告
    analyzer.generate_report(match_features, pretrained_matches, trained_matches)


def demo_directory():
    """演示2: 分析音频目录"""
    print("\n" + "="*70)
    print("📌 演示2: 分析音频目录（批量分析）")
    print("="*70)
    
    # 使用测试目录
    test_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "enhanced", "speaker_0001"
    )
    
    if not os.path.exists(test_dir):
        print(f"⚠️  测试目录不存在: {test_dir}")
        return
    
    print(f"\n📁 测试目录: {test_dir}\n")
    
    # 创建分析器
    analyzer = VoiceAnalyzerAndMatcher()
    
    # 分析目录
    features, match_features = analyzer.analyze_voice(test_dir)
    
    if features is None:
        print("❌ 分析失败")
        return
    
    print(f"\n💡 提示: 目录分析会计算平均特征，匹配更准确")


def demo_json_report():
    """演示3: 生成JSON报告"""
    print("\n" + "="*70)
    print("📌 演示3: 生成JSON格式报告")
    print("="*70)
    
    test_audio = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "enhanced", "speaker_0001", "0001_formant0.85.wav"
    )
    
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "demo_report.json"
    )
    
    print(f"\n📝 报告文件: {output_file}\n")
    
    # 创建分析器
    analyzer = VoiceAnalyzerAndMatcher()
    
    # 分析声音
    features, match_features = analyzer.analyze_voice(test_audio)
    
    if features is None:
        print("❌ 分析失败")
        return
    
    # 匹配
    pretrained_matches = analyzer.match_pretrained_models(match_features, top_n=3)
    trained_matches = analyzer.match_trained_voices(match_features, top_n=3)
    
    # 生成JSON报告
    analyzer.generate_report(
        match_features,
        pretrained_matches,
        trained_matches,
        output_file=output_file
    )
    
    # 读取并显示JSON
    if os.path.exists(output_file):
        print(f"\n📄 JSON报告内容:")
        print("-"*70)
        with open(output_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
            print(json.dumps(report, indent=2, ensure_ascii=False)[:1000])
            print("...")
        print("-"*70)


def demo_comparison():
    """演示4: 对比不同声音"""
    print("\n" + "="*70)
    print("📌 演示4: 对比不同说话人的声音")
    print("="*70)
    
    # 分析两个不同的说话人
    speakers = ["speaker_0001", "speaker_0002"]
    
    analyzer = VoiceAnalyzerAndMatcher()
    
    results = []
    
    for speaker in speakers:
        test_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "enhanced", speaker
        )
        
        if not os.path.exists(test_dir):
            continue
        
        print(f"\n🎤 分析 {speaker}...")
        
        features, match_features = analyzer.analyze_voice(test_dir)
        
        if features:
            # 匹配预训练声模
            pretrained_matches = analyzer.match_pretrained_models(match_features, top_n=1)
            
            results.append({
                'speaker': speaker,
                'f0_mean': match_features.get('f0_mean', 0),
                'gender': match_features.get('estimated_gender', 'N/A'),
                'best_match': pretrained_matches[0]['model']['name'] if pretrained_matches else 'N/A',
                'match_score': pretrained_matches[0]['score'] if pretrained_matches else 0
            })
    
    # 对比结果
    print("\n" + "="*70)
    print("📊 声音对比结果")
    print("="*70)
    print(f"\n{'说话人':<15} {'F0均值':<12} {'性别':<10} {'最佳匹配':<25} {'匹配度':<10}")
    print("-"*70)
    
    for r in results:
        print(f"{r['speaker']:<15} {r['f0_mean']:<12.2f} {r['gender']:<10} {r['best_match']:<25} {r['match_score']:<10.1f}%")
    
    print("\n💡 提示: 不同说话人会匹配到不同的声模")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎤 声音分析与声模匹配系统 - 功能演示")
    print("="*70)
    
    print("\n请选择演示内容:")
    print("1. 分析单个音频文件")
    print("2. 分析音频目录（批量）")
    print("3. 生成JSON格式报告")
    print("4. 对比不同说话人的声音")
    print("5. 运行全部演示")
    print()
    
    choice = input("请输入选项 (1-5): ").strip()
    
    if choice == "1":
        demo_single_file()
    elif choice == "2":
        demo_directory()
    elif choice == "3":
        demo_json_report()
    elif choice == "4":
        demo_comparison()
    elif choice == "5":
        demo_single_file()
        demo_directory()
        demo_json_report()
        demo_comparison()
    else:
        print("❌ 无效选项")
        return
    
    print("\n" + "="*70)
    print("✅ 演示完成！")
    print("="*70)
    print("\n💡 下一步:")
    print("  - 查看 README 文档了解完整功能")
    print("  - 运行 声音分析与匹配-交互版.bat 开始使用")
    print("  - 查看 声音分析与匹配使用指南.md 获取详细帮助")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
