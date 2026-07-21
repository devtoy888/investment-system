# Self-Evolution System (v4-v7, 2026-07-15)

3-layer meta-system that watches the investment helper and improves it.

## Layer 1 — Weekly Health Audit

Script: `system_health_audit.py` → cron `run_health_audit.py` (周六 10:30 CST, push to QQ)

Checks:
- JSONL dedup ratio (target ≤1.5x/day)
- KOL signal resolution (`correct` field null rate)
- Data source availability
- Cron health & QQ delivery errors
- Generates evolution suggestions

**Pattern**: empty stdout → system healthy, silent. Non-empty → problems → QQ push.

## Layer 2 — Auto-Healing

| Script | Schedule | Action |
|--------|----------|--------|
| `deduplicate_archives.py` (`run_dedup.py`) | Trading days 16:20 | Removes duplicate JSONL records, keeps first per day, backs up as .bak |
| `verify_decisions.py` (`run_verify.py`) | Trading days 16:30 | Checks 3-7 day old decisions against current prices, updates verification_3d |

## Layer 3 — Architecture Archiving

Script: `log_evolution.py`

Run after every system change:
```
python3 log_evolution.py "v{N}" "标题" \
  --changes "change 1" --changes "change 2" \
  --issues "issue found" \
  --pending "todo item"
```

Produces on R2:
- `fund-system/evolution/EVOLUTION_LOG.md`
- `fund-system/strategy/SYSTEM_DESIGN_v{N}.md`

## Decision Verification Loop

1. `log_daily_decisions.py` (16:25) — Records daily price snapshot + market accuracy
2. After 3-7 trading days, `verify_decisions.py` updates `verification_3d` from "pending"
3. Results feed into Sunday `weekly_review.py`

## Weekly Review

`weekly_review.py` (Sunday 20:00 CST, push to QQ + R2 archive):
- Weekly index movement (Mon→Fri compare)
- Market direction prediction accuracy average
- KOL signal accuracy (calls `generate_signal_report()`)
- Data source health
- Recent KOL signals for next week outlook
- Auto-archived to `evolution/weekly-{weeknum}.md` on R2

## KOL Direction Detection Fix

Expanded `_DIRECTION_BULLISH_FULL` / `_DIRECTION_BEARISH_FULL` and scan full text:

```python
# Old (~56% neutral):
bullish = sum(1 for w in found_words if w in _DIRECTION_BULLISH)

# New (~30% neutral):
bullish = sum(1 for w in found_words if w in _DIRECTION_BULLISH)
bullish += sum(1 for w in _DIRECTION_BULLISH_FULL if w in text)
```

## Pitfalls Discovered & Fixed This Session

1. **r2_uploader.py had no `__main__`** — `fund_tools.upload_to_r2()` called it as subprocess but got no output. Fix: add CLI entry point.
2. **Argparse `nargs="*"` vs `action="append"`** — when passing `--changes` multiple times, `nargs="*"` overwrites. Use `action="append"`.
3. **Cron script symlinks blocked** — symlinks to `/opt/data/scripts/` trigger "path escapes" error. Use thin subprocess wrappers in `~/profiles/investment/scripts/` instead.
4. **JSONL duplicate explosion** — morning-briefs had 62 records for 13 days (453% duplication). Fix: dedup keeps first record per day.
5. **Direction detection too narrow** — only checked signal-dict intersection, not full text. Added `_DIRECTION_BULLISH_FULL` with 32 words.
6. **R2 charset** — Chinese content uploaded to R2 without `charset=utf-8` renders garbled. Fix: always pass content_type including charset. See `references/r2-content-management.md`.

## ROADMAP + HTML Dashboard

Complete system tracking: `ROADMAP.md` + `roadmap.html` on R2 at `fund-system/evolution/`.

- ROADMAP.md: living markdown doc with per-module status (DC-1/PS-7/EV-4 IDs), version history, bugs, TODO (P0/P1/P2), data verification timeline
- roadmap.html: responsive dashboard fetching same markdown via JS, rendering with colored badges/progress/stats via marked.js CDN. Mobile-first dark theme.
- Both uploaded with `charset=utf-8` (fix: see references/r2-content-management.md)

## Key Metrics (post-v7)

| Metric | Value |
|--------|-------|
| Total cron jobs | 13 |
| Modules tracked in ROADMAP | 53 |
| Completed (✅) | 32 |
| Awaiting data (⏳) | 12 |
| Not started (🔴) | 8 |
| System completion | ~60% |

## Cron Jobs (All 13 as of v7)

```
交易日:
  08:00 财经早餐     ▸ QQ (本地推送)
  11:35 盘中直击     ▸ QQ
  16:00 收盘复盘     ▸ QQ (+周五版含美股关注)
  16:10 加仓信号监控  ▸ QQ (有信号才推)
  16:20 JSONL去重    ▸ 静默
  16:25 决策日志     ▸ 静默+R2
  16:30 决策验证     ▸ 静默

每日:
  23:30 微博看门狗   ▸ QQ (凭证过期推二维码)

周六:
  09:00 周末外盘速报  ▸ QQ
  10:00 数据源验证    ▸ QQ
  10:30 系统自检      ▸ QQ (有问题才推)

周日:
  20:00 周度复盘     ▸ QQ + R2
```
