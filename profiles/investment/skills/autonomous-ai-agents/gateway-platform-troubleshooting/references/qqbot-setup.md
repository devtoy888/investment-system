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

## Profile 级配置注意事项

### 两套 .env 路径

| 场景 | .env 路径 |
|:-----|:----------|
| Default profile | `/opt/data/.env`（根目录） |
| 非 default profile（如 investment） | `/opt/data/profiles/<profile名>/.env` |

⚠️ **这是一个关键坑：** 修改 profile 级的 `.env` 后，必须**重启该 profile 对应的 gateway** 才生效。编辑根目录 `.env` 不影响 profile 级 gateway。

### 验证连接（Profile 级）

```bash
# 1. 找到该 profile 的 gateway PID
GW_PID=$(pgrep -f "hermes.*-p.*<profile名>.*gateway" | head -1)
echo "Gateway PID: $GW_PID"

# 2. 检查 QQ 凭证是否被加载到进程
cat /proc/$GW_PID/environ 2>/dev/null | tr '\0' '\n' | grep QQ_

# 3. 检查 WebSocket 连接是否已建立（ESTABLISHED）
cat /proc/$GW_PID/net/tcp 2>/dev/null | grep -v "00000000:0000" | while read line; do
  remote=$(echo $line | awk '{print $3}')
  if [ "$remote" != "00000000:0000" ] && [ "$remote" != "" ]; then
    rip=$(echo $remote | cut -d: -f1)
    rport=$(echo $remote | cut -d: -f2)
    # 解十六进制 IP
    ip=$(printf "%d.%d.%d.%d" 0x${rip:0:2} 0x${rip:2:2} 0x${rip:4:2} 0x${rip:6:2} 2>/dev/null)
    echo "连接: $ip:$(printf '%d' 0x$rport 2>/dev/null)"
  fi
done

# 4. 查看该 profile 的 gateway 日志
grep "QQBot" /opt/data/profiles/<profile名>/logs/gateway.log | tail -10
```

### 日志路径差异

| Profile | QQ Bot 日志位置 |
|:--------|:----------------|
| default | `/opt/data/logs/gateway.log`（主日志） |
| 非 default | `/opt/data/profiles/<profile名>/logs/gateway.log`（profile 专属） |
| s6 管道日志 | `/opt/data/logs/gateways/<profile名>/current`（rotated） |

### 重启 profile 级 gateway（从外部）

```bash
# 在宿主机上
docker exec hermes-main s6-svc -r /run/service/gateway-<profile名>/

# 或者直接通过 docker exec 重启
docker exec hermes-main hermes -p <profile名> gateway restart
```

### 常见坑：从 gateway 内部无法重启

详见 `gateway-platform-troubleshooting` 技能的 "Inside-Gateway Restart Dilemma" 章节。

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

## Known Bugs

### `connect()` missing `is_reconnect` parameter

The QQ bot adapter's `connect()` method as shipped lacks the `is_reconnect` keyword argument that `gateway/run.py` calls with:

```python
# In adapter.py (broken signature — line 281):
async def connect(self) -> bool:

# What the gateway runner expects (contract from BasePlatformAdapter):
async def connect(self, *, is_reconnect: bool = False) -> bool:
```

**Error in `gateway_state.json`:**
```json
"qqbot": {
    "state": "retrying",
    "error_message": "QQAdapter.connect() got an unexpected keyword argument 'is_reconnect'"
}
```

**Fix (requires root — adapter.py is in the container image):**

```bash
# From host, execute inside container as root:
docker exec -u root hermes-main python3 /opt/data/fix_qqbot_adapter.py
```

Or manually:
```bash
docker exec -u root hermes-main sed -i 's/async def connect(self) -> bool:/async def connect(self, *, is_reconnect: bool = False) -> bool:\n        del is_reconnect  # Reserved for BasePlatformAdapter contract compatibility/' /opt/hermes/gateway/platforms/qqbot/adapter.py
```

Then restart gateway:
```bash
docker exec hermes-main hermes gateway restart
```
