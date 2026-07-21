---
name: wiki-frontend-deployment
description: "Deploy a MkDocs Material frontend for Hermes LLM Wiki in Docker, with persistent storage, CNB git sync, and CF Tunnel exposure."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [wiki, mkdocs, frontend, docker, deployment, cdn]
    category: devops
    related_skills: [llm-wiki, cloudflare-r2, hermes-container-config]
---

# MkDocs Wiki Frontend Deployment

Deploy a MkDocs Material static site as the web frontend for a Hermes LLM Wiki.
Covers Docker Compose integration, MkDocs Material gotchas, R2 asset delivery,
and CNB git sync patterns.

**Use this when**: The user wants to serve their LLM Wiki as a website alongside
their existing Hermes Agent Docker deployment.

---

## Architecture

```
Hermes container (hermes-main)    MkDocs container (llm-wiki)
┌──────────────────────┐          ┌─────────────────────┐
│ ~/.hermes-main:/opt  │  volume  │ ~/llm-wiki:/docs    │
│ /data                │─────share───→                   │
│ WIKI_PATH=/llm-wiki  │  (/llm-  │ mkdocs serve :8456  │
└──────────┬───────────┘  wiki)   └──────────┬──────────┘
           │                                  │
           │ CNB git push (cron)              │ Docker internal DNS
           ▼                                  ▼
    ┌──────────────┐                  ┌──────────────┐
    │ CNB repository│                  │cloudflared    │
    │ devtoy/wiki   │                  │ tunnel → wiki │
    └──────────────┘                  │ .devtoy.xyz   │
                                      └──────────────┘
```

## Deployment Steps

### 1. Directory Structure

```
~/llm-wiki/                    ← Server-side wiki root
├── docs/                      ← MkDocs content directory (MANDATORY)
│   ├── entities/
│   ├── concepts/
│   ├── comparisons/
│   ├── queries/
│   ├── raw/
│   └── _archive/
├── mkdocs.yml                 ← MkDocs config (at root, outside docs/)
├── scripts/                   ← Helper scripts
├── .git/
└── .gitignore
```

**CRITICAL**: MkDocs requires content to be in a subdirectory (`docs/` by default).
Setting `docs_dir: .` in mkdocs.yml will FAIL because MkDocs forbids the content
directory from being the parent of the config file.

### 2. Docker Compose Integration

Add to the existing `docker-compose.yml`:

```yaml
services:
  # ... existing hermes-main ...

  llm-wiki:
    image: squidfunk/mkdocs-material:latest
    container_name: llm-wiki
    restart: unless-stopped
    volumes:
      - ~/llm-wiki:/docs
    networks:
      - existing-network       # Must be same network as cloudflared
    command: ["serve", "--dev-addr", "0.0.0.0:8456"]  # Use unusual port
```

Also add the wiki volume to hermes-main:

```yaml
services:
  hermes-main:
    volumes:
      - ~/.hermes-main:/opt/data
      - ~/llm-wiki:/llm-wiki   # ← Add this
    environment:
      - WIKI_PATH=/llm-wiki    # ← Add this
```

### 3. MkDocs Configuration

```yaml
# mkdocs.yml (at ~/llm-wiki/mkdocs.yml, NOT inside docs/)
site_name: Wiki Name
site_url: https://wiki.example.com
theme:
  name: material
  language: zh
  features:
    - navigation.instant
    - search.suggest
markdown_extensions:
  - pymdownx.superfences
  - footnotes
plugins:
  - search
```

**Note on wikilinks plugin**: `pip install mkdocs-wikilinks-plugin` is NOT
included in the official image. If you need `[[wikilinks]]` support, either:
- Use a custom Dockerfile: `FROM squidfunk/mkdocs-material:latest && RUN pip install mkdocs-wikilinks-plugin`
- Or use a custom entrypoint script (mounted volume) that pip-installs before serving

### 4. Cloudflare Tunnel Exposure

If using a cloudflared container on the same Docker network:
- **Don't expose host ports** — use Docker internal DNS
- cloudflared config: `http://llm-wiki:8456` (container name, not localhost)
- Cloudflare Dashboard → Tunnel → Add Public Hostname

### 5. CNB Git Sync

**Remote URL format**: `https://cnb.cool/org/repo` (no `.git` suffix needed, but compatible)

```bash
git remote add origin https://cnb.cool/devtoy/llm-wiki
```

#### Authentication

CNB requires: **username=`cnb`** (fixed), **password=access token** (NOT your account password).

**Option A — Token in URL (simplest, but exposes in `git remote -v`):**

```bash
git remote set-url origin https://cnb:TOKEN@cnb.cool/org/repo
```

**Option B — Credential store (recommended, hides token):**

```bash
# 1. Store token using printf (avoids shell heredoc quoting issues)
printf 'protocol=https\nhost=cnb.cool\nusername=cnb\npassword=YOUR_TOKEN\n' | \
  git credential-store --file ~/.git-credentials store
chmod 600 ~/.git-credentials

# 2. Set helper
git config --global credential.helper 'store --file ~/.git-credentials'

# 3. Clean remote URL (no token)
git remote set-url origin https://cnb.cool/org/repo
```

**Option C — `url.insteadOf` (alternative, token hidden in gitconfig):**

```bash
# Set a URL rewrite rule (note: git remote -v will show the substituted URL)
git config --global url."https://cnb:TOKEN@cnb.cool".insteadOf "https://cnb.cool"
git remote set-url origin https://cnb.cool/org/repo
```

⚠️ **Known issue**: Both Option B and Option C may not work reliably depending on
the git version and shell environment. If credential store fails to authenticate
with "Repository Not Found", verify the credential file content and helper config
with `git credential fill`. Option A (token in URL) is the fallback.

#### Auto-push Cron Job

```bash
# Create push script
cat > scripts/wiki-push.sh << 'EOF'
#!/bin/bash
cd ~/llm-wiki
if [ -z "$(git status --porcelain)" ]; then
  exit 0
fi
git add -A
git commit -m "auto sync $(date +%Y-%m-%d %H:%M)"
git push origin main 2>&1
echo "Wiki synced to CNB: $(date)"
EOF
chmod +x scripts/wiki-push.sh

# Add to crontab (runs at 3:00 AM daily)
0 3 * * * /home/user/llm-wiki/scripts/wiki-push.sh
```

---

## Pitfalls

### MkDocs `docs_dir` Restriction
- MkDocs 2.x requires content to be in a subdirectory relative to mkdocs.yml
- `docs_dir: .` (parent of config) → ERROR: "should not be the parent directory"
- The container mounts `~/llm-wiki:/docs`, so content goes to `/docs/docs/`
- Fix: create `docs/` subdirectory, move content there

### Official Image Missing Plugins
- `wikilinks` plugin is NOT in official `squidfunk/mkdocs-material` image
- Only `search` plugin is guaranteed available
- To add plugins: custom Dockerfile or entrypoint script

### Cross-Container File Watching (Docker Bind Mount)
- MkDocs `serve` mode uses inotify to detect file changes
- When files are written from another container (e.g., Hermes writing to a shared volume),
  inotify events may NOT propagate correctly through Docker bind mounts
- `--dirty` flag (`mkdocs serve --dirty`) helps but doesn't fully solve it
- **Workaround**: Add a crontab on the host to periodically restart the container:
  ```bash
  # Every 15 minutes — keeps wiki content fresh without manual restarts
  */15 * * * * docker restart llm-wiki >/dev/null 2>&1
  ```
- **Alternative**: Use `mkdocs build` + nginx static serving (no hot-reload needed)

### Raw HTML Path Resolution in MkDocs
- But **raw HTML** `<img src="../images/foo.svg">` paths resolve relative to the **page URL**, not the markdown file
- For a page at `/concepts/knowledge-graph/`, `../images/foo.svg` resolves to `/concepts/images/foo.svg` (wrong), not `docs/images/foo.svg`
- **Fix**: Always use absolute paths in raw HTML: `src="/images/foo.svg"` — MkDocs serves `docs/images/` at `/images/`
- **Same rule applies to lightbox overlay HTML**: both the thumbnail `<img>` and the overlay `<img>` must use absolute paths

### Editing MkDocs Pages with Raw HTML Blocks

Line-based Python string replacement on markdown files containing multi-line raw HTML is fragile and has caused file corruption (duplicate content, truncated trailing sections) on this project.

**Safer approach**:
1. Read the whole file as a single string
2. Find the exact block boundaries using unique anchor strings (not line numbers)
3. Replace the complete block, then verify the file still has ALL expected sections
4. Never assume `before = lines[:start_idx]` + `after = lines[end_idx:]` captures the right boundaries when HTML blocks span multiple logical segments

### WIKI_PATH Must Point to docs/ Subdirectory
- If using `docs/` subdirectory for MkDocs, the Hermes `WIKI_PATH` must point there:
  ```yaml
  environment:
    - WIKI_PATH=/llm-wiki/docs    # NOT /llm-wiki
  ```
- Otherwise the Agent won't find entities/, concepts/ etc.

### R2 / Public URL Content-Type for Browser Display
- Markdown files served from R2 with `Content-Type: text/markdown` may show as
  garbled in browsers (browser doesn't recognize the MIME type)
- **Fix**: Use `Content-Type: text/plain; charset=utf-8` for .md files
- Or serve an HTML wrapper (marked.js CDN for client-side rendering, auto dark mode)

### Container-to-Container Communication
- `cloudflared` must be on the same Docker network as `llm-wiki`
- Use container name as hostname (e.g., `http://llm-wiki:8456`)
- Network names get auto-prefixed by Docker Compose with project directory name

### Docker Volume Path Mismatch (Static File Sync Failed Here!)

**Problem**: The Docker bind mount maps `~/llm-wiki:/docs`. Files on the host may exist at multiple paths (symlinks, bind mounts inside the container host). If you copy a static file (e.g., `graph.svg`) to `/llm-wiki/docs/images/` but the Docker container mounts `/home/devtoy/llm-wiki:/docs`, the container won't see the change even though the host file exists.

**Fix — always verify with `docker exec`**:
```bash
# 1. Copy to the ACTUAL Docker-mounted host path
cp graphify-out/graph.svg ~/llm-wiki/docs/images/knowledge-graph.svg

# 2. Verify the container sees the file and check its content
docker exec llm-wiki sh -c 'ls -la /docs/docs/images/knowledge-graph.svg'
docker exec llm-wiki sh -c 'head -c 300 /docs/docs/images/knowledge-graph.svg | grep -o "LXGWWenKai\|WenQuanYi\|DejaVuSans"'

# 3. Only then restart
docker restart llm-wiki
```

**Why this happened**: `~/llm-wiki` resolved differently depending on the shell context (the Hermes container vs the host shell). Always use `docker exec` to triple-check before claiming a static file change took effect.

### Docker Volume Permissions
- Files created by Hermes container may be owned by `hermes` user (not the host user)
- This can cause permission issues when host tools try to modify the same files
- Use `HERMES_UID`/`HERMES_GID` to match the host user's UID/GID

---

## Graphify Knowledge Graph Integration

### Installation

```bash
python3 -m venv scripts/.graphify-venv
scripts/.graphify-venv/bin/pip install graphifyy matplotlib
```

### Build Script Pattern

`scripts/build-graph.py` — collect .md files, extract entities+relations, run Leiden community detection, export to SVG/JSON/Canvas:

```python
#!/usr/bin/env python3
from pathlib import Path
from graphify import extract, build, cluster, export

WIKI_DIR = '/llm-wiki'
OUT_DIR = Path(WIKI_DIR) / 'graphify-out'
paths = list(Path(WIKI_DIR).glob('docs/**/*.md'))
result = extract.extract(paths, parallel=True)
G = build.build([result], root=WIKI_DIR)
clusters = cluster.cluster(G)

# Auto-label communities by most common source file prefix
labels = {}
for cid, members in sorted(clusters.items(), key=lambda x: -len(x[1])):
    src = [m.split('_')[0] for m in members if m.count('_') > 0]
    from collections import Counter
    common = Counter(src).most_common(1)
    labels[cid] = common[0][0] if common else str(cid)

OUT_DIR.mkdir(exist_ok=True)
export.to_json(G, clusters, str(OUT_DIR / 'graph.json'), community_labels=labels)
export.to_svg(G, clusters, str(OUT_DIR / 'graph.svg'), community_labels=labels)
export.to_canvas(G, clusters, str(OUT_DIR / 'graph.canvas'), community_labels=labels)
```

### Auto-Rebuild Cron (daily at 04:00 + copy to MkDocs)

```bash
0 4 * * * cd ~/llm-wiki && \
  scripts/.graphify-venv/bin/python3 scripts/build-graph.py && \
  cp graphify-out/graph.svg docs/images/knowledge-graph.svg && \
  # Bump version number in the page to bust Cloudflare edge cache
  sed -i 's|/images/knowledge-graph.svg?v=[0-9]*|/images/knowledge-graph.svg?v='"$(date +%s)"'|g' \
    docs/concepts/knowledge-graph.md && \
  docker restart llm-wiki >/dev/null 2>&1
```

**⚠️ Cloudflare cache**: Static SVGs are cached at Cloudflare edge nodes. Without a version number (`?v=N`), users behind CF may see stale images for minutes to hours. The `sed` command above auto-bumps the version to the current Unix timestamp on each rebuild.

Note: static files (SVG in `docs/images/`) need a container restart to refresh — `--dirty` mode doesn't pick them up.

### Chinese Font in Matplotlib SVG Output

Graphify's `export.to_svg()` uses Matplotlib's `nx.draw_networkx_labels()`. Matplotlib default font (DejaVuSans) lacks CJK glyphs. Configuring a font requires care:

```python
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = '/path/to/CJK-font.ttf'   # MUST be a standalone .ttf, NOT .ttc
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.sans-serif'] = [prop.get_name()]
plt.rcParams['axes.unicode_minus'] = False
font_manager._load_fontmanager(try_read_cache=False)  # force font cache rebuild

# ⚠️ Font MUST be configured BEFORE calling export.to_svg()!
# export.to_svg() imports matplotlib internally via nx.draw_networkx_labels()
```

**⚠️ TTC (TrueType Collection) fonts — DO NOT USE with Matplotlib**: WenQuanYi Zen Hei (`.ttc`) caused systematic +1 glyph-index offset on this project's Oracle ARM server. Every Chinese character rendered as the wrong glyph. Use standalone `.ttf` fonts instead.

**⚠️ Font cache**: After adding a new font, call `font_manager._load_fontmanager(try_read_cache=False)` to rebuild the font cache. Without this, Matplotlib may not see the newly registered font and falls back to DejaVuSans.

**✅ Known-good font**: [LXGW WenKai](https://github.com/lxgw/LxgwWenKai) — download to `scripts/fonts/WenKai.ttf` and register via `addfont()`.

### Graph Viewer Page (MkDocs Static HTML)

Create `docs/concepts/graph-viewer/index.html` — ECharts-based interactive graph:

```html
<!-- Minimal standalone page — paste whole thing -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>*{margin:0;padding:0}body{background:#0d1117;overflow:hidden}#g{width:100vw;height:100vh}</style>
<div id=g></div>
<script>
fetch("/images/graph-data.json").then(r=>r.json()).then(d=>{
  const C=["#f97316","#8b5cf6","#06b6d4","#10b981","#ef4444","#3b82f6"];
  const cats=Object.entries(d.community_labels||{}).map(([i,n])=>({name:n,itemStyle:{color:C[i%6]}}));
  const nds=d.nodes.map(n=>({id:n.id,name:n.label||n.id,category:n.community||0,symbolSize:22,itemStyle:{color:C[(n.community||0)%6]}}));
  const lks=d.links.map(l=>({source:l.source,target:l.target}));
  const ch=echarts.init(document.getElementById("g"));
  ch.setOption({backgroundColor:"#0d1117",series:[{type:"graph",layout:"force",roam:true,data:nds,links:lks,categories:cats,force:{repulsion:300,edgeLength:100,gravity:0.1},label:{show:true,position:"right",fontSize:10,color:"#8b949e"},lineStyle:{opacity:0.5},emphasis:{focus:"adjacency"}}]});
  window.addEventListener("resize",()=>ch.resize());
});
</script>
```

**Link from knowledge-graph page**: use absolute paths — `/concepts/graph-viewer/` not `graph-viewer/` (which resolves to the wrong path `/concepts/knowledge-graph/graph-viewer/`).

### Adding Lightbox to Knowledge Graph Page

See `references/svg-lightbox.md` for the complete HTML+JS block.

**Pitfall — edit MkDocs pages with raw HTML blocks carefully**: line-based Python string replacement on `.md` files with multi-line HTML content is fragile. Prefer:
1. Replace the exact block by reading the whole file as a string, using a unique anchor line as the match boundary
2. Or write the section from scratch using known-good content boundaries (start before the block, end after it)
3. Verify the file still has all expected sections after the edit

---

## Post-Edit Auto-Verification

**Mandatory step** — the user explicitly requires this after any wiki or graph change involving multiple tool calls. Do not declare a change done without running this check.

After any change to wiki pages or graph scripts, run verification before declaring done. The user expects this after repeated corruption incidents.

```python
import re
errors = []

with open('docs/images/knowledge-graph.svg') as f:
    svg = f.read()
if 'DejaVuSans-' in svg:
    errors.append('SVG uses DejaVuSans (no CJK)')
if not re.search(r'(LXGWWenKai|NotoSansSC|WenQuanYi)-', svg):
    errors.append('No CJK font paths in SVG')

with open('docs/concepts/knowledge-graph.md') as f:
    md = f.read()
for s in ['图谱概览', '社区分类', '可视化文件', '自动分类机制', '查看图谱']:
    if s not in md:
        errors.append(f'Page missing section: {s}')
for f in ['openLightbox()', 'lbZoomIn()', 'lbZoomOut()', 'lbReset()', 'closeLightbox()']:
    if f not in md:
        errors.append(f'Lightbox missing: {f}')

print(f'{"✅ All checks passed" if not errors else "❌ " + str(len(errors)) + " issues:\\n" + "\\n".join(errors)}')
```

--->

## References

- `references/execution-log.md` — Full execution transcript from a real deployment
- `references/r2-content-type.md` — R2 Content-Type handling for browser views
- `references/svg-lightbox.md` — Self-contained lightbox with zoom/pan for SVG/large images in MkDocs pages
- `references/font-debugging.md` — Diagnosing and fixing Matplotlib CJK font rendering (TTC glyph offset, font cache issues, systematic testing approach)

## Verification Script

`scripts/verify-wiki-update.sh` — Run after any wiki update to check:
- SVG contains proper CJK font paths (LXGW WenKai, not DejaVuSans or WenQuanYi TTC)
- Page has all 5 required sections + lightbox components
- Container has actually synced the new SVG (not serving stale cached file)
- Build script font configuration is correct

```bash
# Run from ~/llm-wiki after any change
bash scripts/verify-wiki-update.sh
```
