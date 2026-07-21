---
name: llm-wiki-visualization
description: "Knowledge graph visualization for LLM Wiki: inline Panzoom, SVG graph generation, interactive graph viewers"
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Wiki Knowledge Graph Visualization

Inline Panzoom component for SVG knowledge graphs, interactive graph viewers, and graph generation pipelines.

## When This Skill Activates

- User asks about knowledge graph, graph visualization, or SVG rendering on their wiki
- User wants to make an SVG image zoomable/panable on a wiki page
- User needs an interactive graph viewer for exploring wiki topics
- User asks about Graphify, Gephi, D3.js, or ECharts graph integration

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

### Pitfalls

- **TTC fonts in Matplotlib**: TrueType Collection fonts cause CJK character offset in Matplotlib SVG output. Always use standalone TTF files for CJK text in generated SVGs.
- **Cache busting**: Cloudflare/edge caches SVG files aggressively. Append `?v=N` to force refresh.
- **Docker MkDocs**: Static file updates (SVG, JS) don't trigger hot reload in MkDocs `--dirty` mode. A container restart is required.
- **Wheel scroll conflict**: Without `{passive: false}` and `preventDefault()`, zooming also scrolls the page.

## Verification Script

See `scripts/verify-panzoom.sh` — checks 18 items: DOM structure, buttons, functions, events, old-code removal, hint text.

```bash
bash scripts/verify-panzoom.sh https://wiki.example.com/concepts/knowledge-graph/
# Expected: 18/18 PASS, exit 0
```
