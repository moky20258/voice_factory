#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人物画像声模生成系统 - 交互式版本
提供友好的交互界面，引导用户完成声模生成流程
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from portrait_to_voice_model import portrait_to_voice_model
from portrait_to_tts_config import list_available_portraits, get_portrait_info


def display_portrait_list():
    """显示可用的画像列表"""
    print("\n" + "="*70)
    print("📋 可用画像列表")
    print("="*70)
    
    portraits = list_available_portraits()
    
    print("\n👨 男声声模:")
    male_portraits = [p for p in portraits if '男' in p]
    for i, portrait in enumerate(male_portraits, 1):
        info = get_portrait_info(portrait)
        print(f"  {i}. {portrait}")
        print(f"     {info['description']}")
    
    print("\n👩 女声声模:")
    female_portraits = [p for p in portraits if '女' in p]
    for i, portrait in enumerate(female_portraits, 1):
        info = get_portrait_info(portrait)
        print(f"  {i}. {portrait}")
        print(f"     {info['description']}")
    
    print("\n" + "="*70)


def select_preset_portrait():
    """选择预设画像"""
    print("\n请选择预设画像:")
    
    portraits = list_available_portraits()
    male_portraits = [p for p in portraits if '男' in p]
    female_portraits = [p for p in portraits if '女' in p]
    
    print("\n👨 男声声模:")
    for i, portrait in enumerate(male_portraits, 1):
        print(f"  {i}. {portrait}")
    
    print("\n👩 女声声模:")
    for i, portrait in enumerate(female_portraits, 1):
        print(f"  {i + len(male_portraits)}. {portrait}")
    
    print()
    
    try:
        choice = int(input(f"请输入选项 (1-{len(portraits)}): "))
        if 1 <= choice <= len(portraits):
            return portraits[choice - 1]
        else:
            print("❌ 无效选项")
            return None
    except ValueError:
        print("❌ 请输入有效的数字")
        return None


def custom_portrait():
    """自定义画像描述"""
    print("\n💡 提示: 可以组合以下关键词")
    print("  性别: 男、女")
    print("  年龄: 青年、中年、年轻、成熟")
    print("  音色: 高音、中音、低音")
    print("  特点: 温暖、清亮、深沉、活泼、温柔等")
    print()
    
    portrait = input("请输入自定义画像描述: ").strip()
    
    if not portrait:
        print("❌ 输入不能为空")
        return None
    
    return portrait


def get_input_with_default(prompt, default):
    """获取用户输入，支持默认值"""
    value = input(f"{prompt} (默认: {default}): ").strip()
    return int(value) if value else default


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎨 人物画像声模生成系统")
    print("="*70)
    print("\n本系统将从人物画像描述生成完整的声模，包括:")
    print("  1. 根据画像特征生成 TTS 参数")
    print("  2. 生成专属训练文本")
    print("  3. 调用 Fish Speech TTS 生成音频")
    print("  4. 准备 RVC 训练数据")
    print("  5. 训练 RVC 声模")
    print("  6. 添加到声模数据库")
    print()
    
    while True:
        print("\n" + "="*70)
        print("请选择输入方式:")
        print("="*70)
        print("1. 选择预设画像")
        print("2. 自定义画像描述")
        print("3. 查看画像列表")
        print("4. 退出")
        print()
        
        try:
            choice = input("请输入选项 (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break
        
        if choice == "4":
            print("\n👋 再见！")
            break
        
        elif choice == "3":
            display_portrait_list()
            continue
        
        elif choice == "1":
            portrait = select_preset_portrait()
            if not portrait:
                continue
        
        elif choice == "2":
            portrait = custom_portrait()
            if not portrait:
                continue
        
        else:
            print("❌ 无效选项")
            continue
        
        # 获取训练参数
        print(f"\n📋 当前选择: {portrait}")
        print()
        
        try:
            epochs = get_input_with_default("请输入训练轮数", 50)
            sentences = get_input_with_default("请输入生成句子数", 30)
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\n❌ 输入无效，返回主菜单")
            continue
        
        # 确认信息
        print("\n" + "="*70)
        print("📋 任务确认")
        print("="*70)
        print(f"  人物画像: {portrait}")
        print(f"  训练轮数: {epochs}")
        print(f"  生成句子: {sentences}")
        print("="*70)
        
        try:
            confirm = input("\n是否开始生成? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break
        
        if confirm != 'y':
            print("已取消")
            continue
        
        # 开始生成
        try:
            portrait_to_voice_model(
                portrait=portrait,
                speaker_id=None,
                epochs=epochs,
                num_sentences=sentences
            )
            
            # 询问是否继续
            print()
            try:
                again = input("是否继续生成其他声模? (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 再见！")
                break
            
            if again != 'y':
                print("\n👋 再见！")
                break
        
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                retry = input("\n是否重试? (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 再见！")
                break
            
            if retry != 'y':
                print("\n👋 再见！")
                break
    
    print("\n感谢使用！👋")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
