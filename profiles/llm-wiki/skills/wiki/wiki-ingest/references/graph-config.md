# Graph Configuration Reference

## Current Graph State (as of 2026-07-14)

| Metric | Value |
|--------|-------|
| Nodes | ~633 |
| Edges | ~777 |
| EXTRACTED | ~693 (direct [[wikilinks]] + document structure) |
| INFERRED | ~84 (same-directory inference) |

## Edge Data Structure

Each edge in graph.json:

```json
{
  "relation": "references",
  "confidence": "EXTRACTED|INFERRED|LIKELY",
  "confidence_score": 1.0|0.7|0.4,
  "source_file": "path/to/source.md",
  "source_location": "L0",
  "weight": 1.0,
  "source": "node_id_1",
  "target": "node_id_2"
}
```

## Confidence Levels

| Level | Score | Meaning | Source |
|-------|-------|---------|--------|
| EXTRACTED | 1.0 | Direct [[wikilink]] or document structure | Parsed from markdown |
| INFERRED | 0.7 | Same directory (topical relationship) | Heuristic |
| LIKELY | 0.4 | Shared tags or weak signal | Reserved (not currently generated) |

## JS Version Bump Protocol

Cloudflare caches JS files aggressively. **Always** increment the version number when changing related-pages.js:

```
v6.js  →  v7.js  →  v8.js  →  v9.js  ...
```

Steps:
1. `cp related-pages.v{N}.js related-pages.v{N+1}.js`
2. Edit files as needed in the new copy
3. `sed -i 's/v{N}\.js/v{N+1}.js/g' mkdocs.yml`
4. Tell user: `docker restart llm-wiki`

Why not query params? MkDocs sets `Cache-Control` headers that Cloudflare respects. Query params (`?v=2`) do not reliably bust CF cache. Only new filenames work.

## JS File Inventory

| File | Purpose |
|------|---------|
| `graph-viewer.v2.js` | ECharts force-directed graph (stable) |
| `related-pages.v{N}.js` | Dynamic 图谱关联 with confidence badges |
