# Firecrawl: Installing in Docker With Root-Owned Venv

## Problem

Hermes Docker images ship with `/opt/hermes/.venv/` owned by **root** (`dr-xr-xr-x`). The container runs as the `hermes` user. Three barriers prevent Firecrawl from working:

| Barrier | Symptom |
|---------|---------|
| Venv not writable | `pip install firecrawl-py` fails with `Permission denied` |
| `HERMES_DISABLE_LAZY_INSTALLS=1` (baked into Dockerfile) | Lazy-install mechanism refuses to even attempt the install |
| `allow_lazy_installs: true` (config) | Contradicts the env var — config says go, environment says stop |

The Dockerfile sets `HERMES_DISABLE_LAZY_INSTALLS=1` deliberately because the venv IS root-owned and any lazy install would fail anyway. But without lazy installs, backends like Firecrawl that aren't bundled in the base image are permanently unavailable.

## Fix: User-Level Workaround (No Sudo)

### Step 1: Create a Separate Venv

```bash
mkdir -p ~/.venvs
uv venv ~/.venvs/firecrawl
uv pip install --python ~/.venvs/firecrawl/bin/python 'firecrawl-py==4.17.0'
```

**Why 4.17.0?** Hermes' `lazy_deps.py` pins the exact version: `"search.firecrawl": ("firecrawl-py==4.17.0",)`. The `_is_satisfied()` check uses `importlib.metadata.version('firecrawl-py')` and compares against `==4.17.0`. Installing any other version (e.g. 4.30.2) makes `_is_satisfied` return False → the `_lazy_ensure()` path raises `FeatureUnavailable` even though the package is importable.

### Step 2: Add to Hermes' Python Path

The running Hermes process has `PYTHONPATH=/opt/data/.feishu-deps:` set. Any package symlinked into `/opt/data/.feishu-deps/` is importable by `/opt/hermes/.venv/bin/python3`.

```bash
# Symlink the package directory
ln -sf ~/.venvs/firecrawl/lib/python3.13/site-packages/firecrawl \
  /opt/data/.feishu-deps/firecrawl

# SYMLINK THE DIST-INFO DIRECTORY (critical, easy to forget)
ln -sf ~/.venvs/firecrawl/lib/python3.13/site-packages/firecrawl_py-4.17.0.dist-info \
  /opt/data/.feishu-deps/firecrawl_py-4.17.0.dist-info
```

**Why dist-info matters:** `importlib.metadata.version('firecrawl-py')` reads from the `.dist-info` directory, not from the package source. Without it, `feature_missing()` returns `('firecrawl-py==4.17.0',)` even though `import firecrawl` succeeds. The Hermes lazy-dep check then raises `FeatureUnavailable` instead of proceeding to use the already-importable backend.

**Why deps aren't a problem:** firecrawl-py's dependencies (httpx, pydantic, websockets, yarl, etc.) are already bundled in the Hermes venv at `/opt/hermes/.venv/`. Only the firecrawl-py package itself is missing from the base image.

### Step 3: Verify

```bash
# Import test (catches missing dist-info)
/opt/hermes/.venv/bin/python3 -c "
from importlib.metadata import version
v = version('firecrawl-py')
import firecrawl
print(f'firecrawl {v} OK')
"

# Web backend auto-detect (now finds Firecrawl as a candidate)
/opt/hermes/.venv/bin/python3 -c "
from tools.lazy_deps import _is_satisfied, feature_missing
print('satisfied:', _is_satisfied('firecrawl-py==4.17.0'))
print('missing:', feature_missing('search.firecrawl'))
"
# Expected: satisfied=True, missing=()
```

### Step 4: Configure Backend (Optional)

Firecrawl is now in the auto-detect chain at priority #4 (after Tavily, Exa, Parallel). To force Firecrawl immediately:

```yaml
# config.yaml
web:
  backend: firecrawl
  search_backend: firecrawl
  extract_backend: firecrawl
```

When Firecrawl is selected, the Hermes tools call `_lazy_ensure("search.firecrawl")` → `feature_missing()` returns empty → `ensure()` returns early at the `if not missing: return` check → **the `HERMES_DISABLE_LAZY_INSTALLS` env var is never reached** because the return happens before the `_allow_lazy_installs()` check.

## Test Commands

After setup, use Hermes built-in tools (NOT curl/Python):

```
web_search(query="Firecrawl features", limit=2)
web_extract(urls=["https://www.firecrawl.dev"])
```

If `web_extract` returns the full page content as clean markdown, Firecrawl is working correctly.

## Backend Auto-Detect Priority

From `tools/web_tools.py:162-171`:

```
1. Tavily     (TAVILY_API_KEY)
2. Exa        (EXA_API_KEY)
3. Parallel   (PARALLEL_API_KEY)
4. Firecrawl  (FIRECRAWL_API_KEY)  ← only if firecrawl-py is importable
5. Firecrawl  (managed gateway)
6. SearXNG    (SEARXNG_URL)
7. Brave      (BRAVE_SEARCH_API_KEY)
8. DuckDuckGo (python package)
```

## Reversion

To switch back to Tavily (or auto-detect):

```yaml
web:
  backend: ''
  search_backend: ''
  extract_backend: ''
```

The symlinks are harmless when not selected — they just sit in the path unused. To fully clean up:

```bash
rm -f /opt/data/.feishu-deps/firecrawl
rm -f /opt/data/.feishu-deps/firecrawl_py-4.17.0.dist-info
```

## Related

- Custom provider key resolution: `references/custom-provider-key-resolution.md`
- Web backend testing: `references/web-api-key-testing.md`
