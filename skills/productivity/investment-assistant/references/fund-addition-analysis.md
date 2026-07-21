# Fund Addition Analysis Framework

## When the user asks "Should I add [sector] funds based on KOL signals?"

### 5-Step Decision Framework

**Step 1: Scan KOL posts for explicit buy signals (not just mentions)**
- Does the KOL say "买" / "加仓" / "搞" / "接" / "机会" regarding this sector?
- Or is it just analysis/observation? (e.g. "医药动了一下" = observation, not buy signal)
- Check the KOL's CURRENT MOOD: are they bullish overall or defensive?
  - Signal: "刷新最大单日亏损" + "从此再无 尽多头义务" + "少挨鞭子" = **NOT a buying mood**
  - Signal: "材料还行，拉回来很快" = **specific subsector positive, but defensive posture**

**Step 2: Check sector performance data**
- Current trend: Is it outperforming or underperforming the market?
- Volume: Is there real money moving in?
- Relative strength vs other sectors
- Use sector data from `get_sector_quotes()` and trend records from `get_group_trend()`

**Step 3: Assess KOL's current overall posture**
- This is the MOST IMPORTANT step. A KOL can like a sector but be in reduction mode.
- Recent signals from 主任 (2026-07-02/03):
  - "刷新史上最大单日亏损" → defensive
  - "用几个交易日调整持仓，使持仓达到出行可以不用太看的水平" → reducing exposure
  - "降低下半年收益率预期" → lowering expectations
  - "质地好的下跌固然是机会" → selective, not broad buying

**Step 4: Check portfolio overlap**
- Does an existing fund already cover this sector?
- Example: 华夏半导体材料设备ETF联接C(024418) covers both semiconductor materials AND equipment.
- Map the proposed fund to existing groups (科技/AI, 黄金, 资源/周期, 新能源)

**Step 5: Output tiered priority**

| Tier | Label | Meaning |
|:----:|:----:|---------|
| 🟢 | Worth considering | KOL bullish + sector momentum + no overlap |
| 🟡 | Monitor only | KOL mentions but no clear buy signal |
| 🔴 | Skip for now | KOL defensive / sector weak / already covered |

### Common Pitfalls

1. **Don't fabricate thresholds.** If you say "wait for a 3% rally", have data to back it (historical vol, RSI). Otherwise say "I don't have enough data."
2. **Use price-drop triggers, not rally triggers.** "Buy back if drops Y% more" not "wait for X% gain."
3. **Don't exaggerate T+1 cost.** Fund pricing is by end-of-day NAV on trade date. T+1 only affects cash settlement (华夏 T+1, 大摩 T+2). User misses at most 1 day.
4. **KOL mood trumps sector signal.** A KOL naming a sector while in defensive mode ("最大亏损, 减仓, 降预期") = subsector interest but timing is risky.
5. **Multi-sector comparison: use a structured output table.** When user asks about 3+ sectors at once (e.g. 机器人/商业航天/金属/医药), create a comparison table: KOL mentions / sector trend / portfolio overlap / add now flag. Never free-form list each sector. Mark missing data clearly (e.g. if the sector isn't in monitored ETFs, say "未追踪" not "0%"). Sort by strength of signal, not by user's question order.
