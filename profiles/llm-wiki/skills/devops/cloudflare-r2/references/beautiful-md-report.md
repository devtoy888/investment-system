# Beautiful Markdown → HTML Report Renderer

When you need to publish a wiki changelog / repair log / status report to R2 as a **polished, readable HTML page** (not raw text), the marked.js and Python `markdown` library approaches in `markdown-html-rendering.md` produce *functional* output but leave it visually plain. For a report the user will actually read and share, build a **custom Python renderer** that styles every element type.

## When to use this over marked.js

| Approach | Output quality | Best for |
|----------|---------------|----------|
| marked.js (client-side) | Plain GFM, default browser styles | Quick internal doc, don't care about looks |
| Python `markdown` lib | Plain, limited GFM (no task lists w/o ext) | Quick server-side |
| **Custom renderer** | Hero, badges, cards, dark/light, full element coverage | **User-facing report / changelog / repair log** |

## Critical quality rule

> Render **every** markdown element type your source uses — headings, paragraphs, **bold**, *inline code*, ordered/unordered lists, task-list checkboxes, blockquotes, tables, horizontal rules. Partial beautification (e.g. styling only tables + hero, leaving lists/paragraphs as raw unstyled text) is **worse than plain text** — the user will see inconsistent styling and have to point it out. Cover all types or don't call it "beautified".

## Renderer architecture (concise)

Single function `md_to_html(md_text)` walking lines, emitting HTML parts:

1. **Skip YAML frontmatter.** If line[0] == `---`, scan to the next `---` and drop the block. (Frontmatter otherwise leaks as `<p>title: ...</p>`.)
2. **Inline pass** (applied to every text cell/paragraph):
   - `html.escape()` first
   - `` `code` `` → `<code>...</code>` (blue monospace)
   - `**bold**` → `<strong>...</strong>`
3. **Block dispatch** by line prefix:
   - `# ` → Hero header (first only) or section title
   - `## ` → h2 with left border
   - `### ` → h3
   - `> ` → `<blockquote>` (collect consecutive lines)
   - `|` table row → accumulate, render `<table>` with `<thead>`/`<tbody>`; status column (`✅`/`⏳`/`❌`) → colored badge `<span>`
   - `- ` → `<ul>`; `1. ` → `<ol>` (group consecutive)
   - `[ ]` / `[x]` → checkbox `<li><input type=checkbox disabled>`
   - `---` → `<hr>`
   - `**Standalone bold**` → emphasized lead paragraph (`<p class="lead">`)
   - else → `<p>`
4. **Hero** (first `# `): gradient header + 4 stat cards (pull numbers via regex from the MD: JS version, edge count, done count, cron ID).
5. **Dark/light**: `prefers-color-scheme: dark` media query; CSS variables for bg/card/text/border/badge colors.
6. **Responsive**: `.stat-grid` 4-col → 2-col under 640px; tables in `.table-wrap{overflow-x:auto}`.

## Status badge helper

```python
def badge_cell(text):
    t = text.strip()
    if '✅' in t: return '<span class="badge badge-done">✅ 完成</span>'
    if '⏳' in t: return '<span class="badge badge-pending">⏳ 待办</span>'
    if '❌' in t: return '<span class="badge badge-fail">❌ 失败</span>'
    return inline(t)
```

## Upload

```python
uploader.s3.put_object(
    Bucket=uploader.bucket_name, Key='references/xxx/changelog.html',
    Body=html.encode('utf-8'), ContentType='text/html; charset=utf-8')
# Also upload the raw .md with text/plain; charset=utf-8 for source access
```

## Verification before declaring done

1. Local assert: `HERO in html`, `no frontmatter leak`, `<strong>` count > 0, `<code>` count > 0, `<ol>/<ul>` present, `type="checkbox"` present.
2. Browser: load the R2 URL (add `?nocache=N` to defeat CDN cache), run a `document.querySelectorAll` count assertion for ol/ul/checkbox/strong/code/badge — confirms the *deployed* file is the new one, not a cached old version.
3. Screenshot + vision check for visual consistency.

**Pitfall — R2/CDN cache:** R2 public URLs are CDN-cached. After re-upload, the browser may show the old file. Always verify with a cache-busting query param or a DOM assertion, not just "upload succeeded".
