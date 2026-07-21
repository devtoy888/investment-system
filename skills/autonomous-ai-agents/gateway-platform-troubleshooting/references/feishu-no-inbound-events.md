# Feishu Connected but No Inbound Events

## Symptom

Gateway log shows:
```
[Feishu] Connected in websocket mode (feishu)
✓ feishu connected
```

But no `inbound message: platform=feishu` entries appear, even when user sends messages to the bot. The bot is completely silent.

WebSocket also keeps disconnecting and reconnecting every few minutes with a new `device_id` each time.

## Verified Causes

### 1. Event subscription not configured (most common)

The Feishu WebSocket connects to Feishu's message gateway, but Feishu only forwards events that the app has explicitly subscribed to. Without `im.message.receive_v1`, Feishu drops all user messages silently.

**Fix:** In [open.feishu.cn](https://open.feishu.cn) → your app → 事件与回调 → 事件 → add `im.message.receive_v1`.

### 2. App permissions not granted

Even with the event subscribed, the app needs the `im:message` permission scope. If it's not granted (by tenant admin or via a published version), Feishu won't deliver message events.

**Fix:** 权限管理 → add `im:message` → either have tenant admin approve, or publish a new version.

### 3. App not published

This is the **most overlooked** step. Permission and event subscription changes in draft mode do NOT take effect. The app must be published (版本管理 → 创建版本 → 发布) for the changes to reach production.

**After publishing**, wait 1-2 minutes then restart the gateway.

### 4. Connection mode mismatch

`FEISHU_CONNECTION_MODE=websocket` in `.env` must match the setting in the Feishu developer console (事件与回调 → 连接方式 → WebSocket).

## Diagnosis Script

```bash
# 1. Verify connection
grep "feishu\\|Lark" /opt/data/logs/gateway.log | tail -10
# Expected: ✓ feishu connected

# 2. Check for any inbound events at all
grep -c "inbound.*feishu" /opt/data/logs/gateway.log
# Expected: > 0 (if user has sent messages)

# 3. Check for duplicate dedup (events arriving but being filtered as duplicates)
grep "duplicate\\|Dropping" /opt/data/logs/agent.log | grep -i feishu

# 4. Find all connection/disconnection events
grep "Connected\\|Disconnected" /opt/data/logs/gateway.log | grep feishu
# Frequent disconnects with new device_id → normal WebSocket reconnect behavior
```

## API-Level Diagnosis (definitive test)

When the basic checks pass but no inbound messages arrive, test the Feishu API directly to verify the app's authentication and activation status:

```bash
# Source dependencies
cd /opt/data && . /opt/hermes/.venv/bin/activate

# Read credentials
APP_ID=$(grep "^FEISHU_APP_ID" /opt/data/.env | cut -d= -f2)
APP_SECRET=$(grep "^FEISHU_APP_SECRET" /opt/data/.env | cut -d= -f2)

# Test using Python (avoids shell escaping issues with long secrets)
python3 -c "
import urllib.request, json

app_id = '$APP_ID'
app_secret = '$APP_SECRET'

# Step 1: Get tenant_access_token (proves credentials are valid)
data = json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode()
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=data,
    headers={'Content-Type': 'application/json; charset=utf-8'}
)
resp = urllib.request.urlopen(req, timeout=15)
result = json.loads(resp.read())
token = result.get('tenant_access_token', '')

if not token:
    print('❌ Token获取失败:', result.get('msg', 'unknown'))
    exit(1)

print('✅ Token获取成功')

# Step 2: Get bot info — check activate_status!
req2 = urllib.request.Request(
    'https://open.feishu.cn/open-apis/bot/v3/info',
    headers={'Authorization': f'Bearer {token}'}
)
resp2 = urllib.request.urlopen(req2, timeout=15)
bot_info = json.loads(resp2.read())

bot = bot_info.get('bot', {})
activate_status = bot.get('activate_status', '?')
app_name = bot.get('app_name', 'N/A')
bot_open_id = bot.get('open_id', 'N/A')

print(f'机器人名称: {app_name}')
print(f'机器人ID: {bot_open_id}')
print(f'激活状态: {activate_status}')

if activate_status == 1:
    print('✅ 机器人已激活 — 应该可以接收消息')
elif activate_status == 2:
    print('❌ 机器人未激活 — 需要在飞书开发者控制台启用并发布')
    print('   修方法: 事件与回调→事件→订阅im.message.receive_v1')
    print('           权限管理→添加im:message→发布新版本')
else:
    print(f'⚠️ 未知激活状态: {activate_status}')
"
```

**Expected `activate_status` values:**
- `1` = Bot is activated and can receive messages
- `2` = ambiguous — may be "not activated" in some cases, but can also indicate a functioning bot. **Do NOT rely on this field alone**; the bot in this session had `2` and worked normally.
- Any other value = unusual state, check the developer console

**Important:** The gateway WebSocket can connect successfully even when `activate_status=2`.
The definitive test is checking gateway logs after sending a message — see
`references/feishu-manual-setup.md` → Post-Setup: Verify the Bot Responds.

## Root Cause Tree

```
Feishu WS connects but no inbound events
│
├── Event subscription missing?
│   → Add `im.message.receive_v1` in Feishu Dev Console
│
├── Permission scope missing?
│   → Add `im:message`, grant or publish
│
├── App not published?
│   → Publish a new version (draft changes don't take effect)
│
└── Connection mode mismatch?
    → Check .env FEISHU_CONNECTION_MODE matches Dev Console setting
```

## Common Frustration Pattern: "I Added Permissions But It Still Doesn't Work"

This is the #1 support issue for Feishu bots. The user:

1. Adds permissions in the Developer Console ✅
2. Subscribes to events ✅
3. Restarts the gateway ✅
4. Sends a message → **still no response** ❌

**Root cause in 90% of cases:** The app was never **published**. Adding permissions and event subscriptions in the Developer Console only modifies the **draft version** of the app. None of those changes take effect in production until a new version is published.

### What Publishing Looks Like

In the [Feishu Developer Console](https://open.feishu.cn):

1. Open your app → look at the **top-right corner** of the page
2. You'll see one of two buttons:
   - **「发布」** (Publish) — click this, then "创建版本" (Create Version) → fill in version notes → "提交" (Submit)
   - **「创建版本」** (Create Version) — the app hasn't been published before. Click this first, then submit.
3. After submitting, the version goes through review (usually 1-30 minutes, sometimes instant for in-company apps)
4. Once approved, `activate_status` changes from `2` → `1`

### How to Confirm Publishing Took Effect

Do NOT rely on the gateway logs — the WebSocket can connect even when `activate_status=2`. The definitive check is the API:

```bash
cd /opt/data && . /opt/hermes/.venv/bin/activate
. /opt/data/.env

python3 -c "
import urllib.request, json

# Read credentials
with open('/opt/data/.env') as f:
    app_id = app_secret = ''
    for line in f:
        if line.startswith('FEISHU_APP_ID='): app_id = line.split('=',1)[1].strip()
        if line.startswith('FEISHU_APP_SECRET='): app_secret = line.split('=',1)[1].strip()

# Get token
data = json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode()
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=data, headers={'Content-Type': 'application/json; charset=utf-8'}
)
token = json.loads(urllib.request.urlopen(req, timeout=15).read()).get('tenant_access_token','')

# Check activation status
req2 = urllib.request.Request(
    'https://open.feishu.cn/open-apis/bot/v3/info',
    headers={'Authorization': f'Bearer {token}'}
)
bot = json.loads(urllib.request.urlopen(req2, timeout=15).read()).get('bot',{})
status = bot.get('activate_status')
print(f'activate_status = {status}')
if status == 1:
    print('✅ 机器人已激活 — 应该可以接收消息了')
elif status == 2:
    print('❌ 仍未激活 — 应用还没发布上线')
    print('   请去 open.feishu.cn → 右上角「发布」→ 创建版本 → 提交')
else:
    print(f'⚠️ 未知状态: {status}')
"
