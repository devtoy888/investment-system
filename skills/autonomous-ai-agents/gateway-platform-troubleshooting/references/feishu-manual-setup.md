# Feishu Manual Step-by-Step Setup

Worked example from a session where the `hermes gateway setup` wizard's curses UI could not be used (the user was running through a CLI agent and couldn't see the interactive menu).

## When to Use This

The `hermes gateway setup` wizard handles everything automatically. Use this manual approach only when:
- Running through a CLI agent (the user can't see/type into the curses menu)
- The PTY+background+process I/O workaround is too slow or awkward for a multi-step wizard
- You need to inspect exactly what the wizard does before committing changes

## Approach

1. **Read the source** — find the platform's `interactive_setup()` function. For Feishu:
   `/opt/hermes/plugins/platforms/feishu/adapter.py::interactive_setup()`
   It reveals every question the wizard asks, with default values.

2. **Ask the user step by step** in plain text. One question at a time.

3. **Apply each answer** using:
   - `hermes config set <key> '<value>'` for config.yaml changes
   - `echo '<KEY>=<value>' >> /opt/data/.env` for environment variables
   - `uv pip install <dep> --target <writable-dir>` for dependencies + `PYTHONPATH`

## Step-by-Step Flow (Feishu)

| # | Question | Options | Default | Config Target |
|---|----------|---------|---------|--------------|
| 1 | Connection mode | WebSocket / Webhook | WebSocket | `FEISHU_CONNECTION_MODE` in `.env` |
| 2 | DM authorization | Pairing / Allow all / Allowlist | Pairing | `FEISHU_ALLOW_ALL_USERS`, `FEISHU_ALLOWED_USERS` in `.env` |
| 3 | Group chat handling | @mention only / Disabled | @mention | `FEISHU_GROUP_POLICY=open` or `disabled` in `.env` |
| 4 (opt) | Home chat ID | Free text | (empty) | `FEISHU_HOME_CHANNEL` in `.env` |

### After collecting user answers, apply:

**1. Enable the plugin:**
```bash
hermes config set plugins.enabled '["feishu-platform"]'
```

**2. Add platform toolset:**
```bash
hermes config set platform_toolsets.feishu '["hermes-feishu"]'
```

**3. Enable the platform:**
```bash
hermes config set platforms.feishu '{"enabled": true}'
```

**4. Write env vars** (one per line, append to `.env`):
```
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=your_secret
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOW_ALL_USERS=false
FEISHU_ALLOWED_USERS=
FEISHU_GROUP_POLICY=open
```

## Post-Setup: Finding the Home Chat ID

After setup, find a Chat ID for `FEISHU_HOME_CHANNEL` (cron/notification delivery target).
Query the Feishu API to list all chats the bot has access to. Use the reusable script
at `scripts/list-feishu-chats.py`, or run inline:

```bash
cd /opt/data && python3 -c "
import json, urllib.request

env = {}
with open('.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

APP_ID = env['FEISHU_APP_ID']
APP_SECRET = env['FEISHU_APP_SECRET']
BASE = 'https://open.feishu.cn' if env.get('FEISHU_DOMAIN', 'feishu') == 'feishu' else 'https://open.larksuite.com'

# Get token
req = urllib.request.Request(f'{BASE}/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({'app_id': APP_ID, 'app_secret': APP_SECRET}).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
token = json.loads(urllib.request.urlopen(req).read())['tenant_access_token']

# List chats
req2 = urllib.request.Request(f'{BASE}/open-apis/im/v1/chats?page_size=50',
    headers={'Authorization': f'Bearer {token}'})
items = json.loads(urllib.request.urlopen(req2).read()).get('data', {}).get('items', [])
for c in items:
    print(f'  [{c.get(\"chat_type\",\"?\")}]  chat_id={c[\"chat_id\"]}  name=\"{c.get(\"name\",\"?\")\}"  members={c.get(\"member_count\",\"?\")}')
"
```

Show the output to the user and suggest the most appropriate one. If there is only
one chat, propose it directly.

**Note on DM vs group chats:** Both DM chats and group chats can work as `FEISHU_HOME_CHANNEL`. Group chats are preferred for multi-user scenarios or when you want notifications visible to a team. DM chats work fine for single-user setups — cron delivery and system notifications are sent successfully to either type. Use the `chat_type`/`chat_mode` columns from the chat list to distinguish them.

To get detailed info on a specific chat, pass its chat_id as an argument:

```bash
python3 /opt/data/skills/autonomous-ai-agents/gateway-platform-troubleshooting/scripts/list-feishu-chats.py oc_xxx
```

Save with:

```bash
echo 'FEISHU_HOME_CHANNEL=oc_xxxxx' >> /opt/data/.env
```

## Post-Setup: Verify the Bot Responds

After restarting the gateway, verify by checking gateway logs — do not just ask
the user to test:

```bash
grep 'feishu' /opt/data/logs/gateway.log | tail -10
```

Expected working pattern:
```
[Feishu] Received raw message type=text message_id=om_xxx
[Feishu] Inbound group message received: id=om_xxx type=text chat_id=oc_xxx
inbound message: platform=feishu user=ou_xxx chat=oc_xxx msg='hi'
response ready: platform=feishu chat=oc_xxx time=6.5s api_calls=1 response=22 chars
[Feishu] Sending response (22 chars) to oc_xxx
```

If the bot does not respond even after restarting, check whether the gateway log
shows `inbound message: platform=feishu ...` at all. If nothing appears, see
`references/feishu-no-inbound-events.md` for the event subscription checklist.

## Troubleshooting: Groups Work but DMs Don't

### Symptom

- @-mentioning the bot in a group chat → responds ✅
- Sending a direct message to the bot → no response ❌
- Gateway log shows group `inbound message` entries, but **no DM entries at all**

### Step 1: Check the Gateway Log Level

Run this first to determine whether DM events are reaching the WebSocket:

```bash
grep 'feishu' /opt/data/logs/gateway.log | grep -E 'Received raw|Inbound dm|Inbound group' | tail -10
```

You will see one of:

| Log Pattern | Meaning | Go to |
|------------|---------|-------|
| `Inbound group message received` BUT **no** `Inbound dm message received` | Feishu Open Platform is not sending DM events at all | **Step 2** |
| `Inbound dm message received` AND `inbound message: platform=feishu` appears for DMs | Events arrive but something blocks them downstream | **Step 3** |

### Step 2: DM Events Never Arrive — Feishu Platform Does Not Forward Them

**Root cause:** The Feishu app on the Open Platform does NOT have the **私聊 (private chat) capability** enabled for the bot. The WebSocket connects successfully and receives group messages, but Feishu's server never forwards DM events because the bot app hasn't declared support for private chats.

**This is NOT a .env config issue** — no amount of `FEISHU_ALLOW_ALL_USERS` or `FEISHU_ALLOWED_USERS` tweaking will fix it, because those env vars are evaluated after the event arrives. The Feishu adapter's `_admit()` function (at `adapter.py` line 4119-4120) **always admits DMs** (`return None` for `not is_group`). If no DM event arrives at all, the admission gate is never reached.

**Fix (in Feishu Developer Console → https://open.feishu.cn → your app):**

1. **添加能力 → 机器人** — ensure the bot capability is enabled
2. **Under 机器人 settings** — check that **私聊** (private chat mode) is selected (not just 群聊/group chat). The specific permission to add in 权限管理 is **"获取单聊、群组信息"** (Get single chat, group info) — this enables the bot to both send and receive DMs.
3. **权限管理** — add the `im:message` permission scope. The bot needs at minimum:
   - `im:message` — to receive and send messages
   - `im:chat` — to read chat info and list chats
   - `contact:contact.employee_id:readonly` — optional, to resolve user IDs
4. **版本管理与发布** — **CRITICAL:** publish a new version for the changes to take effect in production. Draft changes alone do nothing.

After publishing, restart the gateway and test by sending a DM. The log should now show:
```
[Feishu] Inbound dm message received: id=om_xxx type=text chat_id=oc_xxx sender=user:ou_xxx
```

Do NOT conflate this with the "no inbound events at all" scenario (`feishu-no-inbound-events.md`). If group messages arrive, the event subscription and app activation are already correct. The missing piece is specifically the private chat capability declaration.

### Step 3: DM Events Arrive but Bot Doesn't Respond — Config Issue

Check `.env` for the DM authorization settings:

```bash
grep -E 'FEISHU_ALLOW_ALL_USERS|FEISHU_ALLOWED_USERS|FEISHU_GROUP_POLICY' /opt/data/.env
```

**Root cause:** The DM authorization and group policy are governed by **separate** env vars:

```ini
FEISHU_GROUP_POLICY=open               # Groups work for anyone → @mentions succeed
FEISHU_ALLOW_ALL_USERS=false           # DMs require authorization
FEISHU_ALLOWED_USERS=                  # Empty allowlist → NOBODY authorized for DMs
```

The group policy (`open`) only controls @mention behavior and does NOT influence DM access. DM access is independently gated by `ALLOW_ALL_USERS` + `ALLOWED_USERS`. With `ALLOW_ALL_USERS=false` and an empty allowlist, **every user is denied DM access**.

### Fix

Option A — Allow everyone to DM:
```bash
sed -i 's/FEISHU_ALLOW_ALL_USERS=false/FEISHU_ALLOW_ALL_USERS=true/' /opt/data/.env
```

Option B — Allow only specific users (find their open_id in the `sender=user:ou_xxx` portion of gateway log group messages):
```bash
sed -i 's/FEISHU_ALLOWED_USERS=$/FEISHU_ALLOWED_USERS=ou_ca1ca2.../' /opt/data/.env
# leave FEISHU_ALLOW_ALL_USERS=false
```

Option C — Re-run the interactive wizard to set pairing mode (users must then be approved via `hermes pairing approve`):
```bash
hermes gateway setup
```

**After any change, restart the gateway:**
```bash
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/
sleep 8
grep 'feishu' /opt/data/logs/gateway.log | tail -10
```

Verify DMs work by sending a DM to the bot and checking logs for:
```
[Feishu] inbound from=<open_id> type=dm media=0
```

### How to Distinguish from No-Inbound-Events

| Symptom | Likely Cause |
|---------|-------------|
| No inbound events at all (neither group nor DM) | Event subscription / app publishing issue → see `feishu-no-inbound-events.md` |
| Groups work, DMs don't | DM authorization (`ALLOW_ALL_USERS` / `ALLOWED_USERS`) → this section |
| Groups work, DMs show `inbound` in logs but bot doesn't respond | Model config / agent issue, not gateway |

## Important Notes

- **Do NOT ask the user to confirm config entries you can verify yourself.** Once
  they have answered the multi-choice questions, the exact yaml/env entries are
  determinable from the code. Apply and verify immediately without asking "is this
  correct?" for each derived entry. This is a deliberate workflow principle — looping
  back for confirmation on everything wastes the user's attention and erodes trust
  that you can handle routine setup autonomously.
- The `patch` tool refuses to write to Hermes config.yaml at `/opt/data/config.yaml`
  — use `hermes config set` instead.
- Env vars in `.env` are read by `hermes_cli` (python-dotenv) and by the
  `hermes gateway run` s6 script (custom bash parser). The s6 script has a hardcoded
  allowlist — env vars not in it are silently dropped. Check
  `cat /proc/$(pgrep -f "hermes gateway run")/environ | tr '\0' '\n' | grep FEISHU_`
  to verify after starting the gateway.
- The `activate_status` field returned by `/open-apis/bot/v3/info` can be misleading.
  A value of `2` does NOT necessarily mean the bot will not work — the bot in this
  session had `activate_status: 2` and functioned normally. Use gateway logs as the
  definitive verification, not the API status field.



