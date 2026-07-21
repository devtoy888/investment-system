# Wiki Repair / Health-Check Changelog Pattern

When the user asks you to assess, plan, and fix wiki issues, you **must** create a changelog document that tracks each fix's before/after state.

## The Pattern (3 steps)

### Step 1: Survey → Create the Changelog

Before touching any files, do a thorough survey of all issues. Then create a changelog document:

**Local copy** → `/llm-wiki/docs/wiki-repair-changelog.md`

Standard frontmatter with type `concept` and tags `[wiki, repair, changelog]`.

Content structure:
- Title: `Wiki 修复对照记录`
- Summary quote describing scope (architecture layer / navigation layer / visual layer)
- Table: `Priority | Issue | Before | After | Status`
- Detailed modification notes with timestamps

### Step 2: R2 Upload (MD + HTML — BOTH Required)

Upload **both** formats to R2. The user explicitly requires this — do not skip.

```
Key prefix: references/wiki-repair/
```

| Format | Key | Content-Type | Purpose |
|--------|-----|-------------|---------|
| Markdown | `references/wiki-repair/changelog.md` | `text/plain; charset=utf-8` | Source, viewable in browser |
| Adaptive HTML | `references/wiki-repair/changelog.html` | `text/html; charset=utf-8` | Rich visual rendering |

**The HTML companion page must be:**
- Self-contained (no external CSS/JS dependencies)
- Adaptive/responsive (media queries for mobile <640px)
- Dark/light mode following `prefers-color-scheme`
- Rich color coding: green rows = done, orange = pending, red = P0 priority
- Summary cards showing completion stats
- Links section showing all modified files
- Todo section for remaining items

**R2 upload via Python** (system Python lacks `boto3`; use Hermes venv):

```python
from r2_uploader import R2Uploader
r2 = R2Uploader()
url_md = r2.upload_file('/tmp/file.md', 'references/wiki-repair/changelog.md',
                        content_type='text/plain; charset=utf-8')
url_html = r2.upload_file('/tmp/file.html', 'references/wiki-repair/changelog.html',
                          content_type='text/html; charset=utf-8')
```

Alternative: `/opt/hermes/.venv/bin/python3 /path/to/script.py`

Content-Type with `charset=utf-8` is REQUIRED for Chinese text readability. Without it, browsers may render garbled characters.

### Step 3: Update the Changelog as Fixes Progress

After each batch of fixes:
1. Update the table status column (⏳ -> ✅ or ❌)
2. Add detailed notes under the modification log section
3. Re-upload the updated files to R2 (overwriting)
4. At the end, append verification results:
   - Browser checks (200 OK, nav grouping, dark mode toggle, custom CSS)
   - Lint results (broken_wikilinks, total error count diff: Before vs After)
   - Docker restart confirmation

## Pitfalls

- **Do NOT create only a local file** — the user WILL correct you. Always upload to R2.
- **Do NOT upload only markdown** — always create an adaptive HTML companion page.
- **Do NOT forget charset in Content-Type** — `text/plain; charset=utf-8` not `text/plain`.
- **Do NOT use the system python** (`/usr/bin/python3`) for R2 uploads — it lacks `boto3`. Use the Hermes venv: `/opt/hermes/.venv/bin/python3`.
- **Do NOT forget to clean up** temp scripts at `/opt/data/_*.py` after execution.
- **Update the doc as you go** — don't wait until all fixes are done to write the changelog.
- **Always run lint before and after** to show the diff (e.g., "broken_wikilinks: 2->0").
- **Always verify in browser after restart** — don't assume changes took effect. Check nav, dark mode, and at least 2 content pages.
