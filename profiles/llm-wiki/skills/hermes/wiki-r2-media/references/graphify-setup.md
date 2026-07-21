# Graphify Integration Reference

## Installation

```bash
# Create isolated venv (persistent on volume)
uv venv /llm-wiki/scripts/.graphify-venv
source /llm-wiki/scripts/.graphify-venv/bin/activate

# Install graphify and visualization deps
uv pip install graphifyy matplotlib

# Initialize (copies skill files, creates graphify-out/)
cd /llm-wiki && graphify install
```

## Extraction from Markdown

Graphify's `extract.extract()` reads headings (`#`, `##`, `###`), frontmatter, and code blocks from each markdown file. It produces nodes (headings, concepts) and edges (hierarchical parent-child relationships).

```python
from graphify import extract
result = extract.extract([Path('docs/setup-guide.md')], parallel=True)
# result['nodes'] — extracted concepts (headings, frontmatter labels)
# result['edges'] — parent-child, cross-reference relationships
```

## Build + Cluster Pipeline

```python
from graphify import build, cluster, export

# Merge extractions into NetworkX graph
G = build.build([result], root='/llm-wiki')

# Leiden community detection
clusters = cluster.cluster(G)  # returns {cluster_id: [node_names]}

# Label communities
labels = {0: 'Docker Compose', 1: '投资组合', ...}

# Export all formats
export.to_json(G, clusters, 'graphify-out/graph.json', community_labels=labels)
export.to_svg(G, clusters, 'graphify-out/graph.svg', community_labels=labels)
export.to_canvas(G, clusters, 'graphify-out/graph.canvas', community_labels=labels)
export.to_obsidian(G, clusters, 'graphify-out/obsidian/', community_labels=labels)
```

## Community Structure

Leiden algorithm produces fine-grained clusters (typically 10-15 for ~90 nodes). Each cluster groups nodes from the same topic domain. Node ID format: `{filename}_{section-slug}`.

## Scheduled Rebuild

Recommended: daily cron or triggered after each wiki content update:
```bash
0 4 * * * cd /llm-wiki && source scripts/.graphify-venv/bin/activate && python3 scripts/build-graph.py
```

## Known Limitations

- Markdown extraction is heading-based (no deep NLP/semantics) — nodes represent headings, not full concept understanding
- `to_svg()` with Chinese text requires matplotlib with CJK font (DejaVu Sans fallback causes glyph warnings but still produces a valid SVG)
- Graphify's `/graphify` slash commands (for Claude Code/Codex) are NOT used directly — the Python API is used instead
