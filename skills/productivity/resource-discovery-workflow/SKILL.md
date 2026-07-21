---
name: resource-discovery-workflow
description: "Evaluate new open-source projects / tools / resources against user's goals and decide next steps. Covers multi-session scope management: catalog session vs implementation session."
version: 1.1.0
author: Hermes Agent (from user session)
tags: [discovery, evaluation, research, goals, session-management, decision-making]
---

# Resource Discovery & Evaluation Workflow

Trigger: User drops a GitHub link, tool recommendation, or resource URL and asks for analysis.

## 1. Fetch & Understand

- `web_extract` the repo's README (GitHub pages work well)
- Check the directory structure via GitHub API (`api.github.com/repos/{owner}/{repo}/contents`)
- Look at key files: `main.py`, `requirements.txt`, `Dockerfile`, `config.yaml`, `LICENSE`
- Search for existing reviews/discussions if the README is sparse

## 2. Goal Matrix — Map Against User's Core Objectives

From memory, match the resource against these goals:

| Goal | Signal | Priority |
|------|--------|----------|
| 📱 公众号/小红书/抖音内容创作 | Support for self-media publishing, article generation, image creation | Highest for content tools |
| 💰 信息差套利 | Multi-platform data collection, research, aggregation | High for data tools |
| 📈 基金/ETF跟踪 | A-stock data, fund flow, research reports | High for finance tools |
| 🎓 MEM考研(2026) | Study tools, knowledge management, note-taking | Medium |
| 📊 个人仪表盘/日报 | Cron pipeline, data visualization, push notifications | Medium |
| 🖼️ AI配图 | Image generation capability | High for content tools |

## 3. Deployment Viability Checklist

Check these constraints (user's specific environment):

```yaml
servers:
  oracle_arm:   # 152.70.91.4 (container host)
    cpu: ARM64
    gpu: none
    headless: true
    constraints: [no GPU, no desktop GUI, ARM64 base images only]
  
  oracle_arm2:  # 146.56.146.185 (n8n)
    use: n8n + cloudflared only

constraints:
  docker: preferred but must be ARM64-compatible
  gui: UNSUPPORTED (headless servers) — skip pywebview/pyqt/tkinter
  pywin32: Windows-only, irrelevant
  api_keys: user manages .env themselves, don't touch
```

Verify each dependency against these constraints.

## 4. Session Organization Strategy

Once evaluated, decide where to take each resource:

```
┌─ THIS SESSION (catalog) ─────────────────────┐
│  Record + tag + compare + decide priority     │
│  Save: memory entry (compact), reference file │
└───────────────────────────────────────────────┘
         │
         ▼ choice
┌────────────┴────────────┐
│ Deep-dive needed?       │
├──────────┬──────────────┤
│ YES      │ NO           │
│→ Dedicated session      │→ Note and skip       │
│  (e.g. "公众号管线")     │  (track for later)   │
│→ Install/configure      │                      │
│→ Integrate with stack   │                      │
└─────────────────────────┘
```

## 5. Save Reference Docs to R2 (Persistent Storage)

For resources that are worth keeping for future reference, save a markdown doc to R2's `references/` folder:

```python
# 1. Write local md file
content = f\"\"\"# {name} Reference\n\n> Source: {url}\n> Date: ...\n\n## Summary\n...\n\"\"\"
with open('/tmp/resource-ref.md', 'w') as f:
    f.write(content)

# 2. Upload to R2 references/ folder
import sys; sys.path.insert(0, '/opt/data')
from r2_uploader import R2Uploader
r2 = R2Uploader()
r2.upload_file('/tmp/resource-ref.md', 'references/{slug}.md', content_type='text/markdown')

# 3. The references/ folder in R2 is NEVER touched by backup/cleanup scripts
# (backup_to_r2.py only manages backups/ prefix, RETENTION_DAYS=7)
```

**Rules:**
- `references/` folder is **persistent** — no cleanup script touches it
- Include: summary, architecture, deployment assessment, goal matching, decision
- Keep one doc per resource for easy lookup
- Clean up local temp file after upload

## 6. Decision Framework

| Verdict | Meaning |
|---------|---------|
| 🔴 立刻行动 | Directly matches a core goal, deployable with minor effort |
| 🟡 推荐试用 | Good match but has caveats (ARM issues, missing API keys, etc.) |
| ⚪ 参考借鉴 | Useful ideas/workflows but not directly deployable |
| ❌ 跳过 | Does not match goals, too risky, or worse than existing stack |

## Pitfalls

### Code-level issues to always check
- `pywin32` in requirements — conditional on `sys_platform == "win32"`? If unconditional, it will fail on Linux.
- Desktop GUI frameworks (PyWebView, PyQt, tkinter) — useless on headless servers.
- Dockerfile or docker-compose absent — means manual containerization.
- License restrictions in individual source files (some projects put additional restrictions beyond the root LICENSE).
- API keys hardcoded in config examples — never copy those blindly.

### Data source fragility
- Web scraping (BeautifulSoup) based data sources break when target sites change HTML structure.
- Third-party aggregation APIs can change, rate-limit, or go paid.
- Prefer projects using official platform APIs over scraped data.

### Workflow pattern
- Don't deep-dive every resource in the discovery session — it swells the context and buries earlier findings.
- Record key facts (install method, architecture, dependencies) in this session's memory, implement in a dedicated session.
- Use `session_search` later to find this catalog — give it a distinctive memory tag.
