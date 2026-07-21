---
name: fund-evolution-engine
description: 财经AI系统自我进化引擎 — 预测验证 → 准确率追踪 → Prompt自动优化
---

# 进化引擎 v2

## 核心原则 — 真正发挥LLM能力

**LLM不是美工，是首席分析师。** 这是头号设计原则。

| ❌ v1错误用法（已弃用） | ✅ v2正确用法（当前标准） |
|:------------------------|:--------------------------|
| 250-400字输出限制 | **无限字数**，每份分析800-2500字 |
| 传截断数据`data[:300]` | **传完整数据**给LLM自行判断重点(6000+字符) |
| 单次flat prompt | **多步推理链**：画像→赛道→逐基→风险检查 |
| 无置信度评分 | **每个判断带置信度1-10** |
| 无预测回溯 | **验证昨日预测准确率**后再分析 |
| 没持仓深度 | **自动扫描操作记录文件**构建真实持仓 |
| 没KOL交叉验证 | **引用+验证**KOL今日观点 |
| 孤立分析 | **跨报告上下文**：知道上午/昨天说了什么 |
| 无多日趋势 | **5日指数趋势表** (daily-snapshots.jsonl) |
| 无持仓盈亏 | **实时P&L**：成本/市值/盈亏率 |
| 无市场新闻 | **RSS新闻采集** (30+源，分类标签) |

## 基金推荐覆盖 — 每份报告都必须是"操作建议"

**重大教训：即使只给了decision prompt（14:30）操作建议，用户会问"其他报告为什么没有？"**

默认规则：**所有面向用户的分析报告都必须包含基金级别的操作建议。** 深度可以不同，但不能为零。

| 报告 | 推荐深度 |
|:----|:---------|
| 早报 (09:00) | 关注3支+警惕3支（优先级） |
| 午报 (11:35) | 赛道级方向（偏多/偏空/中性） |
| 收盘 (16:00) | 赛道方向+部分基金（明日方向） |
| **14:30决策** | **全部14支逐基评分表** |
| 周度 (周日) | 调仓方向+仓位幅度 |
| 周末 (周六) | 赛道影响+情景预案 |

**14:30决策评分系统**：必须输出三维度评分表格
```
| 代码 | 简称 | 赛道 | 技术分 | 资金分 | 趋势分 | 总分 | 操作 | 理由 | 置信度 |
```
- 技术分(1-10)：当日涨跌+量价+位置
- 资金分(1-10)：北向+成交额
- 趋势分(1-10)：多日趋势方向
- 总分 = (技术+资金+趋势)/3

## 四维数据 — 每次分析的必备输入

每次LLM分析前，检查4项数据全部就绪：

| 维度 | 数据源 | 采集函数 |
|:----|:-------|:---------|
| **① KOL观点** | `_kol_summary.txt` / `_noon_kol.txt` / `fund_tools.get_user_weibos()` | `get_kol_today()` |
| **② 多日趋势** | `daily-snapshots.jsonl` (5天指数) | `get_multi_day_trend(5)` |
| **③ 持仓盈亏** | `daily-snapshots.jsonl` (成本+市值+盈亏率) | `get_portfolio_pnl()` |
| **④ 市场新闻** | `news_sources.json` → RSS采集(requests+xml) | `get_news_headlines(6-8)` |

## T+1规则的正确理解（用户纠正）

**之前我写错了（已删除）：** "今天卖出明天资金可用" / "份额/资金次日到账" / "1日延迟" — 基金卖出资金不是T+1到账的。

**用户纠正后的正确理解：** T+1基金操作的核心约束是 **按当日收盘净值成交，净值未知**，而不是资金到账时间。

| 正确规则 | 说明 |
|:---------|:------|
| **15:00前下单** | 按**今日收盘净值**成交（净值收盘后公布，下单时不知道确切成交价） |
| **15:00后下单** | 按**下一个交易日**收盘净值成交 |
| **估算净值≠实际净值** | 盘中估算仅供方向参考，实际成交价收盘后才知道 |
| **盲操作** | 知道今天涨了还是跌了，但不知道精确成交价 |
| **资金T+2到账** | 卖出后资金2-3个交易日到账（股票/混合基金），**不是T+1** |
| **份额T+1确认** | 买入后次日能看到确认份额 |

**分析含义不同：** 应该提醒"你现在按估算净值做判断，实际成交价收盘后才出来"而不是"明天才能拿到钱"。

## 持仓生命周期管理（减仓/建仓/清仓/持有）

所有报告都必须包含操作建议，不能只分析不行动：

| 操作 | 适用条件 |
|:----|:---------|
| **建仓（新买入）** | 仅新建仓基金。分批建仓：首仓→观察→确认→补仓 |
| **加仓（追加买入）** | 已有持仓且趋势向上、净值相对低位。给出建议金额 |
| **持有（不动）** | 方向不明或趋势中性。**大部分时间应该持有** |
| **减仓（部分卖出）** | 趋势走坏、需降低风险敞口。给出建议比例（如：减30%持仓） |
| **清仓（全部卖出）** | 累计亏损>15%、赛道逻辑彻底破坏、长期垫底。资金T+2才到账 |

### 止损/止盈纪律（P&L驱动）
```
累计亏损>8%  → 减半仓观察，不能再加仓
累计亏损>15% → 清仓离场（建仓基金除外）
累计亏损>25% → 深套不动，耐心等反弹
浮盈>15%     → 可考虑止盈1/3
```
建仓基金（003096/013403）永远不触发止损卖出。

### 同赛道基金对比与冗余优化
周度复盘应检查：
- 科技/AI的7支是否过多？是否有高重叠度？
- 大摩4支科技基金(014871/017103/011712/020233)表现是否分化？可合并？
- 如有冗余，保留表现最好的2-3支，清仓最差的

**实现**：在 `llm_analysis_v2.py` 的 `build_xxx_data_v2()` 中，以 `━━━ 标题 ━━━` 格式段落附加到数据末尾。LLM自行判断哪些数据重要。

## Prompt约束原则：约束格式，不约束判断（2026-07-21用户纠正）

**关键错误**：我之前在prompt里写了"严禁推荐非持仓基金"，用户正确纠正——如果AI真的发现更好的赛道/基金，有数据支撑，为什么不推荐？

| ❌ 错误（我写的） | ✅ 正确（用户要求） |
|:-----------------|:------------------|
| 严禁推荐非持仓基金 | AI可以有新基金建议，但必须明确标注、给数据理由 |
| 不得推荐列表外的基金 | 对比现有同赛道持仓的优劣，用正确代码 |

**只保留的事实约束（不可变）：**
- 基金代码必须真实，不准编造（LLM胡编代码是已知问题）
- 建仓期基金不能建议卖出
- 新基金建议必须明确标注"📌新基金建议"与现有持仓区分

**放开判断：** 让LLM基于数据自行判断是否应该推荐新基金。如果数据支持（板块走强、现有持仓覆盖不足），应该允许推荐。

## 持仓数据注入原则 — 动态注入，不硬编码（2026-07-21）

**重大教训：不要把持仓描述写在prompt的固定文本里。** 每次加新基金/调仓都要改代码，必然遗漏。

### 正确做法

```python
# ✅ 从FUND_CODES动态读取
from fund_tools import FUND_CODES
from llm_analysis_v2 import BUILDING_FUNDS

portfolio_lines = [f"  {code} {name}" for code, name in FUND_CODES.items()]
portfolio_list = "\n".join(portfolio_lines)

prompt = f"你管理的基金({len(FUND_CODES)}支)：\n{portfolio_list}"
```

### 赛道描述也要动态

```python
# ✅ 用sector_map映射，不要写死"科技7支、黄金1支"
sector_map = {
    '009478':'黄金', '011613':'科技', '024418':'科技',
    ...
}
sector_counts = {}
for code, sec in sector_map.items():
    sector_counts[sec] = sector_counts.get(sec, 0) + 1
sector_summary = "；".join([f"{sec}{n}支" for sec, n in sector_counts.items()])
```

### cron脚本修改后必须全量同步

```bash
cp /opt/data/profiles/investment/scripts/run_xxx.py /opt/data/scripts/run_xxx.py
cp /opt/data/profiles/investment/scripts/run_xxx.py "/opt/data/profiles/investment/home/.hermes/profiles/investment/scripts/run_xxx.py"
```

⚠️ **不要反过来cp**：profile版本是源，/opt/data/scripts/是副本。反向cp会把profile版本冲掉。

### 多脚本硬编码审计清单（2026-07-21）

修改任何cron脚本中的基金数据时，必须检查以下文件是否有硬编码：

| 文件 | 常见硬编码位置 |
|:----|:--------------|
| `profiles/investment/scripts/run_morning.py` | 持仓描述字符串（"科技7支：华夏科创50/半导体材料/大摩4支+沪港深"） |
| `profiles/investment/scripts/run_noon.py` | 持仓列表、prompt推荐约束 |
| `/opt/data/scripts/execute_today_plan.py` | `base`字典、`BUILDING_CODES`、`all_codes`、建仓目标元组、BUILD_THRESHOLDS |
| `/opt/data/scripts/llm_analysis_v2.py` | `CLOSING_PROMPT_V2`步骤3赛道数量、"14支总成本6426元" |
| `/opt/data/scripts/llm_analysis.py` | 旧版prompt（v1已不常用） |

**数据层级（从高到低）：**
1. `fund_tools.FUND_CODES` — 全量基金列表（master）
2. `llm_analysis_v2.BUILDING_FUNDS` — 建仓期基金
3. `seed_portfolio.json` — 系统建立前的历史成本和建仓计划
4. `operations/operation_*.md` — 持续操作记录

目前缺失的数据质量层：
- `_source_availability.jsonl` 中有各数据源实时可用率，但未传给LLM
- `_tag_freshness()` 给每个数据加了新鲜度标记，但LLM看不到
- 当数据源失败/使用缓存数据时，LLM不知道，可能基于错误数据做判断
**待办**：创建 `get_data_quality_report()` 函数，在数据段开头附加数据质量摘要。

## v2多步推理提示词模板

### 决策任务（14:30 — 最关键，含评分系统）
```
Step1: 全市场画像 + 5日趋势定位 + 新闻驱动
Step2: 分赛道多空诊断（含KOL交叉验证）
Step3: 逐基金评分+操作建议 → 14支逐支三维度评分
Step4: 风险检查清单 → 逐项标记✅/❌
```

### 收盘复盘
```
Step1: 市场定性 → Step2: 板块轮动解构
→ Step3: 组合逐基诊断 → Step4: 关键信号识别
→ Step5: 明日推演(3情景+概率+应对)
→ Step6: 明日基金操作方向参考
```

### 早盘（09:00）
```
Step1: 隔夜信号传导链 → Step2: 昨日复盘+预测验证
→ Step3: 今日作战地图(3条主线) → Step4: 风险清单
→ Step5: 今日基金关注优先级(3关注+3警惕+中性)
```

### 午盘（11:35）
```
Step1: 上午走势vs昨日预测 → Step2: 半日轮动
→ Step3: 量价深度分析 → Step4: 午后策略调整
→ Step5: 午后基金操作方向(赛道级)
```

### 周度复盘（周日09:00）
```
Step1: 本周全景叙事 → Step2: 组合归因分析
→ Step3: KOL信号聚合(谁看得准) → Step4: 下周基金调仓(配比+幅度)
```

### 周末外盘（周六01:00）
```
Step1: 全球市场全景(传导链) → Step2: 持仓赛道影响评估
→ Step3: KOL信号聚合 → Step4: 周一开盘策略(3种情景+概率)
```

## review_engine.py — 报告审阅进化（2026-07-21新增）
每日17:00运行的完整审阅循环。扩展了evolution_engine.py的预测验证能力。
核心文件：`/opt/data/scripts/review_engine.py` — 质量审查→预测验证→操作回溯→进化分析→看板生成
看板：`fund-system/reports/dashboard.html`

### ⚠️ review_engine 已知缺陷（2026-07-21）

**缺陷1：报告路径不匹配 → 3/4报告"不存在"**

`review_engine.py` 第101行按日期子目录查找报告，但 `push_report_r2.py` 存扁平前缀名。

| 系统 | 期望路径 | 实际路径 |
|:-----|:---------|:---------|
| review_engine | `reports/2026/07/21/closing.md` | ❌ 不存在 |
| push_report | `reports/closing_2026-07-21.md` | ✅ 实际位置 |

所有4份报告中只有morning能被找到（morning走不同存储路径）。其余3份标记为"报告不存在"。

**影响**：报告审查 → 找不到文件 → 无内容可审查 → 无预测可提取 → 0条验证 → 0%准确率 → 看板无价值。

**缺陷2：两套预测系统不共享数据**

`review_engine.py` 有自己的 `extract_predictions()`（关键词正则匹配：看多/看空/涨/跌），而 `evolution_engine.py` 有自己的 `extract_predictions()`（LLM提取）。两套数据不互通。

review_engine 即使找到报告文件，其正则提取的预测也无法被 evolution_engine 验证，因为准确率数据写进不同的JSONL文件。

**缺陷3：dashboard 无LLM分析深度**

看板只是一个计数器面板（报告通过数/预测准确率/操作信号数），没有LLM分析嵌入。用户质疑其"实质意义"。

如果dashboard需要价值，应考虑：添加LLM本周趋势总结、识别持续预测错误的模式、给出明确的prompt调优建议。当前它只告诉你"准确率0%"但不告诉你"为什么"。

### review_engine 预测验证修复（2026-07-21）

**问题**：`_verify_single_prediction()` 试图将预测文本中的关键词（如"半导体看多"）与 `daily-snapshots.jsonl` 里的指数名称（如"科创50"）做字符串匹配。因板块名与指数名不匹配，所有预测均无法验证 → 准确率恒为0%。

**根因**：`_get_actual_market()` 返回的是指数**点位**（如1718.69），不是涨跌幅百分比。`_verify_single_prediction` 尝试 `float(daily-snapshots.jsonl 中的指数点位)` 做涨跌幅验证，指数点位永远>0，逻辑完全失效。

**修复**：重写 `_get_actual_market()` + `_verify_single_prediction()` 三级匹配：

1. **数据源变更**：从 `daily-snapshots.jsonl`（指数点位，无法换算涨跌幅）改为 `/tmp/fund_data/_closing_sector.txt`（收盘板块涨跌幅，文本已标准化）
2. **新增指数涨跌幅解析**：从 `_closing_tables.md` 收盘行情表正则提取指数名称+涨跌幅%
3. **三级匹配逻辑**：
   ```
   第1级: 预测文本中含指数名 → 对比该指数当日涨跌幅
   第2级: 预测文本中含板块名 → 对比该板块当日涨跌幅（如"半导体看多"→匹配半导体+9.99%）
   第3级: 预测文本含"大盘/市场/整体" → 对比所有指数+板块的平均值
   以上均不匹配 → 标记"无法匹配"，不拉低准确率
   ```
4. **整体方向回退**：全部指数+板块涨跌幅的平均值作为"市场整体方向"
5. **结果**：准确率从 **0% → 42.4%** (36/85)

**预测文本清洗** 修复：`extract_predictions()` 原会把数据表行（含 `|` + `%` + emoji）当作预测提取，这些是数据不是预测语句。2026-07-21 增加表行过滤器：
```python
if '|' in line and '%' in line and re.search(r'[🔴🟢🟡]', line):
    continue  # 跳过数据表行
if re.match(r'^[\d\s.,%🔴🟢🟡📈📉➖|:\—\-]+$', line):
    continue  # 跳过纯数据行
```
提取的有效预测从105条降至85条，质量提升。

### review_engine 的LLM集成判断

当前看板不需要LLM（它只是一个统计面板），但如果要让dashboard产生决策价值，需要加入LLM趋势分析模块。当前状态是"计数器"而非"分析器"。

## R2报告推送架构（2026-07-21）
所有LLM报告改为：QQ Bot短摘要+链接，完整MD+HTML上传R2。
详见 `fund-investment-system/references/r2-report-push-architecture.md`。

## 双阶段生成

`evolution_engine.py` → `full_evolution_cycle()`:
1. 初稿 → 2. AI自审(5维评分) → 3. 评分<7时打磨 → 4. 提取预测并存储

**注意**：自审评分偶尔偏低(2-6/10)，初稿本身质量往往优于评分。如果打磨后质量未提升，直接用初稿。

## 预测验证循环

```
生成分析 → 提取可验证预测 → predictions.jsonl
                                    ↓
交易日10:00 → 验证昨日预测 → QQ推送准确率看板
                                    ↓
准确率≥50条 → Prompt自进化 → 优化提示词
```

## 评估分数解析陷阱（重要）

**永远不要直接读取模型的"总分"输出。** 模型经常输出5维之和(如2+3+4+5+6=20)而不是平均分。

```python
# ✅ 正确：各维度独立解析→取平均
vals = [scores['data_accuracy'], scores['logic'], ...]
total = sum(vals) / len(vals)

# ❌ 错误：从模型输出直接读总分
m = re.search(r'总分=(\d+)', result)  # 模型可能输出20而不是4.0
total = float(m.group(1))  # 这是错的
```

**验证脚本**：`validate_v2.py` 的 `evaluate()` 函数已按正确模式实现。

## HTML生成规范（R2无CORS，禁止fetch）

```python
# ✅ 正确：Python侧转义后内嵌到JS模板字面量
escaped = md.replace('\\', '\\\\').replace('`', '\\`')
html = f'<script>const md = `{escaped}`;</script>'

# ❌ 错误：前端fetch('file.md') → R2无CORS头 → 浏览器拦截 → 白屏
html = '<script>fetch("file.md")...</script>'  # 千万别用
```

**每次上传文档到R2时，必须MD+HTML双版本同时上传。** 已犯3次此错。

## Cron架构

| 项目 | 正确路径 |
|:----|:---------|
| cron执行的脚本 | `profiles/investment/scripts/run_xxx.py` |
| 数据采集+格式化 | `/opt/data/scripts/` |
| LLM分析模块 | `/opt/data/scripts/llm_analysis_v2.py` |
| 输出方式 | **stdout**→cron捕获→QQ Bot（not API自调） |
| API密钥来源 | `profiles/investment/.env` 中的 `DEEPSEEK_API_KEY` |

**常见错误**: 修改了`/opt/data/scripts/run_closing.py`但cron实际执行的是 `profiles/investment/scripts/run_closing.py`。

## `send_closing_cards.py` 已废弃

旧飞书平台遗留文件。正确收盘格式脚本为 `/opt/data/scripts/send_closing.py`。

## 质量验证

```bash
# v2全量验证（7种报告）
DEEPSEEK_API_KEY=xxx /opt/hermes/.venv/bin/python3 /opt/data/scripts/validate_v2.py
# 单轮验证（旧版）
DEEPSEEK_API_KEY=xxx /opt/hermes/.venv/bin/python3 /opt/data/scripts/llm_validate.py {round}
```

上传R2: `fund-system/llm-validation/v2_validation_{date}.html`

## 文件清单

| 文件 | 路径 | 说明 |
|:----|:-----|:------|
| 分析引擎v2 | `/opt/data/scripts/llm_analysis_v2.py` | **主文件** — 7套多步推理提示词+完整数据构建+DeepSeek直连 |
| 分析引擎v1 | `/opt/data/scripts/llm_analysis.py` | 旧版，保留兼容 |
| 进化引擎 | `/opt/data/scripts/evolution_engine.py` | 双阶段生成+预测提取+验证+Prompt自进化 |
| 质量验证 | `/opt/data/scripts/llm_validate.py` | 5维度自评估+MD/JSON/HTML→R2 |
| 每日验证cron | `profiles/investment/scripts/run_evolution_verify.py` | 交易日10:00→QQ推送准确率看板 |
| v2全量验证 | `/opt/data/scripts/validate_v2.py` | 批量测试7种报告+评估+自动报告上传 |
| 审阅引擎 | `/opt/data/scripts/review_engine.py` | 2026-07-21 每日17:00全量审阅循环 |
| 每日审阅cron | `profiles/investment/scripts/run_review.py` | 交易日17:00→QQ推送审阅摘要+看板 |
| R2报告推送 | `/opt/data/scripts/push_report_r2.py` | 2026-07-21 MD/HTML报告生成+R2上传 |
| 新闻源配置 | `/opt/data/scripts/news_sources.json` | 30+RSS源，4赛道(🤖⚡🏛️🥇) |
| 决策脚本 | `/opt/data/scripts/execute_today_plan.py` | 09:35/14:30双时段决策，集成v2 LLM |
| 收盘wrapper | `profiles/investment/scripts/run_closing.py` | cron执行的收盘分析wrapper |
| 早报wrapper | `profiles/investment/scripts/run_morning.py` | cron执行的早报wrapper |
| 午报wrapper | `profiles/investment/scripts/run_noon.py` | cron执行的午报wrapper |
| 周报wrapper | `/opt/data/scripts/weekly_review.py` | 周度复盘（自推QQ） |
| 周末wrapper | `profiles/investment/scripts/run_weekend.py` | 周末外盘速报wrapper |

## 已知陷阱

1. **不设字数限制** — 250/300/400限制了模型深度
2. **不截断数据** — 全量数据传给LLM（6000+字符）
3. **R2无CORS** — HTML必须内嵌markdown，不能用fetch
4. **cron脚本路径** — 编辑 `profiles/investment/scripts/` 下的文件
5. **API密钥** — 从`.env`文件读取，cron上下文无全局env
6. **`send_closing_cards.py`已废弃** — 旧飞书遗留，正确文件是`send_closing.py`
7. **周末外盘** — 旧版硬编码相关系数(纳斯达克×0.4)，v2用LLM动态分析
8. **评估总分解析** — 永远取5维度平均，不读模型的"总分"输出
9. **HTML+MD必须成对** — 每次文档上传不能只传MD（用户反复强调⚠️ 已犯3次）
10. **全量审计** — 修改任何cron脚本时，必须检查全部21条任务，不是只改相关的那几条
11. **基金推荐覆盖** — 所有面向用户的报告都必须含操作建议，不能只做行情分析。14:30决策任务必须输出三维度评分表格
12. **数据质量透明** — LLM应知道所用数据的来源可靠性和新鲜度。`_source_availability.jsonl` + `_tag_freshness()` 未嵌入v2流程，待实现
13. **`patch`工具的`replace_all=True`极危险** — 2026-07-20因`replace_all=True`匹配了28处不该匹配的文本，导致46KB文件严重损坏需完整重建。**`replace_all`必须配合极长的、在文件中唯一的前后文使用**。不确定唯一性时，改用`terminal`执行sed或写Python脚本修复。
14. **T+1规则不要写错** — 核心约束是"按收盘净值成交、净值未知"，不是"资金T+1到账"。资金是T+2到账的。参看上方"T+1规则的正确理解"。
15. **`full_evolution_cycle` 有硬编码 max_tokens** — 原代码 `two_pass_generate` 和 `full_evolution_cycle` 的 draft/polish pass 用硬编码 `max_tokens=1200`，覆盖了调用方的 `max_tok` 参数。2026-07-20修复：给 `full_evolution_cycle` 加 `max_tokens` 参数，传给 `two_pass_generate` 的 `max_out` 参数。`call_deepseek` 的 `max_tokens=1200` 改为 `max_tokens=max_out`。
16. **直接调用 vs 进化引擎** — `full_evolution_cycle()` 做3轮API调用(draft+review+polish)，耗时~50-70s。数据采集已占用~60s时，总时长>120s可能被cron SIGTERM。**对于早报等时效性优先的报告，用 `call_ds()` 直接调用（1轮）代替 `generate_v2()`（进化引擎）**。详见 `fund-decision-verify/references/format-block-cron-timeout-fixes.md`。
17. **`<br>` 标签在QQ Bot不渲染** — 所有推送脚本必须加后处理 `analysis.replace("<br>", "\n")`。否则表格内换行失效。
19. **`format_block` 签名易被子代理破坏** — delegate_task重建文件时，子代理可能把 `format_block(title, content)` 改为 `format_block(text, max_len=500)`。**被改后调用方传参不变** → `text[:内容字符串]` → TypeError。每次delegate_task重建文件后必须检查 `format_block` 签名。
20. **收盘报告max_tokens不足（2026-07-21）** — `generate_v2("closing")` 配置 max_tokens=3500，但6步分析+14支基金+深套/超配约束需要至少5500。步骤6常被截断（底部表格不完整）。2026-07-21修复：`llm_analysis_v2.py` 第841行 `(CLOSING_PROMPT_V2, build_closing_data_v2, 5500)`。

## 参考文件

- `references/v2-design-principles.md` — v2引擎设计原则（多步推理/无限字数/完整数据/持仓感知/四维数据/基金推荐评分/数据质量审计）
- `references/cron-audit.md` — 全量21条定时任务LLM潜力审计

## CDN缓存验证模式（2026-07-21会话反复出现）

每次上传到R2后，必须执行：
1. 用 `curl -s URL | grep 关键数据` 直接验证（不要用web_extract——它有自身缓存层）
2. 检查 `curl -s -D- URL | grep last-modified` 确认是最新版本
3. 如CDN仍缓存旧版，手动 `upload_to_r2()` 强制刷新
4. 查看实际渲染的HTML/MD输出，确认每个字段正确，**不要只看原始数据或日志**

**示例验证脚本**：
```bash
curl -s 'https://hermes-main-media.devtoy.xyz/fund-system/reports/dashboard.html' | grep -c '报告不存在'
curl -s -D- 'https://hermes-main-media.devtoy.xyz/fund-system/reports/closing_2026-07-21.html' | grep -i last-modified
```

## review_engine dashboard输出修复（2026-07-21）

1. **导航链接**：原指向 `evolution.html` 和 `月度归档`（不存在），改为只保留 `dashboard.html` 和 `index.json`
2. **URL重复**：`full_review_cycle()` 内 print dashboard URL + `run_review.py` 也打印 → 重复输出。修复：`full_review_cycle` 不打印URL，由 cron wrapper 统一输出。
3. **消息格式**：cron wrapper（`run_review.py`）的输出必须为纯文本，不用 **bold** markdown，不用 `[链接](url)` markdown前缀。QQ Bot支持emoji但不支持markdown。

本次会话产生的关键改进：
- **v2引擎上线**：完全重写分析层，7种报告全部多步推理+完整数据
- **进化引擎**：双阶段生成+预测提取+准确率追踪+Prompt自进化
- **缺失增补**：KOL深度分析、多日趋势、实时P&L、市场新闻RSS（4维数据检查）
- **基金推荐扩展**：从仅14:30有建议扩展到所有报告都有操作建议，决策任务加三维度评分系统
- **全量审计**：从分析5条扩展到21条全部审计
- **评估分数bug修复**：总分=5维平均，不读模型的"总分"输出
- **用户偏好**：每次上传必须MD+HTML双版本；修改cron脚本必须全量21条检查；所有报告必须含操作建议
