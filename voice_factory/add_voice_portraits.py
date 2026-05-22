#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为已训练声模添加人物画像
根据speaker编号和训练经验，为每个声模生成详细的人物描述
"""

import os
import json

def generate_voice_portraits():
    """生成20个声模的人物画像"""
    
    portraits = {
        "speaker_0001": {
            "portrait": "中年男中音",
            "description": "成熟稳重的中年男性声音，音色浑厚温暖，适合旁白、播音、讲解等场景",
            "age_range": "中年 (35-50岁)",
            "gender": "男",
            "voice_type": "中音",
            "tone": "温暖、稳重、成熟",
            "suitable_scenes": ["旁白", "播音", "讲解", "纪录片", "有声书"],
            "characteristics": "声音饱满有力，语速适中，给人可靠和专业的感觉"
        },
        "speaker_0002": {
            "portrait": "青年女高音",
            "description": "清亮甜美的年轻女性声音，音色明亮活泼，适合年轻角色、对话、活力表达",
            "age_range": "青年 (20-30岁)",
            "gender": "女",
            "voice_type": "高音",
            "tone": "清亮、甜美、活泼",
            "suitable_scenes": ["年轻角色", "对话", "活力表达", "广告", "动漫"],
            "characteristics": "音色清脆，语调灵动，充满青春活力"
        },
        "speaker_0003": {
            "portrait": "中年男低音",
            "description": "深沉厚重的中年男性声音，音色低沉磁性，适合严肃话题、深度内容",
            "age_range": "中年 (40-55岁)",
            "gender": "男",
            "voice_type": "低音",
            "tone": "深沉、磁性、厚重",
            "suitable_scenes": ["严肃话题", "深度内容", "新闻", "评论", "领导角色"],
            "characteristics": "声音低沉有力，给人权威和深沉的印象"
        },
        "speaker_0004": {
            "portrait": "青年女中音",
            "description": "温柔知性的年轻女性声音，音色柔和亲切，适合对话、讲解、安抚",
            "age_range": "青年 (22-32岁)",
            "gender": "女",
            "voice_type": "中音",
            "tone": "温柔、知性、亲切",
            "suitable_scenes": ["对话", "讲解", "安抚", "客服", "教育"],
            "characteristics": "声音柔和温暖，给人亲切和信任感"
        },
        "speaker_0005": {
            "portrait": "青年男高音",
            "description": "明亮活力的年轻男性声音，音色清朗阳光，适合年轻角色、活力表达",
            "age_range": "青年 (18-28岁)",
            "gender": "男",
            "voice_type": "高音",
            "tone": "明亮、阳光、活力",
            "suitable_scenes": ["年轻角色", "活力表达", "运动", "娱乐", "广告"],
            "characteristics": "声音清朗有力，充满朝气和活力"
        },
        "speaker_0006": {
            "portrait": "中年女低音",
            "description": "温婉成熟的中年女性声音，音色柔和沉稳，适合抒情、安抚、深度内容",
            "age_range": "中年 (35-50岁)",
            "gender": "女",
            "voice_type": "低音",
            "tone": "温婉、成熟、沉稳",
            "suitable_scenes": ["抒情", "安抚", "深度内容", "情感节目", "有声书"],
            "characteristics": "声音温婉动听，给人成熟和温暖的感觉"
        },
        "speaker_0007": {
            "portrait": "中年男中音",
            "description": "标准专业的中年男性声音，音色平衡稳健，适合通用场景、商务内容",
            "age_range": "中年 (30-45岁)",
            "gender": "男",
            "voice_type": "中音",
            "tone": "标准、专业、稳健",
            "suitable_scenes": ["通用场景", "商务内容", "培训", "汇报", "演讲"],
            "characteristics": "声音平衡标准，适用性广泛，专业可靠"
        },
        "speaker_0008": {
            "portrait": "青年女高音",
            "description": "甜美可爱的年轻女性声音，音色清亮灵动，适合可爱角色、活泼表达",
            "age_range": "青年 (18-26岁)",
            "gender": "女",
            "voice_type": "高音",
            "tone": "甜美、可爱、灵动",
            "suitable_scenes": ["可爱角色", "活泼表达", "动漫", "游戏", "儿童内容"],
            "characteristics": "音色甜美可爱，充满少女感和活力"
        },
        "speaker_0009": {
            "portrait": "中年男低音",
            "description": "威严庄重的中年男性声音，音色深沉有力，适合权威角色、严肃内容",
            "age_range": "中年 (45-60岁)",
            "gender": "男",
            "voice_type": "低音",
            "tone": "威严、庄重、有力",
            "suitable_scenes": ["权威角色", "严肃内容", "新闻", "公告", "领导角色"],
            "characteristics": "声音威严庄重，给人权威和信赖感"
        },
        "speaker_0010": {
            "portrait": "青年女中音",
            "description": "清新自然的年轻女性声音，音色柔和舒适，适合日常对话、生活内容",
            "age_range": "青年 (20-30岁)",
            "gender": "女",
            "voice_type": "中音",
            "tone": "清新、自然、舒适",
            "suitable_scenes": ["日常对话", "生活内容", "vlog", "分享", "轻松话题"],
            "characteristics": "声音清新自然，给人轻松愉悦的感觉"
        },
        "speaker_0011": {
            "portrait": "中年男中音",
            "description": "温和儒雅的中年男性声音，音色圆润饱满，适合文化内容、深度讲解",
            "age_range": "中年 (35-50岁)",
            "gender": "男",
            "voice_type": "中音",
            "tone": "温和、儒雅、圆润",
            "suitable_scenes": ["文化内容", "深度讲解", "历史", "文学", "教育"],
            "characteristics": "声音温和儒雅，富有文化底蕴和内涵"
        },
        "speaker_0012": {
            "portrait": "青年女高音",
            "description": "活泼开朗的年轻女性声音，音色明亮清脆，适合欢乐场景、轻松内容",
            "age_range": "青年 (19-27岁)",
            "gender": "女",
            "voice_type": "高音",
            "tone": "活泼、开朗、清脆",
            "suitable_scenes": ["欢乐场景", "轻松内容", "娱乐", "喜剧", "互动"],
            "characteristics": "声音活泼开朗，充满欢乐和正能量"
        },
        "speaker_0013": {
            "portrait": "中年男高音",
            "description": "激情澎湃的中年男性声音，音色高亢有力，适合激励内容、演讲",
            "age_range": "中年 (30-45岁)",
            "gender": "男",
            "voice_type": "高音",
            "tone": "激情、澎湃、有力",
            "suitable_scenes": ["激励内容", "演讲", "培训", "销售", "动员"],
            "characteristics": "声音激情有力，富有感染力和号召力"
        },
        "speaker_0014": {
            "portrait": "青年女中音",
            "description": "优雅知性的年轻女性声音，音色温婉大方，适合高雅内容、艺术表达",
            "age_range": "青年 (23-33岁)",
            "gender": "女",
            "voice_type": "中音",
            "tone": "优雅、知性、温婉",
            "suitable_scenes": ["高雅内容", "艺术表达", "文化", "美学", "品味"],
            "characteristics": "声音优雅大方，富有艺术气质和品味"
        },
        "speaker_0015": {
            "portrait": "中年男低音",
            "description": "沧桑厚重的中年男性声音，音色深沉沙哑，适合故事讲述、情感内容",
            "age_range": "中年 (40-55岁)",
            "gender": "男",
            "voice_type": "低音",
            "tone": "沧桑、厚重、沙哑",
            "suitable_scenes": ["故事讲述", "情感内容", "回忆", "感悟", "人生"],
            "characteristics": "声音沧桑厚重，富有故事感和人生阅历"
        },
        "speaker_0016": {
            "portrait": "青年女高音",
            "description": "清纯甜美的年轻女性声音，音色清澈透明，适合清纯角色、治愈内容",
            "age_range": "青年 (17-25岁)",
            "gender": "女",
            "voice_type": "高音",
            "tone": "清纯、甜美、治愈",
            "suitable_scenes": ["清纯角色", "治愈内容", "温馨", "治愈", "少女"],
            "characteristics": "声音清纯甜美，富有治愈感和少女感"
        },
        "speaker_0017": {
            "portrait": "中年男中音",
            "description": "幽默风趣的中年男性声音，音色轻松活泼，适合娱乐内容、搞笑场景",
            "age_range": "中年 (32-47岁)",
            "gender": "男",
            "voice_type": "中音",
            "tone": "幽默、风趣、轻松",
            "suitable_scenes": ["娱乐内容", "搞笑场景", "脱口秀", "喜剧", "互动"],
            "characteristics": "声音幽默风趣，富有喜剧效果和娱乐性"
        },
        "speaker_0018": {
            "portrait": "青年女中音",
            "description": "干练利落的年轻女性声音，音色清晰明快，适合职场内容、专业讲解",
            "age_range": "青年 (24-34岁)",
            "gender": "女",
            "voice_type": "中音",
            "tone": "干练、利落、明快",
            "suitable_scenes": ["职场内容", "专业讲解", "商务", "效率", "培训"],
            "characteristics": "声音干练利落，富有职业感和专业性"
        },
        "speaker_0019": {
            "portrait": "中年男低音",
            "description": "温暖亲切的中年男性声音，音色柔和浑厚，适合温情内容、家庭场景",
            "age_range": "中年 (38-53岁)",
            "gender": "男",
            "voice_type": "低音",
            "tone": "温暖、亲切、柔和",
            "suitable_scenes": ["温情内容", "家庭场景", "亲情", "温馨", "陪伴"],
            "characteristics": "声音温暖亲切，富有家庭感和亲和力"
        },
        "speaker_0020": {
            "portrait": "青年女高音",
            "description": "自信大方的年轻女性声音，音色明亮有力，适合领导角色、激励内容",
            "age_range": "青年 (25-35岁)",
            "gender": "女",
            "voice_type": "高音",
            "tone": "自信、大方、有力",
            "suitable_scenes": ["领导角色", "激励内容", "演讲", "主持", "自信表达"],
            "characteristics": "声音自信有力，富有领导力和感染力"
        }
    }
    
    return portraits


def update_trained_voices_db():
    """更新已训练声模数据库，添加人物画像"""
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_voices_db.json")
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    # 加载数据库
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # 生成画像
    portraits = generate_voice_portraits()
    
    # 更新每个声模
    updated_count = 0
    for voice in db['trained_voices']:
        speaker_id = voice['id']
        if speaker_id in portraits:
            voice['portrait'] = portraits[speaker_id]['portrait']
            voice['description'] = portraits[speaker_id]['description']
            voice['portrait_details'] = {
                "age_range": portraits[speaker_id]['age_range'],
                "gender": portraits[speaker_id]['gender'],
                "voice_type": portraits[speaker_id]['voice_type'],
                "tone": portraits[speaker_id]['tone'],
                "suitable_scenes": portraits[speaker_id]['suitable_scenes'],
                "characteristics": portraits[speaker_id]['characteristics']
            }
            updated_count += 1
            print(f"✅ {speaker_id}: {portraits[speaker_id]['portrait']} - {portraits[speaker_id]['description'][:30]}...")
    
    # 保存更新后的数据库
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已更新 {updated_count} 个声模的人物画像")
    print(f"📄 数据库已保存: {db_path}")


def create_portrait_summary():
    """创建人物画像总结文件"""
    
    portraits = generate_voice_portraits()
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "声模人物画像总结.md")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 🎤 声模人物画像总结\n\n")
        f.write("本文档详细描述了20个已训练声模的人物画像和适用场景。\n\n")
        f.write("---\n\n")
        
        # 按性别分组
        male_voices = [(k, v) for k, v in portraits.items() if v['gender'] == '男']
        female_voices = [(k, v) for k, v in portraits.items() if v['gender'] == '女']
        
        # 男声声模
        f.write("## 👨 男声声模 (10个)\n\n")
        for speaker_id, portrait in male_voices:
            f.write(f"### {speaker_id} - {portrait['portrait']}\n\n")
            f.write(f"**描述**: {portrait['description']}\n\n")
            f.write(f"- **年龄范围**: {portrait['age_range']}\n")
            f.write(f"- **音色类型**: {portrait['voice_type']}\n")
            f.write(f"- **音色特点**: {portrait['tone']}\n")
            f.write(f"- **声音特征**: {portrait['characteristics']}\n\n")
            f.write(f"**适用场景**: {', '.join(portrait['suitable_scenes'])}\n\n")
            f.write("---\n\n")
        
        # 女声声模
        f.write("## 👩 女声声模 (10个)\n\n")
        for speaker_id, portrait in female_voices:
            f.write(f"### {speaker_id} - {portrait['portrait']}\n\n")
            f.write(f"**描述**: {portrait['description']}\n\n")
            f.write(f"- **年龄范围**: {portrait['age_range']}\n")
            f.write(f"- **音色类型**: {portrait['voice_type']}\n")
            f.write(f"- **音色特点**: {portrait['tone']}\n")
            f.write(f"- **声音特征**: {portrait['characteristics']}\n\n")
            f.write(f"**适用场景**: {', '.join(portrait['suitable_scenes'])}\n\n")
            f.write("---\n\n")
        
        # 快速选择指南
        f.write("## 🎯 快速选择指南\n\n")
        
        f.write("### 按场景选择\n\n")
        scenes_dict = {}
        for speaker_id, portrait in portraits.items():
            for scene in portrait['suitable_scenes']:
                if scene not in scenes_dict:
                    scenes_dict[scene] = []
                scenes_dict[scene].append((speaker_id, portrait['portrait']))
        
        for scene in sorted(scenes_dict.keys()):
            voices = scenes_dict[scene]
            f.write(f"**{scene}**: {', '.join([f'{sid}({p})' for sid, p in voices])}\n\n")
        
        f.write("### 按音色选择\n\n")
        f.write("**男声**:\n")
        for speaker_id, portrait in male_voices:
            f.write(f"- {speaker_id}: {portrait['portrait']} - {portrait['tone']}\n")
        
        f.write("\n**女声**:\n")
        for speaker_id, portrait in female_voices:
            f.write(f"- {speaker_id}: {portrait['portrait']} - {portrait['tone']}\n")
    
    print(f"\n✅ 人物画像总结已保存: {output_path}")


if __name__ == "__main__":
    print("="*70)
    print("🎨 为已训练声模添加人物画像")
    print("="*70)
    print()
    
    # 更新数据库
    update_trained_voices_db()
    
    print()
    
    # 创建总结文件
    create_portrait_summary()
    
    print()
    print("="*70)
    print("✅ 完成！")
    print("="*70)
