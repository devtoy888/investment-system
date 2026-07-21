# 数据源降级策略（3级回退）

`collect_morning_data.py` 在获取昨日行情数据时按以下优先级：

```
① 收盘快照（_yesterday_snapshot.json）→ 最优，由closing_review.py创建
② JSONL存档   → 从 morning-briefs.jsonl 恢复最新非今日记录
③ 实时API      → ⚠️ 盘中数据非昨日收盘！
```

## 实现逻辑

```python
snapshot_path = SUMMARY_DIR / "_yesterday_snapshot.json"
use_snapshot = snapshot_path.exists()

if use_snapshot:
    # ① 快照优先
    snap = json.loads(snapshot_path.read_text())
    quotes = snap.get('quotes', {})
    sectors = snap.get('sectors', {})
    overview = snap.get('market_overview', {})
    northbound = snap.get('northbound', {})
elif archive_path.exists():
    # ② 存档回退（2026-07-15 新增）
    records = [json.loads(l) for l in archive_path.read_text().split('\n') if l.strip()]
    for r in reversed(records):
        r_date = r.get('date', '')
        if r_date and r_date != today_str and r.get('quotes'):
            quotes = r['quotes']
            sectors = r['sectors']
            overview = r['market_overview']
            northbound = r['northbound']
            break
if not quotes:
    # ③ 实时API（兜底，⚠️盘中）
    quotes = get_all_quotes()
    sectors = get_sector_quotes()
    overview = get_market_overview()
    northbound = get_northbound_flow()
```

## 注意事项

- 收盘快照由 `closing_review.py` 在 16:00 创建
- JSONL 存档文件：`/opt/data/fund_system_data/morning-briefs.jsonl`
- ③的实时API在**市场交易时段**返回的是当前价格，非昨日收盘
- 3级变量 `sectors/overview/northbound` 在顶部已初始化为空 dict
- 后续代码段（3.5/3.6/3.7）使用 `if not sectors:` 检查避免覆盖已加载数据

## 修复背景

2026-07-15 09:46 盘中运行早报采集，因快照缺失且无存档回退，实时API返回了当日盘中的数据（通信显示+0.40%而非+6.56%）。已在当日修复。
