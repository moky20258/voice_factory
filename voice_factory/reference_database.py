#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
参考音频数据库管理系统
管理所有可用的reference_id，支持按特征搜索和匹配
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


# ==================== 参考音频数据库 ====================

REFERENCE_DATABASE = {
    # ========== Fish Audio官方预设声音 ==========
    
    # 男声 - 中年
    "536d3a5e000945adb7038665781a4aca": {
        "name": "Ethan",
        "gender": "male",
        "age_group": "middle_aged",
        "voice_type": "baritone",
        "description": "成熟稳重的中年男性声音，音色浑厚温暖",
        "tags": ["成熟", "稳重", "浑厚", "温暖", "中年", "男中音"],
        "language": "zh",
        "source": "fish_audio_official",
        "sample_url": "https://pub-b995142090474379a930b856ab79b4d4.r2.dev/audio/quickstart/536d3a5e000945adb7038665781a4aca.mp3"
    },
    
    "bf322df2096a46f18c579d0baa36f41d": {
        "name": "Adrian",
        "gender": "male",
        "age_group": "middle_aged",
        "voice_type": "bass",
        "description": "深沉厚重的中年男性声音，音色低沉磁性",
        "tags": ["深沉", "厚重", "低沉", "磁性", "中年", "男低音"],
        "language": "zh",
        "source": "fish_audio_official",
        "sample_url": "https://pub-b995142090474379a930b856ab79b4d4.r2.dev/audio/quickstart/bf322df2096a46f18c579d0baa36f41d.mp3"
    },
    
    # 男声 - 青年
    "802e3bc2b27e49c2995d23ef70e6ac89": {
        "name": "Energetic Male",
        "gender": "male",
        "age_group": "young",
        "voice_type": "tenor",
        "description": "明亮活力的年轻男性声音，音色清朗阳光",
        "tags": ["明亮", "活力", "清朗", "阳光", "青年", "男高音"],
        "language": "zh",
        "source": "fish_audio_official",
        "sample_url": "https://pub-b995142090474379a930b856ab79b4d4.r2.dev/audio/quickstart/802e3bc2b27e49c2995d23ef70e6ac89.mp3"
    },
    
    # 女声 - 青年
    "933563129e564b19a115bedd57b7406a": {
        "name": "Sarah",
        "gender": "female",
        "age_group": "young",
        "voice_type": "soprano",
        "description": "清亮甜美的年轻女性声音，音色明亮活泼",
        "tags": ["清亮", "甜美", "明亮", "活泼", "青年", "女高音"],
        "language": "zh",
        "source": "fish_audio_official",
        "sample_url": "https://pub-b995142090474379a930b856ab79b4d4.r2.dev/audio/quickstart/933563129e564b19a115bedd57b7406a.mp3"
    },
    
    "b347db033a6549378b48d00acb0d06cd": {
        "name": "Selene",
        "gender": "female",
        "age_group": "young",
        "voice_type": "mezzo_soprano",
        "description": "温柔知性的年轻女性声音，音色柔和亲切",
        "tags": ["温柔", "知性", "柔和", "亲切", "青年", "女中音"],
        "language": "zh",
        "source": "fish_audio_official",
        "sample_url": "https://pub-b995142090474379a930b856ab79b4d4.r2.dev/audio/quickstart/b347db033a6549378b48d00acb0d06cd.mp3"
    },
    
    # 女声 - 特殊风格
    "8ef4a238714b45718ce04243307c57a7": {
        "name": "E-girl",
        "gender": "female",
        "age_group": "young",
        "voice_type": "soprano",
        "description": "可爱的年轻女性声音，带有电子风格",
        "tags": ["可爱", "电子", "萌", "青年", "女高音", "特殊风格"],
        "language": "zh",
        "source": "fish_audio_official",
        "sample_url": "https://pub-b995142090474379a930b856ab79b4d4.r2.dev/audio/quickstart/8ef4a238714b45718ce04243307c57a7.mp3"
    },
}


# ==================== 特征关键词映射 ====================

# 性别关键词
GENDER_KEYWORDS = {
    "male": ["男", "male", "先生", "boy", "man", "大叔", "少年", "老者", "爸爸", "爷爷", "哥哥", "男孩", "男人"],
    "female": ["女", "female", "小姐", "女士", "girl", "woman", "女孩", "妈妈", "奶奶", "姐姐", "女孩", "女人", "姑娘"]
}

# 年龄段关键词
AGE_KEYWORDS = {
    "old": ["老年", "old", "老人", "老者", "古稀", "花甲", "沧桑", "年迈", "高龄", "年纪大"],
    "young": ["青年", "年轻", "young", "少年", "少女", "小伙子", "姑娘", "小孩", "儿童", "童年", "青春", "活泼可爱"],
    "middle_aged": ["中年", "middle", "成熟", "steady", "大叔", "阿姨", "稳重", "沉稳", "大气"]
}

# 音高关键词
VOICE_TYPE_KEYWORDS = {
    "soprano": ["高音", "soprano", "清亮", "尖", "高亢"],
    "mezzo_soprano": ["中音", "mezzo", "柔和", "温和", "中等"],
    "tenor": ["高音", "tenor", "明亮", "清朗", "高亢"],
    "baritone": ["中音", "baritone", "浑厚", "温暖", "沉稳"],
    "bass": ["低音", "bass", "低沉", "深沉", "磁性", "厚重"]
}

# 音色特征关键词
TONE_KEYWORDS = {
    "温暖": ["温暖", "warm", "温和"],
    "浑厚": ["浑厚", "thick", "饱满"],
    "清亮": ["清亮", "clear", "清澈"],
    "甜美": ["甜美", "sweet", "甜"],
    "低沉": ["低沉", "deep", "低"],
    "磁性": ["磁性", "magnetic", "魅力"],
    "明亮": ["明亮", "bright", "明朗"],
    "柔和": ["柔和", "soft", "温柔"],
    "活泼": ["活泼", "lively", "active"],
    "稳重": ["稳重", "steady", "沉稳"],
    "阳光": ["阳光", "sunny", "开朗"]
}


class ReferenceDatabase:
    """参考音频数据库管理类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径（可选，用于加载自定义reference）
        """
        self.database = REFERENCE_DATABASE.copy()
        self.db_path = db_path
        
        # 加载自定义数据库（如果存在）
        if db_path and os.path.exists(db_path):
            self.load_custom_database(db_path)
    
    def load_custom_database(self, db_path: str):
        """加载自定义参考音频数据库"""
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                custom_db = json.load(f)
                self.database.update(custom_db)
                print(f"[OK] 加载自定义参考音频数据库: {len(custom_db)} 条记录")
        except Exception as e:
            print(f"[WARN] 加载自定义数据库失败: {e}")
    
    def save_custom_database(self, db_path: str = None):
        """保存自定义参考音频数据库"""
        path = db_path or self.db_path
        if not path:
            raise ValueError("未指定数据库文件路径")
        
        # 只保存自定义的部分（排除官方预设）
        custom_db = {
            k: v for k, v in self.database.items()
            if v.get('source') != 'fish_audio_official'
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(custom_db, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 保存自定义参考音频数据库: {len(custom_db)} 条记录")
    
    def get_reference(self, reference_id: str) -> Optional[Dict]:
        """获取指定reference_id的信息"""
        return self.database.get(reference_id)
    
    def get_all_references(self) -> Dict:
        """获取所有reference信息"""
        return self.database.copy()
    
    def search_by_features(self, features: Dict) -> List[Dict]:
        """
        根据特征搜索reference_id
        
        Args:
            features: 特征字典，例如:
                {
                    "gender": "male",
                    "age_group": "middle_aged",
                    "voice_type": "baritone"
                }
        
        Returns:
            匹配的reference列表，按匹配度排序
        """
        matches = []
        
        for ref_id, ref_info in self.database.items():
            score = 0
            matched_features = []
            
            # 匹配性别
            if 'gender' in features and features['gender']:
                if ref_info.get('gender') == features['gender']:
                    score += 3
                    matched_features.append(f"gender={features['gender']}")
            
            # 匹配年龄段
            if 'age_group' in features and features['age_group']:
                if ref_info.get('age_group') == features['age_group']:
                    score += 2
                    matched_features.append(f"age={features['age_group']}")
            
            # 匹配音高
            if 'voice_type' in features and features['voice_type']:
                if ref_info.get('voice_type') == features['voice_type']:
                    score += 2
                    matched_features.append(f"voice_type={features['voice_type']}")
            
            # 匹配标签
            if 'tags' in features and features['tags']:
                for tag in features['tags']:
                    if tag in ref_info.get('tags', []):
                        score += 1
                        matched_features.append(f"tag={tag}")
            
            # 只返回有匹配的结果
            if score > 0:
                matches.append({
                    "reference_id": ref_id,
                    "name": ref_info.get('name', ''),
                    "description": ref_info.get('description', ''),
                    "score": score,
                    "matched_features": matched_features,
                    "info": ref_info
                })
        
        # 按匹配度排序
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        根据关键词搜索reference_id
        
        Args:
            keywords: 关键词列表，例如: ["中年", "男性", "浑厚"]
        
        Returns:
            匹配的reference列表
        """
        matches = []
        
        for ref_id, ref_info in self.database.items():
            score = 0
            matched_keywords = []
            
            # 在描述中搜索
            description = ref_info.get('description', '')
            for keyword in keywords:
                if keyword in description:
                    score += 2
                    matched_keywords.append(keyword)
            
            # 在标签中搜索
            tags = ref_info.get('tags', [])
            for keyword in keywords:
                if keyword in tags:
                    score += 1
                    if keyword not in matched_keywords:
                        matched_keywords.append(keyword)
            
            # 只返回有匹配的结果
            if score > 0:
                matches.append({
                    "reference_id": ref_id,
                    "name": ref_info.get('name', ''),
                    "description": ref_info.get('description', ''),
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "info": ref_info
                })
        
        # 按匹配度排序
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def add_custom_reference(self, 
                            reference_id: str,
                            name: str,
                            gender: str,
                            age_group: str,
                            voice_type: str,
                            description: str,
                            tags: List[str],
                            audio_path: str = None,
                            **kwargs) -> bool:
        """
        添加自定义参考音频
        
        Args:
            reference_id: reference ID
            name: 名称
            gender: 性别 (male/female)
            age_group: 年龄段 (young/middle_aged/old)
            voice_type: 音高类型 (soprano/mezzo_soprano/tenor/baritone/bass)
            description: 描述
            tags: 标签列表
            audio_path: 音频文件路径（可选）
            **kwargs: 其他信息
        
        Returns:
            是否添加成功
        """
        if reference_id in self.database:
            print(f"[WARN] reference_id已存在: {reference_id}")
            return False
        
        ref_info = {
            "name": name,
            "gender": gender,
            "age_group": age_group,
            "voice_type": voice_type,
            "description": description,
            "tags": tags,
            "language": kwargs.get('language', 'zh'),
            "source": "custom",
            **kwargs
        }
        
        if audio_path:
            ref_info['audio_path'] = audio_path
        
        self.database[reference_id] = ref_info
        print(f"[OK] 添加自定义reference: {name} ({reference_id})")
        
        return True
    
    def list_by_category(self, 
                        gender: str = None,
                        age_group: str = None,
                        voice_type: str = None) -> List[Dict]:
        """
        按类别列出reference_id
        
        Args:
            gender: 性别过滤
            age_group: 年龄段过滤
            voice_type: 音高类型过滤
        
        Returns:
            符合条件的reference列表
        """
        results = []
        
        for ref_id, ref_info in self.database.items():
            # 应用过滤条件
            if gender and ref_info.get('gender') != gender:
                continue
            if age_group and ref_info.get('age_group') != age_group:
                continue
            if voice_type and ref_info.get('voice_type') != voice_type:
                continue
            
            results.append({
                "reference_id": ref_id,
                "name": ref_info.get('name', ''),
                "description": ref_info.get('description', ''),
                "info": ref_info
            })
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        stats = {
            "total_count": len(self.database),
            "by_gender": {},
            "by_age_group": {},
            "by_voice_type": {},
            "by_source": {}
        }
        
        for ref_info in self.database.values():
            # 按性别统计
            gender = ref_info.get('gender', 'unknown')
            stats['by_gender'][gender] = stats['by_gender'].get(gender, 0) + 1
            
            # 按年龄段统计
            age = ref_info.get('age_group', 'unknown')
            stats['by_age_group'][age] = stats['by_age_group'].get(age, 0) + 1
            
            # 按音高类型统计
            voice = ref_info.get('voice_type', 'unknown')
            stats['by_voice_type'][voice] = stats['by_voice_type'].get(voice, 0) + 1
            
            # 按来源统计
            source = ref_info.get('source', 'unknown')
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        return stats


# ==================== 便捷函数 ====================

def get_reference_info(reference_id: str) -> Optional[Dict]:
    """获取reference信息的便捷函数"""
    db = ReferenceDatabase()
    return db.get_reference(reference_id)


def search_references(features: Dict) -> List[Dict]:
    """搜索reference的便捷函数"""
    db = ReferenceDatabase()
    return db.search_by_features(features)


def list_references(gender: str = None, age_group: str = None, voice_type: str = None) -> List[Dict]:
    """列出reference的便捷函数"""
    db = ReferenceDatabase()
    return db.list_by_category(gender, age_group, voice_type)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("参考音频数据库管理系统测试")
    print("=" * 70)
    
    # 创建数据库实例
    db = ReferenceDatabase()
    
    # 1. 显示统计信息
    print("\n[STATS] 数据库统计:")
    stats = db.get_statistics()
    print(f"  总计: {stats['total_count']} 个reference")
    print(f"  按性别: {stats['by_gender']}")
    print(f"  按年龄段: {stats['by_age_group']}")
    print(f"  按音高: {stats['by_voice_type']}")
    
    # 2. 按类别列出
    print("\n" + "=" * 70)
    print("📋 列出所有男声reference:")
    print("=" * 70)
    male_refs = db.list_by_category(gender="male")
    for ref in male_refs:
        print(f"  - {ref['name']}: {ref['description']}")
        print(f"    ID: {ref['reference_id']}")
    
    # 3. 特征搜索测试
    print("\n" + "=" * 70)
    print("🔍 特征搜索测试: 中年男中音")
    print("=" * 70)
    features = {
        "gender": "male",
        "age_group": "middle_aged",
        "voice_type": "baritone"
    }
    matches = db.search_by_features(features)
    if matches:
        best = matches[0]
        print(f"  最佳匹配: {best['name']}")
        print(f"  描述: {best['description']}")
        print(f"  匹配度: {best['score']}")
        print(f"  匹配特征: {', '.join(best['matched_features'])}")
        print(f"  Reference ID: {best['reference_id']}")
    
    # 4. 关键词搜索测试
    print("\n" + "=" * 70)
    print("🔍 关键词搜索测试: 清亮甜美")
    print("=" * 70)
    keywords = ["清亮", "甜美"]
    matches = db.search_by_keywords(keywords)
    if matches:
        for match in matches[:3]:
            print(f"  - {match['name']}: {match['description']}")
            print(f"    匹配关键词: {', '.join(match['matched_keywords'])}")
            print(f"    Reference ID: {match['reference_id']}")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
