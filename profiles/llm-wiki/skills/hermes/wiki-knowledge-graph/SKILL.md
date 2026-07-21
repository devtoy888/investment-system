---
name: wiki-knowledge-graph
description: Build and maintain a knowledge graph for LLM Wiki content using Graphify. Covers installation, extraction, community detection (Leiden algorithm), visualization export, and cron-based auto-rebuild.
author: Hermes Agent
scripts:
  - build-graph.py — Full graph rebuild script at /llm-wiki/scripts/build-graph.py
references:
  - graphify-setup.md — Graphify installation, first-run extraction, and troubleshooting
---

# Wiki Knowledge Graph (Graphify)

Build an interactive knowledge graph from LLM Wiki markdown content using the [Graphify](https://graphify.net/) library. Automatically detects topic communities (Leiden algorithm), identifies core concepts, and exports visualizations.

## Architecture

```
docs/**/*.md  (markdown content)
      │
      ▼ (1) extract  ──  extract_nodes_edges() per file
      │
      ▼ (2) build    ──  NetworkX graph (nodes + edges)
      │
      ▼ (3) cluster  ──  Leiden algorithm → community detection
      │
      ▼ (4) export   ──  SVG / JSON / Canvas / Obsidian notes
```

## Prerequisites

- Graphify virtualenv at `/llm-wiki/scripts/.graphify-venv/` (created by `uv venv && uv pip install graphifyy`)
- Write permission to `/llm-wiki/graphify-out/`
- Wiki content under `/llm-wiki/docs/`

## Step-by-Step

### 1. Install Graphify

```bash
cd ~/llm-wiki
uv venv scripts/.graphify-venv
source scripts/.graphify-venv/bin/activate
uv pip install graphifyy
graphify install
```

### 2. First Run — Extract & Build

```bash
cd ~/llm-wiki
source scripts/.graphify-venv/bin/activate
mkdir -p graphify-out

python3 -c "
from pathlib import Path
from graphify import extract, build, cluster, export
import json

# Collect all markdown files
paths = list(Path('docs').glob('**/*.md'))
print(f'Found {len(paths)} files')

# Extract
result = extract.extract(paths, parallel=True)
with open('graphify-out/extraction.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False)

# Build graph
G = build.build([result], root=str(Path('.').resolve()))
clusters = cluster.cluster(G)

# Label communities
labels = {}
for cid, members in sorted(clusters.items(), key=lambda x: -len(x[1])):
    from collections import Counter
    src = [m.split('_')[0] for m in members if '_' in m]
    common = Counter(src).most_common(1)
    labels[cid] = common[0][0] if common else str(cid)

# Export all formats
export.to_json(G, clusters, 'graphify-out/graph.json', community_labels=labels)
export.to_svg(G, clusters, 'graphify-out/graph.svg', community_labels=labels)
export.to_canvas(G, clusters, 'graphify-out/graph.canvas', community_labels=labels)
export.to_obsidian(G, clusters, 'graphify-out/obsidian', community_labels=labels)

print(f'Done: {G.number_of_nodes()} nodes / {G.number_of_edges()} edges / {len(clusters)} communities')
"
```

### 3. Rebuild (Automated)

Use the build script at `/llm-wiki/scripts/build-graph.py` for cron jobs:

```bash
source /llm-wiki/scripts/.graphify-venv/bin/activate
python3 /llm-wiki/scripts/build-graph.py
```

## Output Files

| File | Location | Purpose |
|------|----------|---------|
| graph.json | graphify-out/graph.json | Structured graph data (nodes/edges/communities). **After build, run `enrich-graph.py` to add EXTRACTED (wikilink) + LIKELY (precise-subdir weak) edges. LIKELY 仅连精确子目录（深度≥2），根目录（entities/、concepts/）不互连，避免跨主题误连。** |
| graph.svg | graphify-out/graph.svg | Static visualization image (needs Chinese font) |
| graph.canvas | graphify-out/graph.canvas | Obsidian Canvas — open in Obsidian for interactive exploration |
| obsidian/ | graphify-out/obsidian/ | Per-community markdown note exports |
| extraction.json | graphify-out/extraction.json | Raw extraction data (intermediate) |
| knowledge-graph.md | docs/concepts/knowledge-graph.md | Wiki page documenting the graph |
| docs/graph-html/graph.html | docs/graph-html/ | **Interactive Graphify-native visualization (vis-network)** — served via iframe in `concepts/graph-viewer.md`. Replaces ECharts. |
| docs/javascripts/related-pages.v{N}.js | docs/javascripts/ | **Per-page "📊 图谱关联" injector** — auto-creates the section on pages lacking it, shows EXTRACTED / INFERRED / LIKELY badges (LIKELY 弱关联折叠为"展开弱关联"按钮). Uses `wiki_title` (中文 H1) for labels. Bump `?v=` query in mkdocs.yml on change (CF cache). 关联质量/标签可见性细节见 `graphify-wiki` 技能的 `references/graph-html-label-visibility.md`. |

## Adding the Graph Page to MkDocs Nav

The graph page lives at `docs/concepts/knowledge-graph.md` and is auto-discovered by MkDocs under Concepts/. No explicit nav entry needed if mkdocs.yml has no manual `nav` section.

## Cron Setup for Auto-Rebuild

```bash
# Daily rebuild at 04:00
0 4 * * * cd /llm-wiki && source scripts/.graphify-venv/bin/activate && python3 scripts/build-graph.py >/tmp/graphify-rebuild.log 2>&1
```

After rebuild, restart the MkDocs container to reflect updates:
```bash
docker restart llm-wiki
```

## Pitfalls

### ⚠️ 中文 SVG 字体：必须用独立 TTF，勿用 TTC

参见 `graphify-wiki` 技能的 Pitfalls 章节。不要在 SVG 中使用 TTC（TrueType Collection）字体——Matplotlib 会错误映射字形索引。必须用独立 TTF 文件。

### Graphify is Code-Focused
The markdown `extract_markdown()` function extracts heading hierarchy and basic structure but doesn't capture [[wikilinks]] or Obsidian-style relationships. For a richer graph, pre-process markdown to add explicit edge mentions in the extraction stage.

### Container Paths vs Host Paths
- Container: `/llm-wiki/` → all commands work with `/llm-wiki/...`
- Host: `~/llm-wiki/` → use relative paths or full host path
- The build script uses absolute `/llm-wiki/` paths (container-safe)

### Permission Errors
If `uv pip install graphifyy` fails with `Permission denied` in the Hermes venv:
```bash
# Create a dedicated venv inside the wiki directory
cd ~/llm-wiki
uv venv scripts/.graphify-venv
source scripts/.graphify-venv/bin/activate
uv pip install graphifyy
```

### MkDocs 集成：SVG/JSON/HTML 必须手动复制
Graphify 构建产出在 `graphify-out/` 下，但 MkDocs 通过 `docs/` 目录服务文件。必须在每次构建后复制：
```bash
# 从 graphify-out 复制到 MkDocs 可访问位置
cp graphify-out/graph.svg docs/images/knowledge-graph.svg   # 静态图
cp graphify-out/graph.json docs/data/graph/graph.json       # 图谱数据（related-pages.js + graph.html 共用）
cp graphify-out/graph.html docs/graph-html/graph.html       # Graphify 原生交互图（vis-network，替代 ECharts）
```
如果使用 `build-graph.py` 脚本，在里面加入这些复制步骤。

### 交互图：用 Graphify 原生 graph.html（非 ECharts）
`export.to_html()` 生成 vis-network 交互图（搜索/缩放/社区过滤/节点点击跳 wiki 页）。
在 `build-graph.py` 末尾调用 `export.to_html(G, clusters, 'graphify-out/graph.html', community_labels=labels)`，
再后处理注入 `network.on('click', ...)` 跳页逻辑（节点 `_source_file` → `/<file>/`）。
`concepts/graph-viewer.md` 用 iframe 嵌入 `docs/graph-html/graph.html`。**不要再用 ECharts。**

### Docker 容器中不可用 graphify venv entrypoint
在 `squidfunk/mkdocs-material` 容器中，尝试使用 graphify venv 的 Python 作为 entrypoint 会导致启动失败：
```yaml
# ❌ 这行会导致容器崩溃
entrypoint: ["/docs/scripts/.graphify-venv/bin/python3", "-m", "mkdocs"]
# 错误: OCI runtime create failed: ... no such file or directory
```
原因：Docker volume 映射 `~/llm-wiki:/docs` 后，宿主机的 `scripts/` 目录映射为容器内的 `/docs/scripts/`。但如果 venv 创建在不同路径或权限不正确，容器无法加载。**解决方案：始终使用 MkDocs 默认 entrypoint，图谱构建在宿主机/独立 venv 完成。**

### build-graph.py 集成示例
完整的 build 脚本应包含复制步骤：
```python
# ... 从 graphify 提取/构建/导出 ...
import shutil, os

# 复制到 MkDocs 可见路径
shutil.copy('graphify-out/graph.svg', 'docs/images/knowledge-graph.svg')
shutil.copy('graphify-out/graph.json', 'docs/data/graph/graph.json')
shutil.copy('graphify-out/graph.html', 'docs/graph-html/graph.html')
print("Copied graph files to docs/")
```

### ⚠️ 重建顺序铁律：build → enrich → 复制 graph.json + graph.html（缺一不可）
`build-graph.py` 生成的 graph.json 是**干净 820 边**（仅 wikilink）。`enrich-graph.py` 在其上叠加 LIKELY 边（1020 边）。**前端 related-pages.js 读的 `docs/data/graph/graph.json` 必须是 enrich 后的版本。**

致命错误（实测踩过）：只重新 build + 复制了 graph.html，却忘了 `enrich-graph.py` 和复制 graph.json → 前端关联数据停留在旧 820 边（无 LIKELY、wiki_title 缺失），中文标签/弱关联全失效。

正确顺序：
```bash
cd /llm-wiki
/llm-wiki/scripts/.graphify-venv/bin/python3 /llm-wiki/scripts/build-graph.py   # 820 边 + graph.html
/llm-wiki/scripts/.graphify-venv/bin/python3 /llm-wiki/scripts/enrich-graph.py  # +LIKELY → 1020 边
cp /llm-wiki/graphify-out/graph.json /llm-wiki/docs/data/graph/graph.json
cp /llm-wiki/graphify-out/graph.html /llm-wiki/docs/graph-html/graph.html
docker restart llm-wiki
```
验证：curl graph.json 后 `grep -c LIKELY` 应 >0；节点含 `wiki_title`。

### 矛盾检测（摄入质量门禁）
每次摄入后运行 `scripts/contradiction-check.py`：
```bash
/llm-wiki/scripts/.graphify-venv/bin/python3 /llm-wiki/scripts/contradiction-check.py
```
检查：frontmatter 必填字段、日期逻辑（created<=updated）、重复 title、contested 无说明、source_file 误填、工具版本漂移。
0 ERROR 为通过；WARN（如 raw/ 源页缺 sources）为已知合规缺口，可酌情补。

## Verification

After a rebuild, check:
```bash
ls -lh /llm-wiki/graphify-out/
# Should show: extraction.json, graph.json, graph.svg, graph.canvas, obsidian/
wc -l /llm-wiki/graphify-out/graph.json
# graph.json should have content (not empty)
```
