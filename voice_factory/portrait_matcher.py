#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能匹配引擎
从角色描述中提取特征，智能匹配最合适的reference_id
"""

import re
from typing import Dict, List, Optional, Tuple
from reference_database import ReferenceDatabase, GENDER_KEYWORDS, AGE_KEYWORDS, VOICE_TYPE_KEYWORDS, TONE_KEYWORDS


class PortraitMatcher:
    """角色画像智能匹配器"""
    
    def __init__(self):
        self.db = ReferenceDatabase()
    
    def extract_features(self, portrait_description: str) -> Dict:
        """
        从角色描述中提取声学特征
        
        Args:
            portrait_description: 角色描述，例如"成熟稳重的中年男性声音，音色浑厚温暖"
        
        Returns:
            特征字典，例如:
            {
                "gender": "male",
                "age_group": "middle_aged",
                "voice_type": "baritone",
                "tone_tags": ["浑厚", "温暖", "稳重"]
            }
        """
        desc = portrait_description.lower()
        features = {
            "gender": None,
            "age_group": None,
            "voice_type": None,
            "tone_tags": []
        }
        
        # 1. 提取性别
        for gender, keywords in GENDER_KEYWORDS.items():
            if any(kw in desc for kw in keywords):
                features["gender"] = gender
                break
        
        # 2. 提取年龄段（按优先级：old > young > middle_aged）
        age_priority = ["old", "young", "middle_aged"]
        for age in age_priority:
            if age in AGE_KEYWORDS:
                if any(kw in desc for kw in AGE_KEYWORDS[age]):
                    features["age_group"] = age
                    break
        
        # 3. 提取音高类型
        for voice_type, keywords in VOICE_TYPE_KEYWORDS.items():
            if any(kw in desc for kw in keywords):
                features["voice_type"] = voice_type
                break
        
        # 4. 提取音色特征标签
        for tone, keywords in TONE_KEYWORDS.items():
            if any(kw in desc for kw in keywords):
                if tone not in features["tone_tags"]:
                    features["tone_tags"].append(tone)
        
        return features
    
    def match_reference(self, portrait_description: str) -> Optional[Dict]:
        """
        智能匹配reference_id
        
        Args:
            portrait_description: 角色描述
        
        Returns:
            匹配结果，例如:
            {
                "reference_id": "536d3a5e000945adb7038665781a4aca",
                "name": "Ethan",
                "description": "成熟稳重的中年男性声音，音色浑厚温暖",
                "confidence": 0.95,
                "matched_features": ["gender=male", "age=middle_aged", "voice_type=baritone"],
                "reason": "完美匹配：中年男性，中音，稳重浑厚"
            }
        """
        # 1. 提取特征
        features = self.extract_features(portrait_description)
        
        # 2. 特征搜索
        matches = self.db.search_by_features(features)
        
        if not matches:
            # 3. 如果特征搜索失败，尝试关键词搜索
            keywords = features["tone_tags"]
            if keywords:
                matches = self.db.search_by_keywords(keywords)
        
        if not matches:
            return None
        
        # 4. 选择最佳匹配
        best_match = matches[0]
        
        # 5. 计算置信度
        max_possible_score = 7  # gender(3) + age(2) + voice_type(2)
        confidence = min(best_match["score"] / max_possible_score, 1.0)
        
        # 6. 生成匹配原因
        reason = self._generate_reason(features, best_match)
        
        return {
            "reference_id": best_match["reference_id"],
            "name": best_match["name"],
            "description": best_match["description"],
            "confidence": round(confidence, 2),
            "matched_features": best_match.get("matched_features", []),
            "reason": reason,
            "extracted_features": features
        }
    
    def _generate_reason(self, features: Dict, match: Dict) -> str:
        """生成匹配原因说明"""
        reasons = []
        
        # 性别匹配
        if features["gender"]:
            gender_map = {"male": "男性", "female": "女性"}
            reasons.append(gender_map.get(features["gender"], features["gender"]))
        
        # 年龄匹配
        if features["age_group"]:
            age_map = {"young": "青年", "middle_aged": "中年", "old": "老年"}
            reasons.append(age_map.get(features["age_group"], features["age_group"]))
        
        # 音高匹配
        if features["voice_type"]:
            voice_map = {
                "soprano": "高音",
                "mezzo_soprano": "中音",
                "tenor": "高音",
                "baritone": "中音",
                "bass": "低音"
            }
            reasons.append(voice_map.get(features["voice_type"], features["voice_type"]))
        
        # 音色特征
        if features["tone_tags"]:
            reasons.append("、".join(features["tone_tags"][:3]))
        
        return "匹配特征：" + "，".join(reasons) if reasons else "默认匹配"
    
    def match_multiple(self, portraits: List[str]) -> List[Dict]:
        """
        批量匹配多个角色描述
        
        Args:
            portraits: 角色描述列表
        
        Returns:
            匹配结果列表
        """
        results = []
        for portrait in portraits:
            result = self.match_reference(portrait)
            if result:
                result["portrait"] = portrait
                results.append(result)
        return results
    
    def get_alternatives(self, portrait_description: str, top_n: int = 3) -> List[Dict]:
        """
        获取多个备选匹配
        
        Args:
            portrait_description: 角色描述
            top_n: 返回前N个备选
        
        Returns:
            备选匹配列表
        """
        features = self.extract_features(portrait_description)
        matches = self.db.search_by_features(features)
        
        if not matches:
            keywords = features["tone_tags"]
            if keywords:
                matches = self.db.search_by_keywords(keywords)
        
        # 返回前N个
        results = []
        for match in matches[:top_n]:
            max_possible_score = 7
            confidence = min(match["score"] / max_possible_score, 1.0)
            
            results.append({
                "reference_id": match["reference_id"],
                "name": match["name"],
                "description": match["description"],
                "confidence": round(confidence, 2),
                "score": match["score"]
            })
        
        return results


# ==================== 便捷函数 ====================

def match_portrait(portrait_description: str) -> Optional[Dict]:
    """匹配角色描述的便捷函数"""
    matcher = PortraitMatcher()
    return matcher.match_reference(portrait_description)


def extract_features(portrait_description: str) -> Dict:
    """提取特征的便捷函数"""
    matcher = PortraitMatcher()
    return matcher.extract_features(portrait_description)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 70)
    print("智能匹配引擎测试")
    print("=" * 70)
    
    matcher = PortraitMatcher()
    
    # 测试1: 预设画像
    test_portraits = [
        "成熟稳重的中年男性声音，音色浑厚温暖",
        "清亮甜美的年轻女性声音，音色明亮活泼",
        "深沉厚重的中年男性声音，音色低沉磁性",
        "温柔知性的年轻女性声音，音色柔和亲切",
        "明亮活力的年轻男性声音，音色清朗阳光"
    ]
    
    print("\n[Test 1] 预设画像匹配:")
    for portrait in test_portraits:
        print(f"\n输入: {portrait}")
        result = matcher.match_reference(portrait)
        if result:
            print(f"  匹配: {result['name']}")
            print(f"  Reference ID: {result['reference_id']}")
            print(f"  置信度: {result['confidence']}")
            print(f"  原因: {result['reason']}")
        else:
            print("  [WARN] 未找到匹配")
    
    # 测试2: 自定义画像
    print("\n" + "=" * 70)
    print("[Test 2] 自定义画像匹配:")
    custom_portraits = [
        "老年男性，声音沧桑厚重",
        "年轻女孩，声音可爱甜美",
        "成熟女性，声音温婉大方"
    ]
    
    for portrait in custom_portraits:
        print(f"\n输入: {portrait}")
        result = matcher.match_reference(portrait)
        if result:
            print(f"  匹配: {result['name']}")
            print(f"  Reference ID: {result['reference_id']}")
            print(f"  置信度: {result['confidence']}")
            print(f"  原因: {result['reason']}")
        else:
            print("  [WARN] 未找到匹配")
    
    # 测试3: 特征提取
    print("\n" + "=" * 70)
    print("[Test 3] 特征提取测试:")
    test_desc = "成熟稳重的中年男性声音，音色浑厚温暖"
    features = matcher.extract_features(test_desc)
    print(f"输入: {test_desc}")
    print(f"提取特征: {features}")
    
    # 测试4: 备选匹配
    print("\n" + "=" * 70)
    print("[Test 4] 备选匹配测试:")
    portrait = "中年男性声音"
    print(f"输入: {portrait}")
    alternatives = matcher.get_alternatives(portrait, top_n=3)
    for i, alt in enumerate(alternatives, 1):
        print(f"  {i}. {alt['name']} (confidence: {alt['confidence']})")
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)
