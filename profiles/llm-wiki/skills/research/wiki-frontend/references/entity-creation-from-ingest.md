# Entity Creation from Ingested Content

Session reference: 2026-07-14 — 网络安全等级保护 10 PDFs → 4 entity pages

## Signal: When to Create Entities

The user asked "why are these only in concepts, not entities?" for ingested 等保 standards. The distinction:

- **Concepts**: standards, theories, frameworks (what X is)
- **Entities**: classifications, procedures, organizations, tools (how to use X, who does X)

For learning-oriented content (user: "I find source docs too difficult"), create entities as quick-reference cards.

## Learning Entity Template

Each entity should answer: "What's the one thing I need to know?"

- `entities/标准体系关系图.md` — 11 standards shown as a dependency tree
- `entities/定级速查.md` — 3-step classification lookup
- `entities/测评全流程.md` — end-to-end lifecycle with time estimates
- `entities/机构分级能力.md` — I/II/III tier comparison

## Key patterns

- Use ASCII diagrams in code fences for process flows
- Use comparison tables (not paragraph text) for specifications
- Add "实际场景判断" examples (user said "快速学习")
- Always cross-link back to the concept pages
- Update entities/index.md and root index.md
