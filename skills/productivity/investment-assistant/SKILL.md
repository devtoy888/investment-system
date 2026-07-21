---
name: investment-assistant
description: 个人投资决策辅助系统 — 市场数据采集(腾讯/天天基金) + 持仓跟踪 + 量价分析 + KOL信号(微博) + AI分析/解读 + 加仓信号监控 + 每日参考推送(早/午/收) + 收盘验证 + 数据归档(JSONL+R2) + SPA查阅页面。整合 cron-content-pipeline + china-market-data + weibo-monitor 三大skill。
tags: [fund, stock, portfolio, daily-briefing, weibo, A-share, data-collection]
---

# Investment Assistant — 个人投资决策辅助系统

Build a complete personal investment decision support system that collects market data, tracks portfolio funds, monitors KOL signals, generates daily briefings with AI analysis, verifies predictions at close, and archives everything for review.

## Architecture

```
                        ┌─ Retry Queue ──┐
                        │ 9:00→9:10      │
                        └──────┬─────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               Data Collection (pre-script)                  │
│  Tencent quotes + Fund values + Weibo KOL posts + AI black │
│  talk interpretation → summary files to /tmp/fund_data/    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Agent formats      │
                    │   morning brief      │
                    │   (reads summaries)  │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
    ┌────────┐          ┌──────────┐          ┌──────────┐
    │ Push to│          │ JSONL to │          │ Images   │
    │ QQ/WX  │          │ R2       │          │ to R2    │
    └────────┘          └─────┬────┘          └──────────┘
                              │
                              ▼
                      ┌──────────────┐
                      │ SPA Dashboard│
                      │ (R2 static)  │
                      └──────────────┘
```

## When to Activate

- User wants daily market/fund briefing automated
- User holds a portfolio of funds (ETF connections, active funds)
- User follows KOLs on Weibo for investment signals
- User wants predictions verified (closing review vs morning forecast)
- User needs a dashboard/history for manual review
- Keywords: 基金, ETF, 持仓, 今日参考, 盘前简报, 收盘复盘, 投资辅助, 个人理财, 定投, 波段

## Strategy Framework (3-Push Design)

Designed around a proven financial framework: the investment bank morning meeting 3-Box model (Goldman Sachs / Morgan Stanley standard structure).

### Core Decision Chain

The three pushes form a single decision loop:

```
08:00 → "What's my plan today?"      (set thesis)
11:35 → "Is the thesis holding?"     (verify in real-time)
15:30 → "Was the thesis right?"      (close loop, learn)
```

### Theoretical Foundations

| Framework | Source | Application |
|-----------|--------|-------------|
| 3-Box Morning Meeting | GS/MS standard | Push content structure (overnight → impact → action) |
| Factor Momentum + Sector Rotation | Jegadeesh & Titman (1993) | What data to track (sector flows, factor exposure) |
| Behavioral Finance | Kahneman (2011) | Why closing review exists (confirmation bias countermeasure) |
| Portfolio Rebalancing | Standard | When to suggest position adjustment (% deviation trigger) |
| Data Saturation Sampling | Guest et al. (2006) | KOL profile methodology (when is enough data enough) |

### Push Naming Convention (2026-06-30/07-01)

| Slot | Cron Job Name | Push Title Header | Schedule (CST) |
|:----|:--------------|:-----------------|:--------------:|
| 早 | 📊 财经早餐 · 基金参考 | **📊 财经早餐 · 基金参考 · M月D日(周X)** | **08:30** (30 0 * * 1-5 UTC) |
| 午 | 📈 盘中直击 · 基金速递 | **📈 盘中直击 · 基金速递 · M月D日(周X)** | 11:35 (35 3 * * 1-5 UTC) |
| 晚 | 🌆 收评 · 基金收盘复盘 | **━━━ 🌆 收评 · 基金收盘复盘 · M月D日(特殊日期) ━━━** | 16:00 (0 8 * * 1-5 UTC) |

### The Push Schedule (US/A-Share Time-Gap Aware)

**推送时间（2026-07-01 更新：早报改为08:30 CST=00:30 UTC）**

### Time Zone Foundation (EDT summer, China = UTC+8)

```
US market:  09:30 ET = 21:30 CST  →  16:00 ET = 04:00 CST (+1 day)
A50 night:  17:00-05:15 CST (+1 day)
```

### Key Timing Issues

The US market closes at **04:00 CST** — 4 hours before the 08:00 push. This works **Tue–Fri** but creates problems around the weekend:

| Day | Issue | Severity |
|-----|-------|:--------:|
| **Mon 08:00** | "隔夜外盘" is from Friday (stale by ~76h). Must not use the word 隔夜. | 🔴 Critical |
| **Fri 16:00** | A-share closed but US opens at 21:30 CST tonight — missing forward guidance. | 🟡 Medium |
| **Sat ~04:00** | Friday US close data arrives but no push collects it. Wasted until Monday. | 🟡 Medium |

### Full Push Schedule

| Beijing | Push Name | Days | Purpose | Content Focus |
|---------|-----------|:----:|---------|---------------|
| 08:00 (00:00 UTC) | 盘前简报 | Mon-Fri | Set daily thesis | **Tue-Fri:** Overnight US/gold/A50 (~4h fresh). **Mon:** Weekend events + Friday US close (marked as stale, NOT called "隔夜"). Supplement with web_search for weekend news. |
| 11:35 (03:35 UTC) | 盘中速递 | Mon-Fri | Verify + adjust | Morning session recap + portfolio estimate + new KOL signals + afternoon outlook |
| 15:30/16:00 (07:30/08:00 UTC) | 收盘复盘 | Mon-Fri | Close loop | Closing data + prediction accuracy. **Fri edition:** append 🌙 section "今晚美股关注" — preview US market tonight. |
| | **09:00 (01:00 UTC)** | **周末外盘速报** | **Sat only** | Weekend analysis | **v2 script:** Yahoo 6-symbol data + portfolio impact mapping + sparkline group trends + KOL signal direction + week-over-week comparison. See `references/weekend-push.md`. |

### Monday-Specific Rules

When the cron runs on Monday 08:00 (which is the first push after Friday 16:00):

1. **Do NOT write "隔夜外盘"** — the US market last traded ~76 hours ago. Write "🌙 上周五外盘关盘". (Script handles this automatically via `is_monday` flag.)
2. **Do NOT write "A股昨收"** — write "📈 上周五A股收盘". (Script handles this automatically.)
3. **Do NOT write "持仓基金（昨日行情参考）"** — write "💰 **持仓基金（上周五行情参考）**". (Script handles this automatically.)
4. **Do NOT pretend the data is fresh** — add a note like "周末无交易，以上为上周五收盘数据".
5. **Supplement with web_search for weekend events** — policy changes, geopolitics, commodity moves. Include a "📰 周末大事" section before all other content. (Cron prompt instructs LLM to do this on Monday.)
6. **KOL posts from the weekend** (Mon 08:00) are valuable — they may have posted Sat/Sun about Monday's outlook. Prioritize these over stale market data.

### Push Test Timing Rule (2026-07-06)

When the user asks for a push test or manual trigger, choose the push that matches the **current Beijing time period**:

| Time (CST) | Push to Test | Reason |
|-----------|:-------------|:-------|
| 09:00–11:30 (morning session) | 早报 (财经早餐) | Pre-market data + overnight analysis |
| 11:30–13:00 (lunch break) | 盘中直击 | Morning session just closed, data fresh |
| 13:00–15:30 (afternoon session) | 盘中直击 or wait | Mid-afternoon; if too close to close, wait |
| 15:30–17:00 (post-close) | 收盘复盘 | Market just closed |
| Weekends | 周末外盘速报 | Weekend reference |

**Rule:** Never push 收盘复盘 during morning trading (data incomplete), never push 早报 in afternoon (data stale). Follow the user's exact phrasing: "现在正在上午开盘中，你就推送早报".

### Saturday AM Push Design (v2)

**Purpose:** Weekend reference card with data + auto-analysis. No AI commentary — pure script-generated content.

**Cron config:** `0 1 * * 6` (UTC) = 09:00 CST Saturday
**Type:** `no_agent=true`, script at `/opt/data/scripts/collect_weekend_data.py`

**Sections (v2, 2026-07-04):**

| # | Section | Purpose | Format |
|---|---------|---------|--------|
| 1 | 🌙 外盘收盘 | Yahoo 6 symbols (DJI/SPX/IXIC/gold/USD/HSI) | Emoji list |
| 2 | 📊 持仓影响评估 | Auto-maps overseas data → portfolio groups via threshold rules | Text analysis |
| 3 | 📈 一周回顾 | Week-over-week overseas comparison (markdown table) | **Markdown table** |
| 4 | 📊 分组本周趋势 | 5-day trend with Unicode sparkline `▁▂▃▄▅▆▇█` | **Markdown table** |
| 5 | 📰 博主信号 | KOL latest post + signal direction + black talk | Structured text |
| 6 | 📌 周一关注 | Data-driven outlook (based on gold/nasdaq thresholds) | Bullet list |

**CRITICAL formatting rules for no_agent scripts:**
- Trend data MUST use Unicode sparkline bars (`▁▂▃▄▅▆▇█`), NOT raw `date=value → date=value` pairs
- Week-over-week comparisons use markdown tables (品种/上周/本周/变化)
- Impact assessment marks: 🔴=利好/偏多, 🟢=利空/承压, 🟡=中性

**Implementation pattern (`collect_weekend_data.py`):**
```python
# Unicode sparkline from float list
spark_chars = ['▁','▂','▃','▄','▅','▆','▇','█']
rng = max(vals) - min(vals)
spark = ''.join(spark_chars[min(int((v - min(vals)) / rng * 7), 7)] for v in vals)
# Output: ▁▂▇▇█ for upward trend, ▇▆▁▁█ for sharp drop+recovery
```

See `references/weekend-push.md` for full reference documentation.

### Friday Evening US Market Preview (added to 16:00 收盘复盘)

Append a section when the cron runs on Friday:

```
🌙 今晚美股关注
● 21:30 美股开盘（关注科技股/黄金/美元走势）
● 若有大幅波动，周末将推送外盘速报
```

## Integration with Existing Skills

| Component | Backend Skill | Purpose |
|-----------|--------------|---------|
| Data collection | `china-market-data` | Tencent quotes + fund values |
| Weibo signals | `weibo-monitor` | KOL posts + auth + black talk |
| Cron scheduling | `cron-content-pipeline` | Pre-script + agent pattern |
| Data storage | `cloudflare-r2` | JSONL archive + HTML site |

## Data Collection Library (fund_tools.py)

Create a single Python module (`scripts/fund_tools.py`) that provides all data collection functions and R2 storage. Structure:

```
fund_tools.py
├── get_tencent_quote(code)        → dict (name/price/change_pct/pe/pb)
├── get_all_quotes()               → dict of all tracked indices/ETFs
├── get_fund_value(fund_code)      → dict (nav/estimated_nav/estimated_change)
├── get_all_funds()                → dict of all held fund codes
├── get_overnight_quotes()         → dict of US/gold/USD/HK closing data
├── get_sector_quotes()            → 10 industry ETF batch via Tencent
├── get_market_overview()          → 涨跌家数 + 两市成交额
├── get_northbound_flow()          → 北向资金实时净流入 (hexin API, auto-retry)
├── get_user_weibos(uid, count=5)  → list of recent weibo posts
├── get_weibo_comments(post_id)    → comment scraping (signal-triggered only)
├── interpret_weibo(text, author)  → black talk keyword interpretation
├── group_funds(fund_data)         → group by theme (科技/黄金/其他)
├── store_jsonl(record, filename)  → append to local + sync to R2
├── upload_to_r2(file, key)        → upload to Cloudflare R2
├── is_trading_day()               → check weekday + holiday set
├── track_source(name, success)    → per-source availability logging
├── record_group_trend(fund_data)  → 每日收盘记录各组涨跌趋势到 _group_trends.jsonl
├── get_group_trend(name, days=5)  → 读取最近N天某组涨跌幅 [(date, pct), ...]
├── check_rebalance(fund_data)     → 检查各组是否偏离目标权重区间
├── score_group_action(name, quotes, sectors, kol_signals, trends) → -5~+5评分+操作建议
├── get_volume_analysis(quotes, sectors, prev_total_turnover) → 量价分析dict（振幅、量价信号、总信号）
├── grade_market_sentiment(rise, fall, limit_up, limit_down) → "普涨 🔴"/"偏强 🔴"/"中性 🟡"/"偏弱 🟢"/"冰点 🟢"（5档机械分档，涨跌家数比例阈值，2026-07-06 新增）
    **Thresholds:** rise_ratio ≥ 0.70 → 普涨 🔴; ≥ 0.55 → 偏强 🔴; ≥ 0.45 → 中性 🟡; ≥ 0.30 → 偏弱 🟢; else → 冰点 🟢. Uses `rise/(rise+fall+flat)` ratio. Adds active火 count (limit_up+limit_down > 50 → 🔥, >100 → 🔥🔥).
├── get_short_term_sentiment(overview) → "📊 大盘情绪: 偏强 (涨跌比2.6:1 涨停45) \n💰 成交额: 3182亿\n📈 涨停45家 跌停5家"（统一输出三行情绪摘要，2026-07-06 新增）
    **Data source:** `get_market_overview()` returns rise_count(f169), fall_count(f170), flat_count(f171), limit_up(f167), limit_down(f168) from East Money push2 API. On Oracle ARM, push2 has ~90% failure rate; data falls back to `_yesterday_snapshot.json` snapshot when live API fails. Sentiment grading still works from snapshot data but uses yesterday's counts.
├── get_short_term_sentiment(overview) → "📊 大盘情绪: 偏强 (涨跌比2.6:1 涨停45) \n💰 成交额: 3182亿\n📈 涨停45家 跌停5家"（统一输出三行情绪摘要，2026-07-06 新增）
├── PORTFOLIO_WEIGHTS              → 各组权重估算+目标上下限+再平衡触发阈值
├── GROUP_ACTION_RULES             → 各组买卖触发条件（buy_triggers/sell_triggers）
└── FUND_CODES / GROUPS / KOLS / QUOTES / SECTOR_ETFS / OVERNIGHT_SYMBOLS → constants
```

### Fund portfolio classification (current as of 2026-06-26)

Group funds by theme, not individually. Each group should have a unified action signal.

**CRITICAL: Fund codes from screenshots are unreliable (~50% error rate).** Always verify every fund code via the 天天基金 API before trusting it.

**Current portfolio (2026-07-06, 15 funds, 5 groups):**

| Group | Count | Codes | Signal |
|-------|:----:|-------|-------|
| 科技/AI | 7 | 011613, 024418, 026449, 014871, 020233, 017103, 011712 | Tech/AI sector trend |
| 黄金 | 2 | 002963, 009478 | Gold price direction |
| 资源/周期 | 2 | 163302, 025857 | Resource cycle exposure |
| 新能源 | 2 | 012329, 011103 | New energy + solar |
| 医药 | 2 | 001551, 014565 | Medical/pharma defensive |

**Notes:**
- 2026-07-06: 新增 天弘中证医药100C(001551) 240元 + 天弘中证创新药产业ETF联接C(014565) 120元 → 15支5组
- 2026-07-06: GROUPS dict 清理旧代码(去掉已清仓的026421/026200/013403/024913和通航组)

**Notes:**
- 2026-06-30: 清仓 易方达恒生港股通创新药ETF联接C (024329) → 18→17
- 2026-07-02: 清仓 华夏恒生科技ETF联接QDII(013403) + 大摩港股通多元成长混合C(026200) + 大摩ESG量化混合C(026421) + 华夏国证通航ETF联接C(024913) → 17→13，删除通航分组。移除 growps/PORTFOLIO_WEIGHTS/GROUP_ACTION_RULES 中的通航。
- 2026-07-06: GROUPS dict 清理旧代码(去掉已清仓的026421/026200/013403/024913和通航组)。新增医药组和维度D(量价分析)+维度E(全量监控)。

**When user asks about adding funds based on KOL signals, see:**
`references/fund-addition-analysis.md` — 5-step decision framework including KOL mood assessment, sector data check, portfolio overlap, and tiered priority output.
\n**Update 2026-06-30:** 清仓 易方达恒生港股通创新药ETF联接C (024329), 已从 FUND_CODES 移除。\n\n**Update 2026-07-06:**\n- 用户选择方案B：天弘中证医药100C(001551) 240元(4%) + 天弘中证创新药产业ETF联接C(014565) 120元(2%)，总6%。下午14:40确认趋势后执行。\n- 唐史主任将创新药定位为**"防御品种"**（2026年4月原话），而非进攻主线。

Tencent quote codes for key indices:
- 上证指数: sh000001
- 创业板指: sz399006
- 科创50: sh000688
- 沪深300: sh000300
- 黄金ETF: sz159934

## Reference Files

- `scripts/collect_morning_data.py` — Pre-collection script (runs before agent as cron's `script` parameter). Available at `/opt/data/scripts/` on this host.
- `scripts/fund_tools.py` — Reusable data collection library. Available at `/opt/data/scripts/` on this host.
- `scripts/closing_review.py` — Closing review data collection. Available at `/opt/data/scripts/` on this host.
- `scripts/kol_expand_phase2.py` — KOL data collection with pagination. Available at `/opt/data/scripts/` on this host.
- `scripts/news_sources.json` — 2026-07-06 赛道 RSS 新闻源配置（30源×4赛道），由 `fetch_rss_news()` 读取。
- `references/rss-news.md` — 2026-07-06 RSS 赛道新闻系统文档。
- `references/kol-analysis.md` — KOL profile analysis findings (227+80+80 posts analyzed).
- `references/kol-following-analysis.md` — 唐史主任's following list analysis (negative finding).
- Strategy document on R2: `fund-system/strategy/STRATEGY_v1.md`
- Strategy v2 on R2: `fund-system/strategy/STRATEGY_v2.md`
- Accuracy report on R2: `fund-system/strategy/KOL_ACCURACY_REPORT_v1.md`
- Black talk analysis on R2: `fund-system/data/kol_blacktalk_analysis.json`
- KOL profile data on R2: `fund-system/data/kol_profiles/final_profiles.json`
- Friday evening US market preview (added to closing review 2026-06-26): `references/timing-analysis.md`
- Holiday calendar (CHINESE_HOLIDAYS_2026 + auto-scrape 2026-06-26): `references/holiday-handling.md`
- Saturday weekend overseas push (no_agent script 2026-06-26): `references/weekend-push.md`
- Cron job configuration (deployed 2026-06-26): `references/cron-config.md`
- Data source API endpoints discovered 2026-06-30: `references/data-sources-2026-06-30.md`
- `references/monitor-report-format.md` — 2026-07-06 全量监控报告格式规范：逐基详情6维度每行一条、表格列数限制、关键信号数据完整性规则。
- `references/self-evolution.md` — 2026-06-30 self-evolution framework: data sanity checks (维度A) + signal tracking (维度B).
- `references/stale-skip-file-fix.md` — 2026-07-06 stale skip file bug: root cause, fix, detection steps.
- `references/report-format-rules.md` — 2026-07-06 report format optimization: tables must preserve ALL content dimensions; never trim detail for formatting.
- `scripts/sparkline.py` — Reusable Unicode sparkline generator (`sparkline_8pt()`, `sparkline_with_summary()`). For trend visualization in text-only channels (QQ/微信). Available under this skill's scripts/ directory.
- `scripts/monitor_buy_signals.py` — 2026-07-06 加仓信号监控脚本(no_agent模式)。每日16:30 CST运行(cron 7ea6086a7749)，监控四支基金(大摩数字C/光伏C/新能源C/电网C)的买入条件。无信号静默，有信号推送。
- `references/volume-analysis-methodology.md` — 2026-07-06 量价分析系统文档：信号分类规则、函数API、三推送集成、已知限制。
- `references/market-sentiment-sources.md` — 2026-07-06 市场情绪系统设计文档：5档机械分档阈值 + 涨停/跌停数据源 + Oracle ARM API可达性说明。
- `references/vibe-research-20260706.md` — 2026-07-06 Vibe-Research 仓库评估：可提取的3个模块（短线情绪/市场情绪分档/赛道RSS）和不fork的理由。
- `references/fund-addition-analysis-20260706.md` — 2026-07-06 基金追加分析：医药/创新药/机器人/军工实时数据对比 + 主任信号 + 操作记录。
- `references/operation-recommendations.md` — 2026-07-01 操作建议系统设计 (维度C): 评分规则+文件格式+pitfalls.
- `fund_system_data/_group_trends.jsonl` — 2026-07-01 新增，每日收盘写入各组涨跌幅，供操作建议系统(N日趋势评分)。
- `references/extra-sessions-20260702.md` — 2026-07-02 额外QQ会话处理记录（Enhancing Stock Data / Missing Structures 两个session的ID、内容摘要、删除方式）。

## Operation Recommendation Output Files (2026-07-01 新增)

每天两个新输出文件由预采集脚本自动生成：

**08:00 今日参考 → `_operation_plan.txt`**
- 格式：markdown 表格（组别/方向/建议/理由）
- 由 `collect_morning_data.py` 第9节生成
- 内容：5组操作计划 + 再平衡检查
- AI 用法：`cat /tmp/fund_data/_operation_plan.txt` 直接输出到推送中的 📋 **今日操作参考** 板块

**16:00 收盘复盘 → `_operation_eval.txt`**
- 格式：6列 markdown 表格（组别/信号/今日建议/收盘表现/评估/明日方向）
- 由 `closing_review.py` 第13节生成
- 内容：操作评估 + 趋势速览 + 再平衡检查
- AI 用法：`cat /tmp/fund_data/_operation_eval.txt` 直接输出到推送中的 📋 **操作评估** 板块

**趋势数据持久化：** `fund_system_data/_group_trends.jsonl` 由 `record_group_trend()` 在收盘时写入，每日一行，随 R2 自动归档。

## Overseas Market Data (Yahoo Finance)

Added to fund_tools.py (2026-06-26): `get_overnight_quotes()` function.

**Verifiable symbols** (confirmed working via Yahoo Finance API):

| Market | Symbol | URL Encoding |
|--------|--------|-------------|
| Dow Jones | `^DJI` | `%5EDJI` |
| S&P 500 | `^GSPC` | `%5EGSPC` |
| Nasdaq | `^IXIC` | `%5EIXIC` |
| Gold Futures | `GC=F` | `GC%3DF` |
| US Dollar Index | `DX-Y.NYB` | `DX-Y.NYB` |

**Failed attempts** (do not retry): A50 futures via Yahoo Finance (symbol `XIN9.F`, `FTXIN9`, `CN` all returned non-futures data).

```python
# Usage:
from scripts.fund_tools import get_overnight_quotes
quotes = get_overnight_quotes()
# Returns: {'道琼斯': {'price': 51920.62, 'change_pct': 0.14}, ...}
# Note: Yahoo's regularMarketPrice is LATEST (not necessarily yesterday close).
# For 08:00 Beijing = ~20:00 ET = US market closed, so latest = yesterday close. ✓
```

## 加仓信号监控系统 (Buy Signal Monitoring)

2026-07-06 新增：用户要求对四支弱势持仓基金设置自动化加仓提醒。

### 架构

no_agent 模式 cron，静默监控。无信号时不输出任何内容→不推送；有信号时输出提醒文字→推送。

### 配置

- **Cron Job ID:** `7ea6086a7749`
- **脚本:** `scripts/monitor_buy_signals.py`
- **运行时间:** 交易日 16:30 CST (30 8 * * 1-5 UTC)
- **模式:** `no_agent=True` — 不消耗LLM token，脚本直接输出

### 触发条件细则

| 基金 | 代码 | 触发条件 | 等级 | 信号类型 |
|:----|:----|:--------|:---:|:--------:|
| 大摩数字经济C | 017103 | 翻红 AND 半导体ETF<1%（独立走强） | 🔥 强 | 资金回流 |
| 大摩数字经济C | 017103 | 日涨>+0.5% | 📈 中 | 短期企稳 |
| 天弘光伏C | 011103 | ETF涨>2% AND 振幅>3%（放量反弹） | 🔥 强 | 趋势反转 |
| 天弘光伏C | 011103 | 翻红>+0.5% | 📈 中 | 短期反弹 |
| 天弘光伏C | 011103 | ETF跌至0.75 | ⚠️ 止损 | 减仓预警 |
| 天弘新能源增强C | 012329 | 涨>1.5% AND 振幅>2%（放量反弹） | 🔥 强 | 趋势反转 |
| 天弘新能源增强C | 012329 | 翻红>+0.5% | 📈 中 | 短期反弹 |
| 电网设备联接C | 025857 | 振幅<2% AND -0.3%~+1.0%（缩量止跌） | ✅ 强 | 回调企稳 |
| 电网设备联接C | 025857 | ETF回1.95以上 | 📈 中 | 企稳回升 |

### 注意事项

- 目前**不自动执行买入**——只提醒，用户决定是否操作
- 光伏止损线0.75来自用户7/6的对话约定（再跌7%触发减半建议）
- 大摩数字C的"独立走强"条件基于半导体ETF走势——数字方向需要走出自己的行情，不跟半导体才算真的企稳

### Future improvements

- 条件可扩展为连续N天触发才推送（减少噪音）
- 可以加入趋势数据（连续3日翻红）作为第二层确认
- 可以考虑自动计算买入金额（基于PORTFOLIO_WEIGHTS的偏离度）

## Pre-Script + Agent Cron Pattern

Use the cron-content-pipeline Pre-Script Data Collection pattern:

### Pre-script (collect_morning_data.py)

```python
# What it does:
# 1. Check if today is a trading day (skip if not)
# 2. Collect market data, fund values, weibo KOL posts
# 3. AI-interpret KOL posts for black talk (画像驱动的过滤)
# 4. Group funds by theme
# 5. Check for new sector opportunities
# 6. Write summary files to /tmp/fund_data/_*.txt
# 7. Save raw data JSON to JSONL + R2 for archival
```

### Skip File Protocol (for non-trading days)

Each pre-collection script writes a skip file when `is_trading_day()` returns False. The cron prompt MUST check for this file in the very first step — otherwise the AI agent will push stale/empty data on holidays.

| Script | Skip File |
|--------|-----------|
| `collect_morning_data.py` | `/tmp/fund_data/_skip.txt` |
| `collect_noon_data.py` | `/tmp/fund_data/_noon_skip.txt` |
| `closing_review.py` | `/tmp/fund_data/_closing_skip.txt` |

Prompt template for Step 1:
```
## 第一步：检查是否交易日
如果 `/tmp/fund_data/_skip.txt` 存在，说明今天不是A股交易日。输出"⏭️ 今日休市，无推送"并结束（不要发送任何其他内容）。
```

**Why this matters:** Before this pattern was added (2026-06-26), `closing_review.py` exited on holidays but wrote NO skip file — the AI agent would find no data files, then hallucinate a report based on empty input. Every pre-script + agent cron pair must implement this protocol.

Use the 3-Box model for the 08:00 push:

```
数据已由 collect_morning_data.py 预采集到 /tmp/fund_data/。

步骤1：读取数据
  cat /tmp/fund_data/_market_summary.txt
  cat /tmp/fund_data/_group_summary.txt
  cat /tmp/fund_data/_fund_summary.txt
  cat /tmp/fund_data/_overnight_summary.txt
  cat /tmp/fund_data/_sector_summary.txt
  cat /tmp/fund_data/_market_overview_summary.txt
  cat /tmp/fund_data/_northbound_summary.txt
  cat /tmp/fund_data/_kol_summary.txt

步骤2：格式化成盘前简报
用上述数据按此模板写中文盘前简报：
━━ 今日参考 · 日期 ━
🌙 隔夜外盘（Box 1）
📊 昨收A股（Box 1）
💰 持仓分组（Box 2）
📰 博主信号（Box 2 - 画像驱动）
🚀 新赛道关注（Box 2 - 可选）
📌 今日建议（Box 3）

步骤3：deliver="origin" 回到对话来源
```

## 唐史主任 6/6 准确性验证证据链

Each claim was independently verified via web search against external news sources.

| # | 他的原话 | 日期 | 验证方法 | 结果 |
|:-:|---------|:----:|---------|:----:|
| 1 | 「美光的业绩出来了，全超，所有指标都超」 | 6/25 | 搜「美光2026Q3 营收」确认414.6亿美元(+346%), 毛利率84.9% | ✅ |
| 2 | 「两市昨天成交3.76万亿」 | 6/23 | 搜「A股 6月22日 成交额 3.76万亿」确认历史第二 | ✅ 精确到数字 |
| 3 | 「科创综指创业板指等都新高」 | 6/23 | 搜「科创50 6月24日 历史新高」确认1989.43点(+3.82%) | ✅ |
| 4 | 「棒子那是去掉一些杠杆……国内的存储今天还是涨的」 + 「昨天白天是韩国熔断」 | 6/23-6/24 | 搜「韩国股市 6月23日 熔断」确认KOSPI跌8.11% | ✅ |
| 5 | 「指数已经基本完成本次回踩」 | 6/16 | 搜「6月16日 上证 回踩 4090 MACD金叉」确认站上四线 | ✅ |
| 6 | 「科技方向在反弹中占优」 | 4/9 | 跟踪Q2科创50从4月到6月连创新高 | ✅ 趋势正确 |

**验证原则（适用于任何KOL评估）：**
1. 事实陈述（成交量、业绩等）→搜索新闻确认数字
2. 趋势判断（触底、回踩等）→搜索后续技术指标确认
3. 时限判断（某事件在何时发生）→搜索事件时间线确认
4. 不验证无标准答案的判断（"看好科技"、"风格轮动"等模糊表述不计入统计）
5. 多来源交叉验证（至少两个独立新闻源）

### 三位博主定位 (get_user_weibos count=15 updated 2026-06-30)

Changed from count=3 to count=15 per blogger to capture yesterday's posts + today's real-time content. With count=3, active bloggers like 唐史主任 would have ALL 3 recent posts from today, completely missing yesterday's analysis.

| 博主 | 信号密度 | 风格 | 推送角色 | 采集策略 |
|------|:-------:|------|---------|---------|
| 唐史主任司马迁 | 26.7% | 操作信号+情绪引导 | 主力信号源 | 近5条 - 信号词加权提取买入信号 |
| 小浣熊1230 | 26.3% | 宏观分析+风险警示 | 风险补充信号 | 近5条 - 提取风险警示信号 |
| **IT精英带你养基** | **7.5%** | **日常定投记录** | **情绪参考** | **近3条 - 仅取「今天亏了X」情绪数据。不用于配比参考** |\n## Self-Evolution Framework (维度A + B)

Two layers added 2026-06-30 to make the system self-correcting:

### 跨任务数据桥接（2026-07-01）

两条独立的数据传递通道，确保推送之间的数据一致性：

**通道1: 开盘方向预测桥接**
```
今日参考(08:30) LLM → _morning_predictions.json → 收盘复盘(16:00) 验证预测
```

**通道2: 昨日收盘数据快照**
```
收盘复盘(16:00) 脚本 → _yesterday_snapshot.json → 财经早餐(08:30) 读取昨收数据
```

**快照架构优点：**
- 早报在任何时间运行（包括盘中手动触发），读到的永远是昨日收盘数据
- 不依赖实时API（API在非交易时段可能返回异常值）
- 外盘(Yahoo)仍然实时拉取，因为隔夜数据需要新鲜
- 博主微博仍然实时拉取，因为最新观点需要即时性

**快照保存位置：** `_yesterday_snapshot.json` 在 `/tmp/fund_data/`，由 `closing_review.py` 在步骤11保存。包含：
- `quotes` — 收盘行情（6个指数）
- `sectors` — 收盘板块（10个ETF）
- `market_overview` — 涨跌家数+两市成交
- `northbound` — 收盘北向
- `funds` — 收盘基金估算净值
- `fund_groups` — 分组数据

**collect_morning_data.py 读取逻辑：** 优先读快照，无快照时回退实时API。每条数据独立fallback——快照缺失的单项仍可走API获取。

### 格式化推文（脚本生成，根治格式漂移，2026-06-30/07-01 应用）

| 推送 | 脚本 | 生成文件 | 格式 |
|:----|:-----|:---------|:----|
| 收盘复盘 | `closing_review.py` → | `_closing_tables.md` | 81行完整推文 |
| 财经早餐 | `collect_morning_data.py` → | `_morning_tables.md` | 76行完整推文 |
| （盘中速递待跟进） | | | |

**晨间表格格式（2026-07-01 用户确认，2026-07-06 新增量价分析）：**

隔夜外盘（3列）、A股昨收（3列）、**📊 量价分析（5列：品种/涨跌/振幅/量价信号）**、板块热度（3列表格）、持仓基金（每组3列简化版：基金/前日净值/昨日涨跌，去掉估算净值列）

```

### 维度A: 数据合理性校验 (Data Sanity)

Each pre-collection script calls `run_sanity_checks(raw_data)` at the end, writing a `_*_sanity.json` report. The cron prompt cats this file; if `status='⚠️'`, the push begins with a warning annotation.

**Validated dimensions** (defined in `_SANITY_RANGES` dict):
| Dimension | Threshold | Skip Condition |
|-----------|:---------:|----------------|
| Index price (上证 / 科创50 / 创业板等) | 2500-4500 / 800-3000 / 1500-5000 | No data → skip |
| Sector collection rate | ≥ 50% | 0 sectors → skip |
| 涨跌家数 total | ≥ 100 | 0 → skip (non-trade time) |
| 两市成交额 | 500-50000亿 | 0 → skip |
| 北向资金 | -200 ~ +200亿 | None → skip |
| Fund collection rate | ≥ 60% | 0 → skip |
| KOL posts present | > 0 | Missing → warn (微博凭据过期) |

Output: `{status: '✅'|'⚠️', checks: [...], warnings: [...], issue_count: N}`
Files: `_sanity_report.json` (morning), `_noon_sanity.json` (noon), `_closing_sanity.json` (closing)

### 维度C: 操作建议系统 (Operation Recommendations)

2026-07-01 新增：将观测数据（行情+KOL信号+趋势）转化为结构化的操作建议，集成到三推送中。

**`PORTFOLIO_WEIGHTS`** — 各组持仓权重估算 + 目标上下限 + 再平衡触发阈值
```python
PORTFOLIO_WEIGHTS = {
    '黄金':     {'weight': 12, 'target_min': 5,  'target_max': 20, 'rebalance_trigger': 5},
    '科技/AI':  {'weight': 59, 'target_min': 40, 'target_max': 70, 'rebalance_trigger': 10},
}
```

**`GROUP_ACTION_RULES`** — 各组买卖触发条件（买/卖/持有信号词 + 定量条件）

**趋势记录** — 每日收盘 `record_group_trend()` 追加到 `_group_trends.jsonl`，`get_group_trend()` 读取最近N天数据供评分

**`score_group_action()`** — 综合评分引擎（-5~+5），输入：趋势数据 + 板块动量 + KOL信号，输出：增持/关注/持有/观望/减持

**`check_rebalance()`** — 再平衡偏离检测，单日涨跌造成的估算权重偏移超过 trigger 时推送建议

**三推送集成：**
| 推送 | 脚本生成文件 | AI prompt 读取 | 输出板块 |
|:----|:------------|:--------------|:--------|
| 今日参考(08:30) | `_operation_plan.txt` | cat 后原样输出 | 📋 今日操作参考 |
| 收盘复盘(16:00) | `_operation_eval.txt` | cat 后原样输出 | 📋 操作评估+趋势速览 |

**关键规则：** prompt 必须要求 AI "原样输出"操作建议文件内容，禁止重新排版。更新 prompt 后需查 `next_run_at` 判断何时生效。

**后续计划：** 盘中速递操作提示（待5个交易日）→ 未持仓候选基金（待10个交易日）→ 操作建议跟踪验证

### 维度D: 量价分析体系 (2026-07-06 新增)

在已有价格/涨跌分析上增加成交量和振幅维度，判断趋势可靠性。核心函数 `get_volume_analysis()` 在 fund_tools.py §7，详见 `references/volume-analysis.md`。

**7档量价信号分类:** 放量上攻🔥(涨>1.5%+振幅>3%) > 温和放量📈 > 放量下跌💧(跌<-1%+振幅>3%) > 放量回调📉 > 缩量阴跌💧 > 缩量横盘➖ > 正常波动🔸

**三推送集成：** 早/收→预格式化表格中嵌入"量价分析"表；午→`_noon_volume.txt` 供LLM读取。旧快照(7/6前)板块无振幅数据跳过。

**核心规则：** 放量上攻=趋势可靠；放量下跌>3%振幅=资金出逃规避；缩量阴跌=卖压减弱不止跌；半日量达前日全天60%+=当日大概率放量。

### 维度E: 全量持仓监控系统 (2026-07-06 新增)

**脚本:** `monitor_all_funds.py`，no_agent cron 交易日16:30CST，静默模式(有信号才推送)。

**6维评分:** D1今日估值变化(天天基金) + D2组别趋势(8天) + D3组内排名 + D4关联标的 + D5量价信号 + D6综合评分。评分→建议映射：>=+2增持/推送, +1关注/推送, -0.5~+0.5持有/静默, -1观望/静默, <=-2减持/推送。

**四支基金专用加仓条件（独立触发）：** 大摩数字C(翻红且半导体<1%或日>+0.5%)；光伏C(放量反弹涨>2%+振幅>3%或翻红或ETF到0.75止损)；新能源C(涨>1.5%+振幅>2%或翻红)；电网C(缩量止跌振幅<2%或回1.95)。

**报告格式规范（详见 `references/monitor-report-format.md`）：** [4] 逐基诊断表包含紧迫度列(🔴高/🟢低/🟡中)，紧迫度在评分与建议之间，建议列用rec自身emoji不重复加紧迫度前缀

### 维度B: 信号归因追踪 (Signal Attribution)

Tracks KOL predictions over time to measure which signal sources are worth including.

**Functions in fund_tools.py**:
- `extract_signals_from_kols(kol_posts, push_type, quotes)` — scans each post against `SIGNALS` dict, detects bullish/bearish/neutral direction, maps to sector index (科技→科创50, 大盘→上证指数, etc), records index price. Stores to `signals.jsonl`.
- `store_signals(signals)` — appends to `fund_system_data/signals.jsonl` + mirrors to R2
- `resolve_past_signals(quotes)` — reads 3-7 day old unresolved signals from JSONL, compares predicted direction vs actual index movement, writes resolution to `signals-resolved.jsonl`
- `generate_signal_report()` — reads last 30 days of resolved signals, produces per-KOL accuracy stats with status levels: ✅ ≥70%, 🔶 ≥50%, ❌ <50%

**Integration**: morning/noon scripts call extract+store, closing script calls resolve.

See `references/data-sources-2026-06-30.md` for the original rationale design doc.

### 维度C: 操作建议系统 (2026-07-01 新增)

### 维度D: 量价分析系统 (Volume/Amplitude Analysis)

2026-07-06 用户指正加入：**分析不能只看涨跌幅，必须结合成交量、振幅判断趋势可靠性。**

#### 核心原则
- 只看涨跌幅是"截面分析"（谁涨谁跌），加上成交量+振幅才是"时间序列分析"（趋势是否可靠）
- **放量上攻（振幅>3% + 涨幅>1.5%）** → 反弹有量支撑，趋势可靠
- **放量下跌（振幅>3% + 跌幅>1%）** → 资金出逃确认，短期内规避
- **缩量横盘（振幅<1.5% + 涨跌幅<0.3%）** → 多空平衡，等待方向
- **缩量阴跌（振幅<1.5% + 跌幅）** → 弱势延续但卖压减弱
- 振幅>4% = 异常波动，多空博弈激烈

#### 函数：`get_volume_analysis(quotes, sectors, prev_total_turnover)`

```python
from fund_tools import get_volume_analysis
va = get_volume_analysis(quotes, sectors, prev_total_turnover=31818)
# 返回:
# volume_signals: [{'name':'科创50','change_pct':1.96,'amplitude':5.2,
#                   'signal':'放量上攻','emoji':'🔥','volume':'1213亿'}]
# total_signal: '偏强：多方放量上攻' | '偏弱：空方放量砸盘' | '震荡：多空博弈激烈'
# turnover_change: '较前日放量32%↑' (对比prev_total_turnover)
# amplitude_summary: '振幅异常（>4%）：1个'
```

#### 信号分类阈值（机械规则）

| 条件 | 信号 | Emoji |
|:----|:----|:-----:|
| pct > 1.5 AND amplitude > 3 | 放量上攻 | 🔥 |
| pct > 0.5 AND amplitude > 1.5 | 温和放量 | 📈 |
| pct < -1.0 AND amplitude > 3 | 放量下跌 | 💧 |
| pct < -0.5 AND amplitude > 2 | 放量回调 | 📉 |
| abs(pct) < 0.3 AND amplitude < 1.5 | 缩量横盘 | ➖ |
| pct > 0 AND amplitude > 2 | 放量反弹 | 🔥 |
| pct < 0 AND amplitude < 1.5 | 缩量阴跌 | 💧 |

#### 三推送集成

| 推送 | 生成方式 | 数据来源 |
|:----|:--------|:---------|
| 财经早餐 | 脚本自动写入 `_morning_tables.md` 中的"📊 量价分析（昨日）"表格 | 收盘快照 JSON 的 quotes+sectors |
| 盘中速递 | 脚本写 `_noon_volume.txt` → LLM 读取并生成"📊 量价分析"表格 | 实时 get_all_quotes() + get_sector_quotes() |
| 收盘复盘 | 脚本自动写入 `_closing_tables.md` 中的"📊 量价分析"表格 | 收盘 quotes_now + sectors_now |

#### LLM prompt 用法

在分析板块轮动或趋势判断时，必须引用量价信号：
- "科创50放量上攻5.2%振幅 → 反弹有量支撑" → 比仅说"科创50涨+1.96%"更有说服力
- "通信放量下跌7%振幅 → 资金出逃确认" → 比仅说"通信跌-1.77%"更准确
- 成交量对比（前日 vs 今日）用于判断市场整体活跃度

**目标：** 将已有的数据采集+信号归因 → 推送到结构化操作建议（增持/减持/持有/关注/观望），让三条推送从"信息展示"升级为"决策辅助"。

**新增数据结构和函数（`fund_tools.py`）：**

```python
```python
# ── 持仓权重（当前13支，4组，2026-07-02更新：删除通航）
PORTFOLIO_WEIGHTS = {
    '黄金':     {'weight': 12, 'target_min': 5,  'target_max': 25, 'rebalance_trigger': 5},
    '科技/AI':  {'weight': 56, 'target_min': 40, 'target_max': 70, 'rebalance_trigger': 10},
    '资源/周期': {'weight': 12, 'target_min': 5,  'target_max': 25, 'rebalance_trigger': 5},
    '新能源':   {'weight': 12, 'target_min': 5,  'target_max': 25, 'rebalance_trigger': 5},
    '医药':     {'weight': 6,  'target_min': 3,  'target_max': 15, 'rebalance_trigger': 3},
}
```python
# ── 组别操作判定规则（2026-07-02：删除通航组）
GROUP_ACTION_RULES = {
    '黄金': {'buy_triggers': ['黄金期货连涨2日', 'KOL看多黄金', '避险情绪升温'],
             'sell_triggers': ['黄金期货连跌3日', '美元走强', 'KOL看空黄金']},
    '科技/AI': {'buy_triggers': ['科创50涨>2%且放量', 'KOL看多科技', '半导体板块领涨'],
                'sell_triggers': ['科创50连跌3日', 'KOL提示科技过热', '北向大幅流出']},
    '资源/周期': {'buy_triggers': ['有色板块涨>2%', '大宗商品反弹'],
                  'sell_triggers': ['KOL提示周期见顶', '资源板块连跌5日']},
    '新能源': {'buy_triggers': ['光伏/新能源板块领涨', 'KOL看多新能源'],
                'sell_triggers': ['新能源板块连跌', '利空政策']},
    '医药': {'buy_triggers': ['医药板块领涨', 'KOL看多医药/创新药', '创新药政策利好'],
              'sell_triggers': ['医药板块连跌5日', '集采利空', 'KOL提示医药风险']},
}
```

**评分机制（`score_group_action()`）：**
- 趋势得分（近3日涨跌幅均值）：+2~-2
- 板块动量得分（对应指数涨跌）：+2~-2
- KOL信号得分（多头/空头匹配组别）：+1~-1
- 综合得分 → 操作：≥+3 增持, ≥+1 关注, ≤-3 减持, ≤-1 观望, 其余 持有

**新增输出文件：**

| 推送 | 脚本 | 新文件 | 用途 |
|:----|:-----|:-------|:-----|
| 今日参考 | `collect_morning_data.py` | `_operation_plan.txt` | 早盘操作计划（供AI读取） |
| 收盘复盘 | `closing_review.py` | `_operation_eval.txt` | 收盘操作评估+趋势速览（供AI读取） |

**今日参考 prompt 新增 `cat /tmp/fund_data/_operation_plan.txt`：**
```
📋 **今日操作参考**
| 组别 | 方向 | 建议 | 理由 |
|:----|:----:|:----|:-----|
| 科技/AI | 🟡 | 持有 | 无明显信号 |
| 黄金 | 🔴 | 观望 | 黄金ETF市场价跌-1.02% |
...（5组完整表格）
✅ 再平衡检查：各组占比均在目标范围内
```

**收盘复盘 prompt 新增 `cat /tmp/fund_data/_operation_eval.txt`：**
```
📋 **操作评估**
| 组别 | 方向 | 今日建议 | 收盘表现 | 评估 | 明日方向 |
|:----|:----:|:--------:|:--------:|:----:|:--------:|
| 科技/AI | 🔴 | 观望 | 📉 -0.07% | ✅ 正确 | 观望/减持 |
...

📊 **本周分组趋势**（sparkline走势图，脚本自动生成）
| 分组 | 走势 | 本周幅度 |
|:----|:---:|:--------:|
| 黄金 | ▁▂▇▇█ | -1.1% → +1.4% 📈 持续上行 |
...

✅ 再平衡检查：各组占比均在目标范围内
```

**数据积累注意事项：** 趋势记录需≥3天才有统计意义。第一天只有单日数据，评分以行情+KOL信号为主。随着天数增加，趋势得分权重自然上升。

### Script References (2026-07-06 update — added volume analysis get_volume_analysis + _noon_volume.txt)

| Script | Location | Purpose | Created/Updated |
|--------|----------|---------|:---------------:|
| `fund_tools.py` | `/opt/data/scripts/` | Core data lib (+volume analysis) | Updated 2026-07-06 |
| `collect_morning_data.py` | `/opt/data/scripts/` | 08:00 pre-script → `_morning_tables.md` + `_operation_plan.txt` | Updated 2026-07-01 |
| `collect_noon_data.py` | `/opt/data/scripts/` | 11:35 pre-script (lightweight calls before slow fund queries) | Updated |
| `closing_review.py` | `/opt/data/scripts/` | 16:00 closing → `_closing_tables.md` + `_operation_eval.txt` + trend record | Updated 2026-07-01 |
| `auto_validate_sources.py` | `/opt/data/scripts/` | Weekly data-source availability report (Sat no_agent cron) | **New** |
| `collect_weekend_data.py` | `/opt/data/scripts/` | Sat 09:00 no_agent weekend overseas push | New |
| `kol_analyze_phase0.py` | `/opt/data/scripts/` | KOL initial profiling (20 posts) | Historic |
| `kol_analyze_phase1.py` | `/opt/data/scripts/` | KOL expansion profiling (50 posts) | Historic |
| `kol_analyze_final.py` | `/opt/data/scripts/` | KOL saturation verification | Historic |
| `kol_evaluate_candidates.py` | `/opt/data/scripts/` | Candidate KOL quality filter | Historic |
| `kol_deep_mofei.py` | `/opt/data/scripts/` | 莫非 deep evaluation (300 posts) | Historic |
| `kol_sector_gap.py` | `/opt/data/scripts/` | Holdings vs Tang industry coverage | Historic |

### R2 Strategy Documents

| Document | R2 Path | Version |
|----------|---------|:-------:|
| System Design v1 | `fund-system/strategy/SYSTEM_DESIGN_v1.md` | Complete architecture + task backlog, 2026-06-26 |
| Timing Analysis v1 | `fund-system/strategy/TIMING_ANALYSIS_v1.md` | Weekend gap analysis, 2026-06-26 |
| Strategy v1 | `fund-system/strategy/STRATEGY_v1.md` | Initial |
| Strategy v2 | `fund-system/strategy/STRATEGY_v2.md` | After implementation |
| Accuracy Report | `fund-system/strategy/KOL_ACCURACY_REPORT_v1.md` | KOL verification |
| Black Talk JSON | `fund-system/data/kol_blacktalk_analysis.json` | Full term analysis |
| Final Profiles | `fund-system/data/kol_profiles/final_profiles.json` | All 3 KOLs |
| 莫非 Deep | `fund-system/data/kol_profiles/mofei_deep_analysis.json` | 300-post eval |
| Sector Gap | `fund-system/data/kol_profiles/sector_gap_analysis.json` | Holdings comparison |

> 用户问「我总感觉他是为了唱空而唱空，你验证下」→ 经300条数据深挖，他不是。

**基础数据：** 300条博文，38天跨度，7.9条/天，均长95字

**多空比变化（证明他随行情调整，不是单一空头）：**

| 时段 | 空头% | 多头% | 多空比 |
|:----:|:----:|::----:|:-----:|
| 早期(5/19-5/31) | 34% | 14% | 0.41 |
| 中期(6/1-6/13) | 29% | 20% | 0.69 |
| 近期(6/14-6/26) | 30% | 24% | **0.80** |

空头倾向在减弱 → 不是"为了唱空而唱空"而是随着市场数据调整。

**有数据源支撑：** 300条中29条(10%)引用了具体数据源(TrendForce、Tom's Hardware、投行报告)。AI泡沫论点有数据支撑而非纯情绪。

**致命缺陷（不纳入主力信源的理由）：**
- 0条长文（>300字）— 结论与80%的分区中篇一样，无深度分析
- 38天的历史大短无法验证预言准确率
- 内容大量重复（"泡沫"×23次，基本是同一论点的多种表述）

**推送角色：** 不单独采集，仅当唐史主任发出强烈买入信号时自动向Yahoo/Google验证他引用的数据（如"75个数据中心被叫停"是否仍成立）。权重15%。

**评估脚本：** `scripts/kol_deep_mofei.py`（300条）+ `scripts/kol_analyze_mofei.py`（100条快筛）

> ⚠️ **IT精英配比修正（2026-06-26数据验证）**：经80条/137天数据分析，他声称的"稳健60%/波动40%"是每周一固定复读的话术模板，并非实际交易记录。
> 实际"进攻组合"金额仅1,000-4,300元，总资产290万的0.15%而非声称的40%（116万）。137天内买入2次、卖出0次，未执行他本人科普的"股债动态再平衡"策略。
> **核定推送角色：仅保留"今天亏了X"作为情绪参考，不作为配比或定投节奏参考源。**

### 画像饱和确认流程

```python
# 4个饱和度指标（满足3个即饱和）
CRITERIA = {
    'sample_size': lambda n: n >= 80,
    'density_stable': lambda d: d < 0.15,  # 四分位密度差值<15%
    'signal_density': lambda d: d > 0.10 or '非信号类',
    'style_stable': True,  # 风格连续2次一致
}

# 渐进采集流程
Phase 0: 最近20条 - 初始画像草稿
Phase 1: 再30条(累计50) - 对比Phase 0一致性
Phase 2: 再30条(累计80) - 验证饱和
Validation: 对一个KOL拉到150+条 - 验证116条画像与150条一致
```

### 新赛道发现机制

扫描用户未持有的申万行业，看动量+博主话题+与已有持仓相关性。

**Done in this session (2026-06-26):**
Sector gap analysis comparing 唐史主任's 227 posts against user's 11-fund portfolio.

Result: User's tech coverage (科创50C+半导体C+沪港深科技C+ESG) already aligns with Tang's core industries. Three apparent gaps (消费/白酒, 金融/券商, 汽车) were disproven on close reading — Tang was analyzing, not recommending. Script: `scripts/kol_sector_gap.py`

**Methodology (data-driven, not inferred):**
1. Define your holding sectors from fund_tools.py FUND_CODES
2. Map each to the industry keywords the KOL uses (INDUSTRY_KW dict)
3. For each KOL industry topic, count mentions AND check if buy-signal words appear in the SAME post
4. If signal_pct > 30%, it's a candidate gap to investigate
5. CRITICAL: read the actual post text. A post containing both '买' and '白酒' is not automatically a buy recommendation — distinguish recommendation from analysis by reading the KOL's actual stance
6. Save gap analysis to /tmp/sector_gap.json for reference

## Chart / Infographic Strategy (Analyzed 2026-06-26)

### Two Different Kinds of "Charts"

| Type | Tool | Precision | Interactivity | Chinese Text | Best For |
|------|------|:---------:|:-------------:|:-----------:|----------|
| Data chart | matplotlib/plotly/echarts | ✅ Exact axes & values | ✅ Clickable/hoverable | ✅ Native | SPA dashboard, K-line, yield curves |
| Info-card | baoyu-infographic (FLUX AI) | ❌ No exact coordinate control | ❌ Static image | ❌ **Garbled** — FLUX cannot render CJK characters reliably | Weekend recap, comparison cards — **only if text is English or <10 Chinese chars** |

### When to Use Each

| Context | Text Push | Info-Card (baoyu) | Data Chart (SPA) |
|---------|:---------:|:-----------------:|:----------------:|
| Daily QQ push (this user uses QQ) | ✅ Primary — 30s read | ❌ Not embedded; images increase read time | ❌ N/A |
| Weekend recap card | — | ✅ bento-grid + corporate-memphis | — |
| Monthly review | Text | ✅ dashboard + corporate-memphis | — |
| SPA page (future) | — | — | ✅ echarts, interactivity |
| Blog post / content creation | — | ✅ | — |

### baoyu-infographic Layout Recommendations

| Scenario | Layout | Style | Rationale |
|----------|--------|-------|-----------|
| 周末回顾卡 | bento-grid | corporate-memphis | Multi-topic overview, clear sections |
| 信号时间线 | linear-progression | craft-handmade | Event-timeline structure |
| 持仓对比 | comparison-table | technical-schematic | Fund-to-fund comparison |
| 风险提示卡 | iceberg | aged-academia | Surface vs hidden risks |

**Key constraint for daily push:** The QQ platform delivers text natively. Adding images forces the user to tap to view → increases friction. Info-cards are for **non-urgent, reference-oriented** delivery (weekend, monthly), not for the 30-second decision window.

### User Formatting Preferences (captured 2026-06-26 from iterative corrections)

This user is specific about push format. Rules that MUST be followed:

1. **Tables for data, not prose.** 外盘、A股、持仓分组全部用 markdown 表格展示，禁用一个一个列数字写句子。
2. **No IT精英 section.** 他不在推送正文中出现，删除所有对他的引用。
3. **昨收A股标题必须标注具体日期.** Write `📊 昨收A股 · 6月25日(三)` not just `📊 昨收A股`.
4. **Emoji headers + clean hierarchy.** Use `━` separators, emoji-leading section headers, and clear visual structure.
5. **No Box labels.** Do not write "Box 1" / "发生了什么" / "影响评估" — the sections speak for themselves.
6. **No footer decorations.** No trailing `---` or `⚡ 自动生成 · 不构成投资建议 ⚡` at the bottom. End clean.
7. **博主信号用引用式.** For each KOL, quote their key post then summarize the signal. Not a bullet list of their life story.
8. **No excessive color.** Use 🔴🟢🟡 for direction, not for decoration.
9. **博主标注.** 唐史主任后标注 `[已验证6/6]`，其他博主不标注验证状态。
10. **Trend data must be visual, not raw text** (2026-07-04). Raw `date=value → date=value` format was rejected. Always use Unicode sparklines (`▁▂▃▄▅▆▇█`) for trend sequences. Sparkline is created via: `spark_chars = ['▁','▂','▃','▄','▅','▆','▇','█']; ''.join(chars[min(int((v-min)/(max-min)*7),7)])`.

### Sparkline Reusable Technique

Unicode block sparkline for compact visual trend display in QQ/text-only channels:

```python
def sparkline_8pt(values: list[float]) -> str:
    """Convert float list to 8-level Unicode sparkline bar"""
    chars = ['▁','▂','▃','▄','▅','▆','▇','█']
    if not values:
        return ''
    mn, mx = min(values), max(values)
    if mx == mn:
        return '▄' * len(values)
    return ''.join(chars[min(int((v - mn) / (mx - mn) * 7), 7)] for v in values)
```

Always pair with a range summary (min% → max%) and direction emoji (📈持续上行/📉跌幅扩大/➖震荡).

### 08:00 盘前简报模板

**Tue–Fri (normal) version:**
```
**📊 财经早餐 · 基金参考 · M月D日(周X)**

📊 **隔夜外盘**
| 指数 | 收盘 | 涨跌 |
|:----|:----:|:----:|

📈 **A股昨收**
| 指数 | 点位 | 涨跌 |
|:----|:----:|:----:|

💰 两市成交 XXXX亿 | 🌊 北向 X亿

🔥 **板块热度**
| 板块 | 今开→收盘 | 涨跌 |
|:---|:--------:|:----:|

💰 **持仓基金（昨日行情参考）**
**【黄金】**
| 基金 | 前日净值 | 昨日涨跌 |
|:---|:-------:|:--------:|
...

📋 **今日判断**
- 上证指数：开方向↑（预计高开）
...

📊 **博主观点**
（引用并解读博主微博内容）

✅ **数据校验**
```

**Monday version (never say 隔夜):**
```
━━━ 今日参考 · M月D日(一) ━━━

🌙 上周五外盘关盘（周末无交易）
| 品种 | 收盘 | 涨跌 |
（表格展示道琼斯/标普/纳指/黄金/美元 — 标注为上周五数据）

📰 周末大事
● web_search 搜到的周末重大事件（政策/地缘/大宗）

📊 上周五A股收盘 · M月X日(周X)
| 指数 | 收盘 | 涨跌 |

💰 持仓分组
...

📰 博主信号（注意抓取周末新发的博文）

📌 今日关注
● 关注开盘后修复力度
● 操作建议
```

### 11:35 盘中速递

```\n━━━ 盘中速递 · M月D日(周X) ━━━\n\n📈 大盘实时\n| 指数 | 点位 | 涨跌 |\n|------|------|------|\n| 上证指数 | XXXX | 🔴 +X.XX% |\n| 创业板指 | XXXX | 🟢 -X.XX% |\n| 科创50 | XXXX | 🔴 +X.XX% |\n\n📊 上午板块排行\n| 板块 | 涨跌 |\n|------|:----:|\n| 通信 | 🔴 +4.26% |\n| 军工 | 🔴 +3.16% |\n| ...按涨跌排序... |\n\n💰 两市成交 XXXX亿  📈 涨跌家数 涨XXX 跌XX\n\n🌊 北向资金\n| 渠道 | 净流入 |\n|------|:------:|\n| 沪股通 | 🟢 -X.XX亿 |\n| 合计 | 🟡 X.XX亿 |\n\n💰 持仓估算\n| 分组 | 涨跌 | 支数 |\n|------|:----:|:----:|\n| 科技/AI | 🔴 +X.XX% | 9支 |\n| 黄金 | 🟢 -X.XX% | 2支 |\n\n📰 盘中信号\n[博主名] 关键引语 → 解读\n\n📌 关注\n- 核心观点1\n- 核心观点2\n\n规则：🔴=涨 🟢=跌，板块/成交额/北向为空则跳过\n```

### 16:00 收盘复盘（脚本生成表格，LLM只加分析）

**格式根治方案（2026-06-30 应用）：** LLM不可靠地排版表格，改为 `closing_review.py` 生成 `_closing_tables.md`（含全部预格式化表格），LLM 原样输出 + 添加 🔮 后市推演。

**架构：**
```
closing_review.py (预采集+数据+表格生成)
  → /tmp/fund_data/_closing_tables.md  (预格式化的完整推文)
  → LLM 读取 _closing_tables.md      (原样输出表格)
  → LLM 添加 🔮 后市推演              (仅分析，不触碰表格)
  → 推送
```

**Cron prompt 结构：**
```
## 第一步：检查交易日
如果 _closing_skip.txt 存在 → 非交易日，跳过

## 第二步：读取数据
1. cat /tmp/fund_data/_closing_tables.md — 预格式化的完整推文
2. cat /tmp/fund_data/_closing_sanity.json — 数据校验

## 第三步：输出推文并添加推演
**重要：表格部分直接输出 _closing_tables.md 的内容，一字不改！**
**你只需要在末尾添加 🔮 后市推演 章节。**
```

**行业板块（3列表格，2026-06-30 用户确认格式）：**
```
📊 **行业板块**
| 板块 | 今开→收盘 | 涨跌 |
|:---|:--------:|:----:|
| 通信 | 1.337→1.397 | 🔴 +4.33% |
| 军工 | 1.235→1.280 | 🔴 +3.73% |
| ... |            |       |
```

## 持仓基金（2026-07-01 简化：只保留前日净值+昨日涨跌）

⚠️ 2026-07-01 用户指正：早报是\"参考\"性质，展示昨日基金表现即可。原先4列（昨收净值/估算净值/涨跌）中\"估算净值\"一列令人困惑，现已简化为3列。

**收盘复盘格式（保留4列，需展示估算值）：**
```
**【黄金】**
| 基金 | 昨收净值 | 估算净值 | 涨跌 |
|:---|:-------:|:--------:|:----:|
| 易方达黄金ETF联接C | 2.7952 | 2.7919 | 📉-0.12% |
```

**财经早餐格式（简化3列，仅供昨日参考）：**
```
**【黄金】**
| 基金 | 前日净值 | 昨日涨跌 |
|:---|:-------:|:--------:|
| 易方达黄金ETF联接C | 2.7952 | 📉-0.12% |
```

**NaN处理：** 天天基金API偶尔返回NaN或Inf的涨跌值（如QDII基金在港股休市时）。Python代码中 `float(ec)` 后必须检查 `math.isnan()` 和 `math.isinf()`，命中时显示`"-"`而不是`nan%`。已应用于`collect_morning_data.py`和`closing_review.py`。需 `import math`。
```
💰 **持仓基金（收盘估算净值，待晚间确认）**
**【黄金】**
| 基金 | 昨收净值 | 估算净值 | 涨跌 |
|:---|:-------:|:--------:|:----:|
| 易方达黄金ETF联接C | 2.7952 | 2.7919 | 📉-0.12% |
| 中银上海金ETF联接C | 1.9513 | 1.9513 | ➖+0.00% |
```

**早盘预测验证（从 _morning_predictions.json 读取）：**
```
📋 **早盘预测验证**
| 指数 | 开方向预测 | 收盘实际 | 验证 |
|:----|:---------:|:--------:|:----:|
| 上证指数 | ↑ 预计高开 | +0.50% ↑ | ✅ 预测正确 |
| 科创50 | ↓ 预计低开 | +3.85% ↑ | ❌ 预测失误 |
预测准确率：5/6 (83%)
```

**方向验证规则（2026-06-30 用户纠正）：**
- 比较的是**早盘预测的开盘方向** vs **收盘实际涨跌幅**，不是开方向vs收方向
- 例如：上证指数预测"开方向↓"但收盘+0.50%↑ → ❌（预测跌实际涨）
「预测成功了=验证通过」
- 预测数据来源：`_morning_predictions.json`（今日参考 LLM 步骤生成）
- 当 `_morning_predictions.json` 不存在时（首次部署/测试），跳过验证部分
- 详细架构见 `references/snapshot-and-tables.md`

**特殊日期措辞（2026-06-30 用户纠正）：**
- 6/30 → 上半年收官日，下一交易日说"下半年首个交易日" **不说"明日"**
- 3/31 → 一季度收官日，下一交易日说"二季度首个交易日"
- 9/30 → 三季度收官日
- 12/31 → 全年收官日
- 月末 → "下月首个交易日"

**完整推演示例：**
```
━━━ 🌆 收评 · 基金收盘复盘 · 2026-06-30(上半年收官) ━━━

📊 **大盘走势**
| 指数 | 昨收 | 今开 | 收盘 | 涨跌 | 开方向 |
...（6列表格）

💰 **两市成交**: 32731亿 (沪15296亿 深17434亿)

📊 **行业板块**
| 板块 | 今开→收盘 | 涨跌 |
...（3列表格）

🌊 **北向资金**: 沪-9.28亿 深-31.10亿 合计🟢-40.38亿

💰 **持仓基金（收盘估算净值，待晚间确认）**
**【黄金】**
| 基金 | 昨收净值 | 估算净值 | 涨跌 |
...（每组4列表格）
**【科技/AI】**
...

📋 **早盘预测验证**
| 指数 | 开方向预测 | 收盘实际 | 验证 |
...（4列表格）
**预测准确率：6/6 (100%)**

🔮 **后市推演**
...（AI 分析，不碰表格）
```

## Data Storage (JSONL + R2)

Store both raw input AND AI output for later analysis:

```
fund-system/
├── data/
│   ├── morning-briefs.jsonl    # raw + summary per day
│   ├── closing-reviews.jsonl   # predictions + actuals
│   └── accuracy.jsonl          # running accuracy stats
└── site/                       # SPA dashboard (future)
    ├── index.html
    └── ...
```

JSONL format (append-only, one JSON object per line):
```jsonl
{"_date":"2026-06-26","_stored_at":"...","type":"morning_brief",
 "raw_inputs":{"quotes":{...},"funds":{...},"kol_posts":{...}},
 "summary":{"market":"...","groups":{...},"kol_signals":[...]}}
```

## User Preferences (Data-Driven Mandate)

This user explicitly rejects inference-based claims about KOLs or strategies. Every assertion must be backed by quantitative evidence.

**Rules of engagement (from user's direct statements, captured 2026-06-26):**
1. "要以数据说话，不要以推断说话" — When evaluating a KOL, pull actual data and compute the metrics. Do not infer signal density from reputation or follower count.
2. "你决定有用没用，要有成熟方法论指导" — The agent decides data sufficiency using documented methodology (4-criteria saturation matrix), not arbitrary limits.
3. "你慢慢拉取扩大样本直到你觉得可用有用为止" — Data collection is iterative (Phase 0→1→2→validation), not a single fixed batch. Each phase re-evaluates whether to continue.
4. "要迭代以事实说话" — Strategy evolves based on actual observed data, not pre-conceived notions.
5. Strategy documents are versioned and uploaded to R2 — every iteration is recorded for traceability.
6. Reject any candidate KOL where the data shows <10% signal density or 0% long-form content — these are not viable signal sources regardless of reputation.
7. **Cross-verify all comment claims** — "评论里比如有人说挣了翻倍，也要以实际证据交叉验证，如果有人乱说呢。" Personal return reports in comments are unverifiable and must not be pushed as fact. Only KOL's own replies and sector names (cross-checked with market data) can be pushed. Aggregate sentiment direction is acceptable ("评论区情绪偏乐观") but never specific user claims.

## KOL Expansion: Following-List Analysis (Negative Finding)

2026-06-26: Analyzed 唐史主任司马迁's following list (98 of 181 followers) to find new signal sources.

**Result: No viable replacements or additions found.** Even well-known financial KOLs in his follow list have collapsed signal quality on Weibo:

| Famous KOL | Followers | Signal Density | Status |
|-----------|:---------:|:--------------:|:------:|
| 洪榕 (交易策略) | 357万 | 0% | Last post Jul 2025 |
| 侯宁 (空军司令) | 424万 | 0% | Only retweets since Nov 2025 |
| 扬韬 (职业投资者) | 138万 | 0% | Sporadic, no measurable signal |
| 狂龙十八段 (资金流派) | 123万 | 5% | Low density, short form |
| 陈果-投资策略 | 15万 | 10% | Avg 42 chars per post |
| 梦想家林奇 | 39万 | **30%** | Only promising one, but last post Oct 2025 |

**Methodology:** Pulled most recent 20 posts from 10 candidate KOLs via desktop API, calculated signal density (same SIGNAL_WORDS_MAP used for Tang), analyzed content depth (avg post length, deep post ratio), and checked posting recency.

**Takeaway:** High-follower-count financial KOLs on Weibo are generally not active signal sources. Don't assume popularity = signal value. 唐史主任司马迁 and 小浣熊1230 together already provide the best available signal coverage. Script: `/opt/data/scripts/kol_evaluate_candidates.py`

## 数据源可用性验证

新增了 `scripts/auto_validate_sources.py`，每周六 10:00 CST 自动运行（no_agent cron），生成可用率报告。

| 验证维度 | 方法 | 阈值 |
|---------|------|:----:|
| API可用率 | 每次采集调用 `track_source()` 记录 | < 50% 标记不稳定 |
| 归档存在率 | 检查JSONL归档中该数据是否出现 | ≥ 80% 稳定 |
| 自动建议 | 连续14天可用率 < 50% → 建议移除 | |

### 2026-06-30 新增数据源

| 数据源 | 函数 | 接口 | 对应推送 | 成本 |
|-------|------|------|---------|:----:|
| 行业板块涨跌 | `get_sector_quotes()` | 腾讯批量 (10个ETF一次HTTP) | 盘中+收盘 | ~180ms |
| 涨跌家数 | `get_market_overview()` | 东财 `api/qt/stock/get` (f169涨/f170跌/f171平) | 盘中+收盘 | ~800ms |
| 两市成交额 | `get_market_overview()` | 腾讯 sh000002+sz399001 field[35] 三段式价格/量/成交额 | 全部推送 | ~200ms |
| 北向资金 | `get_northbound_flow()` | 同花顺 hexin 分钟级API | 全部推送 | ~800ms |

**北向资金** — 2026-06-30 已添加。使用 a-stock-data 中验证的同花顺 hexin 接口 `data.hexin.cn/market/hsgtApi/method/dayChart/`，返回 262 个时间点的沪股通/深股通累计净流入。仅取最后一个有效值用于推送。同花顺接口不封IP。

### a-stock-data 评估结论 (2026-06-30)

**simonlin1212/a-stock-data** 是一个40个端点的 SKILL.md 代码库（非pip包）。对其十层数据架构的评估：

| 层 | 对基金投资者价值 | 原因 |
|----|:--------------:|------|
| 行情层 (mootdx/腾讯) | 无需使用 | 已有腾讯采集 |
| 研报层 (东财/THS/iwencai) | 低 | 个股研报，非基金决策维度 |
| 信号层 (北向/热点) | ✅ 高 | 北向hexin接口已提取使用 |
| 资金面 (融资/大宗/龙虎榜) | 低 | 个股维度 |
| 新闻层 (东财新闻/全球资讯) | 低 | 已有web_search覆盖更广 |
| 基础数据 (财报/F10) | 低 | 个股基本面 |
| 公告层 (巨潮cninfo) | 低 | 个股公告 |
| 打板层 (涨停池) | 低 | 短线个股，非基金场景 |
| ETF期权层 | 低 | 不交易期权 |
| 舆情层 (互动Q&A/热榜) | 中低 | 概念热度可作为新赛道补充 |

**结论:** a-stock-data 的核心价值在于提供了已验证的北向资金接口（同花顺hexin）作为我们之前失败路径的替代方案。其40个端点中，除北向外，其余对个人基金投资+三推送场景的价值不高。不建议全量集成，而是按需提取已验证的API端点。

**非交易时段处理：** `total_turnover` 在非交易时段返回 0，预采集脚本和 prompt 都加了 `if total>0` 条件跳过空数据。

### 自动去留逻辑

```
新数据源 → 部署 → track_source() 每天记录
         → 积累 >= 7天数据
         → 每周六验证脚本评估:
           - 可用率 ≥ 80% → ✅ 保留
           - 可用率 50-80% → 🔶 持续观察
           - 可用率 < 50% 持续14天 → ❌ 自动建议移除
```

## ⚠️ 基金涨跌数据准确性（2026-07-08 新增）

### 根因分析：收盘快照涨跌幅为何不准确

`closing_review.py` 在16:00 BJT运行时，调用 `get_fund_value()` 获取的 `gszzl`（实时估算涨跌）**不是官方发布的净值涨跌**，而是天天基金的盘中实时估算。当官方净值在18:00-22:00发布后，两者可能存在显著差异。

**已知偏差实例（2026-07-07 收盘快照 vs 官方净值）：**

| 基金 | 快照估算涨跌 | 官方净值涨跌 | 偏差 | 影响 |
|:----|:--------:|:----------:|:---:|:----:|
| 009478 (中银上海金ETF联接C) | 0.00%（持平） | **-0.42%**（下跌） | 未显示 | 晨报显示➖，实际📉 |
| 020233 (大摩景气智选混合C) | +0.01%（微涨） | **-0.09%**（微跌） | 方向反转 | 晨报显示📈，实际📉 |
| 017103 (大摩数字经济混合C) | +0.35%（上涨） | **-0.11%**（下跌） | 方向反转 | 晨报显示📈，实际📉 |

### 修复方案：早间官方净值修正

在 `collect_morning_data.py` 中（08:30 BJT运行，此时前日官方净值已发布），对快照中的每支基金执行修正：

```python
# 伪代码逻辑
current = get_fund_value(code)
if current.nav_date > snapshot.nav_date:
    # 官方净值已更新！
    actual_change = (current.nav - snapshot.nav) / snapshot.nav * 100
    # 使用 actual_change 替代 snapshot 的 estimated_change
```

**修正时机：** 08:30 BJT = 官方净值已发布（通常在18:00-22:00发布），所有基金的前日官方净值均可获取。

**适用场景：** 所有三推送的"昨日涨跌"展示都经过此修正。盘中推送（11:35）使用实时 `gszzl` 不受影响。

### 黄金联接基金特殊处理（009478）

黄金联接基金（如009478）的天天基金实时估算 `gszzl` **始终为0.00%**，因为基金公司不提供盘中估值。

**修正策略（三层兜底）：**
1. `get_fund_value()` 新增盘中重试：如果 `gszzl=0.00` 且当前是交易时段(9:25-15:30 BJT)，等3秒重读一次
2. `closing_review.py` 收盘快照保存时：如果 `gszzl=0.00`，用黄金ETF现货（茅台/金价等 proxy）涨跌幅替代
3. `collect_morning_data.py` 早间修正：用官方净值差自动修正（同上述方案）

**代码位置：** `fund_tools.py` lines 232-240 (重试逻辑), `closing_review.py` lines 388-412 (黄金ETF替代), `collect_morning_data.py` lines 112-153 (官方净值修正)

### 北向资金数据源说明

快照中的北向资金（如 -40.38亿）是**昨日收盘时**的有效数据，不是今日实时值。在晨报展示时已加"(昨日)"标注以区分。

北向实时数据通过同花顺 hexin API 获取，在盘中推送（11:35, 16:00）中展示实时值。

### 修改涉及的文件

| 文件 | 修改内容 | 2026-07-08 |
|:----|:--------|:-----------|
| `fund_tools.py` | `get_fund_value()` 添加交易时段重试+`has_official`字段 | ✅ |
| `collect_morning_data.py` | 早间用官方净值差修正涨跌幅 | ✅ |
| `collect_morning_data.py` | 北向加"(昨日)"标签 | ✅ |
| `closing_review.py` | 快照中009478用黄金ETF替代0.00% | ✅ |
| `monitor_all_funds.py` | 009478黄金ETF替代逻辑细化 | ✅ |

### 后续维护

- 如果发现新的基金 `gszzl` 始终为0.00%，可能是该基金类型不支持实时估算，需加入特殊处理
- 官方净值修正依赖 `nav_date` 比较，确保快照中的 `nav_date` 是正确的（当前为基金净值日期）
- 如果某基金官方净值在08:30 BJT仍未发布（极少数情况），修正会自动跳过，保留数据源的估算值

## Pre-Output Verification (MANDATORY)

Before making any recommendation or analysis output, self-check the following — violations caught by the user ("为什么总是我质疑你才去做出修改") are unacceptable:

### Fund/ETF recommendation: data-first, never skip
1. Pull fund size via `get_fund_value(code)` — must show actual scale
2. web_search for manager tenure & performance — for index funds, explain it's the index, not the manager
3. Compile ≥2 comparable alternatives in a side-by-side table (columns: 代码/净值/估算涨跌/规模/特点)
4. THEN give recommendation with data-backed rationale
5. Document the output in `references/fund-addition-analysis.md`

### Count-based verification (MANDATORY after any format change)
After converting a no_agent script's output format (plain text → tables/text restructuring):
1. Compare OUTPUT ITEM COUNT per section with the original
2. If original had 5 D5 volume signals, new version MUST have ≥5
3. If original had 15 abnormal items in volume section, new MUST show ≥15
4. If original per-fund detail showed D3+D4+D5, new version MUST show same
5. Run the script once and manually verify output before pushing
6. User's complaint pattern: "报告内容不够具体" = you trimmed data for formatting

### Percentage allocation: always clarify the base
- Wrong: "建议6-8%" → "6-8%是总金额的还是单独的？"
- Right: "总基金金额6%（=360元），其中A基金4%（=240元）+ B基金2%（=120元），合计6%"

### Timing decisions: ask, don't decide
- When setting up an afternoon buy window, DON'T pick the time yourself
- ASK: "要不要等两点半后趋势确认再买"
- CORRECT: 14:30 CST (`30 6 * * 1-5` UTC) = after 两点半, leaves 30min to operate
- WRONG: 13:30 (volatile reopen), 14:00 (too early), any time set without user input

## Pitfalls

1. **Weibo CLI commands broken on headless servers** — `weibo weibos`, `weibo search`, `weibo profile` use mobile API (m.weibo.cn) which needs separate auth. Use desktop API directly (weibo.com/ajax/statuses/mymblog) with QR-login cookies.
2. **Fund API rate limiting** — 天天基金 API has per-IP limits. Space requests > 1s apart; use 10s timeout.
3. **Weibo credential expiry (~7 days)** — Plan for re-login. Monitor `weibo status` output.
4. **Cron 3-minute hard timeout** — Must use pre-script pattern for data collection. Agent-only phase should be fast (reading pre-parsed files + formatting).
5. **Model override silently not honored** — When pinning a model on the cron job, always include explicit `base_url` for custom providers. See cron-content-pipeline pitfalls.
6. **Market holidays — now handled via CHINESE_HOLIDAYS_2026 set + auto-scrape framework** — See `references/holiday-handling.md`. The SSE publishes next year's schedule in December. The pre-collection scripts write skip files (`_skip.txt`, `_noon_skip.txt`, `_closing_skip.txt`) on non-trading days, and all three cron prompts MUST check for these files in Step 1. For 2027+, rely on `_scrape_sse_holidays()` auto-scrape; if it fails, manually add a `CHINESE_HOLIDAYS_2027` set.
   
   **⚠️ Stale skip file bug (2026-07-06):** Old skip files from PREVIOUS non-trading days survive in `/tmp/fund_data/` and block the NEXT trading day's push (LLM sees the file → "非交易日"). Fix applied: all three pre-scripts now auto-clean old skip files on startup. If this fails again, manually run `rm -f /tmp/fund_data/_*skip*.txt` or re-trigger the pre-script. See `references/stale-skip-file-fix.md`.
7. **Monday 08:00: never say "隔夜"** — US market last closed ~76h earlier (Sat 04:00 CST). Write "上周五外盘关盘" instead, and supplement with web_search for weekend events. See `references/timing-analysis.md`.
### Push images not archived — Images sent via MEDIA: protocol are ephemeral. Save R2 URL in the JSONL record for later retrieval.
1. **KOL comment analysis: triggered, not daily** — Weibo comments on signal posts can reveal sectors/positions the author intentionally omitted from the main post. E.g. 唐史主任's post "清杂毛接货" said nothing about sectors; comments revealed 锂电、面板/玻璃、配件龙头. But daily comment scraping is too noisy (539 comments/post, ~60% noise). Use only as triggered pattern: when KOL publishes a signal post (融资仓/加仓/右侧/触底), pull top 20-30 comments for supplementary analysis. Three-tier value extraction: (a) author's own replies (highest weight) → (b) high-liked sector-specific questions → (c) follower return reports as verification of direction. See `references/weibo-comment-analysis.md`.
1. **Weibo comment API: only `aj/v6/comment/big` works** — `weibo.com/ajax/statuses/buildComments` returns 参数错误. Use `weibo.com/aj/v6/comment/big?ajwvr=6&id={post_id}&from=singleWeiBo&page={n}` instead. Returns HTML — parse with regex for `node-type="root_comment"` blocks + `WB_text` for content.
11. **sparkline 走势图 = 用户认可的数据趋势展示形式** — 2026-07-04 验证。用 Unicode 8级色阶字符 `▁▂▃▄▅▆▇█` 将5天分组趋势可视化为迷你走势图。已应用于：周末外盘速报（分组本周趋势）和收盘复盘（本周分组趋势）。**禁止**用纯文本 `date=value → date=value` 格式展示趋势数据。sparkline 算法：归一化到 [0,7] 区间后映射到字符索引，若等值则全部显示`▄`。配套提供区间摘要（`min% → max%`）和方向描述（📈 持续上行/📉 跌幅扩大等）。
9. **Fund codes from screenshots are unreliable (~50% error rate)** — User-provided fund codes from screenshot OCR or manual transcription are frequently wrong. Always verify every fund code via the 天天基金 API before trusting it. Run verification script after any code update.
1. **Tencent supports batch queries — use them** — `https://qt.gtimg.cn/q=code1,code2,code3` returns all codes in one HTTP call. Use this for sector ETFs and any multi-symbol queries instead of individual calls (reduces 8 sequential 150ms queries to one ~180ms batch). Applied to `get_sector_quotes()` in fund_tools.py.
1. **Pre-script execution order matters** — 天天基金 fund queries have 5s timeout each and 17 funds can take 50-85s combined. Put lightweight calls (sector ETFs ~180ms, market overview ~1s, northbound ~800ms, Yahoo ~3s for 6 symbols) BEFORE fund queries and KOL Weibo calls. That way even if the script times out at 120s, the lightweight data is already saved. Applied to all three pre-scripts on 2026-06-30.
1. **北向资金 only via 同花顺 hexin API, not East Money** — East Money's `push2.eastmoney.com/api/qt/kamt.kline/get` returns unclear zero values. 同花顺's `data.hexin.cn/market/hsgtApi/method/dayChart/` works reliably with 262 minute-level data points. Use `get_northbound_flow()` in fund_tools.py which has built-in single retry. Source: verified via a-stock-data (simonlin1212/a-stock-data) SKILL.md.
1. **Auto-validation crons** — `auto_validate_sources.py` runs every Saturday 10:00 CST as a no_agent cron. It reads `_source_availability.jsonl` (logged by `track_source()` after each API call) and checks JSONL archives. Output goes to QQ. New data sources need >= 7 days before entering evaluation.

15. **18-fund parallel collection — timeout 5s→8s improved success from 12/18 to 17/18** — Initially fixed serial→parallel (ThreadPoolExecutor max_workers=5, completes ~23s vs ~50-100s serial). But individual fund requests to `fundgz.1234567.com.cn` still timed out at 5s.
   **Remaining issue discovered 2026-06-30:** 12/18 funds succeeded (67%). The timeouts were random (different fund codes each run), indicating API-side congestion not rate-limiting. The parallel batch completes in ~23s regardless.
   **Second fix (2026-06-30):** Raised `get_fund_value()` timeout from 5s→8s (line 166 of fund_tools.py). Result: **17/18 success (94%)** — only 1 fund timeout per run on average. Overall script still ~37s because 8s timeout only affects the slow few, not the fast majority.
   **Implementation pattern:**
   ```python
   from concurrent.futures import ThreadPoolExecutor, as_completed

   def get_all_funds() -> dict:
       result = {}
       items = list(FUND_CODES.items())
       with ThreadPoolExecutor(max_workers=5) as exc:
           future_map = {exc.submit(get_fund_value, code): (code, name) for code, name in items}
           for f in as_completed(future_map):
               code, name = future_map[f]
               v = f.result()
               if v: result[code] = v
               else: result[code] = None
       return result
   ```

16. **Cron prompt template drift risk** — Each of the three fund cron jobs (今日参考 `d7b0a`, 盘中速递 `d29e6`, 收盘复盘 `7a165`) has its own separate prompt stored in the scheduler DB. When adding new data sources, you must update ALL THREE prompts — updating only the data collection script is not enough. Verification method: for each prompt, check that (a) the `cat` command for every data file is present in Step 2, and (b) the formatting template includes the new data. Current file sets: morning = already embedded in `_morning_tables.md` (量价分析 in pre-formatted table); noon = 11 files (_noon_skip, _noon_market, _noon_fund, _noon_group, _noon_overview, **_noon_volume**, _noon_northbound, _noon_sector, _noon_kol, _noon_rss, _noon_sanity); closing = already embedded in `_closing_tables.md` (量价分析 in pre-formatted table).

17. **Cron output formatting: markdown tables NOT optional — verify via session search** — This user explicitly rejects prose-style text dumps. The original sin was text-as-bullets (纯文字堆叠). **User's actual complaint:** "不是图片，是说文本格式不对，显示的都是文本堆一起，没有表格结构什么的" — the correction was about text format, NOT about images. Every data section (外盘、A股、板块排行、持仓分组、北向) MUST use markdown tables with headers and aligned columns. The cron prompt must explicitly say "文本必须用 markdown 表格排版，不要纯文字堆叠". **Verification method:** After updating a cron prompt, search for the cron session output via `session_search()` to confirm the generated report uses tables. The 盘中速递 prompt is confirmed working (see session `cron_d29e6063c469_20260630_052038` output). Rules embedded in cron prompt: 🔴=涨 🟢=跌 (domestic A-share convention), empty data auto-skipped, no IT精英 section, total chars ≤800.

18. **Sanity report files have per-push prefixes** — Don't use `_sanity_report.json` for all three scripts. The three pre-collection scripts write different filenames: `_sanity_report.json` (morning), `_noon_sanity.json` (noon), `_closing_sanity.json` (closing). Each cron prompt must `cat` the correct one. New data file added → ALL three prompts must be updated (cron prompt template drift risk, same as #16).

19. **Signal tracking needs 3+ days to show results** — `resolve_past_signals()` looks for signals 3-7 days old. On day 1 of deployment, no signals exist to resolve. The first resolved signals appear on day 4 (after 3 trading days of paired signal→outcome data). `generate_signal_report()` requires 30 days of resolved data to produce meaningful stats. Be patient and explain this timeline to the user.\n\n20. **JSONL archive fallback for closing comparison** — `closing_review.py` compares morning predictions vs closing actuals by reading `_raw_data.json` from `/tmp/fund_data/`. If this file is missing (e.g. `/tmp/` was cleaned, or the morning cron failed), the comparison section is silently skipped. Fix: `closing_review.py` now falls back to `morning-briefs.jsonl` in `fund_system_data/` — it reads the last entry matching today's date and type='morning_brief'. The JSONL is written by `store_jsonl()` in the morning pre-script and synced to R2, so it persists even if `/tmp/` is wiped. Implemented in `closing_review.py` lines 24-44.\n\n22. **Fund timeout: triple-layer defense (2026-06-30)** — (a) get_fund_value() raised 5s→8s timeout, (b) auto-retry once with 0.5s delay, (c) closing_review.py falls back to morning fund data for timed-out codes. Result: 12/18 to 17/18 to ~18/18 with fallback.

23. **KOL sanity: closing pushes should NOT warn about empty KOL** — run_sanity_checks changed to 'if kols: ... else: 本推送无采集'. Passing kol_posts:{} from closing no longer triggers false 凭据过期 warning.

24. **Closing review format: user requires per-index comparison table** — Not just a summary score. Prompt must force table with 指数/早盘方向/收盘方向/验证 columns. Data in _closing_summary.txt.

25. **Sector ETFs now include open/prev_close** — get_sector_quotes() returns price, change_pct, open, prev_close. Summary files formatted as 板块名: 今开盘价→收盘价 (涨跌幅). Cron prompt must show openclose column.

26. **Fund group summary now includes per-fund detail** — Format: 分组名: 均涨跌 (N支) [基金名 昨收净值→估算净值 (涨跌幅%)]. First 2 funds of each group.

27. **Cross-job prediction handoff: morning cron MUST save _morning_predictions.json** — The 收盘复盘 cron reads this file to verify predictions. Without it, the prediction verification section is silently skipped. This file is ONLY created by the 今日参考 cron's LLM step (saving via `cat > /tmp/fund_data/_morning_predictions.json`). On the first day after deployment, no predictions file exists — the closing cron gracefully skips.

28. **AI output self-verification after push is MANDATORY, not optional** — User explicitly expressed frustration at having to find bugs himself. Every cron prompt must include a format self-check step before delivering: (a) table column alignment matches template, (b) data numbers match source files, (c) prediction sources are from _morning_predictions.json not hallucinated, (d) forbidden words checked (e.g. "明日" on month-end dates), (e) non-trade-day skip active. See `cron-content-pipeline` → references/financial-cron-data-accuracy.md → Section 4 for the self-check template.

29. **Format drift is chronic — definitive fix: pre-generate output in Python script, not LLM.** The LLM keeps deviating from table format despite explicit templates, self-check steps, and repeated user complaints. The definitive fix (applied 2026-06-30 to closing_review.py): generate `_closing_tables.md` with ALL tables pre-formatted in Python. The LLM reads this file and outputs it verbatim — no formatting decisions. See `cron-content-pipeline` → `references/financial-cron-data-accuracy.md` → Section 5 for the full pattern. This applies to all three fund crons (closing review done; morning and noon should follow).

30. **推送后需等用户确认再推送下一版** — 对同一个数据项多次推送不同格式的版本会导致用户混淆。应等待用户确认格式后再修正推送，或标记旧版本已过期。

31. **When giving fund advice, do NOT fabricate thresholds** — Never say "wait for 3% rally" without data backing. Use price-level triggers (e.g. "buy back if 科创50 falls below 1930") and cite historical crash-recovery patterns. If unsure, say "I don't have enough data" rather than inventing a number.

32. **Fund T+1 pricing is by end-of-day NAV on trade date, not confirmation date** — Sell today before 15:00 → get TODAY's closing NAV. Buy back → get THAT day's closing NAV. T+1 only affects cash settlement (华夏 T+1, 大摩 T+2). User only misses 1 day of exposure, not 3. Never exaggerate time cost.

33. **Buy-back triggers should be price-drop based, not rally-based** — "If drops X% more, buy back Y%." Rally triggers ("wait for 3% gain") are buy-high logic. Valid exception: "stabilizes for 3+ days without further drop" = panic over signal.

34. **Weibo re-login: use `weibo_login_direct.py` (2026-07-04 verified)** — The QR login flow at `passport.weibo.com` sets passport cookies, but SUB comes from cross-domain redirects. Do NOT use `weibo login --qrcode` CLI (QR ID truncated to 20 chars → rapid expiry). Do NOT generate QR images locally with `qrcode` library (same truncation bug).
   
   **Verified approach:** Run `scripts/weibo_login_direct.py`. It:
   - Requests QR image URL from Weibo's `/sso/v2/qrcode/image` endpoint
   - Downloads the server-generated QR image directly (no truncation → full 4-min validity)
   - On login success: follows `data.url` + `data.alt` to capture all 6 cookies (SUB, SUBP, SCF, ALF, ALC, X-CSRF-TOKEN)
   - Saves to `~/.config/weibo-cli/credential.json` — same path `fund_tools.py` auto-reads
   
   After login, verify: `get_user_weibos('2014433131', count=3)` returns 3 posts with no 会话过期 error.
   
   Cookie expiry ~7 days. No browser/Chrome dependency — works on headless servers.

35. **When user asks about adding funds based on KOL signals, use the 5-step framework** — (1) Scan KOL posts for explicit buy signals (not just mentions); (2) Check sector performance data (current trend, volume, relative strength); (3) Assess KOL's current mood (bullish/bearish/cautious) — e.g. 主任 saying "刷新最大单日亏损" + "从此再无 尽多头义务" = not a buying signal; (4) Check portfolio overlap — if existing funds already cover the sector; (5) Output tiered priority with reasoning at each level. Document the output in `references/fund-addition-analysis.md`.

31. **closing_review.py 生成 _closing_tables.md 的模式** — 2026-06-30 应用。所有 markdown 表格由 Python 代码生成（行业板块3列表格、持仓基金每组4列表格），LLM 不再参与排版。LLM 只读 `_closing_tables.md` 原样输出 + 添加推演分析。这是格式反复漂移 3 次后的终极方案。

32. **操作建议依赖趋势数据积累** — `score_group_action()` 的精度随趋势数据天数增长。第一天只有单日行情+KOL信号得分，≥3天才有趋势得分权重。部署后前3天操作建议会偏保守（多出"持有"），属正常现象。

33. **PORTFOLIO_WEIGHTS 是估算值，不可用于精确再平衡** — 权重基于组内基金数量等权估算。用户若有实际持仓金额/份额数据，应替换为精确值。`rebalance_trigger` 是"触发检查的阈值"而非"精确边界"。

34. **操作评估的准确性受限于数据质量** — `score_group_action()` 的 KOL 信号匹配是简单的关键词匹配（"科技"关键词触发科技/AI组评分）。若KOL博文提到"科技"但实际讨论其他行业，会导致评分偏差。引入 KOL 画像后可通过博主→行业映射缓解。

35. **三推送操作建议的一致性** — 今日参考生成的操作计划(`_operation_plan.txt`)和收盘复盘的操作评估(`_operation_eval.txt`)各自独立计算评分。若盘中出现大幅反转（如北向从早盘的+50亿急转为-30亿），两遍评分可能不一致。属设计上的合理差异——早盘计划基于开盘前信息，收盘评估基于全天数据。不一致本身是信号。盘中速递的"盘中操作提示"可填补这个差距，待前两个跑通后考虑。

36. **Fund group removal must update hardcoded lists in scripts + verify with grep** — When removing the LAST fund in a group from FUND_CODES, you must ALSO remove that group name from the hardcoded group iteration lists in `closing_review.py` (search `for gname in ['黄金', '科技/AI', '资源/周期', '新能源']`) and `collect_morning_data.py` (same pattern). Additionally remove the group from `fund_tools.py`: `GROUPS`, `PORTFOLIO_WEIGHTS`, `GROUP_ACTION_RULES`, and the group-sector mapping in `score_group_action()`. Failure causes empty group headers in push output.

    **Adding a group** also requires updating ALL same hardcoded lists + `fund_tools.py` `GROUPS`/`PORTFOLIO_WEIGHTS`/`GROUP_ACTION_RULES` (2026-07-06: added 医药 group).

56. **All-fund monitoring in quiet mode** (2026-07-06) — Use `monitor_all_funds.py` (no_agent cron, 16:30 CST) for daily full coverage. Silent unless a non-hold signal fires. The user expects ALL 15 funds analyzed, not just weak ones.
   
   **Verification step (MUST run after every group removal):**
   ```bash
   grep -rn '通航\|REMOVED_GROUP' /opt/data/scripts/*.py
   ```
   Search for the removed group name across ALL `.py` files. Also search for it in FUND_CODES in fund_tools.py specifically. If any reference remains (excluding comments that say "已清仓"), fix it. Common missed locations: `PORTFOLIO_WEIGHTS`, `GROUP_ACTION_RULES`, `score_group_action()` sector_map, `closing_review.py` group_order, `collect_morning_data.py` group_order.
   
   **Run the consistency checker after any group change:**
   ```bash
   python3 scripts/check_group_consistency.py
   ```

37. **When recommending specific fund products, ALWAYS pull and present the full data set FIRST** — User will (rightfully) call you out if you recommend without showing: (a) fund size, (b) manager tenure & performance (even for index funds — explain why it's the index not the manager), (c) comparable alternatives with a side-by-side table. The pattern for any fund recommendation should be: `get_fund_value(code)` for NAV + web_search for scale/performance history + compile comparison table → THEN give a recommendation with rationale. Never skip to the recommendation step without the data table. User's exact words: "为什么总是我质疑你才去做出修改...你为什么不能做到自我分析判定推荐"\n\n**Percentage communication: always clarify the basis** — When giving allocation advice, state explicitly "% of total fund portfolio". When splitting into sub-funds (e.g. "医药100 4% + 创新药 2%"), clarify that the total is still 6%. Ambiguity between "total allocation" and "per-fund split" causes confusion. Template: "建议总仓位X%（=总基金金额的X%），其中A基金Y%、B基金Z%，合计Y+Z=X%"。\n\n**Afternoon analysis timing: confirm at 14:40 (after 两点半), not earlier** — User explicitly wants 两点半定律 respected. 13:30 is too early (market just reopened after lunch, volatile). 14:00 still premature. 14:40 gives 20 minutes to operate before 15:00 close. The cron should be set to `40 6 * * 1-5` UTC. When setting up afternoon analysis, always ask "要不要等两点半后趋势确认再买" rather than deciding the time yourself.\n\n**推创新药 = 防御品种确认** — Verified via web search: 唐史主任司马迁's own post (April 2026) states "创新药我是作为防御品种配置的". Also confessed "被创新药揍的鼻青脸肿" (losses in innovation drugs). This means: (a) 创新药 is NOT a科技进攻品种 in 主任's framework, (b) it's a low-elasticity defense position, (c) if recommending 创新药 vs 医药100, explain this positioning difference and the 科创板 overlap (23 innovation drug companies on STAR board =科技外围属性).\n\n**Cron `run` only completes after LLM step** — Pre-script may run (files updated in /tmp/) but `last_run_at` only updates when LLM completes. A stale `last_run_at` with fresh data files means LLM failed. Check via `session_search()` — if `bookend_end` is `[]` and message_count=1, re-trigger with `cronjob(action='run')`. See references/extra-sessions-20260702.md.

36. **Extra QQ sessions may be auto-created by gateway** — Agent cannot create/switch sessions. Check new sessions' content, merge un-integrated work into main session, record IDs in a reference file, then delete. See references/extra-sessions-20260702.md.

37. **Multi-sector comparison: use structured table output** — When user asks "怎么看[行业A/行业B/行业C/行业D]" (3+ sectors at once), produce a comparison table: signal source / trend / portfolio overlap / add-flag. Mark unmonitored sectors as "未追踪". Sort by signal strength. Example: 机器人/商业航天/金属/医药 analysis from 2026-07-03.

38. **Cron prompt: LLM will reformat pre-generated tables despite "一字不改"** — Verified 2026-07-06. The LLM reads `_morning_tables.md` (which has correct Monday titles like "🌙 上周五外盘关盘") but then outputs its own version with old titles ("📊 **隔夜外盘**") when the prompt says "输出, 一字不改". The fix is:
    - Use explicit command language: "⚠️ 必须遵守的规则（违反会导致推送错误）"
    - Numbered rules: "1. **你必须逐字原样输出 _morning_tables.md 的全部内容**，不准修改任何一个字符、一个标点、一个字。"
    - List the EXACT titles that must NOT be changed as examples.
    - Structure: check skip → cat file → output file verbatim → THEN add analysis sections after.
    - Always verify via `session_search()` after updating a prompt — check the anchor message's section headers.
  
42. **Oracle ARM server: Chinese financial APIs have intermittent SSL/timeout failures** — Verified 2026-07-06. From the Oracle ARM data center (likely non-China region), the following APIs are unreliable:
    - **East Money push2** (`push2.eastmoney.com`) — SSL handshake timeout, ~90% failure rate. Affects `get_market_overview()` for rise/fall/limit-up counts. Mitigation: `_yesterday_snapshot.json` snapshot fallback.
    - **East Money push2ex** (`push2ex.eastmoney.com`) — Completely unreachable. 连板/封板 data blocked. Mitigation: requires China-located proxy (Tencent Cloud server, 146.56.146.185).
    - **Reliable APIs:** Tencent `qt.gtimg.cn` (quotes), 天天基金 `fundgz.1234567.com.cn` (NAV), Yahoo Finance (overseas), Weibo (KOL).

43. **Inter-prompt RSS file sharing** — The closing prompt reads `_rss_news.txt` (generated by the morning script `collect_morning_data.py`) for its `📰 赛道回顾` section. This is a cross-session data dependency: the closing pushes in the afternoon reference morning-collected RSS data. If the morning cron fails (skip.txt written), `_rss_news.txt` won't exist, and the closing prompt should handle this gracefully. When adding new data files to one pre-script that another push's prompt reads, verify the fallback behavior for the dependent push.

44. **All three cron prompts must be updated together when adding new data files** — Confirmed 2026-07-06: when `collect_morning_data.py` started writing `_rss_news.txt`, the morning prompt needed Step 2 addition AND the closing prompt needed it for 赛道回顾. The noon prompt's `_noon_rss.txt` (added 2026-07-06) also needed its own Step 2 addition. Never update only one prompt — run `cronjob(action='list')` to verify all three, then **read each existing prompt with cronjob(action='list') BEFORE overwriting** — accidentally setting a prompt to "placeholder" in an update call requires session_search() to recover the original.
  
**Market sentiment grading** — `grade_market_sentiment()`, `get_short_term_sentiment()` added to fund_tools.py (2026-07-06).
    - `is_monday` → overnight_label: "🌙 上周五外盘关盘" (vs "📊 **隔夜外盘**")
    - `is_monday` → a_share_label: "📈 上周五A股收盘" (vs "📈 **A股昨收**")
    - `is_monday` → fund_label: "💰 **持仓基金（上周五行情参考）**" (vs "💰 **持仓基金（昨日行情参考）**")
    - The LLM cron prompt must also be updated to: (a) NOT mention the old title names in prompt examples (so LLM doesn't repeat them), (b) add a Monday-specific instruction: "用 web_search 搜索周末重大事件，添加「📰 周末大事」板块在最前面".

40. **Market sentiment grading** — `grade_market_sentiment(rise, fall, limit_up)` added to fund_tools.py (2026-07-06). Uses 5-tier mechanical threshold: ratio >0.70=普涨 🔴, >0.55=偏强 🔴, >0.45=中性 🟡, >0.30=偏弱 🟢, else=冰点 🟢. Integrated into all three pre-scripts (morning/noon/closing) via `_market_overview_summary.txt`, `_noon_overview.txt`, `_closing_overview.txt`. The grade is embedded in the data file; the LLM picks it up when it cats the file. No cron prompt changes needed for this integration.

45. **量价分析依赖 sector 振幅数据 — 旧快照无 high/low 字段** — `get_sector_quotes()` 在 2026-07-06 之前只返回 price/change_pct/open/prev_close，不包含 high/low/volume/turnover。因此 7/6 之前的 `_yesterday_snapshot.json` 的 sectors 中没有振幅数据。旧快照中的 sector 振幅会显示 0.0%，在量价分析表格中会被自动跳过。新快照（7/6 及之后）的 sector 包含完整字段。**影响范围：** 财经早餐的"📊 量价分析（昨日）"板块在 7/6 之后才会显示完整的 sector 量价数据。

46. **量价分析结论比纯价格分析更有力 — 必须在分析中引用** — 用户 7/6 明确指正：只看涨跌幅不够。分析结论必须包含成交量+振幅维度的判断。例如：
    - ❌ "科创50涨+1.96%领涨" → 截面描述，无可靠性判断
    - ✅ "科创50放量上攻5.2%振幅，反弹有量支撑" → 时间序列+量价验证
    - ❌ "通信跌-1.77%最弱" → 短期描述
    - ✅ "通信放量下跌7%振幅+15亿成交，非散户行为，资金出逃确认" → 量价确认

47. **Monitor script vs buy-signal script** (2026-07-06) — Two separate monitoring cron jobs exist: (a) `monitor_all_funds.py` (no_agent, 16:30 CST) for full 14-fund portfolio scan with 6-dimension analysis; (b) `monitor_buy_signals.py` for the original 4-weak-fund targetted signal watch. Run BOTH — they serve different purposes (broad coverage vs targeted alert).\n\n48. **Format optimization: STRUCTURE only, never trim content** (2026-07-06) — When converting no_agent script output from plain text to markdown tables, verify the new output shows every data dimension the original did. Compare: original had D1+D2+D3+D4+D5 → new must have same. Check counts: original showed N items → new must show ≥N. User explicitly complained about removed D3 (组内表现), D4 (关联标的), and truncated signal lists. See `references/report-format-rules.md`.\n\n49. **Portfolio update: verify everything** (2026-07-06) — Every time a fund is ADDED or REMOVED, update ALL of:\n    • `FUND_CODES` in fund_tools.py\n    • `GROUPS` in fund_tools.py\n    • `PORTFOLIO_WEIGHTS` in fund_tools.py\n    • `GROUP_ACTION_RULES` in fund_tools.py\n    • Monitor script fund lists (`monitor_buy_signals.py`, `monitor_all_funds.py`)\n    • Then run `grep -rn 'REMOVED_CODE\\|REMOVED_GROUP' /opt/data/scripts/*.py` to find any missed references\n    • Then run the check_group_consistency.py script\n    User expects the count shown in the report header (\ "覆盖: N只基金\") to match actual FUND_CODES count.\n\n**Verification command after any portfolio change:**\n```bash\ngrep -n 'FUND_CODES' fund_tools.py | head -3\npython3 -c \ "from fund_tools import FUND_CODES; print(f'{len(FUND_CODES)} funds')\"
    
    **Implementation (add dedup in `get_group_trend()`):**
    ```python
    def get_group_trend(name, days=5):
        entries = []
        seen = {}
        for row in _read_jsonl(TREND_FILE):
            seen[row.get('_date')] = row  # last wins
        entries = sorted(seen.values(), key=lambda x: x.get('_date', ''))
        # Then filter by group name and take last N days
        ...
    ```