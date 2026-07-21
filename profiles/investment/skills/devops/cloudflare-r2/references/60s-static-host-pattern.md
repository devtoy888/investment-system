# 60s-static-host Image Brief Pattern

## Project Overview
GitHub: https://github.com/vikiboss/60s-static-host
Automated Chinese news aggregation service that generates daily news cards as PNG images.

### Architecture
1. **Fetch**: Scrapes WeChat public accounts for daily news articles
2. **Parse**: Uses Gemini LLM to extract news items, cover image, daily tip
3. **Render**: React + Puppeteer renders HTML card → PNG screenshot
4. **Store**: Saves JSON + PNG to GitHub repo, served via CDN

### Tech Stack
- Runtime: Bun (TypeScript)
- Rendering: React Server Components + Puppeteer
- Styling: UnoCSS (runtime Tailwind)
- Compression: Sharp (PNG optimization)
- CI: GitHub Actions (cron every 10 min during 00:00-10:00 Beijing time)

### Key Files
- `src/update-60s.tsx` — Main orchestrator
- `src/services/parser.ts` — Gemini LLM HTML parser (extracts news, cover, tip)
- `src/services/renderer.tsx` — Puppeteer screenshot renderer
- `src/components/news.tsx` — React card component (TailwindCSS styled)
- `src/services/storage.ts` — JSON + PNG file management

### Card Layout (news.tsx)
- Size: 1200×2400px, 2x DPR
- Background: Stone/amber gradient
- Sections: Header (date/lunar/day) → News list (numbered) → Tip → Footer
- Font: DouyinSansBold (custom CJK font)

### CDN URLs
- JSON: `https://cdn.jsdmirror.com/gh/vikiboss/60s-static-host@main/static/60s/{date}.json`
- PNG: `https://cdn.jsdmirror.com/gh/vikiboss/60s-static-host@main/static/images/{date}.png`

### Lessons for Hermes Implementation
1. **Puppeteer rendering requires Chromium** — heavy dependency for cron jobs
2. **Alternative**: Use AI image generation (Agnes) or Playwright for lighter rendering
3. **Key insight**: The React component approach (HTML→screenshot) is the cleanest way to generate consistent branded cards
4. **Font handling**: CJK fonts need explicit configuration in headless browsers
