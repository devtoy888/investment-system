# contradiction-check.py — Static Consistency Gate

> Session 2026-07-19. Lightweight, dependency-free (uses PyYAML from the graphify venv) checker run after every graph rebuild / ingestion batch. Pins quality BEFORE deploy.

## What it checks (6 classes)
| # | Check | Severity | Note |
|---|-------|----------|------|
| 1 | Frontmatter required fields (`title/created/updated/type/tags/sources`) | WARN | `raw/` OCR pages & `index.md` legitimately lack `sources` — known schema gap, not a real contradiction |
| 2 | Date logic: `created <= updated`, both valid `YYYY-MM-DD` | **ERROR** if `updated < created` | Real blocking contradiction |
| 3 | Duplicate `title` across pages | INFO | Potential conflicting facts under one title |
| 4 | `contested: true` pages must carry a contradiction note (`矛盾/冲突/contradict/contested/不一致`) | WARN | Flagged contested pages with no explanation |
| 5 | Same `source_file` in >1 page frontmatter | WARN | Mis-filed page |
| 6 | Tool version drift: same keyword (graphify/mkdocs/hermes/python/node) with differing version literals in different pages | INFO | Cross-page version inconsistency |

## Run
```bash
/llm-wiki/scripts/.graphify-venv/bin/python3 \
  /llm-wiki/scripts/contradiction-check.py
```
Exit code **non-zero on ERROR** (use as a CI/cron gate). Current baseline: 0 ERROR / 48 WARN (WARNs are schema gaps in `raw/`, `index.md`, `log.md` — not blockers).

## Parsing notes
- Frontmatter parsed with `yaml.safe_load` (NOT line-split) — multi-line YAML lists (`sources:\n  - url`) break naive `:` splitters and cause false "missing field" reports.
- Excludes `graphify-out/ data/ stylesheets/ javascripts/ images/ __pycache__` so generated artifacts aren't scanned.

## How to extend
- Add a new check as an `issues.append((LEVEL, loc, msg))` line; LEVEL in `ERROR/WARN/INFO`.
- Add a new version-drift keyword to the `('graphify','mkdocs','hermes','python','node')` tuple in check #6.
- To make a check blocking, ensure it emits `ERROR` — the exit gate keys off `ERROR` only.
- Schema-gap WARNs (e.g. `raw/` pages missing `sources`) are intentional; do NOT promote them to ERROR or the gate will always fail.
