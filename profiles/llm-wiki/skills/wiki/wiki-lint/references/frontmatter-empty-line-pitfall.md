# Frontmatter Empty-Line Pitfall

## Problem

LLM-generated markdown files often have an empty line after the opening `---`:

```yaml
---
                           ← BLANK LINE!
title: 实体索引
created: 2026-07-14
type: index
tags: [index]
---
```

This causes YAML parsing to fail because the parser sees an empty key before `title`. The page may still render in MkDocs (which silently ignores broken frontmatter) but:
- Dataview/metadata queries won't find the page
- `extra_javascript` that relies on `type` field won't work
- The lint script's `frontmatter_issues` check flags it

## Fix

```python
with open(file_path) as f:
    lines = f.read().split('\n')
# Remove empty lines immediately after ---
if lines[0] == '---' and lines[1] == '' and lines[2].startswith('title:'):
    lines.pop(1)
with open(file_path, 'w') as f:
    f.write('\n'.join(lines))
```

## Detection in lint-wiki.py

The current frontmatter check splits on `---` and expects exactly 3 parts. An empty line after `---` produces an additional part, causing the check to flag "missing/invalid type" or "no frontmatter at all" as a side effect. The fix script (`fix-wiki.py`) should strip empty lines from the frontmatter block.
