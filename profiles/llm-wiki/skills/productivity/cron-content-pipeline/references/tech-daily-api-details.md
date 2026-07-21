# Tech Daily API Details

Session-verified API configurations for the tech daily newsletter pipeline. Each API was actually exercised on 2026-06-21.

## V2EX Hot Topics

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```
Returns: JSON array of topic objects. Key fields: `title`, `node.title`, `replies`.
No auth required. Reliable.

## Hacker News (via Jina Reader)

```bash
curl -s "https://r.jina.ai/https://news.ycombinator.com/" -H "User-Agent: agent-reach/1.0"
```
Returns: Markdown-converted page. Each entry has pattern: `[Title](url) (domain) N points by user [N hours ago] | [N comments]`
Parse with regex or Python. Jina rate-limits but works reliably for single pages.

## GitHub Trending

**Primary (reliable):** GitHub Search API
```bash
curl -s "https://api.github.com/search/repositories?q=created:>$(date -d '7 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=5" \
  -H "User-Agent: agent-reach/1.0" -H "Accept: application/vnd.github+json"
```
Returns: full search result. Key fields: `items[].full_name`, `description`, `stargazers_count`, `language`.
Uses: 60 req/hr unauthed. Fine for daily cron.

**Fallback (may return empty):**
```bash
curl -s "https://github-trending-api.vercel.app/repositories?since=daily"
```
On 2026-06-21 this returned an empty file. Do NOT rely on it as primary source.

## Bilibili

**Important:** ALL Bilibili endpoints require browser-like headers:
```bash
-H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
-H "Referer: https://www.bilibili.com/"
```

**General popular (works with headers):**
```bash
curl -s "https://api.bilibili.com/x/web-interface/popular" [headers]
```
Returns: JSON with `data.list[]`. Each video has `title`, `owner.name`, `stat.view`, `stat.like`, `tid`, `tname`.
⚠️ The general popular list is dominated by entertainment/lifestyle — NOT tech.

**Popular series (may fail with -352):**
```bash
curl -s "https://api.bilibili.com/x/web-interface/popular/series/one?number=1" [headers]
```
Returns code -352 → try `/popular` instead.

**Tech-specific search (use this for tech content):**
```bash
curl -s "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=AI%20%E7%A7%91%E6%8A%80%20%E7%BC%96%E7%A8%8B&order=click&tids=201" [headers]
```
- `tids=201` = 科技区 category ID
- `order=click` = sort by popularity
- Returns: `data.result[]` with `title` (has `<em>` highlight tags to strip), `author`, `play`, `like`, `description`
