# related-pages.js: Known Pitfalls & Fixes

Mistakes made during the P2 implementation that future sessions should avoid.

## 1. `document$` does NOT fire on initial page load

`document$.subscribe()` only fires on subsequent PJAX navigations. If the init code ONLY subscribes to `document$`, the JS never runs on the user's first visit.

**✅ Fix**: Always call init immediately AND subscribe:
```javascript
// Immediate init (for first page load):
(function(){ setTimeout(loadFunction, 300); })();
// PJAX subscription (for subsequent navigations):
if (typeof document$ !== "undefined") {
  document$.subscribe(function(){ setTimeout(loadFunction, 100); });
}
```
Using an IIFE + `document$` dual pattern ensures the code runs on both cold load and PJAX nav.

## 2. `while (sibling) { sibling.remove() }` destroys page layout

This pattern removes ALL DOM siblings after the `h2` heading, including the "回到页面顶部" button and any other content below the 图谱关联 section.

**✅ Fix**: Target only the static placeholder elements (first `<p>` and `<ul>`):
```javascript
var h2 = section.querySelector("h2");
if (h2) {
  var el = h2.nextElementSibling;
  for (var n = 0; n < 2 && el; n++) {
    var next = el.nextElementSibling;
    if (el.tagName === 'P' || el.tagName === 'UL') { el.remove(); }
    el = next;
  }
}
```

## 3. XHR vs fetch race conditions

When both `loadRelatedPages` (XHR) and `loadRelatedPagesFetch` (fetch) are active, they fight:
- fetch adds items → XHR removes `.related-page-item` elements → XHR callback fails to re-add
- Result: no related pages visible despite console logging "Found N related pages"

**✅ Fix**: Use only ONE approach. Prefer `fetch()` over XHR (simpler, better error handling). Do NOT run two versions with staggered timeouts.

## 4. MkDocs PJAX caches script execution

After `docker restart`, users need Ctrl+Shift-R (hard refresh) to clear MkDocs' in-memory PJAX cache. Without it, old JS may run on new content, or new JS might not execute at all when navigating via sidebar clicks.

## 5. Cloudflare requires new filenames for JS cache busting

Query params (`?v=2`) do NOT work — Cloudflare respects the `Cache-Control` header set by MkDocs, which ignores query strings. Only new filenames force a fresh download:
```bash
cp related-pages.v{N}.js related-pages.v{N+1}.js
sed -i 's/v{N}\\.js/v{N+1}.js/g' mkdocs.yml
docker restart llm-wiki
```

## 6. PAGE_URLS must include subdirectory paths

Bad: `"概述": "/概述/"` — this does NOT match the real MkDocs URL.
Good: `"概述": "/concepts/网络安全等级保护/概述/"`.

The mapping must be auto-generated from the actual file tree, not from just the filename stem:
```python
for root, dirs, fnames in os.walk('/llm-wiki/docs'):
    for f in fnames:
        if not f.endswith('.md'): continue
        rel = os.path.relpath(os.path.join(root, f), '/llm-wiki/docs')
        fn_stem = f.replace('.md', '')
        page_urls[fn_stem] = '/' + rel.replace('.md', '') + '/'
```

## 7. Multiple `index.md` files overwrite each other in PAGE_URLS

When generating `page_urls` from all `.md` files, each `index.md` overwrites the previous one. Only the LAST `index.md` survives in the mapping. Index files should be stored in INDEX_URLS instead, keyed by directory path.

**✅ Fix**: In the URL generation script, skip `index.md` files in `page_urls` — they are handled by `index_urls`:
```python
if f == 'index.md':
    # Add to index_urls, NOT page_urls
    key = 'root' if dirname == '' else dirname
    index_urls[key] = url
    # Do NOT add to page_urls — "index" key would be overwritten
else:
    page_urls[fn_stem] = url
```

## 8. `section.querySelector("h2")` re-queries WRONG h2 ⚠️ CRITICAL

When `section = headings[i].parentElement` captures the `<article>` element (which contains ALL h2s), `section.querySelector("h2")` returns the **FIRST** h2 in the article, NOT the one that was matched.

**Example**: The knowledge-graph page has `## 图谱概览` first and `## 📊 图谱关联` last. `section.querySelector("h2")` returns "图谱概览" even though the code matched "📊 图谱关联". Badges get injected under the wrong heading.

**✅ Fix**: Save a reference to the matched h2 element before it goes out of scope:
```javascript
for (var i = 0; i < headings.length; i++) {
    if (headings[i].textContent.indexOf("图谱关联") >= 0) {
        section = headings[i].parentElement;
        var matchedH2 = headings[i];  // ← SAVE THIS
        break;
    }
}
// Later:
var h2 = matchedH2 || section.querySelector("h2");  // ← USE THE SAVED REFERENCE
```

## 9. Self-reference filter compares full path vs short name

The filter `if (!tf || tf === currentFile) continue;` compares `"concepts/6dim-analysis-framework.md"` (full path from graph.json source_file) against `"6dim-analysis-framework"` (PAGE_URLS key). They NEVER match, so the current page's own graph nodes appear as "related" pages.

**Symptom**: An empty/broken link appears in the 图谱关联 list linking to the same page with a slug label like "6dim-analysis-framework".

**✅ Fix**: Compare by basename (strip directory + .md extension):
```javascript
var tfBase = tf.split("/").pop().replace(/\.md$/, "");
if (!tf || tfBase === currentFile) continue;
```

## 10. Root path `/` not in PAGE_URLS (homepage matching fails)

The homepage `/` has no entry in PAGE_URLS (which only stores non-index pages). The URL matching loop only searches PAGE_URLS, so the homepage never finds a match.

**Symptom**: On the homepage, static content in 图谱关联 section is removed but no dynamic content is injected. Console shows `"Page not in mapping: "`.

**✅ Fix**: Also search INDEX_URLS:
```javascript
if (!currentFile) {
    for (var dir in INDEX_URLS) {
        if (INDEX_URLS[dir].replace(/\/$/, "") === path) {
            currentFile = dir === "root" ? "index.md" : (dir + "/index.md");
            break;
        }
    }
}
```

## 11. URL-level self-reference dedup needed

Even with basename comparison (pitfall 9), some graph edges still connect a page to itself through different node IDs. These should be filtered by comparing the TARGET URL against the current page URL.

**✅ Fix**: Compare the resolved URL of each related page against the current page URL:
```javascript
var currentPath = window.location.pathname.replace(/\/$/, "");
var filteredKeys = [];
for (var ki = 0; ki < Object.keys(rel).length; ki++) {
    var k = Object.keys(rel)[ki];
    var url = getUrlForNode(rel[k]);
    if (url.replace(/\/$/, "") === currentPath) continue; // skip self-link
    filteredKeys.push(k);
}
```

## 12. Content removal must happen AFTER currentFile check

If the static content `<p>` and `<ul>` are removed BEFORE checking that `currentFile` was found, and `currentFile` isn't found (e.g., homepage before the INDEX_URLS fix), the section is left empty with no replacement.

**✅ Fix**: Reorder the function:
1. Find the h2 section
2. Match currentFile (search PAGE_URLS + INDEX_URLS)
3. If no match, log and return (keep static content visible)
4. Fetch graph.json
5. In the callback: remove static content → inject dynamic content

## 13. Git SHA is not a durable identifier

Do NOT reference a specific git SHA in graph edge data or related-pages URL maps. SHAs change on every push and the JS will silently fail to match pages. Use stable filenames or relative paths instead.

## 14. Confidence badge labels should be bilingual

Users unfamiliar with the EN labels EXTRACTED/INFERRED/LIKELY won't understand them. Always add Chinese translation:

```javascript
var confLabel = {
    'EXTRACTED': 'EXTRACTED (直接引用)',  // green — [[wikilinks]]
    'INFERRED': 'INFERRED (推断关联)',    // amber — same-directory
    'LIKELY': 'LIKELY (弱关联)'           // gray — shared tags
}[info.confidence] || info.confidence;
```

Rendered as: `<span class="related-conf related-conf-EXTRACTED">EXTRACTED (直接引用)</span>`

## 15. Don't hardcode `[]()` links for PEP 508 URLs in graph data

When adding graph edges from `[[wikilinks]]` in markdown, ensure the URL mapping can resolve PEP 508-style URLs (like `datasets @ https://...`). These appear in `requirements.txt` files ingested into the wiki. The graph enrichment script should skip non-markdown links.

## 16. `enrich-graph.py` INFERRED regression — all edges become EXTRACTED

**Symptom**: After a rebuild, `contradiction-check` / graph stats show 0 INFERRED edges (e.g. 820 edges all `EXTRACTED`). The same-directory inference dimension is silently lost.

**Root cause**: The original `enrich-graph.py` added `(f1, f2)` to `existing` on the *first* pair inside the inner loop, so every subsequent pair in the same directory was skipped by `if (f1,f2) in existing`. Also the wikilink branch pre-seeds `existing` with `(rel_path, target_file)`, which the INFERRED branch then collides with.

**✅ Fix** (`/llm-wiki/scripts/enrich-graph.py`): only add to `existing` when an edge is *actually emitted*; iterate ALL pairs in a directory; never block on a prior intra-dir pair. Expected after fix: ~890 EXTRACTED + ~160 INFERRED ≈ 1050 edges.

**Verify**: `python3 /llm-wiki/scripts/enrich-graph.py` → confirm both counters > 0.

## 17. `resolveCurrentFile()` must `decodeURIComponent` the pathname

**Symptom**: Pages under a subdirectory with a **Chinese path** (e.g. `/concepts/网络安全等级保护/概述/`) show 0 related items, while ASCII-path pages work. No JS console error.

**Root cause**: `window.location.pathname` returns the **percent-encoded** URL (`/concepts/%E7%BD%91.../%E6%A6%82...`). `PAGE_URLS` keys are decoded Chinese. The equality `PAGE_URLS[fn] === path` never matches → `currentFile` stays `""` → 0 edges.

**✅ Fix**: `var path = decodeURIComponent(window.location.pathname.replace(/\/$/, ""));` at the top of `resolveCurrentFile()`.

## 18. Subdir pages need a `stem2ids` index, not just `f2id`

**Symptom**: After fixing #17, Chinese-subdir pages STILL show 0 items even though graph.json has edges for them.

**Root cause**: `currentFile` resolves to the filename *stem* (e.g. `概述`), but `f2id` is keyed by the **full `source_file`** (`concepts/网络安全等级保护/概述.md`). `f2id['概述']` is `undefined`. ASCII-path pages worked only by accident (stem === basename === source_file basename).

**✅ Fix**: build a second map `stem2ids` keyed by `source_file.split("/").pop().replace(/\.md$/,"")`, and resolve `var curIds = f2id[currentFile] || stem2ids[currentFile] || [];`.

## 19. CF cache busting via `?v=N` query string DOES work here (nuance vs pitfall #5)

**Important correction to pitfall #5**: The earlier note claimed "query params don't work with Cloudflare." For THIS wiki it is the opposite — Cloudflare serves a *stale cached copy* of the **bare** `related-pages.v20.js` URL, but a **different-query URL** (`related-pages.v20.js?v=2`) correctly bypasses the cache and hits origin (verified: curl bare → old content, curl `?v=2` → new content). 

**✅ Working pattern**: in `mkdocs.yml` reference the JS with a `?v=N` suffix:
```yaml
extra_javascript:
- javascripts/related-pages.v20.js?v=2
```
On each JS change, bump `?v=` (or bump the filename vN). This forces CF to fetch fresh. (The earlier "filename-only" advice is fine too, but `?v=` avoids creating N file copies.)

## 20. Auto-create the `📊 图谱关联` section for pages lacking the h2

**Symptom**: Entity pages (`/entities/hermes-agent/`) and YouTube source pages (`/sources/youtube/...`) show NO related section at all, while concept pages (which happen to contain `## 图谱关联`) do.

**Root cause**: `related-pages.js` did `if (!section) return;` — pages without a manual `## 图谱关联` heading were skipped entirely.

**✅ Fix**: in the section resolver, if no `图谱关联` h2 is found, create one and append it to `<article>` (before the trailing `<hr>` if present):
```javascript
var art = document.querySelector('article');
if (art) {
  var h2 = document.createElement('h2');
  h2.id = '图谱关联'; h2.textContent = '📊 图谱关联';
  var sep = art.querySelector('hr');
  if (sep) art.insertBefore(h2, sep); else art.appendChild(h2);
  section = h2.parentElement; matchedH2 = h2;
}
```

## 21. Live multi-angle browser testing is the ONLY way these surface

All of #16–#20 were invisible to static checks, build logs, and single-page smoke tests. They were found only by: (a) loading 4+ page *types* in a real browser (concept / entity / homepage / Chinese-subdir / YouTube-source), (b) asserting actual DOM via `browser_console` (`document.querySelectorAll('.related-page-item').length`), (c) checking `window.location.pathname` decoding, (d) `curl`ing the served JS with vs without `?v=` to detect CF staleness. **Do not declare the related-pages feature done on build success alone.**
