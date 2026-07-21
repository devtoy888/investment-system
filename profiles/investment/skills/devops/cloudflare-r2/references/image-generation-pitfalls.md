# Image Generation Pitfalls for Daily Reports

## generate_briefing.py vs generate_news_card.py

| Aspect | generate_briefing.py (OLD) | generate_news_card.py (NEW) |
|--------|---------------------------|----------------------------|
| Data input | `--news` array (flat) | `--v2ex/--hn/--github/--bilibili/--summary` (structured) |
| Content match | Hardcoded sample data | Matches actual report sections |
| Sources footer | "央视新闻·新华社·人民日报" (wrong!) | "V2EX · Hacker News · GitHub · Bilibili" (correct) |
| Section rendering | Single list, no categorization | Colored section headers per source |
| Status | **DO NOT USE** | ✅ Use for daily reports |

## Key Lesson (2026-06-23)

When generating images from cron job data:
1. **Never use placeholder/sample data** — the image content must match the actual report
2. **Never hardcode sources** — use the actual data sources (V2EX, HN, GitHub, Bilibili)
3. **Preserve section structure** — each section (V2EX, HN, GitHub, Bilibili, Summary) should be visually distinct
4. **User will verify** — if image content doesn't match text report, it's a failure

## Cloudflare 60s-static-host Pattern

The [60s-static-host](https://github.com/vikiboss/60s-static-host) repo uses Puppeteer + React to render HTML then screenshot. Our Pillow approach is simpler and sufficient for text-based cards. Puppeteer approach only needed if HTML/CSS styling is required.
