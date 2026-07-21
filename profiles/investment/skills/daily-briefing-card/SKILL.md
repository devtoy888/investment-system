---
name: daily-briefing-card
description: "Generate programmatic daily news briefing card images using Pillow + Cloudflare R2. Supports V2EX, HN, GitHub, Bilibili sections with lunar calendar, Douyin Sans font, and structured layout."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [daily-briefing, image-generation, news-card, cloudflare-r2]
---

# Daily Briefing Card Generator

Generate high-quality PNG briefing cards from structured news data, inspired by the [60s-static-host](https://github.com/vikiboss/60s-static-host) design aesthetic.

## When to Use

Trigger this skill when the user asks to generate a daily briefing card, news summary image, or visual daily digest. Also trigger when integrating image output into cron-based daily reports.

## Files

- **Script**: `scripts/generate_news_card_v2.py` — Main generator script
- **Uploader**: `scripts/r2_uploader.py` — Cloudflare R2 S3-compatible uploader
- **Font**: `assets/DouyinSansBold.otf` — Douyin Sans Bold font (2MB, from 60s-static-host repo)

## Prerequisites

1. **Douyin Sans Bold font**: Download from `https://raw.githubusercontent.com/vikiboss/60s-static-host/main/assets/DouyinSansBold.otf` to `assets/DouyinSansBold.otf`
2. **Cloudflare R2 credentials**: Account ID, bucket name, access key, secret key, public URL
3. **Pillow**: `uv pip install Pillow`

## Usage

```bash
python3 scripts/generate_news_card_v2.py \
  --date=YYYY-MM-DD \
  --time="HH:MM 北京时间" \
  --v2ex "标题1" "标题2" ... \
  --hn "Title 1" "Title 2" ... \
  --github "repo/name ⭐stars Language Description" ... \
  --bilibili "标题1" "标题2" ... \
  --summary "摘要1" "摘要2" ... \
  --tip "每日一句" \
  --output /tmp/card.png \
  --upload
```

## Layout

- **Size**: 1200×2400px (portrait, 1:2 ratio)
- **Header**: Centered title "📰 每日简报", date with weekday, time label, lunar date
- **Sections**: V2EX (red), HN (orange), GitHub (green), Bilibili (blue), Summary (purple)
- **Divider**: Decorative lines with amber diamond at center
- **Footer**: Source attribution + "Powered by Hermes Agent"

## Pitfalls

1. **Chinese character rendering**: Must use Douyin Sans Bold font. System fallback fonts often render Chinese as blank squares (tofu). Always verify font file exists before generating.
2. **Bottom overlap**: Content y-coordinate can exceed image height with many items. Always clamp `y` before drawing footer: `if y > height - 150: y = height - 150`.
3. **Footer positioning**: Use `min(height - 120, y + 80)` for footer_y to ensure spacing.
4. **Image cleanup**: Script deletes output file after upload by default. Comment out cleanup during debugging.
5. **R2 upload**: Use S3-compatible endpoint, set `region_name='auto'` for Cloudflare R2.
6. **Section spacing**: Each section separator line draws across full width (1101 pixels at 1200px width) — this is EXPECTED, not an overlap bug.
7. **Lunar calendar**: Built-in 1900-2099 lookup table. No external dependency needed.

## R2 Configuration

```python
uploader = R2Uploader(
    account_id='YOUR_ACCOUNT_ID',
    bucket_name='YOUR_BUCKET',
    access_key_id='YOUR_ACCESS_KEY',
    secret_access_key='YOUR_SECRET_KEY',
    public_url='https://YOUR_DOMAIN'
)
```

Upload path: `daily-news/YYYY-MM/month/DATE_briefing_v2.png`

## Design Reference

Based on [60s-static-host](https://github.com/vikiboss/60s-static-host):
- Font: Douyin Sans Bold
- Colors: Stone/amber palette (warm beige background)
- Layout: Clean section separation with colored accents
- Lunar calendar integration
