# T+1 持仓更新流程

> 基金交易T+1确认，当日买入以收盘净值确认份额。
> 盘中估算净值仅供参考，不能作为份额计算的最终依据。

## 两步更新流程

### 步骤A — 用户告知后立即执行

```python
# PORTFOLIO_COST 字典中只更新 cost_total（实际花出去的钱）
"011613": {
    "cost_total": 1401.98,       # ✅ 立刻更新：原1301.98 + 加仓100
    "shares": 901.23,            # ❌ 不动，等收盘后再更新
    "cost_price": 1.5556,        # ❌ 不动，等收盘后再更新
}
```

**为什么 cost_total 可以立刻更新？**
- 它是用户真金白银花出去的总金额
- `log_daily_decisions.py` 的市值计算依赖 `cost_total × (1+涨跌幅)`，不依赖份数
- PnL = 市值 - cost_total，所以 cost_total 正确时 PnL 也是正确的

**🚨 不要用估算净值算份额（2026-07-15 用户纠正）：**
- 用户原话："你记录的份数计算也是估算吧，正式今日收盘值出来你才能知道吧"
- 用盘中估算净值算份额会有0.5-2%的偏差
- 正确做法：只更新cost_total，等收盘后实际净值出来再算份额

### 步骤B — 收盘后执行

收盘后（通常在16:00-20:00之间）基金公布当日实际净值：

```python
# 1. 获取实际收盘净值
from fund_tools import get_fund_value
data = get_fund_value("011613")
nav = data["nav"]  # 实际收盘净值

# 2. 计算实际买入份额
add_shares = 100 / nav
old = PORTFOLIO_COST["011613"]
new_shares = old["shares"] + add_shares
new_cost_total = old["cost_total"] + 100
new_cost_price = new_cost_total / new_shares

# 3. 更新
PORTFOLIO_COST["011613"]["shares"] = round(new_shares, 2)
PORTFOLIO_COST["011613"]["cost_price"] = round(new_cost_price, 4)
```

## 盘中估算 vs 实际净值偏差

| 基金代码 | 盘中估算净值 | 实际收盘净值 | 偏差 |
|:--------:|:----------:|:-----------:|:----:|
| 011613 | 1.5614 | 待收盘确认 | ~±0.5-2% |
| 024418 | 2.8226 | 待收盘确认 | ~±0.5-2% |

## 用户手动加仓记录格式

```python
{
    "_date": "2026-07-15",
    "code": "011613",
    "amount": 100,
    "reason": "跌得多长期看好",
    "estimated_nav": 1.5614,
    "status": "pending"        # pending → closed(收盘后)
}
```

## 历史数据位置

持仓成本数据硬编码在 `/opt/data/scripts/log_daily_decisions.py::PORTFOLIO_COST`（行20-33）。

每次持仓变更后必须同步更新该字典，否则：
- `check_allocation.py` 的占比计算会偏移（也依赖cost_total）
- `daily-snapshots.jsonl` 中的 portfolio_value 会沿用旧数据
- 所有报告（portfolio.md / 诊断报告）都会使用旧成本

## Pitfall

**2026-07-15 用户纠正：** 第一次估算份额时直接更新了shares字段，用户指出这是不准确的。修复方案：先只更新cost_total，收盘后等实际净值再算份额。后续所有手动加仓操作都遵循此两步模式。
