#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人物画像到 TTS 参数映射系统
根据人物画像特征，生成对应的 Fish Speech TTS 参数配置
"""

import random
from typing import Dict, Tuple, Optional


# 人物画像到 TTS 参数的映射表
# 注意：这些参数需要通过实际测试和优化来调整
PORTRAIT_TTS_MAPPING = {
    # ==================== 男声声模 ====================
    "中年男中音": {
        "temperature": 0.75,  # 较低温度，声音稳定成熟
        "top_p": 0.85,
        "repetition_penalty": 1.15,
        "seed_range": (1000, 2500),  # 男声中音种子范围
        "description": "成熟稳重的中年男性声音，音色浑厚温暖"
    },
    "中年男低音": {
        "temperature": 0.73,  # 更低温度，声音更深沉
        "top_p": 0.83,
        "repetition_penalty": 1.16,
        "seed_range": (500, 1500),  # 男声低音种子范围
        "description": "深沉厚重的中年男性声音，音色低沉磁性"
    },
    "青年男高音": {
        "temperature": 0.78,  # 稍高温度，声音更明亮
        "top_p": 0.87,
        "repetition_penalty": 1.13,
        "seed_range": (2500, 4000),  # 男声高音种子范围
        "description": "明亮活力的年轻男性声音，音色清朗阳光"
    },
    "中年男高音": {
        "temperature": 0.77,
        "top_p": 0.86,
        "repetition_penalty": 1.14,
        "seed_range": (2800, 4200),
        "description": "激情澎湃的中年男性声音，音色高亢有力"
    },
    
    # ==================== 女声声模 ====================
    "青年女高音": {
        "temperature": 0.82,  # 较高温度，声音活泼清亮
        "top_p": 0.89,
        "repetition_penalty": 1.11,
        "seed_range": (7000, 9000),  # 女声高音种子范围
        "description": "清亮甜美的年轻女性声音，音色明亮活泼"
    },
    "青年女中音": {
        "temperature": 0.80,  # 中等温度，声音温柔
        "top_p": 0.88,
        "repetition_penalty": 1.12,
        "seed_range": (5000, 7000),  # 女声中音种子范围
        "description": "温柔知性的年轻女性声音，音色柔和亲切"
    },
    "中年女低音": {
        "temperature": 0.76,  # 较低温度，声音温婉成熟
        "top_p": 0.84,
        "repetition_penalty": 1.15,
        "seed_range": (4000, 5500),  # 女声低音种子范围
        "description": "温婉成熟的中年女性声音，音色柔和沉稳"
    },
}


# 预设的20个人物画像列表
PRESET_PORTRAITS = [
    "中年男中音",  # speaker_0001, 0007, 0011, 0017
    "青年女高音",  # speaker_0002, 0008, 0012, 0016, 0020
    "中年男低音",  # speaker_0003, 0009, 0015, 0019
    "青年女中音",  # speaker_0004, 0010, 0014, 0018
    "青年男高音",  # speaker_0005
    "中年女低音",  # speaker_0006
    "中年男高音",  # speaker_0013
]


def get_tts_config_for_portrait(portrait: str) -> Dict:
    """
    根据人物画像获取 TTS 参数配置
    
    Args:
        portrait: 人物画像描述（如"中年男中音"）
    
    Returns:
        dict: TTS 参数配置
    """
    # 精确匹配
    if portrait in PORTRAIT_TTS_MAPPING:
        config = PORTRAIT_TTS_MAPPING[portrait].copy()
        config['portrait'] = portrait
        return config
    
    # 模糊匹配（支持自定义画像）
    matched_config = fuzzy_match_portrait(portrait)
    if matched_config:
        return matched_config
    
    # 默认配置（中年男中音）
    print(f"⚠️  未找到匹配的画像配置: {portrait}")
    print("💡 使用默认配置（中年男中音）")
    config = PORTRAIT_TTS_MAPPING["中年男中音"].copy()
    config['portrait'] = portrait
    config['is_default'] = True
    return config


def fuzzy_match_portrait(portrait: str) -> Optional[Dict]:
    """
    模糊匹配人物画像
    
    Args:
        portrait: 人物画像描述
    
    Returns:
        dict or None: 匹配的配置
    """
    portrait_lower = portrait.lower()
    
    # 提取关键词
    has_male = any(k in portrait_lower for k in ['男', 'male'])
    has_female = any(k in portrait_lower for k in ['女', 'female'])
    
    has_young = any(k in portrait_lower for k in ['青年', '年轻', 'young'])
    has_middle = any(k in portrait_lower for k in ['中年', 'middle'])
    
    has_high = any(k in portrait_lower for k in ['高音', 'high'])
    has_middle_tone = any(k in portrait_lower for k in ['中音', 'middle'])
    has_low = any(k in portrait_lower for k in ['低音', 'low'])
    
    # 组合匹配
    if has_male:
        if has_middle and has_middle_tone:
            return get_base_config("中年男中音", portrait)
        elif has_middle and has_low:
            return get_base_config("中年男低音", portrait)
        elif (has_young or not has_middle) and has_high:
            return get_base_config("青年男高音", portrait)
        elif has_middle:
            return get_base_config("中年男中音", portrait)
    elif has_female:
        if (has_young or not has_middle) and has_high:
            return get_base_config("青年女高音", portrait)
        elif (has_young or not has_middle) and has_middle_tone:
            return get_base_config("青年女中音", portrait)
        elif has_middle and has_low:
            return get_base_config("中年女低音", portrait)
        elif has_young:
            return get_base_config("青年女中音", portrait)
    
    return None


def get_base_config(portrait_key: str, custom_portrait: str) -> Dict:
    """
    获取基础配置并添加自定义画像信息
    
    Args:
        portrait_key: 预设画像键名
        custom_portrait: 自定义画像描述
    
    Returns:
        dict: 配置字典
    """
    config = PORTRAIT_TTS_MAPPING[portrait_key].copy()
    config['portrait'] = custom_portrait
    config['matched_from'] = portrait_key
    config['is_fuzzy_match'] = True
    return config


def generate_random_seed(portrait: str) -> int:
    """
    根据画像生成随机种子
    
    Args:
        portrait: 人物画像描述
    
    Returns:
        int: 随机种子
    """
    config = get_tts_config_for_portrait(portrait)
    seed_range = config['seed_range']
    return random.randint(seed_range[0], seed_range[1])


def generate_tts_params(portrait: str, fixed_seed: Optional[int] = None) -> Dict:
    """
    生成完整的 TTS 参数
    
    Args:
        portrait: 人物画像描述
        fixed_seed: 固定种子（可选）
    
    Returns:
        dict: TTS 参数
    """
    config = get_tts_config_for_portrait(portrait)
    
    params = {
        "temperature": config['temperature'],
        "top_p": config['top_p'],
        "repetition_penalty": config['repetition_penalty'],
        "seed": fixed_seed if fixed_seed else generate_random_seed(portrait),
        "portrait": config['portrait'],
        "description": config['description']
    }
    
    return params


def list_available_portraits() -> list:
    """
    列出所有可用的预设画像
    
    Returns:
        list: 画像列表
    """
    return list(PORTRAIT_TTS_MAPPING.keys())


def get_portrait_info(portrait: str) -> Dict:
    """
    获取画像的详细信息
    
    Args:
        portrait: 人物画像描述
    
    Returns:
        dict: 画像信息
    """
    config = get_tts_config_for_portrait(portrait)
    return {
        "portrait": config['portrait'],
        "description": config.get('description', ''),
        "temperature": config['temperature'],
        "top_p": config['top_p'],
        "repetition_penalty": config['repetition_penalty'],
        "seed_range": config['seed_range'],
        "is_preset": portrait in PORTRAIT_TTS_MAPPING
    }


# 测试代码
if __name__ == "__main__":
    print("="*70)
    print("🎨 人物画像到 TTS 参数映射系统测试")
    print("="*70)
    
    # 列出所有可用画像
    print("\n📋 可用画像列表:")
    for i, portrait in enumerate(list_available_portraits(), 1):
        info = get_portrait_info(portrait)
        print(f"  {i}. {portrait} - {info['description']}")
    
    # 测试预设画像
    print("\n" + "="*70)
    print("🧪 测试预设画像")
    print("="*70)
    
    test_portraits = ["中年男中音", "青年女高音", "中年男低音"]
    for portrait in test_portraits:
        print(f"\n🎤 画像: {portrait}")
        params = generate_tts_params(portrait)
        print(f"  参数: {params}")
    
    # 测试自定义画像
    print("\n" + "="*70)
    print("🧪 测试自定义画像（模糊匹配）")
    print("="*70)
    
    custom_portraits = [
        "年轻女高音，活泼可爱",
        "成熟男低音，深沉磁性",
        "温柔女中音，知性优雅"
    ]
    
    for portrait in custom_portraits:
        print(f"\n🎤 自定义画像: {portrait}")
        params = generate_tts_params(portrait)
        print(f"  参数: {params}")
        if 'matched_from' in params:
            print(f"  匹配自: {params['matched_from']}")
    
    print("\n" + "="*70)
    print("✅ 测试完成！")
    print("="*70)
