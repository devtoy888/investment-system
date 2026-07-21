# LLM Wiki Runtime Audit & Graphify Notes (DevToy deployment)

Condensed from a live audit (2026-07-19). Read before any wiki runtime/Graphify work for this user.

## 1. Live wiki location (CRITICAL)
The served wiki is NOT under `/opt/data`. Runtime source is on a separate disk mount:
- Host (Oracle box): `/home/devtoy/llm-wiki`
- llm-wiki container: host `/home/devtoy/llm-wiki` -> container `/llm-wiki` (`/dev/sda1`, not a `/opt/data` volume)
- Build scripts: `/llm-wiki/scripts/build-graph.py`, `rebuild-graph.py`
- Graphify output: `/llm-wiki/graphify-out/` (graph.json ~716KB, graph.svg ~3MB, graph.canvas, obsidian/)
- Served graph data: `/llm-wiki/docs/data/graph/graph.json` -> `https://wiki.devtoy.xyz/data/graph/graph.json`
- Site: `https://wiki.devtoy.xyz` (MkDocs Material + CF Tunnel)

**Rule:** verify live artifacts at `/llm-wiki/`, never `/opt/data/llm-wiki/` (that tree is just this skill's stored copy and looks empty of runtime output).

## 2. Graphify has native visualization - ECharts is a recommended add-on, not mandatory
- Graphify (`graphifyy`, PyPI, Graphify-Labs, MIT, active - 0.9.19 as of audit) outputs `graph.html` (D3 force-directed, click/zoom/filter/search), `graph.svg`, `graph.json`, `GRAPH_REPORT.md`. It DOES have data-display capability on its own.
- This wiki additionally renders via **ECharts** (`graph-viewer.v2.js` + `graph-query.v3.js`) - chosen by a prior model, not user-required.
- graph.json edges carry `confidence` (EXTRACTED|INFERRED) + `confidence_score` + `relation` + `source_location` (line number) + `source_file`. Nodes carry `community`, `community_name`, `url`, `source_file`.
- **Gap found:** ECharts viewer does NOT use the `confidence` field for edge coloring (Jsong's design colors green=EXTRACTED / yellow=INFERRED). Node click->wiki navigation exists in skill template but verify the deployed `graph-viewer.v2.js` wires it via the `url` field.
- **Decision point for user:** keep ECharts (visual parity with MkDocs theme) but add confidence coloring + click navigation, OR drop ECharts and serve Graphify's native `graph.html`.

## 3. Reference-design gap analysis (vs Jsong / Kunal)
| Requirement | Status |
|---|---|
| 3-layer + SCHEMA + auto graph + public site | met/exceeds |
| Per-page "Related (from Graphify)" injection (EXTRACTED/INFERRED + community) | NOT done; only graph-viewer top community list |
| Edge confidence coloring | NOT done |
| Contradiction-checking prompt in ingest (Kunal) | missing |
| Incremental graph rebuild | full rebuild daily, not incremental |

## 4. Graphify skill ownership drift (FIX-IN-PROGRESS)
- `graphify-wiki` + `wiki-knowledge-graph` skills were in `profiles/investment/skills/` but serve llm-wiki ONLY.
- Action: migrate to `profiles/llm-wiki/skills/`. Before assuming a Graphify skill is absent, grep BOTH profiles.

## 5. Path gotchas
- `docs/javascripts/graph-data.json` referenced in old setup-guide cron is OBSOLETE. Live fetch target is `/data/graph/graph.json` (absolute). A 404 on the old path does NOT mean the graph is broken.
- Cloudflare caches JS 4h - bump `graph-viewer.vN.js` + update `mkdocs.yml` extra_javascript, then `docker restart llm-wiki`.
- `docker restart llm-wiki` is mandatory after any `mkdocs.yml` change.
