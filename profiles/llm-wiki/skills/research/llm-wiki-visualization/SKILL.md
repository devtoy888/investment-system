---
name: llm-wiki-visualization
description: "Knowledge graph visualization for LLM Wiki: inline Panzoom, SVG graph generation, interactive graph viewers, ECharts integration"
version: 1.4.0
author: Hermes Agent
license: MIT
---

# Wiki Knowledge Graph Visualization

Inline Panzoom component for SVG knowledge graphs, interactive ECharts graph viewers, Graphify integration, and graph data pipeline.

## When This Skill Activates

- User asks about knowledge graph, graph visualization, or SVG rendering on their wiki
- User wants to make an SVG image zoomable/panable on a wiki page
- User needs an interactive graph viewer for exploring wiki topics
- User asks about Graphify, Gephi, D3.js, ECharts, or force-directed graph integration
- User reports broken graph links, empty graph pages, or data not loading

## Inline Panzoom Component

Replaces full-screen Lightbox with a page-inline zoomable SVG container. Users scroll-zoom and drag-pan directly on the graph without leaving the page flow.

### HTML Structure

```
<div id="pz-wrap">               ← container (70vh, overflow:hidden)
  <div id="pz-stage">            ← transform layer
    <img id="pz-img">            ← the SVG (pointer-events:none)
  </div>
  +/−/↺ buttons                  ← control bar
  <div id="pz-level">100%</div>  ← auto-hide zoom indicator
</div>
```

### JavaScript Implementation

Key implementation choices:
- CSS `transform: translate(X,Y) scale(S)` with `transform-origin: 0 0` for smooth GPU-accelerated zoom/pan
- `pointer-events: none` on `<img>` so the container captures all mouse events
- Clamp pan boundaries with 20% over-pan allowance (so edges never vanish)
- `{passive: false}` on wheel listener prevents page scroll interference
- All variables in an IIFE to avoid polluting global scope

| Interaction | Behavior |
|-------------|----------|
| Scroll wheel | Zoom centered on cursor (1.12x factor) |
| Click + drag | Pan |
| Double-click | Toggle between fit and 2x zoom |
| Touch | Pinch-zoom + single-finger drag |
| +/- buttons | Zoom in/out toward center |
| ↺ button / Ctrl+0 | Reset to fit view |
| Zoom indicator | Auto-hiding percentage in corner |

### Interaction Logic

```javascript
// Core state: S=scale, X/Y=translate
// On wheel: compute new scale, keep cursor point fixed
function onWheel(e) {
  var rect = wrap.getBoundingClientRect();
  var cx = e.clientX - rect.left;
  var cy = e.clientY - rect.top;
  var ns = S * (e.deltaY < 0 ? 1.12 : 1/1.12);
  ns = Math.max(0.1, Math.min(ns, 20));
  // Keep point (cx,cy) stationary during zoom
  X = cx - (cx - X) * (ns / S);
  Y = cy - (cy - Y) * (ns / S);
  S = ns;
  clamp(); // apply boundary + render
}
```

### Pan Boundary Clamping

```javascript
function clamp() {
  var cw = wrap.clientWidth, ch = wrap.clientHeight;
  var vw = W * S, vh = H * S;          // view size in CSS px
  var opx = cw * 0.2, opy = ch * 0.2;  // 20% over-pan
  var minX = Math.min(cw - vw - opx, opx);
  var maxX = Math.max(cw - vw - opx, opx);
  X = Math.max(minX, Math.min(maxX, X));
  // same for Y
}
```

### Touch Support

- Single touch: drag to pan (same as mouse)
- Two-finger pinch: compute distance ratio, zoom toward midpoint
- `touchstart`/`touchmove`/`touchend` all use `{passive: false}`

## Cloudflare Cache Busting for JS Files

Cloudflare caches JS files at the edge with `max-age=14400` (4 hours). When updating `graph-viewer.js`, the old file is served from Cloudflare cache even after `docker restart llm-wiki`.

**The fix**: Rename the JS file and update `extra_javascript` in `mkdocs.yml`:

```bash
# Create versioned copy
cp docs/javascripts/graph-viewer.js docs/javascripts/graph-viewer.v2.js

# Update mkdocs.yml reference
sed -i 's|javascripts/graph-viewer.js|javascripts/graph-viewer.v2.js|' mkdocs.yml

# Restart container to pick up config change
docker restart llm-wiki
```

Cloudflare sees a new URL it has never cached, so it fetches from origin. The old `.js` can be left in place (no longer referenced).

## Fullscreen Mode (Fullscreen API)

Add a floating fullscreen button (`⛶`) to the graph container using the browser Fullscreen API.

### Implementation

Add this code inside the `.then()` callback after `chart` is initialized:

```javascript
var fsBtn = document.createElement("button");
fsBtn.textContent = "⛶";
fsBtn.title = "全屏查看";
fsBtn.style.cssText = "position:absolute;top:8px;right:8px;z-index:10;background:rgba(255,255,255,0.9);border:1px solid #ddd;border-radius:4px;cursor:pointer;font-size:18px;line-height:1;padding:4px 8px;opacity:0.6;transition:opacity .2s";
fsBtn.onmouseenter = function(){fsBtn.style.opacity="1"};
fsBtn.onmouseleave = function(){fsBtn.style.opacity="0.6"};
container.style.position = "relative";
container.appendChild(fsBtn);

function toggleFS() {
  if (!document.fullscreenElement && !document.webkitFullscreenElement) {
    container.requestFullscreen ? container.requestFullscreen() : container.webkitRequestFullscreen();
    fsBtn.textContent = "✕";
    fsBtn.title = "退出全屏";
  } else {
    document.exitFullscreen ? document.exitFullscreen() : document.webkitExitFullscreen();
    fsBtn.textContent = "⛶";
    fsBtn.title = "全屏查看";
  }
}
fsBtn.onclick = toggleFS;
document.addEventListener("fullscreenchange", function() {
  if (!document.fullscreenElement) { fsBtn.textContent = "⛶"; fsBtn.title = "全屏查看"; }
  chart.resize();
});
document.addEventListener("webkitfullscreenchange", function() {
  if (!document.webkitFullscreenElement) { fsBtn.textContent = "⛶"; fsBtn.title = "全屏查看"; }
  chart.resize();
});
```

**Details**:
- Button positioned in container (needs `position: relative`)
- Uses `container.requestFullscreen()` / `webkitRequestFullscreen()` fallback
- Esc key fires `fullscreenchange` → button reverts + chart resizes
- Semi-transparent (0.6), full opacity on hover

### Verification

1. ⛶ button visible in top-right corner
2. Click → fullscreen, chart auto-resizes
3. Esc → back to container size, button reverts
4. No console errors

## ECharts Interactive Graph Viewer

Create an interactive force-directed graph rendered inside a MkDocs page using ECharts.

### 🔥 CRITICAL: Inline `<script>` Tags Do NOT Work with `navigation.instant`

MkDocs Material's `navigation.instant` (PJAX mode) **strips inline `<script>` tags from page content**. JavaScript embedded directly in a `.md` file via raw HTML will NEVER execute — the `<div>` renders empty with no error in console.

**❌ WRONG — inline scripts are silently discarded:**
```markdown
<div id="graph-container"></div>
<script>
// This NEVER runs when navigation.instant is enabled
echarts.init(document.getElementById("graph-container"));
</script>
```

**✅ CORRECT — external JS file via `extra_javascript`:**

### Step 1: Create External JS File

`docs/javascripts/graph-viewer.js`:

```javascript
function initGraphViewer() {
  var c = document.getElementById("graph-container");
  if (!c || c.__echarts_instance__) return;

  fetch("/data/graph/graph.json")
    .then(function(r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function(data) {
      if (!data || !data.nodes) return;
      var nodes = data.nodes.map(function(n) { return {
        id: n.id, name: n.label || n.id,
        category: n.community || 0, source: n.source_file
      };});
      var edges = data.links.map(function(l) { return {source: l.source, target: l.target}; });

      var chart = echarts.init(c);
      c.__echarts_instance__ = true;
      chart.setOption({ series: [{
        type: "graph", layout: "force", roam: true,
        data: nodes, edges: edges,
        force: { repulsion: 300, edgeLength: [50, 200], gravity: 0.1 },
        label: { show: true, position: "right", fontSize: 10 },
        lineStyle: { opacity: 0.3 },
        emphasis: { focus: "adjacency" }
      }]});
      chart.on("click", function(p) {
        var t = p.data && (p.data.url || p.data.source);
        if (t) { window.location.href = "/" + t.replace(/\.md$/, "").replace(/^\//, ""); }
      });
      window.addEventListener("resize", function() { chart.resize(); });
    });
}

// MkDocs instant nav compatibility
if (typeof document$ !== "undefined") {
  document$.subscribe(function() { initGraphViewer(); });
} else {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGraphViewer);
  } else {
    initGraphViewer();
  }
}
```

**Key**: `document$` is MkDocs Material's RxJS Subject. `document$.subscribe()` fires on both full page loads AND PJAX navigations, so the chart initializes reliably.

### Step 2: Update `mkdocs.yml`

Add `extra_javascript` (order matters — ECharts CDN must load before your script):

```yaml
extra_javascript:
  - https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js
  - javascripts/graph-viewer.js
```

### Step 3: The `.md` File — No Script Tags

```markdown
---
title: Interactive Knowledge Graph
type: concept
tags: [graph, visualization, echarts]
---

# Interactive Knowledge Graph

<div id="graph-container" style="width:100%;height:700px;border:1px solid #ddd;border-radius:8px;"></div>

## Usage Instructions

- **Scroll wheel** — Zoom in/out
- **Drag** — Pan the graph
- **Click node** — Navigate to wiki page
```

### Step 4: Restart Container

`mkdocs serve --dirty` only watches `.md` files. `mkdocs.yml` config changes (like `extra_javascript`) require a full container restart:

```bash
docker restart llm-wiki
```

### Critical: Fetch Path MUST Be Absolute

The graph JSON is at `docs/data/graph/graph.json` → served by MkDocs at `/data/graph/graph.json`.

```javascript
// ✅ CORRECT - absolute path works from any page
fetch("/data/graph/graph.json")

// ❌ WRONG - relative path breaks depending on page directory depth
fetch("../data/graph/graph.json")      // breaks on /concepts/graph-viewer/
fetch("../../images/graph-data.json")  // wrong data file URL
```

**Rule**: Always use absolute paths starting with `/` for data fetches in MkDocs raw HTML blocks.

### Click-to-Navigate on Node Click

Add an event handler so clicking a graph node navigates to the corresponding wiki page:

```javascript
chart.on("click", function(params) {
  if (params.data && params.data.source) {
    var src = params.data.source;
    if (src.endsWith(".md")) src = src.slice(0, -3);
    window.location.href = "/" + src;
  }
});
```

The `source` field comes from the graph.json node's `source_file` property, which stores the `.md` file path (e.g., `concepts/foo.md`).

### Conflict: .md + index.html in Same Directory

If BOTH `graph-viewer.md` AND `graph-viewer/index.html` exist in the same directory:

- MkDocs builds `graph-viewer.md` into a page served at `/concepts/graph-viewer/`
- The `index.html` file is NOT served by MkDocs (it's outside the build pipeline)
- But the browser may return "(empty page)" because of the ambiguity

**Fix**: Keep only `graph-viewer.md`. Delete `graph-viewer/index.html` (or keep as a standalone backup, but it won't be served by MkDocs).

```bash
rm /llm-wiki/docs/concepts/graph-viewer/index.html
```

### Graph Data Location

The graph JSON dataset (`graph.json`) is generated by Graphify and copied to the MkDocs data directory:

| Location | Served at | Use |
|----------|-----------|-----|
| `docs/data/graph/graph.json` | `/data/graph/graph.json` | ECharts viewer fetch target |
| `graphify-out/graph.json` | N/A (source only) | Graphify output for SVG/Canvas export |

The copy is done by `rebuild-graph.py`:
```python
shutil.copy2(GOUT / 'graph.json', DDAT / 'graph.json')
```

### Complete Graph Viewer Page — File Checklist

When setting up a graph-viewer page, ensure these files exist:

1. **`docs/concepts/graph-viewer.md`** — Frontmatter + `<div id="graph-container">` + description text + usage instructions + cross-links
2. **`docs/javascripts/graph-viewer.js`** — External JS with `document$.subscribe()` for instant nav compatibility
3. **`docs/mkdocs.yml`** — Has `extra_javascript` section loading echarts CDN + graph-viewer.js
4. **`docs/data/graph/graph.json`** — Graphify-generated dataset (fetched by JS via `/data/graph/graph.json`)

The `.md` file should NOT contain any `<script>` tags:

```markdown
---
title: Interactive Knowledge Graph
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept
tags: [graph, visualization, echarts]
---

# Interactive Knowledge Graph

<div id="graph-container" style="width:100%;height:700px;border:1px solid #ddd;border-radius:8px;"></div>

## Usage Instructions

- **Scroll wheel** — Zoom in/out
- **Drag/pan** — Navigate the graph
- **Click node** — Visit the corresponding wiki page

## Data Source

Generated by Graphify using Leiden community detection.

[Back to Knowledge Graph](knowledge-graph.md)
```

### Pitfalls

- **`navigation.instant` strips inline scripts**: MkDocs Material's PJAX mode removes `<script>` tags from page content. NEVER use inline `<script>` tags for graph initialization. Always use `extra_javascript` + external JS file + `document$.subscribe()` pattern.
- **`document$.subscribe()` alone unreliable on direct page loads**: The standard `document$.subscribe(fn)` silently fails on first direct navigation. Wrap in `setTimeout(fn, 150)` inside the subscription, and add a `DOMContentLoaded` fallback with the same setTimeout. See "Natural Language Graph Query → Pitfalls" for the exact fix pattern.
- **`extra_javascript` changes require container restart**: `mkdocs serve --dirty` only watches `.md` file changes. Adding/removing `extra_javascript` entries in `mkdocs.yml` won't take effect until `docker restart llm-wiki`.
- **TTC fonts in Matplotlib**: TrueType Collection fonts cause CJK character offset in Matplotlib SVG output. Always use standalone TTF files.
- **Cache busting**: Cloudflare/edge caches SVG files aggressively. Append `?v=N` to force refresh.
- **Wheel scroll conflict**: Without `{passive: false}` and `preventDefault()`, zooming also scrolls the page.
- **ECharts CDN not loading**: If `cdn.jsdelivr.net` is unreachable, the graph area shows blank. Verify CDN availability; fall back to local `echarts.min.js` in `extra_javascript` if needed.

## Dynamic Related Pages from Graph

Auto-display related wiki pages derived from Graphify's knowledge graph on every page. Uses a client-side JS script (`related-pages.js`) that fetches `graph.json` and injects neighbor links into a `📊 图谱关联` section.

See `references/related-pages-implementation.md` for the full implementation guide.

### Quick Reference

1. **Add target section to every page** that should show related pages:
   ```markdown
   ## 📊 图谱关联
   
   <!-- JS fills this dynamically -->
   ```

2. **Create `related-pages.vX.js`** with:
   - `PAGE_URLS` + `INDEX_URLS` mapping tables (page name to canonical URL)
   - h1 title matching (with pilcrow strip for MkDocs permalinks)
   - URL fallback matching (when h1 doesn't match)
   - **`getUrlForNode()`** for correct index page URL resolution:
     ```javascript
     function getUrlForNode(node) {
       var srcFile = node.source_file || "";
       if (!srcFile) return "";
       if (srcFile === "index.md") return "/";
       if (srcFile.endsWith("index.md")) {
         var dir = srcFile.replace(/\/index\.md$/, "");
         return INDEX_URLS[dir] || "/" + dir + "/";
       }
       var fn = srcFile.split("/").pop().replace(/\.md$/, "");
       return PAGE_URLS[fn] || "/" + fn + "/";
     }
     ```
     **Why**: Without this, all index.md references map to `/index/` instead of their correct directory URLs, causing dedup to collapse different index pages into one link.
   - **`getLabelForNode()` + `LABEL_MAP`** for semantic page labels instead of raw "index.md":
     ```javascript
     var LABEL_MAP = {
       "index.md": "首页",
       "concepts/index.md": "概念索引",
       "entities/index.md": "实体索引",
       "comparisons/index.md": "对比分析",
       "queries/index.md": "查询归档",
       "concepts/网络安全等级保护/index.md": "等保 2.0",
       "concepts/vibe-trading/index.md": "Vibe-Trading"
     };
     function getLabelForNode(node) {
       var sf = node.source_file || "";
       if (sf === "index.md" || sf.endsWith("/index.md")) {
         return LABEL_MAP[sf] || sf.split("/").slice(-2,-1)[0] || "首页";
       }
       var label = node.label || "";
       return label.replace(/\.md$/, "");
     }
     ```
     **Why**: Graphify labels index pages as just "index.md". Without this map, all index links show "index.md" instead of descriptive names like "首页" or "概念索引".
   - Neighbor discovery from graph.json edges to file-to-file relation scoring
   - **Dedup via `seen[url]`** — prevents same page appearing twice
   - **Confidence badge** — track `l.confidence` from each link during neighbor aggregation, pick the best score per node, render as colored badge:\n     ```javascript\n     // In the links.forEach loop, add:\n     if (!related[otherId]) related[otherId] = {count:0, weight:0, bestConf:null, bestConfScore:-1};\n     related[otherId].count++;\n     related[otherId].weight += l.weight || 1;\n     var cs = l.confidence_score || 0;\n     if (cs > related[otherId].bestConfScore) {\n       related[otherId].bestConf = l.confidence || \"EXTRACTED\";\n       related[otherId].bestConfScore = cs;\n     }\n     // In HTML generation:\n     html += '<a href=\"' + url + '\">' + label + '</a> <span class=\"related-conf related-conf-' +\n       (related[id].bestConf || \"EXTRACTED\") + '\">' + (related[id].bestConf || \"EXTRACTED\") + \"</span>\";\n     ```\n     Add CSS (injected via JS `document.head.appendChild`):\n     ```css\n     .related-conf-EXTRACTED{background:#e6f7e6;color:#2e7d32;border:1px solid #a5d6a7;}\n     .related-conf-INFERRED{background:#fff8e1;color:#e65100;border:1px solid #ffe082;}\n     .related-conf-LIKELY{background:#f5f5f5;color:#616161;border:1px solid #bdbdbd;}\n     ```
   - `document$.subscribe()` for MkDocs instant-nav compatibility

3. **Register in mkdocs.yml**:
   ```yaml
   extra_javascript:
     - https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js
     - javascripts/graph-viewer.v2.js
     - javascripts/related-pages.v5.js
   ```

### Key Pitfalls

- **Pilcrow in h1**: MkDocs adds it via TOC permalink. Always strip before matching
- **Duplicate neighbor pages**: Two graph nodes may reference the same source_file. Use `seen[url]` to dedup.
- **CDN version bump**: Cloudflare caches JS for 4h. Rename file to force fresh fetch.
- **MkDocs instant nav**: Use `document$.subscribe()` for PJAX navigation compatibility.
- **Graph data sparsity**: If related pages show only 2-3 links (index pages), graph.json lacks `[[wikilinks]]` cross-reference edges. See `wiki-knowledge-graph` skill -> "Graph Edge Enrichment" for the post-processing fix.

### Debugging Related Pages

When the section shows too few links or wrong links:

1. **Check if JS is loaded**: Open browser console and run:
   ```javascript
   document.querySelectorAll('script[src*="related-pages"]')
   ```

2. **Check the rendered UL content**:
   ```javascript
   var h2 = document.querySelector('h2#_8');
   var ul = h2 ? h2.nextElementSibling : null;
   while (ul && ul.tagName !== 'UL') ul = ul.nextElementSibling;
   ul.innerHTML;
   ```

3. **Diagnose graph data sparsity** -- check how many other files the current page connects to in the graph data:
   ```bash
   python3 << 'PYEOF'
   import json
   with open('/llm-wiki/docs/data/graph/graph.json') as f:
       data = json.load(f)
   nodes = data.get('nodes', [])
   links = data.get('links', [])
   
   target_file = "concepts/vibe-trading/项目总览.md"
   target_ids = set(n['id'] for n in nodes if n.get('source_file') == target_file)
   
   linked = set()
   for l in links:
       s_in = l['source'] in target_ids
       t_in = l['target'] in target_ids
       if s_in or t_in:
           other = l['target'] if s_in else l['source']
           if other not in target_ids:
               for n in nodes:
                   if n['id'] == other:
                       sf = n.get('source_file', '')
                       if sf and sf != target_file: linked.add(sf)
                       break
   print(f"{len(linked)} linked files")
   for sf in sorted(linked): print(f"  {sf}")
   PYEOF
   ```
   If this shows 0-3 files (especially just index pages), the graph extraction missed the cross-references.

4. **Browser console for JS errors**: `browser_console(clear=true)` then navigate to the page, then `browser_console()` to check for fetch errors.

## Natural Language Graph Query

Client-side query engine that loads `graph.json` and enables natural language queries via keyword matching + BFS shortest path across the knowledge graph.

See `references/natural-language-graph-query.md` for the full implementation guide.

### Quick Setup

1. Create `docs/concepts/graph-query.md` with a search input div and `window.__GRAPH_QUERY_CONFIG__`
2. Create `docs/javascripts/graph-query.v1.js` with the minified query engine
3. Add to mkdocs.yml:
   ```yaml
   extra_javascript:
     - javascripts/graph-query.v1.js
   nav:
     - 🔗 知识图谱:
       - 图查询: concepts/graph-query.md
   ```

### How It Works

User enters natural language → engine tokenizes (CJK char split + English word split + stop word filter) → 4-level node matching (exact_label > label_contains > filename_contains > id_contains) → BFS shortest path between matched groups (max 6 steps) → renders interactive clickable path cards with community trajectory.

### Example Queries

| Input | Finds |
|-------|-------|
| `Vibe-Trading 等保` | Cross-community path between Vibe-Trading and 等保 nodes |
| `赵小杰 测评机构` | Shortest path from portfolio to assessment org |
| `setup 涉及哪些页面` | All sub-pages of setup-guide |

### Key Technique: JS Minification

Since `skill_manage write_file` rejects JavaScript with backticks in the body and shell heredocs can trigger timeouts, the engine JS file is produced as a single-line minified IIFE. This fits in a single `write_file` call and avoids the complex escaping issues with `python3 -c "open().write()"`.

### Pitfalls

- **`document$.subscribe()` alone is NOT reliable on direct page loads**: The standard pattern silently fails when the page is first navigated to directly (not via PJAX). **Fix**: Wrap initialization in `setTimeout(setupUI, 150)` inside the callback, AND add a recursive polling fallback:
  ```javascript
  function setupUI() {
    var inp = document.getElementById('graph-query-input');
    if (!inp) { setTimeout(setupUI, 300); return; }  // keep polling
    // attach events...
  }
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function() { setTimeout(setupUI, 150); });
  }
  ```
  This pattern applies to ALL client-side JS features in MkDocs Material with `navigation.instant`.
- **Write path discrepancy**: In this profile, `write_file` resolves to `/opt/data/` but the wiki content lives at `/llm-wiki/`. Files written to `docs/concepts/graph-query.md` land at `/opt/data/docs/` which MkDocs never sees. **Fix**: Use `terminal()` with `cat > file << 'EOF' ... EOF` heredoc to write files directly to `/llm-wiki/docs/`.
- **Runtime-audit location mismatch (NOT the same as write path)**: When VERIFYING the live graph — searching for `graph.json`, `build-graph.py`, `graphify-out/`, or checking what the site actually serves — search `/llm-wiki/`, NOT `/opt/data/llm-wiki/` or `/opt/data/profiles/...`. A session once wasted 10+ tool calls searching the wrong trees before discovering the live source is the container path `/llm-wiki` (host `/home/devtoy/llm-wiki`, mounted from `/dev/sda1`, NOT a volume under `/opt/data`). The ECharts viewer fetches `/data/graph/graph.json` (absolute). To confirm the live data: hit `https://wiki.devtoy.xyz/data/graph/graph.json` (expect HTTP 200) or `cat /llm-wiki/docs/data/graph/graph.json`. NOTE: stale docs may reference `docs/javascripts/graph-data.json` — that path is OBSOLETE; the current fetch target is `/data/graph/graph.json`. Never conclude "the graph is broken / missing" from a 404 on the old path.
- **Graphify skill ownership drift**: The `graphify-wiki` and `wiki-knowledge-graph` skills that DRIVE this wiki's graph were stored under the *investment* profile's skills dir, not llm-wiki, even though they serve llm-wiki exclusively. Before concluding a Graphify skill is missing, grep BOTH `profiles/llm-wiki/skills/` AND `profiles/investment/skills/`. Consolidate into the llm-wiki profile to avoid config drift or accidental deletion.
- **JS version bump = two edits**: Rename file (`v1` → `v2`) AND update `mkdocs.yml`. Shell heredoc for file; `python3 -c` string replacement for yml (since `patch`/`write_file` are blocked on `/llm-wiki/` paths).
- **`navigation.instant` strips inline scripts**: Always use `extra_javascript` + external JS + `document$.subscribe()` (same as ECharts viewer).
- **Large graph.json load**: ~633KB on first fetch; loading indicator is built in.
- **Graph sparsity**: Few cross-community edges → no paths. BFS fallback to top candidates across different communities helps.
- **CJK single-char ambiguity**: Whitelist of meaningful chars prevents false matches.
- **CF cache**: Bump JS version for logic changes; URL mapping changes live in .md page, not JS.

## Verification Script

See `scripts/verify-panzoom.sh` — checks 18 items: DOM structure, buttons, functions, events, old-code removal, hint text.

```bash
bash scripts/verify-panzoom.sh https://wiki.example.com/concepts/knowledge-graph/
# Expected: 18/18 PASS, exit 0
```

## Runtime Audit Reference

Before any live-wiki or Graphify verification for this user, read `references/llm-wiki-runtime-audit.md` — it records the correct container paths (`/llm-wiki`, not `/opt/data/llm-wiki`), Graphify's native visualization vs the ECharts add-on, the obsolete `graph-data.json` path trap, and the Graphify skill-ownership drift between profiles. Skipping it causes wasted tool calls searching the wrong filesystem tree.

## Graph Viewer Verification Checklist

After setting up or fixing a graph-viewer page:

1. `docker restart llm-wiki` — **mandatory** for any mkdocs.yml change (extra_javascript)
2. Check browser: page should show ECharts graph with nodes
3. Verify: page source has NO inline `<script>` with echarts init code (would indicate old approach)
4. Verify: page loads `echarts.min.js` AND `graph-viewer.js` as `<script src=...>` tags (not inline)
5. Test: scroll zoom, drag pan, click node → navigate to wiki page
6. Test: responsive — graph container fills available width
7. Check browser console: no errors (graph.json fetch, echarts init)
