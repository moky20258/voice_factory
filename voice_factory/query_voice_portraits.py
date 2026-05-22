#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声模人物画像快速查询工具
用于快速浏览和搜索已训练声模的人物画像
"""

import os
import json
import sys

def load_trained_voices():
    """加载已训练声模数据库"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_voices_db.json")
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return None
    
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_all_portraits(db, gender_filter=None):
    """列出所有声模画像"""
    voices = db.get('trained_voices', [])
    
    # 按性别筛选
    if gender_filter:
        voices = [v for v in voices if v.get('portrait_details', {}).get('gender') == gender_filter]
    
    print("\n" + "="*80)
    if gender_filter == '男':
        print("👨 男声声模画像")
    elif gender_filter == '女':
        print("👩 女声声模画像")
    else:
        print("🎤 全部声模画像")
    print("="*80)
    
    for voice in voices:
        speaker_id = voice.get('id', 'N/A')
        portrait = voice.get('portrait', '未分类')
        description = voice.get('description', '')
        details = voice.get('portrait_details', {})
        
        print(f"\n{speaker_id} - {portrait}")
        print(f"  描述: {description}")
        print(f"  年龄: {details.get('age_range', 'N/A')}")
        print(f"  音色: {details.get('tone', 'N/A')}")
        print(f"  特征: {details.get('characteristics', 'N/A')}")
        print(f"  适用: {', '.join(details.get('suitable_scenes', [])[:5])}")
    
    print(f"\n共计: {len(voices)} 个声模")
    print("="*80)


def search_by_scene(db, scene_keyword):
    """根据场景搜索声模"""
    voices = db.get('trained_voices', [])
    matches = []
    
    for voice in voices:
        details = voice.get('portrait_details', {})
        scenes = details.get('suitable_scenes', [])
        
        # 检查是否包含关键词
        for scene in scenes:
            if scene_keyword.lower() in scene.lower():
                matches.append(voice)
                break
    
    if not matches:
        print(f"\n❌ 未找到包含 '{scene_keyword}' 的声模")
        return
    
    print("\n" + "="*80)
    print(f"🔍 搜索场景: {scene_keyword}")
    print("="*80)
    
    for voice in matches:
        speaker_id = voice.get('id', 'N/A')
        portrait = voice.get('portrait', '未分类')
        description = voice.get('description', '')
        details = voice.get('portrait_details', {})
        
        # 高亮匹配的场景
        matched_scenes = [s for s in details.get('suitable_scenes', []) 
                         if scene_keyword.lower() in s.lower()]
        
        print(f"\n{speaker_id} - {portrait}")
        print(f"  描述: {description}")
        print(f"  年龄: {details.get('age_range', 'N/A')}")
        print(f"  音色: {details.get('tone', 'N/A')}")
        print(f"  ✅ 匹配场景: {', '.join(matched_scenes)}")
    
    print(f"\n找到 {len(matches)} 个匹配的声模")
    print("="*80)


def search_by_tone(db, tone_keyword):
    """根据音色搜索声模"""
    voices = db.get('trained_voices', [])
    matches = []
    
    for voice in voices:
        details = voice.get('portrait_details', {})
        tone = details.get('tone', '')
        
        if tone_keyword.lower() in tone.lower():
            matches.append(voice)
    
    if not matches:
        print(f"\n❌ 未找到音色包含 '{tone_keyword}' 的声模")
        return
    
    print("\n" + "="*80)
    print(f"🔍 搜索音色: {tone_keyword}")
    print("="*80)
    
    for voice in matches:
        speaker_id = voice.get('id', 'N/A')
        portrait = voice.get('portrait', '未分类')
        description = voice.get('description', '')
        details = voice.get('portrait_details', {})
        
        print(f"\n{speaker_id} - {portrait}")
        print(f"  描述: {description}")
        print(f"  年龄: {details.get('age_range', 'N/A')}")
        print(f"  音色: {details.get('tone', 'N/A')}")
        print(f"  适用: {', '.join(details.get('suitable_scenes', [])[:5])}")
    
    print(f"\n找到 {len(matches)} 个匹配的声模")
    print("="*80)


def show_voice_detail(db, speaker_id):
    """显示指定声模的详细信息"""
    voices = db.get('trained_voices', [])
    
    # 查找声模
    voice = None
    for v in voices:
        if v.get('id') == speaker_id:
            voice = v
            break
    
    if not voice:
        print(f"\n❌ 未找到声模: {speaker_id}")
        return
    
    portrait = voice.get('portrait', '未分类')
    description = voice.get('description', '')
    details = voice.get('portrait_details', {})
    
    print("\n" + "="*80)
    print(f"🎤 {speaker_id} - {portrait}")
    print("="*80)
    
    print(f"\n📝 描述:")
    print(f"  {description}")
    
    print(f"\n📊 详细信息:")
    print(f"  年龄范围: {details.get('age_range', 'N/A')}")
    print(f"  性别: {details.get('gender', 'N/A')}")
    print(f"  音色类型: {details.get('voice_type', 'N/A')}")
    print(f"  音色特点: {details.get('tone', 'N/A')}")
    print(f"  声音特征: {details.get('characteristics', 'N/A')}")
    
    print(f"\n🎯 适用场景:")
    for scene in details.get('suitable_scenes', []):
        print(f"  • {scene}")
    
    print(f"\n📁 文件信息:")
    print(f"  模型文件: {voice.get('model_v2', 'N/A')}")
    print(f"  索引文件: {voice.get('index_file', 'N/A')}")
    print(f"  声模目录: {voice.get('speaker_dir', 'N/A')}")
    
    print("="*80)


def interactive_search(db):
    """交互式搜索"""
    while True:
        print("\n" + "="*80)
        print("🔍 声模画像查询系统")
        print("="*80)
        print("\n请选择查询方式:")
        print("1. 列出全部声模")
        print("2. 列出男声声模")
        print("3. 列出女声声模")
        print("4. 按场景搜索")
        print("5. 按音色搜索")
        print("6. 查看声模详情")
        print("7. 退出")
        print()
        
        choice = input("请输入选项 (1-7): ").strip()
        
        if choice == "1":
            list_all_portraits(db)
        elif choice == "2":
            list_all_portraits(db, gender_filter='男')
        elif choice == "3":
            list_all_portraits(db, gender_filter='女')
        elif choice == "4":
            keyword = input("\n请输入场景关键词 (如: 旁白, 对话, 动漫): ").strip()
            if keyword:
                search_by_scene(db, keyword)
        elif choice == "5":
            keyword = input("\n请输入音色关键词 (如: 温暖, 清亮, 深沉): ").strip()
            if keyword:
                search_by_tone(db, keyword)
        elif choice == "6":
            speaker_id = input("\n请输入声模ID (如: speaker_0001): ").strip()
            if speaker_id:
                show_voice_detail(db, speaker_id)
        elif choice == "7":
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选项")
        
        # 询问是否继续
        if choice != "7":
            continue_query = input("\n是否继续查询? (y/n): ").strip().lower()
            if continue_query != 'y':
                print("\n👋 再见！")
                break


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🎤 声模人物画像查询工具")
    print("="*80)
    
    # 加载数据库
    db = load_trained_voices()
    if not db:
        return
    
    print(f"\n✅ 已加载 {db['total_count']} 个声模")
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_all_portraits(db)
        elif command == "list-male":
            list_all_portraits(db, gender_filter='男')
        elif command == "list-female":
            list_all_portraits(db, gender_filter='女')
        elif command == "search-scene" and len(sys.argv) > 2:
            search_by_scene(db, sys.argv[2])
        elif command == "search-tone" and len(sys.argv) > 2:
            search_by_tone(db, sys.argv[2])
        elif command == "detail" and len(sys.argv) > 2:
            show_voice_detail(db, sys.argv[2])
        else:
            print("❌ 无效命令或参数")
            print("\n用法:")
            print("  python query_voice_portraits.py list                  # 列出全部")
            print("  python query_voice_portraits.py list-male             # 列出男声")
            print("  python query_voice_portraits.py list-female           # 列出女声")
            print("  python query_voice_portraits.py search-scene 旁白     # 按场景搜索")
            print("  python query_voice_portraits.py search-tone 温暖      # 按音色搜索")
            print("  python query_voice_portraits.py detail speaker_0001   # 查看详情")
            print("  python query_voice_portraits.py                       # 交互模式")
    else:
        # 交互模式
        interactive_search(db)


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
