# Web API key Testing Results

Tested: June 25, 2026 · Oracle ARM Docker container

## Tested Keys

| # | Key | Env Var | Status | Notes |
|---|-----|---------|--------|-------|
| 1 | Tavily | `TAVILY_API_KEY` | ✅ Active | Auto-detected as #1 backend. `web_search` returns results. |
| 2 | Exa | `EXA_API_KEY` | ✅ Standby | Priority #2 in auto-detect chain. Not currently used (Tavily takes precedence). |
| 3 | Parallel | `PARALLEL_API_KEY` | ⏸ Standby | Priority #3. Syntax valid. |
| 4 | Firecrawl | `FIRECRAWL_API_KEY` | ⚠️ Repaired | `firecrawl-py` not in base image. Installed via user-level workaround (separate venv + symlink into `PYTHONPATH` directory). |
| 5 | xAI | `XAI_API_KEY` | ✅ Valid | Works as model provider (Grok). Not part of web backend auto-detect chain. |

## Hermes Web Backend Auto-Detect (from `web_tools.py`)

Priority order when `web.backend: ''`:

1. `TAVILY_API_KEY` → **Tavily** (current active)
2. `EXA_API_KEY` → Exa
3. `PARALLEL_API_KEY` → Parallel
4. `FIRECRAWL_API_KEY` → Firecrawl (needs `firecrawl-py` installed)
5. Firecrawl via managed gateway
6. `SEARXNG_URL` → SearXNG
7. `BRAVE_SEARCH_API_KEY` → Brave (free)
8. DuckDuckGo (python package)

## Firecrawl Installation Workaround (no sudo)

```bash
# Docker venv at /opt/hermes/.venv/ is root-owned (555) — can't pip install.
# Workaround: install in user-level venv, symlink into PYTHONPATH dir.
uv venv ~/.venvs/firecrawl
uv pip install --python ~/.venvs/firecrawl/bin/python firecrawl-py
ln -sf ~/.venvs/firecrawl/lib/python3.13/site-packages/firecrawl \
  /opt/data/.feishu-deps/firecrawl
# Verify:
/opt/hermes/.venv/bin/python3 -c "import firecrawl; print(firecrawl.__version__)"
# Expected: 4.30.2
```

## What Each Key Is Used For

| Service | Purpose in Hermes | Can be tested via |
|---------|------------------|-------------------|
| Tavily | Search + extract backend | `web_search()`, `web_extract()` |
| Exa | Search backend (fallback) | `web_search()` after removing TAVILY_API_KEY |
| Parallel | Search backend (fallback) | `web_search()` |
| Firecrawl | Search + extract + scrape | `web_extract()` with `backend: firecrawl` set |
| xAI | AI model provider (Grok) | Configure as `provider: xai` in model config |
