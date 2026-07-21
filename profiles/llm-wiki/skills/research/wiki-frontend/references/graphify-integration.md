# Graphify Integration for LLM Wiki

## What Graphify Does

[Graphify](https://github.com/Graphify-Labs/graphify) (`pip install graphifyy`) is a tool that analyzes markdown content and builds knowledge graphs with community detection.

For this project, a `build-graph.py` script wraps the Graphify library:

```
提取 (extract) → 建图 (build) → 社区检测 (cluster) → 导出 (export: SVG/JSON/Canvas)
```

## Real-World Build Workflow

### Prerequisites

The project venv at `scripts/.graphify-venv/` has graphifyy and matplotlib pre-installed. Two gotchas:

1. **pip may be missing** (orphan venv): bootstrap with get-pip.py
2. **scipy is NOT declared as a dependency** of graphifyy but is required for SVG export (networkx.spring_layout)

### Full Rebuild Command

```bash
cd /llm-wiki

# 1. Ensure scipy (install if missing)
scripts/.graphify-venv/bin/python3 -c "import scipy" 2>/dev/null || (
  curl -sL https://bootstrap.pypa.io/get-pip.py | \
    scripts/.graphify-venv/bin/python3 --quiet
  scripts/.graphify-venv/bin/pip install scipy --quiet
)

# 2. Build graph (46 markdown files → 542 nodes, 571 edges, 41 communities)
scripts/.graphify-venv/bin/python3 scripts/build-graph.py 2>&1

# 3. Deploy to MkDocs
cp graphify-out/graph.svg docs/images/knowledge-graph.svg

# 4. Update community table in knowledge-graph.md if counts changed
# (check graphify-out/graph.json for new community distribution)

# 5. Restart MkDocs
docker restart llm-wiki
```

### Build Output

```
graphify-out/
├── extraction.json   # Raw extraction data
├── graph.json        # NetworkX graph (542 nodes, 571 links)
├── graph.svg         # Matplotlib SVG (2.2MB for 542 nodes)
├── graph.canvas      # Obsidian Canvas format
└── obsidian/         # Obsidian vault export
```

### Community Table Update

After rebuilding, the community counts change. Update `docs/concepts/knowledge-graph.md`:

```python
import json
from collections import Counter
data = json.load(open('/llm-wiki/graphify-out/graph.json'))
comm = Counter()
for n in data['nodes']:
    c = n.get('community', -1)
    comm[c] += 1
for cid, cnt in comm.most_common(15):
    sample = [n['label'] for n in data['nodes'] if n.get('community')==cid][:2]
    name = sample[0][:30] if sample else f'社区{cid}'
    desc = sample[1][:40] if len(sample) > 1 else ''
    print(f'| {cid} | {name} | {cnt} | {desc} |')
```

### Known Limitations

- **Standard nodes**: `graphify` from this project's version extracts word-frequency-based nodes (TF-based), not LLM-semantic. It finds every significant word/phrase across markdown files and links them by co-occurrence. This means:
  - Nodes are granular (word-level), not concept-level
  - Edge weight reflects co-occurrence frequency, not semantic relationship
  - "God node" detection works (most-connected words) but the "gods" may be bland (e.g., "文档", "安全")
  - The 41+ communities are driven by co-word clustering, not topic modeling
- **LLM-powered extraction**: Graphify supports LLM-based extraction for richer semantics, but this project uses the lighter AST/statistical mode to avoid token costs.
- **Chinese font**: LXGW WenKai TTF required for CJK labels; glyph warnings for emoji characters (✅🔴🟢⭐🔍📊🐝👥) are cosmetic.
