#!/usr/bin/env python3
"""Clean up cron-generated sessions.

Sessions with IDs starting with 'cron_' (from scheduled tasks) are deleted
if they are older than CLEANUP_AFTER_HOURS.

Designed to be run as a no_agent cron job. When run this way, stdout
is delivered verbatim to the user's chat channel as a brief report.

Usage:
    python3 /path/to/cleanup-cron-sessions.py

Cron job config:
    schedule: 0 */6 * * *
    script: cleanup-cron-sessions.py
    no_agent: true
    deliver: <channel>
"""

import sqlite3
import os
import subprocess
from datetime import datetime, timezone

# ── Config ─────────────────────────────────────────────────
CLEANUP_AFTER_HOURS = 6   # Keep cron sessions younger than this
HERMES_BIN = "/opt/hermes/bin/hermes"

# HERMES_HOME is preferred; fall back to ~/.hermes
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
DB_PATH = os.path.join(HERMES_HOME, "state.db")


def main():
    if not os.path.exists(DB_PATH):
        print(f"[cleanup-cron] DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.now(timezone.utc).timestamp()
    cutoff = now - (CLEANUP_AFTER_HOURS * 3600)

    cur.execute(
        "SELECT id, title, started_at FROM sessions "
        "WHERE id LIKE 'cron_%' AND started_at < ?",
        (cutoff,),
    )
    sessions = cur.fetchall()
    conn.close()

    if not sessions:
        print(f"[cleanup-cron] No stale cron sessions (threshold: {CLEANUP_AFTER_HOURS}h)")
        return

    total = 0
    for sid, title, started_at in sessions:
        ts = datetime.fromtimestamp(started_at, tz=timezone.utc).strftime("%m-%d %H:%M")
        result = subprocess.run(
            [HERMES_BIN, "sessions", "delete", sid],
            input="y\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "Deleted" in result.stdout:
            total += 1
            print(f"  ✓ {ts} | {sid[:35]:35s} | {title or '(no title)'}")
        else:
            print(f"  ✗ {ts} | {sid[:35]:35s} | {result.stdout.strip() or result.stderr.strip()}")

    print(f"\n[cleanup-cron] Done: {total} cron session(s) deleted")


if __name__ == "__main__":
    main()
