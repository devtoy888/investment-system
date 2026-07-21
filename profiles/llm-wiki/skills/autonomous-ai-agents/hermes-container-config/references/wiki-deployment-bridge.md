# LLM Wiki: Docker/Remote Deployment Patterns

## Problem

The built-in [llm-wiki skill](research/llm-wiki) assumes the wiki directory is on a local machine. When Hermes runs in Docker on a remote server (e.g. Oracle ARM), Obsidian cannot directly open the server's `~/wiki/` directory. The wiki and the Obsidian vault live on different machines.

## Architecture: Git Bridge

```
Server ~/wiki/  ←── git push ──→  CNB/GitHub  ←── git pull ──→  MacBook ~/DevToyWiki/
(Agent writes)    (cron daily)     (100G free)    (obsidian-git plugin)  (Obsidian reads)
```

## Setup Steps

### Server side
1. Mount wiki volume in docker-compose.yml: `- ~/wiki:/wiki`
2. Set `WIKI_PATH=/wiki` env var
3. Initialize git in `/wiki` + remote add CNB
4. Cron job: daily `git add -A && git commit -m "auto sync" && git push cnb main`
5. Optional reverse sync: cron job 30min later `git pull cnb main`

### MacBook side
1. `git clone https://devtoy@cnb.cool/devtoy/llm-wiki.git ~/DevToyWiki`
2. Obsidian: open folder as vault → `~/DevToyWiki`
3. Install obsidian-git plugin → auto-pull every 30 min

## Content-Type for Chinese Files on R2

When uploading reference documents to R2:

| Content | Content-Type | Reason |
|---------|-------------|--------|
| Chinese markdown | `text/plain; charset=utf-8` | `text/markdown` causes browser garbled text |
| HTML wrapper | `text/html; charset=utf-8` | Safe for all browsers |

Use companion script: `python3 /opt/data/scripts/r2_upload_and_verify.py doc.md remote-key`

## Frontend Deployment (MkDocs)

| Component | Purpose | Format |
|-----------|---------|--------|
| MkDocs Material | Wiki web frontend | `docker pull squidfunk/mkdocs-material` |
| Data source | Reads directly from `~/wiki/` | No database needed |
| Domain | wiki.devtoy.cn | Cloudflare Tunnel → localhost:8000 |
| Graph view | mkdocs-network-graph-plugin | From `[[wikilinks]]` |

## Graphify Integration

Not included in the base llm-wiki skill. Two options:

1. **Lightweight**: `mkdocs-network-graph-plugin` — auto-generates graph from `[[wikilinks]]`, zero config
2. **Full**: `pip install graphifyy` + cron job → outputs graph.html/graph.json to `_graph/` dir
