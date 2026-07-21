# 周度复盘数据源交叉验证（2026-07-19 定型）

## 问题背景

weekly_review.py 最初使用 `daily-snapshots.jsonl` 作为大盘走势主数据源，但实际只有3/5个交易日（周三~周五）。周报只显示3天数据，且周涨跌使用日涨跌累加（偏差大）。

## 验证方法

### 第1步：检查数据源覆盖

```python
# daily-snapshots.jsonl
>>> 5条记录, 日期: ['2026-07-15', '2026-07-16', '2026-07-17']
# closing-reviews.jsonl (本周)
>>> 2026-07-13 ~ 2026-07-17, 完整5天
```

**发现：** closing-reviews 有完整5天数据（包含market_accuracy.指数.change_pct），snapshots只有3天。

### 第2步：检查字段完整性

```python
# closing-reviews 字段：
- market_score: "6/6" (正确率字符串)
- market_accuracy_pct: 100 (整数百分比)
- market_accuracy: {指数名: {change_pct, direction_same, open, close, prev_close}}
```

**发现：** closing-reviews 包含周报需要的全部字段。`market_score` 和 `market_accuracy_pct` 可直接用于准确率表。

### 第3步：验证KOL信号数据

```python
# signals.jsonl: 543条
# signals-resolved.jsonl: 5条 (全部唐史主任司马迁)
# generate_signal_report() output:
#   - 5条全部 direction=neutral
#   - correct=null (中性信号无正确/错误)
#   - 但显示为 0/5 (0%)
```

**发现：** KOL准确率数据不可用。543条原始信号仅5条被解析，全部为中性方向。**不展示比展示错误数据好。**

### 第4步：验证周涨跌算法

旧算法：`sum(daily_changes)` 累加5天change_pct
问题：每日基准不同（change_pct是相对当日开盘的），累加不等于周涨跌

正确算法：`(周五收盘 - 周一开盘前) / 周一开盘前 × 100`
数据：closing-reviews[Mon].market_accuracy[指数].prev_close (周一开盘前)
     closing-reviews[Fri].market_accuracy[指数].close (周五收盘)

## 通用方法论

每次构建报告前执行"4步交叉验证"：

1. **源覆盖检查** — 声称覆盖N天，实际有没有N条数据？
2. **字段一致性** — 脚本读的字段 vs JSONL实际存的字段，一致吗？
3. **计算逻辑验证** — 用原始值手算一遍，和脚本结果对比
4. **无用数据识别** — 某些字段"有值"但"无意义"（如全部中性信号的准确率）
