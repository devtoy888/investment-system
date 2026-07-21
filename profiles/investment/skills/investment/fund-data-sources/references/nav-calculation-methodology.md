# AKShare NAV 计算方法

> ⚠️ **本文件必须先读**。2026-07-20发生过一次严重数据错误：用固定日期6/15做起点，基金6/15→6/30暴涨→7/1→7/17暴跌，一涨一跌抵消，导致011613的1m错报为-1.76%（真实-6.37%）。**这个bug修复了两次才发现参考文件已有记录——问题是没先读。**

## 铁律

1. **只允许前推法，禁止固定日期法**。绝对不能用 `rows[rows['日期'] >= '2026-06-15']` 这种写死的起点做1m计算。
2. **必须同时报告四个维度**：1周 + 1月 + 3月 + 今年。1月可能被中间波动扭曲（暴涨+暴跌=平），1周才是当前真实趋势。
3. **数据必须至少独立拉取2轮验证**，不可在同一个数据拉取中重复使用同一批数据做"验证"。

## 前推法（正确，必须使用）

从最新净值日往前推 N 天，找最近的数据点计算涨跌：

```python
from datetime import datetime, timedelta

# 1周: 前推7天
one_w_ago = latest_date - timedelta(days=7)
w_closest = min(rows, key=lambda r: abs(r[0] - one_w_ago))
one_w = (latest_nav / w_closest[1] - 1) * 100

# 1月: 前推30天
one_m_ago = latest_date - timedelta(days=30)
m_closest = min(rows, key=lambda r: abs(r[0] - one_m_ago))
one_m = (latest_nav / m_closest[1] - 1) * 100

# 3月: 前推90天
three_m_ago = latest_date - timedelta(days=90)
t_closest = min(rows, key=lambda r: abs(r[0] - three_m_ago))
three_m = (latest_nav / t_closest[1] - 1) * 100

# 今年: 今年第一个交易日
this_year = [r for r in rows if r[0].year >= 2026]
ytd = (latest_nav / this_year[0][1] - 1) * 100
```

## 固定日期法（错误，已弃用）

```python
# ❌ 不要这样做！
d30 = [r for r in rows if r[0] >= date(2026, 6, 15)]
m1 = (d30[-1][1] / d30[0][1] - 1) * 100
# → 基金6/15→6/30暴涨+25%，7/1→7/17暴跌-22%
# → 一涨一跌抵消 → 错报-1.8%（真实-6.4%）
```

## 必须同时报告四个维度

不能只看 1月。基金可能 1月数据被中间波动掩盖：

```
基金         1周         1月         3月        今年
011613     -16.1%      -6.4%      +19.9%     +21.6%    ← 1周才是当前真实情况
024418     -22.3%      -6.8%      +58.9%     +73.8%    ← 1月-6.8%掩盖了1周-22%
003096      -1.3%     +25.2%       +5.6%      +4.0%    ← 1月+25%强但1周已微调
```

- **近1周** = 当前最重要（急跌/反弹的信号）
- **近1月** = 中期趋势（可能被中间波动扭曲）
- **近3月** = 中期验证
- **今年** = 长期基准
