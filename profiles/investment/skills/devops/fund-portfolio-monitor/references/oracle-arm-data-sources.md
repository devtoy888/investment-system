# Oracle ARM Data Source Reliability

Status as of 2026-07-09. Environment: Oracle ARM (Ampere A1, 2C11G45G), China mainland, Docker.

## Fund Data

| Source | URL | Status | Notes |
|:-------|:----|:-------|:------|
| 天天基金 | `fundgz.1234567.com.cn/js/{code}.js` | ⚠️ **Intermittent** | SSL handshake times out from Python requests on ARM. Works with curl. Has 1 retry in `get_fund_value()`. Fields: `dwjz`=昨日净值, `gsz`=估算净值, `gszzl`=估算涨跌%, `jzrq`=净值日期. **009478 (中银上海金) always returns gszzl=0.00** — gold-linked fund has no daily estimate. Must substitute with 黄金ETF市场价 (sh518880/sz159934) from Tencent quotes. |
| 东方财富历史净值 | `fund.eastmoney.com/pingzhongdata/{code}.js` | ✅ Stable | Large JS payload (50KB+), `Data_netWorthTrend` contains historical NAV. Not suitable for real-time. |

## Market Quotes

| Source | URL | Status | Notes |
|:-------|:----|:-------|:------|
| 腾讯行情 | `qt.gtimg.cn/q={code}` | ✅ **Stable, fast** | Preferred for all real-time quotes. Codes: sh000001=上证, sz399006=创业板, sh518880=黄金ETF. Timeout 5s. |
| Yahoo Finance | Yahoo API | ✅ Stable | Used for overseas indices via `_yahoo_quote()`. Slower but reliable. |

## Northbound Fund Flow

| Source | URL | Status | Notes |
|:-------|:----|:-------|:------|
| hexin | `data.hexin.cn/market/hsgtApi/method/dayChart/` | ⚠️ **Unreliable** | Returns **different data between calls** (confirmed: same endpoint returned sgt=-31.10 and sgt=+379.75 minutes apart on 2026-07-09). `sgt` array length varies (35 vs 262). **Not trustworthy for critical analysis.** |
| 新浪财经 | `tags.sina.com.cn/finance_beixiangzijin` | ✅ **Stable** | HTML page with news snippets. Two-strategy regex: **(A)** `r'(昨日\|当日\|今日)\s*北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` for prefix-tagged entries; **(B)** `r'北向资金\s*合计\s*净([买卖出]+)\s*([\d.]+)\s*亿'` broad catch-all, takes LAST match (most recent). Both have >200亿 plausibility gate. |
| 东方财富 | `push2.eastmoney.com/api/qt/kamt.kline/get` | ❌ **Blocked** | Connection reset from Oracle ARM. |

## Sector Data

| Source | URL | Status |
|:-------|:----|:-------|
| 腾讯行情 | `qt.gtimg.cn/q={codes}` | ✅ Stable, batch query |
| 同花顺 | `data.10jqka.com.cn` | ❌ Blocked |

## Priority Chain in Code

### Northbound (three-layer staleness)
```
hexin ──┬── stale=True ──┬── total matches cached ──→ Sina scraper (A→B) ──→ snapshot (stale)
        │                └── total diff from cache ──→ use hexin
        └── stale=False ──→ use hexin
```

**Layer 1 — Time proximity**: During trading hours (9:00-16:00 CST), if hexin data is >60 min older than current time, mark stale=True.

**Layer 2 — Date file**: `_northbound_date.txt` stores the date of last successful hexin fetch. If saved date ≠ today, mark stale=True (catches hexin returning yesterday's close).

**Layer 3 — Cache-total cross-check (2026-07-09)**: When hexin data is stale AND the total amount exactly matches the previously cached `_northbound_fallback.json` value (±0.001亿), hexin is **skipped entirely** — falls through to Sina backup. This prevents hexin from serving the same stale number (-40.38亿) multiple days in a row.

**Sina Strategy**: First tries Strategy A (exact prefix match with "当日/昨日/今日"). If result >200亿 (implausible), falls to Strategy B (broad match, takes last occurrence). If Sina also fails, falls to yesterday's snapshot with stale=True.

### Fund NAV (gold proxy)
```
fundgz ──┬── 009478 + gszzl=0.00 ──→ substitute with 黄金ETF市场价 change_pct
         └── other codes ──→ use as-is
```

**Gold ETF proxy (009478)**: The fundgz API always returns gszzl=0.00 for gold-linked funds because the fund's underlying assets (physical gold ETFs) are not in the daily estimation model. Must substitute the estimated_change with the gold ETF market price (from Tencent quotes). Applied at TWO points:
1. **In `closing_review.py`**: right after morning-data fallback (~line 67) — BEFORE push table generation. Previously was applied too late (after table gen) causing 0.00% in the push.
2. **In `monitor_all_funds.py`**: in `analyze_individual_fund()` — D1 label gets suffix `（替代基金估算）`.

### Overseas Indices
```
Yahoo Finance (get_overnight_quotes)
```
