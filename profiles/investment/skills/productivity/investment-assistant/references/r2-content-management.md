# R2 Content Management & Roadmap Pattern

## Charset Fix (2026-07-15)

**Problem**: ROADMAP.md rendered garbled Chinese in browser because `content-type: text/markdown` lacked charset.

**Fix**: Always specify `charset=utf-8` when uploading Chinese content to R2:

```python
# ❌ garbled — no charset specified
upload_to_r2(path, key, 'text/markdown')

# ✅ correct — charset forces browser encoding
upload_to_r2(path, key, 'text/markdown; charset=utf-8')

# HTML also needs it
upload_to_r2(path, key, 'text/html; charset=utf-8')
```

**Underlying bug**: `fund_tools.upload_to_r2()` called r2_uploader.py as subprocess but only passed 2 args (file, key). The third arg `content_type` was silently ignored. Fixed in v7.

## ROADMAP.md

Living tracking document at `fund-system/evolution/ROADMAP.md` on R2.

Sections: status legend, per-module status tables (unique IDs DC-1/PS-7/EV-4), evolution version history, known bugs + P0/P1/P2 TODO, data verification status with expected dates, R2 file index.

Updated after each system evolution.

## roadmap.html

Adaptive dashboard at `fund-system/evolution/roadmap.html` on R2.

Fetches ROADMAP.md via `fetch()`, renders with marked.js (CDN), enriches with colored badges/progress bars/stats cards, mobile-first responsive dark theme. Markdown is single source of truth.
