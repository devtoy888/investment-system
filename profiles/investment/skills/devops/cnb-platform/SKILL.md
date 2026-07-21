---
name: cnb-platform
description: >-
  CNB (Cloud Native Build) 腾讯云原生研发平台集成 — 代码托管, Open API, Git操作, CI/CD, 资源管理。
  MUST USE when user references cnb.cool, devtoy.cn, NPC, CodeBuddy, 或云原生构建/开发。
triggers:
  - cnb: cnb.cool/cloud native build/云原生构建/腾讯云原生研发平台
  - devtoy: devtoy/devtoy.cn
  - npc: NPC/CodeBuddy/云端智能体
  - code: 代码托管/cnb仓库/npc开发
  - resource: 核时/用量/免费额度/储存空间
metadata:
  platform: cnb.cool
  api_base: https://api.cnb.cool
  org: devtoy
---

# CNB Platform Integration

## Quick Reference

| Item | Value |
|------|-------|
| **Platform** | https://cnb.cool |
| **API** | https://api.cnb.cool (Bearer token) |
| **Org** | `devtoy` (Owner) |
| **Domain** | devtoy.cn |
| **API token env** | `CNB_ACCESS_TOKEN` (27 chars, from `.env`) |
| **Git username** | `cnb` (固定值, 平台规定) |
| **Git password** | `CNB_ACCESS_TOKEN` |
| **User** | devtoy (赵小杰, devtoy@163.com) |

## Required Env Vars

User adds these to `.env` — agent reads via `os.environ.get()`:

```bash
CNB_GIT_USERNAME=cnb           # Git认证用户名（固定值）
CNB_ACCESS_TOKEN=xxx            # 个人访问令牌，用于 API + Git
```

## Working API Endpoints (已验证)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/user` | GET | 用户信息 (id, email, repo_count 等) |
| `/user/groups` | GET | 组织列表 (Owner权限) |
| `/user/repos` | GET | 全量仓库列表 (含 Secret/Private/Public) |
| `/events/{path}/-/{date}` | GET | 仓库事件 (yyyy-mm-dd 格式) |

未验证但文档有: 文件CRUD, PR/Issue, CI/CD 流水线。

## Authentication

```bash
# API call
curl -s "https://api.cnb.cool/user" \
  -H "Authorization: Bearer $CNB_ACCESS_TOKEN" \
  -H "accept: application/json"

# Git operations
git clone https://cnb.cool/devtoy/repo-name.git
# Username: cnb
# Password: (your CNB_ACCESS_TOKEN)
```

## Free Resource Tiers (社区版)

| 资源 | 免费额度 | 计费标准 |
|------|---------|---------|
| 仓库存储 (Git) | 100 GiB | 1元/GiB/月 |
| 对象存储 (制品/LFS) | 100 GiB | 1元/GiB/月 |
| 云原生构建-CPU | 160 核时/月 | 0.125元/核时 |
| 云原生开发-CPU | 1600 核时/月 | 0.125元/核时 |
| AI Credits (NPC等) | 500 credits/月 | 0.05元/credit |

用量查看: 登录后 `组织 → 设置 → 用量管理`

## NPC / Skills 系统

- NPC = 仓库专属 AI 助手，通过 `.cnb/settings.yml` 配置
- Skills = NPC 的工具包，基于 OpenAPI
- 官方 Skills 仓库: `cnb/skills/cnb-skill`
- 自定义 Skills: `.codebuddy/skills/<name>/SKILL.md`
- 安装: `npm install -g @cnbcool/cnb-cli skills && npx skills add <repo-url>`

## Repo Visibility Levels

| Level | Prefix | Count |
|-------|--------|-------|
| Secret | `*-env-keys` | 存密钥配置 |
| Private | `hermes-deploy`, `font-split-service` 等 | 项目代码 |
| Public | `hello-cnb`, `vibe-agent-course` | 公开项目 |

## Pitfalls

1. **Token 安全** — 不要求用户直接在聊天中告知 token 值 (见 `secure-credential-usage` skill)。定义好 env var name，让用户自行配置到 `.env`。
2. **Groups API** — `GET /groups/{name}` 和 `GET /groups/{id}` 均返回 404。获取组织信息只能用 `GET /user/groups`。
3. **Web UI** — 浏览器访问需要登录(微信扫码/Passkey)，用量管理页面无法通过未认证的浏览器访问。
4. **构建节点** — 支持 amd64 和 arm64/v8，CPU 1-64 核可选，最大运行时间 20 小时(构建)/18 小时(开发)。
5. **工作区回收** — 云原生开发空间闲置自动回收(心跳检测)，最长保留 18 小时。
6. **Token 含特殊字符导致 shell URL 解析失败** — 测试 Git 访问时，`git ls-remote https://cnb:{token}@cnb.cool/...` 可能因 token 中含 `/` 或 `.` 等特殊字符导致 `URL rejected: Port number was not a decimal number` 错误。应使用 Python 测试（避免 shell 解析），或在 shell 中用 `git credential.helper store` 方式写入凭证后测试。详见 `references/git-credential-patterns.md`。
7. **Credential store 的 heredoc 问题** — `git credential-store --file ~/.git-credentials store <<< '...'` 在 Termius 粘贴多行时可能卡在 `quote>` 状态。改用 `printf '...\n...\n' | git credential-store` 方式。

## See Also

- [references/api-endpoints.md](references/api-endpoints.md) — 详细 API 端点和响应示例
- [references/git-credential-patterns.md](references/git-credential-patterns.md) — Git 凭据管理实战模式
- `secure-credential-usage` skill — 凭据处理规范
- 官方文档: https://docs.cnb.cool
- OpenAPI spec: https://api.cnb.cool
