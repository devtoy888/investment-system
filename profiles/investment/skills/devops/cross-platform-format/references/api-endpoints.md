# Data Source API Reference

Reliable endpoints and parsing snippets for the industry tech daily report cron job.

## V2EX

**Endpoint:** `GET https://www.v2ex.com/api/topics/hot.json`
**Headers:** `User-Agent: agent-reach/1.0`
**Response:** Array of topic objects. Fields: `title`, `replies`, `node.title`, `id`
**Link format:** `https://www.v2ex.com/t/{id}`
**Note:** Returns 9-10 items (varies by time of day).

## Hacker News

**Endpoint:** `GET https://news.ycombinator.com/`
**Headers:** `User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36`
**Fallback (firebase API):** `GET https://hacker-news.firebaseio.com/v0/topstories.json`
**Link format:** `https://news.ycombinator.com/item?id={id}`

**IMPORTANT — `r.jina.ai` approach is unreliable for HN:**
`r.jina.ai/https://news.ycombinator.com/` often returns rendered/minified content with no parseable HTML structure (IDs, scores, comments all stripped). Always use direct curl to HN.com instead.

**Direct HTML extraction (Python, proven working):**
```python
import re
content = open('/tmp/_hn_raw.html').read()
ids = re.findall(r'class="athing submission" id="(\d+)"', content)
for idx, mid in enumerate(ids[:10]):
    tit_pat = rf'id="{mid}".*?<span class="titleline"><a[^>]*>([^<]+)</a>'
    tm = re.search(tit_pat, content, re.DOTALL)
    title = tm.group(1).strip().replace('&#x27;',"'").replace('&amp;','&').replace('&quot;','"')
    sc = re.search(rf'score_{mid}">(\d+)', content)
    score = sc.group(1) if sc else '?'
    cm = re.search(rf'item\?id={mid}">(\d+)&nbsp;comments?', content)
    comments = cm.group(1) if cm else 'discuss'
    link = f'https://news.ycombinator.com/item?id={mid}'
```
**Note on extraction:**
- IDs appear in double-quotes: `id="48653216"` (not single quotes)
- Comment counts use `&nbsp;` between number and word, not spaces
- Items with 0 comments or "discuss" status have no comment count span at all
- Scores are inside `<span class="score" id="score_{mid}">NNN points`

## GitHub Trending

**Endpoint:** `GET https://api.github.com/search/repositories?q=created:>{7-days-ago}&sort=stars&order=desc&per_page=10`
**Headers:** `Accept: application/vnd.github+json`
**Fields:** `full_name`, `html_url`, `stargazers_count`, `language`, `description`
**Link format:** `{html_url}`
**Dedup:** Check `full_name` to avoid duplicates.

## B站 (Bilibili)

**Endpoint:** `GET https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all`
**Headers:** `User-Agent: agent-reach/1.0`, `Referer: https://www.bilibili.com`
**Fields:** `title`, `owner.name`, `stat.view`, `bvid`, `short_link_v2`
**Link format:** `{short_link_v2}` (prefer) or `https://www.bilibili.com/video/{bvid}`
**⚠️ CRITICAL:** `bvid` field from API ALREADY includes "BV" prefix (e.g. `BV1rz7569EWw`). Do NOT prepend another "BV" in your code. `BVBV1rz7569EWw` → broken URL.
**Note:** This API returns ALL categories mixed. Filter for tech content manually.
**Alternative:** `GET https://api.bilibili.com/x/web-interface/popular?ps=5&pn=1` — more curated but still mixed.