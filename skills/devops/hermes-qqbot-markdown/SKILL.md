---
name: hermes-qqbot-markdown
description: Diagnose and fix QQ bot markdown messages rendering as plain text when delivered through the Hermes gateway (cron deliver=qqbot or agent replies). Covers the real root cause (Hermes truncate_message splitting long messages and breaking markdown structure), the bare-payload direct-send workaround, and the 0.18.2 provider-name change (custom:agnes -> agnes) that causes HTTP 422.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, qqbot, markdown, gateway, message-delivery, debugging]
---

# Hermes QQ Bot Markdown Rendering

## When to use this skill

The user reports that a message sent to their **QQ bot** shows as **plain text / "一坨纯文字"** instead of rendered markdown (titles, bold, lists, quotes not styled), even though QQ markdown is supposed to be supported.

Triggers:
- "qqbot markdown 没渲染" / "QQ 里显示是普通文本"
- A cron job with `deliver=qqbot` produces unstyled text
- Long agent-generated reports (daily briefings, digests) look broken in QQ

## CRITICAL — verify before assuming the bot can't do markdown

The #1 mistake is assuming the QQ bot account doesn't support markdown. **It almost certainly does.** QQ's official docs state custom Markdown is open to ALL bots (no template application needed) for C2C and group. Before any fix, PROVE the account works:

Send a bare payload directly (bypassing Hermes) using the bot's own credentials:

```python
import requests, os
env = {}
for line in open('/opt/data/.env'):          # or the profile's .env
    line = line.strip()
    if line.startswith('QQ_APP_ID=') or line.startswith('QQ_CLIENT_SECRET='):
        k, v = line.split('=', 1); env[k] = v.strip().strip('"')
APP_ID, SECRET = env['QQ_APP_ID'], env['QQ_CLIENT_SECRET']
tok = requests.post('https://bots.qq.com/app/getAppAccessToken',
                    json={'appId': APP_ID, 'clientSecret': SECRET}, timeout=10).json()['access_token']
OPENID = '<the user QQ C2C openid — same as their Hermes chat_id for that bot>'
md = '# 测试标题\n这是 **加粗**\n- 列表一\n- 列表二'
r = requests.post(f'https://api.sgroup.qq.com/v2/users/{OPENID}/messages',
                  headers={'Authorization': f'QQBot {tok}', 'Content-Type': 'application/json'},
                  json={'msg_type': 2, 'markdown': {'content': md}}, timeout=15)
print(r.status_code, r.text[:120])
```

If this **renders** in QQ → the account is fine; the bug is in Hermes's delivery path. If it does NOT render even with this, the account truly lacks markdown permission (rare — check the QQ open platform console).

> Verified fact this session: a 6645-char markdown sent via bare payload returned HTTP 200 and rendered. QQ imposes NO 4000-char hard limit on markdown — the 4000 cutoff is Hermes's own `MAX_MESSAGE_LENGTH`, not QQ's.

## Root cause (the real one)

Hermes's QQ adapter `send()` calls `truncate_message(content, MAX_MESSAGE_LENGTH)` where `MAX_MESSAGE_LENGTH = 4000` (`gateway/platforms/qqbot/constants.py`).

- If the message is **≤ 4000 chars**: returned as a single chunk → `_build_text_body` wraps it in `{"msg_type": 2, "markdown": {"content": ...}}` → **renders correctly**.
- If the message is **> 4000 chars**: `truncate_message` splits it on newlines/spaces into multiple chunks. Each chunk is re-sent through `_build_text_body` with `msg_type: 2`, BUT the split lands **mid-markdown-structure** (a `#` title cut in half, an unpaired `**`, a broken list). QQ receives structurally-broken markdown and **silently downgrades it to plain text**.

So: NOT an account limitation, NOT a syntax problem — it's Hermes's generic length-splitter destroying markdown integrity for long messages.

The adapter path (verified in source):
`adapter.send()` → `format_message()` (passes through when `markdown_support: true`) → `truncate_message(formatted, 4000)` → `_send_chunk` → `_send_c2c_text` → `_build_text_body` (markdown branch, `msg_type: 2`).

## Fixes

### Fix A — keep the message ≤ 4000 chars (simplest, no code change)
For agent-generated reports, constrain the prompt: "严格控制总篇幅 ≤ 3800 字符，确保单条 Markdown 不被拆分". This makes `truncate_message` return one chunk that renders. Persistent (prompt lives in state.db). Downside: loses ~30% content for long digests.

### Fix B — send bare payload directly from the script (best for scripts/cron)
For `no_agent` cron jobs or scripts, skip Hermes's `deliver=qqbot` entirely and POST the markdown yourself using the bot's `.env` credentials (the snippet above, or see `references/bare_payload_send.md`). This bypasses `truncate_message`. You control chunking: split on `***` or section boundaries, keep each chunk < 4000, and each chunk is still valid markdown. This is what made the OpenRouter free-model monitor render correctly.

Caveat: `.env` must not be hard-coded — read it from the file (Hermes loads it but doesn't export to env). See the references file for the exact read pattern. Never write `.env` (agent is forbidden).

### Fix C — raise MAX_MESSAGE_LENGTH (NOT recommended)
Editing `gateway/platforms/qqbot/constants.py` to e.g. 8000 would let long messages send whole. BUT `/opt/hermes` is a **read-only container image layer** — changes are lost on container rebuild/upgrade. Do not rely on this.

## Related 0.18.2 gotcha — provider name change

Symptom: cron job fails `HTTP 422: ...unknown variant` or `Unknown provider 'custom:agnes'`.

In Hermes **0.18.2**, `custom:agnes` (old `custom_providers` block style) is **invalid**. Agnes is now a top-level provider. Fix: set the cron/model override `provider` to `agnes` (not `custom:agnes`), `model` to `agnes-2.0-flash`, `base_url: null` (uses the `agnes:` block in config.yaml). Also remove any stray `reasoning_effort: minimal` from `config.yaml` personalities — `minimal` is not a valid OpenAI variant (use `low`/`medium`/`high`); an invalid value causes HTTP 422 `reasoning_effort: unknown variant`. Edit config via `hermes config set` (direct file writes to config.yaml are blocked by the agent guard).

## Verification checklist
1. Send bare payload (Fix B snippet) → confirm it renders in QQ. This isolates account vs delivery.
2. For agent reports: after a real cron run, check the user's QQ — confirm titles/lists/bold render.
3. Check `truncate_message` wasn't triggered: log line `Cron output truncated (NNNN chars)` in `logs/gateway.log` means the message exceeded 4000 and was split → fix A or B needed.
