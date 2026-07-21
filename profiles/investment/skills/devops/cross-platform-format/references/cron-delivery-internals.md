# Cron Delivery Internals (Cross-Platform)

## MEDIA: Protocol Delivery Flow

When a cron job's agent outputs `MEDIA:/path/to/file.png`, the cron scheduler processes it as follows:

### 1. Extraction (`cron/scheduler.py`, line 758-761)
```python
from gateway.platforms.base import BasePlatformAdapter
media_files, cleaned_delivery_content = BasePlatformAdapter.extract_media(delivery_content)
media_files = BasePlatformAdapter.filter_media_delivery_paths(media_files)
```
- `extract_media()` scans for `MEDIA:<path>` tags using regex `[`"']?MEDIA:\s*\S+`
- Returns `[(path, is_voice), ...]` + text content with MEDIA: tags stripped
- `filter_media_delivery_paths()` validates files exist on disk and checks extensions

### 2. Live Adapter Path (line 814-885)
- Tries the gateway's live `runtime_adapter.send()` first
- For **DingTalk**: calls `adapter.send(chat_id, text, ...)` which uses `_session_webhooks` dict → fails if no incoming message received → falls through to standalone
- For **QQ/WeChat/Feishu**: works directly via the live adapter

### 3. Text Delivery via Adapter (line 817-825)
```python
future = safe_schedule_threadsafe(
    runtime_adapter.send(chat_id, text_to_send, metadata=send_metadata),
    loop,
)
```
Text is sent as-is (MEDIA: tags already stripped).

### 4. Media Delivery via Adapter (line 863-873, `_send_media_via_adapter` at line 657)
```python
_send_media_via_adapter(runtime_adapter, chat_id, media_files, ...)
```
For each media file:
- `.png/.jpg/.gif` → `adapter.send_image_file(chat_id, image_path=path, ...)`
- `.mp3/.wav` → `adapter.send_voice(chat_id, audio_path=path, ...)`
- `.mp4` → `adapter.send_video(chat_id, video_path=path, ...)`
- Other → `adapter.send_document(chat_id, file_path=path, ...)`

### 5. Standalone Fallback Path (line 887-916)
When live adapter fails (e.g. DingTalk no session_webhook):
```python
coro = _send_to_platform(platform, pconfig, chat_id, cleaned_delivery_content, ..., media_files=media_files)
```
- **QQ Bot**: `_send_qqbot(pconfig, chat_id, chunk)` — uses HTTP API
- **WeChat (iLink)**: `_send_weixin(pconfig, chat_id, message, media_files)` — uses iLink API
- **DingTalk**: `_registry_standalone_send("dingtalk", ...)` → uses `DINGTALK_WEBHOOK_URL` (static webhook, ignores chat_id)
- **Feishu**: `_registry_standalone_send("feishu", ...)` → uses Feishu API

### Platform send_image_file Support

| Platform | File | Line | Works? |
|----------|------|------|--------|
| QQ Bot | `gateway/platforms/qqbot/adapter.py` | 2777 | ✅ Sends native image |
| WeChat (iLink) | `gateway/platforms/weixin.py` | 1983 | ✅ Sends native image |
| DingTalk | `plugins/platforms/dingtalk/adapter.py` | 964 | ❌ **Returns error.** Only text/markdown via session webhook. Use `![image](URL)` in markdown body instead. |
| Feishu | `plugins/platforms/feishu/adapter.py` | 2103 | ✅ Sends native image |

## Platform Delivery Quirks

### DingTalk Stream Mode
- Connects via `DINGTALK_CLIENT_ID` + `DINGTALK_CLIENT_SECRET` (Stream Mode WebSocket)
- `_session_webhooks: Dict[chat_id, (webhook_url, expiry)]` populated on inbound messages
- No incoming message → `send()` returns `SendResult(success=False, error="No valid session_webhook available")`
- Standalone fallback uses `DINGTALK_WEBHOOK_URL` (custom robot webhook) — sends to a fixed group, chat_id is ignored
- After gateway restart, must receive a message in the target group before cron delivery works

### Custom Robot Webhook (DINGTALK_WEBHOOK_URL)
- Format: `https://oapi.dingtalk.com/robot/send?access_token=xxx`
- Used as fallback when live adapter path fails
- Always sends to whatever group the webhook was created for — the chat_id in cron deliver field is NOT used
- Webhook security settings (keyword, IP whitelist) may block messages
- Token never expires but can be reset in DingTalk admin panel

## Cron Timeout Behavior
- 180s hard limit (`cron/scheduler.py`)
- Agent process is killed with `SIGTERM` → `Errno 32: Broken pipe` if it was mid-write to stdout
- Pre-script data collection (`--script`) runs BEFORE the agent and counts toward the 180s
- Total time = script time + agent time. Script typically takes 10-15s, agent 20-40s = ~30-55s total

## Debugging Failed Deliveries
1. `cronjob list` — check `last_status`, `last_delivery_error`
2. `grep "3726bb16751c\|Broken pipe\|No valid session_webhook\|delivery error" /opt/data/logs/default/gateway.log`
3. Read local cron output: `cat /opt/data/cron/output/<job_id>/<timestamp>.md`
4. Check cron output directory: `ls -lt /opt/data/cron/output/<job_id>/`
