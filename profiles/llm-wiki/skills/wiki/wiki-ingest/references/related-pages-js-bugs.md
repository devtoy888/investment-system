# related-pages.v{N}.js — Known MkDocs Material JS Pitfalls

Captured from a real v10→v19 iteration of the cross-reference badge injector
(`related-pages.v{N}.js`). Each bug class below is reusable — if you touch this
file again, check against this list instead of re-debugging from scratch.

## Context

`related-pages.v{N}.js` runs on every wiki page. It:
1. Reads the current page path from `window.location.pathname`.
2. Loads `graph.json` (fetched from `/data/graph/graph.json`).
3. Finds neighbor nodes, builds a "📊 图谱关联" list with confidence badges
   (EXTRACTED = green, INFERRED = orange).
4. Appends that list under the matching `## 📊 图谱关联` `<h2>` on the page.

It uses `PAGE_URLS` / `INDEX_URLS` / `f2id` maps for resolution.

## Bug Classes (in order encountered)

| # | Symptom | Root cause | Fix |
|---|---------|-----------|-----|
| 1 | URLs wrong (38→60, subdir pages 404) | Hardcoded `PAGE_URLS` missed Chinese-named + subdirectory pages | Regenerate full `PAGE_URLS`/`INDEX_URLS` from `mkdocs.yml` + filesystem walk |
| 2 | Layout collapses / "回到顶部" button disappears | `section.querySelectorAll('h2')` + `remove()` deleted ALL siblings of the first h2, including the back-to-top button | Only remove the `<p>` + `<ul>` directly, not the whole section's children |
| 3 | List never appears on cold load | `document$.subscribe(fn)` doesn't fire on first paint | Run init directly on load + subscribe for PJAX navigations |
| 4 | Old XHR version fights new fetch version | Two copies of the script loaded | Disable the old XHR version; keep one fetch-based init |
| 5 | Init runs before DOM ready | IIFE + `document$` race | Guard init, re-query DOM each cycle |
| 6 | Badges appear under wrong `📊 图谱关联` section (e.g. under 图谱概览) | `section.querySelector('h2')` returns the FIRST h2 in `<article>` (图谱概览), not the matched one | Save `matchedH2` reference when matching; reuse it |
| 7 | Self-reference link (page links to itself, empty label) | Self-edge from graph not filtered — comparison used full path vs short name | Filter by **basename** (strip dir + `.md`); also dedupe by resolved URL |
| 8 | Homepage (`/`) shows no related pages after static clear | Content deletion ran BEFORE the current-page match check; `/` not in `PAGE_URLS` | Add `INDEX_URLS` matching + move the removal AFTER the currentFile check; map `dir === 'root'` → `index.md` |
| 9 | Stale JS served after edit | Cloudflare edge cache by filename | Bump version v{N}→v{N+1} in filename + `mkdocs.yml` BEFORE restart (see wiki-ingest CF cache rule) |

## Resilient Init Pattern (use this)

```javascript
function initRelated() {
  var path = window.location.pathname.replace(/\/+$/, '') || '/';
  // match against PAGE_URLS + INDEX_URLS ...
  // save matchedH2 = the actual h2 node we matched
  // only remove its <p> + <ul>, then append rebuilt list
}
if (typeof document$ !== 'undefined') {
  document$.subscribe(function(){ setTimeout(initRelated, 150); });
} else if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function(){ setTimeout(initRelated, 150); });
} else { setTimeout(initRelated, 150); }
```

## URL/label helpers

- `getLabelForNode(n)` should return a human label, not the raw filename
  (`6dim-analysis-framework.md` → "6维分析框架"). Fall back to `n.label`.
- Always dedupe by **resolved URL**, not by node id — two nodes can map to the
  same page (e.g. `index.md` referenced from multiple communities).
- Self-ref check: `basename(source_file) === basename(current_page_file)`.
