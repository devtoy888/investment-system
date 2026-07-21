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
- 唐史主任司马迁 / 小浣熊1230 / KOL signal verification for fund choices

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
