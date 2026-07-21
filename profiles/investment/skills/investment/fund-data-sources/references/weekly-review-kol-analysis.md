# 周度复盘 KOL分析集成

## 文件位置
- `/opt/data/scripts/weekly_review.py`

## 数据流（v3 策略驱动版）

```
collect_weekly_data()
  │
  ├─ closing-reviews.jsonl    → 本周每日收盘+涨跌数据
  ├─ daily-snapshots.jsonl    → 本周每日快照(指数点位+持仓)
  ├─ signals.jsonl            → 历史KOL信号(仅用于统计)
  ├─ ft.get_user_weibos()     → 实时微博(不读缓存的signals.jsonl)
  └─ ft.get_all_quotes()      → 当前行情(供Verifier核查)

5个Section:
  S1: build_rebalance()       → 组合周度检视(周涨跌+配比+评估)
  S2: build_trend()           → 趋势诊断(指数方向+市场状态)
  S3: build_kol_aggregated()  → KOL信号聚合(多空统计+准确率+逆向信号)
  S4: build_monday_actions()  → 周一操作清单(具体基金代码+方向+仓位)
  S5: build_events()          → 下周关键节点+止损纪律
  
→ send_markdown_in_chunks()  → QQ Bot
```

## S3: KOL信号聚合（不是逐条展示，而是合成）

```python
lines = ["💬 KOL信号聚合"]
# 1. 赛道多空统计表
# 2. 事实核查: 本周信号准确率
# 3. 逆向信号: 总多空比 >2 → 提醒一致性看多风险
#    总多空比 <0.5 → 提醒恐慌过度
```

**关键**: 不逐条展示KOL帖子。用ka.analyze_from_kol_data()提取信号后，只输出聚合结果(多空统计+准确率+逆向提示)。

## S4: 周一操作清单（可执行操作）

```python
lines = ["📋 周一开盘操作清单"]
# 从ka分析结果提取actions, 按置信度排序
# 输出表格: 优先级 | 方向(emoji) | 基金名 | 代码(完整6位) | 仓位调整(%)
# 附理由说明
```

**原则**: 这个section的每个操作都是用户周一开盘可以执行的。不输出模糊建议。

## S1: 组合周度检视（数据来源关键）

```python
# 使用 daily-snapshots 而非 closing-reviews
# snapshots 有所有指数的实际点位值(上证指数/科创50/沪深300/创业板指/上证50/黄金ETF市场价)
# closing-reviews 的 close_change_pct 可能为None
sector_map = {
    '科技/AI': '科创50',        # 直接
    '黄金': '黄金ETF市场价',    # 直接
    '资源/周期': '沪深300',      # 代理
    '新能源': '创业板指',        # 代理
    '医药': '创业板指',          # 代理(无独立医药指数数据)
    '消费': '上证指数',          # 代理(无独立消费指数数据)
}
```

**TARGET_ALLOCATION必须全部覆盖**（6个赛道+市场整体），缺失的会导致输出表不完整。

## 关键规则

| 规则 | 原因 |
|:-----|:------|
| 不用 `signals.jsonl` | 数据陈旧, 不是当前KOL观点 |
| KOL列表从`ft.KOLS`动态获取 | 不可硬编码 |
| 最新微博实时拉取 | `ft.get_user_weibos(uid, count=15)` |
| 分析用`ka.analyze_from_kol_data` | 统一的提取→核查→映射流程 |
| 操作建议在推送最前面 | 用户优先看"周一做什么" |
| 赛道周涨跌用snapshots而非closing-reviews | closing-reviews部分字段为None |
