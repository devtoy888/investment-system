---
name: agent-reach
description: >
  MUST USE when user wants to research/search/look up anything on the internet.
  Also MUST USE for platform-specific queries: 小红书, Twitter, B站, V2EX,
  Reddit, LinkedIn, YouTube, GitHub, 雪球, RSS, podcasts.
  Installs and configures Agent Reach's 13-platform router on diverse environments.
triggers:
  - research: 调研/全网调研/帮我调研/研究一下/research/深入了解
  - search: 搜/查/找/search/搜索/查一下/帮我搜/看看大家怎么说
  - social: 小红书/xiaohongshu/xhs, Twitter/推特/x.com, B站/bilibili, V2EX, Reddit
  - career: 招聘/职位/linkedin/领英
  - dev: github/代码/仓库
  - web: 网页/链接/文章/rss
  - video: youtube/视频/播客/字幕
  - finance: 雪球/股票/stock/xueqiu
metadata:
  openclaw:
    homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — Internet Capability Router

13 platforms, multi-backend routing. **Use this skill to install, configure, and operate Agent Reach.**

## Routing Table

| User intent | Category | Detailed docs |
|------------|----------|---------------|
| Web/code search | search | [references/search.md](references/search.md) |
| Social media | social | [references/social.md](references/social.md) |
| Career/LinkedIn | career | [references/career.md](references/career.md) |
| GitHub/code | dev | [references/dev.md](references/dev.md) |
| Web articles/RSS | web | [references/web.md](references/web.md) |
| YouTube/Bilibili/podcasts | video | [references/video.md](references/video.md) |

## Installation on Server/VPS (No Root, No pipx, No Desktop)

This is the most common failure mode. Agent Reach's `--env=auto` installer assumes
a desktop environment with root access — it fails silently on constrained servers.

### Step 1: Initial Setup
```bash
# Find the binary (it's in a uv tool cache, not in PATH)
AGENT_REACH=$(find / -name "agent-reach" -type f 2>/dev/null | grep bin | head -1)
$AGENT_REACH install --env=auto  # baseline install
```

### Step 2: Install Missing Channels via `uv tool install`
```bash
export PATH="$HOME/.local/bin:$PATH"  # uv tools install here by default

# Core tools (all via uv, no root needed):
uv tool install gh           # GitHub CLI
uv tool install yt-dlp       # YouTube download
uv tool install twitter-cli  # Twitter search
uv tool install bilibili-cli # Bilibili
uv tool install rdt          # Reddit (rdt-cli)

# npm-based tools (Node.js must be available):
npm install -g mcporter --prefix "$HOME/.local"  # Exa search backend
```

### Step 3: Install ARM64 Binaries (Oracle ARM servers)
```bash
mkdir -p ~/.agent-reach/tools
cd ~/.agent-reach/tools

# xiaohongshu-mcp (needs ARM64 binary, not amd64):
curl -fsSL "https://github.com/xpzouying/xiaohongshu-mcp/releases/latest/download/xiaohongshu-mcp-linux-arm64.tar.gz" -o xhs-mcp.tar.gz
tar xzf xhs-mcp.tar.gz

# Start the MCP server in background:
# Use terminal(background=true) so Hermes tracks it, then verify readiness
./xiaohongshu-mcp-linux-arm64 &

# Register with mcporter:
mcporter config add xiaohongshu http://localhost:18060/mcp
```

### Step 4: Verify
```bash
$AGENT_REACH doctor --json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for platform, info in sorted(data.items()):
    icon = {'ok':'✅','warn':'⚠️','off':'❌'}[info['status']]
    print(f'{icon} {info[\"name\"]}: {info.get(\"active_backend\",\"None\")}')
"
```

### Known Server-Side Limitations
- **OpenCLI** — requires desktop + Chrome, skip on servers
- **LinkedIn** — limited on server environments, needs desktop
- **GitHub** — `agent-reach` ships a wrapper `gh`; install real `gh` from GitHub releases for full auth
- **Twitter** — needs API key (X Premium)
- **Reddit** — needs Cookie login via `rdt login`
- **小宇宙** — transcribe.sh script works but website SPA structure may break audio URL extraction; test with real audio file if parsing fails
- **雪球** — cookie format must be `name=value` (e.g. `xq_a_token=xxx`), NOT just the raw token value. No `S` prefix.
- **小红书（服务器可行路径，2026-07 实测修正）** — after starting xiaohongshu-mcp binary, must register with `mcporter config add xiaohongshu http://localhost:18060/mcp`. **Headless ARM64 服务器**：`xiaohongshu-mcp`（go-rod+Chromium）仍不可用、`xhs login --qrcode`（camoufox）在服务器会崩；但 **`xiaohongshu-cli`（jackwener，逆向 Web API）数据采集中途不依赖浏览器**（search/read/feed/comments 走纯 HTTP 签名），仅在登录环节需浏览器。做法：桌面 `xhs login` → 导出 `~/.xiaohongshu-cli/cookies.json` → 传到服务器复用（约 7 天有效期，到期重导）。详见 `references/xiaohongshu-server.md`。mcporter config saves to /tmp by default; write to /opt/data/config/mcporter.json for persistence.

## Working Rules (from SKILL.md)

1. **Run `doctor --json` first** — check active_backend per platform before issuing commands
2. **Declare your backend** — start with "使用 agent-reach 的 X 平台 / Y 后端"
3. **Follow retry chains** in references/* when failures occur
4. **For 全网调研** — combine multiple platforms (Exa search + Twitter/Reddit discussion + 小红书/Bilibili Chinese context)
5. **After major tasks** — run `agent-reach check-update` and note any new version

## Environment Checks

```bash
# Check all channels and active backends
agent-reach doctor --json

# Check for updates
agent-reach check-update
```

## Workspace Rules

**Never create files in agent workspace.** Use `/tmp/` for temp output, `~/.agent-reach/` for persistent data.

## Detailed Documentation

Read the appropriate reference file based on user need:
- [references/search.md](references/search.md) — Exa AI search via mcporter
- [references/server-setup.md](references/server-setup.md) — Server/VPS installation patterns, uv tool PATH, ARM64 binaries, SPA site quirks
- [references/social.md](references/social.md) — 小红书, Twitter, B站, V2EX, Reddit (multi-backend commands)
- [references/career.md](references/career.md) — LinkedIn
- [references/dev.md](references/dev.md) — GitHub CLI
- [references/web.md](references/web.md) — Jina Reader, RSS
- [references/video.md](references/video.md) — YouTube, B站, 小宇宙