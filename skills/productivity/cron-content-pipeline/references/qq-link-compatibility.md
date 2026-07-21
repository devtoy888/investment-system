# QQ Platform Link Compatibility

Discovered during a cron content pipeline debugging session (July 1, 2026). The daily tech report had links that worked on some domains but not others, regardless of format.

## Tested Formats (all failed identically for restricted domains)

| Format | Example | GitHub | Bilibili | V2EX | HN |
|--------|---------|:------:|:--------:|:----:|:--:|
| Markdown table `[title](url)` | `\| [text](url) \| cat \|` | ✅ | ✅ | ❌ | ❌ |
| Numbered list `[title](url)` | `1. [text](url)` | ✅ | ✅ | ❌ | ❌ |
| Bare URL `→ url` | `→ https://...` | ✅ | ✅ | ❌ | ❌ |

## Conclusion

The issue is **domain-level, not format-level**. QQ's built-in browser or URL handler applies domain restrictions. Same format, same message structure — only certain domains pass through.

## Affected Domains

| Domain | Works? | Notes |
|--------|:------:|-------|
| `github.com` | ✅ | Foreign, developer-focused |
| `www.bilibili.com` | ✅ | Chinese video platform |
| `www.v2ex.com` | ❌ | Chinese tech forum |
| `news.ycombinator.com` | ❌ | Foreign, has `?id=` query param |

## Workarounds

- Accept the limitation: add a note like "🔗 V2EX链接需浏览器手动打开"
- Use URL shorteners for affected domains
- Replace sources: e.g. use a Chinese proxy/aggregator instead of V2EX
- Summarize content inline without clickable links
