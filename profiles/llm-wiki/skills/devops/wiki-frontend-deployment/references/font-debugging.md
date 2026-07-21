# Matplotlib CJK Font Debugging for Graphify SVG

Debugging transcript for getting Chinese characters to render in Matplotlib-generated SVG nodes.

## The Problem

Graphify's `export.to_svg()` uses `nx.draw_networkx_labels()` which calls `ax.text()` with Matplotlib. The SVG must contain proper CJK glyph paths or the browser shows tofu (□□□).

## Attempted Solutions

### Attempt 1: DejaVuSans (default)
- **Result**: ❌ Boxes (□□□)
- **Cause**: DejaVuSans has zero CJK glyphs
- **Lesson**: Must configure a CJK font explicitly

### Attempt 2: WenQuanYi Zen Hei (`.ttc`)
- **Result**: ❌ Each Chinese character rendered as wrong glyph, off by +1 code point
  - e.g. 完(U+5B8C) → 宍(U+5B8D), 整(U+6574) → 敵(U+6575), etc.
- **Root cause**: `wqy-zenhei.ttc` is a **TrueType Collection** (3 fonts in one file). Matplotlib extracts glyph indices from the collection with a systematic +1 offset. The font weight warning `findfont: Failed to find font weight normal, now using 500` was a symptom.
- **Diagnosis**: Checked SVG `<use>` elements — glyph IDs were `WenQuanYiZenHei-3058` (じ), `WenQuanYiZenHei-3a40` (㩀) instead of expected CJK code points for "完整搭建方案"
- **Lesson**: TTC == dangerous with Matplotlib. Use standalone TTF only.

### Attempt 3: Unifont (`.otf`)
- **Result**: ❌ Same +1 offset
- **Symptom**: 完(U+5B8C)→宍(U+5B8D), etc. — identical systematic shift
- **Lesson**: OTF without proper glyph-to-Unicode mapping has same issue

### Attempt 4: Noto Sans CJK (downloaded `.otf` from GitHub)
- **Result**: ❌ `FT_Open_Face failed: unknown file format`
- **Root cause**: The GitHub raw `.otf` was actually a broken/truncated download (312KB instead of expected ~15MB)
- **Lesson**: Verify downloaded font file before use

### Attempt 5: LXGW WenKai (`.ttf`)
- **Result**: ✅ Success — 862 CJK glyphs, 1479 WenKai path references
- **Why it worked**: Standalone `.ttf` (not TTC), proper glyph-to-Unicode mapping, correct font file
- **Glyph IDs seen**: `LXGWWenKai-Regular-1c3e`, `LXGWWenKai-Regular-23a6`, etc. (font-internal glyph indices, not Unicode — but mapped correctly)

## Diagnostic Commands

### Check what font is actually used in SVG:
```python
import re
with open('graph.svg') as f:
    content = f.read()
for m in re.finditer(r'<path id="([^"]+)"', content):
    print(m.group(1))  # Shows "WenQuanYiZenHei-xxx" or "LXGWWenKai-Regular-xxx" etc.
```

### Check if Chinese glyphs map correctly in test:
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont('/path/to/font.ttf')
prop = font_manager.FontProperties(fname='/path/to/font.ttf')
plt.rcParams['font.sans-serif'] = [prop.get_name()]
plt.rcParams['axes.unicode_minus'] = False
font_manager._load_fontmanager(try_read_cache=False)

fig, ax = plt.subplots(figsize=(4, 0.5))
ax.text(0.5, 0.5, '完整搭建方案', fontsize=20, ha='center', va='center')
ax.axis('off')
fig.savefig('/tmp/test.svg', format='svg')
plt.close()

# Check if glyphs map to expected CJK Unicode range (U+4E00–U+9FFF)
import re
with open('/tmp/test.svg') as f:
    out = f.read()
for m in re.finditer(r'<use xlink:href="#([^"]+)"', out):
    suffix = m.group(1).split('-')[-1]
    try:
        cp = int(suffix, 16)
        if 0x4E00 <= cp <= 0x9FFF:
            print(f'CJK: U+{cp:04X} {chr(cp)}')
    except ValueError:
        pass
```

### Check system CJK fonts:
```bash
fc-list :lang=zh
matplotlib.font_manager.fontManager.addfont('/path/to/font.ttf')
```

## Key Configuration Pattern

```python
# CORRECT — works with LXGW WenKai TTF
font_manager.fontManager.addfont('/path/to/WenKai.ttf')
_prop = font_manager.FontProperties(fname='/path/to/WenKai.ttf')
plt.rcParams['font.sans-serif'] = [_prop.get_name()]  # Use .get_name() not hardcoded string
plt.rcParams['axes.unicode_minus'] = False
font_manager._load_fontmanager(try_read_cache=False)   # CRITICAL: rebuild font cache
```

**Wrong patterns that LOOK like they should work but don't:**
- `plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']` — string name lookup may pick wrong font from TTC
- Omitting `font_manager._load_fontmanager()` — new font not seen
- Using `plt.rcParams['font.family']` instead of `font.sans-serif`

## Verification After Fix

Run `bash scripts/verify-wiki-update.sh` from `~/llm-wiki/`. Key checks:
1. SVG file contains `LXGWWenKai` references, not `DejaVuSans` or `WenQuanYi`
2. Container has synced the new SVG (check via `docker exec`)
3. Page has all 5 sections + lightbox components
4. Rebuild script font config is up to date
