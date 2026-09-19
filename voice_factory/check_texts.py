#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查文本文件情况"""
import os

text_dir = "texts"
files = [f for f in os.listdir(text_dir) if f.endswith('.txt')]
print(f'文本文件数量: {len(files)}')

total_lines = 0
for f in files:
    content = open(os.path.join(text_dir, f), 'r', encoding='utf-8').read().strip()
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    total_lines += len(lines)
    print(f'{f}: {len(lines)} 行')

print(f'\n总行数: {total_lines}')
print(f'需要至少 150 行（5个speaker × 30句）')
if total_lines < 150:
    print(f'⚠️  文本不足，还需 {150 - total_lines} 行')
else:
    print(f'✅ 文本充足')
