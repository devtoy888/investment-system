import os, re

# Only fix the 2 obsidian-bridge errors
fixes = {
    '../../raw/papers/网络安全等级保护/核心标准/ocr/定级指南-ocr.md': '../../raw/papers/网络安全等级保护/核心标准/ocr/定级指南-ocr',
    '../../raw/papers/网络安全等级保护/核心标准/ocr/实施指南-ocr.md': '../../raw/papers/网络安全等级保护/核心标准/ocr/实施指南-ocr',
}

for root, dirs, files in os.walk('/docs/docs'):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r') as fh:
            content = fh.read()
        orig = content
        for old, new in fixes.items():
            content = content.replace(f'[[{old}]]', f'[raw源文档]({new})')
            content = content.replace(f'[[{old}|', f'[raw源文档]({new})')
        if content != orig:
            with open(path, 'w') as fh:
                fh.write(content)
            print(f'fixed: {path}')

print('done')
