---
name: wiki-lint
title: Wiki Lint & Health Check
description: Run automated health checks on LLM Wiki content — orphan pages, broken wikilinks, frontmatter completeness, stale pages, index coverage. Auto-fix mode (--apply) safe-completes missing frontmatter fields; other issues report-only.
---

# Wiki Lint & Health Check

Automated QA for Karpathy-style LLM Wikis. Scans all markdown content, reports issues, and auto-fixes common problems.

## Checks (6 items)

| # | Check | Severity | What it finds |
|---|-------|----------|---------------|
| 1 | `orphan_pages` | warn | Content pages with zero incoming `[[wikilinks]]` (raw/ docs excluded) |
| 2 | `broken_wikilinks` | error | `[[wikilinks]]` pointing to non-existent files |
| 3 | `frontmatter_issues` | error | Missing/invalid title, created, updated, type, tags, sources |
| 4 | `stale_pages` | warn | `updated` date >30 days ago |
| 5 | `index_misses` | warn | Files not listed in their directory's `index.md` |
| 6 | `contested_pages` | info | Pages marked `contested: true` (intentional contradictions) |

## Quick Start

```bash
# Report-only mode (default)
python3 /llm-wiki/scripts/lint-wiki.py

# Auto-fix mode — safe frontmatter field completion + restart
python3 /llm-wiki/scripts/lint-wiki.py --apply

# JSON saved to: /llm-wiki/docs/lint-report.json
```

## Frontmatter Requirements

Every `.md` page must start with:

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept|entity|comparison|query|index|raw
tags: [tag1, tag2]
sources: []
---
```

Type field validation (valid set — must match `lint-wiki.py` `valid_types`):
- `index` — directory landing pages (index.md). NOT `meta`
- `concept` — knowledge concepts, frameworks, theories
- `entity` — real-world entities (people, companies, products)
- `comparison` — side-by-side comparisons
- `query` — archived Q&A records
- `raw` — raw source text archives (not for browsing)
- `source` — ingested source material under `sources/` (YouTube transcripts, etc.) — **also valid, add to `valid_types` if lint flags it**

## Wikilink Resolution Order

The lint script resolves `[[wikilinks]]` in 4 strategies (applied in order):

1. **Relative to source file directory** — `os.path.join(src_dir, target)`
2. **Absolute from docs root** — `target` as-is
3. **Filename only** — `target.split('/')[-1]` joined with source dir
4. **Stem-based (Obsidian-style)** — matches any `.md` file whose stem (filename without extension) equals the wikilink target. Built from ALL `.md` files in the wiki (including EXCLUDE_FILES), not just content pages. This resolves `[[setup-guide]]` from `index.md` even though `setup-guide.md` is in EXCLUDE_FILES.

This matches how `mkdocs-obsidian-bridge` plugin resolves wikilinks.

### Auto-Fix via `--apply` Flag (built into lint-wiki.py)

`lint-wiki.py --apply` auto-fixes **safe, non-destructive** frontmatter issues and restarts the container. All other issue classes remain report-only.

**Auto-fix scope (safe, additive only):**
- Missing `title` → derived from filename
- Missing `created`/`updated` → set to file mtime
- Missing `type` → inferred from directory (concepts/→concept, entities/→entity, etc.)
- Missing `tags` → set to `[]`
- Missing `sources` → set to `[]`

**Report-only scope (requires human judgment):**
| Issue | Why not auto-fix |
|-------|-----------------|
| `[[wikilinks]]` literal in prose | May need backticks or rephrase — ambiguous |
| `raw/` / `sources/` frontmatter | Immutable source material, never touch |
| `type: source` flagged invalid | Already added to `valid_types` in lint script |
| Real orphan (no nav + no wikilinks) | Fix is adding to `mkdocs.yml` nav, not auto-fix |
| Stale pages (>30 days) | Bumping `updated` date masks real staleness |
| Index misses | Index structure needs human review |

**Cron usage:**
```bash
# lint-wiki.py --apply in cron = auto-fix + report
# Cron must use profile-copied script: /opt/data/profiles/llm-wiki/scripts/lint-wiki.py --apply
```

## Auto-Run via Cron

The lint can run before graph rebuild to ensure clean data:

```bash
# In rebuild-graph.py, add before graphify extraction:
import subprocess
subprocess.run(['python3', '/llm-wiki/scripts/lint-wiki.py'], timeout=60)
```

## Supplementary Tools

### Surprising Connections Detection

Find unexpected cross-domain paths in the knowledge graph:

```bash
python3 /llm-wiki/scripts/surprising-connections.py
```

Generates `/llm-wiki/docs/concepts/surprising-connections.md` with:
- Shortest paths between topic areas (Vibe-Trading ↔ 等保, 实体 ↔ 查询, etc.)
- Hub pages that bridge multiple domains
- File-level BFS (not node-level) for clean output

## Pitfalls

### Orphan Detection — nav-referenced pages are NOT orphans

A page reachable via mkdocs `nav:` is a valid entry point even with zero `[[wikilinks]]` incoming. The orphan check MUST consult `mkdocs.yml` `nav:` and exclude those paths. **Two real pitfalls:**
- The nav-extraction regex must include Chinese chars and hyphens: `[\w/一-鿿.-]+\.md` — `\w` alone misses `hermes-agent.md` (hyphen) and Chinese filenames.
- `raw/` and `sources/` are immutable source material, never nav-linked and never wikilink-targeted — exclude them from the orphan count entirely.
- **Do NOT "fix" a nav-orphan by adding `[[wikilinks]]`** — the real fix is adding it to `mkdocs.yml` `nav:`. Forcing wikilinks pollutes source pages.

### frontmatter check must skip `raw/` and `sources/`

Per SCHEMA, `raw/` and `sources/` are immutable captured material and are NOT required to carry `title/created/updated/type/tags/sources`. The frontmatter completeness check should skip any file whose top-level dir is `raw` or `sources`. Otherwise you get 13+ false-error "Missing: sources" on every YouTube transcript.

### Literal `[[wikilinks]]` in prose is NOT a broken link

When a page explains Obsidian syntax ("supports `[[wikilinks]]`"), the brackets are descriptive, not a link. The wikilink scanner must strip fenced ``` ``` ``` and inline `` ` `` code spans before regex-matching `[[...]]`, or it will false-flag `wikilinks.md` (a non-existent target) as broken.

### Cron is report-only UNLESS lint is invoked with --apply

`lint-wiki.py` (no args) only writes `lint-report.json` and prints. A cron running it without `--apply` does NOT auto-remediate. If the user expects auto-fix, invoke with `--apply`. (User flagged this exact gap: "你做了自动修复处理了吗" after a cron reported 61 issues with zero fixes applied.)

### Wikilink Resolution Depends on Source File Location

`[[filename]]` from different directories resolves differently:
- `entities/index.md` → `[[zhao-xiaojie-portfolio]]` → `entities/zhao-xiaojie-portfolio.md` ✅
- `concepts/index.md` → `[[6dim-analysis-framework]]` → `concepts/6dim-analysis-framework.md` ✅
- Both are resolved correctly by the 3-strategy algorithm.

### Index Coverage Requires File Content Check

The index miss check reads the actual text of `index.md`. It checks if the short filename (without path) appears anywhere in the index content. This catches entries added as markdown links `[]()` but not wikilinks `[[]]`, or vice versa.

### frontmatter `---` Parsing

The script splits on `---` and expects exactly 3 parts: `---`, frontmatter, body. Files with `---` inside code blocks or raw content may misparse. Verified working on LLM Wiki content which follows standard frontmatter conventions.
