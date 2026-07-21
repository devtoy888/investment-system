# Feishu Bot Creation Steps (Multi-Profile Multiplexing)

Create a new Feishu bot for each Hermes profile in a multiplexing setup.

## Feishu Open Platform

1. Go to [https://open.feishu.cn/](https://open.feishu.cn/) → Enterprise account login
2. Top right → **"Create App"** → **"Enterprise Self-built App"**
3. App name: descriptive (e.g. "LLM Wiki", "Investment Bot")
4. App description: short purpose statement

## Credentials

Left sidebar → **"Credentials & Basic Info"**

```
App ID:     cli_xxx...          → FEISHU_APP_ID
App Secret: ****************    → FEISHU_APP_SECRET (click "View" to copy)
```

## Bot Capability

Left sidebar → **"App Features" → "Bot"** → Toggle **"Enable Bot"** ON ✅

## Permissions

Left sidebar → **"Permissions"** → Search and add:

| Permission code | Required? | Purpose |
|:----------------|:---------:|:--------|
| `im:message` | ✅ Must | Receive messages |
| `im:message:send_as_bot` | ✅ Must | Send messages as bot |
| `im:resource` | ⚠️ Recommended | Get images/files from messages |
| `im:chat` | Optional | Get group info |

Click **"Batch Add"**

## Events & Callbacks

Left sidebar → **"Events & Callbacks"**:

**① Connection mode**
- Select **"Long Connection (WebSocket)"** (长连接 WebSocket)
- ⚠️ **Do NOT fill in callback URL** — not needed for websocket mode

**② Subscribe to events**
Click **"Add Event"** → Search and add:

```
im.message.receive_v1    ← Required! Without this, bot won't receive messages
```

Other events (group join/leave, reactions, etc.) are not needed by Hermes.

## Publish

Left sidebar → **"Version Management & Release" → "Create Version"**

| Field | Value |
|:------|:------|
| Version | `1.0.0` |
| Notes | `Initial release` |

→ **"Save" → "Apply for Release"** → Admin approval (or self-approve if admin)

## .env Configuration

In the new profile's `.env`, add/modify:

```bash
FEISHU_APP_ID=cli_xxx...new          ← New bot's App ID
FEISHU_APP_SECRET=***                ← New bot's App Secret
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOW_ALL_USERS=false
FEISHU_ALLOWED_USERS=ou_xxx          ← Same user's Open ID (same person across bots)
FEISHU_GROUP_POLICY=open
FEISHU_HOME_CHANNEL=                 ← Will be auto-set on first message
FEISHU_HOME_CHANNEL_THREAD_ID=
```

## Verification

- Find the new bot in Feishu app contacts (search bot name)
- Send a message → should receive a reply
- Check gateway logs: `grep "feishu" /opt/data/logs/gateway.log | tail -5`

### 🔍 Finding the Correct OpenID

When the bot doesn't respond despite all config being correct, check if the user's OpenID differs between bots:

1. **Check the gateway log** for the actual sender OpenID:
   ```bash
   grep "Unauthorized user\|Inbound dm" /opt/data/profiles/<name>/logs/gateway.log
   # Example: Unauthorized user: ou_3f77589516f5edfbaf89d5c23c8355a3
   ```
2. **Update ALLOWED_USERS** with the actual OpenID from the log:
   ```bash
   sed -i 's/FEISHU_ALLOWED_USERS=.*/FEISHU_ALLOWED_USERS=ou_<actual-id>/' /opt/data/profiles/<name>/.env
   ```
3. Restart the profile's gateway

## Pitfalls

- **Permissions only take effect after publishing** — configuring permissions is not enough
- **Events subscription is mandatory** — without `im.message.receive_v1`, the bot won't see any messages
- **FEISHU_HOME_CHANNEL** is auto-set on first interaction — don't try to pre-fill it unless you know the chat ID
- **⚠️ OpenID may differ across bots** — The same user in the same Feishu tenant may get a different `ou_xxx` OpenID for different apps (bots). Do NOT assume the OpenID from the first bot works for the second bot. Check the gateway log for the actual sender ID when the user sends a message.
