---
name: agent-reach-setup
description: "Install and configure Agent Reach — 13-platform internet access router for Hermes Agent on Docker/VPS environments."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [agent-reach, internet-access, research, docker, vps]
    related_skills: [hermes-agent]
---

# Agent Reach Setup

Install and configure Agent Reach for maximum platform coverage on Docker/VPS environments.

## When to Use This Skill

- User wants to research/search anything on the internet
- User mentions platforms: 小红书, Twitter/X, B站, V2EX, Reddit, LinkedIn, YouTube, 雪球, 小宇宙
- User says 调研/research/搜索/search/查/找/看看大家怎么说
- After a fresh Hermes Agent install on a new server

## Quick Install (All-in-One)

```bash
AGENT_REACH=/opt/data/home/.local/share/uv/tools/agent-reach/bin/agent-reach
$AGENT_REACH install --env=auto
$AGENT_REACH install --channels=all
```

Then manually install remaining tools (see below).

## Manual Tool Installation (Server/Docker)

On Docker containers without root/apt, use `uv tool install` instead of `pipx` or `apt-get`:

```bash
export PATH="/opt/data/home/.local/bin:$PATH"

# Core tools (no auth needed)
uv tool install yt-dlp          # YouTube downloader
uv tool install twitter-cli     # Twitter search
uv tool install bilibili-cli    # B站 search/subtitles
uv tool install rdt-cli         # Reddit (git+...)
npm install -g mcporter --prefix /opt/data/home/.local  # mcporter needs npm

# GitHub CLI — CRITICAL: uv tool install gh gives a BROKEN wrapper
# Download real CLI from GitHub releases (aarch64 for ARM servers):
cd /tmp && curl -fsSL "https://github.com/cli/cli/releases/download/v2.78.0/gh_2.78.0_linux_arm64.tar.gz" -o gh.tar.gz
tar xzf gh.tar.gz && cp gh_*/bin/gh /opt/data/home/.local/bin/gh
gh version  # verify it says "gh version X.XX.X" not "v0.0.4"
```

**⚠️ Binary naming:** `twitter-cli` installs as `twitter`, `bilibili-cli` installs as `bili`. Agent Reach auto-detects these.

**⚠️ gh CLI wrapper trap:** `uv tool install gh` on this system installs a minimal CLI wrapper (`v0.0.4`) that does NOT support `gh auth login` or `gh auth status`. You MUST download the real binary from GitHub releases.

## Platform-Specific Setup

### 小红书 (XiaoHongShu) — Needs Login

```bash
# 1. Download ARM64 binary
mkdir -p ~/.agent-reach/tools
curl -fsSL "https://github.com/xpzouying/xiaohongshu-mcp/releases/latest/download/xiaohongshu-mcp-linux-arm64.tar.gz" \
  -o ~/.agent-reach/tools/xiaohongshu-mcp.tar.gz
tar xzf ~/.agent-reach/tools/xiaohongshu-mcp.tar.gz -C ~/.agent-reach/tools/

# 2. Start MCP server (background)
~/.agent-reach/tools/xiaohongshu-mcp-linux-arm64  # runs on port 18060

# 3. Register with mcporter
mcporter config add xiaohongshu http://localhost:18060/mcp

# 4. First run: scan QR code to login
```

### Exa 全网搜索

```bash
mcporter config add exa https://mcp.exa.ai/mcp
# Requires Exa API key (free tier available)
```

### 小宇宙播客

```bash
# Script already installed with agent-reach install --env=auto
# Requires Groq API key for transcription
agent-reach configure groq-key gsk_xxxxx
```

### GitHub

```bash
# After real gh CLI is installed, authenticate
echo "ghp_XXX" | gh auth login --with-token
gh auth status  # verify
```

See `references/github-auth.md` for mobile-friendly PAT generation guide.

## Status Check

```bash
AGENT_REACH=/opt/data/home/.local/share/uv/tools/agent-reach/bin/agent-reach
$AGENT_REACH doctor --json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p, info in sorted(data.items()):
    icon = {'ok':'✅','warn':'⚠️','off':'❌'}[info['status']]
    print(f'{icon} {info[\"name\"]}: {info.get(\"active_backend\",\"None\")}')
"
```

## Known Limitations on Server/VPS

| Platform | Issue | Workaround |
|----------|-------|------------|
| LinkedIn | Needs desktop browser for scraping | Use Jina Reader for public pages only |
| Twitter | Needs API key (X Premium) | Basic search may work without auth |
| Reddit | Needs login cookie | Use rdt-cli + cookie import |
| 小红书 | Needs QR code login | Run xiaohongshu-mcp, scan once |
| OpenCLI | Needs Chrome + desktop env | Skip on headless servers |

## Pitfalls

- **agent-reach not in PATH** — binary is at `/opt/data/home/.local/share/uv/tools/agent-reach/bin/agent-reach`, not in system PATH
- **uv tool binaries not in PATH** — `uv tool install` puts binaries in `/opt/data/home/.local/bin/`, must add to PATH
- **npm global install needs --prefix** — on Docker containers without root, `npm install -g` fails; use `--prefix /opt/data/home/.local`
- **xiaohongshu-mcp needs ARM64 binary** — server is aarch64, download `-linux-arm64` variant, NOT amd64
- **mcporter config file location** — stores at `/opt/data/home/.agent-reach/tools/config/mcporter.json`, not standard locations
- **Agent Reach skill lives at** `~/.agents/skills/agent-reach/` — verify it loads with `hermes skills list`
- **`skill_view` won't find agent-reach** — it's in `~/.agents/skills/` not `~/.hermes/skills/`. Read references directly with `cat ~/.agents/skills/agent-reach/references/<name>.md`
- **gh CLI wrapper trap** — `uv tool install gh` gives a broken v0.0.4 wrapper. Must download real binary from GitHub releases (aarch64 tar.gz for ARM servers)
- **mcporter call syntax** — uses `server.tool_name param: "value"` positional format, NOT JSON. Example: `mcporter call exa.web_search_exa query: "term" numResults: 3`. JSON body gets double-encoded and fails validation.
- **xueqiu cookie format** — `_inject_cookie_string()` parses `"name=value; name2=value2"` format. Write `xq_a_token=YOUR_TOKEN` in config.yaml. The token value is the raw hex (e.g. `bf314c69991389db874f6a94089112bfe67ade27`), NOT `Sbf314c69991389db874f6a94089112bfe67ade27` — the S prefix causes 400016 session error.
- **小红书 on headless server** — xiaohongshu-mcp requires Chromium browser (go-rod), which cannot download on ARM64 headless servers. All MCP tools fail with "can't find a browser binary." This is a hard limitation — skip 小红书 on pure VPS/Docker without GUI.
- **小宇宙 website parsing** — xiaoyuzhoufm.com is a Next.js SPA; audio URLs come from JS-rendered content. The `transcribe.sh` script uses static regex that breaks on SPA pages. Works only with direct .m4a/.mp3 files passed to Groq transcription.

## References
- `references/platform-status.md` — Verified working configurations, mcporter call syntax, headless server limitations matrix.
- **mcporter call syntax** — uses `server.tool_name param: "value"` positional format, NOT JSON. Example: `mcporter call exa.web_search_exa query: "term" numResults: 3`. JSON body gets double-encoded and fails validation.
- **xueqiu cookie format** — `_inject_cookie_string()` parses `"name=value; name2=value2"` format. Write `xq_a_token=YOUR_TOKEN` in config.yaml. The token value is the raw hex (e.g. `bf314c69991389db874f6a94089112bfe67ade27`), NOT `Sbf314c69991389db874f6a94089112bfe67ade27` — the S prefix causes 400016 session error.
- **小红书 on headless server** — xiaohongshu-mcp requires Chromium browser (go-rod), which cannot download on ARM64 headless servers. All MCP tools fail with "can't find a browser binary." This is a hard limitation — skip 小红书 on pure VPS/Docker without GUI.
- **小宇宙 website parsing** — xiaoyuzhoufm.com is a Next.js SPA; audio URLs come from JS-rendered content. The `transcribe.sh` script uses static regex that breaks on SPA pages. Works only with direct .m4a/.mp3 files passed to Groq transcription.