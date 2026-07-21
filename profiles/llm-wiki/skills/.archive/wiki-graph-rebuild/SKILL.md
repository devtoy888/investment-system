---
name: wiki-graph-rebuild
title: Wiki Graph Rebuild
description: "Post-feed workflow: lint -> fix -> rebuild graph -> deploy to website. Run after creating/updating wiki markdown files."
---

# Wiki Graph Rebuild

Post-feed workflow for LLM Wiki. After creating/updating markdown files in `/llm-wiki/docs/`, follow this pipeline.

## Full Post-Feed Workflow

```
1. Create/update .md files
   ↓
2. Lint check (optional but recommended)
   ↓
3. Auto-fix common issues (optional)
   ↓
4. Rebuild knowledge graph
   ↓
5. ⚠️ Bump JS version -> only then ask user to restart
```

## Step-by-Step

### 1. Lint Check

```bash
python3 /llm-wiki/scripts/lint-wiki.py
```

Verify 0 errors, acceptable warnings. See `wiki-lint` skill for details.

### 2. Auto-Fix Common Issues

```bash
python3 /llm-wiki/scripts/fix-wiki.py
```

Fixes missing frontmatter, invalid types, broken wikilinks, orphan pages.

### 3. Rebuild Knowledge Graph

```bash
/llm-wiki/scripts/.graphify-venv/bin/python3 /llm-wiki/scripts/rebuild-graph.py
```

This pipeline:
- Runs graphify extraction -> build -> cluster -> export (full rebuild with `force=True`)
- Runs `enrich-graph.py` to add `[[wikilinks]]` edges (EXTRACTED) + same-directory inference (INFERRED)
- Copies `graph.json` and `graph.svg` to `docs/data/graph/` and `docs/images/`

### 4. Bump JS Version BEFORE Asking for Restart

**CRITICAL: Always increment the version number FIRST, then ask for restart.**

Pattern:
```bash
# 1. Copy old JS with incremented version
cp /llm-wiki/docs/javascripts/related-pages.v{N}.js \
   /llm-wiki/docs/javascripts/related-pages.v{N+1}.js

# 2. Update mkdocs.yml to reference new version
sed -i 's/related-pages\.v{N}\.js/related-pages.v{N+1}.js/g' /llm-wiki/mkdocs.yml

# 3. Then tell user: "Please restart: docker restart llm-wiki"
```

Why: Cloudflare caches JS files aggressively by URL. A content change without version bump = users see stale JS. Incrementing the version creates a brand new URL that bypasses all caches.

**Do NOT:**
- Ask user to restart, then realize CF cached old version, then bump version, then ask again
- Bump version and restart in one step without telling the user what happened

### 5. Restart Container

```bash
docker restart llm-wiki
```

Or wait for the 15-min auto-restart host cron to pick it up.

## Auto-Rebuild

A Hermes cron job (`auto-rebuild-graph`) runs every 30 minutes:
- Checks if any `.md` files changed since last rebuild
- If changes detected, runs `rebuild-graph.py`
- Does NOT restart container (host cron restarts llm-wiki every 15 min)

## Scripts Reference

| Script | Path | Purpose |
|--------|------|---------|
| `rebuild-graph.py` | `/llm-wiki/scripts/` | Master pipeline: graphify -> enrich -> deploy |
| `enrich-graph.py` | `/llm-wiki/scripts/` | Adds wikilink edges + inferred edges to graph.json |
| `build-graph.py` | `/llm-wiki/scripts/` | Core graphify extraction (called by rebuild) |
| `trigger-rebuild.sh` | `/llm-wiki/scripts/` | Host-side: docker exec + restart |
| `setup-rebuild-cron.sh` | `/llm-wiki/scripts/` | Install daily 4am rebuild cron on host |

## Graph Data

After rebuild:
- `graph.json` at `/llm-wiki/docs/data/graph/graph.json` (consumed by `related-pages.v{N}.js`)
- `knowledge-graph.svg` at `/llm-wiki/docs/images/knowledge-graph.svg`
- Confidence levels: `EXTRACTED` (direct wikilink), `INFERRED` (same-directory), `LIKELY` (shared tags, reserved)

## Output to Verify

```
OK: N nodes, M edges
  EXTRACTED: X
  INFERRED: Y
```

Expected range: ~630 nodes, ~770 edges.

## Pitfalls

- **No Docker socket** inside Hermes container: `rebuild-graph.py` deploys data to `docs/` but cannot restart. Version bump + restart request is your responsibility.
- **Duplicate entries** on index pages: adding `[[wikilinks]]` to an index file that already has markdown `[]()` links causes duplicate entries. Remove one format.
- **graphify safety check**: `export.to_json` refuses to overwrite if node count drops. The rebuild script adds `force=True` automatically.
- **CF cache on JS files**: New version number is the ONLY reliable cache-busting strategy. Query params (`?v=2`) do not work - Cloudflare ignores them when MkDocs sets `Cache-Control`.
