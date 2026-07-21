# DingTalk Gateway Setup (Docker Container)

Environment-specific details for setting up DingTalk (钉钉) via the Hermes plugin at `/opt/hermes/plugins/platforms/dingtalk/`.

## Architecture

DingTalk uses **Stream Mode** — a WebSocket connection initiated from Hermes to DingTalk's servers. No public URL, domain, or webhook server needed. Works behind NAT and firewalls.

The adapter is a **plugin**, not a built-in platform:
- Plugin root: `/opt/hermes/plugins/platforms/dingtalk/`
- Plugin manifest: `plugin.yaml`
- Adapter code: `adapter.py`
- Registration: installed by default in the `enabled` plugin list; no `hermes plugins install` needed

## Prerequisites

Python packages (installed in the target dir since the venv is root-owned):
```bash
uv pip install "dingtalk-stream>=0.20" httpx --target /opt/data/.feishu-deps --no-compile
```

## Setup Options

### Option A: QR Code Login (Recommended)

Run the gateway setup wizard interactively:
```bash
hermes gateway setup
```

Flow:
1. Select **DingTalk** from the platform list
2. Choose **QR Code Scan (Recommended)**
3. A QR code is displayed in the terminal (ASCII art + URL link)
4. **Scan with DingTalk mobile app** → the QR authorization flow auto-obtains Client ID and Client Secret
5. Credentials are auto-written to `/opt/data/.env` and optionally `~/.hermes/weixin/accounts/` (for persistent storage)
6. The wizard then prompts for:
   - **Allowed users** — DingTalk User IDs (staff_ids) that are allowed to interact with the bot
   - **Home channel** — whether to use a specific chat for cron/notification delivery
7. Gateway restarts automatically

> **Note on branding**: The QR flow uses DingTalk's `openClaw` registration template (hardcoded verification URI). This is a cosmetic DingTalk-side display issue — the bot is fully yours and private to your tenant.

### Option B: Manual Credentials

1. Go to https://open-dev.dingtalk.com/
2. Create **Application Development → Custom Apps → Create App via H5 Micro-App (or Robot)**
3. Fill in App Name (e.g. "Hermes Agent") and description
4. Get **Client ID** (AppKey) and **Client Secret** (AppSecret) from **Credentials & Basic Info**
5. Enable **Robot** capability → set **Message Reception Mode** to **Stream Mode**
6. Set credentials in `.env`:
```
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret
DINGTALK_ALLOWED_USERS=your-dingtalk-user-id
```

> **Important**: Client Secret is only shown once in the DingTalk console. Save it immediately.

## Current Config

```env
DINGTALK_CLIENT_ID=<app-key>
DINGTALK_CLIENT_SECRET=<app-secret>
DINGTALK_ALLOWED_USERS=<user-id>  # Comma-separated for multiple
```

## Key Paths

| Path | Purpose |
|------|---------|
| `/opt/data/.env` | Credentials (DINGTALK_CLIENT_ID, DINGTALK_CLIENT_SECRET) |
| `/opt/data/.feishu-deps/` | Python deps (dingtalk-stream, httpx) installed via `--target` |
| `/run/service/gateway-default/run` | s6 gateway script (PYTHONPATH for deps) |
| `/opt/data/logs/gateway.log` | Gateway logs — check for `dingtalk` messages |
| `/opt/hermes/plugins/platforms/dingtalk/` | DingTalk plugin source |

## Log Patterns

**Successful connection:**
```
Connecting to dingtalk...
[DingTalk] Stream client connected
✓ dingtalk connected
Gateway running with N platform(s)
```

**Missing dependencies:**
```
ModuleNotFoundError: No module named 'dingtalk_stream'
```

**Missing credentials:**
```
DINGTALK_CLIENT_ID and DINGTALK_CLIENT_SECRET required
```

## DingTalk User ID

To find your DingTalk User ID:
1. Ask your organization's DingTalk admin — it's in the admin console under **Contacts → Members**
2. Alternatively, start the gateway, send the bot a message, then check the gateway logs for `sender_id`

## Behavior Summary

| Context | Behavior |
|---------|----------|
| Direct Messages (1:1) | Responds to every message. No @mention needed. Each DM gets its own session. |
| Group chats | Responds only when @mentioned (controlled by `DINGTALK_REQUIRE_MENTION`). |
| Shared groups, multiple users | Each user gets an isolated session by default (`group_sessions_per_user: true`). |

## Restart Sequence

Same as other platforms:
```bash
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/
sleep 8
grep -i "dingtalk\|Connected\|platform" /opt/data/logs/gateway.log | tail -10
```
