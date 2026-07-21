# DeepSeek Direct API Streaming Stalls in Cron Jobs

## Symptom

Cron job fails with `[Errno 32] Broken pipe` after 180s. All 3 retries fail.
The agent log shows:

```
Stream stale for 180s (threshold 180s) — no chunks received. model=deepseek-v4-flash
context=~XX,XXX tokens. Killing connection.
...
API call failed (attempt 1/3) error_type=ReadError summary=[Errno 32] Broken pipe
```

## Root Cause

**This is NOT the 3-min cron hard timeout.** The 180s is Hermes's stream-staleness detector (`chat_completion_helpers.stale_stream_threshold`) killing the HTTP streaming connection because the API accepted the TCP connection but sent **zero streaming chunks** for 180 seconds.

DeepSeek's direct API (`api.deepseek.com`) exhibits this behavior on large contexts (~17K+ tokens) at certain times of day (observed: 08:00-09:00 CST / 00:00-01:00 UTC). The same model/context works fine at other times or on retry.

## Key Patterns (Observed in Production — Jun 2026)

### Pattern A: Retry Succeeds (Nominal — most common)

| Attempt | Context | Latency | Outcome | Notes |
|---------|---------|---------|---------|-------|
| #1 | ~17,748 tokens | 180s (stale kill) | Broken pipe | First request to server per prompt hangs |
| #2 (retry) | ~19,044 tokens | 17.2s | ✅ Success | 89% prompt cache hit (17,024/19,044) |

The retry succeeds because DeepSeek's internal prompt cache has been populated by the first (failed) attempt. The second attempt routes to a different server instance or reuses cached KV cache.

### Pattern B: All 3 Retries Fail (Severe — observed 6/30/2026 08:00 CST)

| Attempt | Context | Latency | Outcome | Notes |
|---------|---------|---------|---------|-------|
| #1 | ~17,770 tokens | 180s (stale kill) | Broken pipe | Zero chunks, same as Pattern A |
| #2 | ~17,770 tokens | 180s (stale kill) | Broken pipe | Even retry hangs — no cache benefit |
| #3 | ~17,770 tokens | 180s (stale kill) | Broken pipe | All 3 fail identically |

Same job run at **10:00 CST** the same day: ✅ **17.4s, 89% cache hit** — one attempt, no stale stall at all. This eliminates the prompt content or connection setup as the root cause; the issue is specifically time-of-day server-side load on DeepSeek.

### Time-of-Day Sensitivity

| Time (CST) | Outcome | Context | Wall time |
|-----------|---------|---------|-----------|
| 08:00 (Jun 30) | ❌ 0/3 retries | ~17.7K tokens | 9min all fail |
| 10:00 (Jun 30) | ✅ single attempt | ~19K tokens | 17.4s |
| 08:00 (Jun 29) | ✅ retry #2 works | ~19K tokens | ~3.5min |

Hypothesis: DeepSeek's **08:00 CST peak** coincides with concurrent cron jobs (all daily jobs fire at 00:00 UTC = 08:00 CST). This is the busiest minute on the API, and large-context requests are the first to stall. Moving the cron job to 07:50 or using a retry-optimized approach resolves it.

### Concurrency Red Herring: What the Data Actually Shows

When two cron jobs share a DeepSeek provider, the **intuitive suspicion is concurrent requests overwhelming the API**. Tracing exact timestamps reveals a different picture:

```
行业技术日报 (17.7K tokens)           今日参考 (5.8K-7.7K tokens)
─────────────────────               ─────────────────────
00:01:09 → DeepSeek stream (stalls)
                                      00:03:00 → ✅ API #1: 1.8s
                                      00:03:03 → ✅ API #2: 2.8s
                                      00:03:31 → ✅ API #3: 21.1s
00:04:09 → ❌ Stale kill (180s)
```

**Key insight**: The large-context job was already stalling **before** the small-context job started. The small job made 3 successful calls to the same DeepSeek endpoint during the large job's stalled stream. This proves the issue is **not** API-level concurrency (rate limits, connection pool exhaustion) but something specific to how DeepSeek accepts but never starts processing a large-context stream at peak times.

**However**: Staggering the schedules (e.g. moving the large job to 07:50, keeping the small job at 08:00) still fixes the problem — likely because the large job now runs **before** the 08:00 congestion window, not because it avoids the other job.

## Comparison: With vs Without Skill Loading

| State | Context size | Result |
|-------|-------------|--------|
| `--skills agent-reach,cross-platform-format` | ~22,287 tokens | All 3 retries → Broken pipe |
| No skills loaded | ~17,748 tokens | Attempt #1 fails, retry succeeds in 17s |

Loading unnecessary skills adds 4-5K tokens of context. For DeepSeek direct streaming, every 1K token reduction improves the chance that the retry's cache hit backfills fast enough to succeed.

## Diagnostic Steps

### Check if the failure is stream-stall (not cron timeout)

```bash
grep "Stream stale\|Broken pipe\|stale_stream_kill" /opt/data/logs/agent.log | grep <job_id_prefix> | tail -5
```

Stream-stall shows:
```
Stream stale for 180s (threshold 180s) — no chunks received.
OpenAI client aborted (stale_stream_kill, ...)
[Errno 32] Broken pipe
```

Cron hard timeout shows the job being killed at exactly 180s from start with no LLM output.

### Check which retry pattern is happening

```bash
python3 -c "
import sqlite3, datetime
db = sqlite3.connect('/opt/data/state.db')
cur = db.execute(\"\"\"SELECT id, message_count, started_at 
  FROM sessions WHERE id LIKE 'cron_<job_id_prefix>%' 
  ORDER BY started_at DESC LIMIT 3\"\"\")
for r in cur.fetchall():
    ts = datetime.datetime.fromtimestamp(r[2]).strftime('%m-%d %H:%M:%S') if r[2] else '?'
    print(f'{r[1]}msgs  {ts}')
db.close()
"
```

- **1 msg session** = failed at API call (only system prompt sent, no tool calls)
- **8+ msg session** = succeeded (agent read files + formatted + responded)

## Fixes

### Immediate workaround (keep DeepSeek direct)

1. **Remove unnecessary skill loading**: The pre-script pattern doesn't need `agent-reach`, `cross-platform-format`, or similar skills — data is already parsed into summary files. Remove them:
   ```
   cronjob(action="update", job_id="...", skills=[])
   ```

2. **Shorten the agent prompt**: Every line in the system prompt adds tokens. Keep the prompt under 20 lines. Use compact instructions.

3. **Accept the retry cost**: The first attempt will often fail, but the second succeeds in ~17s. Total wall time ~3.5min is still under the 180s × 3 retry budget. The cron job will eventually deliver.

### Robust fix (switch to OpenRouter)

OpenRouter handles DeepSeek streaming with different connection management:

```
cronjob(action="update", job_id="...", model={
    "provider": "openrouter",
    "model": "deepseek/deepseek-v4-flash"
})
```

The user chose to stay on DeepSeek direct (option B) over switching to OpenRouter (option A) in this session.

## Comparison: DeepSeek Direct vs OpenRouter for Cron

| Factor | DeepSeek Direct | OpenRouter |
|--------|----------------|------------|
| Streaming reliability | First attempt often stalls at 17K+ tokens | More stable; different connection management |
| Retry success | ✅ Retry succeeds (cache hit) | First call may hit 429 rate limit, retry succeeds |
| Latency (nominal) | ~17s on cache hit | ~15s on cache hit |
| Latency (with stall) | ~3.5min (180s stall + 17s retry) | ~30s (no stall, occasional 429 retry) |
| Cost | Same model | Same model (no markup on equal pricing) |
