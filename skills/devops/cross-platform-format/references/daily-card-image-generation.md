# Daily News Card Image Generation (v3)

## Architecture

```
collect_daily_data.py (cron --script)
  ↓ fetches V2EX, HN, GitHub, Bilibili → pre-parses → /tmp/_*_summary.txt
  ↓ calls generate_news_card_v3.py with --v2ex --hn --github --bilibili --summary --upload
  ↓ v3.py outputs /tmp/daily-card.png + uploads to R2 + prints URL=<R2_URL>
  ↓ script writes R2_URL to /tmp/_r2_url.txt
  ─── agent runs with short prompt ───
  ↓ agent cats /tmp/_*_summary.txt → formats report
  ↓ agent outputs ![日报图片](R2_URL) + MEDIA:/tmp/daily-card.png
  ─── gateway delivers ───
  ↓ QQ: MEDIA → send_image_file
  ↓ Weixin: MEDIA → send_image_file
  ↓ Feishu: MEDIA → send_image_file
  ↓ DingTalk: ![alt](url) in msgtype:markdown
```

## v3 Layout Specs

- Canvas: 1080px wide, dynamic height (estimated via estimate_height())
- Background: (252, 248, 240) warm cream
- Left margin: 30px
- Title font: 44px bold
- Section header: 30px bold, colored accent bar (80px wide, 3px)
- Item number badge: 14px in 18px circle
- Item text: 24px, line height 28px
- Item gap: 4px
- Section gap: 12px divider + 18px spacing
- Footer: 18px gray

## v3 vs v2 vs v1

| Feature | v1 (deprecated) | v2 (deprecated) | v3 (current) |
|---------|----------------|----------------|--------------|
| Font | No Douyin Sans Bold, garbled CJK | Douyin Sans Bold | Douyin Sans Bold |
| Canvas | 1200x2400 | 1200x2400 | 1080xdynamic |
| Sections | V2EX only | V2EX + GitHub | V2EX + HN + GitHub + Bilibili + Summary |
| Items/section | 5 | 5 | up to 8 |
| Summary | No | No | Yes auto-generated |
| Margins | 50px | 50px | 30px |
| Font (items) | 18px | 22px | 24px |
| R2 key suffix | _briefing.png | _briefing_v2.png | _briefing_v3.png |

## Cron Prompt for the Agent

Maximum 15 lines. Agent just cats pre-parsed summaries and formats.

## argpase nargs='+' Pitfall

argparse.add_argument('--bilibili', nargs='+', action='append') -- nargs='+' requires at least 1 value. When the list is empty, argparse consumes the next flag as a title.

Always guard:
```python
if bili_titles:
    cmd += ['--bilibili'] + bili_titles
```

## Bilibili API Error Values

- {"code":-352,"message":"-352"} -- rate limited or region issue
- These produce empty bili_titles; the guard handles gracefully.
