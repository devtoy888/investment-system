# MkDocs Link Warning Diagnostic & Fix Reference

## Warning Types

### 1. `unrecognized relative link 'X'` ❌ Must Fix

The link `<a href="X">` points to a path that MkDocs cannot resolve to any page.

**Two possible sources:**

| Source | Format | Example |
|--------|--------|---------|
| Wikilink (obsidian-bridge) | `[[index]]` | resolved to `<a href="index">` |
| Graphify 图谱 widget | `[index](index)` | standard markdown link |

**Diagnostic:**

```bash
# Check for wikilink source
docker exec llm-wiki sh -c "find /docs/docs -name '*.md' -exec grep -n '\[\[index\]\]' {} + | head -10"

# Check for markdown link source
docker exec llm-wiki sh -c "find /docs/docs -name '*.md' -exec grep -n '\[index\](index)' {} + | head -10"
```

### 2. `absolute link '/'` ℹ️ Harmless INFO

MkDocs prefers relative paths. Absolute paths work perfectly on deployed sites.

## Fix Recipes

### Fix A: `[index](index)` → `[首页](/)` (Graphify output)

```bash
docker exec llm-wiki sh -c "
  find /docs/docs -name '*.md' -exec sed -i \
    -e 's|\[index\](index)|[首页](/)|g' \
    -e 's|\[index\](entities/index)|[实体索引](/entities/)|g' \
    -e 's|\[index\](concepts/index)|[概念索引](/concepts/)|g' \
    -e 's|\[index\](queries/index)|[查询归档](/queries/)|g' \
    -e 's|\[index\](comparisons/index)|[对比分析](/comparisons/)|g' \
    -e 's|\[index\](concepts/网络安全等级保护/index)|[等保索引](/concepts/网络安全等级保护/)|g' \
    {} +
  echo 'Done'
"
```

### Fix B: `[[index]]` → `[首页](/)` (Agent-generated wikilinks)

```bash
docker exec llm-wiki sh -c "
  find /docs/docs -name '*.md' -exec sed -i \
    -e 's|\[\[index\]\]|[首页](/)|g' \
    -e 's|\[\[entities/index\]\]|[实体索引](/entities/)|g' \
    -e 's|\[\[concepts/index\]\]|[概念索引](/concepts/)|g' \
    -e 's|\[\[queries/index\]\]|[查询归档](/queries/)|g' \
    -e 's|\[\[comparisons/index\]\]|[对比分析](/comparisons/)|g' \
    -e 's|\[\[concepts/网络安全等级保护/index\]\]|[等保索引](/concepts/网络安全等级保护/)|g' \
    {} +
  echo 'Done'
"
```

### Fix C: Absolute links → Relative paths (silences INFO warnings)

**Approach A — Suppress via `validation:` config (recommended):**

```yaml
# In mkdocs.yml — suppresses ALL absolute/unrecognized link warnings
validation:
  absolute_links: ignore
  unrecognized_links: ignore
```

**Approach B — Manually convert to relative paths (only if config not desired):**

⚠️ **DON'T use complex sed with escaped backticks** — it corrupts files. Use Python inside the container instead:

```bash
docker exec llm-wiki python3 -c "
import os
for root, dirs, files in os.walk('/docs/docs/entities'):
    for f in files:
        if not f.endswith('.md'): continue
        p = os.path.join(root, f)
        with open(p) as fh: c = fh.read()
        o = c
        c = c.replace('[首页](/)', '[首页](../index.md)')
        c = c.replace('[实体索引](/entities/)', '[实体索引](index.md)')
        if c != o:
            with open(p, 'w') as fh: fh.write(c)
            print(f'fixed: {p}')

for root, dirs, files in os.walk('/docs/docs/queries'):
    for f in files:
        if not f.endswith('.md'): continue
        p = os.path.join(root, f)
        with open(p) as fh: c = fh.read()
        o = c
        c = c.replace('[首页](/)', '[首页](../index.md)')
        c = c.replace('[查询归档](/queries/)', '[查询归档](index.md)')
        if c != o:
            with open(p, 'w') as fh: fh.write(c)
            print(f'fixed: {p}')
print('done')
"
```

### Fix D: Missing `.md` suffix in raw cross-references

```bash
docker exec llm-wiki sed -i \
  's|](concepts/网络安全等级保护/GB-T-22240-2020-定级指南)|](concepts/网络安全等级保护/GB-T-22240-2020-定级指南.md)|g' \
  /docs/docs/raw/papers/网络安全等级保护/核心标准/ocr/定级指南-ocr.md

docker exec llm-wiki sed -i \
  's|](concepts/网络安全等级保护/GB-T-25058-2019-实施指南)|](concepts/网络安全等级保护/GB-T-25058-2019-实施指南.md)|g' \
  /docs/docs/raw/papers/网络安全等级保护/核心标准/ocr/实施指南-ocr.md
```

## "Pages Not in Nav" INFO

MkDocs generates this INFO when `.md` files exist in the docs directory but aren't in the `nav:` config:

```
INFO - The following pages exist in the docs directory, but are not included in the "nav" configuration:
```

### Root Cause

MkDocs `nav:` is **static** — it only lists explicitly named pages. Subdirectory files (e.g., `concepts/网络安全等级保护/*.md`) are not auto-included even when the parent `index.md` is in nav.

**❌ MkDocs does NOT support bare directory references.** Writing:

```yaml
nav:
  - 等保 2.0: concepts/网络安全等级保护/   # ← WRONG, MkDocs WARNINGs "not found"
```

...causes `WARNING - A reference to '.../' is included in the 'nav' configuration, which is not found`.

### Fix: List Every Page Explicitly

Each `.md` file must be listed individually:

```yaml
nav:
  - 📖 概念:
    - 概念索引: concepts/index.md
    - 等保 2.0: concepts/网络安全等级保护/index.md
    - 概述: concepts/网络安全等级保护/概述.md
    - GB/T 22239-2019 基本要求: concepts/网络安全等级保护/GB-T-22239-2019-基本要求.md
    ...
    - Vibe-Trading: concepts/vibe-trading/index.md
    - 项目总览: concepts/vibe-trading/项目总览.md
    ...
```

### Automated Nav Generation

Maintaining nav manually is impractical. Use `scripts/update-nav.py` which auto-scans docs/ and writes the nav section:

```bash
python3 /llm-wiki/scripts/update-nav.py
docker restart llm-wiki
```

The script:
- Scans `entities/`, `concepts/` (incl. subdirs), `comparisons/`, `queries/`
- Lists all `.md` files in each section
- Preserves the rest of `mkdocs.yml` (theme, plugins, validation config)
- Logs the change to `docs/log.md`

**Recommended cron schedule**: daily at 04:30 (after graph rebuild at 04:00):

```bash
30 4 * * * python3 /llm-wiki/scripts/update-nav.py && docker restart llm-wiki
```

### What raw/ Pages Are Not in Nav

`raw/` pages are intentionally excluded — they are source materials, not navigation targets. This is expected and correct behavior.

## Container Environment Notes

### BusyBox Grep Limitations

Inside `squidfunk/mkdocs-material` container, grep is BusyBox:

| Feature | Status | Alternative |
|---------|--------|-------------|
| `--include=*.md` | ❌ Not supported | `find ... -exec grep ... {} +` |
| `-E` (extended regex) | ✅ Supported | Use instead of `-P` |

## Verification

```bash
docker restart llm-wiki
sleep 3
docker logs llm-wiki --tail 10
# Expected: Zero lines with 'unrecognized relative link'
```

### Fix E: Comprehensive relative-link fix for 图谱关联 sections

Graphify generates the "图谱关联" section on every page with relative paths, creating doubled-path links. Use Python inside the container:

```bash
docker exec llm-wiki python3 -c "
import os, re

for root, dirs, files in os.walk('/docs/docs'):
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        with open(path) as fh: content = fh.read()
        orig = content

        def fix_section(m):
            sec = m.group(0)
            def fix_link(m2):
                url = m2.group(2)
                if url.startswith('/') or url.startswith('http'): return m2.group(0)
                url = re.sub(r'\.md$', '', url)
                if url in ('index.md', 'index'): url = '/'
                else: url = '/' + url + '/'
                return f'[{m2.group(1)}]({url})'
            return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', fix_link, sec)

        content = re.sub(
            r'## 📊 图谱关联.*?(?=\n## |\Z)',
            fix_section,
            content,
            flags=re.DOTALL
        )

        if content != orig:
            with open(path, 'w') as fh: fh.write(content)
            print(f'fixed: {os.path.relpath(path, \"/docs/docs\")}')
print('done')
"
```

**Post-fix path correction** (links may lose directory context like `queries/` prefix):

```python
fixes = {
    '/docs/docs/queries/index.md': [
        ('(/飞书代码块渲染对比-验证记录/)', '(/queries/飞书代码块渲染对比-验证记录/)'),
        ('(/测评机构资质要求/)', '(/queries/测评机构资质要求/)'),
    ],
}
for path, file_fixes in fixes.items():
    with open(path) as f: content = f.read()
    orig = content
    for old, new in file_fixes:
        content = content.replace(old, new)
    if content != orig:
        with open(path, 'w') as f: f.write(content)
```

### Fix F: obsidian-bridge `../../raw/...` path error

obsidian-bridge cannot resolve `../../raw/...` relative paths (returns `ERROR - [ObsidianBridge] No candidates`). Convert to absolute paths:

```bash
docker exec llm-wiki sed -i \
  's|../../raw/papers/网络安全等级保护/核心标准/ocr/定级指南-ocr.md|/raw/papers/网络安全等级保护/核心标准/ocr/定级指南-ocr|g' \
  /docs/docs/concepts/网络安全等级保护/GB-T-22240-2020-定级指南.md

docker exec llm-wiki sed -i \
  's|../../raw/papers/网络安全等级保护/核心标准/ocr/实施指南-ocr.md|/raw/papers/网络安全等级保护/核心标准/ocr/实施指南-ocr|g' \
  /docs/docs/concepts/网络安全等级保护/GB-T-25058-2019-实施指南.md
```

## Self-Check After Fixes

Run ALL checks before declaring done:

### 1. Docker logs — zero warnings
```bash
docker restart llm-wiki
sleep 3
docker logs llm-wiki --tail 20
# Expect: Zero 'unrecognized relative link', Zero 'ObsidianBridge ERROR', Zero 'absolute link'
```

### 2. Live page verification (from Hermes container)
Use `web_extract` to verify key pages return 200:
```
https://wiki.devtoy.xyz/
https://wiki.devtoy.xyz/entities/
https://wiki.devtoy.xyz/concepts/
https://wiki.devtoy.xyz/comparisons/
https://wiki.devtoy.xyz/queries/
https://wiki.devtoy.xyz/concepts/knowledge-graph/
```

### 3. Source file integrity
```bash
docker exec llm-wiki sh -c "grep -c '图谱关联' /docs/docs/concepts/knowledge-graph.md"
# Expect: 1 (section not deleted)
```
