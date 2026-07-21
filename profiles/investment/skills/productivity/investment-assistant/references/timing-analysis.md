# Timing Analysis — US/A-Share Time Gap

> Analyzed 2026-06-26 | Based on EDT summer (UTC-4) → CST (UTC+8)

## Time Zone Foundation

```
US market:  09:30 ET = 21:30 CST  →  16:00 ET = 04:00 CST (+1 day)
A50 night:  17:00-05:15 CST (+1 day)
```

## Data Freshness by Day

| Day | 08:00 Push | Freshness | Issue |
|:---:|------------|:---------:|-------|
| Tue–Fri | US data from ~4h ago | ✅ Fresh | Normal operation |
| Mon | US data from 76h ago (Sat 04:00) | ❌ Stale | **Must reframe: never say "隔夜"** |
| Sat | Friday US data (04:00 Sat) lost | ❌ Wasted | **Add Saturday push** |
| Fri PM | US opens at 21:30 tonight | 🟡 Missing | **Add preview to closing review** |

## Monday 08:00 Fix

**Rule: Never write "隔夜外盘" on Monday.**

Instead:
1. Use "🌙 上周五外盘关盘（周末无交易）"
2. Supplement with `web_search` for weekend events → include "📰 周末大事" section
3. Mark stale data clearly — don't pretend it's fresh
4. KOL posts from Saturday/Sunday are valuable (may include Monday outlook)

## Friday 16:00 Fix

Append a "🌙 今晚美股关注" section:
```
🌙 今晚美股关注
● 21:30 美股开盘
● 关注科技股/黄金/美元走势
● 若有大幅波动，本周末将推送外盘速报
```

## Saturday 09:00 New Push

See `references/weekend-push.md` for full implementation details.

## Winter Time Transition

When US switches from EDT to EST (usually Nov):
- EDT: US open 21:30, close 04:00 CST
- EST: US open 22:30, close 05:00 CST
- The 1-hour shift may require re-evaluating push times
- China doesn't observe DST, so the gap grows by 1 hour in winter

## Key Design Principle

All three daily pushes form a single decision loop:
```
08:00 → "What's my plan today?"      (set thesis)
11:35 → "Is the thesis holding?"     (verify in real-time)
16:00 → "Was the thesis right?"      (close loop)
```
The Saturday push breaks this loop intentionally — it's a reference card, not a decision trigger.
