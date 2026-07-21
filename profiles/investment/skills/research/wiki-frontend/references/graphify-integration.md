# Graphify Integration for LLM Wiki

## What Graphify Does

[Graphify](https://github.com/Graphify-Labs/graphify) (`pip install graphifyy`) is an open-source tool that analyzes content and builds interactive knowledge graphs. For a Karpathy-pattern wiki:

- Analyzes raw/ content (md, pdf, images, code)
- Extracts nodes (concepts/entities) and edges (relationships)
- Runs Leiden community detection → clusters content into "knowledge neighborhoods"
- Identifies "God Nodes" (most-connected) and "Surprising Connections"
- Outputs graph.html (interactive), graph.json (NetworkX queryable), GRAPH_REPORT.md

## Integration Architecture

```
~/wiki/
├── _graph/                  ← Graphify output dir
│   ├── graph.html           ← Interactive visualization
│   ├── graph.json           ← Machine-queryable graph
│   └── GRAPH_REPORT.md      ← Text report
├── raw/                     ← Graphify scans this
├── entities/
└── concepts/
```

## Cron Job

```bash
docker exec hermes hermes cron create \
  --schedule "0 4 * * *" \
  --name "wiki-graphify" \
  --no-agent \
  --script /opt/data/scripts/wiki-graphify.sh
```

Script `/opt/data/scripts/wiki-graphify.sh`:
```bash
#!/bin/bash
cd /wiki
if ! command -v graphify &>/dev/null; then
    pip install graphifyy -q
fi
graphify ./raw --output _graph --no-viz 2>&1
echo "Graphify update: $(date)"
```

## Frontend Access

Option A: Embed via MkDocs custom page
- Copy `graph.html` into wiki root and add to nav in mkdocs.yml
- Or serve via Caddy/Nginx alongside MkDocs

Option B: Direct URL
- `https://wiki.devtoy.cn/_graph/graph.html` if MkDocs serves it via `extra_files`

## vs mkdocs-network-graph-plugin

| Aspect | Graphify | Plugin |
|--------|----------|--------|
| LLM-dependent | ✅ (semantic extraction) | ❌ (reads existing links) |
| Community detection | ✅ Leiden | ❌ |
| God nodes | ✅ | ❌ |
| Resource | cron job + LLM tokens | zero |

Start with plugin. Add Graphify when you need semantic cross-domain relationship discovery.
