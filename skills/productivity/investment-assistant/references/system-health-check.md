# System Health Check Checklist

Run this when the user asks for a status update, alignment, or "当前最新阶段".

## 1. Data Sources (fund_tools.py)

| Function | Status | Verification |
|----------|--------|-------------|
| `get_tencent_quote(code)` | ✅ Editable funds (FUND_CODES) + indices (QUOTES) | `get_all_quotes()` returns ≥ 5 results |
| `get_fund_value(code)` | ✅ Fund codes verified by API | `get_all_funds()` succeeds for ≥ 12/18 codes |
| `get_overnight_quotes()` | ✅ Yahoo Finance | Real-time from query1.finance.yahoo.com |
| `get_sector_quotes()` | ✅ Tencent batch (10 ETFs) | Batch API: qt.gtimg.cn/q=code1,code2,... |
| `get_market_overview()` | ✅ East Money + Tencent | f169/f170 rise/fall + sh000002/sz399001 turnover |
| `get_northbound_flow()` | ✅ Hexin API (auto-retry) | data.hexin.cn/market/hsgtApi/method/dayChart/ |
| `get_user_weibos(uid)` | ✅ Desktop API (cookies) | weibo.com/ajax/statuses/mymblog?feature=1 |
| `get_weibo_comments(id)` | ✅ aj/v6/comment/big (HTML parsing) | Triggered only for signal posts |
| `track_source()` | ✅ JSONL logger | fund_system_data/_source_availability.jsonl |
| `is_trading_day()` | ✅ Static holidays + weekday | CHINESE_HOLIDAYS_2026 set |

## 2. Pre-Collection Scripts

Verify each script writes files in this order (lightweight BEFORE fund collection):

### collect_morning_data.py (08:00)
```
overnight → market → sector → overview → northbound → fund → groups → KOL → comments
```

### collect_noon_data.py (11:35)
```
market → sector → overview → northbound → fund → groups → KOL
```

### closing_review.py (16:00)
```
sector → overview → northbound → fund → groups → comparison → accuracy
```

**Run-time check:** Each script should complete in < 60s with `timeout 90 python3 scripts/...py`. If > 90s, the fund parallelization may need fixing.

## 3. Cron Prompts

| Cron | Prompt File Count | Table Templates | Empty-Data Skip |
|------|:-----------------:|:---------------:|:---------------:|
| 今日参考 (d7b0a) | 8 files + _skip | ✅ 外盘/A股/板块/北向/持仓 | ✅ |
| 盘中速递 (d29e6) | 7 files + _noon_skip | ✅ 大盘/板块/成交/北向/持仓 | ✅ |
| 收盘复盘 (7a165) | 6 files + _closing_skip | ✅ 收盘/板块/验证/北向 | ✅ |

**Verification:** Read the actual output from the most recent cron run via `session_search()`. Confirm tables are used (not prose text stacking). Key test: check the format matches the templates in the cron prompt.

## 4. Run-time Test

```bash
# Clean slate
rm -rf /tmp/fund_data/

# Run all three
time python3 /opt/data/scripts/collect_morning_data.py
time python3 /opt/data/scripts/collect_noon_data.py
time python3 /opt/data/scripts/closing_review.py

# Verify file count
ls /tmp/fund_data/
```

**Target:** All three finish under 90s wall time, individual fund success rate ≥ 12/18.

## 5. Cron Schedule Verification

| Push | UTC Schedule | CST Time | Status |
|------|:-----------:|:--------:|:------:|
| 今日参考 | 0 0 * * 1-5 | 08:00 | ✅ |
| 盘中速递 | 35 3 * * 1-5 | 11:35 | ✅ |
| 收盘复盘 | 0 8 * * 1-5 | 16:00 | ✅ |
| 周末外盘速报 | 0 1 * * 6 | 09:00 | ✅ |
| 数据源验证 | 0 2 * * 6 | 10:00 | ✅ |

## 6. Common Failure Patterns

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Some fund codes missing (024418, 026421, 026200 etc.) | Per-request timeout (5s) at fundgz.1234567.com.cn | Already parallelized — individual timeouts don't block others |
| Northbound flow empty | hexin API timeout | Auto-retry built in; if persistent, check network to data.hexin.cn |
| KOL posts from months ago | feature=0 in API params | Must use `feature=1` (only shows recent images/text, not archived) |
| Low-value KOL in push | signal density < 10% | Remove from KOLS dict in fund_tools.py |
| All fund values = 0.00%, estimated_change absent | Non-trading hours | Expected; fund API returns stale data after 15:00 CST |
| Script > 120s cron timeout | Serial collection | Check ThreadPoolExecutor is applied in all three get_all_* functions |

## 7. Version Check

Record last verification date and any changes since:

| Date | Change | Verified By |
|------|--------|:-----------:|
| 2026-06-30 | Parallel fund collection (ThreadPoolExecutor, max_workers=5) | Run test: 37s/48s/45s all 3 scripts ✅ |
| 2026-06-30 | Data sources: sector ETFs, market breadth, turnover, northbound | Source check + API call test ✅ |
| 2026-06-30 | Cron prompt formatting fix (markdown tables) | session_search crons ✅ |

## 8. Phase-Gate Progression Check

Run this to determine which optimization phases are ready to advance. The investment-assistant system evolves through 3 phases after the core operation recommendation system (维度C) was deployed on 2026-07-01.

### Required Checks

```bash
# 1. Verify operation plan/eval files exist
ls -la /tmp/fund_data/_operation_plan.txt /tmp/fund_data/_operation_eval.txt

# 2. Count trend data accumulation (distinct trading days)
python3 -c "
import json
dates = set()
with open('/opt/data/fund_system_data/_group_trends.jsonl') as f:
    for line in f:
        d = json.loads(line)['_date']
        dates.add(d)
print(f'Distinct trading days with trend data: {len(dates)}')
print(f'Dates: {sorted(dates)}')
"

# 3. Group consistency check
python3 scripts/check_group_consistency.py
```

### Phase Gate Conditions

| Phase | Condition | Status Check | Current |
|:------|:----------|:-------------|:-------:|
| 🔴 Phase 2 | 操作建议系统稳定运行 >= 5个交易日 | `python3 -c "print(len(set(...)))"` (from #2) >= 5 | ✅ |
| 🟡 Phase 3 | 趋势数据积累 >= 10个交易日 | Same check >= 10 | ❌ |
| 🟢 Phase 4 | 操作建议文件已生成 >= 5个交易日 | ls check from #1 + date count >= 5 | ✅ |

### Per-Check Reports Template

**Phase 2 (盘中速递操作提示):**
- Files exist ✓/✗ + last modified dates
- Trend data days count
- What to do next (e.g. "add `_noon_operation.txt` generation to `collect_noon_data.py` + update noon prompt")

**Phase 3 (未持仓候选基金):**
- Sector ETF data days count
- Current strongest sectors (brief table)
- ETA in trading days

**Phase 4 (操作建议跟踪验证):**
- Operation files days count  
- What to implement: `record_action()` + `verify_actions()` in fund_tools.py

### Stale Group Reference Check

After any fund group removal, verify ALL scripts are consistent:

```bash
# Replace REMOVED_GROUP with the actual removed group name
grep -rn 'REMOVED_GROUP' /opt/data/scripts/*.py | grep -v '已清仓\|已移除'
```

Expected targets in fund_tools.py: `PORTFOLIO_WEIGHTS`, `GROUP_ACTION_RULES`, `score_group_action()` sector_map
Expected targets in pre-scripts: `closing_review.py` group_order, `collect_morning_data.py` group_order
