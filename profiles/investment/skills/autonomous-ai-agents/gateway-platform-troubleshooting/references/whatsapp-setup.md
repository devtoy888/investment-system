# WhatsApp (Baileys Bridge) Setup

Full reference for configuring WhatsApp via the Baileys bridge in a Docker/read-only Hermes environment.

## Architecture

Unlike Chinese platforms which use Python adapters, the WhatsApp bridge runs as a **standalone Node.js process** using the `@whiskeysockets/baileys` library. It emulates WhatsApp Web's protocol to authenticate and exchange messages.

```
Python Gateway  <--HTTP-->  Node.js Bridge (Baileys)  <--WebSocket-->  WhatsApp
    (hermes)                  (bridge.js on port 30xx)                     (servers)
```

## Bridge Source & Mirroring

The bridge source lives at `/opt/hermes/scripts/whatsapp-bridge/`. On first use, `resolve_whatsapp_bridge_dir()` checks if the install tree is writable. If not (Docker), it copies the source to `HERMES_HOME/scripts/whatsapp-bridge/` and returns that path for npm to write into.

**If the auto-mirror fails**, do it manually:
```bash
mkdir -p /opt/data/scripts
cp -r /opt/hermes/scripts/whatsapp-bridge /opt/data/scripts/
chmod -R u+w /opt/data/scripts/whatsapp-bridge/
cd /opt/data/scripts/whatsapp-bridge
npm install --no-fund --no-audit --progress=false
# 144 packages expected (Baileys + express + pino + qrcode-terminal)
```

### PYTHONPATH Conflict

When `PYTHONPATH` is set (e.g., to `/opt/data/.feishu-deps` for Feishu dependencies), the gateway's `resolve_whatsapp_bridge_dir()` may resolve the bridge path relative to the `PYTHONPATH` tree instead of the actual install or `HERMES_HOME` tree. This produces:

```
WARNING gateway.platforms.whatsapp: [Whatsapp] Bridge script not found: /opt/data/.feishu-deps/scripts/whatsapp-bridge/bridge.js
```

**Fix** — Copy the bridge into the PYTHONPATH directory:
```bash
mkdir -p /opt/data/.feishu-deps/scripts
cp -r /opt/data/scripts/whatsapp-bridge /opt/data/.feishu-deps/scripts/
```

Then restart the gateway. The bridge will be found on the PYTHONPATH.

## Dependencies

The bridge's `package.json` pins Baileys to a specific git commit:
```json
"@whiskeysockets/baileys": "WhiskeySockets/Baileys#01047debd81beb20da7b7779b08edcb06aa03770"
```

Other deps: `express`, `qrcode-terminal`, `pino`.

## Configuration (`.env`)

Set by `hermes whatsapp` wizard:
```
WHATSAPP_MODE=bot
WHATSAPP_ALLOWED_USERS=8618135070938,8618192361520
```

Optional overrides:
```
WHATSAPP_ALLOW_ALL_USERS=true    # Bypass allowlist (same as WHATSAPP_ALLOWED_USERS=*)
```

## Bridge Modes

The bridge distinguishes `bot` vs `self-chat`:
- **bot**: Listens for messages from any `WHATSAPP_ALLOWED_USERS` number
- **self-chat**: Only processes messages the user sends to themselves

Mode is set via `WHATSAPP_MODE` env var and passed to bridge.js when spawned.

### Switching Between Modes (bot ↔ self-chat)

If you need to switch from bot mode to self-chat (or vice versa):

1. **Update the mode in `.env`:**
   ```bash
   sed -i 's/WHATSAPP_MODE=.*/WHATSAPP_MODE=self-chat/' /opt/data/.env   # or "bot"
   ```

2. **Update allowed users** (self-chat typically uses `*`):
   ```bash
   sed -i 's/WHATSAPP_ALLOWED_USERS=.*/WHATSAPP_ALLOWED_USERS=*/' /opt/data/.env
   ```

3. **Clear stale session** — old session data is incompatible with the new mode:
   ```bash
   rm -rf /opt/data/whatsapp/session/*
   ```

4. **Re-pair** with fresh QR code:
   ```bash
   hermes whatsapp
   ```

5. **Restart gateway**:
   ```bash
   /package/admin/s6-*/command/s6-svc -r /run/service/gateway-default/
   ```

## QR Code Session Pairing

The Baileys library generates a pairing code on first connection (when no session files exist). The `qrcode-terminal` npm package renders it as ASCII art. After scanning with WhatsApp, `creds.json` and other session files are written to the session directory.

**Session path:** `HERMES_HOME/platforms/whatsapp/session/` (or explicitly `SESSION_DIR` env var)

**Session files include:**
- `creds.json` — encryption keys, device credentials
- `pre-key/` — Signal Protocol pre-keys
- `sender-key/` — sender key records
- `app-state-sync-*` — WhatsApp app state

**Session persistence:** Sessions survive gateway restarts. If the session is invalidated (phone reset, manual unlink, WhatsApp protocol update), re-run `hermes whatsapp`.

## QR Code Display Workaround

When the terminal rendering of ASCII QR codes is unscannable (common via chat interfaces):

### Step 1: Patch bridge.js to save raw QR data

In `/opt/data/scripts/whatsapp-bridge/bridge.js`, add inside the `if (qr) {` block:

```javascript
try { writeFileSync('/opt/data/whatsapp/qr-code.txt', qr, 'utf-8'); } catch(e) {}
```

`writeFileSync` is already imported at the top of bridge.js.

### Step 2: Generate a proper QR image

```bash
# Read the raw pairing code
QR_DATA=$(cat /opt/data/whatsapp/qr-code.txt)

# Generate PNG via Python qrcode library
python3 -c "
import qrcode, base64
from io import BytesIO

qr_data = open('/opt/data/whatsapp/qr-code.txt').read().strip()
qr = qrcode.QRCode(box_size=10, border=4)
qr.add_data(qr_data)
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')

# Save PNG
img.save('/opt/data/whatsapp/qr-code.png')

# Create HTML with embedded base64
buf = BytesIO()
img.save(buf, format='PNG')
b64 = base64.b64encode(buf.getvalue()).decode()
with open('/opt/data/whatsapp/qr-code.html', 'w') as f:
    f.write(f'''<!DOCTYPE html>
<html><head><meta charset=\"utf-8\"><title>WhatsApp QR</title></head>
<body style=\"display:flex;justify-content:center;align-items:center;min-height:100vh;background:#333\">
<div style=\"background:white;padding:40px;border-radius:16px;text-align:center\">
<h2>📱 WhatsApp QR</h2>
<img src=\"data:image/png;base64,{b64}\" style=\"max-width:100%\"/>
<p style=\"color:#666\">Open WhatsApp → Settings → Linked Devices → Link a Device</p>
</div></body></html>''')
print(f'HTML: /opt/data/whatsapp/qr-code.html')
"
```

### Step 3: Serve the file

```bash
# Quick HTTP server
cd /opt/data && python3 -m http.server 9120
# Then visit http://<host>:9120/qr-whatsapp.html
```

### Step 4: Provide the data URL or upload to image host

The HTML file embeds the QR as a base64 data URI. Copy the `src` attribute value from the `<img>` tag and paste it into a browser address bar for instant QR display.

**For Cloudflare Tunnel / remote deployments** where the user can't reach the container's IP:
```bash
# Upload to a free temporary image host
curl -s -F "file=@/opt/data/whatsapp/qr-code.png" https://tmpfiles.org/api/v1/upload
# Returns a URL like: https://tmpfiles.org/xxxxx/qr-code.png
# Share this URL with the user to view the QR in their browser
```

## Running `hermes whatsapp` in Non-Interactive Mode

Since the setup wizard is interactive, use the PTY+background+process pattern:

```bash
# Start
terminal(command="hermes whatsapp", pty=true, background=true)
# Session ID returned: e.g. proc_abc123

# Wait for prompt, submit choice
process(action="poll", session_id="proc_abc123")
process(action="submit", session_id="proc_abc123", data="1")  # 1=bot, 2=self-chat

# Enter allowed phone numbers
process(action="submit", session_id="proc_abc123", data="8618135070938,8618192361520")

# If already configured and asked "Update allowed users?", answer "n"
process(action="submit", session_id="proc_abc123", data="n")
```

## Handling Stale/Empty Sessions

If the session directory exists but is empty, Baileys will generate a new QR code. Delete it to force fresh pairing:
```bash
rm -rf /opt/data/whatsapp/session/
```

If a partial/corrupt session exists, remove `creds.json` only:
```bash
rm /opt/data/whatsapp/session/creds.json
```

## Self-Chat Mode Bug: Messages Ignored with `self_chat_mode_rejects_non_self`

**Symptom:** In self-chat mode, messages sent to yourself produce no response. Gateway logs show:
```
{"event":"ignored","reason":"self_chat_mode_rejects_non_self","chatId":"8618135070938@s.whatsapp.net","senderId":"8618135070938@s.whatsapp.net"}
```

**Root cause:** WhatsApp delivers self-chat messages with `fromMe=false` when they originate from the phone rather than the bridge. The original bridge code unconditionally rejected all `!fromMe` messages in self-chat mode, even when the sender was the user's own number.

**Fix:** In the bridge script (`bridge.js`), modify the `!msg.key.fromMe` block in self-chat mode to check if the sender matches the user's own number before rejecting:

```javascript
// In /opt/data/scripts/whatsapp-bridge/bridge.js (or wherever the bridge lives)
if (!msg.key.fromMe) {
  if (WHATSAPP_MODE === 'self-chat') {
    // Allow messages from your own number that arrive as !fromMe
    const myNumber = (sock.user?.id || '').replace(/:.*@/, '@').replace(/@.*/, '');
    const myLid = (sock.user?.lid || '').replace(/:.*@/, '@').replace(/@.*/, '');
    const senderNumber = senderId.replace(/@.*/, '');
    const isOwnMessage = (myNumber && senderNumber === myNumber) || (myLid && senderNumber === myLid);
    if (!isOwnMessage) {
      // Reject stranger DMs
      continue;
    }
    // Fall through — own message in self-chat, process it
  }
  // ... rest of the handler
}
```

After patching, sync the fix to all copies and restart the gateway:
```bash
cp /opt/data/scripts/whatsapp-bridge/bridge.js /opt/data/.feishu-deps/scripts/whatsapp-bridge/bridge.js
/package/admin/s6-*/command/s6-svc -r /run/service/gateway-default/
```

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| ✗ Bridge script not found at .../.feishu-deps/... | PYTHONPATH causes resolve_whatsapp_bridge_dir() to look in wrong tree | Copy bridge to PYTHONPATH dir: `mkdir -p /opt/data/.feishu-deps/scripts && cp -r /opt/data/scripts/whatsapp-bridge /opt/data/.feishu-deps/scripts/` |
| `QR code not scanning` | Terminal width <60 cols, or unicode support | Generate HTML/PNG workaround (see above) |
| `Bridge crashes on start` | Node.js < v18 or npm deps missing | `node --version` + re-run npm install |
| `Logged out unexpectedly` | Long inactivity, phone offline | Re-run `hermes whatsapp` to re-pair |
| `Messages not received` | `WHATSAPP_ALLOWED_USERS` doesn't match sender's number | Verify number format (country code, no +) |
| `Bridge exited with code 0 immediately` | Session already exists and is valid; bridge starts in background via gateway | Check gateway logs: `grep whatsapp /opt/data/logs/gateway.log` |
| `Auth fails after WhatsApp update` | WhatsApp protocol change broke Baileys | Update Hermes to get latest bridge, re-pair |
| `无法关联设备 (Can't link device)` | Stale/corrupt session data from previous pairing attempt, or device already linked to another instance | 1) Unlink old devices in WhatsApp → Settings → Linked Devices 2) `rm -rf /opt/data/whatsapp/session/*` 3) Also clean `.feishu-deps` copy: `rm -rf /opt/data/.feishu-deps/scripts/whatsapp-bridge/session/*` 4) Generate fresh QR via `hermes whatsapp` |
| `QR expired or stale` | QR codes last ~20 seconds | Regenerate by re-running `hermes whatsapp`
| `npm install fails with EACCES` | Copied files have no write permission | `chmod -R u+w /opt/data/scripts/whatsapp-bridge/` |

## Key Files & Paths

| File | Purpose |
|------|---------|
| `/opt/hermes/scripts/whatsapp-bridge/bridge.js` | Main bridge source (read-only in Docker) |
| `/opt/data/scripts/whatsapp-bridge/` | Mirrored bridge source (writable) |
| `/opt/data/scripts/whatsapp-bridge/node_modules/` | npm dependencies |
| `/opt/data/whatsapp/session/` | Baileys session data (persist across restarts) |
| `/opt/data/whatsapp/qr-code.txt` | Raw QR pairing code (after patching bridge.js) |
| `/opt/data/whatsapp/qr-code.html` | HTML page with embedded QR image |
| `/opt/data/.env` | WHATSAPP_MODE, WHATSAPP_ALLOWED_USERS |
