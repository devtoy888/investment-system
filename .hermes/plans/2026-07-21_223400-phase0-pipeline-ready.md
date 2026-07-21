# Phase 0: Pipeline Ready (v0.1.0)

> 管线就绪：GitHub + D1 + Pages + schema + React scaffold

**目标：** 建立完整CI/CD管线，Git版本控制→Cloudflare生态全自动化部署

**确认资源：**
- ✅ Node v22.22.3 + npm 10.9.8
- ✅ Python 3.13.5 (venv)
- ✅ GITHUB_TOKEN (ghp_) ✓
- ✅ CLOUDFLARE_API_TOKEN (cfut_) ✓
- ❌ wrangler CLI 未安装
- ❌ gh CLI 未安装
- ❌ Git仓库未初始化

---

## 子任务清单

### Task 1: Git初始化 + GitHub仓库

**创建:** `.gitignore` — 排除venv/cache/logs/env/temp
**创建:** Git仓库 + 首次commit
**创建:** GitHub远程仓库（通过API）+ push

### Task 2: 安装wrangler CLI + 登录CF

安装wrangler via npm，用CF_TOKEN配置，创建D1数据库、Pages项目

### Task 3: 写schema.sql

6张D1表：portfolio_snapshots, fund_values, operations, signals, analysis_reports, market_data

### Task 4: 创建dashboard/ React脚手架

Vite + React 19 + TypeScript + Tailwind + ECharts
_redirects SPA路由 + 基本文件结构

### Task 5: Pages部署 + D1绑定

CF API→创建Pages项目→绑定D1→触发首次部署

### Task 6: 验证管线

curl线上URL 200 + D1可查询

---

## Verification

- [ ] `git log` 有初始commit
- [ ] GitHub上能看到仓库
- [ ] wrangler能列出D1数据库
- [ ] `schema.sql` 能在D1执行
- [ ] dashboard/ 中 `npm run build` 成功
- [ ] 线上URL返回200
