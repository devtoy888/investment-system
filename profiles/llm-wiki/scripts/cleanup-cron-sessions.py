#!/usr/bin/env python3
"""Clean up cron-generated sessions in the llm-wiki profile.

Sessions with IDs starting with 'cron_' (from scheduled tasks) are deleted
if they are older than CLEANUP_AFTER_HOURS.
"""

import sqlite3
import os
import subprocess
from datetime import datetime, timezone

# Config
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
DB_PATH = os.path.join(HERMES_HOME, "state.db")
HERMES_BIN = "/opt/hermes/bin/hermes"
CLEANUP_AFTER_HOURS = 6  # Keep cron sessions younger than this

def main():
    if not os.path.exists(DB_PATH):
        print(f"[cleanup] DB not found: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Find cron sessions older than threshold
    now = datetime.now(timezone.utc).timestamp()
    cutoff = now - (CLEANUP_AFTER_HOURS * 3600)

    cur.execute(
        "SELECT id, title, started_at FROM sessions WHERE id LIKE 'cron_%' AND started_at < ?",
        (cutoff,)
    )
    sessions = cur.fetchall()
    conn.close()

    if not sessions:
        print(f"[cleanup] No stale cron sessions found (threshold: {CLEANUP_AFTER_HOURS}h)")
        return

    total_deleted = 0
    total_messages = 0

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
            total_deleted += 1
            print(f"  ✓ {ts} | {sid[:35]:35s} | {title or '(no title)'}")
        else:
            print(f"  ✗ {ts} | {sid[:35]:35s} | failed: {result.stdout.strip() or result.stderr.strip()}")

    print(f"\n[cleanup] Done: {total_deleted} cron session(s) deleted")


if __name__ == "__main__":
    main()
