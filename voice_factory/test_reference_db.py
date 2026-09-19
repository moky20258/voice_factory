#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试参考音频数据库搜索功能"""
from reference_database import ReferenceDatabase

db = ReferenceDatabase()

# 测试1: 特征搜索 - 中年男中音
print("Test 1: Search for middle-aged male baritone")
features = {
    "gender": "male",
    "age_group": "middle_aged",
    "voice_type": "baritone"
}
matches = db.search_by_features(features)
if matches:
    for m in matches[:3]:
        print(f"  {m['name']}: score={m['score']}, id={m['reference_id']}")

# 测试2: 特征搜索 - 青年女高音
print("\nTest 2: Search for young female soprano")
features = {
    "gender": "female",
    "age_group": "young",
    "voice_type": "soprano"
}
matches = db.search_by_features(features)
if matches:
    for m in matches[:3]:
        print(f"  {m['name']}: score={m['score']}, id={m['reference_id']}")

# 测试3: 关键词搜索
print("\nTest 3: Search by keywords: 清亮甜美")
matches = db.search_by_keywords(["清亮", "甜美"])
if matches:
    for m in matches[:3]:
        print(f"  {m['name']}: {m['description']}")
        print(f"    matched: {m['matched_keywords']}")

print("\nAll tests completed!")
