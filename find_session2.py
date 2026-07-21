import sqlite3
conn = sqlite3.connect('/opt/data/profiles/investment/state.db')
cursor = conn.cursor()

# Check sessions table schema
cursor.execute("PRAGMA table_info(sessions)")
columns = cursor.fetchall()
print("=== sessions 表结构 ===")
for col in columns:
    print(col)

# Show all sessions
print("\n=== 所有会话 ===")
cursor.execute("SELECT * FROM sessions ORDER BY rowid DESC LIMIT 20")
for row in cursor.fetchall():
    print(row)
conn.close()
