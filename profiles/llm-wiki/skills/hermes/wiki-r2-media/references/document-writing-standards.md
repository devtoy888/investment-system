# Wiki Document Writing Standards

Every wiki page created or edited by the Agent MUST follow these standards.

## Frontmatter (SCHEMA.md)

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [分类标签]
sources: [来源文件路径]
---
```

## Content Requirements

| Requirement | Detail |
|------------|--------|
| **YAML frontmatter** | title, created, updated, type, tags, sources — all required |
| **Official references** | Link to original documentation, repos, or sources |
| **Executable commands** | Show actual `bash` commands user can copy-paste, not descriptions |
| **Problem/Solution table** | Every issue documented: Problem | Root cause | Solution | Verification | Status |
| **Verification** | After each solution, show the command that confirms it works |
| **Code blocks** | Use `` ```bash `` / `` ```yaml `` / `` ```python `` with proper language tags |
| **Tables** | For any structured comparison, use markdown tables |
| **No shallow content** | Minimum 3+ meaningful sections per document |
| **Alt text on images** | `![描述](URL)` — never empty alt text |

## Minimum Sections for Setup/Ops Docs

1. Architecture overview (with table)
2. Step-by-step execution (with commands)
3. Problem record (what went wrong, how it was fixed)
4. Reference links
5. Verification / path cheat-sheet

## What to Avoid

- Pure prose without code blocks
- Commands that aren't verified to work
- Missing frontmatter (SCHEMA violation)
- "It works" without showing how to verify
