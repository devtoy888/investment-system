#!/usr/bin/env python3
"""Delete specific sessions by ID."""
import sqlite3
db = "/opt/data/state.db"
targets = ["20260715_075816_922fee7a", "20260715_062710_52da323d"]
conn = sqlite3.connect(db)
cur = conn.cursor()
for sid in targets:
    cur.execute("SELECT title FROM sessions WHERE id=?", (sid,))
    row = cur.fetchone()
    title = row[0] if row else "(not found)"
    if not row:
        print(f"SKIP {sid}: not found")
        continue
    cur.execute("DELETE FROM messages WHERE session_id=?", (sid,))
    msg_count = cur.rowcount
    cur.execute("DELETE FROM messages_fts WHERE rowid IN (SELECT rowid FROM messages WHERE session_id=?)", (sid,))
    cur.execute("DELETE FROM sessions WHERE id=?", (sid,))
    conn.commit()
    print(f"DELETED id={sid} title='{title}' msgs={msg_count}")
conn.close()
print("DONE")
