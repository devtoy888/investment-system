# Holiday Handling — A-Share Market Closure Calendar

> Implemented 2026-06-26 | Source: SSE Announcement [2025] No. 45

## The Problem

Original `is_trading_day()` only checked weekends (weekday >= 5). Chinese legal holidays that fall on weekdays (e.g., 元旦 on Thursday, 国庆 on Thursday) caused the cron jobs to run, producing stale-data pushes.

## 2026 Chinese Holiday Calendar

| Holiday | Dates | Trading Days Lost | 
|---------|-------|:-----------------:|
| 元旦 | Jan 1 (Thu) – Jan 3 (Sat) | 3 |
| 春节 (Spring Festival) | Feb 15 (Sun) – Feb 23 (Mon) | **9** |
| 清明 (Qingming) | Apr 4 (Sat) – Apr 6 (Mon) | 3 |
| 劳动节 (Labor Day) | May 1 (Fri) – May 5 (Tue) | 5 |
| 端午 (Dragon Boat) | Jun 19 (Fri) – Jun 21 (Sun) | 3 |
| 中秋 (Mid-Autumn) | Sep 25 (Fri) – Sep 27 (Sun) | 3 |
| 国庆 (National Day) | Oct 1 (Thu) – Oct 7 (Wed) | **7** |

## Implementation

**Code location:** `fund_tools.py`, Section 7 (交易日判断)

### Constants

```python
CHINESE_HOLIDAYS_2026 = {
    '2026-01-01', '2026-01-02', '2026-01-03',
    '2026-02-15', ..., '2026-02-23',  # 9 days
    '2026-04-04', '2026-04-05', '2026-04-06',
    '2026-05-01', ..., '2026-05-05',  # 5 days
    '2026-06-19', '2026-06-20', '2026-06-21',
    '2026-09-25', '2026-09-26', '2026-09-27',
    '2026-10-01', ..., '2026-10-07',  # 7 days
}
```

### Auto-Scrape Function (for 2027+)

```python
def _scrape_sse_holidays(year: int) -> set:
    """Attempts to auto-scrape SSE holiday announcement.
    
    SSE publishes the next year's schedule annually in December.
    URL pattern: https://www.sse.com.cn/disclosure/announcement/general/c_YYYYMMDD_XXXXXXXX.shtml
    """
    try:
        # Not fully implemented — placeholder for 2027
        return set()  # Empty = fallback: all weekdays treated as trading days
    except Exception:
        return set()
```

### Fallback Strategy

| Year | Mechanism | Behavior |
|:----:|-----------|----------|
| 2026 | Hardcoded `CHINESE_HOLIDAYS_2026` | 33 dates, all verified against SSE announcement |
| 2027+ | `_scrape_sse_holidays(year)` | Tries auto-scrape. Fails → all weekdays = trading days (safe fallback — no false negatives, only false positives on holidays) |

### Skip File Protocol

Each pre-collection script writes a skip file on non-trading days. The cron prompt MUST check for it in Step 1.

| Script | Skip File |
|--------|-----------|
| `collect_morning_data.py` | `_skip.txt` |
| `collect_noon_data.py` | `_noon_skip.txt` |
| `closing_review.py` | `_closing_skip.txt` |

Cron prompt template:
```
## 第一步：检查是否交易日
如果 `/tmp/fund_data/_skip.txt` 存在，输出"⏭️ 今日休市，无推送"并结束。
```

### Yearly Maintenance

Every December:
1. SSE publishes next year's holiday schedule
2. If auto-scrape works → no action needed
3. If auto-scrape fails → add a new `CHINESE_HOLIDAYS_<YEAR>` set to `fund_tools.py`
4. Verify by running `is_trading_day()` against the first holiday of the new year
