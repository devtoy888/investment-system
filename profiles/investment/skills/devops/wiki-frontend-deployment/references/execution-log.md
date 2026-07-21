# LLM Wiki 部署执行日志

> 记录自 2026-07-09 起的实际部署过程、问题及解决方案

---

## Step 1: 目录结构创建（完成 ✅）

**操作**: `mkdir -p ~/llm-wiki/{raw/{articles,papers,transcripts,assets},entities,concepts,comparisons,queries,_archive,scripts}`

## Step 2: Git 初始化 + CNB 连接（完成 ✅）

### 问题：CNB Git 认证用户名
- 用户以为用自己 CNB 用户名
- 实际 CNB 文档要求固定 `cnb`
- 解决: `https://cnb:TOKEN@cnb.cool/org/repo`

### 问题：Token 暴露在 remote URL
- `git remote -v` 显示明文 token
- 解决方法1（未生效）: `git credential.helper store`
- 解决方法2（生效）: token 保留在 URL 中
- **待优化**: 后续改 credential store

### 问题：默认分支是 master
- 解决: `git branch -m master main`

## Step 3: Docker Compose + MkDocs 启动（完成 ✅）

### 问题：mkdocs.yml 不存在
- 症状: 容器不断重启
- 解决: 通过 hermes-main 容器创建文件到 /llm-wiki/mkdocs.yml

### 问题：MkDocs 要求 docs_dir 为子目录
- 尝试 `docs_dir: .` → 报错 "should not be the parent directory"
- 最终: 建 `docs/` 子目录，内容移入，mkdocs.yml 留在根目录

### 问题：wikilinks 插件未安装
- 官方镜像不带此插件
- 解决: 从 plugins 移除

### 最终状态
- 容器 `llm-wiki` 运行中，日志: `Serving on http://0.0.0.0:8456/`

## 待完成
- Cloudflare Tunnel 配置 wiki.devtoy.xyz
- Cron job 自动 git push
- MacBook Obsidian 同步
- Token 凭据优化
