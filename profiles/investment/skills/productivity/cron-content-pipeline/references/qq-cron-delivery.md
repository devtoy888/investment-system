# QQ Cron Delivery Reliability

## Symptom

Cron job shows `last_status: ok` with `last_delivery_error: null`, cron session exists with complete assistant output, but the user reports not receiving the push on QQ.

## Known Occurrences

| Date | Job | Note |
|:----|:----|:-----|
| 2026-06-30 | 收盘复盘 (7a165a5748ce) | Multiple manual `run` triggers; session created, LLM output generated, status=ok, but user didn't receive |
| 2026-06-30 | 今日参考 (d7b0ad464c01) | Same pattern |
| 2026-07-02 | 收盘复盘 (7a165a5748ce) | Pre-script ran (data files updated 17:22), cron session with 1 message only (LLM step incomplete or delivery failed) |

## Root Causes Identified

### 1. LLM Step Incomplete (Session Has 1 Message Only)
The cron session exists but has `message_count: 1` — only the user prompt, no assistant response. The LLM was invoked but the model call failed or timed out. Check:
- Session DB: `message_count` field (1 = only prompt, > 1 = assistant responded)
- `bookend_end` array in session_search: empty = no completed output

### 2. Gateway Restart Race Condition
If the Gateway is restarted while a cron job's agent is finishing, the delivery futures fail with `cannot schedule new futures after interpreter shutdown`. The session has complete output but delivery fails.

### 3. Silent Delivery Failure (Status=ok, No Error)
Most concerning pattern: `last_status=ok`, no delivery error, session has complete LLM output, but QQ never receives it. Gateway logs show no QQ-related delivery lines for cron jobs (gateway.log only logs `delivered to` for interactive sessions, not cron deliveries).

## Debugging Checklist

1. **Check session completeness:** `session_search(query="cron_<job_id_prefix>", sort="newest")` — look for `bookend_end` content and `message_count`
2. **Check cron list:** `cronjob(action='list')` — look at `last_status` and `last_delivery_error`
3. **Check data file timestamps:** `ls -la /tmp/fund_data/_closing_*.txt` — do they show recent timestamps? If not, the pre-script didn't run
4. **Check gateway log:** `grep -i "qq\|qqbot\|deliver\|error" /opt/data/logs/gateways/default/current | tail -20`
5. **Re-trigger:** `cronjob(action='run', job_id='<id>')` — if the gateway was restarted, a second run usually delivers successfully

## Mitigation

- After any Gateway restart, wait 3 minutes before triggering cron test runs
- After triggering a cron run, verify via session_search that the assistant produced output (not just the user prompt)
- If `message_count=1`, the LLM step failed — re-trigger the run
- For scheduled jobs, the next day's auto-run usually recovers (the scheduler was down during upgrade, next tick works)
