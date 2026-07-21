import sqlite3
conn = sqlite3.connect('/opt/data/profiles/investment/state.db')
cursor = conn.cursor()

# Search for sessions with titles containing 看板 or 设计
cursor.execute("SELECT id, title, started_at, message_count FROM sessions WHERE title LIKE '%看板%' OR title LIKE '%设计%' ORDER BY started_at DESC")
results = cursor.fetchall()
print(f"找到 {len(results)} 个匹配会话:")
for row in results:
    print(f"  id: {row[0]}")
    print(f"  title: {row[1]}")
    print(f"  started: {row[2]}")
    print(f"  msgs: {row[3]}")
    print()

conn.close()
