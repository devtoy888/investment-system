---
name: hermes-session-management
description: "Inspect, manage, and maintain Hermes Agent sessions — listing, selective batch-deletion, auto-prune configuration, and database health."
version: 1.1.0
author: Hermes Agent
tags: [hermes, sessions, maintenance, cleanup, lifecycle]
---

# Hermes Session Management

Hermes stores all conversations in an SQLite database at `$HERMES_HOME/state.db`. Key locations:

| Profile | Typical $HERMES_HOME | state.db path | Example |
|---------|---------------------|---------------|---------|
| Default (no `-p`) | `/opt/data` | `/opt/data/state.db` | QQ/微信/钉钉/etc |
| Named profile (`-p foo`) | `/opt/data/profiles/foo` | `/opt/data/profiles/foo/state.db` | 投资助手, llm-wiki |

> ⚠️ **Common pitfall:** `/opt/data/.hermes/state.db` may exist as a stale 0-byte file from an early setup step. Hermes does NOT use this file — the real DB lives directly under `$HERMES_HOME`. If you see a tiny/empty `.hermes/state.db` alongside a large `state.db` at the root, the real data is at the root.

Over time, cron test runs, short greetings, and CLI tests accumulate and bloat the database. This skill covers lifecycle management.

## Troubleshooting: "Sessions are missing"

When a user reports sessions disappearing, follow this debugging path:

### Step 1 — Find all state.db files
Scan for every Hermes SQLite database on the system:

```bash
find /opt/data -name "state.db" -not -path "*/node_modules/*" -type f -exec ls -lh {} \;
```

Expected output (multi-profile setup):
```
126M /opt/data/state.db                          # ← default profile (HERMES_HOME=/opt/data)
8.0M /opt/data/profiles/investment/state.db      # ← named profile "investment"
 72M /opt/data/profiles/llm-wiki/state.db        # ← named profile "llm-wiki"
   0 /opt/data/.hermes/state.db                  # ← stale/abandoned, ignore
```

### Step 2 — Identify which gateway uses which DB
Check running processes:

```bash
ps aux | grep "gateway run"
```

Key patterns:
```
hermes gateway run --replace              # default profile → /opt/data/state.db
hermes -p investment gateway run --replace # named profile → /opt/data/profiles/investment/state.db
hermes -p llm-wiki gateway run --replace  # named profile → /opt/data/profiles/llm-wiki/state.db
```

### Step 3 — Confirm the actual HERMES_HOME in use
Read the process environment to double-check:

```bash
cat /proc/<PID>/environ | tr '\0' '\n' | grep HERMES_HOME
```

The first match is the authoritative state.db location. This resolves confusion when shell `$HERMES_HOME` differs from the gateway's actual environment.

### Step 4 — Verify sessions exist
Query the identified state.db:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
c = conn.cursor()
c.execute('SELECT source, COUNT(*) FROM sessions GROUP BY source')
for r in c.fetchall(): print(f'{r[0]}: {r[1]} sessions')
conn.close()
"
```

### Step 5 — Find a session by title when FTS5 misses it

When `session_search()` returns nothing but you know the session exists (e.g., it's empty or very new), fall back to a direct SQLite query using `LIKE`:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/data/profiles/investment/state.db')
c = conn.cursor()
c.execute(\"SELECT id, title, started_at, message_count FROM sessions WHERE title LIKE '%看板%' ORDER BY started_at DESC\")
for row in c.fetchall():
    print(f'id: {row[0]}, title: {row[1]}, msgs: {row[3]}')
conn.close()
"
```

Replace `'%看板%'` with the search term. The `PRAGMA table_info(sessions)` command reveals all available columns if you need `source`, `user_id`, or `chat_id` filtering.

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

## Session Title Uniqueness

Session titles must be **unique within a profile**. When you try to create a new session with a title already used by an existing session in the same profile, the system auto-appends ` #2`, ` #3`, etc. to disambiguate.

**Key rules:**
- Uniqueness is **profile-scoped** — the same title can exist in different profiles (e.g., "飞书消息格式优化" can exist in both `investment` and `default` profiles)
- Duplicate suffix (` #2`, ` #3`) is auto-generated — not user-configurable
- Renaming a session (`hermes sessions rename <ID> <TITLE>`) also checks uniqueness; providing an existing name generates an error or auto-suffix

## `/resume` Behavior

`/resume` resumes the **most recent session from the same chat context** — it is scoped to the exact platform + chat_id (the specific DM or group) where you issue the command. It does **NOT** search across all sessions from the same platform or profile.

**What `/resume` does:**
- Finds the last session created in the current channel (e.g., this specific Feishu DM)
- Loads it back into conversation context

**What `/resume` does NOT do:**
- Does NOT search sessions from other channels on the same platform (e.g., a session created in Feishu Group A is not findable via `/resume` in Feishu Group B)
- Does NOT show a list of sessions to pick from
- Does NOT do fuzzy title matching

**How to switch to a session outside the current channel:**
```
@session:<profile>/<session_id>
```
See "Session switching" section below.

## Searching & Switching Sessions

### Cross-session full-text search (profile-scoped)

The `session_search` tool searches ALL sessions in the CURRENT profile's SQLite database via FTS5, not just the 20 most recent:

> ⚠️ **Scope:** When Hermes is running under the `investment` profile, `session_search()` only searches the investment profile's state.db. Sessions in the default profile (`/opt/data/state.db`) or other profiles are invisible. To search another profile's sessions, use `session_search(query, profile="profile_name")` or query the other DB directly.

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

**Best practice for recall:** When the user asks "find the session where we did X", use session_search first — don't fall back to `hermes sessions list` (only shows 20 recent sessions) or SQLite queries (no full-text). If session_search returns nothing but you know the session exists, it may be empty (0 messages) — fall back to a direct SQLite `LIKE` query on the `sessions` table (see Step 5 in the troubleshooting section above for the exact query template).

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

### 1. `hermes sessions delete` requires interactive confirmation

The command prompts `Delete session 'ID' and all its messages? [y/N]`. Without confirmation input, the deletion is silently **Cancelled** — the exit code is still 0, so it looks like it succeeded.

**Fix:** Pipe `y` to the command:
```bash
echo "y" | hermes sessions delete <SESSION_ID>
```

**Batch pattern:**
```bash
for id in session1 session2 session3; do
  echo "y" | hermes sessions delete "$id"
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

### 4. `/resume` does not search cross-channel

A common misconception: users expect `/resume` to find any session from the same platform or profile. In reality, `/resume` only checks the exact current chat context (same source + same channel_id). A session created in Feishu Group A is invisible to `/resume` in Feishu Group B, even though both belong to the same profile.

**Fix:** Use `@session:<profile>/<session_id>` to switch to sessions outside the current channel. First find the session ID via `session_search` (agent) or `hermes sessions list` (user CLI).

### 5. Session title collisions produce ` #2` silently

Users who re-create a session (e.g., starting a new one with the same topic title) will get an auto-suffixed ` #2` title without any warning. This can cause confusion when `/resume` picks up the wrong variant.

### 6. Empty sessions are invisible to session_search (FTS5)

`sessions_search(query=...)` uses SQLite FTS5 full-text search over the `messages` table. **Sessions with zero messages are never indexed** — they simply don't appear in any `session_search` result, even by browse or discovery.

This affects:
- **Freshly created sessions** (user says "just created, no content") — `session_search()` returns nothing
- **Sessions under very old auto-pruning** that have been drained
- **Sessions created via `/new` and never used**

**Fix — fall back to direct SQLite query on state.db when session_search misses:**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/opt/data/profiles/investment/state.db')
c = conn.cursor()
c.execute('SELECT id, title, started_at, message_count FROM sessions ORDER BY started_at DESC')
for row in c.fetchall():
    print(f'id: {row[0]}, title: {row[1]}, msgs: {row[3]}')
conn.close()
"
```

Then delete with:
```bash
echo "y" | /path/to/hermes sessions delete <SESSION_ID>
```

**Tip — filter by zero-message sessions specifically:**
```sql
SELECT id, title, started_at, message_count FROM sessions WHERE message_count = 0
```

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
5. **Verify** — Re-check stats to confirm

## Retaining Valuable Sessions

Sessions worth keeping typically have:
- 100+ messages (substantive debugging/configuration)
- Meaningful titles (model setup, platform integration, cron workflow fixes)
- Cross-platform interactions (QQ + Feishu + WeChat coordination)

When in doubt, preserve and prune later — deletion is irreversible.
