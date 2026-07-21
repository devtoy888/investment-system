# Douyin Sans Bold Font Setup

## Official Source

ByteDance open-sourced the Douyin Sans font family under the SIL Open Font License 1.1.

- **Official repo**: https://github.com/bytedance/fonts
- **Font directory**: `DouyinSans/`
- **Available files**: `DouyinSansBold.ttf`, `DouyinSans-Regular.ttf`
- **License**: SIL Open Font License 1.1 (free for commercial use)

## Download

```bash
# DouyinSans Bold (TTF — use this one)
curl -sL -o /opt/data/scripts/DouyinSansBold.ttf \
  https://raw.githubusercontent.com/bytedance/fonts/main/DouyinSans/DouyinSansBold.ttf

# Verify
python3 -c "
from PIL import ImageFont
font = ImageFont.truetype('/opt/data/scripts/DouyinSansBold.ttf', 24)
print(f'Font: {font.getname()}')
print(f'BBox (你好): {font.getbbox(\"你好世界\")}')
"
```

## Format: TTF, not OTF

The ByteDance repository only provides **TTF** files. **There is no `DouyinSansBold.otf` file.** The previous font_paths entry `/tmp/DouyinSansBold.otf` was always wrong — even if the file existed at that path, PIL would fail to load it because the actual format is TTF.

## Persistent Storage

**Never put the font in `/tmp/`.** Docker containers clear `/tmp` on restart. Use a persistent path mounted from the host:

| Location | Persistent? | Purpose |
|----------|------------|---------|
| `/opt/data/scripts/DouyinSansBold.ttf` | ✅ Yes (Docker volume) | Primary font location |
| `/tmp/DouyinSansBold.otf` | ❌ No (lost on restart) | Legacy backward compatibility only |

After container restart, verify font persists:
```bash
python3 -c "from PIL import ImageFont; font = ImageFont.truetype('/opt/data/scripts/DouyinSansBold.ttf', 24); print('OK:', font.getname())"
```

## Font Search Order (in generate_news_card_v3.py)

```python
def get_font(size, bold=False):
    font_paths = [
        '/opt/data/scripts/DouyinSansBold.ttf',       # ← PERSISTENT
        '/tmp/DouyinSansBold.otf',                     # ← Legacy /tmp (backward compat)
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # ← System fallback
        # ... other CJK paths
    ]
```

## Container System Font Fallbacks

If Douyin Sans is unavailable, PIL falls back to:

| Font | Path | CJK support | Style |
|------|------|-------------|-------|
| WenQuanYi Zen Hei | `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc` | ✅ Full | Sans-serif, square |
| NotoSansCJK | Various `/usr/share/fonts/noto-cjk/` paths | ✅ Full | Sans-serif, rounder |
| DejaVuSans | System default | ❌ No | Latin only (tofu for Chinese) |

## Alternatives

- **Noto Sans CJK** (Google/Adobe): `https://github.com/googlefonts/noto-cjk` — comprehensive CJK coverage, multiple weights
- **Source Han Sans** (Adobe): Same as Noto Sans CJK, different name
- **LXGW WenKai** (霞鹜文楷): Open-source brush-script style, beautiful for Chinese text
