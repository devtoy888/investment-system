---
name: wiki-frontend
description: "Deploy and visualize LLM Wiki content on the web: MkDocs Material, knowledge graphs, storage architecture, and CI/CD."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [wiki, frontend, mkdocs, graph, visualization, knowledge-graph]
    category: research
    related_skills: [llm-wiki, obsidian]
---

# Wiki Frontend

Serve, visualize, and publish an LLM Wiki (Karpathy pattern) as a web-accessible site with interactive knowledge graphs. Companion skill to `llm-wiki` — that skill handles content creation and curation; this one handles the serving and visualization layer.

## When This Skill Activates

Use this skill when the user:
- Asks to deploy a web frontend for their wiki
- Asks about graph visualization, knowledge graphs, or "Graphify" for their wiki
- Asks where wiki data is stored or how the frontend accesses it
- Needs to set up a domain/SSL (Cloudflare Tunnel) for wiki access
- Wants git backup, sync, or CI/CD for wiki content
- Asks about storage architecture for large wiki files

## Core Architecture

The wiki frontend has **no database**. All data lives in the wiki directory as markdown files:

```
~/wiki/ (唯一数据源 — 文件系统)
├── entities/deepseek.md   → MkDocs 实时读取 → /entities/deepseek/
├── concepts/attention.md  → MkDocs 实时读取 → /concepts/attention/
├── mkdocs.yml             → 站点配置
├── _graph/                → Graphify 图谱（可选）
└── site/                  → mkdocs build 静态文件（仅 build 模式产生）
```

MkDocs Material 在 `mkdocs serve` 模式下：
- 从磁盘实时读取 markdown
- 搜索索引在启动时构建于内存
- 文件变更即时生效，无需重启容器

## Frontend Framework: MkDocs Material

### Why MkDocs Material

| 框架 | 镜像体积 | Markdown 原生 | 内置搜索 | 图谱可视化 |
|------|---------|-------------|---------|-----------|
| **MkDocs Material** | ~120MB | ✅ 原生 | ✅ 中文 | ✅ 插件 |
| Astro | Node.js 重 | ✅ 原生 | 需插件 | 需自建 |
| Vitepress | Node.js 重 | ✅ 原生 | ✅ | 需自建 |

### Docker Compose Deployment

```yaml
services:
  wiki-web:
    image: squidfunk/mkdocs-material:latest
    container_name: llm-wiki
    restart: unless-stopped
    volumes:
      - ~/wiki:/docs
    ports:
      - "127.0.0.1:8000:8000"
    command: ["serve", "--dev-addr", "0.0.0.0:8000"]
```

> **Docker volume 映射**: wiki 目录通过 volume 从宿主机映射到容器。在 Hermes Docker 容器中也映射同一个目录，Agent 写入的 markdown 即时反映到前端。

### mkdocs.yml 模板

```yaml
site_name: My Wiki
site_url: https://wiki.example.com
theme:
  name: material
  language: zh
  features:
    - navigation.instant
    - search.suggest
    - content.code.copy
markdown_extensions:
  - pymdownx.superfences
  - pymdownx.tabbed
  - footnotes
plugins:
  - search
  - wikilinks
  - graph:                    # 页面关系图谱
      name: "title"
```

## Graph Visualization

Two approaches depending on requirements:

### Approach A: mkdocs-network-graph-plugin (推荐优先)

A MkDocs plugin that auto-generates an interactive network graph from `[[wikilinks]]`:

```bash
pip install mkdocs-network-graph-plugin
```

```yaml
plugins:
  - graph:
      name: "title"    # "title" or "file_name"
```

Features:
- Zero configuration — reads existing `[[wikilinks]]` between pages
- Nodes = pages, edges = wiki links
- Interactive: click nodes to jump, hover for preview, color-coded
- Embedded directly in MkDocs site (no separate page needed)
- Customizable via CSS variables

**Customization:**
```css
:root {
  --md-graph-node-color: #1976d2;
  --md-graph-node-color--hover: #1565c0;
  --md-graph-node-color--current: #ff5722;
  --md-graph-link-color: #757575;
}
```

Installation in Docker: use a custom entrypoint script that pip-installs before mkdocs serve, or a custom Dockerfile.

### Approach B: Graphify (进阶可选)

[Graphify](https://github.com/Graphify-Labs/graphify) — `pip install graphifyy` — is a standalone knowledge graph tool that builds semantic graphs from content.

```bash
graphify ./raw --output _graph --no-viz
```

Output:
```
~/wiki/_graph/
├── graph.html        # Interactive visualization (browser-ready)
├── graph.json        # Queryable graph data (NetworkX)
└── GRAPH_REPORT.md   # God nodes, surprising connections, communities
```

Features (beyond plugin):
- **Leiden community detection** — auto-clusters content into "knowledge neighborhoods"
- **God Nodes** — most-connected concepts (what everything flows through)
- **Surprising Connections** — unexpected cross-domain links
- **Confidence scoring** — EXTRACTED vs INFERRED vs AMBIGUOUS edges

**Cron job for automatic updates:**

```bash
docker exec hermes hermes cron create \
  --schedule "0 4 * * *" \
  --name "wiki-graphify" \
  --no-agent \
  --script /opt/data/scripts/wiki-graphify.sh
```

Script (`wiki-graphify.sh`):
```bash
#!/bin/bash
cd /wiki
pip install graphifyy -q 2>/dev/null || true
graphify ./raw --output _graph --no-viz
echo "Graphify update: $(date)"
```

### Comparison

| 特性 | Plugin | Graphify | ECharts 独立页 |
|------|--------|----------|----------------|
| 安装 | `pip install mkdocs-network-graph-plugin` | `pip install graphifyy` | CDN 零安装 |
| 数据源 | `[[wikilinks]]` 页面链接 | 内容语义分析 + LLM | graph.json |
| 输出 | 内嵌 MkDocs 页面 | 独立 `graph.html` | 独立 HTML |
| 社区检测 | ❌ | ✅ Leiden | ✅（显示已有社区）|
| God Nodes | ❌ | ✅ | ❌ |
| 资源消耗 | 极低 | 中等（调用 LLM）| 极低 |
| 兼容性 | 需插件安装 | 需 cron + LLM | ✅ 任何 MkDocs 版本 |
| 交互性 | 页面内嵌 | 独立页面 | 拖拽/缩放/高亮 |

**Recommendation**: 
1. Start with **ECharts 独立页**（零安装，立即可用，跨版本兼容）
2. Add Graphify for semantic analysis if needed (god nodes, community detection)
3. Avoid `obsidian-interactive-graph` plugin — 已被 MkDocs 2.0 迁移废弃，在 MkDocs Material 9.x 上不可用

### Approach C: Standalone ECharts Page (推荐)

Zero-installation interactive graph viewer using ECharts CDN. No MkDocs plugin, no pip install, no Dockerfile changes.

**Setup:**

```bash
# 1. Create viewer directory
mkdir -p docs/concepts/graph-viewer

# 2. Copy content from reference file
cp /path/to/interactive-graph-viewer.md # 参考下面的 HTML 模板

# 3. After Graphify rebuild, copy output files
cp graphify-out/graph.svg docs/images/knowledge-graph.svg
cp graphify-out/graph.json docs/images/graph-data.json

# 4. Restart MkDocs to serve new files
docker restart llm-wiki
```

**HTML 模板** (place at `docs/concepts/graph-viewer/index.html`):

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Knowledge Graph</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>*{margin:0;padding:0}body{background:#0d1117;overflow:hidden}#g{width:100vw;height:100vh}</style>
</head>
<body><div id=g></div>
<script>
fetch("../../images/graph-data.json").then(r=>r.json()).then(d=>{
const C=["#f97316","#8b5cf6","#06b6d4","#10b981","#ef4444","#3b82f6"];
const cats=Object.entries(Object.fromEntries(d.nodes.map(n=>[n.community,n.community_name||("C"+n.community)])))
  .map(([i,n])=>({name:n,itemStyle:{color:C[i%6]}}));
const nds=d.nodes.map(n=>({id:n.id,name:n.label||n.id,category:n.community||0,symbolSize:22,itemStyle:{color:C[(n.community||0)%6]}}));
const lks=d.links.map(l=>({source:l.source,target:l.target}));
const ch=echarts.init(document.getElementById("g"));
ch.setOption({backgroundColor:"#0d1117",series:[{type:"graph",layout:"force",roam:true,data:nds,links:lks,categories:cats,force:{repulsion:300,edgeLength:100,gravity:0.1},label:{show:true,position:"right",fontSize:10,color:"#8b949e"},lineStyle:{opacity:0.5},emphasis:{focus:"adjacency"}}]});
window.addEventListener("resize",()=>ch.resize())});
</script></body></html>
```

**Path rules:**
- `/concepts/graph-viewer/` ← 访问路径（MkDocs 自动将 `docs/concepts/graph-viewer/index.html` 路由到此）
- `../../images/graph-data.json` ← 从 viewer 页访问 graph.json 的相对路径
- ECharts 从 CDN 加载，无需任何本地文件

## Storage Architecture

### Two-Tier Storage

| Tier | Media | Content | Access |
|------|-------|---------|--------|
| **Hot** | Local disk | Markdown text, small images | Agent: instant. Frontend: real-time. |
| **Cold** | R2/S3 | Large images (>1MB), PDFs | Via CDN URL in markdown |

**Markdown stays local** — it's space-efficient (~1-3MB per 100 pages) and fast.  
**Large binaries go to R2** — Agent uploads during ingest and stores the URL.

### R2 Integration

```python
from r2_uploader import R2Uploader  # Use existing project R2Uploader

def ingest_large_file(path, key_prefix="wiki-assets"):
    if os.path.getsize(path) > 1_000_000:  # >1MB
        uploader = R2Uploader()
        url = uploader.upload_file(path, f"{key_prefix}/{os.path.basename(path)}")
        os.remove(path)  # Free local disk
        return url  # Store this URL in the wiki markdown
    return None  # Keep local
```

**Experience impact**: Near-zero. CDN-cached images load in 50-200ms. Markdown full text is always local for instant Agent queries.

## Git Sync and CI/CD

### CNB / GitHub Integration

```bash
cd ~/wiki
git init
git remote add origin https://your-git-host.com/user/wiki.git
git add -A && git commit -m "init"
git push origin main
```

### Cron Job for Auto-Sync

```bash
0 3 * * * cd ~/wiki && \
  if [ -n "$(git status --porcelain)" ]; then \
    git add -A && \
    git commit -m "auto sync $(date +%Y-%m-%d)" && \
    git push origin main; \
  fi
```

### .gitignore (exclude large binaries)

```gitignore
*.pdf
*.png
*.jpg
*.jpeg
raw/assets/*
!raw/assets/.gitkeep
_graph/
site/
```

## Cloudflare Tunnel (Domain/SSL)

If the server has no public IP / no port 80/443, use Cloudflare Tunnel:

```
Cloudflare Dashboard → Access → Tunnels → your-tunnel → Add Public Hostname
  Subdomain: wiki
  Domain: your-domain.com
  Type: HTTP
  URL: localhost:8000
```

No open ports needed. Automatic SSL. Optional Access Group authentication.

## Obsidian Compatibility

The wiki directory works as an Obsidian vault out of the box:

| Setting | Value |
|---------|-------|
| Open as vault | `File → Open folder as vault → ~/wiki` |
| Attachment folder | `raw/assets/` |
| Wikilinks | ✅ Enable |
| Dataview plugin | Install for tag/type queries |
| Graph View | Native `[[wikilinks]]` rendering |

## Pitfalls

- **MkDocs serve 模式 vs build 模式**: `serve` 模式实时读磁盘，文件变更即时生效。`build` 模式生成静态 HTML 到 `site/`，每次内容更新后需重新 build。对 Agent 动态写入的场景，**永远用 serve 模式**。
- **mkdocs-network-graph-plugin 需要安装**: 官方 MkDocs 镜像不包含此插件。方案：自定义 entrypoint 脚本 `pip install && exec mkdocs serve`。
- **`obsidian-interactive-graph` 插件已废弃**: 在 MkDocs Material 9.x 上配置该插件会导致 `The "obsidian-interactive-graph" plugin is not installed` 错误退出。MkDocs 2.0 已移除插件系统，该插件不再兼容。**替代方案**: ECharts 独立 HTML 页（见 Approach C）。
- **不要 git commit 大文件**: 确保 `.gitignore` 排除了图片和 PDF，否则 git 历史会膨胀到撑满磁盘。
- **中文搜索**: MkDocs Material 内置搜索支持中文，但如果体验不佳，可以加 `mkdocs-jieba-plugin` 或启用 `lang: zh` 配置。
- **Graphify LLM token 消耗**: Graphify 会对内容调用 LLM 提取语义，每天一次 cron job 消耗可预测。如果不希望额外消耗，只用 plugin 即可。
- **多 Profile 共享 wiki**: 所有 Hermes profile 共享同一 `~/wiki` 目录，只需统一设置 `WIKI_PATH` 环境变量。并发写入风险极低（markdown append/write 模式）。
- **Graphify 输出需手动复制**: 构建后必须将输出文件复制到 MkDocs 可访问的位置:
  ```bash
  cp graphify-out/graph.svg docs/images/knowledge-graph.svg
  cp graphify-out/graph.json docs/images/graph-data.json
  ```
  MkDocs `--dirty` 模式自动检测并重新渲染；生产环境需 `docker restart llm-wiki`。
- **SVG Lightbox 可以通过嵌入原始 HTML+JS 实现**: MkDocs Material 的 `--dirty` 模式和 `mkdocs serve` 不会剥离 markdown 文件中的 `<script>` 和 HTML 事件属性。可以嵌入完整的 lightbox 实现（含缩放/平移/重置按钮），方法：
  - 在 `.md` 文件中直接写 `<div>` + `<script>` 块
  - Lightbox 需要：图片预览区、点击打开的遮罩层、缩放按钮（+/-/↺）、鼠标滚轮缩放（阻止冒泡到背景页面）、拖拽平移、键盘快捷键（Esc/+/-/0）
  - 注意遮罩层 `position:fixed;overflow:hidden` 阻止背景滚动
  - 参见 `references/lightbox-template.md` 完整实现
- **MkDocs serve 模式下静态文件变更需重启容器**: `--dirty` 模式只重新渲染 markdown 页面变更，不自动检测 `docs/images/` 下的静态文件（SVG、JSON 等）。Graphify 重建后如果 SVG/JSON 变了，必须执行 `docker restart llm-wiki` 才能生效。浏览器可能需要 Ctrl+Shift+R 强制刷新。
- **修改后必须自动验证**: 每次修改页面或生成新 SVG/JSON 后，应运行验证脚本检查：
  - SVG 路径（确认 WenQuanYiZenHei 或 CJK 字体嵌入，而非 DejaVuSans）
  - 页面板块完整性（图谱概览、社区分类、可视化文件等）
  - Lightbox 组件的完整性（缩放/重置/关闭函数 + 滚轮事件 + 键盘快捷键）
- **Docker 中自定义 entrypoint 需谨慎**: 尝试在 `squidfunk/mkdocs-material` 容器中使用自定义 Python venv 的 entrypoint（如 `["/docs/scripts/.graphify-venv/bin/python3", "-m", "mkdocs"]`）可能因路径不匹配导致 `OCI runtime create failed`。推荐做法：
  - 默认 entrypoint + command（不开插件）→ 最稳定
  - 需插件时 → 自定义 Dockerfile 打包
  - 交互图谱 → ECharts 独立页（零依赖）
- **ECharts 图谱页的路径结构**: 
  ```
  docs/concepts/graph-viewer/index.html  → 访问 /concepts/graph-viewer/
  docs/images/graph-data.json             → ECharts 从 ../../images/graph-data.json 加载
  ```
  `index.html` 在 `graph-viewer/` 目录下，MkDocs 自动将其作为页面路由。注意不要用 `knowledge-graph/graph-viewer/` 路径——MkDocs 不会将子目录嵌套当作同一页面的子路由。

## Related Skills

- `llm-wiki` — Build and maintain the wiki content (this skill covers the serving layer)
- `obsidian` — Obsidian vault integration for desktop reading

## References

- `references/graphify-integration.md` — Detailed Graphify setup, cron job, and frontend embedding
- `references/mkdocs-deployment-docker.md` — Full Docker Compose configuration with graph plugin entrypoint
- `references/r2-wiki-storage.md` — R2 cold-storage integration for wiki large files
