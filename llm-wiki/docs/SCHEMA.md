---
title: LLM Wiki Schema
created: 2026-07-12
updated: 2026-07-12
type: meta
tags: [schema, rules, conventions]
sources: []
---

# LLM Wiki Schema

## 三层架构

- `raw/` —— 不可变的原始材料（PDF、网页文章、转录稿）。只读，绝不修改。
- `concepts/` —— 概念/实体/比较/查询页面。可创建、更新、交叉引用。
- `SCHEMA.md` —— 规则、约定、标签分类法。

## Frontmatter 模板

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: concept | entity | comparison | query | meta
tags: [标签1, 标签2]
sources: [raw/xxx.md, https://...]
---
```

## 标签分类法

### 领域标签
- `finance` — 金融/量化/交易
- `ai-agent` — AI Agent 相关
- `quant` — 量化交易/因子/策略
- `open-source` — 开源项目

### 技术标签
- `architecture` — 架构设计
- `cli` — 命令行工具
- `api` — API 接口
- `mcp` — MCP 协议
- `backtest` — 回测引擎
- `data-source` — 数据源

### 类型标签
- `tutorial` — 教程
- `reference` — 参考手册
- `overview` — 概览
- `comparison` — 对比分析

## 交叉引用规则

- 每页至少 2 个 `[[wikilinks]]`
- 超 200 行拆分
- 矛盾标记 `contested: true`，不静默覆盖

## 文件名规范

- 中文文件名，空格用半角，超过 4 个字用减号连接
- 全小写，无特殊字符
