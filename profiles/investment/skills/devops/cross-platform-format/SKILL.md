---
name: cross-platform-format
description: >
  Cross-platform message formatting guide for Hermes Agent cron job outputs.
  Ensures reports look good and are functional across WeChat, QQ Bot, DingTalk, and Feishu.
  Also covers the Pre-Script data collection pattern to avoid cron timeout.
---

# Cross-Platform Message Formatting Guide

## Platform Capabilities Matrix

| Feature | WeChat (iLink) | QQ Bot | DingTalk | Feishu |
|---------|---------------|--------|----------|--------|
| Markdown | Partial (bold, lists) | ✅ Full | ✅ Cards/Markdown | ✅ Cards/Markdown |
| Clickable links `[text](url)` | ❌ Raw URL only | ✅ | ✅ | ✅ |
| Bold `**text**` | ✅ (⚠ 渲染为大号文字，非标准粗体) | ✅ | ✅ | ✅ |
| Lists | ✅ | ✅ | ✅ | ✅ |
| Emoji | ✅ | ✅ | ✅ | ✅ |
| Max length | ~2000 chars/msg | 4000 chars | ~20000 chars | ~20000 chars |
| Image via `![alt](url)` markdown | ❌ Stripped | ✅ Desktop only | ✅ Live adapter only | ❌ `<Image data error>` |
| Image via native attachment | ✅ `send_image_file()` | ✅ `send_image_file()` | ❌ Not supported | ✅ `send_image_file()` |

## Link Format: `[title](url)` Markdown — the preferred format (works on QQ desktop)

Use standard markdown link syntax `[标题](url)` for clickable links. This is the user's preferred format because it produces clean tables with embedded clickable links.

### Format Rules for Tables
Inside markdown tables, ensure the closing `)` is followed by **at least one space** before the `|` cell delimiter:
```
✅ | [标题](https://www.v2ex.com/t/1223821) | 分类 | 热度 |
❌ | [标题](https://www.v2ex.com/t/1223821)| 分类 | 热度 |
```

### QQ Mobile Domain Restriction (NOT a format issue)

Some domains cannot be opened when clicked on **QQ mobile** (`github.com`, `v2ex.com`, `news.ycombinator.com`). This is **NOT a markdown format issue** — the exact same `[title](url)` format works perfectly for `bilibili.com` in the same message. The restriction is at QQ mobile's built-in browser/URL handler level, not the markdown renderer.

| Format test | GitHub | Bilibili | V2EX | HN |
|-------------|:------:|:--------:|:----:|:--:|
| `[title](url)` in table | ✅ | ✅ | ❌ | ❌ |
| `[title](url)` in list | ✅ | N/A | ❌ | ❌ |
| Bare `→ url` | ❌ | ✅ | ❌ | ❌ |

**Key takeaway:** The domain itself determines whether a link opens on QQ mobile, not the format. `[title](url)` in tables is the best all-around format — it works on QQ desktop, DingTalk, Feishu, and WeChat for all domains. QQ mobile is the only platform with domain restrictions.

**QQ desktop** has no such restriction — all domains open fine.

### If QQ Mobile Link Access Is Critical
Add a separate links section at the bottom of the report:
```
📋 手机端链接导航 → https://external-link-navigation-page
```
Or note per source: `🔗 V2EX链接需手动复制到浏览器打开`

### Section Dividers
Use `━━━` (not `---`)

### Example Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 行业技术日报 · 2026-07-01
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔥 V2EX 热议

| 标题 | 分类 | 热度 |
|------|------|------|
| [好奇大家用的牙膏是什么牌子的？](https://www.v2ex.com/t/1223821) | 生活 | 165条回复 |
| [苹果电脑全线涨价](https://www.v2ex.com/t/1223840) | Apple | 118条回复 |

━━━ Hacker News 热门 ━━━

| 标题 | 分类 | 热度 |
|------|------|------|
| [Claude Sonnet 5](https://news.ycombinator.com/item?id=48736605) | AI | ↑845分 · 479条评论 |

━━━ 今日摘要 ━━━
3-5句话总结。
```

---

## Image Delivery: BOTH markdown image AND MEDIA: protocol

**DingTalk cannot receive native image attachments.** `send_image_file()` on DingTalk returns an error — the session webhook only supports text/markdown payloads. So DingTalk must get images via `![日报图片](R2_URL)` in the markdown text body.

QQ/WeChat/Feishu get native images via `MEDIA:` which the gateway processes into `send_image_file()` calls.

### The Combined Pattern

The cron agent's response must contain **both** at the end:

```
![日报图片](https://hermes-main-media.devtoy.xyz/daily-news/...png)
MEDIA:/tmp/daily-card.png
```

- **`![日报图片](R2_URL)`** — renders in DingTalk (live adapter sends as `msgtype: "markdown"`, which supports image tags). Stripped/ignored by other platforms.
- **`MEDIA:/tmp/daily-card.png`** — extracted by the cron scheduler, sent as native image attachment to QQ/WeChat/Feishu. Stripped from the text body before delivery.

**Cron prompt instruction:**
```
输出时顺序：
1. 纯文本报告
2. 在文本末尾另起一行写：![日报图片](上一步读取的R2_URL)
3. 再单独一行写：MEDIA:/tmp/daily-card.png
```

### Verification (from this session, 2026-06-24)

| Platform | MEDIA: send_image_file | ![alt](url) in markdown | Result |
|----------|----------------------|------------------------|--------|
| QQ desktop | ✅ Works | ✅ Works | Both OK |
| QQ mobile | ✅ Works | ❌ Raw markdown text | MEDIA needed |
| WeChat | ✅ Works | ❌ Stripped | MEDIA needed |
| Feishu | ✅ Works | ❌ `<Image data error>` | MEDIA needed |
| DingTalk | ❌ Returns error | ✅ Works (live adapter only) | Markdown needed |

---

## Cron Job Pre-Script Pattern (Required for Timeout-Free Operation)

**Critical: The cron job has a 180s hard timeout.** Long prompts with inline `curl` + `python3 -c` parsing blocks for 4+ data sources will reliably timeout on free-tier models (agnes-2.0-flash). Fix: use a deterministic Python `--script` that pre-collects and pre-parses all data.

### Architecture

```
[--script collect_daily_data.py] → fetches 4 sources + pre-parses to _summary.txt + generates image
    ↓ (~15s, no LLM)
[Agent prompt: 5 cat commands + format report]
    ↓ (~30s on agnes-2.0-flash)
[Hermes Gateway delivery] → text + image to all platforms
```

### Script Pattern (`~/.hermes/scripts/collect_daily_data.py`)

```python
#!/usr/bin/env python3
"""Pre-fetch and pre-parse data from 4+ sources, generate image."""
import subprocess, json, os, re, datetime, sys
DATA_DIR = '/tmp'

def fetch(url, output_file, headers=None):
    cmd = ['curl', '-sL', url, '-o', output_file]
    if headers:
        for h in headers: cmd.extend(['-H', h])
    subprocess.run(cmd, timeout=20)

# V2EX, HN, GitHub, Bilibili: fetch → parse → write _summary.txt
# Each line: field1|field2|... (agent cats these and formats as markdown)

# Image: run generate_news_card_v3.py → upload to R2 → save URL
# Also save local path /tmp/daily-card.png for MEDIA: delivery
```

### Agent Prompt (Max 15 Lines)

```
数据已由脚本预采集并生成图片到 /tmp/daily-card.png。

步骤：
1. cat /tmp/_r2_url.txt
2. cat /tmp/_v2ex_summary.txt
3. cat /tmp/_hn_summary.txt
4. cat /tmp/_gh_summary.txt
5. cat /tmp/_bili_summary.txt

然后用这些数据写一份行业技术日报。每条记录以 | 分隔：标题|链接|...。

格式要求：所有链接用 [标题](链接) 格式。

输出时顺序：
1. 纯文本报告
2. 在文本末尾另起一行写：![日报图片](上一步读取的R2_URL)
3. 再单独一行写：MEDIA:/tmp/daily-card.png
```

### Cron Job Configuration

```bash
hermes cron create "0 0 * * *" --name "行业技术日报" \
  --script collect_daily_data.py \
  --skills agent-reach,cross-platform-format \
  --deliver "weixin:...,qqbot:...,dingtalk:correct_chat_id,feishu:..." \
  --prompt "数据已由脚本预采集..."
```

---

## Platform Gateway Configuration

### Environment Variables

| Platform | Auth env vars |
|----------|-------------|
| QQ Bot | `QQ_APP_ID`, `QQ_CLIENT_SECRET` |
| Weixin (iLink) | `WEIXIN_TOKEN`, `WEIXIN_ACCOUNT_ID` |
| DingTalk | `DINGTALK_CLIENT_ID`, `DINGTALK_CLIENT_SECRET` |
| Feishu | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` |

DingTalk also uses `DINGTALK_WEBHOOK_URL` as standalone fallback (custom robot webhook).

### Plugin Registration

```yaml
plugins:
  enabled:
    - platforms/dingtalk
    - platforms/feishu
```

### Platform Toolsets

```yaml
platform_toolsets:
  weixin:
    - hermes-weixin
  dingtalk:
    - hermes-dingtalk
  feishu:
    - hermes-feishu
  qqbot:
    - hermes-qqbot
```

### Cron Deliver Format

```
weixin:account_id,qqbot:bot_token,dingtalk:chat_id,feishu:chat_id
```

**Gateway restart required** after config changes.

---

### QQ Bot Markdown 标题格式铁律（2026-07-19定稿）

| 规则 | 举例 | 原因 |
|:-----|:------|:------|
| ❌ 不用 `##` 标题 | ~~`## 大盘走势`~~ → `📈 大盘走势` | QQ渲染为超大字体 |
| ❌ 不用 `**KOL名**` 加粗 | ~~`**唐史主任**`~~ → `唐史主任` | QQ渲染为H3标题 |
| ❌ 不输出 `#话题#` 原文 | 微博的`#话题#`必须清理 | QQ解析为标题或乱码 |
| ❌ 不用 `━` `═` 长框线 | ~~`━━━━━`~~ → `• • •` 或空行 | 渲染异常 |
| ✅ 操作建议表格放最前 | 用户最关心"今天要不要操作" | 优先展示 |

**清理微博文本中markdown的方法：**
```python
text = re.sub(r"[#*_~`]", "", text)  # 去掉所有markdown符号
```

### QQ Bot Compact Push Format (投资类专用)

2026-07-15 定型的投资类操作建议推送格式。适用场景：带紧急分级的盘中/收盘推送。

### 格式模板（注意：QQ Bot不渲染 `##`和`**`，只用emoji+纯文字）

```
📅 操作建议 · MM-DD

⚠️ 止损信号
  · ⚠️ 光伏ETF跌至0.723（触及0.75止损线）！建议减仓一半。

🔴 组合偏离度
  · 🚨 科技/AI █████████████████░░░ 86.7%
  · 🟡 黄金    █░░░░░░░░░░░░░░░░░░░ 7.3%

📊 基准对比
  · 📊 沪深300: -0.20%
  · 💼 组合盈亏: -2.57%
  · ❌ 跑输大盘 2.37%

📝 数据基于盘中实时估算
```

### 设计原则

1. **紧凑4段式** — 每段≤8行，总长≤1000字符
2. **Emoji 分级** — 🚨>🔴>⚠️>🟡，一眼识别严重程度
3. **进度条** — `███████░░░` 每5%一格，共20格
4. **无表格** — 纯子弹列表，QQ Mobile渲染稳定
5. **分隔线** — `━━━━━━━━━━━━━━━━`（非markdown `---`或`___`）

### 适用平台

| 平台 | 效果 | 说明 |
|:-----|:----:|:-----|
| QQ Bot | ✅ | 最佳，emoji+分隔线渲染稳定 |
| DingTalk | ✅ | bullet列表好，进度条显示略窄 |
| Feishu | ⚠️ | 进度条需调宽（4字符空格≈1格） |
| WeChat | ⚠️ | 部分emoji不支持 |

---

## Platform-Specific Quirks

### Feishu: Code Block Line Truncation

**Problem:** Feishu's UI truncates single lines exceeding ~80 characters with `...`. When the agent echoes long terminal commands in code blocks, the displayed command is truncated and copying from Feishu also copies the truncated version. Users cannot run truncated commands.

**Fix — split long commands into multiple lines, each ≤80 chars:**

```bash
# 🚫 Bad — truncated by Feishu (single line >80 chars)
cd /opt/data/scripts && python3 collect_morning_data.py 2>&1 | grep -E "✅|⚠️"

# ✅ Good — each line fits in Feishu's viewport
cd /opt/data/scripts
python3 collect_morning_data.py 2>&1 | grep -E "✅|⚠️"
```

Rules:
- Keep each command line under **80 characters**
- Avoid `&&` chaining — use separate lines for `cd` then `python3` / `npm` / etc.
- The shell session state persists between terminal calls, so separate lines work identically
- Long flags or paths belong on their own line

### Feishu: Structured Card Components

When building cards via the Feishu Open API, use these element types:

| Element tag | Purpose | Example |
|-------------|---------|---------|
| `"tag": "markdown"` | Rich text with GFM tables, bold, links | Main body content |
| `"tag": "hr"` | Horizontal divider | Separate sections within a card |
| `"tag": "note"` | Small gray footnote | `{"elements": [{"tag": "plain_text", "content": "..."}]}` |
| `"tag": "column_set"` | Multi-column layout | Side-by-side content (rarely needed for investment cards) |
| `"tag": "table"` | Native table component (V7.4+) | Structured data, max 5 per card, supports pagination |

Structured card pattern (used in `send_morning_cards.py`):
```python
elements = [
    {"tag": "markdown", "content": main_section},
    {"tag": "hr"},
    {"tag": "markdown", "content": detail_section},
    {"tag": "note", "elements": [{"tag": "plain_text", "content": "footnote"}]},
]
```

### DingTalk: Session Webhook Primer

**Critical:** DingTalk Stream Mode bots record `session_webhook` **only when someone @mentions them or sends a message in the group**. After every gateway restart, the `_session_webhooks` dict is empty. To re-prime:

1. **User must send a message in the target DingTalk group** — any message, @mention not strictly required
2. Gateway log will show: `inbound message: platform=dingtalk user=... chat=CID_STRING msg='...'`
3. The `CID_STRING` is the **correct chat_id** for the cron `deliver` field
4. Once recorded, cron delivery uses the live adapter (`msgtype: "markdown"`) for texts

**chat_id verification:** The chat_id in `deliver` must match the `chat=...` value in gateway logs. A mismatched chat_id (e.g., copied from another source) causes silent failures. Always extract the chat_id from gateway log after a group interaction.

**Standalone fallback:** When no session_webhook exists, the standalone path uses `DINGTALK_WEBHOOK_URL` (custom robot webhook). This sends as `msgtype: "text"` (no markdown image rendering) and ignores the chat_id (always goes to the webhook's group).

**Docker note:** In Docker, `~/.hermes` on the host may be mapped to `/opt/data` in the container. Adjust paths accordingly.

### WeChat (iLink): Rate Limits

- ~1 msg/sec. `-2` error on rate limit
- Gateway auto-backoffs, but rate limits cascade if multiple cron runs fire close together
- **Avoid test runs with `1m` schedule** — triggers rate limits. Use daily schedule for real use

### File-Mutation Verifier Warning Leakage

The verifier appends `⚠️ File-mutation verifier:` to the agent's output when `write_file` is attempted on protected paths. This leaks into delivered messages.

**Solutions (preferred first):**
1. **Pre-Script pattern** — use `--script` parameter for all data collection. Script filesystem writes bypass the verifier. Agent only does `cat` reads.
2. **Prompt instruction** — add to the prompt: "绝对不要使用 write_file 工具创建 .py 或 .sh 文件。临时数据用 curl -o /tmp/file 写入，再用 python3 -c 读取。"

---

## Image Generation (v3 — All 4 Sources, Dynamic Layout)

**Use `/opt/data/generate_news_card_v3.py` (NOT v2 — only shows 2 sections, NOT v1 — garbled Chinese text).**

v3 generates a compact card with all 4 data sources + summary:
- **Canvas**: 1080px wide, dynamic height (typically ~1683px vs old 1200×2400 with wasted space)
- **Margins**: 30px (vs 50px in v2)
- **Font**: Items 24px (vs 22px), section headers 30px
- **Capacity**: 8 items/section (vs 5 in v2)
- **Sections**: V2EX + HN + GitHub + Bilibili + 今日摘要 (vs V2EX + GitHub only)
- **Output path**: `/tmp/daily-card.png` (same default as v2 for backward compat with MEDIA: delivery)

```bash
/opt/hermes/.venv/bin/python3 /opt/data/generate_news_card_v3.py \
  --date=YYYY-MM-DD \
  --v2ex "标题1" "标题2" ... --hn "标题1" ... \
  --github "repo1 — ⭐N" ... --bilibili "标题1" ... \
  --summary "摘要1" "摘要2" ... --upload
```

The `--upload` flag uploads to R2 and prints `URL=<r2_url>`. The local file at `/tmp/daily-card.png` is used for MEDIA: delivery.

### Pre-Script Integration (collect_daily_data.py)

The cron `--script` must pass ALL data sources to v3:

```python
cmd = ['/opt/hermes/.venv/bin/python3', '/opt/data/generate_news_card_v3.py',
       '--date=' + today,
       '--v2ex'] + v2ex_titles + ['--hn'] + hn_titles + \
       ['--github'] + gh_names + ['--bilibili'] + bili_titles
if summaries:
    cmd += ['--summary'] + summaries
cmd += ['--upload']
```

### Pitfalls: `nargs='+'` + empty list eats next flag

**`argparse` with `nargs='+'` requires at least one value.** If a flag like `--bilibili` is followed by an empty list, argparse consumes the next flag (`--summary`, `--upload`) as its value, causing parse errors and silent image-generation failure.

**Fix:** Only add section flags when data exists:

```python
cmd = ['v3.py', '--date=...', '--v2ex'] + v2ex_titles
if hn_titles:      cmd += ['--hn'] + hn_titles
if gh_names:       cmd += ['--github'] + gh_names
if bili_titles:    cmd += ['--bilibili'] + bili_titles
if summaries:      cmd += ['--summary'] + summaries
cmd += ['--upload']
```

### Pitfalls: Two script copies in Docker

In Docker, the volume mount (`~/.hermes-main:/opt/data`) creates `/opt/data/` on the container filesystem. Hermes cron resolves `--script` relative to `~/.hermes/scripts/`, which lives under `/opt/data/home/.hermes/scripts/`. If you manually test from `/opt/data/`, `python3 scripts/collect_daily_data.py` picks up `/opt/data/scripts/` (the docker-mount copy), not the cron one. **Always test from `~/.hermes/scripts/`** or verify which copy you're editing.

### Content Consistency
- Image must match text report exactly — never use placeholder/sample data
- Pass ALL sections to the script (do NOT skip even if data is sparse)
- Verify with `vision_analyze` before sending

---

## References
- `references/api-endpoints.md` — Reliable endpoints, fields, link formats for each data source.
- `references/cron-delivery-internals.md` — MEDIA protocol lifecycle, DingTalk session_webhook internals, delivery debugging.
