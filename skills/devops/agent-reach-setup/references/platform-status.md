# Agent Reach Platform Status Reference

## Working Platforms (Verified 2026-06-23)

### GitHub (gh CLI)
- **Binary**: Real CLI from GitHub releases (NOT `uv tool install gh` which gives broken v0.0.4 wrapper)
- **Auth**: `echo "ghp_XXX" | gh auth login --with-token`
- **Token storage**: `~/.config/gh/hosts.yml`
- **Capabilities**: repo search, issues, PRs, code browsing, user info

### V2EX
- **Method**: Public REST API (`https://www.v2ex.com/api/topics/hot.json`)
- **Auth**: None needed
- **Capabilities**: hot topics, node browsing, topic details, user info

### 雪球 (Xueqiu)
- **Auth**: Cookie `xq_a_token=RAW_HEX_VALUE` in `~/.agent-reach/config.yaml`
- **Format**: `xq_a_token=bf314c69991389db874f6a94089112bfe67ade27` (no S prefix)
- **Capabilities**: stock quotes, search, hot posts, hot stocks
- **Endpoints**: `stock.xueqiu.com/v5/stock/batch/quote.json`, `xueqiu.com/v4/statuses/public_timeline_by_category.json`

### Exa 全网搜索
- **Method**: MCP server via mcporter (`mcporter config add exa https://mcp.exa.ai/mcp`)
- **Auth**: Free tier, no API key needed
- **mcporter call syntax**: `mcporter call exa.web_search_exa query: "term" numResults: 3`
- **Capabilities**: semantic web search, web content extraction

### B站 (Bilibili)
- **Method**: `bili-cli` (installed via `uv tool install bilibili-cli`, binary is `bili`)
- **Auth**: None needed for search; OpenCLI needed for subtitles
- **Note**: Upstream stopped updating 2026-03

### YouTube
- **Method**: `yt-dlp` (installed via `uv tool install yt-dlp`)
- **Capabilities**: video info, subtitle extraction, audio transcription (via Groq)

### 小红书 (XiaoHongShu)
- **Method**: `xiaohongshu-mcp` + mcporter
- **Server**: Port 18060, ARM64 binary from GitHub releases
- **Login**: QR code scan (first time only)
- **mcporter register**: `mcporter config add xiaohongshu http://localhost:18060/mcp`
- **mcporter call syntax**: `mcporter call xiaohongshu.search_feeds keyword: "term"`
- **Limitation**: Requires Chromium browser (go-rod). FAILS on headless ARM64 servers — cannot download Chromium binary.

### 小宇宙 (Xiaoyuzhou)
- **Method**: `transcribe.sh` script + Groq Whisper
- **Auth**: `agent-reach configure groq-key gsk_XXX`
- **Capabilities**: podcast download + audio transcription
- **Limitation**: Website is Next.js SPA; static regex extraction fails on episode pages. Works with direct .m4a/.mp3 files.

## mcporter Call Syntax (Important!)
- **Format**: `mcporter call server.tool_name param: "value" param2: 3`
- **NOT JSON**: Passing JSON body like `'{"query": "..."}'` causes double-encoding and validation errors
- **Example**: `mcporter call exa.web_search_exa query: "AI agent" numResults: 3`

## Headless Server Limitations
| Platform | Requirement | Headless Compatible? |
|----------|-------------|---------------------|
| 小红书 | Chromium browser (go-rod) | ❌ No |
| LinkedIn | Desktop browser scraping | ❌ No |
| Twitter | API key (X Premium) | ⚠️ Partial (search only) |
| Reddit | Login cookie | ⚠️ Yes (with cookie) |
| GitHub | gh CLI | ✅ Yes |
| V2EX | Public API | ✅ Yes |
| 雪球 | Cookie | ✅ Yes |
| Exa | MCP server | ✅ Yes |
| B站 | bili-cli | ✅ Yes |
| YouTube | yt-dlp | ✅ Yes |
| 小宇宙 | Script + Groq | ✅ Yes |
