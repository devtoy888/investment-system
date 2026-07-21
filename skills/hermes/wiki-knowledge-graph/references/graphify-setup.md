# Graphify Setup Reference

> From session 2026-07-10 — first Graphify installation and wiki knowledge graph build.

## Installation

```bash
cd ~/llm-wiki
uv venv scripts/.graphify-venv
source scripts/.graphify-venv/bin/activate
uv pip install graphifyy
```

Graphify was installed to a dedicated venv under `scripts/.graphify-venv/` (not the Hermes venv, which had permission issues).

## Notes on Graphify's CLI

| Command | Purpose |
|---------|---------|
| `graphify install` | Copies skill file to platform config dirs for AI assistants (Claude Code, Codex, etc.) |
| `graphify install --platform hermes` | Installs as Hermes Agent skill |
| `graphify add <url>` | Fetches URL, saves to ./raw, and updates graph |

There is no standalone `graphify build` or `graphify extract` CLI command — the `/graphify` command is a slash-command run inside an AI assistant (Claude Code, Codex, etc.), not a standalone binary. Programmatic use requires Python API calls.

## Programmatic API

### Extract Phase

```python
from graphify import extract

paths = list(Path('docs').glob('**/*.md'))
result = extract.extract(paths, parallel=True)
# returns dict with keys: nodes, edges, input_tokens, output_tokens
```

### Build Phase

```python
from graphify import build, cluster, export

# build() expects a LIST of dicts (each dict = one file extraction)
G = build.build([result], root='/path/to/root')

# Community detection
clusters = cluster.cluster(G)  # returns {cluster_id: [node_names, ...]}

# Label communities based on most common source file prefix
from collections import Counter
labels = {}
for cid, members in sorted(clusters.items(), key=lambda x: -len(x[1])):
    src = [m.split('_')[0] for m in members if '_' in m]
    common = Counter(src).most_common(1)
    labels[cid] = common[0][0] if common else str(cid)
```

### Export Phase

```python
export.to_json(G, clusters, 'graph.json', community_labels=labels)
export.to_svg(G, clusters, 'graph.svg', community_labels=labels)  # needs matplotlib
export.to_canvas(G, clusters, 'graph.canvas', community_labels=labels)  # Obsidian canvas
export.to_obsidian(G, clusters, 'obsidian/', community_labels=labels)  # per-community notes
```

## First Run Results (2026-07-10)

| Metric | Value |
|--------|-------|
| Files processed | 7 markdown files |
| Nodes extracted | 89 |
| Edges extracted | 85 |
| Communities detected | 12 (Leiden algorithm) |

Communities:
- Docker Compose 部署 (12 nodes) — container config
- 投资组合 (11 nodes) — portfolio entities
- Git 凭据 (10 nodes) — credential optimization
- R2 媒体存储 (10 nodes) — media upload workflow
- 6维分析 (9 nodes) — investment analysis framework
- 首页导航 (7 nodes) — site home page
- SCHEMA 规则 (7 nodes) — wiki rules
- Obsidian 同步 (6 nodes) — MacBook sync
- MkDocs 前端 (5 nodes) — web frontend
- 变更日志 (4 nodes) — log entries
- Cloudflare Tunnel (4 nodes) — domain config
- 架构决策 (4 nodes) — architecture decisions

## Chinese Font Issue

SVG export uses matplotlib default (DejaVu Sans) which lacks CJK glyphs. Labels appear as empty boxes. To fix:

```bash
# Option 1: Install Noto Sans CJK
apt-get install -y fonts-noto-cjk

# Option 2: Use the knowledge-graph.md page instead of SVG
# The graph.canvas (Obsidian Canvas) and graph.json are not affected
```

## Important: Community dict format

`cluster.cluster(G)` returns `{int: [str, ...]}` — mapping from community ID to list of node names. NOT `{node: community_id}`. Iterate accordingly.

## File Structure

```
/llm-wiki/
  graphify-out/
    extraction.json    ← Raw extraction data (intermediate)
    graph.json         ← Structured graph with communities
    graph.svg          ← Static visualization
    graph.canvas       ← Obsidian Canvas (open in Obsidian)
    obsidian/          ← Per-community markdown notes
  scripts/
    .graphify-venv/    ← Virtual environment
    build-graph.py     ← Rebuild script (cron-ready)
```
