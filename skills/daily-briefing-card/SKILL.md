---
name: daily-briefing-card
description: "Generate programmatic daily news briefing card images using Pillow + Cloudflare R2. v3 — 1080px dynamic-height layout, 4 sections + summary, Douyin Sans Bold font, all data sources."
version: 1.1.0
author: Hermes Agent
platforms: [linux]
tags: [daily-briefing, image-generation, news-card, cloudflare-r2, chinese-font]
triggers:
  - 日报图片/每日简报图片/daily briefing card/news card image generation
  - 图片生成/行业技术日报图片
  - 中文图片字体/chinese font rendering in PIL
  - douyin sans font installation
  - generate_news_card_v3
---

# Daily Briefing Card Generator (v3)

Generate high-quality PNG briefing cards from structured news data using Pillow. v3 layout: 1080px wide, dynamic height, 4 data sections + summary, Douyin Sans Bold font.

## v2 → v3 Migration

| Aspect | v2 (deprecated) | v3 (current) |
|--------|----------------|--------------|
| Width | 1200px fixed | 1080px |
| Height | 2400px fixed | Dynamic (auto-calculated, ~800-1700px) |
| Margin | 50px | 30px |
| Items/section | 5 | 8 |
| Sections | V2EX + GitHub only | V2EX, HN, GitHub, Bilibili + Summary |
| Font size | 22px items | 24px items, 30px headers, 44px title |
| File | `generate_news_card_v2.py` | `generate_news_card_v3.py` |
| R2 suffix | `_briefing_v2.png` | `_briefing_v3.png` |
| Background | Beige (252,248,235) | Same warm beige |
| Section colors | Same 4-source palette | Same |

## Files

- **Generator (v3)**: `/opt/data/generate_news_card_v3.py`
- **Generator (v2, deprecated)**: `/opt/data/generate_news_card_v2.py`
- **Uploader**: `/opt/data/r2_uploader.py` (S3-compatible Cloudflare R2 uploader)
- **Font**: `/opt/data/scripts/DouyinSansBold.ttf` (Douyin Sans Bold, TTF, persistent storage)
- **Pre-script**: `/opt/data/scripts/collect_daily_data.py` (cron pre-collection — calls v3)

## Font: Douyin Sans Bold

### Installation

Download from ByteDance's official open-source repository:

```bash
curl -sL -o /opt/data/scripts/DouyinSansBold.ttf \
  https://raw.githubusercontent.com/bytedance/fonts/main/DouyinSans/DouyinSansBold.ttf
```

- **Format**: TTF — the file `DouyinSansBold.otf` does NOT exist in the official repo
- **Persistent location**: `/opt/data/scripts/DouyinSansBold.ttf` (Docker volume mount, survives restarts)
- **Never put in /tmp**: `/tmp` is cleared on container restart. Font loss causes silent fallback to wqy-zenhei (system Chinese font) — image still generates, just with different typography
- **License**: SIL Open Font License 1.1 (free for commercial use)
- **Official repo**: https://github.com/bytedance/fonts/tree/main/DouyinSans

### Font Search Order (in get_font())

The `get_font()` function in `generate_news_card_v3.py` tries paths in order:

```
1. /opt/data/scripts/DouyinSansBold.ttf    ← PERSISTENT (preferred)
2. /tmp/DouyinSansBold.otf                  ← Legacy /tmp (backward compat, may be stale)
3. /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc  ← System WenQuanYi (fallback)
4. ... other system CJK paths
5. DejaVuSans.ttf (no CJK support)
6. PIL default bitmap font (tofu symbols for Chinese)
```

The function silently falls through if a path is missing — no error is raised. Verify with `vision_analyze` that Chinese text renders correctly.

## Layout (v3)

| Property | Value |
|----------|-------|
| Width | 1080px |
| Height | Dynamic (auto-calculated) |
| Margins | 30px |
| Line height | 28px |
| Items/section | 8 |
| Sections | V2EX (red), HN (orange), GitHub (green), Bilibili (blue), Summary (purple) |
| Background | Warm beige (252, 248, 240) |
| Footer | "数据来源: ... · Powered by Hermes Agent" |

## Usage

```bash
/opt/hermes/.venv/bin/python3 /opt/data/generate_news_card_v3.py \
  --date=YYYY-MM-DD \
  --time=0800 \
  --v2ex "标题1" "标题2" ... \
  --hn "Title 1" "Title 2" ... \
  --github "repo/name — ⭐N" ... \
  --bilibili "标题1" "标题2" ... \
  --summary "摘要1" "摘要2" ... \
  --output /tmp/daily-card.png \
  --upload
```

- `--upload` → uploads to R2, prints `URL=<r2_url>` and `URL=<public_url>`
- Local file at `/tmp/daily-card.png` is used for MEDIA: delivery in cron jobs

### Pre-Script Integration (in collect_daily_data.py)

```python
cmd = ['/opt/hermes/.venv/bin/python3', '/opt/data/generate_news_card_v3.py',
       '--date=' + today, '--v2ex'] + v2ex_titles
if hn_titles:      cmd += ['--hn'] + hn_titles
if gh_names:       cmd += ['--github'] + gh_names
if bili_titles:    cmd += ['--bilibili'] + bili_titles
if summaries:      cmd += ['--summary'] + summaries
cmd += ['--upload']
```

Only add section flags where data exists (see Pitfalls below).

### R2 Upload Path

```
daily-news/YYYY-MM/YYYY-MM-DD_briefing_v3.png
```

## Pitfalls

### 1. `argparse nargs='+'` with empty list eats next flag

**Critical.** `argparse` with `nargs='+'` requires at least one value. If a flag like `--bilibili` is followed by an empty list, argparse consumes the **next flag** (`--summary`, `--upload`) as its value, causing parse errors.

**Fix:** Guard each section flag with an existence check (see Pre-Script Integration above).

**Diagnostic:** Check the script's stderr output — it prints `Image generation skipped: <error>` when this happens. The image is NOT generated; the script silently continues.

### 2. Container restart loses /tmp font

The font at `/tmp/DouyinSansBold.otf` (or any `/tmp/*`) is ephemeral in Docker. On restart, the font is gone and `get_font()` falls back to wqy-zenhei. The image still generates with no errors — the only symptom is different typography.

**Fix:** Keep the font at `/opt/data/scripts/DouyinSansBold.ttf` (persistent Docker volume) and prioritize it in `font_paths`.

### 3. Two script copies in Docker volume

In Docker, `~/.hermes-main` on the host maps to `/opt/data` in the container. Hermes cron resolves `--script` relative to `~/.hermes/scripts/` (`/opt/data/home/.hermes/scripts/`). Manual testing from `/opt/data/` runs `/opt/data/scripts/collect_daily_data.py`. These are **two different copies** if not symlinked. Always make changes in BOTH.

The `~/.hermes/scripts/` dir is typically a symlink → `../scripts/` (which resolves to `/opt/data/scripts/`). Verify with `readlink -f` before editing.

### 4. R2 upload requires `region_name='auto'`

Cloudflare R2 uses a non-AWS endpoint. Setting `region_name='auto'` is required:
```python
client = boto3.client('s3',
    endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='auto'
)
```

### 5. Content consistency with text report

The image brief must contain the same data as the text report. Never use placeholder or sample data. Pass ALL 4 sources + summary to v3. Verify with `vision_analyze` before delivery.

## References

- `references/douyin-font-setup.md` — Font download, format verification, and persistent storage.
