# Agent Reach — Server/VPS Installation Patterns

## uv tool PATH Gotcha

`uv tool install` places executables in `$HOME/.local/bin/` but this is **NOT on PATH by default** on our Oracle ARM Docker container.

**Fix:** Always run `export PATH="$HOME/.local/bin:$PATH"` after installing tools, or add it to the session environment.

```bash
export PATH="/opt/data/home/.local/bin:$PATH"
```

## Real gh CLI vs Wrapper

Agent Reach ships a minimal `gh` wrapper at `/opt/data/home/.local/bin/gh` — it's a Python argparse stub, NOT the real GitHub CLI. It lacks `auth login`, `api`, etc.

**Fix:** Download the real binary from GitHub releases:
```bash
curl -fsSL "https://github.com/cli/cli/releases/download/v2.78.0/gh_2.78.0_linux_arm64.tar.gz" -o /tmp/gh.tar.gz
tar xzf /tmp/gh.tar.gz
cp gh_2.78.0_linux_arm64/bin/gh /opt/data/home/.local/bin/gh
chmod +x /opt/data/home/.local/bin/gh
```

Then authenticate:
```bash
echo "ghp_..." | gh auth login --with-token
```

## xiaohongshu-mcp on ARM64

The release page has `linux-arm64` variant (not `aarch64`). Binary name pattern:
```
xiaohongshu-mcp-linux-arm64.tar.gz  → extracts to xiaohongshu-mcp-linux-arm64
xiaohongshu-login-linux-arm64       → companion login helper
```

Start as background process via `terminal(background=true)`, then register:
```bash
mcporter config add xiaohongshu http://localhost:18060/mcp
```

## Groq API Key for 小宇宙

`agent-reach configure groq-key <key>` writes to `~/.agent-reach/config.yaml`.
The transcribe.sh script reads it via Python YAML parser. If the script fails to
extract the key, set `GROQ_API_KEY` env var directly:
```bash
export GROQ_API_KEY=gsk_xxxxx
bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh <episode-url>
```

## Xueqiu Cookie Configuration (Critical Pitfall)

The `_inject_cookie_string()` in `xueqiu.py` expects the cookie value in
`name=value` format (e.g. `xq_a_token=bf314c69991389db874f6a94089112bfe67ade27`),
NOT just the raw token value.

**Common mistake:** Adding `S` prefix. The token value is `bf314c69991389db874f6a94089112bfe67ade27` —
no `S` prefix. Writing `Sbf314c69991389db874f6a94089112bfe67ade27` causes 400016 error.

**Correct config.yaml entry:**
```yaml
xueqiu_cookie: xq_a_token=bf314c69991389db874f6a94089112bfe67ade27
```

**Test before assuming it works:**
```bash
curl -s -b "xq_a_token=bf314c69991389db874f6a94089112bfe67ade27" \
  -H "User-Agent: Mozilla/5.0 ..." \
  -H "Referer: https://xueqiu.com/" \
  "https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol=SH000001"
# Success: returns quote data. Failure (400016): token expired/invalid.
```

## mcporter Config Location (Critical)

`mcporter config add <name> <url>` saves to `/tmp/config/mcporter.json` by default,
which is lost on container restart. The **persistent project config** is at
`/opt/data/config/mcporter.json`.

**Fix:** Always add servers to the project config, not /tmp:
```bash
# Check where mcporter reads config from:
mcporter config list

# Write to the correct location:
python3 -c "
import json
with open('/opt/data/config/mcporter.json', 'r') as f:
    cfg = json.load(f)
if 'mcpServers' not in cfg: cfg['mcpServers'] = {}
cfg['mcpServers']['<name>'] = {'baseUrl': '<url>'}
with open('/opt/data/config/mcporter.json', 'w') as f:
    json.dump(cfg, f, indent=2)
"
```

## Website SPA Breakage

Many modern sites (小宇宙, B站) are SPAs — the audio URL is embedded in JavaScript
rendered content, not in the raw HTML. The `transcribe.sh` script uses `curl -s`
which only gets the initial HTML, not the JS-rendered DOM.

**Workaround:** If the script fails with "无法从页面提取音频链接":
1. Try getting the audio URL manually via browser DevTools Network tab
2. Or use `yt-dlp` as a fallback for YouTube/B站 audio extraction
3. For 小宇宙 specifically, the audio CDN pattern changed from `media.xyzcdn.net`
   to a new domain — update the regex in transcribe.sh if needed

## 小红书 on Headless ARM64 Servers — Confirmed Unusable

xiaohongshu-mcp uses go-rod which requires Chromium. On ARM64 servers:
- Google Playwright chromium archive has no arm64 build
- npm mirror has no arm64 chromium
- The binary downloads fail silently with empty files (111 bytes = error page)

**Result:** 小红书 is impossible on headless ARM64 servers. On desktop machines,
use OpenCLI instead (reuses browser login state, no Chromium needed).

**Desktop alternative:** `agent-reach install --channels opencli` + Chrome extension
Cookie-Editor → export cookie → configure in agent-reach.