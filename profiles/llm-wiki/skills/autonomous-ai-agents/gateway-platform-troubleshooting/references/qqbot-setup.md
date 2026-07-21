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

## Troubleshooting

### Error: `qqbot-appid_lock` — "QQBot app ID already in use (PID XXXX)"

This means another gateway process is holding the same QQ App ID's WebSocket connection. The current gateway cannot connect until that process releases the app ID.

**Check the conflicting PID:**
```bash
ps -p <PID> -o pid,cmd
```

If it's a stale/defunct hermes gateway process — kill it:
```bash
kill -9 <PID>
```

**Then restart the gateway** to pick up the new state (see Restart Sequence). Note: you CANNOT restart the gateway from inside a running gateway session — the `terminal` tool blocks `kill/hermes gateway restart` on the gateway PID itself. Run the restart command from a separate shell or a Docker exec:

```bash
docker exec hermes-main hermes gateway restart
# or
docker restart hermes-main
```

**Root cause:** The old gateway process had already established a WebSocket connection with the QQ bot platform. When the gateway restarted (e.g. via `--replace`), the new process saw the old process's connection still active and refused to create a duplicate.

### Error: `100016` — "invalid appid or secret"

The QQ bot client secret has expired or been revoked. Regenerate from [QQ Open Platform](https://q.qq.com/) and update `QQ_CLIENT_SECRET` in `.env`.

### Gateway connects with old credentials after .env edit

**The .env file is read by python-dotenv at process import time, NOT per-request.** If you modify `.env` while the gateway is running, the new values will NOT be seen until the gateway process is fully restarted.

After updating `QQ_APP_ID` / `QQ_CLIENT_SECRET` in `.env`:
1. Kill the conflicting old PID (if `qqbot-appid_lock` error appears)
2. Restart the gateway via Docker exec or docker restart
3. Verify in logs: `grep "qqbot" /opt/data/logs/gateway.log | tail -10`

Expected successful connection with the new app ID:
```
[QQBot:<new_app_id>] Access token refreshed
[QQBot:<new_app_id>] WebSocket connected to wss://api.sgroup.qq.com/websocket
[QQBot:<new_app_id>] Connected
✓ qqbot connected
```

### Stale `gateway_state.json`

After killing the conflicting PID and the gateway fully restarting, `gateway_state.json` may still show the old PID and old error. The state file is written by the gateway process on state transitions — if the gateway was restarted (new PID) the old state file persists with stale data until the new gateway writes an update.

**Check the actual running PID vs the state file:**
```bash
# Actual running gateway PID
ps aux | grep "hermes gateway run" | grep -v grep
# vs state file reference:
python3 -c "import json; d=json.load(open('/opt/data/gateway_state.json')); print('State claims PID:', d.get('pid'))"
```

If the PIDs differ, the state file is stale. The new gateway will overwrite it on the next platform state transition (connection, disconnection, reconnect attempt). Wait for the qqbot reconnect cycle (every ~300s) and re-check.

## Notes

- QQBot WebSocket sessions auto-reconnect on timeout (every ~30 minutes). This is normal behaviour — the adapter handles reconnection transparently.
- The `Identify` handshake establishes the session; `Ready` confirms the bot is listening.
- `GATEWAY_ALLOW_ALL_USERS=true` must be set in `.env` for the bot to respond to users who aren't on any allowlist.
- If the user modifies `.env` themself (preferred for credential operations), you must still handle the gateway restart side — kill stale PIDs first, then restart.
