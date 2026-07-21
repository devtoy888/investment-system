# Natural Language Graph Query — Implementation Guide

Client-side JS engine that loads `graph.json` and enables natural language queries against the knowledge graph via keyword matching + BFS shortest path.

## Architecture

```
User query (natural language)
    ↓
Tokenization (Chinese char split + English word split + stop word filter)
    ↓
4-level node matching (exact_label → label_contains → filename_contains → id_contains)
    ↓
BFS shortest path between matched node groups (max 6 steps)
    ↓
Render: interactive path cards with community trajectory
```

## Files

| File | Purpose |
|------|---------|
| `docs/concepts/graph-query.md` | Page with search input + results container + query examples |
| `docs/javascripts/graph-query.v1.js` | Minified query engine (10KB) |
| `mkdocs.yml` | Add to `extra_javascript` and `nav` |

## Page Setup

The `.md` page provides:
- **Search UI**: input field + button, styled with CSS variables for dark/light theme
- **Status bar**: shows match count and bridge node count
- **Results container**: dynamically filled with path cards
- **Query examples**: pre-written samples
- **`window.__GRAPH_QUERY_CONFIG__`**: config object with `graphUrl`, `pageUrls`, `indexUrls`, `labelMap`

## Query Engine

### Tokenization

Mixed Chinese + English: CJK chars split individually, English split by whitespace/punctuation. Stop words filtered (的, 和, 什么, how, what, find, between, etc.). Single CJK chars kept only if meaningful identifiers (等, 保, 级, 测, 赵, 杰, 投, 资, 安, 全, etc.).

### Node Matching (4-level scoring)

| Level | Score | Match | Example |
|-------|-------|-------|---------|
| 1. Exact label | 100 | `node.label === token` | "Vibe-Trading 项目总览" |
| 2. Label contains | 60 | `node.label.includes(token)` | "等保" matches 等保节点 |
| 3. Filename contains | 40 | `source_file.includes(token)` | "等保" matches 目录文件 |
| 4. ID contains | 25 | `node.id.includes(token)` | Broad fallback |

### Path Finding

- BFS from source to target, max 6 steps
- Dedup by sorted key (source < target)
- Multi-group: paths between all token groups + top-10 candidates across communities
- Sort: shorter paths first

### Path Enrichment

Each step enriches with: `label`, `url` (clickable link), `community`, edge confidence badge (✓=EXTRACTED, ~=INFERRED).

### Rendering

Path cards show: path number, step count, source→target names, clickable node links with → arrows, confidence badges, community trajectory.

### MkDocs Compatibility

#### ❗ Critical: `document$.subscribe()` Alone Is NOT Reliable

The standard pattern (`document$.subscribe(function() { init(); })`) **fails silently** on direct page loads. The JS file loads from `<head>` via `extra_javascript`, but `document$` may not fire the subscription callback correctly when the page is first navigated to (as opposed to PJAX-navigated within an already-running session).

**✅ Fix: Wrap initialization in `setTimeout(150)` + recursive DOM polling fallback:**

```javascript
function setupUI() {
  var inp = document.getElementById('graph-query-input');
  var btn = document.getElementById('graph-query-btn');
  if (!inp || !btn) {
    setTimeout(setupUI, 300);  // Keep trying until DOM elements exist
    return;
  }
  // Attach event listeners here
  btn.addEventListener('click', run);
  inp.addEventListener('keydown', function(e) { if (e.key === 'Enter') run(); });
}

// Bootstrap — try all three paths
if (typeof document$ !== 'undefined') {
  document$.subscribe(function() { setTimeout(setupUI, 150); });
} else {
  var st = function() { setTimeout(setupUI, 150); };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', st);
  } else {
    st();
  }
}
```

Key differences from the naive `document$.subscribe(fn)`:
1. **`setTimeout(setupUI, 150)`** — the 150ms delay lets MkDocs Material finish DOM replacement before your JS queries for elements
2. **`setTimeout(setupUI, 300)` recursive fallback** — if elements don't exist yet, keep polling every 300ms until they do. This handles edge cases where DOM content arrives after the callback fires
3. **Triple bootstrap** — `document$` for PJAX nav, `DOMContentLoaded` for initial loads, and synchronous fallback for late-loaded scripts

This pattern applies to ALL client-side JS features in MkDocs Material with `navigation.instant`, not just graph query.

### URL Query Parameter Support

Supports `?q=` parameter: `/concepts/graph-query/?q=Vibe-Trading 等保`

## Configuration Objects

Three mapping objects shared with related-pages.js (embedded in `__GRAPH_QUERY_CONFIG__` on the .md page, not in JS):
- `pageUrls`: filename → canonical URL
- `indexUrls`: directory → index URL
- `labelMap`: source_file → display label for index pages

## Pitfalls

1. **Large graph.json load time**: ~633KB on first request. Loading indicator provided.
2. **Single CJK char ambiguity**: Whitelist mitigates but may miss edge cases.
3. **Graph sparsity**: Few cross-community edges → no paths. BFS fallback to top candidates across communities helps.
4. **Cloudflare JS caching**: Bump JS version for logic changes; URL mapping changes live in .md page, no version bump needed.
5. **`navigation.instant`**: Query UI re-inits correctly via `document$.subscribe()` on PJAX navigation.
