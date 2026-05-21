#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声音分析与声模匹配 - 交互式版本
提供友好的交互界面，引导用户完成分析和匹配流程
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_analysis_and_recommendation import VoiceAnalyzerAndMatcher


def select_audio_path():
    """交互式选择音频路径"""
    print("\n" + "="*70)
    print("📁 选择音频输入")
    print("="*70)
    print("\n请选择输入方式:")
    print("1. 输入单个音频文件路径")
    print("2. 输入音频目录路径")
    print("3. 使用默认测试音频")
    print("4. 浏览最近使用的音频")
    print()
    
    choice = input("请输入选项 (1-4): ").strip()
    
    if choice == "1":
        path = input("\n请输入音频文件路径: ").strip().strip('"')
        if not os.path.exists(path):
            print(f"❌ 文件不存在: {path}")
            return None
        return path
    
    elif choice == "2":
        path = input("\n请输入目录路径: ").strip().strip('"')
        if not os.path.exists(path):
            print(f"❌ 目录不存在: {path}")
            return None
        return path
    
    elif choice == "3":
        # 使用默认测试音频
        test_audio = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "enhanced", "speaker_0001", "0001_formant0.85.wav"
        )
        if os.path.exists(test_audio):
            print(f"\n✅ 使用测试音频: {test_audio}")
            return test_audio
        else:
            print("❌ 测试音频不存在")
            return None
    
    elif choice == "4":
        # 浏览 recent audios（如果有记录）
        recent_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            ".recent_audios.json"
        )
        if os.path.exists(recent_file):
            with open(recent_file, 'r', encoding='utf-8') as f:
                recent = json.load(f)
            
            print("\n最近使用的音频:")
            for i, audio in enumerate(recent[:5], 1):
                print(f"  {i}. {audio}")
            
            idx = input("\n请选择 (1-5) 或输入新路径: ").strip()
            if idx.isdigit() and 1 <= int(idx) <= 5:
                return recent[int(idx) - 1]
            else:
                return idx.strip('"') if os.path.exists(idx.strip('"')) else None
        else:
            print("⚠️  没有最近使用记录")
            return None
    
    else:
        print("❌ 无效选项")
        return None


def select_options():
    """选择分析选项"""
    print("\n" + "="*70)
    print("⚙️  分析选项")
    print("="*70)
    
    options = {
        'top_n': 3,
        'output_file': None,
        'no_pretrained': False,
        'no_trained': False
    }
    
    # 匹配数量
    print("\n返回匹配数量:")
    print("  1. 3 个 (默认)")
    print("  2. 5 个")
    print("  3. 10 个")
    print("  4. 自定义")
    
    choice = input("\n请选择 (1-4): ").strip()
    if choice == "2":
        options['top_n'] = 5
    elif choice == "3":
        options['top_n'] = 10
    elif choice == "4":
        n = input("请输入数量: ").strip()
        if n.isdigit():
            options['top_n'] = int(n)
    
    # 输出文件
    save = input("\n是否保存报告到文件? (y/n): ").strip().lower()
    if save == 'y':
        default_name = "voice_match_report.json"
        filename = input(f"文件名 (默认: {default_name}): ").strip()
        options['output_file'] = filename if filename else default_name
    
    # 匹配类型
    print("\n匹配类型:")
    print("  1. 预训练声模 + 已训练声模 (默认)")
    print("  2. 仅预训练声模")
    print("  3. 仅已训练声模")
    
    choice = input("\n请选择 (1-3): ").strip()
    if choice == "2":
        options['no_trained'] = True
    elif choice == "3":
        options['no_pretrained'] = True
    
    return options


def save_recent_audio(audio_path):
    """保存最近使用的音频路径"""
    recent_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".recent_audios.json"
    )
    
    recent = []
    if os.path.exists(recent_file):
        with open(recent_file, 'r', encoding='utf-8') as f:
            recent = json.load(f)
    
    # 添加到开头
    if audio_path in recent:
        recent.remove(audio_path)
    recent.insert(0, audio_path)
    
    # 只保留最近 10 个
    recent = recent[:10]
    
    with open(recent_file, 'w', encoding='utf-8') as f:
        json.dump(recent, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎤 声音分析与声模匹配建议系统")
    print("="*70)
    print("\n本系统将:")
    print("  1. 分析输入音频的声音特征")
    print("  2. 匹配预训练声模库（理论推荐）")
    print("  3. 匹配已训练的实际声模（直接使用）")
    print("  4. 生成详细的匹配报告和建议")
    print()
    
    # 1. 选择音频
    audio_path = select_audio_path()
    if not audio_path:
        print("\n❌ 未选择音频，程序退出")
        return
    
    # 2. 选择选项
    options = select_options()
    
    # 3. 创建分析器
    print("\n🔧 初始化分析器...")
    analyzer = VoiceAnalyzerAndMatcher()
    
    # 4. 执行分析
    print("\n" + "="*70)
    print("🚀 开始分析与匹配")
    print("="*70)
    
    # 分析声音
    features, match_features = analyzer.analyze_voice(audio_path)
    
    if features is None:
        print("\n❌ 声音分析失败")
        return
    
    # 保存最近使用
    save_recent_audio(audio_path)
    
    # 匹配预训练声模
    pretrained_matches = []
    if not options['no_pretrained']:
        pretrained_matches = analyzer.match_pretrained_models(
            match_features, top_n=options['top_n']
        )
    
    # 匹配已训练声模
    trained_matches = []
    if not options['no_trained']:
        trained_matches = analyzer.match_trained_voices(
            match_features, top_n=options['top_n']
        )
    
    # 生成报告
    analyzer.generate_report(
        match_features,
        pretrained_matches,
        trained_matches,
        output_file=options['output_file']
    )
    
    # 5. 后续操作
    print("\n" + "="*70)
    print("✨ 后续操作")
    print("="*70)
    print("\n您可以:")
    print("  1. 再次分析其他音频")
    print("  2. 查看报告文件")
    print("  3. 退出程序")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 递归调用
        main()
    elif choice == "2":
        if options['output_file'] and os.path.exists(options['output_file']):
            print(f"\n📄 打开报告文件: {options['output_file']}")
            os.startfile(options['output_file'])
        else:
            print("⚠️  没有保存报告文件")
    
    print("\n👋 感谢使用！")


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
