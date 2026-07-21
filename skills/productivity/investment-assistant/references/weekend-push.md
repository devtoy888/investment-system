# Weekend Overseas Market Push (周六外盘速报)

> v1: 2026-06-26 · v2: 2026-07-04 (持仓影响 + sparkline + 信号方向)

## Purpose

Friday US market trades 21:30–04:00 CST (Fri→Sat). Previously, this data was not pushed until Monday 08:00 — wasting 2 days of advance planning time for the user. A light Saturday push lets the user mentally prepare for Monday over the weekend.

## Cron Configuration

| Field | Value |
|-------|-------|
| Name | 周末外盘速报 |
| Schedule | `0 1 * * 6` (UTC) = 09:00 CST Saturday |
| Type | `no_agent=true` |
| Script | `collect_weekend_data.py` |
| Delivery | `qqbot:<chat_id>` |

## Script Design v2 (`collect_weekend_data.py`)

Located at `/opt/data/scripts/collect_weekend_data.py` (~215 lines)

### Sections (in order)

| # | Section | Description | Format |
|---|---------|-------------|--------|
| 1 | 🌙 外盘收盘 | Yahoo 6 symbols (DJI, SPX, IXIC, gold, USD, HSI) | Emoji list |
| 2 | 📊 持仓影响评估 | Auto-maps overseas data → portfolio groups with threshold rules | Text analysis |
| 3 | 📈 一周回顾 | Week-over-week overseas comparison (saved to `_weekend_prev.json`; starts empty, real data from 2nd run) | **Markdown table** |
| 4 | 📊 分组本周趋势 | 5-day group trend with **Unicode sparkline** (`▁▂▃▄▅▆▇█`) | **Markdown table** |
| 5 | 📰 博主信号 | KOL latest post + signal direction + black talk interpretation | Structured |
| 6 | 📌 周一关注 | Data-driven outlook based on gold/nasdaq performance | Bullet list |

### v2 Enhancements

#### Unicode Sparkline (分组本周趋势)

Converts 5 daily values into a 8-step Unicode bar chart for instant visual recognition:

```python
spark_chars = ['▁','▂','▃','▄','▅','▆','▇','█']
rng = max(vals) - min(vals)
spark = ''.join(spark_chars[min(int((v - min(vals)) / rng * 7), 7)] for v in vals)
```

Output example:
```
| 分组 | 走势 | 本周幅度 |
|:----|:---:|:--------:|
| 黄金 | ▁▂▇▇█ | -1.1% → +1.4% 📈 持续上行 |
| 科技/AI | ▇▆▁▁█ | -5.3% → -0.1% 📈 跌幅收窄 |
```

**CRITICAL**: The user specifically rejected raw text `date=value → date=value` format. Always use sparkline + range summary instead.

#### Overseas-to-Portfolio Impact Mapping

Rules defined in `OVERNIGHT_IMPACT_MAP` constant:

| Overseas Symbol | Portfolio Group | Coefficient | Notes |
|----------------|:---------------:|:-----------:|-------|
| 黄金期货 | 黄金 | 1:1 | Direct correlation |
| 纳斯达克 | 科技/AI | 0.4x weak | A-share tech has independent momentum |
| 标普500 | 大盘情绪 | 0.3x weak | General sentiment |
| 美元指数 | 资源/周期 | -0.5x inverse | Strong USD = commodity pressure |
| 道琼斯 | 大盘方向 | 0.2x weak | Used as primary 大盘 indicator |
| 恒生指数 | 恒生科技方向 | 0.3x weak | HK tech reference |

Threshold-based descriptions (gold example):
- `pct > 1` → "金价大涨 → 黄金组显著利好"
- `pct > 0.3` → "金价上涨 → 黄金组偏多"
- `pct > -0.3` → "金价微调 → 影响有限"
- else → "金价下跌 → 黄金组承压"

#### KOL Signal Direction Scoring

Simple keyword-based function `score_signal_direction()`:

```python
bull = ['看多','买入','加仓','增持','机会','利好','右侧','地板','吃肉']
bear = ['看空','卖出','减仓','减持','风险','利空','出货','砸盘','天花板']
```

Output: 🔴 偏多, 🟢 偏空/提示风险, 🟡 中性/观察

#### Week-over-Week Comparison

Saves current overseas data to `/tmp/fund_data/_weekend_prev.json` on each run. Reads it on next run to produce comparison table:

```
| 品种 | 上周 | 本周 | 变化 |
|------|:---:|:---:|:----:|
| 🔴 道琼斯 | +0.84% | +1.14% | 📈 扩大涨幅 |
```

First run always shows "➖ 基本持平" (baseline saved). Real comparison starts from 2nd run.

### Script Functions

| Function | Purpose |
|----------|---------|
| `assess_impact(name, q, quotes)` | Returns (label, emoji, description) via Overnight Impact Map |
| `score_signal_direction(text)` | Returns (emoji, direction string) via keyword matching |
| `sparkline(vals, min_v, max_v)` | Inline — converts float list to Unicode bar sequence |

### Edge Cases

| Case | Behavior |
|------|----------|
| Friday was a Chinese holiday | Yahoo returns last close before holiday. Still pushes |
| KOL didn't post over weekend | Shows "（周末暂无博主新信号）" |
| Yahoo API fails | Shows error per symbol, still delivers partial data |
| No prev data for week comparison | First run saves baseline, shows "基本持平" |
| All values equal (flat line) | Sparkline defaults to ▄▄▄▄▄ |
