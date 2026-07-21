---
name: chinese-etf-fund-comparison
title: Chinese ETF / OTC Fund Comparison & Portfolio Advice
category: investment
triggers:
  - User asks "推荐XX基金" / "XXX和YYY哪个好" / "建仓XX板块" / "XX和YY有什么区别"
  - User asks portfolio allocation advice for sector ETFs
  - User asks to compare specific fund codes or sector indices
description: Methodology for comparing Chinese sector ETFs/funds, incorporating KOL signals, verifying claims with live data, and giving ranked recommendations with transparent reasoning.
---

# Chinese ETF / OTC Fund Comparison & Portfolio Advice

## When to use

User asks about:
- "推荐XX板块的ETF，为什么A不是B"
- "现在适合建仓XX吗，买哪个"
- "XX和YY有什么区别"
- Portfolio rebalancing across sectors
- "全量评估持仓优化" / "减仓建仓方案" / "重新评估持仓"
- User provides another model's report/output and asks for independent re-evaluation
- 唐史主任司马迁 / 小浣熊1230 / KOL signal verification for fund choices

> Full portfolio optimization workflow documented in `references/full-portfolio-optimization-workflow.md`

## Data Collection (always collect before answering — NEVER skip to recommendation)

### FUNDAMENTAL RULE (from user correction 2026-07-06):
**ALWAYS pull fund size, manager tenure & performance, and 1-year trend BEFORE making any recommendation.**
The user explicitly said: "为什么总是我质疑你才去做出修改...你为什么不能做到自我分析判定推荐"
The recommendation step is the LAST step, not the FIRST. Data-first, always.
Violation pattern: recommending a fund → user points out scale/performance issues → you then verify → user is frustrated. This pattern is UNACCEPTABLE.

### 1. Fund Size, Manager, and Historical Performance
Before recommending any fund, ALWAYS:
1. Call `get_fund_value(code)` → check `nav`, `estimated_change`, `nav_date`
2. Use `web_search` to find fund size (e.g. search "001551 基金规模 2026")
3. Check manager tenure — for index funds, explain it's the index not the manager
4. Check 1-year performance through web_search or index data
5. Compile ALL alternatives in a side-by-side comparison table BEFORE giving a recommendation
6. If the fund has poor scale or performance, state it honestly: "规模很小/业绩不好是因为指数跌了X%" — don't hide it

### 2. Sector ETF Real-Time Quotes (腾讯行情)
Use `get_tencent_quote(code)` from `fund_tools.py`:

```python
sectors = {'医药ETF(512170)': 'sh512170', '创新药ETF(159992)': 'sz159992', ...}
for name, code in sectors.items():
    q = get_tencent_quote(code)  # returns {price, change_pct, ...}
```

### 2. Fund NAV & Estimated Change
Use `get_fund_value(code)` from `fund_tools.py`:

```python
codes = {'天弘中证医药100C': '001551', ...}
for name, code in codes.items():
    data = get_fund_value(code)  # {code, name, nav, estimated_nav, estimated_change, nav_date}
```

### 3. Index Composition Table
When comparing similar funds (e.g. 医药100 vs 医疗 vs 创新药), explain index composition:

| Fund | Index | Coverage | Style |
|:----|:------|:---------|:------|
| 医药100C | 中证医药100 | 100 stocks: 中药+商业+器械+服务 | 均衡偏防御 |
| 医疗ETF联接 | 中证医疗 | 50 stocks: 器械+服务 | 偏器械 |
| 创新药联接 | 中证创新药 | R&D-biotech heavy, 科创板 | 偏科技成长 |

### 4. KOL Signal Verification
Always verify claims with actual data:
- `get_user_weibos('2014433131')` — 主任's latest posts
- Look for exact quotes about the sector
- If user says "主任说了XXX" and you can't find it, state so honestly

## Comparison Framework

Structure recommendations as a **table**:

| 品种 | 代码 | 跟踪指数 | 成分股 | 风格 | 今日涨跌 | 上日净值 | 估算涨跌 |
|:----|:---:|:--------|:-------|:----|:-------:|:--------:|:--------:|

For each candidate, explain **why THIS one not the others** by 3 axes:
1. **Index difference** — actual constituent breakdown
2. **Performance** — today's real-time + yesterday's estimated NAV change
3. **Defense vs Offense** — is this defensive or growth-oriented?

## Portfolio Context

Always read `PORTFOLIO_WEIGHTS` from `fund_tools.py` before advising new positions:

```python
GROUPS = {...}           # fund-to-group mapping
PORTFOLIO_WEIGHTS = {...}  # weight, target_min, target_max, rebalance_trigger
```

New positions require specifying:
- **Source of funds** — reduce from which existing group(s)?
- **Position sizing** — total % for new directions, split priority
- **Entry rhythm** — phased (1/2 today, fill next week) or wait for pullback

## 主任's Position-Sizing Philosophy

Key principles from actual posts:
- **"流动性是血液"** — never lock up all liquidity
- **"调整持仓到出行不用看的水平"** — reducing frequency, not going all-in
- **"降低下半年收益率预期"** — not an aggressive buying environment
- **"莫偏爱，更勿偏执"** — don't marry positions
- **创新药定位** — 防御品种配置（2026年4月原话）
- **核心主线** = 算力/存储/玻璃基封装/先进封装

Framing for new positions: 零仓位 = can enter light (保有流动性), but don't heavy-buy into trends 主任 isn't backing.

## Common Pitfalls

1. **Fund code mismatch**: Some codes return wrong names. Always verify the `name` field.
2. **NAV vs Real-time**: Previous close NAV vs intraday estimate — don't confuse.
3. **Sector index failure**: Some codes (931152, 399989) may fail. Use ETF codes as fallback.
4. **KOL cache stale**: Call `get_user_weibos()` fresh for today's opinions.
5. **C类 vs A类**: User prefers C-class (7-day redemption-free). Don't recommend A-class.
6. **京东金融 platform**: User trades on 京东金融, not 天天基金/蚂蚁. Check availability.
7. **不要追涨（用户教训）**：板块单日大涨>5%后，等回调-2~3%再入场。用户原话"刚配置就跌了好多天" — 大涨次日大概率回调。
8. **三段时间框分析法**：推荐任何板块前必须完成三阶段数据验证：
   - **全年YTD** — 判断全年主线（如科创50+43%=科技牛市）
   - **近20天** — 判断近期轮动方向（如中证医疗+8.7%=资金流入）
   - **近1年/成立以来** — 判断是否只是短期反弹（如中欧医疗健康C近1年+16.95%≠中证医疗ETF-3.47%）
9. **数据源矛盾时减仓**：KOL说科技见底 + 市场数据显示科技流出 + 板块表现显示科技下跌 → 三个信源方向不一致，正确操作是减仓。组合风控高于方向判断。
10. **`stock_zh_index_daily()` 用法**：`akshare` 的全年历史日K API。date列为`datetime.date`类型，用`date(2026,1,1)`比较而非字符串。指数代码：sh000688(科创50)、sh000300(沪深300)、sz399989(中证医疗)、sz399967(中证半导体)。

11. **⛔ 禁止用行业指数收益替代基金净值（用户最尖锐纠正 2026-07-16）**：判断某支基金"涨/跌多少"时，**必须拉该基金真实单位净值**（`akshare.fund_open_fund_info_em(symbol=code, indicator='单位净值走势')`，用 `date(2026,1,1)` 至今首末值算 YTD），**绝不能**用"中证XX指数-25%"之类的行业指数涨跌幅代替。实测案例：024418 华夏半导体材料设备ETF联接C，前版误用"中证半导体指数-25%"当成基金收益，判定"今年最弱、被011613包含"→ 实际该基金今年 **+101%**（涨最多），且与宽基011613(+35%)非包含关系。用指数代推基金 = 张冠李戴，用户明确不接受。

12. **🔍 发布前必须做全量事实核查（用户纠正 2026-07-16）**：报告若经多轮增量修改，必须**回头用原始数据源重算每个数字**再发布，不能信任报告自身。本会话增量修改曾引入错误：长鑫"8次"(实为7条/按提及微博条数)、中石油"4次"(实为2条)。核查方法：基金净值用 `fund_open_fund_info_em` 重拉全部重算；微博频次用开放词库对原始141条JSON重跑 `text.count()`。每条数字都要能对回原始数据。

13. **📄 R2 报告 HTML 必须用语义化表格 + 配色，且 charset 不能忘（用户反复纠正 2026-07-16/20）**：基金净值/减持方案/建仓策略/配置结构等**一律用 markdown 表格**（不用代码块 ``` 展示数据），且上传的 HTML 必须用本 skill 的 `templates/r2_report_html.html`（斑马纹表格、圆角阴影、A股红涨绿跌自动配色 `td.pos`/`td.neg`、移动端适配）。流程：写好 `.md` → 复制 `templates/r2_report_html.html` 为同名 `.html`（HTML内 `fetch('xxx.md')` 自动 fetch 渲染）→ 用 `r2_uploader.py` 同时 upload `.md` 和 `.html`。代码块(```)只用于微博原文引用、脚本片段等真代码。  
    **⚠️ charset 老问题**：MD 必须用 `content_type='text/markdown; charset=utf-8'`，HTML 必须用 `content_type='text/html; charset=utf-8'`。少一个 `charset=utf-8` 浏览器就乱码。用户说\"这老问题了，你怎么又犯了\" — 必须每次检查 content_type 字符串是否完整。

14. 模型纪律：用户当前 session 模型为 tencent/hy3:free（OpenRouter）。分析全程用此模型，不得切换模型，也不要声称切换到某模型做分析。若输出出现无意义的乱码段落，那是生成错误，重新组织语言即可，不是模型切换。

15. QDII/港股基金代码极易混淆（2026-07-16 新增/用户纠正）：港股恒生科技/互联网类基金代码与A股基金不同（QDII前缀），且同一主题有多个基金公司的C类产品。写进报告前必须用 get_fund_value(code) 确认 name 字段与实际推荐标的一致。
    - 依赖记忆或猜测写代码的教训：022398=大成添鑫债券C，曾被误认为恒生科技基金
    - 正确做法：先枚举候选 013403(华夏)/014439(博时)/018578(摩根) 均为恒生科技C类
    - 拉各家的YTD/近1M/最新净值/规模对比后再推荐

16. 同一主题多选一的比较方法（2026-07-16 新增）：当推荐一个板块/主题的基金（如恒生科技、医药100、半导体材料设备）时，必须展示全部C类候选再给结论，不能只写一个推荐而不说明不选其他。
    - 先枚举该主题所有可能的C类基金代码
    - 拉各家的YTD/近1M/最新净值/规模对比表
    - 如果YTD差异小（跟踪同一指数），以规模+流动性+QDII额度为决胜标准
    - 每一行候选都要有数据，最后注明推荐优先级

17. 绝不使用其他模型报告中的数字（2026-07-16 新增）：当用户提供另一个模型/系统的输出报告（HTML/MD/链接）要求重新评估时：
    - ✅ 只提取报告结构（几大部分、决策框架、分析维度）
    - ❌ **绝不提取其中的任何数字**（净值、涨跌幅、收益率、成本）
    - ❌ **绝不把另一个模型的数据作为自己分析的输入**
    - 即使对方的数字看起来合理，也必须自己重拉原始数据全部重算
    - 原因：另一模型可能用错误数据源（如用中证半导体-19%代推基金+101%）、缓存过期、预设白名单遗漏赛道

16. **📐 全量优化报告的骨架要求**：用户要求"内容翔实、理论充分"的持仓优化方案时，必须包含以下10个模块（详见 `references/full-portfolio-optimization-workflow.md`）：
    - 持仓全景 → YTD表现 → 重叠分析 → 主任微博 → 板块环境 → 减仓方案 → 建仓方案 → 配置结构 → 执行计划 → 情景推演
    - 每一条建议必须有 **数据 + 策略 + 理论** 三重支撑
    - 报告文件必须同时上传MD和同名HTML（自适应前端，fetch MD渲染）

18. **📈 建议必须基于多日趋势而非单日涨跌（2026-07-20 新增）**：用户纠正了"只根据当日涨跌给建议"的问题。每个基金的操作建议必须参考：
    - 近3日逐日涨跌 + 合计 → 判断短期动量
    - YTD/近1月/近3月 → 判断中期趋势
    - 科创50近3日/5日趋势 → 判断大盘环境
    - 同时展示"今日最强3支/最弱3支"让用户感知分化
    - 最终判定要结合大盘状态：急跌(-3%以下)不操作、反弹(+2%以上)可减仓、震荡按计划执行

19. **📚 策略理论必须嵌入每条建议（2026-07-20 新增）**：用户要求"决策要有原因、具体依据、策略理论"。每条操作建议的格式应为：
    ```
    ① 代码 基金名 | 操作(金额)
       依据: 具体数据（YTD/1M/3M/规模/重叠度）
       策略: 某策略理论的具体定义
    ```
    策略理论库从用户认可的框架中提取，至少包含：金字塔建仓、止盈防回撤、同质化减仓、大跌观望、反弹减仓、流动性为王、云厂对冲、趋势跟踪、业绩避雷、各美其美。

20. **📂 必须先读实际持仓数据（trade_decisions.jsonl），绝不估算（2026-07-20 用户最重要纠正）**：所有涉及当前持仓金额/占比的分析，必须先读 /opt/data/fund_system_data/trade_decisions.jsonl，该文件每行JSON含 date、holdings（各基金代码 cost成本）。用 json.loads 解析每行，cost 为精确持仓金额。同时用 AKShare fund_open_fund_info_em 拉取最新净值计算时值。必须双字段展示：成本(历史买入) + 今年YTD(最新涨跌)，不能只展示估算金额。

    交叉检查：对比 trade_decisions.jsonl 记录的基金代码列表与用户描述（如12支基金/6,000元），确认是否完全覆盖。实际记录可能多于用户记忆（实测发现14支，含用户已持有的黄金009478/资源163302/恒生科技013403/电网设备025857等易遗漏方向）。

21. **⛔ 不推荐数据证据不足的建仓方向（2026-07-20 用户质疑）**：推荐任何新方向前必须同时检查：

    | 检查项 | 不合格标准 → 不推荐 |
    |:-------|:------------------|
    | YTD 涨幅 | <5%（基本持平，无正向动量） |
    | 近1月涨幅 | 下跌 >5%（负向动量） |
    | 主任141条微博提及 | 0次（KOL不关注该方向） |
    | 同主题对比 | 没有同类标的明显更好 |

    如果>2个维度不合格，必须明确说不建仓。实测：021345卫星(YTD+2% 1m-1.1% 主任0次)、020075机器人(YTD+0.2% 1m-9.6% 主任0次)均不通过。如果有已持有且方向成熟的标的（黄金/资源/医药），优先加仓已有方向而非新增弱的。

22. **🔄 已持有的分散方向优先级高于新增（2026-07-20 实测教训）**：用户已有黄金(009478 中银上海金ETF联接C, 成本439元/6.8%)、资源(163302 大摩资源优选LOF, 214元/3.3%)、恒生科技(013403 华夏恒生科技QDII C, 150元/2.3%)、电网设备(025857 华夏电网设备C, 127元/2%)。分析减持释放的资金怎么用时，必须首先检查是否加仓这些已持有方向，而不是完全无视它们推荐全新的卫星/机器人。读取 trade_decisions.jsonl 画出真实结构后再给建议。

23. **📊 1m/1w/3m 涨跌幅计算方法：必须用最新净值日期前推法（2026-07-20 用户纠正）**：计算基金的近1月/近1周/近3月涨跌幅时，**禁止使用固定参考日期**（如 `rows >= date(2026,6,15)` 然后取首末比较）。正确方法：

    ```python
    from datetime import datetime, timedelta
    
    rows = [(date, nav) for date, nav in ...]  # 所有历史净值
    last = rows[-1]  # 最新净值日期
    
    # 前推法：从最新日期往前推 N 天，找最近的数据点
    for days, label in [(7, '1w'), (30, '1m'), (90, '3m')]:
        cutoff = last[0] - timedelta(days=days)
        closest = min(rows, key=lambda r: abs(r[0] - cutoff))
        change = (last[1] / closest[1] - 1) * 100
    ```

    **为什么固定日期法会严重失真**（实测教训）：用 `rows >= date(2026,6,15)` 取起点时，如果基金在6/15→6/30大幅上涨、7/1→7/17暴跌（先涨后崩），固定起点刚好捕捉到上涨前低点和下跌后低点 → 涨跌抵消 → 1m被显示为-1.8%，但实际1周已跌了-16%。前推法直接从最新日期(7/17)前推30天找到6/17 → 正确显示1m=-6.4%。

    应用范围：此方法适用于 `fund_open_fund_info_em(..., indicator='单位净值走势')` 返回的每日净值序列。AKShare 返回的 `净值日期` 列为 `datetime.date` 类型，可直接做减法。最新日期可通过 `df.iloc[-1]` 获取。
