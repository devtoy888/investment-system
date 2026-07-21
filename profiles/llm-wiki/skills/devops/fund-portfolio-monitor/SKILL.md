---
name: fund-portfolio-monitor
description: >-
  Configure and maintain a fund portfolio monitoring system — collect fund/ETF data,
  run multi-dimensional diagnosis, generate formatted reports with urgency scoring,
  and track suggestion accuracy over time. Covers monitor_all_funds.py and the
  6-dimension analysis framework.
triggers:
  - User mentions 持仓监测, 基金监测, 财经辅助系统, or monitor_all_funds
  - User wants to adjust report format, add/remove columns, or change scoring logic
  - User wants to track or verify operation suggestion accuracy
  - Time-based: push test during trading hours should pick appropriate content
category: devops
reference_files:
  - references/portfolio-maintenance.md: User's exact holdings, transaction log, and update commands
  - references/oracle-arm-data-sources.md: Which financial APIs work from Oracle ARM (verified 2026-07-08)
---

# Fund Portfolio Monitoring System

## Overview

The fund portfolio monitoring system (`monitor_all_funds.py`) runs daily to analyze 13 funds across 4 groups using a 6-dimension framework. It produces a formatted report with operation suggestions and tracks their accuracy day-over-day.

## Architecture

```
monitor_all_funds.py  (main analysis)
  ├── collect_all()    — parallel data collection (funds, indices, sectors, northbound, overnight)
  ├── run_full_analysis() — 6D analysis + grouping + rebalancing
  ├── print_report()  — formatted output
  │   ├── _verify_previous_suggestions() — compare yesterday's advice vs today's performance
  │   └── _save_suggestion_log() — persist today's advice for tomorrow's verification
  └── fund_tools.py   — data fetching utilities

Log file: /tmp/fund_data/_suggestion_log.json
```

## 6-Dimension Analysis

| D# | Dimension | Source |
|:---|:----------|:-------|
| D1 | 今日估值变化 | Fund estimated_change |
| D2 | 近3日组别趋势 | get_group_trend(days=5) |
| D3 | 组内相对表现 | vs group avg, rank within group |
| D4 | 关联标的 | Related sector/index quote |
| D5 | 量价信号 | Volume analysis (放量/缩量/振幅) |
| D6 | 综合操作建议 | Scored recommendation + urgency |

## Report Format Rules

### [4] 逐基诊断 Table
```
| 代码 | 名称 | 组别 | 估值 | 评分 | 紧迫度 | 建议 |
|:----|:----|:----:|:----:|:---:|:-----:|:----:|
| 017103 | 大摩数字经济混合C | 科技/AI | -2.59% | -2.0 | 🔴高 | 🔴 减仓观望 |
```

CRITICAL: `rec` (recommendation) already contains its own emoji prefix (e.g. `🔴 减仓观望`, `🟡 持有`). Do NOT prepend another urgency emoji to it — that produces double emoji (`🔴🔴`). Use `{rec}` alone for the 建议 column, and `{urg_icon}{urg}` for the 紧迫度 column.

### [4] Signal Detail Format
Every fund with signals gets:
```
📌 {code} {name}

今日: {d1}

趋势: {d2}

组内: {d3}

关联: {d4}

量价: {d5}

信号: {sigs}
```
Each dimension on its own line, blank line between dimensions. No extra emoji suffix on the title line.

### [2] 板块热度 Table
```
| 板块 | 涨跌 | 振幅 | 量价信号 |
|:----|:----:|:----:|:--------:|
| 🔴 半导体 | +0.84%█░░░░░░░░░ | — | 缩量 📈 |
```

### [1] 市场全景
```
| 指数 | 点位 | 涨跌 |
|:----|:---:|:----:|
| 上证指数 | 4041.24 | 🟢 -0.06% |
```

## User Portfolio Tracking (用户实时持仓)

The system supports tracking actual shares held per fund, stored at `/tmp/fund_data/_user_portfolio.json`. This enables real-weight-based rebalancing instead of static PORTFOLIO_WEIGHTS percentages.

### Data Structure

```json
{
  "017103": {"shares": 121.66, "cost": 4.3921, "note": "大摩数字经济混合C(已减持25%)"},
  "009478": {"shares": 214.27, "cost": 2.0162}
}
```

### Key Functions (in fund_tools.py)

| Function | Purpose |
|:---------|:--------|
| `load_user_portfolio()` | Read JSON file, return dict |
| `save_user_portfolio(portfolio)` | Write dict to JSON file |
| `calc_group_actual_weights(fund_data)` | Shares × NAV → group weight % per group |

### Impact on Reports

1. **权重 column in [3]** — Shows `{actual_pct}%` when portfolio data exists, otherwise falls back to `PORTFOLIO_WEIGHTS` target
2. **check_rebalance()** — Uses actual weights, not drift-estimated ones, for rebalance advice
3. **PORTFOLIO_WEIGHTS targets** — Keep in sync with actual allocation intent (updated this session: 新能源 12→6%, 科技/AI 59→55% after user's 50%/25% reductions)

### Update Protocol

When user reports a trade (buy or sell):
1. **ALWAYS update both**: memory (for human-readable context) AND `/tmp/fund_data/_user_portfolio.json` (for code to read)
2. **FAILURE MODE**: Saving trade data only to memory means the code never sees it. The next report will use old PORTFOLIO_WEIGHTS and stale share counts. The user will rightfully complain "I told you but you didn't use it."
3. Calculate remaining shares: `existing_shares - reduction_amount`
4. Save with `save_user_portfolio()` from fund_tools.py
5. If PORTFOLIO_WEIGHTS target % changed significantly due to the trade, update that too
6. Verify next run shows correct actual weights

```python
from fund_tools import load_user_portfolio, save_user_portfolio
p = load_user_portfolio()
p['017103']['shares'] = 121.66  # after 25% reduction
save_user_portfolio(p)
```

### Initial Setup for New Funds

When user adds a new fund to the portfolio:
1. Add to `FUND_CODES` in fund_tools.py
2. Add to appropriate `GROUPS` dict
3. Add to `_user_portfolio.json` with estimated shares based on investment amount ÷ NAV
4. Add to display lists in `monitor_all_funds.py` overnight/other sections if needed

### Fund Removal (清仓卖出)

When user sells a fund entirely:

1. **Remove from `FUND_CODES`** in fund_tools.py — stops data collection
2. **Remove from `_user_portfolio.json`** — weights no longer include it
3. **Remove from `GROUPS` dict** if present — prevents group stats from including it
4. **Update `PORTFOLIO_WEIGHTS`** if group allocation changed
5. **Verify** next run with `python3 monitor_all_funds.py --fast`

**Example** (2026-07-09: user sold 天弘中证医药100C + 天弘创新药精选50ETF联接C after 3 days):
```python
# Remove from FUND_CODES + pop from portfolio
p.pop('001551', None); p.pop('014565', None)
save_user_portfolio(p)
```

## Northbound Fund Data (北向资金)

### Source Chain
1. **Primary**: `data.hexin.cn/market/hsgtApi/method/dayChart/` — real-time intraday data during trading hours (09:30-15:00 CST)
2. **Fallback 1**: **Sina Finance scraper** (`tags.sina.com.cn/finance_beixiangzijin`) — extracts daily aggregate from news feeds. Regex: `r'(昨日|当日|今日)\s*北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` → direction + amount. Works reliably from Oracle ARM.
3. **Fallback 2**: Reads from `/tmp/fund_data/_yesterday_snapshot.json` with `stale=True` (last resort)

### Time-Proximity Matching (Hexin)

`get_northbound_flow()` picks the data point **closest to current time** within a ±120 minute window, not the last non-None value.

```python
# Old: took last non-None (yesterday's 15:00 close)
# New: finds closest to current time within ±120min
for i in range(len(times) - 1, -1, -1):
    if times[i] and hgt[i] is not None and sgt[i] is not None:
        data_minutes = time_to_minutes(times[i])
        if abs(now_minutes - data_minutes) <= 120:
            best_idx = i  # update if closer
use_idx = best_idx if best_idx >= 0 else last_idx
```

### Staleness Detection (Two Layers)
1. **Time-proximity** — `stale=True` when trading hours (9:00-16:00) and data is >60 min old
2. **Date-file persistence** (`/tmp/fund_data/_northbound_date.txt`) — each successful hexin fetch saves `today_str`. Next run, if saved date ≠ today, marks `stale=True` immediately (detects hexin returning yesterday's data)

### Staleness Cross-Check (NEW: 2026-07-09)

`get_northbound_flow()` now includes a **third staleness layer**: when hexin returns data marked as stale AND the total amount matches the previously cached fallback value exactly (±0.001亿), the hexin data is **skipped entirely** — the function falls through to the Sina backup source.

```python
# In the hexin success block:
if result['stale'] and _NB_DATA_FILE.exists():
    prev_nb = json.loads(_NB_DATA_FILE.read_text())
    if abs(prev_nb['total'] - result['total']) < 0.001:
        skip_hexin = True  # total matches cache → stale repeat
        # Falls through to Sina backup
```

**Why this matters**: hexin occasionally returns the SAME stale value multiple days in a row (e.g. -40.38亿 appearing for multiple days even though actual northbound flow changed). Without this check, stale=True data still gets used. With the check, identical stale data is rejected and the Sina backup (which reads from fresh daily news feeds) is used instead.

### Sina Scraper Details (Two-Strategy Regex)
- URL: `https://tags.sina.com.cn/finance_beixiangzijin`
- Response: HTML page with news snippets containing aggregate daily northbound flow
- **Strategy A (exact prefix)**: `r'(昨日|当日|今日)\s*北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` — requires time prefix immediately before "北向资金"
  - Direction: `group(2)` = `卖出` → negative, `买入` → positive
  - Amount: `group(3)` = float
  - Plausibility check: if `abs(total) > 200`亿, discard and fall through to Strategy B
- **Strategy B (broad, last-match)**: `r'北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` — no prefix requirement
  - Finds ALL matches, uses the LAST one (most recent in DOM, likely latest news item)
  - Same direction/amount parsing
  - Plausibility check: if `abs(total) > 200`亿, raises exception and falls through to snapshot fallback
- `source='sina_prefix'` or `source='sina_broad'` in returned dict depending on which strategy matched
- Splits total into hgt≈30%, sgt≈70% (approximate ratio, only total is verified)
- This scraper is essential because hexin API returns **unreliable data** (confirmed: hexin returns different values between calls, and returns stale data matching cached fallback)

### Oracle ARM Data Source Reliability

| Source | Endpoint | Status | Notes |
|:-------|:---------|:-------|:------|
| 天天基金 | fundgz.1234567.com.cn | ⚠️ Intermittent | SSL handshake times out from ARM; curl works. Has retry logic. |
| 腾讯行情 | qt.gtimg.cn | ✅ Stable | Works for indices and ETFs |
| Sina财经 | tags.sina.com.cn | ✅ Stable | HTML page, regex parsing |
| hexin北向 | data.hexin.cn | ⚠️ Unreliable | Returns wrong cumulative data; data structure inconsistent (sgt array length varies) |
| 东方财富API | push2.eastmoney.com | ❌ Blocked | Connection reset from Oracle ARM |

## Operation Suggestion Verification

### Data Flow
1. **Save** — After each run, `_save_suggestion_log()` writes today's group scores + fund suggestions to `/tmp/fund_data/_suggestion_log.json`
2. **Load** — Next run's `_verify_previous_suggestions()` reads yesterday's entry from the log
3. **Compare** — Yesterday's suggestions vs today's actual performance (from `self.group_analyses` and `self.fund_analyses`)
4. **Report** — Prints verification section before the summary:

```
📋 操作建议验证（2026-07-05 → 2026-07-06）

📁 组别操作验证:
| 组别 | 前日建议 | 今日实际 | 判定 |
|:----|:--------|:--------:|:----:|
| 科技/AI | 观望(评分-1) | -1.07% | ✅ 正确 |
| 黄金 | 增持(评分+3) | +0.00% | ❌ 偏差 |

📊 准确率: 86% (6/7)
```

### Group Judgement Logic
- Bearish action (观望/减持) + today_change < -0.3% → ✅ Correct
- Bullish action (增持/关注) + today_change > 0.3% → ✅ Correct  
- 持有 → 🟡 Neutral (not counted in accuracy)
- Anything else → ❌ 偏差

### Fund Judgement Logic
- Bearish rec (减仓/减持/观望) or urgency=高 + today_chg < -0.5% → ✅ Correct
- Bullish rec (增持/关注) + today_chg > 0.5% → ✅ Correct
- 持有 → 🟡 Neutral
- Anything else → ❌ 偏差

## Push Timing Strategy

When doing push tests or scheduled pushes, choose content based on current time:

| Time | Content |
|:----|:--------|
| 06:00-09:00 | 财经早餐 (overnight data + opening predictions) |
| 09:30-11:30 | 盘中速递 (intraday data + sector heatmap) |
| 13:00-15:00 | 午后盘中直击 (afternoon session analysis) |
| 15:00+ | 收盘全盘监测 (monitor_all_funds.py with full 6D analysis) |

## Northbound Fund Data (北向资金)

### Source Chain
1. **Primary**: `data.hexin.cn/market/hsgtApi/method/dayChart/` — real-time intraday data during trading hours (09:30-15:00 CST)
2. **Fallback**: Reads from `/tmp/fund_data/_yesterday_snapshot.json` when hexin fails (common after market close or from Oracle ARM)

### Staleness Detection (Two Layers)
1. **Time-proximity matching** (in `get_northbound_flow()`): picks the data point closest to current time (within ±120 min window), not the last non-None value (which would be yesterday's 15:00 close)
2. **Date-file persistence** (`/tmp/fund_data/_northbound_date.txt`): each successful fetch saves `today_str`. Next run, if saved date ≠ today, marks `stale=True` immediately (detects hexin returning yesterday's data)

`get_northbound_flow()` returns `{'hgt', 'sgt', 'total', 'time', 'stale'}\`
- `stale=True` = data is cached/from snapshot, not real-time
- Report shows `⚠️(缓存)` suffix when stale

### Known Behavior
- Pre-market (before ~08:30 CST): hexin returns yesterday's full day data (marked stale after first cross-day detection)
- Trading hours (09:30-15:00): returns today's real-time intraday data + call auction (09:10-09:30)
- Post-close (after 15:00): returns today's complete day data (fresh until next day pre-market)

### Adding New Indices
To add an overseas index to reports:
1. Add to `OVERNIGHT_SYMBOLS` in `fund_tools.py` — e.g. `'韩国KOSPI': '^KS11'` (Yahoo Finance symbol)
2. Add to the display list in `monitor_all_funds.py` overnight section
3. Pre-formatted tables in `collect_morning_data.py` and `closing_review.py` iterate over `overnight.items()` dynamically — they auto-pick up new entries from step 1

## Score Stability (Hysteresis)

`score_group_action()` in `fund_tools.py` supports a `prev_action` parameter to prevent one-day recommendation flips.

### How it works
1. Raw score is calculated from trend + sector momentum + KOL signals (same as before)
2. `raw_action` is determined from the raw score (same thresholds)
3. If `prev_action` is a directional recommendation (增持/减持/关注/观望) and `raw_action` is in the opposite direction, the flip is **blocked** — action is forced to `'持有'` as a one-day buffer

### Flip rules (blocked transitions)

| prev_action | raw_action | Output | Reason |
|:------------|:-----------|:-------|:-------|
| 增持 | 减持 | 持有 | Day 1 buffer: don't reverse immediately |
| 增持 | 观望 | 持有 | Day 1: from buy to slight bearish → buffer |
| 减持 | 增持 | 持有 | Same, opposite direction |
| 减持 | 关注 | 持有 | Same |
| 关注 | 观望 | 持有 | From bullish → slight bearish → buffer |
| 关注 | 减持 | 持有 | Strong flip → blocked |
| 观望 | 关注 | 持有 | From bearish → slight bullish → buffer |
| 观望 | 增持 | 持有 | Strong flip → blocked |

The `raw_action` value is still returned in the dict (under `'raw_action'` key) for debugging. The output action always shows the stable one.

### Integration points
- `monitor_all_funds.py` loads `prev_action` from `_suggestion_log.json` and passes it
- `collect_morning_data.py` does NOT pass prev_action (no cross-day log loaded)
- When no prev_action is provided, the function behaves identically to the old version

### fund_analyses entry
```python
{
    'code': '017103',
    'name': '大摩数字经济混合C',
    'group': '科技/AI',
    'estimated_change': '-2.59',
    'dimensions': {'D1_今日估值': '大跌-2.59%', 'D2_组别趋势': '...', ...},
    'signals': ['📉 今日大跌', '🚩 组内落后(排名7/7)'],
    'recommendation': '🔴 减仓观望',
    'urgency': '高',  # 高/中/低
    'score': -2.0,
}
```

### group_analyses entry
```python
{
    'group': '科技/AI',
    'avg_change': -1.07,
    'count': 7,
    'score': 0,
    'action': '持有',  # 增持/关注/持有/观望/减持
    'urgency': '低',
    'reasons': [...],
}
```

## Pitfalls

1. **Double emoji in 建议 column** — `rec` field already has emoji prefix. Use `{rec}` alone, NOT `{urg_icon}{rec}`.
2. **Verification data source** — Always use `self.group_analyses` / `self.fund_analyses` for "today's actual" comparison, NOT `get_group_trend()` from file (may not be saved yet for --fast mode).
3. **Log file path** — Fixed at `/tmp/fund_data/_suggestion_log.json`. The directory `/tmp/fund_data/` is created on first save.
4. **Log retention** — Only last 30 days are kept automatically.
5. **Northbound data staleness** — hexin API returns empty response after market close (16:00+) and from Oracle ARM intermittently. Falls back to `_yesterday_snapshot.json` and marks `stale=True`. Report shows `⚠️(缓存)` suffix. Time-proximity matching (closest data point within ±120min of current time) prevents picking yesterday's 15:00 close during today's trading session.
6. **Overnight symbols** — Adding a new index requires TWO changes: (a) `fund_tools.py` `OVERNIGHT_SYMBOLS` dict, and (b) the hardcoded display list in `monitor_all_funds.py` overnight table. Pre-formatted cron tables (morning/closing) iterate dynamically and auto-pick up new symbols from step (a).
7. **Trend window file** — `fund_system_data/_group_trends.jsonl`. Written by other scripts (closing_review.py etc.), not by monitor_all_funds.py.
8. **Sector data in --fast mode** — Phase 2 collection (sectors, northbound, overnight) is skipped. Reports will show "⚠️ 市场总览数据缺失" and may have gaps in volume analysis.
9. **collect_morning_data.py must pass real trend data** — `score_group_action()` call in collect_morning_data.py was passing `[]` (empty list) for trend_data. This caused trend analysis to be entirely skipped in morning reports, making scores inconsistent with monitor_all_funds.py (which passes real `get_group_trend()` data). Fix: pass `get_group_trend(gname, days=3)` instead of `[]`.
10. **009478 gold fund always shows 0% estimated_change** — The fundgz API (天天基金) does not provide real-time NAV estimates for gold-linked funds. `estimated_change` is always 0.00. Fix in `monitor_all_funds.py`: if `code == '009478'` and `abs(change_pct) < 0.01`, substitute with the gold ETF market price (`黄金ETF市场价 / sh518880`) from the quotes dict. D1 label gets suffix `（替代基金估算）` so user knows it's a proxy.
11. **医药 missing from sector_map** — The `sector_map` dict in `score_group_action()` did not include `'医药'`, so医药 sector momentum never affected its score. Fix: add `'医药': '医药'` to sector_map.
12. **`from collections import defaultdict` missing** — When adding new functions in `fund_tools.py` that use `defaultdict`, verify the import exists at the top of the file.
13. **Sina scraper regex fails on weekends** — On non-trading days, news feeds may not have "当日北向资金合计" text. The fallback to snapshot handles this.
14. **Fund data freshness (nav_date)** — `get_fund_value()` now returns a `stale` flag: `stale=True` when `nav_date != today`. Prevents saving yesterday's NAV as today's close.
15. **009478 gold fund proxy** — Always 0% from fundgz API. Fix: substitute with gold ETF (sh518880) from Tencent quotes in `analyze_individual_fund()`.
17. **Export defaultdict** — `from collections import defaultdict` must be at top of `fund_tools.py` when using `defaultdict` in new functions.
18. **Gold correction timing in closing_review.py** — The gold ETF correction for 009478 must be applied to `funds_now` BEFORE the push table is generated (~line 67, right after the morning-data fallback loop), not to `funds_for_snapshot` after the table (~line 388). If too late, the push shows `0.00%` for 中银上海金ETF联接C even though the correction was logged. Fix: add the correction block right after the morning-data fallback loop.
19. **Northbound cross-source discrepancy** — hexin and Sina often return different totals for the same day. Neither is authoritative. The stale-detection cross-check (total matches cached value) prevents identical stale data from hexin, but does NOT resolve active discrepancies. When digging: check Sina page article body (which may have embedded "昨日...北向资金合计净卖出X亿" text not captured by the prefix regex), and East Money data pages (update around 18:00 CST daily). Best practice: log both sources in debug output and let the agent reason about plausibility.
20. **Sina Strategy B was added to catch loose-format totals** — The original regex `r'(昨日|当日|今日)\s*北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` misses entries where there's punctuation between the prefix and "北向资金" (e.g. "昨日，...北向资金合计净卖出11.10亿元"). Strategy B: `r'北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` catches these without prefix requirement, takes the LAST match (most recent in DOM). Always pair with a plausibility check (skip >200亿). Both strategies run in sequence: Strategy A first, Strategy B as fallback.

## Quick Reference Commands

```bash
# Full analysis
python3 /opt/data/scripts/monitor_all_funds.py

# Fast mode (funds + indices only, skip sectors/northbound/overnight)
python3 /opt/data/scripts/monitor_all_funds.py --fast

# JSON output (suppresses collection logs)
python3 /opt/data/scripts/monitor_all_funds.py --json

# Funds-only diagnostics
python3 /opt/data/scripts/monitor_all_funds.py --funds-only

# Groups-only analysis
python3 /opt/data/scripts/monitor_all_funds.py --groups-only

# View suggestion log (verification history)
cat /tmp/fund_data/_suggestion_log.json | python3 -m json.tool
```
