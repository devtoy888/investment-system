---
name: feishu-platform-api
description: "Feishu (Lark) API integration: authentication, permission scopes, document/bitable/task creation, and profile-level credential location."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [feishu, lark, api, bot, permissions]
    category: devops
---

# Feishu Platform API

Feishu (Lark) API integration for creating documents, multidimensional tables (bitable), and tasks from Hermes Agent.

**Use this when**: You need to create Feishu docs, bitable records, or tasks programmatically; or when troubleshooting Feishu API permission issues.

---

## Credential Locations

Feishu credentials are stored in **profile-level** `.env`, NOT the default `/opt/data/.env`:

| Location | Purpose |
|----------|---------|
| `~/.hermes-main/profiles/<profile-name>/.env` | ✅ Current profile's Feishu credentials |
| `/opt/data/.env` | ❌ Default profile — may have wrong/old credentials |

**Always check the profile env first:**
```bash
cat /opt/data/profiles/llm-wiki/.env | grep FEISHU
```

## API Auth

```python
import requests
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': APP_ID, 'app_secret': APP_SECRET}, timeout=10)
token = resp.json()['tenant_access_token']
```

Token expires in 7200s (2 hours). Cache or re-fetch per operation batch.

## Required Scopes

### Document Operations

| Operation | Required Scope | Endpoint |
|-----------|---------------|----------|
| Create docx | `docx:document` | `POST /open-apis/docx/v1/documents` |
| Read drive | `drive:drive` or `drive:drive:readonly` | `GET /open-apis/drive/v1/files` |
| Write drive | `drive:drive` | Various drive/file endpoints |

### Multidimensional Table (Bitable)

| Operation | Required Scope | Endpoint |
|-----------|---------------|----------|
| Create bitable app | `bitable:app` | `POST /open-apis/bitable/v1/apps` |
| Add records | `bitable:app` | `POST /open-apis/bitable/v1/apps/:token/tables/:table_id/records` |

### Task/TODO

| Operation | Required Scope | Endpoint |
|-----------|---------------|----------|
| Create task | `task:task:write` or `task:task:writeonly` | `POST /open-apis/task/v2/tasks` |
| Read tasks | `task:task:readonly` | `GET /open-apis/task/v2/tasks` |

**⚠️ Note**: `task:task` (without `:write`) is NOT sufficient for creating tasks. The v2 API requires `task:task:write`.

## Granting Permissions

1. Go to open.feishu.cn → your app → **权限管理** → **API 权限列表**
2. Search for each scope name (e.g., `docx:document`)
3. Click "开通" (Enable)
4. **No need to publish version** — permissions take effect immediately for API calls
5. **Do NOT configure "应用能力" settings** (工作台小组件, 云文档小组件, 多维表格插件) — these are UI components for different use cases, unrelated to API access

## Usage Pattern (via Python execute_code)

Since Hermes does not ship native Feishu write tools (`feishu_doc_create`, `feishu_bitable_create`, `feishu_task_create`), use `execute_code` with the Feishu REST API:

```python
import requests

APP_ID = 'cli_xxx'
APP_SECRET = 'your_secret'

# Get token
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': APP_ID, 'app_secret': APP_SECRET}, timeout=10)
token = resp.json()['tenant_access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Create document
r = requests.post('https://open.feishu.cn/open-apis/docx/v1/documents',
    headers=headers, json={'title': 'Doc Title'}, timeout=10)
doc_token = r.json()['data']['document']['document_id']

# Add content to document — use block_type=2 for text, 5 for heading3
children = [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "Paragraph"}}], "style": {}}},
    {"block_type": 5, "heading3": {"elements": [{"text_run": {"content": "Section"}}], "style": {}}},
]
requests.post(
    f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children',
    headers=headers, json={'children': children}, timeout=10)

# Create bitable
r = requests.post('https://open.feishu.cn/open-apis/bitable/v1/apps',
    headers=headers, json={'name': 'My Table'}, timeout=10)
app_token = r.json()['data']['app']['app_token']

# Get table ID, add fields, add records
r = requests.get(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables',
    headers=headers, timeout=10)
table_id = r.json()['data']['items'][0]['table_id']

# Add select field with options
requests.post(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields',
    headers=headers, json={
        'field_name': '优先级', 'type': 3,
        'property': {'options': [{'name': 'P0', 'color': 1}, {'name': 'P1', 'color': 2}]}
    }, timeout=10)

# Add record
requests.post(f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records',
    headers=headers, json={'fields': {'优先级': 'P0', '优化项': 'Task'}}, timeout=10)

# Create task (v2 API) — ⚠️ MUST include members for user visibility
USER_OPEN_ID = 'ou_xxx'
r = requests.post('https://open.feishu.cn/open-apis/task/v2/tasks',
    headers=headers, json={
        'summary': 'Task title',
        'members': [{'id': USER_OPEN_ID, 'type': 'user', 'role': 'assignee'}]
    }, timeout=10)
task_guid = r.json()['data']['task']['guid']
```

## Initial Auth Test

```python
import requests
r = requests.get('https://open.feishu.cn/open-apis/drive/v1/files?page_size=1',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, timeout=10)
if r.json().get('code') == 0:
    print('Auth + drive permissions OK')
elif r.json().get('code') == 99991672:
    print(f'Missing scope: {r.json()["msg"]}')
```

## Pitfalls

### Profile-Level Env is NOT the Default Env

The profile's `.env` (`/opt/data/profiles/<profile>/.env`) is what the gateway reads, NOT `/opt/data/.env`. The default `.env` may have outdated or wrong credentials. Always check the profile path first.

### 应用能力 is NOT Needed for API Calls

**DO NOT** enable 工作台小组件, 云文档小组件, or 多维表格插件 — these are UI components that embed the bot into Feishu app interfaces. API permissions (like `docx:document`) are configured separately under 权限管理 → API 权限列表.

### task:task vs task:task:write

The v1 task API (`task/v1/tasks`) requires `task:task`, but field validation is picky. The v2 task API (`task/v2/tasks`) is simpler but requires `task:task:write`. If both fail:
- v1 `field validation failed`: check payload structure (needs exact field names)
- v2 `Access denied`: missing `task:task:write` scope

### Permissions Don't Require Re-Publish

Unlike events and bot configuration changes, **API permission scope changes take effect immediately** — no need to create and publish a new version. This was confirmed via testing.

### ⚠️ Bitable Record Update — Use Field Display Names, NOT Field IDs

When updating or creating bitable records, the `fields` key MUST use the **display name** (e.g., `"优化项"`), **not the field ID** (e.g., `"fldDj7CzqF"`). Passing field IDs returns `FieldNameNotFound` (code 1254045):

```python
# ✅ Correct — use display names
payload = {
    "fields": {
        "优化项": "任务描述",
        "状态": "已完成",
        "优先级": "P0"
    }
}

# ❌ Wrong — field IDs return 1254045
payload = {
    "fields": {
        "fldDj7CzqF": "任务描述",     # ← error!
    }
}
```

For single-select fields, pass the **option display name** as a string, not the option ID:
```python
"状态": "已完成"          # not "opt4qph3GV"
"优先级": "P0"             # not "optKGkptWj"
```

Use `GET .../fields` to discover field display names and their option names, then use those same names when writing.

### :warning: Bitable: Find Before Create — NEVER Blind-Insert a New Record

When asked to "update the multidoc table" or "mark a task complete", the correct workflow is:

1. **READ ALL RECORDS FIRST** — find the matching record by its task/optimization item field
2. **UPDATE the existing record** — change its status field using its `record_id`
3. **NEVER create a new record** unless the task genuinely doesn't exist

```python
# ✅ Correct workflow: find then update
r = requests.get(f'.../apps/{app_token}/tables/{table_id}/records',
    params={'page_size': 50}, headers=headers)
records = r.json()['data']['items']

target = None
for rec in records:
    fields = rec.get('fields', {})
    if fields.get('优化项', '').startswith('修复交互式图谱'):
        target = rec['record_id']
        break

if target:
    requests.put(f'.../apps/{app_token}/tables/{table_id}/records/{target}',
        headers=headers, json={'fields': {'状态': '已完成'}})
```

**Why this matters**: The bitable likely has pre-existing tasks from a previous session. Creating a duplicate "已完成" row while the original stays "待完成" confuses the user. Always use the existing record's `record_id`.

**How to identify existing records**:
- Match by task name prefix: `fields.get('优化项','').startswith('修复')`
- Match by priority + description combination
- List all bitables via `drive/v1/files?type=bitable` and search by name if you lost the token

### 404 on Bitable v1 APIs

The bitable v1 API (`/open-apis/bitable/v1/apps`) may return 404 for some query patterns. The create endpoint (`POST .../v1/apps`) works. For listing existing apps, try the app-specific token endpoint.
