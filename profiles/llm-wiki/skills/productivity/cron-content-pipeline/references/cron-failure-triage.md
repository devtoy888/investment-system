# Cron Failure Triage

Common reasons cron jobs fail and how to diagnose/fix them.

## First Rule: Distinguish Code Failures from Delivery Failures

When a cron job shows `last_status: "error"`, the most common pitfall is **assuming the code failed** when actually the **content was generated correctly but delivery to the target platform(s) failed**.

**How to tell the difference:**

| Signal | Likely Code Error | Likely Delivery Error |
|--------|:-----------------:|:--------------------:|
| `last_status: "error"` | ✅ possible | ✅ possible |
| `last_delivery_error: "delivery error: ..."` | ❌ | ✅ **definitive** |
| `last_delivery_error: null` | ✅ likely | ❌ |
| Cron session shows partial/no output | ✅ likely | ❌ |
| Cron session shows full completed report | ❌ | ✅ likely |

**The diagnostic workflow — batch-run ALL failing jobs at once:**

When multiple cron jobs show errors, batch-run them all immediately:

```
cronjob(action="run", job_id="<job1_id>")
cronjob(action="run", job_id="<job2_id>")
cronjob(action="run", job_id="<job3_id>")
```

Then check their cron sessions after they complete and check gateway logs:

```bash
grep -i "delivery error\|delivered to\|delivery failed" /opt/data/logs/gateway.log | tail -20
```

**Interpreting the results:**

- **Code runs, delivery fails**: The cron session shows a complete agent response (report generated), but `last_delivery_error` has platform-specific errors. These are platform credential issues — fix by re-authenticating the platform. The cron job itself is fine.
- **Code fails**: The cron session has only the user message (no assistant response), or the assistant response is an error message. Check the model, skills, and prompt.

### Key Insight: Delivery Errors ≠ Code Errors

A cron job can:
- ✅ Generate content successfully
- ❌ Fail to deliver to one or more platforms
- ⚠️ Still show `last_status: "error"` system-wide

This is by design: `last_status` reflects whether delivery to ALL target platforms succeeded. If even one platform rejects the message, the whole job is marked `"error"`.

**Common delivery errors that look like code failures:**

```
delivery error: Weixin send failed: iLink sendmessage rate limited; cooldown active for 30.0s
  → WeChat rate limit. Re-trigger the cron run after 30s.

delivery error: QQBot: no access_token in response
  → QQ Bot credentials expired. Need new QQ_APP_ID / QQ_CLIENT_SECRET.

delivery error: Feishu send failed: obtain self tenant access token failed, code: 10014, msg: app secret invalid
  → Feishu app secret expired. Need new FEISHU_APP_SECRET.

delivery error: Telegram send failed: You must pass the token you received from https://t.me/Botfather!
  → Telegram bot token never configured. Need TELEGRAM_BOT_TOKEN.

delivery error: platform 'weixin' not configured/enabled
  → Weixin platform is NOT set up in gateway. Either configure it or remove from deliver field.

delivery error: cannot schedule new futures after interpreter shutdown
  → Gateway restart race. Re-trigger the cron run.
```

**Counter-intuitive scenario**: A delivery error on one platform cascades. If the deliver field lists 4 platforms and only 1 fails, the whole job shows `"error"` — but the other 3 platforms received the message. This makes TUI show `last_status: "error"` even when most deliveries succeeded.

## Skill Not Found

**Symptom:** `⚠️ Skill(s) not found and skipped: <name>` in cron session.

**Root cause:** The skill is installed in a non-standard path (e.g. `~/.agents/skills/`) and `skills.external_dirs` in config.yaml doesn't include it.

**Fix:**
1. Add the path to `config.yaml`: `skills.external_dirs: [~/.agents/skills]`
2. OR copy/symlink the skill to `~/.hermes/skills/<name>/`
3. Restart gateway so the new config is picked up by future cron sessions

## Model Override Not Honored (Silent Model Misrouting)

**Symptom:** `last_status: "error"`, `[Errno 32] Broken pipe` repeated across 3 retries. Job listing shows the expected model override, but API calls go to a different provider's base URL.

**Root cause:** The cron job's `model` override is stored in the database but NOT honored at runtime when:
- The main model provider was changed after the override was saved
- The override has `base_url: null` and the runtime cannot resolve the custom provider's base_url from config
- The runtime falls through to the current main provider instead

**Diagnosis — request dump files are the definitive tool:**

```bash
# Find request dumps for the failed cron run
ls /opt/data/sessions/request_dump_cron_<job_id>_*

# Check the ACTUAL API endpoint called (not what the job listing shows)
python3 -c "
import json, glob, os
dumps = sorted(glob.glob('/opt/data/sessions/request_dump_cron_<job_id>_*.json'),
               key=os.path.getmtime)
if dumps:
    d = json.load(open(dumps[-1]))
    r = d['request']
    print(f'Actual URL:    {r[\"url\"]}')
    print(f'Actual model:  {r[\"body\"][\"model\"]}')
else:
    print('No request dumps found — job may have succeeded or never started the LLM call')
"
```

Compare the Actual URL/Model against the cron job's stored override from `cronjob(action="list")`.

**Fix — update the job with explicit `base_url`:**

```python
cronjob(
    action="update",
    job_id="<job_id>",
    model={
        "provider": "custom:agnes",     # or your custom provider name
        "model": "agnes-2.0-flash",     # or your model name
        "base_url": "https://apihub.agnes-ai.com/v1"  # ← REQUIRED for custom providers
    }
)
```

**Key insight:** `cronjob(action="list")` shows what the override was **set to**, not what the runtime **actually used**. They can diverge silently. When a cron job starts failing after a main-model switch, always verify via request dumps.

## Systematic Diagnostic: Timeline of Model Changes

When a cron job works for days then suddenly fails:

```bash
# 1. Find all request dumps for this job
ls -lt /opt/data/sessions/request_dump_cron_<job_id>_*

# 2. Check which API was called at each point
for f in /opt/data/sessions/request_dump_cron_<job_id>_*; do
  python3 -c "
import json
d = json.load(open('$f'))
r = d['request']
from datetime import datetime
print(f'{datetime.fromisoformat(d[\"timestamp\"][:19])} → {r[\"url\"]} ({r[\"body\"][\"model\"]})')
"
done

# 3. The timestamp where the URL changes points to when the main model was switched
```

## Model Quota Exhaustion (429)

**Symptom:** Cron job `last_status: "error"`, or silently falls to paid model.

**Root cause:** The pinned model's free quota is exhausted (e.g. Gemini free tier: 1500 req/day, 30 req/min).

**Fix:**
1. Switch to a working model: `cronjob(action="update", job_id=..., model={"provider": "openrouter", "model": "deepseek/deepseek-v4-flash"})`
2. Test: `cronjob(action="run", job_id=...)`
3. Check result: `cronjob(action="list")` → verify `last_status: "ok"`

## Concurrent Job Timing Analysis (DeepSeek Peak-Hour Stalls)

**Use case:** Multiple cron jobs share the same API provider, fire at the same schedule (e.g. 00:00 UTC = 08:00 CST), and one or all fail with Broken pipe / stale stream.

**Common assumption:** "Concurrent requests overwhelmed the API."

**Why the assumption is often wrong:** Tracing exact timestamps can show the large-context job was already stalling *before* the small-context job even started its first API call — and the small job completed 3 successful calls to the same endpoint during the large job's stalled connection.

**Diagnostic — trace exact timestamps for ALL concurrent jobs:**

```bash
# Step 1: Get the job IDs for jobs that fire at the same schedule
cronjob(action="list")

# Step 2: For each job, trace the exact API call timestamps from the failing run
# Use today's date (YYYY-MM-DD) from the job's last_run_at
grep "<job_id_1>" /opt/data/logs/agent.log | grep -E "API call|Turn ended|Broken pipe|delivered" | tail -20
grep "<job_id_2>" /opt/data/logs/agent.log | grep -E "API call|Turn ended|Broken pipe|delivered" | tail -20
```

**Key columns in agent.log:**
- `API call #1: model=... in=N out=M total=T latency=Xs` — a SUCCESSFUL call with token counts and latency
- `Stream stale for 180s ... Killing connection` — the stream accepted by the server but received zero chunks
- `Broken pipe` — the connection was torn down after 180s stale
- `delivered to ...` — the message was sent to the platform

**Reading the result — three patterns:**

| Pattern | What the data shows | Real cause |
|---------|--------------------|------------|
| **True concurrency** | Both jobs' API call timestamps overlap AND both fail identically | API rate limiting or connection pool exhaustion. Stagger schedules. |
| **Peak-hour isolation** | Large-context job stalls at 00:01; small-context job starts at 00:03 and succeeds 3 times during the stall | DeepSeek server-side congestion at 08:00 CST. Stalling is about context size + time, not concurrency. Staggering still fixes it by moving the large job out of the peak window. |
| **Model misrouting** | Both jobs fire at different times, but the large job fails consistently while small jobs succeed. Check `cronjob(action="list")` → `model` field — if the failing job has a model override without `base_url`, it may be silently using the wrong provider. | See "Model Override Not Honored" section above. |

**Fix when step 2 shows peak-hour isolation (Pattern 2):**
- Move the large-context job to run **before** the peak window (e.g. 07:50 instead of 08:00)
- The added 10-minute gap is not about avoiding the other job — it's about clearing the 08:00 CST congestion window
- Verify: `cronjob(action="run")` a few minutes before the peak and check latency

**Note for the triager:** The user's intuitive hypothesis ("concurrent requests overloading the API") was disproven by the data in the production case, yet the same fix (staggering schedules) still worked. Always trace timestamps before assuming the fix's mechanism — the real mechanism may inform better long-term solutions.

**Symptom:** `delivery error: cannot schedule new futures after interpreter shutdown`

**Root cause:** Gateway was restarted while cron job was delivering its response.

**Fix:** Don't restart gateway within ~3 minutes of triggering a cron run. If it happens, just re-trigger the cron run.

## Cron Session Is Created But Never Produces Output

**Symptom:** `session_search()` shows a cron session with only the user message (the prompt), and no assistant response. `last_status: "error"` but `last_delivery_error: null`.

**Root cause:** The cron agent timed out or errored before producing any output. Common causes:
- **Model unavailable** — the pinned model returned HTTP error or timeout
- **Prompt too long** — very long prompts (especially with full skill content embedded, 5K+ tokens) overwhelm free-tier models
- **Agent stuck** — the agent loop hit max_turns or ran into a tool permission issue

**Diagnosis:**
```bash
# Check the session content — if only user message exists, the model never responded
session_search(session_id="cron_<job_id>_<timestamp>")

# Check model availability
hermes chat -q "hello" --provider <provider> --model <model> 2>&1 | head -5

# Check gateway logs for agent errors
grep "cron\|error\|timeout" /opt/data/.hermes/logs/agent.log | tail -10
```

**Fix:**
1. Verify the model works standalone (test with a simple query)
2. Shorten the cron prompt — remove verbose examples, keep only essential instructions
3. Switch to a more capable model for long prompts

## Systematic Batch Diagnosis (All-Jobs-at-Once Pattern)

When multiple cron jobs show errors, the most efficient approach:

```
1. cronjob(action="list")
2. cronjob(action="run") → for EVERY failing job (batch)
3. Wait for sessions to be created
4. session_search() → browse for new cron sessions
5. For each cron session, check if it produced output or only has user message
6. grep "delivery error" /opt/data/logs/gateway.log → check if deliveries failed
7. grep -i "error\|401\|token\|secret\|invalid" /opt/data/logs/gateway.log → platform-level errors
```

This pattern reveals:
- **Systemic issues** (all jobs failing the same way → model/skill/platform problem)
- **Code bugs** (single job failing differently from others)
- **Delivery problems** (jobs produce output but cannot deliver)

## Feishu Adapter Failure After Gateway Restart (Dependency-Missing Pattern)

**NOT the same as the race condition above.** This is a persistent failure, not a timing issue.

**Symptom:**
```
delivery error: Feishu dependencies not installed. Run: pip install 'hermes-agent[feishu]'
```

But the job worked before — Feishu deliveries used the "live adapter" (gateway WebSocket). After restart, they fail permanently.

**Root cause — two layers:**

| Layer | Mechanism | Evidence |
|-------|-----------|----------|
| **Immediate failure** | Gateway restart breaks the existing Feishu WebSocket. On restart, the Feishu adapter tries to initialize from scratch and hits a `requirements not met` check for `hermes-agent[feishu]` | `WARNING gateway.platform_registry: Platform 'Feishu / Lark' requirements not met (pip install 'hermes-agent[feishu]')` |
| **Underlying cause** | The Docker container lacks the Feishu SDK. The original gateway worked because the WebSocket was established before the dependency was checked (or the initial build had it) | `python3 -c "import hermes_platform_feishu"` → ModuleNotFoundError |

**Distinguishing from the race condition:**

| Symptom | Likely Cause |
|---------|-------------|
| `delivery error: Feishu dependencies not installed` | Dependency missing — fails every time, persists across restarts |
| `delivery error: cannot schedule new futures after interpreter shutdown` | Race condition — one-time, next cron run works fine |
| Feishu worked yesterday, failed today, no code/config changed | Gateway was restarted (possibly by auto-container updates, health checks, or admin action) |

**Gateway log confirms the diagnosis:**
```bash
grep -i "feishu\|lark\|requirements not met" /opt/data/logs/gateway.log
# Look for: "Platform 'feishu' is registered but adapter creation failed"
#         "Platform 'Feishu / Lark' requirements not met"
```

**The gateway log shows the lifecycle:**
```
[initial startup] → Feishu WS connects ✅ → works for days
[any gateway restart] → Feishu adapter init fails ❌ (dependency missing)
                        → never recovers until dependency installed
```

**Red herring to avoid:** The Feishu WebSocket has a 24-hour ticket expiry pattern (observed: `receive message loop exit, err: no close frame received or sent` every ~24h, followed by auto-reconnect in ~30s). This ticket reconnection works fine — it's NOT the cause of the persistent failure. The persistent failure is specifically gateway restart clearing adapter state while dependency is absent.

**Feishu WebSocket lifecycle (normal operation before any restart):**
```
Day 1 14:27  → WS connected
Day 2 14:28  → Disconnect (24h ticket expiry, "no close frame")
Day 2 14:28  → Auto-reconnect (30s later) ✅
Day 2 14:29  → WS connected again
...
Repeats every ~24h indefinitely — auto-reconnect always works
```

**Fix:**
```bash
# Option 1: Install the dependency in the container
pip install 'hermes-agent[feishu]'
hermes gateway restart

# Option 2: Remove Feishu from the cron job's deliver field if not needed
cronjob(action="update", job_id="<id>", deliver="qqbot:...,dingtalk:...")

# Option 3: If read-only rootfs blocks pip install, remove Feishu from delivery
```

**Long-term monitoring:** Check `hermes gateway run` logs on startup for adapter creation successes/failures. A daily cron grepping for `adapter creation failed` would catch this.

## Checklist for Diagnosing Any Cron Failure

```bash
# 1. Check cron job status — immediately reveals if it's a delivery error
cronjob(action="list")

# 2. Check the cron session for errors
session_search(query="cron_<job_id>", sort="newest")

# 3. Check gateway logs for delivery errors
grep -i "delivery error\|delivered to" /opt/data/logs/gateway.log | tail -10

# 4. Check platform authentication errors
grep -i "token\|secret\|invalid\|401" /opt/data/logs/gateway.log | tail -10

# 5. Check if the model works
hermes chat -q "hello" --provider <provider> --model <model> 2>&1 | head -5

# 6. Check skill availability
skill_view(name="<skill_name>")

# 7. Only after the above 6 checks fail to identify the issue — dig into code
```
