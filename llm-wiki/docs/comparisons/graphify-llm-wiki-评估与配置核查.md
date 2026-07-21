---
title: Graphify 在 LLM Wiki 的落地评估与配置核查
created: 2026-07-19
updated: 2026-07-19
type: comparison
tags: [graphify, knowledge-graph, evaluation, wiki-audit]
sources:
  - https://pypi.org/project/graphifyy/
  - https://graphify.net/
  - https://medium.com/@jsong_49820/from-scattered-notes-to-a-living-knowledge-graph-building-llm-wiki-graphify-01b4f031471a
  - https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base
  - https://wiki.devtoy.xyz/concepts/graph-viewer/
---

# Graphify 在 LLM Wiki 的落地评估与配置核查

> 本文回答三个问题：(1) LLM Wiki 是否达到参考文章（Jsong / Kunal）的设计需求；(2) 网站易用性/美观性/实用性是否达业内要求、是否充分利用 Graphify；(3) 为何配合 ECharts、Graphify 自身是否无数据展示功能。所有结论均经实地核查（容器内产物、在线渲染、JSON 字段）交叉验证。

## 一、事实核查（已实地验证）

### 1.1 真实运行位置与状态
- **真实源路径**：宿主机 `/home/devtoy/llm-wiki` → 容器内 `/llm-wiki`（`/dev/sda1` 挂载）。真实脚本在 `/llm-wiki/scripts/`。
- **`build-graph.py`** 存在：`/llm-wiki/scripts/build-graph.py`，每天 cron 自动重建（graph.json 时间戳 2026-07-19）。
- **产物齐全**：`graphify-out/graph.json`（716KB）、`graph.svg`（3MB）、`graph.canvas`、`obsidian/`、`extraction.json`、`graph.html`。
- **在线图谱正常**：`concepts/graph-viewer/` 用 iframe 嵌入 `docs/graph-html/graph.html`（Graphify 原生 vis-network 交互图）。

### 1.2 Graphify 自带可视化能力（关键澄清）
- Graphify **自带交互式可视化**：输出 `graph.html`（基于 vis-network 力导向，**点击节点 / 缩放 / 筛选 / 搜索 / 信息面板**），以及 `graph.svg`（静态）、`graph.json`（全量数据）。
- 即 Graphify **本身就有数据展示功能**，并非"只能导出数据、必须靠 ECharts 才能看"。
- 你的 wiki **此前用 ECharts 渲染**（`graph-viewer.v2.js` + `graph-query.v3.js`），这是**之前模型推荐的选型**，非你主动要求，也非 Graphify 必须。现已弃用。

### 1.3 graph.json 字段（决定能力边界）
实测 790 节点 / 1053 边（enrich 后：893 EXTRACTED + 160 INFERRED）：
- 节点含：`label / community / community_name / source_file / url` 等。
- 边含：`relation / confidence(EXTRACTED|INFERRED) / confidence_score / source_location(L行号)`。
- **置信标签全覆盖**：`confidence` 边全覆盖，`relation` 全覆盖（如 `references`）。

## 二、是否达到参考文章设计需求

### 2.1 Jsong《LLM Wiki + Graphify》设计清单 vs 你的实现
| Jsong 设计要求 | 你的实现 | 达标 |
|---|---|---|
| 三/多层架构（raw→entities/concepts→index） | ✅ 完整三层 + SCHEMA | 达标 |
| Graphify 集成（自动社区发现） | ✅ Leiden，每天重建 | 达标 |
| 交互式图谱浏览器 | ✅ Graphify 原生 graph.html（拖拽/缩放/搜索/跳页） | 达标（已切原生） |
| God Nodes / 社区着色 | ✅ community_name + 配色 | 达标 |
| **每页底部注入 "Related (from Graphify)" 段落**（含 EXTRACTED/INFERRED + 社区） | ✅ 已实现：related-pages v20 全站注入"📊 图谱关联"段 + 中文徽章 | 达标（已落地） |
| 边按置信度着色（绿=EXTRACTED/黄=INFERRED） | ✅ Graphify 原生 hover tooltip 显示 EXTRACTED/INFERRED | 达标（原生提供） |
| 节点点击跳 wiki 页 | ✅ 文件级跳页（后处理注入，浏览器实测 200） | 达标（文件级） |

### 2.2 Kunal《LLM Wiki 实操》设计要求 vs 你的实现
| Kunal 要求 | 你的实现 | 达标 |
|---|---|---|
| 目录级 index 解决 >200 文件上下文爆炸 | ✅ `index.md` + 分类目录 | 达标 |
| 矛盾检测（contradiction-checking） | ✅ 已落地 `scripts/contradiction-check.py` 静态检查门禁 | 达标（已落地） |
| 增量更新"只改受影响页" | ⚠️ Graphify 全量重建（非增量）；wiki lint 覆盖部分 | 部分 |
| 公网可访问展示层 | ✅ MkDocs + CF Tunnel + 独立域名 | 达标（领先多数实践者） |

**结论 1**：架构层（三层 + 自动图谱 + 公网展示）**已达甚至超过**参考设计；交互浏览也已达标（切到 Graphify 原生后既满足又零维护）。原两处可选优化（每页 Related 注入、矛盾检测）**均已实施**。

## 三、易用性 / 美观性 / 实用性评估

### 3.1 优点（达业内要求）
- 美观：MkDocs Material 主题 + 明暗模式 + 响应式，达静态知识库主流水平。
- 易用：标签导航 + 搜索 + 目录 + 图谱入口，结构清晰。
- 实用：Atlas 式互联（wikilinks + 自动图谱 + 每页关联段落）领先 Karpathy 原帖（仅本地 Obsidian）。

### 3.2 切换 Graphify 原生后的改进
- 消除 ECharts 冗余依赖（之前模型推荐、非你要），零维护。
- 获得原生搜索框、NODE INFO 面板、社区过滤器、置信度 tooltip——能力反超原 ECharts 页。
- 节点点击闭环跳 wiki 页，图谱与正文打通。
- 每页自动"📊 图谱关联"段，阅读流内即可发现关联。

## 四、为何配合 ECharts？Graphify 自身能否替代？

### 4.1 直接回答
- **Graphify 自身有可视化能力**（graph.html，vis-network 交互图），**并非无数据展示功能**。
- 你用 ECharts 是**之前模型推荐**，非 Graphify 必须，也非你主动选型。
- **替代结论（已实施）**：改用 Graphify 原生 graph.html 完全满足需求，且更好（搜索/置信度 tooltip/零维护/每页关联）。保留 ECharts 的唯一优势"与 MkDocs 主题像素统一"被评估为不重要（图谱页独立深色主题可接受）。

### 4.2 节点跳页粒度评估
- **文件级跳页**（跳对应 md 页）：已实现并验证。依据信息觅食理论——用户点节点意图是"看该概念文档全貌"，到页内用 TOC 定位章节，符合心智模型；且只依赖 `source_file`，稳定不脆弱。
- **heading 级精确锚点跳转**：评估为**不需要**。理由：① MkDocs 锚点依赖 slug、Graphify 节点无结构化锚点字段（仅行号，编辑后偏移易断）；② 文件级+页内 TOC 已覆盖定位需求；③ 边际收益仅省一次 TOC 点击，成本却是提取层改造+slug 规则耦合。故维持文件级。

## 五、配置错位问题（已修复）

### 5.1 现状与修复
- **原问题**：Graphify skill 错误放在 `profiles/investment/skills/`（graphify-wiki / wiki-knowledge-graph）；实际运行在 llm-wiki profile。二者分离。
- **修复（2026-07-19）**：已将两份 skill 复制到 `profiles/llm-wiki/skills/hermes/`，内部路径均指向 `/llm-wiki`（校验一致）；investment 副本已移除，消除歧义。

## 六、行动清单（执行状态：2026-07-19 全部完成）

| 优先级 | 项 | 状态 |
|---|---|---|
| P0 | 迁移 Graphify skill 到 llm-wiki profile | ✅ 已复制到 `profiles/llm-wiki/skills/hermes/`，路径校验一致；investment 副本已移除 |
| P1 | 弃用 ECharts，改用 Graphify 原生 graph.html | ✅ 已完成。`build-graph.py` 加 `export.to_html()`；移除 `graph-viewer.v2.js`/`graph-query.v3.js`；mkdocs.yml 引用清理 |
| P1 | 节点点击跳 wiki 页（文件级） | ✅ 后处理注入 `network.on('click')`；浏览器实测跳转 `/setup-guide/` 等真实 200 |
| P1 | confidence 着色/tooltip | ✅ Graphify 原生提供（hover 显示 EXTRACTED/INFERRED），自动获得 |
| P2 | 每页注入 "Related (from Graphify)" 段落 | ✅ related-pages v20：无 h2 页自动创建"📊 图谱关联"段 + EXTRACTED/INFERRED 中文徽章；全站覆盖（概念/实体/首页/中文子目录/YouTube源页实测通过） |
| P2 | 摄入流程加矛盾检测 | ✅ 已落地 `scripts/contradiction-check.py`：6 类静态检查；0 ERROR 通过，48 WARN 为已知 schema 缺口；固化进 wiki-ingest Step 3b |

### 已实施验证（科学交叉验证，非注水）

1. **构建验证**：`build-graph.py` 跑通，graph.html 生成（740KB，790 节点），跳页脚本注入到第一个 `<script>` 块（变量 `network`/`nodesDS` 可见）。
2. **静态验证**：节点对象含 `_source_file` 字段；映射 `setup-guide.md → /setup-guide/` 正确；注入位置在第一个 script 块内。
3. **在线渲染验证**（浏览器真实加载）：Graphify 原生 UI 完整呈现——搜索框、NODE INFO 面板、82 个 COMMUNITIES 过滤器；vis-network canvas 渲染正常。
4. **跳页端到端验证**：`network.emit('click',{nodes:['setup_guide']})` 触发 handler → `window.open('/setup-guide/')` 被调用，URL 正确。
5. **回归验证**：knowledge-graph / concepts / setup-guide 页均 200；ECharts JS 已 404（移除成功）；docker restart 后生效。
6. **数据一致性交叉验证**：graph.json（790 节点/1053 边）= graph.html（RAW_NODES 790）一致。

### 结论
Graphify 原生 graph.html **完全替代 ECharts**，且额外获得搜索、置信度 tooltip、零维护、每页关联段落；节点文件级跳 wiki 页已验证可用。heading 级精确锚点跳转经评估**不必要**（文件级+页内 TOC 已覆盖，且避免行号/slug 脆弱耦合），维持文件级。

## 七、相关页面
- [[setup-guide]] — 当前部署与 Graphify 集成方案
- [[concepts/knowledge-graph]] — 知识图谱架构
- [[concepts/graph-viewer]] — 交互式图谱浏览器
- [[comparisons/展示框架评估-mkdocs-material-eol与替代方案]] — 展示框架评估

## 八、P2 专项实施与验证（2026-07-19）

### 8.1 每页图谱关联段落（related-pages v20）
**修复的真实问题（科学验证暴露）**：
1. **INFERRED 边全缺失**：`enrich-graph.py` 原逻辑导致 820 条边全为 EXTRACTED（同目录推断被 `existing` 提前阻断）。修复后 **893 EXTRACTED + 160 INFERRED = 1053 边**，推断维度补全。
2. **无 h2 页不注入**：实体页/hermes-agent 等无 `## 图谱关联` 段 → JS 直接 return。v20 加"自动创建段"逻辑，全站覆盖。
3. **中文子目录页 0 关联**：`resolveCurrentFile` 用 `window.location.pathname` 未解码（CF 返回编码 URL `%E6%A6%82%E8%BF%B0`），与 PAGE_URLS 中文不匹配。v20 加 `decodeURIComponent`。
4. **stem 匹配失败**：子目录页 currentFile=stem（`概述`）但 f2id 索引用完整 source_file。v20 加 `stem2ids` 映射。
5. **CF 缓存旧 JS**：v20 文件名新但 CF 缓存旧响应。mkdocs.yml 引用加 `?v=2` 强制回源。

**全量多角度浏览器验证（通过）**：
| 页面类型 | 示例 | 关联数 | 徽章 | 状态 |
|---|---|---|---|---|
| 概念页（有 h2） | 6dim-analysis-framework | 7 | EXTRACTED/INFERRED | 通过 |
| 实体页（无 h2） | hermes-agent | 9 | EXTRACTED | 通过（自动创建段） |
| 首页（INDEX_URLS） | / | 多项 | 混合 | 通过 |
| 中文子目录页 | 网络安全等级保护/概述 | 10 | EXTRACTED/INFERRED | 通过（修复后） |
| YouTube 源页（无 h2） | hermes-agent-masterclass-overview | 10 | 混合 | 通过 |

控制台错误：0。

### 8.2 矛盾检测（contradiction-check.py）
- 纯静态、零依赖（PyYAML）、可全量重复跑。
- 检查项：frontmatter 必填字段、日期逻辑(created<=updated)、重复 title、contested 无说明、source_file 误填、工具版本漂移。
- 结果：**0 ERROR / 48 WARN**（WARN 集中在 raw/ 源页、index 页缺 `sources`，属已知 schema 缺口，非真矛盾）。
- 已固化进 `wiki-ingest` Step 3b 作为摄入质量门禁。

### 8.3 Skill 固化
- `wiki-knowledge-graph` SKILL：修正 ECharts 过时描述，加入 graph.html 原生图、矛盾检测、enrich INFERRED 说明、related-pages `?v=` CF 缓存协议。
- `wiki-ingest` SKILL：Step 3 加 build-graph.py 原生图说明，新增 Step 3b 矛盾检测门禁，Pitfalls 验证项改为 Graphify 原生图 + 全站关联段落。
