# Cron Session Auto-Cleanup Pattern

## Problem

Agent-driven cron jobs (`auto-rebuild-graph`, etc.) create a new session
each run. Over time, these accumulate — 6+ per day × 30 days = 180+ stale
sessions, bloating the database.

## Solution: no_agent cleanup script

Run a periodic no_agent Python script that:
1. Queries `state.db` for sessions with `cron_` prefix
2. Deletes those older than a threshold (e.g., 6 hours)
3. Reports results via stdout (delivered to the user's chat)

## Key details

| Aspect | Value |
|--------|-------|
| **Script location** | `scripts/cleanup-cron-sessions.py` |
| **Retention** | 6 hours (configurable via `CLEANUP_AFTER_HOURS`) |
| **Cron schedule** | Every 6 hours (`0 */6 * * *`) |
| **Cron type** | `no_agent: true` (script-only, no LLM cost) |
| **Delivery** | Direct to user's chat channel |

## DB path resolution (pitfall)

When a cron job runs the script, `HOME` may point to the profile data
directory (e.g. `/opt/data/profiles/llm-wiki/home`), NOT the actual
user home. Always use `HERMES_HOME` env var when connecting to the
session database:

```python
HERMES_HOME = os.environ.get("HERMES_HOME",
    os.path.expanduser("~/.hermes"))
DB_PATH = os.path.join(HERMES_HOME, "state.db")
```

`hermes sessions delete` requires `y` piped to stdin:

```python
result = subprocess.run(
    [HERMES_BIN, "sessions", "delete", sid],
    input="y\n",
    capture_output=True,
    text=True,
    timeout=10,
)
```

## Sample cron job creation

```text
hermes cron create                              \
  name: cleanup-cron-sessions                   \
  schedule: '0 */6 * * *'                       \
  script: cleanup-cron-sessions.py              \
  no_agent: true                                \
  deliver: <channel_id>
```
