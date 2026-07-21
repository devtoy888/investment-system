---
name: hermes-session-management
description: "Inspect, manage, and maintain Hermes Agent sessions — listing, selective batch-deletion, auto-prune configuration, and database health."
version: 1.3.0
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

## User Preferences

### Session naming: prefer `/new 标题` over `/new` + `/title`

The user prefers:

```text
/new 我的项目名称    ✅ 一步到位
/new                ❌ 模糊的自动标题，难找
```

优点：
- 压缩链自动延续：`我的项目 #2` → `#3`
- `/resume 项目名称` 直接跳到最新会话
- `/sessions` 列表里显示有意义的名字

### Pattern for new work sessions

1. Always start with `/new <有意义名称>`
2. If you forgot to name it at creation, use `/title <名称>` immediately

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

The tool supports FTS5 full-text search across ALL sessions, returning the top matches with bookend context (first/last messages + -5 around the match) — no need for raw SQL.

### 3. User teaching preference

When the user asks about session management, **teach them the CLI commands** rather than silently executing everything. Show the exact command and let them choose to run it. This builds their understanding of the system. When they then say "do it", proceed with execution.

### 4. /resume vs /sessions — critical distinction

Users often confuse `/resume` (no args) with `/sessions`:

| Command | Behavior |
|---------|----------|
| `/resume` | Lists **titled** sessions on messaging platforms (not just 1). Shows numbered list. |
| `/resume 标题` | Searches by title, resumes best match. |
| **`/sessions`** | **Shows all recent sessions** (titled + unnamed) for this user/platform on messaging platforms. |

On messaging platforms (not CLI), both commands go through the same visibility filter — so if `/sessions` shows nothing, `/resume` (no args) will also show nothing.

Note: On the CLI, `/resume` has different semantics (resumes the most recent session). This pitfall covers the **messaging gateway** behavior.

### 5. "No sessions found" — diagnostic workflow

When `/sessions` or `/resume` (no args) returns "No sessions found" but the user expects sessions:

**Step 1 — Check the database directly:**
```python
import sqlite3
conn = sqlite3.connect("~/.hermes/state.db")
cur = conn.cursor()
cur.execute("""
    SELECT id, title, source, chat_id, thread_id, user_id
    FROM sessions WHERE source = 'feishu'
    ORDER BY started_at DESC
""")
for r in cur.fetchall():
    print(f"  {r[0]} | {r[1]} | chat={r[3]} | thread={r[4]} | user={r[5]}")
```

Compare with investment_profile's state.db to find differences.

**Step 2 — Find the source code:**
```bash
grep -n "def _handle_sessions_command" /opt/hermes/gateway/slash_commands.py
grep -n "def _resume_target_allowed" /opt/hermes/gateway/slash_commands.py
```

**Step 3 — Trace the filter chain:**

The entry points are at lines ~9414-9418 (gateway/run.py):
```python
if canonical == "sessions":
    return await self._handle_sessions_command(event)
```

Which calls into `slash_commands.py`:

1. `query_session_listing()` — fetches root-only sessions (excludes compression children), filters by source/platform
2. `_resume_row_visible()` → `_resume_target_allowed()` — the **IDOR guard** (lines 765-906)

**Step 4 — Check the IDOR guard conditions:**

In `_resume_target_allowed()` (lines 765-906 of `slash_commands.py`), the filter checks these conditions in order:

| Condition | Code Line | What it checks |
|-----------|-----------|----------------|
| **Platform match** | 794-797 | `row.source` must equal `caller.source` |
| **Origin chat match** | 807-808 | Live session origin? → `_same_origin_chat()` |
| **Thread match** | 809-810, 845-848 | `row.thread_id` must equal `caller.thread_id` |
| **DM participant** | 852-869 | Same user_id if DM; handles feishu `user_id_alt` |
| **Non-DM chat** | 870-897 | Same chat_id + same participant |

The most common causes of "No sessions found" despite sessions existing:

| Cause | Symptom in DB | Fix |
|-------|---------------|-----|
| **Caller is in a thread, sessions are not** | All sessions have `thread_id=None`, caller has `thread_id=om_xxx` | Exit the thread (back to main DM) before `/sessions` |
| **Old sessions have NULL chat_id** | `chat_id=None` in DB | Use `hermes sessions list` CLI, or admin `--all` |
| **Wrong profile's DB** | Gateway is reading default profile's DB, sessions are in profile DB | Check `find / -name "state.db" -path "*hermes*"` |
| **Compression child excluded** | Session has `parent_session_id` set | Root session is projected forward automatically |
| **Thread session mismatch** | Session has `thread_id=om_xxx` but caller is in DM (no thread) | The reverse — caller in DM, session in thread |

### 6. Thread ID mismatch — the most subtle case

The `origin_ok` check at line 845-848 of `slash_commands.py` requires **thread_id equality**:

```python
origin_ok = (
    bool(row_src) and bool(caller_src)
    and str(row_src) == str(caller_src)
    and row_thread == caller_thread  # ← This is the critical line
)
```

This means:
- If caller is in a **thread** (`thread_id=om_xxx`), only sessions in the **same thread** are visible
- If caller is in the **main DM** (`thread_id=None`), only sessions with **no thread** are visible
- Sessions are **isolated by thread** — they cannot be listed across thread boundaries

**Why this exists**: The `build_session_key()` appends `thread_id` to the session key. Two sessions with the same `chat_id` but different `thread_id` are in different session keys. The IDOR guard must enforce this boundary to prevent cross-thread session enumeration.

**Recovery**: The user can still switch to a thread-scoped session by:
1. Going to the main DM (not a thread) → `/sessions` shows all DM-level sessions
2. Using `/resume "exact session title"` with the title (goes through the same filter if in a thread, but works from DM)
3. Using CLI `hermes -r "session title"` (no chat_id/thread_id filter)

### 7. Feishu identity model impact on session visibility

Feishu uses a three-tier identity model (from adapter.py docstring):

```
open_id  (ou_xxx) — App-scoped user ID (always available)
union_id (on_xxx) — Cross-app stable ID (used as user_id_alt)
user_id  (u_xxx)  — Tenant-scoped ID (may not be present)
```

The session key uses `union_id` (via `user_id_alt`) when available.

This means in `_resume_target_allowed()`:
- `caller_keys_on_alt = True` (feishu always has `user_id_alt` set)
- At line 864: `caller_keys_on_alt and not (bool(row_chat) and bool(caller_chat))`
  - If **both** have chat_id → passes (chat_id is the DM key for feishu)
  - If row has `chat_id=NULL` → **blocks** the session (the alt_id alone can't prove ownership)
- This is why sessions created before chat_id capture are permanently invisible to `/sessions`

**To diagnose feishu-specific visibility issues**, check:
```sql
SELECT id, title, chat_id, thread_id, user_id FROM sessions WHERE source='feishu';
```
Then compare `user_id` against the feishu user's `open_id` (`ou_xxx`), and note that `user_id_alt` (union_id) isn't stored in the sessions table.

### 8. Old sessions (NULL chat_id) invisible to /sessions

In `_resume_target_allowed()` (line 807-808 of `slash_commands.py`):

```python
caller_chat = str(getattr(source, "chat_id", "") or "")
row_chat = str(row.get("chat_id") or "")
```

Sessions created before the chat_id capture feature was added have `chat_id=NULL` in the database. Combined with the feishu `user_id_alt` check (line 864), these sessions fail the visibility check. They are ONLY recoverable via:

- `hermes sessions list` (CLI, no chat_id/thread_id filter)
- Admin `--all` override (`/sessions all` or `/resume --all`)
- Direct `@session:<profile>/<id>` link
- CLI `hermes -r "<session title>"`

This is by design — it prevents cross-origin session enumeration (CWE-639). Old sessions are not lost, they are just invisible to the `/sessions` picker on messaging platforms.

### 9. Multi-profile database: which state.db is in use

Hermes can have **multiple state.db files** depending on profile setup:

| Path | Contents | When used |
|------|----------|-----------|
| `$HERMES_HOME/state.db` (e.g. `/opt/data/state.db`) | All sessions, all platforms | Default gateway (`hermes gateway run`) |
| `$HERMES_HOME/profiles/<name>/state.db` | Profile-scoped sessions | Profile gateway (`hermes -p <name> gateway run`) |

The default profile's config may point to another profile's config (`Config: .../profiles/llm-wiki/config.yaml`), but the `state.db` path is derived from the profile data directory, not the config file. This means:

- `hermes sessions list` (no `-p`) may read from a profile-specific DB if the default profile's config cross-references another profile
- `hermes -p llm-wiki sessions list` always reads from `profiles/llm-wiki/state.db`
- A gateway started with `-p llm-wiki` reads from `profiles/llm-wiki/state.db`

**To check which DB a gateway actually uses:**
```bash
find / -name "state.db" -path "*hermes*" 2>/dev/null
cat /proc/<PID>/environ | tr '\0' '\n' | grep HERMES_HOME
```

See also: `references/feishu-null-chatid-fix.md` — exact SQL fix and platform comparison table for the NULL chat_id issue.

### 10. Compression chain: why root sessions don't appear in /sessions

When a session chain exists like:

```
LLM Wiki 主频道  ──compression──→  LLM Wiki 主频道 #2  ──compression──→  LLM Wiki 主频道 #3 (current)
```

`list_sessions_rich()` with `project_compression_tips=True` (default) projects the root to show the **latest continuation's** data — including the session ID. If the latest continuation IS the current session, that projected ID matches `current_session_id` and gets excluded by `query_session_listing()`.

**Result**: The root of a compression chain only appears when the user starts a NEW session (`/new`), making the previous chain inactive.

**This is by design.** One conversation chain = one list entry, pointing to the active tip. The user can always reach it via:
- `/resume LLM Wiki 主频道` — leaves the chain name, resumes the latest tip
- `hermes -r "LLM Wiki 主频道"` from CLI

### 11. HERMES_HOME vs HOME in cron scripts

When a no_agent cron script runs, `HOME` may point to the profile data
directory (e.g. `/opt/data/profiles/llm-wiki/home`), NOT the actual
user home. Always use `HERMES_HOME` environment variable to locate
`state.db`:

```python
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
DB_PATH = os.path.join(HERMES_HOME, "state.db")
```

Using `os.path.expanduser("~/.hermes")` alone in a cron context will
resolve to the wrong directory and silently miss the database.

## Cron Session Auto-Cleanup (no_agent pattern)

Agent-driven cron jobs create sessions with `cron_` ID prefix. These
accumulate rapidly (e.g., `auto-rebuild-graph` runs every 30 min → 48
sessions/day). Instead of manual cleanup, set up a periodic no_agent
script that deletes old cron sessions.

**Located in this skill:**
- `scripts/cleanup-cron-sessions.py` — executable cleanup script
- `references/cron-cleanup-pattern.md` — detailed pattern + pitfalls

Key details: the script connects to `$HERMES_HOME/state.db`, queries for
`cron_%` sessions older than a threshold (default 6 hours), and deletes
them via `hermes sessions delete`. Runs as a no_agent cron job (zero LLM
cost) with stdout delivered as a report.

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