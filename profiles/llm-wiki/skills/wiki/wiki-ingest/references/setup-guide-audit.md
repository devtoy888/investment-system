# Setup-Guide Audit Reference

Detailed methodology from the 2026-07-14 comprehensive update session.

## Section-by-Section Checklist

### Frontmatter
```
updated: YYYY-MM-DD  ← set to current date
tags:                ← append new categories (mkdocs, youtube, wikilink)
sources:             ← add every reference doc consulted since last update
```

### 相关文档 table
Add new rows for:
- Medium articles explaining the approach
- Hermes Agent official docs
- Plugins (obsidian-bridge, roamlinks, graphifyy)
- Any tool or service that was consulted

### MkDocs config section (四)
Replace the old `mkdocs.yml` sample with the **actual current config** from the running system. Key changes to look for:
- `pymdownx.magiclink` added
- `obsidian-bridge` plugin (not roamlinks)
- Full `nav:` with all sections (实体, 概念, 对比, 查询, 源文件)
- `extra_javascript` entries for ECharts
- `validation:` for link warnings
- `language: zh`

### Cron section (八)
Replace the simple two-row table with the current real crontab. Look for:
- MkDocs restart (15 min)
- Git auto-push (03:00)
- Graph rebuild (04:00)
- Lint check (05:00)

### Agent Skills section (九)
Replace the old one-skill table with current inventory. Each skill needs a brief description.

### Path table (十)
Add newly created scripts: build-graph, enrich-graph, rebuild-graph, trigger-rebuild, lint, youtube-ingest.

### Problem Records (十一)
Append new issues, don't replace old ones. Each new issue gets a sequential number.

### Graphify section (十三)
This accumulates duplicate content over time. Look for:
- Repeated "安装" sub-sections (appear both at 13.1 and 13.x)
- Duplicate "测试验证" sections (can appear 2-3 times with same content)
- Duplicate "Agent 创建文件注意事项" (same content with minor wording differences)
- Duplicate font-download code blocks
- **Fix**: Keep only the FIRST occurrence of each sub-section, delete the rest

### New sections for new features
Add after the Graphify section:
- 十四: YouTube multi-modal ingestion
- 十五: Auto lint health check
- 十六: Version history and reference design comparison

### Reference design conformance table (十六)
Compare Karpathy's original design against current implementation row by row:
- raw/, entities/, concepts/, comparisons/, queries/
- index.md, log.md, SCHEMA.md
- [[wikilinks]] cross-references
- Graph visualization
- Multi-platform access

### 图谱关联 section
Convert old markdown links `[text](/path/)` to `[[path|text]]` format. Graphify auto-generates this section on rebuild.
