---
name: hermes-session-management
description: "Inspect, manage, and maintain Hermes Agent sessions — listing, selective batch-deletion, auto-prune configuration, and database health."
version: 1.1.0
author: Hermes Agent
tags: [hermes, sessions, maintenance, cleanup, lifecycle]
---

# Hermes Session Management

Hermes stores all conversations in an SQLite database at `~/.hermes/state.db` (or under `$HERMES_HOME`). Over time, cron test runs, short greetings, and CLI tests accumulate and bloat the database. This skill covers lifecycle management.

## CLI Reference

All session commands are available via `hermes sessions`:

| Command | Purpose |
|---------|---------|
| `hermes sessions list` | Show recent sessions (title, preview, age, ID) |
| `hermes sessions stats` | Session store statistics (count, messages, DB size) |
| `hermes sessions delete <ID>` | Delete a single session |
| `hermes sessions prune --older-than N` | Bulk-delete sessions older than N days |
| `hermes sessions rename <ID> <TITLE>` | Rename a session |
| `hermes sessions export <PATH>` | Export to JSONL |

## Searching & Switching Sessions

### Cross-session full-text search

The `session_search` tool searches ALL sessions in the SQLite database via FTS5, not just the 20 most recent:

| Shape | When to use | Example |
|-------|-------------|---------|
| **Discovery** (by query) | Find sessions about a topic | `session_search("Agent Reach 日报")` |
| **Scroll** (within session) | Read more context around a match | `session_search(session_id="...", around_message_id=N, window=10)` |
| **Read** (full session) | Dump entire session by ID | `session_search(session_id="...")` |
| **Browse** (no args) | See recent sessions chronologically | `session_search()` |

**FTS5 query syntax:**
- Multi-word = AND by default — `Agent Reach 日报` matches sessions containing ALL three terms
- `OR` for broader recall — `Agent OR Reach`
- `"exact phrase"` — `"Hermes Gateway"` matches only that exact phrase
- Prefix wildcard — `deploy*` matches deploy, deployment, deploying
- Boolean — `python NOT java`

**Best practice for recall:** When the user asks "find the session where we did X", use session_search first — don't fall back to `hermes sessions list` (only shows 20 recent sessions) or SQLite queries (no full-text).

### Session switching (gateway-level)

When the agent or user is in the wrong session, switch using:

```
@session:<profile>/<session_id>
```

For the default profile:
```
@session:default/20260624_075822_a51db8c5
```

**Behavior:** The gateway loads the target session's context — both agent and user see the session's history. The user sends this as a message in their chat. Old sessions that are months old can still be navigated to this way — they are never lost unless explicitly deleted.

**WARNING about deletion:** You CAN switch into a session and then delete it from within — but that terminates the current conversation. Always confirm with the user before deleting the session they're actively using.

## Pitfalls

### ⚠️ 0. `/resume` or `hermes sessions list` shows far fewer sessions than expected — dual state.db

**Symptom:** The user runs `/resume` and sees only 1–3 sessions when they know there should be dozens. `hermes sessions list` (if available) also shows few results. Note that `session_search(browse)` (the tool's browse mode with no query) only returns the **3 most recent** sessions — this is by design, not a sign of data loss. Use `session_search(query=...)` with a specific query to find older sessions.

**Root cause:** A stale, empty `state.db` file sitting at `$HERMES_HOME/.hermes/state.db` (0 bytes) shadows the real session database. The **gateway** writes to `$HERMES_HOME/state.db` (directly in `HERMES_HOME`, confirmed by the Hermes source: `state_db_path = hermes_home / "state.db"` in `doctor.py` line 1216), but the **CLI** (`/resume` in particular) may read from `$HERMES_HOME/.hermes/state.db` depending on version and invocation path.

This happens when:
- The `.hermes/` directory was created early (e.g. a month ago) with an empty placeholder `state.db`
- The gateway later started using a different path (`$HERMES_HOME/state.db` directly)
- The stale `.hermes/state.db` blocks the real data from being visible via CLI tools

**Multi-profile state.db layout:** In a multi-profile Docker setup (s6-overlaid), each profile has its own `state.db`:
| Profile | state.db path |
|---------|--------------|
| default (no `-p` flag) | `$HERMES_HOME/state.db` (e.g. `/opt/data/state.db`) |
| named profile (`-p name`) | `$HERMES_HOME/profiles/<name>/state.db` (e.g. `/opt/data/profiles/investment/state.db`) |
| stale leftover | `$HERMES_HOME/.hermes/state.db` (0 bytes, should not exist) |

**Diagnosis — check both files:**

```bash
# Gateway's active state.db
ls -lh /opt/data/state.db                    # Should be large (100MB+)
ls -lh /opt/data/state.db-wal /opt/data/state.db-shm  # WAL = actively written

# CLI's potential state.db
ls -lh /opt/data/.hermes/state.db            # Should NOT be 0 bytes

# Check which the gateway process actually uses
python3 -c "
import os
for pid_dir in os.listdir('/proc'):
    if not pid_dir.isdigit(): continue
    try:
        for fd in os.listdir(f'/proc/{pid_dir}/fd'):
            link = os.readlink(f'/proc/{pid_dir}/fd/{fd}')
            if 'state.db' in link:
                cmd = open(f'/proc/{pid_dir}/cmdline').read().replace(chr(0), ' ')
                print(f'  PID {pid_dir}: {link}')
                print(f'    cmd: {cmd[:100]}')
    except: pass
"

# Count sessions in both databases for comparison
python3 -c "
import sqlite3
for path in ['/opt/data/state.db', '/opt/data/.hermes/state.db']:
    try:
        conn = sqlite3.connect(path)
        c = conn.execute('SELECT COUNT(*) FROM sessions')
        print(f'{path}: {c.fetchone()[0]} sessions')
        conn.close()
    except Exception as e:
        print(f'{path}: {e}')
"
```

**Fix approach — options (consult user before proceeding):**

**Option A — Remove the stale file and let Hermes resolve the real one:**
```bash
rm /opt/data/.hermes/state.db
```
After removal, CLI commands should naturally find `/opt/data/state.db` since `HERMES_HOME=/opt/data`. Verify with `hermes sessions list` afterwards.

**Option B — Symlink the stale file to the real one:**
```bash
rm /opt/data/.hermes/state.db
ln -s /opt/data/state.db /opt/data/.hermes/state.db
```

Option B is safer if any code hardcodes the `.hermes/state.db` path — the symlink ensures both locations see the same data.

**Verification after fix:**
```bash
# Check both paths point to real data
stat /opt/data/.hermes/state.db
# Should show the real file or a valid symlink with non-zero size

# Test resume
hermes sessions list | head -10
# Should show many sessions
```

**Prevention:** If you encounter a fresh Hermes install with a 0-byte `.hermes/state.db`, delete it immediately before any gateway writes to `$HERMES_HOME/state.db` — preventing the split from forming. The gateway always creates its own database.

### 1. `hermes sessions delete` requires confirmation

The command prompts `Delete session 'ID' and all its messages? [y/N]`. Without confirmation, the deletion is silently **Cancelled** (exit code still 0, so it looks successful).

**Fix (modern — preferred):** Use the `--yes` / `-y` flag to skip the prompt:
```bash
hermes sessions delete --yes <SESSION_ID>
```

**Legacy fix (older versions without `--yes`):** Pipe `y`:
```bash
echo "y" | hermes sessions delete <SESSION_ID>
```

**Batch pattern:**
```bash
for id in session1 session2 session3; do
  hermes sessions delete --yes "$id"
done
```

### 2. `hermes sessions list` truncates at 20 rows

The CLI only shows the 20 most recent sessions even when the database has many more. **Do NOT use SQLite queries for recall** — the `session_search` tool is the correct approach:

```python
# ❌ BAD — use hermes sessions list or SQLite when user asked about finding sessions
# ✅ GOOD — use session_search(query) in the agent's own toolset
```

The tool supports FTS5 full-text search across ALL sessions, returning the top matches with bookend context (first/last messages + ±5 around the match) — no need for raw SQL.

### 3. User teaching preference

When the user asks about session management ("如何列举所有会话", "如何删除会话"), **teach them the CLI commands** rather than silently executing everything. Show the exact command and let them choose to run it. This builds their understanding of the system. When they then say "do it", proceed with execution.

## Auto-Prune Configuration

Hermes automatically prunes old sessions. Configure in `config.yaml`:

```yaml
sessions:
  auto_prune: true              # Enable auto-cleanup
  retention_days: 30            # Keep sessions for N days (adjust for your needs)
  min_interval_hours: 24        # Check frequency
  vacuum_after_prune: true      # Reclaim disk space after pruning
```

**Evaluation guidance:**
- **30 days**: Good default if you don't need long-term history
- **90–180 days**: Recommended for users with substantive recurring conversations (model tuning, daily briefings, etc.)
- **0 / false**: Disable auto-prune for full manual control (risk: DB grows unbounded)
- Consider the age of your earliest valuable session when setting `retention_days`

## Workflow: Selective Bulk Cleanup

1. **Assess** — `hermes sessions stats` for total count + DB size
2. **Inventory** — Use Python/SQLite to list all sessions with title, source, message_count
3. **Categorize** what's safe to delete:
   - Cron test/debug runs (titles like "行业技术日报 · Jun DD HH:MM" with 1–50 messages)
   - Short platform greetings (3–5 messages, boilerplate titles)
   - Empty CLI sessions (1–2 messages, no title)
   - Historical debug sessions for already-resolved issues
4. **Delete** — Batch with `echo "y" | hermes sessions delete <ID>` in a shell loop
### 5. **Batch-delete 20+ sessions via Python/SQLite** (much faster than CLI loop)

For large cleanups (20+ sessions), the `echo "y" | hermes sessions delete` loop is slow (one per session). Use Python SQLite directly:

```python
import sqlite3
db = sqlite3.connect('/opt/data/state.db')

# Find target sessions by criteria
cur = db.execute('''
  SELECT id, title FROM sessions 
  WHERE id LIKE "cron_%"  -- or title matching pattern
  AND started_at < ?       -- cutoff timestamp
  ORDER BY started_at
''', (cutoff_timestamp,))

for sid, title in cur.fetchall():
    db.execute('DELETE FROM sessions WHERE id = ?', (sid,))
    db.execute('DELETE FROM messages WHERE session_id = ?', (sid,))

db.commit()
db.close()
```

**Schema note:** The `sessions` table has `started_at` (REAL, timestamp) and `ended_at` (REAL). No `last_active` column — use `started_at` for age-based filtering.

**Safety:** Always VACUUM after mass delete to reclaim disk space: `db.execute('VACUUM')`.

**Pitfall:** The `hermes sessions list` command does NOT have a `--search` flag. To find sessions by pattern, use `session_search()` tool (FTS5) or Python/SQLite queries directly.

### 6. Targeted cleanup of ONLY cron logs (preserve user conversations)

A common need: each cron run creates a NEW session (`cron_<jobid>_<timestamp>`), so cron logs accumulate fast (e.g. 93 of 158 sessions) while the user's real conversations must stay. Source values in the store:
- **Cron logs:** `source='cron'`
- **User conversations:** `source` ∈ {`qqbot`, `weixin`, `feishu`, `cli`, `tui`, `unknown`}

**⚠️ `hermes sessions prune --older-than N` has NO source filter** — it deletes ALL sessions older than N days, including user conversations. Do NOT use it for cron-only cleanup.

**Correct approach — `SessionDB.prune_sessions(source=..., older_than_days=...)`:** The Python API (under `hermes_state`) supports `source=` / `exclude_sources=`, so you can target exactly `source='cron'`:

```python
import hermes_state
db = hermes_state.SessionDB()
n = db.prune_sessions(older_than_days=7, source='cron')
print(f"Deleted {n} cron sessions; user conversations untouched")
```

**Why prefer this over the raw-SQLite DELETE in Step 5:** `prune_sessions` also cleans the FTS5 index, compression-tip lineage, and child sessions atomically. Raw `DELETE FROM sessions/messages` leaves orphaned FTS rows and can break `/resume` search. Use `prune_sessions` whenever the filter fits `source=` / `older_than_days=` / `exclude_sources=`.

**Ready-to-run:** `scripts/prune_cron_sessions.py` — run with `--dry-run` first to preview, then schedule a weekly cron (`0 4 * * 0`) to keep cron logs trimmed to the last 7 days automatically. Never touches user conversations.

## Retaining Valuable Sessions

Sessions worth keeping typically have:
- 100+ messages (substantive debugging/configuration)
- Meaningful titles (model setup, platform integration, cron workflow fixes)
- Cross-platform interactions (QQ + Feishu + WeChat coordination)

When in doubt, preserve and prune later — deletion is irreversible.
