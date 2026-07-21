# QQBot Gateway Setup (Docker Container)

Environment-specific details for setting up the QQ Bot platform adapter in this Docker-based Hermes deployment.

## Current Config

**Credentials** (in `/opt/data/.env`):
```
QQ_APP_ID=1904452472
QQ_CLIENT_SECRET=*** (redacted)
```

**Platform policies** (set via `hermes config set qqbot.*` and confirmed during setup):
| Setting | Value | Meaning |
|---------|-------|---------|
| `qqbot.dm_policy` | `open` | Anyone can DM the bot |
| `qqbot.group_policy` | `open` | Bot works in any group |
| `qqbot.markdown_support` | `true` | Rich text messages enabled |

Set these with:
```bash
hermes config set qqbot.dm_policy open
hermes config set qqbot.group_policy open
hermes config set qqbot.markdown_support true
```

**Gateway allowlist**: `GATEWAY_ALLOW_ALL_USERS=true` — no user restrictions.

## Protocol Details

- **API**: QQ Official Bot API v2 (`api.sgroup.qq.com`)
- **Transport**: WebSocket (wss) for events, REST for outbound messages
- **Intents**: The adapter auto-negotiates the required intents via the Identify/Ready handshake

## Key Paths

| Path | Purpose |
|------|---------|
| `/opt/data/.env` | QQBot credentials (`QQ_APP_ID`, `QQ_CLIENT_SECRET`) |
| `/opt/data/config.yaml` | Platform settings (`qqbot.*` under `platform_toolsets`) |
| `/run/service/gateway-default/run` | s6 gateway service run script |
| `/opt/data/logs/gateway.log` | Gateway logs — check for `qqbot` connect/disconnect |
| `/opt/data/channel_directory.json` | Platform chat routing (qqbot key exists) |

## Log Patterns

**Successful connection:**
```
Connecting to qqbot...
[QQBot:1904452472] Access token refreshed, expires in 1462s
[QQBot:1904452472] Gateway URL: wss://api.sgroup.qq.com/websocket
[QQBot:1904452472] WebSocket connected to wss://api.sgroup.qq.com/websocket
[QQBot:1904452472] Connected
✓ qqbot connected
Identify sent
Ready, session_id=xxx
Gateway running with 2 platform(s)
```

**Reconnection (session timeout):**
```
[QQBot:1904452472] Server requested reconnect (op 7)
[QQBot:1904452472] WebSocket closed: code=4009 reason=Session timed out
[QQBot:1904452472] Reconnecting in 2s (attempt 1)...
[QQBot:1904452472] WebSocket connected to wss://api.sgroup.qq.com/websocket
[QQBot:1904452472] Reconnected
[QQBot:1904452472] Resume sent (session_id=xxx, seq=N)
[QQBot:1904452472] Session resumed
```

## Configuration Commands

```bash
# Set platform policies (takes effect after gateway restart)
hermes config set qqbot.dm_policy open          # open | allowlist | disabled
hermes config set qqbot.group_policy open       # open | allowlist | disabled
hermes config set qqbot.markdown_support true   # true | false
```

## Restart Sequence

```bash
# 1. Find s6-svc
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)

# 2. Restart gateway
"$S6_SVC" -r /run/service/gateway-default/

# 3. Wait and verify
sleep 8
grep -i "qqbot\\|platform" /opt/data/logs/gateway.log | tail -10
```

## Notes

- QQBot WebSocket sessions auto-reconnect on timeout (every ~30 minutes). This is normal behaviour — the adapter handles reconnection transparently.
- The `Identify` handshake establishes the session; `Ready` confirms the bot is listening.
- `GATEWAY_ALLOW_ALL_USERS=true` must be set in `.env` for the bot to respond to users who aren't on any allowlist.
