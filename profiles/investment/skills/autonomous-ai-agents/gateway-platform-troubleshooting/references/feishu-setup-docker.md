# Feishu Gateway Setup (Docker Container)

Environment-specific details for setting up the Feishu/Lark platform adapter in this Docker-based Hermes deployment.

## Current Config

**Credentials** (in `/opt/data/.env`):
```
FEISHU_APP_ID=cli_aabdd9b86278dcd7
FEISHU_APP_SECRET=QGLMdv...hhb5          (redacted)
FEISHU_DOMAIN=feishu                      # 'feishu' for Chinese mainland, 'lark' for international
FEISHU_CONNECTION_MODE=websocket          # WebSocket (push) mode; alternative: webhook
```

**Connection mode**: `websocket` — the gateway maintains a persistent WebSocket connection to Feishu's event push service. The bot receives events in real-time without needing a public HTTPS endpoint.

## Complete Env Vars

A fully-configured `.env` for Feishu (domestic China version):

```env
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=your_secret
FEISHU_DOMAIN=feishu                      # 'feishu' for Chinese mainland, 'lark' for international
FEISHU_CONNECTION_MODE=websocket          # websocket (recommended) or webhook
FEISHU_REQUIRE_MENTION=true               # Require @mention in group chats (default: true)
FEISHU_GROUP_POLICY=allowlist             # open | allowlist | disabled
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy        # Comma-separated open_ids for allowlist
FEISHU_HOME_CHANNEL=oc_xxx                # Chat ID for cron/notification delivery
```

**Important:** After adding any `FEISHU_*` env vars to `.env`, you must also add them to the **s6 env passthrough allowlist** in `/run/service/gateway-default/run` — see the 🔥 Critical section in the main SKILL.md.

## ⚠️ Config Wiring Trap

`FEISHU_*` env vars in `.env` alone are **not sufficient** to enable Feishu. The platform must also be wired into `config.yaml`:

1. **Platform switch** — `gateway.platforms.feishu.enabled: true` (or root `platforms.feishu.enabled`)
2. **Toolset** — `platform_toolsets.feishu: [hermes-feishu]`
3. **Plugin** — `plugins.enabled: [feishu-platform]` (add to existing list, don't replace it)

The `hermes gateway setup` wizard handles all three automatically. If you manually edit `.env` without running the wizard, you must add these entries yourself or the platform will appear "configured" in status checks but never actually connect.

## ⚠️ Activation Status Trap

The WebSocket connection will succeed (`[Feishu] Connected in websocket mode`) even when the app has **never been published**. Feishu's WebSocket gateway accepts valid credentials, but **does not forward any message events** until `activate_status=1`.

**Diagnose with the API test in `references/feishu-no-inbound-events.md`.** Key interpretation:

| activate_status | Meaning | What to do |
|----------------|---------|------------|
| `1` | ✅ Active — events flowing | Message the bot in Feishu |
| `2` | ❌ Not activated — events blocked | Go to open.feishu.cn → Publish button → Create version → Submit |

This is the #1 support issue for Feishu bots. Adding permissions and subscribing to events only modifies the **draft** — none of it takes effect until a version is published.

## Key Paths

| Path | Purpose |
|------|---------|
| `/opt/data/.env` | Feishu credentials (FEISHU_APP_ID, FEISHU_APP_SECRET, etc.) |
| `/opt/data/.feishu-deps/` | Feishu Python dependencies (lark-oapi) installed via `--target` |
| `/run/service/gateway-default/run` | s6 gateway service run script (PYTHONPATH added here) |
| `/opt/data/logs/gateway.log` | Gateway logs — check for `feishu` connect/disconnect messages |
| `/opt/data/channel_directory.json` | Platform chat routing (feishu key exists) |
| `/opt/data/feishu_seen_message_ids.json` | Dedup cache — empty `{}` means zero inbound events ever received |
| `/opt/data/.local/state/hermes/gateway-locks/feishu-app-id-*.lock` | Gateway instance lock for Feishu app (prevents concurrent connections) |

## Log Patterns for Feishu

**Successful connection:**
```
Connecting to feishu...
[Feishu] Connected in websocket mode (feishu)
✓ feishu connected
Gateway running with 2 platform(s)
```

**Missing dependencies (before fix):**
```
Platform 'Feishu / Lark' requirements not met (pip install 'hermes-agent[feishu]')
Platform 'feishu' is registered but adapter creation failed (check dependencies and config)
No adapter available for feishu
```

## Restart Sequence

```bash
# 1. Find s6-svc
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)

# 2. Restart
"$S6_SVC" -r /run/service/gateway-default/

# 3. Wait and verify
sleep 8
grep -i "feishu\|platform\|Connected" /opt/data/logs/gateway.log | tail -10
```
