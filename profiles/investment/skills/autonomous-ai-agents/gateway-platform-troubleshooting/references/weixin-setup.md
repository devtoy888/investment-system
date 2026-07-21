# Weixin (WeChat) Gateway Setup (Docker Container)

Environment-specific details for setting up the WeChat personal account platform adapter in this Docker-based Hermes deployment.

## How It Works

The Weixin adapter uses **Tencent's iLink Bot API** (`ilinkai.weixin.qq.com`) to connect personal WeChat accounts. Messages are delivered via **long-polling** — no webhook, WebSocket, or public endpoint is needed.

## Setup Methods

### Method 1: QR Code Login (Recommended)

```bash
hermes gateway setup
```

The wizard will:
1. Request a QR code from the iLink Bot API
2. Display the QR code in the terminal (or provide a URL)
3. Wait for you to scan it with the WeChat mobile app
4. Prompt confirmation on the phone
5. Save credentials automatically to `~/.hermes/weixin/accounts/`

**If running from a non-interactive Hermes session** (tool-calling mode), use the PTY+background+process pattern:

```
terminal(command="hermes gateway setup", pty=true, background=true)
→ note the session_id returned

# Select option 13 (Weixin/WeChat):
process(action="submit", session_id="<id>", data="13")

# Confirm start:
process(action="submit", session_id="<id>", data="y")
```

Poll output via `process(action="poll", session_id="<id>")` between submits to read QR URLs and confirm the flow.

Expected output:
```
微信连接成功，account_id=your-account-id
```

After QR login, set at minimum the account ID in `.env`:
```
WEIXIN_ACCOUNT_ID=your-account-id
```

### Method 2: Manual Token

Get credentials from the iLink Bot platform, then set in `.env`:
```
WEIXIN_ACCOUNT_ID=your-account-id
WEIXIN_TOKEN=your-bot-token
```

## Current Config

**Credentials** (in `/opt/data/.env`):
```env
WEIXIN_ACCOUNT_ID=1378bfc90242@im.bot
# Token is saved automatically from QR login in ~/.hermes/weixin/accounts/
```

**Current policies:**
| Policy | Value | Description |
|--------|-------|-------------|
| `WEIXIN_DM_POLICY` | `pairing` | DM pairing approval — unknown users must request access, approved via `hermes pairing approve` |
| `WEIXIN_GROUP_POLICY` | `disabled` | Group chats disabled (iLink bots cannot join ordinary WeChat groups) |

**DM pairing flow** (chosen during `hermes gateway setup`):
- When an unknown user DMs the bot, Hermes notifies the operator to approve/deny
- Approve: `hermes pairing approve <user_id>`
- List pending: `hermes pairing list`
- Revoke: `hermes pairing revoke <user_id>`
- Alternative: set `WEIXIN_DM_POLICY=open` in `.env` to allow all DMs without approval

**Policy env var values:**
| Env Var | Values | Description |
|---------|--------|-------------|
| `WEIXIN_DM_POLICY` | `open` / `allowlist` / `disabled` / `pairing` | DM access control. `pairing` requires operator approval. |
| `WEIXIN_GROUP_POLICY` | `open` / `allowlist` / `disabled` | Group access control. Default `disabled`. |
| `WEIXIN_ALLOWED_USERS` | comma-separated user IDs | When `dm_policy=allowlist` |
| `WEIXIN_GROUP_ALLOWED_USERS` | comma-separated group IDs | When `group_policy=allowlist` |

## Key Paths

| Path | Purpose |
|------|---------|
| `/opt/data/.env` | Weixin credentials and optional overrides |
| `/opt/data/config.yaml` | `platforms.weixin.extra` for advanced config |
| `/opt/data/weixin/` | Context-token persistence and account files |
| `/opt/data/logs/gateway.log` | Gateway logs — check for `weixin` connect/disconnect |
| `/opt/data/channel_directory.json` | Platform chat routing (weixin key) |

## Log Patterns

**Successful connection:**
```
Connecting to weixin...
✓ weixin connected
Gateway running with N platform(s)
```

**Missing credentials:**
```
Connecting to weixin...
No adapter available for weixin
```

## Important Limitations

The iLink Bot identity is **NOT** a fully scriptable personal WeChat account:

| Capability | Works? |
|------------|--------|
| DMs to the bot (1-on-1) | ✅ Yes |
| Group messages | ❌ iLink typically does not deliver group events |
| @-mentioning personal account in groups | ❌ Different from mentioning the bot |
| Inviting bot to groups | ❌ iLink bots generally cannot be added |

These are iLink-side limitations, not Hermes bugs. The gateway logs a `WARNING` at startup if `group_policy` is set to anything other than `disabled`.

## Restart Sequence

```bash
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/
sleep 8
grep -i "weixin\|platform\|Connected" /opt/data/logs/gateway.log | tail -10
```
