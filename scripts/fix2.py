#!/usr/bin/env python3
"""Fix duplicate triple-quote"""
content = open('/opt/data/scripts/llm_analysis_v2.py', 'r', encoding='utf-8').read()
old = '还是仅为明日计划"""\n"""'
new = '还是仅为明日计划"""'
if old in content:
    content = content.replace(old, new, 1)
    open('/opt/data/scripts/llm_analysis_v2.py', 'w', encoding='utf-8').write(content)
    print("Fixed")
else:
    print("Pattern not found")
