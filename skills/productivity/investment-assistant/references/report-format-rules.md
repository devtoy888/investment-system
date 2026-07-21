# Report Format Optimization Rules (2026-07-06)

## Golden Rule: Optimize Structure, NEVER Trim Content

When reformatting a no_agent script or AI prompt from plain-text to markdown tables:

✅ **DO:** Convert prose rows to `| col1 | col2 | col3 |` tables
✅ **DO:** Add column headers and alignment markers
✅ **DO:** Replace text separators (`───`×72) with compact separators (`═══`×56)
✅ **DO:** Add emoji prefixes to improve readability of detail sections

❌ **DON'T:** Remove any data dimension (D1–D5 must all stay)
❌ **DON'T:** Limit the number of displayed items (show all 15 abnormal items, not top 10)
❌ **DON'T:** Remove columns that existed in the original (volume/turnover data)
❌ **DON'T:** Combine multiple data points into one line unless user confirms

## Sector/Ranking Tables: Always Add Amplitude + Volume Data

When displaying sector or fund ranking tables, include:
- Change % (always present)
- Amplitude % (for volatility context)
- Volume data (成交额 or 成交量)
- Signal label (放量/温和/缩量 + direction)

## Detail Sections: Full Format

For per-fund or per-item detailed sections, use this emoji-prefixed format (all 5 dimensions):

```
**Fund Name** ⚠️/✅
  📅 今日: D1 value
  📊 趋势: D2 value
  📊 组内: D3 value (including rank N/M)
  🔗 关联: D4 value
  📈 量价: D5 value
  🚩 信号: signal1 | signal2
```

Never skip D3 (组内表现) or D4 (关联标的) — even if they seem redundant. The user relies on ALL five dimensions for decision-making.

## Heat Bars in Sector Tables

When showing sector change %, add a Unicode heat bar alongside the percentage:

```python
abs_pct = min(abs(cp), 5)
filled = int(abs_pct / 5 * 10)
bar = '█' * filled + '░' * (10 - filled)
# Output: | 🔴 半导体 | +0.84%█████░ | 6.4% | 放量 📈 |
```

## Summary Section

For the analysis summary, use a single direction emoji line:
```
🟢/🔴/🟡 偏多:N 中性:N 偏空:N (共N只)
```
Then list group rankings and alerts. Keep compact but complete.
