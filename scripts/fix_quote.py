#!/usr/bin/env python3
"""Fix the duplicate triple-quote in llm_analysis_v2.py"""
content = open('/opt/data/scripts/llm_analysis_v2.py', 'r', encoding='utf-8').read()

# Find the pattern: 计划"""\n"""\n\n\nFINANCIAL_THEORY_FRAMEWORK
# Replace with: 计划\n\n\n\nFINANCIAL_THEORY_FRAMEWORK
old = '计划"""\n"""\n\n\nFINANCIAL_THEORY_FRAMEWORK'
new = '计划\n\n\n\nFINANCIAL_THEORY_FRAMEWORK'

if old in content:
    content = content.replace(old, new, 1)
    open('/opt/data/scripts/llm_analysis_v2.py', 'w', encoding='utf-8').write(content)
    print("Fixed: removed duplicate triple-quote")
else:
    print("Pattern not found - checking alternatives...")
    # Debug: show the area around line 49
    lines = content.split('\n')
    for i in range(46, 56):
        print(f'  {i+1}: {repr(lines[i])}')
