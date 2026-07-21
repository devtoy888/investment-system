# Feishu NULL chat_id 修复方案

## 问题

Hermes Feishu 适配器中，早期创建的会话 `chat_id=NULL`，导致 `_resume_target_allowed()`（`gateway/slash_commands.py` 第 864 行）的 IDOR 守卫拦截。

现象：用户在飞书发 `/sessions` 或 `/resume`（无参数），回复 "No sessions found"，但数据库里确实有会话。

## 诊断

```python
import sqlite3
conn = sqlite3.connect("/opt/data/profiles/<profile>/state.db")
cur = conn.cursor()
cur.execute("SELECT id, title, chat_id, thread_id, user_id, source FROM sessions WHERE source='feishu' ORDER BY started_at DESC")
for r in cur.fetchall():
    print(f"{r[0]:<36} {(r[1] or 'None'):<30} chat_id={(r[2] or 'NULL')}")
conn.close()
```

## 修复 SQL

```sql
UPDATE sessions 
SET chat_id = '<caller_chat_id>', chat_type = 'dm'
WHERE source = 'feishu' AND (chat_id IS NULL OR chat_id = '') AND user_id = '<caller_user_id>';
```

- `<caller_chat_id>` — 从已有 chat_id 的会话获取（格式 `oc_xxxx`）
- `<caller_user_id>` — 飞书 open_id（格式 `ou_xxxx`），从已有会话获取

## 为什么其他平台没问题

| 平台 | user_id_alt | 旧会话受影响 | 原因 |
|------|-------------|-------------|------|
| Feishu | ✅ union_id | ✅ | 第 864 行：`caller_keys_on_alt and not(row_chat and caller_chat)` → chat_id=NULL 被拦截 |
| QQ Bot | ❌ | ❌ | 第 866 行：直接比较 user_id，chat_id 不影响 |
| Telegram | ❌ | ❌ | 同上 |

## 原理

```python
# 仅 Feishu（设了 user_id_alt）走这条路径
if caller_keys_on_alt and not (bool(row_chat) and bool(caller_chat)):
    return False
return bool(row_uid) and row_uid == caller_uid and row_chat == caller_chat
```

旧会话：`bool(row_chat)=False` → `not(False and True)`=True → 拦截。
修复后：`bool(row_chat)=True` → `not(True and True)`=False → 走到 `row_chat == caller_chat` → 通过。

## 不需要重启网关

`list_sessions_rich()` 每次请求都执行 SQL 查询，直接读 SQLite 文件。
