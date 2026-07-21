# Case Study: Agent-Reach 行业技术日报

Concrete example built in a real session — 4-source daily tech briefing pushed to Weixin/Feishu/QQ/DingTalk.

## Setup Steps

### 1. Install Agent-Reach

```bash
# On a server without pipx/sudo:
uv tool install "https://github.com/Panniantong/agent-reach/archive/main.zip"
export PATH="/opt/data/home/.local/bin:$PATH"
agent-reach install --env=auto
agent-reach doctor            # Verify — expect 4/13 channels active by default
```

### 2. Create the cron job

```bash
hermes cron create "0 0 * * *" \
  --name "行业技术日报" \
  --prompt "..." \
  --skills agent-reach \
  --deliver all
```
## Key Parameters

- `0 0 * * *` = daily at 08:00 CST (UTC+8)
- `--skills agent-reach` loads the Agent-Reach skill  
- **AVOID `--deliver all`**: it only reaches home channels (typically just WeChat). Use explicit platform:chat_id delivery instead: `--deliver "weixin:CHAT_ID,qqbot:CHAT_ID,dingtalk:CHAT_ID"`

## Finding Chat IDs for All Platforms

```bash
# Extract all inbound chats from gateway logs
grep "inbound message:" /opt/data/logs/gateway.log | grep -oP "platform=\S+ chat=\S+" | sort -u
```

Feishu: user must send at least one message to the bot first, otherwise no chat ID exists.
DingTalk: standalone delivery requires a webhook URL (Client ID+Secret mode only supports replies)。

## Gemini 429 Rate Limit During Testing

The free Gemini 2.0 Flash quota is 1500 req/day / 30 req/min. During initial cron setup with multiple test runs, it's easy to exhaust this quota. The cron job's `deliver: "all"` only goes to home channels — explicit platform:chat_id required.

## Delivery Troubleshooting

After `hermes cron run <id>`, check:
```bash
grep "delivered to\|delivery error" /opt/data/logs/agent.log | tail -10
```
Each platform should appear as a separate line. Missing lines = configuration problem.

Common issues:
- **DingTalk**: "No valid session_webhook" → needs standalone webhook URL
- **Feishu**: Only "delivered to weixin" appears → chat ID not captured
- **QQBot**: Works with explicit chat_id in delivery list

### 3. Test immediately

```bash
hermes cron run <job_id>
hermes cron list              # Check last_status after a few seconds
```

## Data Sources Used

| Source | Endpoint | Extracted fields |
|--------|----------|-----------------|
| V2EX 热门 | `https://www.v2ex.com/api/topics/hot.json` | title, node, replies |
| Hacker News | `https://r.jina.ai/https://news.ycombinator.com/` | title, score, comments |
| GitHub Trending | `https://api.github.com/search/repositories?q=created:>...&sort=stars` | name, description, stars, language |
| GitHub Trending (fallback) | `https://github-trending-api.vercel.app/repositories?since=daily` | name, description, stars |
| B站热门 | `https://api.bilibili.com/x/web-interface/popular/series/one?number=1` | title, play count, uploader |

## Report Format

```
━━━ 行业技术日报 ━━━
📅 [日期]（[星期]）

━━━ V2EX 热议 ━━━
1. [标题] — N条回复
...

━━━ Hacker News 精选 ━━━
1. [标题] ↑N分 / N条评论
...

━━━ GitHub 热门仓库 ━━━
1. [仓库名] — ⭐N — [语言]
   [描述]
...

━━━ B站技术热门 ━━━
1. [标题] — UP主 — N播放
...

━━━ 今日摘要 ━━━
3-5句总结今日技术趋势。
```

## Model Usage

- All data collection: free public APIs
- LLM summarization: inherits default model (Gemini 2.0 Flash = free)
- No paid model needed at any stage

## Tips

- **Jina Reader** returns clean markdown from any URL via `curl https://r.jina.ai/URL`
- **B站 API** does not require login for popular/hot endpoints
- **GitHub API** unauthed limit is 60 req/hr — more than enough for a daily cron
- Keep final report under 2000 chars for WeChat/QQ mobile readability
- Use emoji and dividing lines in the output for mobile-friendly formatting
