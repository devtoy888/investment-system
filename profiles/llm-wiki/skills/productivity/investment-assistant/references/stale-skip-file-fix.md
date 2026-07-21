# Stale Skip File Bug (2026-07-06)

## Root Cause

Three pre-scripts (`collect_morning_data.py`, `collect_noon_data.py`, `closing_review.py`) write a `_*_skip.txt` file when `is_trading_day()` returns False. On the **next trading day**, `is_trading_day()` returns True, so the pre-script does NOT write a new skip file — but the OLD skip file from yesterday is still sitting in `/tmp/fund_data/`.

The LLM cron prompt reads: 
```
如果 /tmp/fund_data/_closing_skip.txt 存在且非空，输出"⏭️ 非交易日，跳过推送"并结束。
```

Since the stale file still exists, the LLM stops before reading any collected data → **false "非交易日" on a trading day**.

## Fix Applied (2026-07-06)

All three pre-scripts now clean old skip files at the very start, before the `is_trading_day()` check:

```python
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

# Clean stale skip files from previous non-trading day
for skip_file in ['_closing_skip.txt', '_skip.txt']:  # <-- varies by script
    f = SUMMARY_DIR / skip_file
    if f.exists():
        f.unlink()
```

Files patched:
- `collect_morning_data.py` — cleans `_skip.txt`, `_closing_skip.txt`
- `collect_noon_data.py` — cleans `_noon_skip.txt`, `_skip.txt`, `_closing_skip.txt`  
- `closing_review.py` — cleans `_closing_skip.txt`, `_skip.txt`

## Affected skip files

| Script | Skip File | Cleaned by |
|--------|-----------|------------|
| `collect_morning_data.py` | `_skip.txt` | Self + noon + closing |
| `collect_noon_data.py` | `_noon_skip.txt` | Self |
| `closing_review.py` | `_closing_skip.txt` | Self + morning |

## Detection

If a cron push says "非交易日" on an obvious trading day:
1. Check `stat /tmp/fund_data/_closing_skip.txt` — if `Modify` timestamp is from a PREVIOUS day, it's the stale file bug
2. Run the pre-script manually to trigger the cleanup
3. Confirm fix: re-run the cron job or manually push
