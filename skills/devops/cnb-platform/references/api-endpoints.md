# CNB API Endpoints Reference

## Verified Endpoints (tested 2026-06-25)

### User Info
```
GET /user
```
```json
{
  "id": "1871918567745507328",
  "username": "devtoy",
  "nickname": "赵小杰",
  "type": 0,
  "verified": 1,
  "verified_expire_in": "2026-12-25T14:00:44Z",
  "created_at": "2024-12-25T13:59:00Z",
  "email": "devtoy@163.com",
  "group_count": 1,
  "repo_count": 29,
  "mission_count": 1,
  "public_repo_count": 8,
  "public_mission_count": 1
}
```

### User Groups / Orgs
```
GET /user/groups
```
Returns array of organizations, each with:
- `id`, `name`, `path`, `domain`, `access_role` (Owner/Member etc)
- `sub_repo_count`, `all_sub_repo_count`
- `created_at`, `updated_at`

### User Repositories
```
GET /user/repos?page=1&page_size=50
```
Each repo includes:
- `name`, `path` (org/repo-name), `web_url`
- `visibility_level`: "Secret" | "Private" | "Public"
- `flags`: "Unknown" | "NPC" (has NPC configured)
- `description`, `languages`, `open_issue_count`, `open_pull_request_count`
- `created_at`, `updated_at`, `last_updated_at`
- `forked_from_repo` (present if forked)
- `access`: "Owner" | "Admin" | "Developer" etc

### Repository Events
```
GET /events/{org}/{repo}/-/{date}
```
Date format: `yy-mm-dd` (daily) or `yy-mm-dd-h` (hourly).
Daily queries have 1-day lag.

## OpenAPI Spec

- URL: https://api.cnb.cool
- Auth: Bearer token
- Requires `Accept: application/json` header
- Categorized schemas include: Repository, Git, Pull Request, Issue, Release, Build Pipeline, Workspace, Knowledge Base, Container Registry, Search

## Endpoint Patterns from OpenAPI Spec (文档提到但未全部验证)

- `/user/*` — user info, groups, repos
- `/events/*` — repository events
- `/repos/*` — repository CRUD, content management
- `/builds/*` — pipeline, logs, status
- `/workspaces/*` — dev environment management
- `/knowledge/*` — knowledge base queries

## HTTP Status / Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 404 | Resource not found (check path/org name) |
| errcode:5 | Resource not found |
| errcode:16 | Not logged in / auth issue |
