# QQ Message Merging — Technical Reference

## Problem

The morning briefing (`run_morning.py`) generated 8–12 separate QQ messages for a single push. Each message carried one "card" section (外盘&A股指数, 量价分析, 板块热度, 持仓参考, KOL共识, 唐史主任观点, 小浣熊观点, RSS新闻, 深度解读…). User complained: "too many messages."

## Root Cause

Two‑layer splitting created fragmentation:

### Layer 1: stdout‑based card generation (`send_qqbot.py`)

`send_morning_cards.py` calls `send_card_with_tables()` 7–10 times. Each call in `send_qqbot.py` prints:
```
\n═══════════════════════════════════\n
## {title}\n\n{content}
```
to stdout. Sections are separated by `═══════════════════════════════════`.

### Layer 2: QQ API splitting (`send_qq_bot.py` → old behavior)

`send_markdown_in_chunks()` took the merged stdout and split it by the separator:
```python
# OLD: split by separator → each card = one message
sections = content.split("\n" + sep + "\n")
for section in sections:
    msg = f"## {title}\n\n{section}"
    # send as independent message
```

This turned 7–10 cards into 7–10 messages, plus any extra from status lines or over‑size splits. Total: **12+ messages**.

### Why sections were small

Each card section was only 500–2000 chars, well under QQ's 3800 limit. No single section needed splitting — but each became its own message anyway.

## Fix

**Single change in `/opt/data/scripts/send_qq_bot.py`:**

Replaced `send_markdown_in_chunks()` and removed the helper `_split_oversized()`.

### New behavior

1. Strip status/debug lines from the captured stdout (lines starting with `"OK "`, `"FAIL "`, `"All done"`, `"Morning cards done"`, `"————"`)
2. Keep separator lines as visual content within the message
3. Prepend one `## 📚 {title}\n\n` header
4. If total ≤ 3800 chars → **1 message**
5. If total > 3800 chars → split at paragraph boundaries, each ≤ 3800 chars
6. Add `_(📎 接上条)_` / `_(📎 续下条)_` markers on multi‑chunk deliveries

### Before/After

| Metric | Before | After |
|--------|--------|-------|
| Morning brief messages | 8–12 | 2–3 |
| Noon brief messages | 6–10 | 1–3 |
| Closing review messages | 6–10 | 1–3 |
| Status line contamination | "Morning cards done!" sent as message | Filtered |
| Redundant headers | Each message carried `## 财经早餐` | One header at start |

## Affected Files

| File | Change | Note |
|------|--------|------|
| `/opt/data/scripts/send_qq_bot.py` | Modified | `send_markdown_in_chunks()` rewritten; `_split_oversized()` removed |
| `/opt/data/scripts/run_morning.py` | None | Shares `send_qq_bot.py` |
| `/opt/data/scripts/run_noon.py` | None | Shares `send_qq_bot.py` |
| `/opt/data/scripts/run_closing.py` | None | Shares `send_qq_bot.py` |

## Verification

Test with simulated content (6 sections, 850 chars):
```
python3 -c "
from send_qq_bot import send_markdown_in_chunks
# Test with mock content — verify it sends as 1 message, not 6+
# Monitor stderr for 'sent N' in run_morning.py output
"
```

Real cron run verification:
```bash
hermes cron run d41a3db12dda  # morning brief job ID
# Check cron session for sent count via stderr
```

## Related

- `cron-content-pipeline` SKILL.md → "QQ Message Merging Strategy" section
- `/opt/data/scripts/send_qqbot.py` — the stdout‑based card output module (NOT to be confused with `send_qq_bot.py`)
- `references/qq-cron-delivery.md` — QQ delivery reliability debugging
