---
name: hermes-maintenance
description: Operational housekeeping for a running Hermes deployment — safely switching the active model (and auto-reverting on a date), pruning cron/auto-generated sessions WITHOUT touching user conversations, analyzing and shrinking state.db (FTS5 trigram bloat, VACUUM), and clearing pip/uv caches. Use when the user asks to clean up sessions, reduce disk usage, switch models, or debug why state.db is large.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Maintenance & Housekeeping

Procedures for keeping a Hermes instance lean and reconfiguring the active model without downtime.

## When to use
- User asks to "clean up sessions", "what's taking up space", "why is state.db 100MB+"
- User wants to switch the active model (e.g. to a free/promo model) and switch back later
- Disk usage on the host is growing and you need to find the culprit

## Environment notes (this deployment)
- `hermes` CLI is NOT on PATH. Prefix every command with:
  `export PATH="/opt/hermes/.venv/bin:/opt/hermes/bin:$PATH"`
- Main config: `/opt/data/config.yaml` (reachable as `~/.hermes/config.yaml` via the home→/opt/data mapping)
- Session DB: `/opt/data/state.db` (SQLite + FTS5). Profiles have their own: `/opt/data/profiles/<name>/state.db`
- Cron scripts must live in `~/.hermes/scripts/` (== `/opt/data/scripts/`). `cronjob create --script` REJECTS absolute paths and any path outside that dir.
- **Host↔container mapping**: the Docker container's `/opt/data` is a persistent volume backed by the HOST's `~/.hermes-main` directory. So host `~/.hermes-main/...` == container `/opt/data/...`. Scripts/data written under `/opt/data` survive container restarts/rebuilds. (User corrected a wrong assumption that the data lived under `~/.hermes-main` mapping to a different in-container path — it maps to `/opt/data`.)
- `~/.hermes/scripts` is a SYMLINK to `/opt/data/scripts` — same physical dir, either name resolves to the cron script location.
- The `patch` tool REFUSES to edit `config.yaml` ("Agent cannot modify security-sensitive configuration"). ALWAYS use `hermes config set KEY VAL` instead — never hand-edit or patch the config.

## Switching the active model (safe)
Do NOT edit config.yaml by hand. Use:
```
hermes config set model.default tencent/hy3:free
hermes config set model.provider openrouter
hermes config set model.base_url https://openrouter.ai/api/v1
```
Verify with `grep -A4 '^model:' /opt/data/config.yaml`.
New sessions pick up the change immediately; a running gateway applies it on next session start (CLI needs a restart).

### Auto-switch-back pattern (free/promo model with revert date)
1. Switch model now (commands above).
2. Create a ONE-SHOT cron that runs the revert via `hermes config set` (never patch):
```
cronjob create --name "revert model" --schedule "2026-07-21T00:00:00" \
  --prompt "Run: hermes config set model.default deepseek-v4-flash ; hermes config set model.provider deepseek ; hermes config set model.base_url https://api.deepseek.com . Verify config.model section and report." --deliver origin
```
The cron must use `hermes config set` for the same security reason patch is blocked.

## Pruning sessions (keep user conversations safe)
`hermes sessions prune --older-than N` deletes by AGE across ALL sources — it WILL also delete the user's own chat history. To prune ONLY cron/auto-generated logs:

**Reliable filter: `source='cron'`.** Cron auto-sessions are stored with `source='cron'`; user chats are `qqbot` / `weixin` / `feishu` / `cli` / `tui`. The `cron_` ID prefix is a WEAK signal (some user sessions also carry it) — always filter by `source`, never by ID prefix.

Use the internal API (script at `scripts/prune_cron_sessions.py`, also `~/.hermes/scripts/`):
```
python /opt/data/scripts/prune_cron_sessions.py --days 7 --dry-run   # verify first, no delete
python /opt/data/scripts/prune_cron_sessions.py --days 7             # execute
```
It calls `db.prune_sessions(older_than_days=days, source='cron')` — only cron logs older than N days are removed; user sessions are untouched.

**PITFALL — dry-run count ≠ actual delete count.** The script's manual candidate list (built from `last_active_ts`) and `prune_sessions`'s own cutoff (uses a different timestamp field) can disagree. In one run the dry-run reported 93 candidates but the live delete removed 71. Trust the `prune_sessions` return value, not the pre-count.

**Schedule it weekly** (pass the script filename, not a path):
```
cronjob create --name "weekly cron log prune" --schedule "0 4 * * 0" \
  --script prune_cron_sessions.py \
  --prompt "Run the prune script (--days 7), report N deleted, confirm user sessions (qqbot/weixin/feishu) unchanged."
```

## Cron scheduling: script args & timezone pitfalls

### Script field = bare filename, NO inline args
`cronjob create --script` accepts ONLY the filename that lives in `~/.hermes/scripts/`
(it rejects absolute paths AND any path outside that dir). Anything after a space is
treated as PART OF THE FILENAME, so `openrouter_free_monitor.py check` fails at runtime
with `Script not found: /opt/data/scripts/openrouter_free_monitor.py check`.
- If your script needs an argument, either (a) make the argument the DEFAULT in the
  script's `argv` parser so no flag is needed, or (b) write a thin wrapper
  `~/.../scripts/run_x.py` that calls the real script with the arg baked in.
- Verified-good pattern: `cronjob create --script openrouter_free_monitor.py --no-agent ...`
  ran with `execution_success: true`.

### Crontab timezone is PER-PROFILE — verify with next_run_at
The scheduler does NOT use one global TZ. In this deployment:
- **main / default profile** interprets crontab as **UTC**
  (evidence: `行业日报 0 0 * * *` → `next_run_at 2026-07-16T00:00:00+00:00`;
   `每日 R2 备份 0 18` → `18:00:00+00:00`).
- **investment profile** interprets crontab as **Beijing +08**
  (evidence: `0 8 * * 1-5` → `next_run_at 2026-07-16T08:00:00+08:00`).
`cronjob` has NO profile switch — tasks you create land in the MAIN profile (UTC). The
user's convention is that ALL times are Beijing unless explicitly stated otherwise, so:
- To fire at Beijing 09:00 & 21:00 from the main profile, write `0 1,13 * * *`
  (UTC 01:00 = Beijing 09:00; UTC 13:00 = Beijing 21:00).
- ALWAYS verify with `cronjob list` and read the `next_run_at` offset: `+00:00` = UTC,
  `+08:00` = Beijing. Do not trust the system `date` alone.

### Cron storage & end-to-end test
- Main profile jobs: `/opt/data/cron/jobs.json` (managed via the `cronjob` tool, not by hand).
- Profile jobs (e.g. investment): `/opt/data/profiles/<name>/cron/jobs.json`.
- `cronjob run --job_id X` triggers an immediate execution and returns `execution_success`
  plus `execution_error` — use it as the end-to-end test BEFORE declaring a cron done
  (catches "Script not found" / wrong workdir / import errors that `list` won't show).

### Delivery & agent mode (monitor/watchdog pattern)
- `--deliver qqbot` pushes the script's stdout verbatim to the user's QQ DM.
- `--no-agent` (no_agent=true) delivers the script's stdout with NO LLM post-processing —
  ideal for monitors that already print the final human message. **Empty stdout = silent**
  (nothing sent). This is the correct pattern for a "notify only when something changed"
  monitor: print the alert only when there is one, stay quiet otherwise.
- Reference recipe for one such monitor (OpenRouter limited-free model detection, incl. the
  `expiration_date` ISO-string pitfall): `references/openrouter_free_model_detection.md`.

## Analyzing state.db size
If `state.db` is unexpectedly large, the cause is almost always FTS5 indexes, not messages. Per-table page usage:
```python
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
ps = conn.execute('PRAGMA page_size').fetchone()[0]
for name, pages in conn.execute('SELECT name, SUM(ncell) FROM dbstat GROUP BY name ORDER BY pages DESC'):
    print(f'{name:35s} {pages*ps/1024/1024:7.2f} MB')
```
Typical finding: `messages_fts_trigram_*` tables dominate (~78%). Hermes 0.18.2 builds BOTH a standard FTS5 and a trigram FTS5 (for CJK substring search); the trigram index is 3-5x the raw message size. This is EXPECTED for Chinese-heavy deployments — do NOT disable it unless substring search is unused.

### Reclaim deleted space (VACUUM)
SQLite does not shrink the file after DELETE — freed pages stay as a freelist. Reclaim with:
```python
import sqlite3
conn = sqlite3.connect('/opt/data/state.db'); conn.execute('VACUUM'); conn.close()
```
Locks the db a few seconds; safe to run occasionally (monthly). Pruning 71 cron sessions took 133MB→127MB.

## Clearing pip/uv caches (biggest easy win)
Profile venvs accumulate download caches under `home/.cache`:
```
du -sh /opt/data/profiles/*/home/.cache/{pip,uv}
rm -rf /opt/data/profiles/investment/home/.cache/pip
rm -rf /opt/data/profiles/investment/home/.cache/uv
rm -rf /opt/data/profiles/llm-wiki/home/.cache/pip
rm -rf /opt/data/profiles/llm-wiki/home/.cache/uv
```
~205 MB recovered; safe (re-downloaded on next install).

### akshare-deps __pycache__
`/opt/data/akshare-deps` (fund-data venv) holds ~318 `__pycache__` dirs (~50 MB). Safe to clear; rebuilt on import:
```
find /opt/data/akshare-deps -name "__pycache__" -type d -exec rm -rf {} +
```

## Do NOT touch
- `lazy-packages/` (~69 MB) — Hermes core lazy deps; deleting breaks the agent
- `state.db` message content — only prune via the `source='cron'` filter
- `akshare-deps` package bodies — only the `__pycache__`, never the libraries

## Verification checklist (run after any cleanup)
- `hermes sessions list` shows user conversations intact
- `python -c "import hermes_state; db=hermes_state.SessionDB(); print(len(db.list_sessions_rich(source='cron')))"` shows reduced cron count
- `ls -lh /opt/data/state.db` shows expected size
- `grep -A4 '^model:' /opt/data/config.yaml` reflects intended model after a switch
