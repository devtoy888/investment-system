import sqlite3
conn = sqlite3.connect('/opt/data/profiles/investment/state.db')
cursor = conn.cursor()

# Find sessions with '看板' in the title
print("=== 搜索含'看板'的会话 ===")
cursor.execute("SELECT id, title, created_at, message_count FROM sessions WHERE title LIKE '%看板%' ORDER BY created_at DESC")
for row in cursor.fetchall():
    print(f'id: {row[0]}, title: {row[1]}, created: {row[2]}, msgs: {row[3]}')

# Also check all recent session titles
print("\n=== 最近20个会话 ===")
cursor.execute("SELECT id, title, created_at, message_count FROM sessions ORDER BY created_at DESC LIMIT 20")
for row in cursor.fetchall():
    print(f'id: {row[0]}, title: {row[1]}, created: {row[2]}, msgs: {row[3]}')
conn.close()
