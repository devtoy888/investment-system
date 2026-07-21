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
| graph.json | graphify-out/graph.json | Structured graph data (nodes/edges/communities) |
| graph.svg | graphify-out/graph.svg | Static visualization image (needs Chinese font) |
| graph.canvas | graphify-out/graph.canvas | Obsidian Canvas — open in Obsidian for interactive exploration |
| obsidian/ | graphify-out/obsidian/ | Per-community markdown note exports |
| extraction.json | graphify-out/extraction.json | Raw extraction data (intermediate) |
| knowledge-graph.md | docs/concepts/knowledge-graph.md | Wiki page documenting the graph |

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

### MkDocs 集成：SVG/JSON 必须手动复制
Graphify 构建产出在 `graphify-out/` 下，但 MkDocs 通过 `docs/` 目录服务文件。必须在每次构建后复制：
```bash
# 从 graphify-out 复制到 MkDocs 可访问位置
cp graphify-out/graph.svg docs/images/knowledge-graph.svg   # 静态图
cp graphify-out/graph.json docs/images/graph-data.json       # ECharts 交互页数据
```
如果使用 `build-graph.py` 脚本，在里面加入这些复制步骤。

### Docker 容器中不可用 graphify venv entrypoint
在 `squidfunk/mkdocs-material` 容器中，尝试使用 graphify venv 的 Python 作为 entrypoint 会导致启动失败：
```yaml
# ❌ 这行会导致容器崩溃
entrypoint: ["/docs/scripts/.graphify-venv/bin/python3", "-m", "mkdocs"]
# 错误: OCI runtime create failed: ... no such file or directory
```
原因：Docker volume 映射 `~/llm-wiki:/docs` 后，宿主机的 `scripts/` 目录映射为容器内的 `/docs/scripts/`。但如果 venv 创建在不同路径或权限不正确，容器无法加载。**解决方案：始终使用 MkDocs 默认 entrypoint，交互图用 ECharts 独立页。**

### build-graph.py 集成示例
完整的 build 脚本应包含复制步骤：
```python
# ... 从 graphify 提取/构建/导出 ...
import shutil, os

# 复制到 MkDocs 可见路径
shutil.copy('graphify-out/graph.svg', 'docs/images/knowledge-graph.svg')
shutil.copy('graphify-out/graph.json', 'docs/images/graph-data.json')
print("Copied graph files to docs/images/")
```

## Verification

After a rebuild, check:
```bash
ls -lh /llm-wiki/graphify-out/
# Should show: extraction.json, graph.json, graph.svg, graph.canvas, obsidian/
wc -l /llm-wiki/graphify-out/graph.json
# graph.json should have content (not empty)
```
