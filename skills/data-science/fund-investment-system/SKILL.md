---
name: fund-investment-system
description: "个人基金投资辅助系统 — 自动化采集+并行化+自校验+信号归因。涵盖数据采集(A股/外盘/微博)、KOL画像、三推时间线(08:00/11:35/16:00)、节假日处理、评论分析、数据合理性校验、信号准确率追踪。"
version: 3.1.0
author: Hermes (for 赵小杰)
tags: [fund, investment, KOL, cron, automation, self-evolution, sanity-checks, signal-tracking]
---

# 基金投资辅助系统

> 适用于赵小杰的个人基金投资场景：每天三条推送（盘前/午间/收盘），辅助30秒决策。
> 系统文件位于 `/opt/data/scripts/`，定时任务由 Hermes Agent Cron 管理。
>
> ⚠️ 本技能与 `investment-assistant` (productivity) 重叠。后者为更全面的顶层 umbrella skill，包含本技能全部内容 + 更详细的推坑记录。

## 系统架构

### 文件布局

```
/opt/data/scripts/
├── fund_tools.py                 # 核心库：并行采集/自校验/信号追踪/R2存储
├── collect_morning_data.py       # 08:00 预采集脚本 (含sanity check + 信号提取)
├── collect_noon_data.py          # 11:35 预采集脚本 (同)
├── closing_review.py             # 16:00 预采集脚本 (含JSONL归档回退 + 信号解析)
├── collect_weekend_data.py       # 周六09:00 周末外盘速报（no_agent）
├── auto_validate_sources.py      # 周六10:00 数据源可用性验证
│
├── (共享库) r2_uploader.py       # R2存储上传
│
└── kol_analyze_*.py              # 博主画像分析（一次性，历史存档）
```

### 三条推送时间线（2026-06-30: 标题+格式最终定版）

| 时间(CST) | Cron Job 名 | 推送标题 | 脚本 | 类型 |
|-----------|:------------|:---------|------|------|
| 08:00 交易日 | 📊 财经早餐 · 基金参考 | **📊 财经早餐 · 基金参考** | collect_morning_data.py | AI agent |
| 11:35 交易日 | 📈 盘中直击 · 基金速递 | **📈 盘中直击 · 基金速递** | collect_noon_data.py | AI agent |
| 16:00 交易日 | 🌆 收评 · 基金收盘复盘 | **━━━ 🌆 收评 · 基金收盘复盘 · 6/30(上半年收官) ━━━** | closing_review.py | AI agent + **脚本生成表格** |
| 09:00 周六 | 周末外盘速报 | collect_weekend_data.py | no_agent | — |
| 10:00 周六 | 数据源验证 | auto_validate_sources.py | no_agent | — |

### 关键性能指标

| 指标 | 当前值 |
|:-----|:------:|
| 全流程运行耗时 | ~37s (远低于120s cron限制) |
| 基金采集成功率 | 17/18 (94%, timeout=8s) |
| 基金采集耗时 | ~23s (ThreadPool max_workers=5) |
| 大盘预测准确率 | 4/6 (67%, 开vs收方向) |

## 微博采集配置

| 脚本 | 采集条数/博主 | 说明 |
|------|:------------:|------|
| collect_morning_data.py | **15** | 覆盖昨日+今早日均发博量。确保抓住昨日全部帖子 |
| collect_noon_data.py | **15** | 同上 |
| collect_weekend_data.py | 5 | 周末够用 |

**历史问题（2026-06-30 修复）：** 原 `count=3` 导致唐史主任昨日帖子0条被抓到——今日发了3条就占满位置了。必须 count≥15 才能覆盖全量。

## 跨任务预测桥接

```
今日参考(08:00)         收盘复盘(16:00)
  │                        │
  │  ┌──────────────────┐  │
  └──│ _morning_predictions │──┘
     │ .json              │
     │                    │
     │ 今日参考AI生成的    │
     │ 6条开方向预测       │
     └────────────────────┘
```

**工作流：**
1. 今日参考 cron 的 LLM 步骤生成方向预测（6个指数，每个 predicted_direction ↑/↓/→ + reason）
2. LLM 必须执行 `cat > /tmp/fund_data/_morning_predictions.json` 保存结构化数据
3. 收盘复盘 cron 读取该文件，对每条预测比较 predicted_direction vs 收盘涨跌方向

**方向验证规则（2026-06-30 用户纠正）：**
- 比较的是**早盘预测的开盘方向** vs **收盘实际涨跌幅**，不是开方向vs收方向
- 例如：上证指数预测"开方向↓"但收盘+0.50%↑ → ❌（预测跌实际涨）
- 验证的不是"低开高走=开方向错"，而是"预测错了=验证失败"
- 脚本 `_closing_summary.txt` 的 4/6 是"开vs收方向"指标（不同维度）
- AI在推送中展示的"早盘预测验证"必须是基于预测文件，而不是基于脚本的对比

**首次部署注意事项：** 第一个交易日没有预测文件，收盘复盘会跳过验证部分（prompt 有 PASS fallback）。

## 并行采集架构

2026-06-30 从串行改为并行：

| 数据源 | 接口 | 线程池 | 耗时 |
|--------|------|:------:|:----:|
| A股指数(6个) | `get_tencent_quote` | max_workers=4 | ~2s |
| 基金估值(18支) | `get_fund_value` | max_workers=5 | ~23s |
| 外盘(6个) | `_yahoo_quote` | max_workers=4 | ~3s |

**超时优化历程：** 串行(5s, ~10/18) → 并行5并发(5s, 12/18) → 并行5并发(8s, 17/18) → +自动重试1次(**8s+retry, 17/18+回退**)

**三重兜底（2026-06-30）：**
1. `get_fund_value()` 带 `_retry=True`，超时后 sleep(0.5) 重试一次
2. `get_all_funds()` 并行5并发，各基金超时不互相阻塞
3. `closing_review.py` 基金采集后检查：超时的基金用早盘数据回退 (`if code in morning_funds and morning_funds[code]`)

## 推送自检清单（2026-06-30 新增）

用户明确要求推送后Agent必须自我核验。每条推送prompt的最后一个步骤必须是**格式自检**：

1. **表格列对齐** — 列数与模板一致，每行都有数据，不能缺列
2. **数据一致性** — 所有指数涨跌幅与 `_closing_summary.txt` / `_market_summary.txt` 一致
3. **预测来源** — 早盘预测验证列必须从 `_morning_predictions.json` 读取，不能编造
4. **涨跌幅符号** — 带正负号 +/-
5. **禁用词检查** — 月/季/半年末日禁止出现"明日"字样
6. **非交易日过滤** — skip 文件存在时不能编造行情数据
7. **格式回归检查** — 外盘/板块/大盘表格必须用 markdown 表格格式，不能退化为纯文字堆叠

**用户2026-06-30原话：** "你推送后不能就逻辑，数据准确性，格式准确性做自我核验吗，为什么要我发现"

## 特殊日期措辞规则

| 日期 | 含义 | 推演措辞 |
|------|------|---------|
| 6/30 | 上半年收官日 | "下一个交易日（下半年首个交易日）" **不说"明日"** |
| 3/31 | 一季度收官日 | "下一个交易日（二季度首个交易日）" |
| 9/30 | 三季度收官日 | "下一个交易日（四季度首个交易日）" |
| 12/31 | 全年收官日 | "下个交易日（明年首个交易日）" |
| 月末 | 月线收盘 | "下月首个交易日" |

因果：6/30 = 半年末 → 7/1不是普通的"明日"而是重要的时间节点分界线。推演必须体现这个转换视角。

### 数据格式变更 (2026-06-30)

本次会话新增了以下数据格式字段：

| 数据类型 | 新增字段 | 说明 |
|---------|---------|------|
| 板块ETF | `open`, `prev_close` | 板块今开和昨收，摘要文件格式改为 `🔴 板块名: 今开→收盘 (涨跌幅)` |
| 北向资金 | `time` (已有) | 摘要文件加入时间戳：`北向资金(15:00): 沪/深/合计` |
| 基金分组 | 明细行 | 分组摘要加入 `昨收净值→今日估算净值` 明细，方便SPA展示 |

所有改动的原理是：腾讯API原始数据已有这些字段（parts[4]=昨收, parts[5]=今开），之前未提取。时间戳字段同花顺hexin已有。

**更改涉及：** `fund_tools.py::get_sector_quotes()` 返回字典 + 三条预采集脚本的摘要文件写入格式。

### 2026-07-01 新增：操作建议系统 (维度C)

**新增 fund_tools.py 常量和函数：**

| 名称 | 类型 | 用途 |
|:----|:----|:-----|
| `PORTFOLIO_WEIGHTS` | 常量 | 5组持仓权重+目标范围+再平衡触发阈值 |
| `GROUP_ACTION_RULES` | 常量 | 各组的buy/sell触发条件（关键词匹配） |
| `record_group_trend(fund_data)` | 函数 | 收盘写入各组涨跌到 `_group_trends.jsonl` |
| `get_group_trend(name, days=5)` | 函数 | 读取最近N天该组趋势 |
| `check_rebalance(fund_data)` | 函数 | 检测各组权重是否偏离目标范围 |
| `score_group_action(name, quotes, ...)` | 函数 | 多因素评分(-5~+5) → 操作建议 |

**新增输出文件：**

| 推送 | 新文件 | 内容 |
|:----|:-------|:-----|
| 今日参考 | `_operation_plan.txt` | 早盘5组操作计划表 + 再平衡检查 |
| 收盘复盘 | `_operation_eval.txt` | 6列操作评估表 + 趋势速览 + 再平衡检查 |

**评分公式：** 趋势得分(±2) + 板块动量得分(±2) + KOL信号得分(±1) → 综合得分 → 增持(≥+3)/关注(≥+1)/持有(0)/观望(≤-1)/减持(≤-3)

**新文件加入 cron prompt 风险提示：** 三条prompt各自存储，新增 `_operation_plan.txt` 和 `_operation_eval.txt` 必须在当前推送的 prompt 中加 `cat` 命令。见 pitfall #18（已更新）。

## 自校验系统 (维度A)

每条推送自动检查数据合理性，异常时推送开头标注 `⚠️ 本日数据异常：...`。

### 校验范围

| 检查项 | 正常范围 | 写入文件 |
|--------|---------|---------|
| 大盘指数 | 上证2500-4500, 科创50 800-3000 等 | `_sanity_report.json` |
| 板块采集率 | ≥50% | 同上 |
| 涨跌家数 | ≥100家 | 同上 |
| 两市成交额 | 500-50000亿 | 同上 |
| 北向资金 | -200~+200亿 | 同上 |
| 基金采集率 | ≥60% | 同上 |
| KOL博文 | >0条 | 同上 |

### 文件命名规则

- morning → `_sanity_report.json`
- noon → `_noon_sanity.json`
- closing → `_closing_sanity.json`

Cron prompt 必须 cat 对应文件并在 status='⚠️' 时在推送开头追加标注。

## 信号归因系统 (维度B)

追踪KOL预测的历史准确率，自动评估哪些信号源值得保留。

### 数据流

```
morning/noon → extract_signals_from_kols() → store_signals() → signals.jsonl (R2同步)
                                                                       ↓
                                                           closing → resolve_past_signals()
                                                                       ↓
                                                           signals-resolved.jsonl (R2同步)
                                                                       ↓
                                                           generate_signal_report() (周报)
```

### 信号词→方向映射

| 方向 | 信号词 |
|:----:|--------|
| 看涨(bullish) | 右侧, 加仓, 补仓, 接货, 底部, 触底, 反弹, 抄底, 建仓, 吃肉 |
| 看跌(bearish) | 泡沫, 风险, 过热, 警惕, 回调, 出货, 洗盘, 砸盘, 左侧 |

### 板块→指数映射

| 关键词 | 映射到 |
|--------|--------|
| 科技, AI, 半导体 | 科创50 |
| 大盘, A股 | 上证指数 |
| 创业板, 中小盘 | 创业板指 |
| 权重 | 上证50 |
| 黄金 | 黄金ETF市场价 |
| (其他/默认) | 大盘 |

### JSONL归档回退

`closing_review.py` 早盘对比逻辑：优先读 `/tmp/fund_data/_raw_data.json`，如果不存在则从 `fund_system_data/morning-briefs.jsonl` 读取今天的最早日盘记录。确保测试 `/tmp/` 被清也不丢失对比数据。

### 信号解析计时

- `resolve_past_signals()` 查找3-7天前的未解析信号
- 第一份有效数据需**3天后**才产生（需要先积累信号再对比）
- `generate_signal_report()` 需**30天**数据积累才有统计意义

## KOL 画像驱动策略

| 博主 | UID | 角色 | 采集策略 |
|------|-----|------|---------|
| 唐史司马迁 | 2014433131 | ▶ 主力信号源 | 15条+信号词加权 [已验证6/6] |
| 小浣熊1230 | 6114912545 | ⚠ 风险警示源 | 15条风险词侧重 |
| IT精英带你养基 | 5044466342 | ℹ 情绪参考 | 1行情绪参考（已剔除） |
| 莫非是托 | (仅触发式) | ↔ 对立面校验 | 仅触发式调用 |

## 周一/周五特殊处理

- **周一 08:00**：美股数据来自上周五，不得说"隔夜外盘"。用"上周五外盘收盘" + web_search 补充周末大事
- **周五 16:00**：末尾增加"🌙 今晚美股关注"小节

## Pitfalls (fund-investment-system 特有)

1. **不能 `rm -rf /tmp/fund_data/` 在上午和收盘复盘之间** — closing_review.py 的早盘对比依赖 `_raw_data.json` 在 `/tmp/` 中。虽然已有JSONL归档回退，但最好的做法是保持 **/tmp/fund_data/** 在交易日完全不被清理。

2. **信号追踪头3天没有任何输出** — 第一天部署后，3天内都不会有解析结果。用户会问"信号追踪怎么没输出"——需要在部署时告知这个延迟。

3. **三条prompt分别存储** — 在 scheduler DB 中各自独立。新增数据文件/改格式时必须同时更新三条prompt否则某个推送会静默断裂。

4. 周一不得写隔夜 — 即使auto_fix，仍需在prompt中写清楚。

5. **收盘复盘prompt必须强制逐项对比**（用户强调）— 用户反馈只有总分没有具体对比。prompt模板必须显式写出对比表格结构，不能依赖AI自动推断。

6. 收盘复盘板块必须展示今开今收 — 摘要文件已格式化板块名: 今开→收盘(涨跌幅)，prompt模板需包含今开→收盘列。

7. KOL检查不要误报收盘复盘 — run_sanity_checks已改为if kols...else本推送无采集。

8. **方向验证逻辑：预测vs收盘，不是开vs收** — 2026-06-30用户纠正。早盘预测(开方向↑/↓)必须与收盘实际涨跌比较，不是开方向vs收方向。脚本生成的 `_closing_summary.txt` 的4/6是不同指标。

9. **预测文件必须由今日参考AI保存** — `_morning_predictions.json` 不是脚本生成的，是cron的LLM步骤生成的。若该文件不存在，收盘复盘会跳过验证部分。首次部署后第一个交易日没有预测文件。

10. **格式自检是强制步骤，不是可选** — 每个推送prompt必须包含自检步骤。用户曾因未自检直接推送损坏格式而明确不满。

11. **特殊日期措辞** — 6/30不说"明日"，说"下半年首个交易日"。已添加至prompt日期判断步骤。

12. **微博 count=15, 不是3** — 2026-06-30修复。count=3导致昨日帖子0条被抓到。collect_morning_data.py和collect_noon_data.py都需保持count=15。

13. **推送后自检优先于回答用户问题** — 用户对"发现问题->修复->再推送而不核验"的模式不满。自检步骤必须在推送完成前执行。

14. **表格格式回归（2026-06-30复发）** — 修改prompt模板后AI可能在后续推送中退化为纯文字格式。每次修改prompt后必须用 session_search 验证最新推送的格式。用户原话："为什么格式问题又重犯了"。

15. **`cronjob(action='run')` 影响调度** — ad-hoc触发会修改 `last_run_at`，可能导致定时调度跳过一次。测试触发后检查 `next_run_at` 是否正确。不要在交易日 08:00-16:00 之间随意触发可能覆盖生产数据的推送。

16. **KOL检查不要误报收盘复盘** — `run_sanity_checks` 的 KOL 检查已改为 `if kols: ... else: "本推送无采集"`。`closing_review.py` 传 `kol_posts: {}` 不触发警告。如果后续加了KOL采集，需同步更新该检查逻辑。

17. **微博凭证到期处理** — 凭证在 `~/.config/weibo-cli/credential.json`，ALF 标记约30天有效期。KOL功能不需用户操作，但如果微博API报-100（会话过期），需用 `weibo_login_v2.py` 或 `weibo_qr_login.py`（在 `/opt/data/scripts/` 或技能目录下）重新扫码登录。注意 Docker 环境需在宿主机运行。

18. **操作建议系统新文件需加入 cron prompt** — `_operation_plan.txt`（今日参考）和 `_operation_eval.txt`（收盘复盘）由预采集脚本生成后，必须在其对应的 cron prompt 的 Step 2 中加入 `cat` 命令。同 pitfall #3（三条prompt分别存储，改一个不进行）。

19. **趋势数据至少3天才有统计意义** — `score_group_action()` 在无趋势数据时只依赖行情+KOL信号评分，偏保守。前3天操作建议会多出"持有"结果，属正常。

## R2 设计文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **SYSTEM_DESIGN_v3.md** | `fund-system/strategy/SYSTEM_DESIGN_v3.md` | **最新** 系统和自进化设计 |
| TIMING_ANALYSIS_v1.md | `fund-system/strategy/TIMING_ANALYSIS_v1.md` | 推送时间修正 |
| HOLIDAY_HANDLING_v1.md | `fund-system/strategy/HOLIDAY_HANDLING_v1.md` | 节假日处理 |

## 推送格式指南

详见 references/push-format-guide.md — 包含用户明确要求的推送格式规范（逐项对比、板块开收、基金明细、方向验证规则等）。修改 cron prompt 前必须查阅。

> 注：investment-assistant (productivity) 包含本技能全部内容 + 详细推坑记录，是实际的顶层技能。本技能保持独立供快速参考。
