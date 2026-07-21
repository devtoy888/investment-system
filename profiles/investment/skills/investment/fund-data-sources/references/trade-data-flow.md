# 基金持仓数据流

> 系统如何追踪持仓成本和操作记录，避免"数据不对"的重复纠正。
> 最后更新: 2026-07-20 — 新增 portfolio_snapshot v2 市值计算法

## 三个数据源的关系

```
trade_decisions.jsonl    ← 当前持仓成本快照（单条JSON，每次快照覆盖）
     ↑ 来源于
operations/operation_*.md ← 每次买入操作记录（多文件，积累所有历史操作）
     ↑ 来源于
portfolio_snapshot.py    ← 每日17:00自动生成持仓市值快照（CSV+MD+HTML，上传R2）
```

### trade_decisions.jsonl

- 位置: `/opt/data/fund_system_data/trade_decisions.jsonl`
- 格式: 每行一条JSON，最新行为当前持仓
- 字段: `{code: {cost: 成本, est_change: 估算涨跌幅}}`
- **更新时机**: 每次portfolio_snapshot.py运行时覆盖最新行（更新当日市值）
- **⚠️ 必须手动更新的情况**: 当用户实际进行了买卖操作后，必须手动更新该文件的cost值，否则系统不知道新成本

### operations/operation_*.md

- 位置: `/opt/data/fund_system_data/operations/operation_YYYY-MM-DD.md`
- **同步要求**: 操作记录必须同步到本地。如果只上传到R2没同步到本地，`execute_today_plan.py` 的 `parse_ops()` 读不到数据，建仓进度显示为0。
- 同步命令:
  ```bash
  curl -s "https://hermes-main-media.devtoy.xyz/fund-system/operations/operation_YYYY-MM-DD.md" \
    > /opt/data/fund_system_data/operations/operation_YYYY-MM-DD.md
  ```

### portfolio_snapshot.py

- 脚本: `/opt/data/scripts/portfolio_snapshot.py`
- 定时: 交易日17:00（cron任务: `abeb2f69bd48`，no_agent模式）
- 功能: 读取trade_decisions → AKShare取最新净值 → 生成CSV+MD+HTML → 上传R2
- 路径: `fund-system/data/portfolio/portfolio-{date}.{csv,md,html}`

## ⚠️ 持仓市值计算：份额 × 净值（v2修复）

**2026-07-20严重错误**：v1版本用 `value = cost × (nav / cost)` = nav本身（1.34元），完全失真。

**正确公式（必须使用）**：

```
市值 = 持有份额 × 当前净值
盈亏 = 市值 - 成本
```

### 份额获取方式（两种）

| 来源 | 适用基金 | 方法 |
|:-----|:---------|:------|
| ✅ **操作记录精确份额** | 003096, 013403 | 从 `operations/operation_*.md` 提取"确认份额 XX份" |
| ⚠️ **年初净值估算份额** | 其他12支 | `份额 ≈ 总成本 / 今年首个净值` |

### 实现代码（portfolio_snapshot.py）

```python
# 方式1: 从operation文件解析精确份额
def parse_ops_shares():
    """解析"确认份额 XX.XX份"模式"""
    shares = {}
    if OPS_DIR.exists():
        for fpath in sorted(OPS_DIR.glob('operation_*.md')):
            text = fpath.read_text(encoding='utf-8')
            for m in re.finditer(r'(\d{6}).*?确认份额\s*([\d.]+)\s*份', text):
                code, qty = m.group(1), float(m.group(2))
                shares[code] = shares.get(code, 0) + qty
    return shares

# 方式2: 年初首个净值估算份额
first_nav = get_first_2026_nav(code)  # AKShare fund_open_fund_info_em
shares = cost / first_nav if first_nav else 0

# 市值计算
current_value = shares * current_nav
pnl = current_value - cost
pnl_pct = pnl / cost * 100
```

### 已知份额数据（精确值）

| 基金 | 买入批次 | 份额 | 来源 |
|:-----|:---------|:----:|:-----|
| 003096 | 7/16 160元@1.9810 | 80.77份 | 用户确认 |
| 003096 | 7/17 120元@1.8294 | 65.60份 | 用户确认 |
| **003096** | **合计** | **146.37份** | |
| 013403 | 7/16 150元@0.7886 | **190.21份** | 用户确认 |

### YTD验证方法

估算份额必须与AKShare的今年累计涨幅交叉验证：
```
估算YTD = (当前市值 / 成本 - 1) * 100
AKShare YTD ≠ 估算YTD → 份额估算有偏差，需查找原因
```

## 常见错误模式

| 错误 | 根因 | 正确做法 |
|:-----|:------|:---------|
| 持仓金额用"~估算" | 没读trade_decisions.jsonl | 必须从JSONL读取精确cost |
| 003096成本重复计算(280+280=560) | base字典和ops都贡献了成本 | base的003096设cost=0，全由ops提供 |
| 013403建仓进度显示0% | operations/文件没同步到本地 | 从R2下载operation_*.md到本地 |
| 报告写了不存在的新基金 | 没核查实际持仓数据 | 先读trade_decisions确认持仓 |
| **市值显示1.34元** | **value = cost × (nav/cost) = nav** | **value = shares × nav** |
| **HTML缺失** | 只上传了MD | 必须MD+HTML成对上传 |

## 建仓进度计算公式

```python
# execute_today_plan.py 第388-396行
ops = parse_ops()  # 从本地operations/读取
for code, total_plan in [('003096', 370), ('013403', 300)]:
    done = ops.get(code, {}).get('cost_total', 0)  # 从操作记录累加
    remain = max(0, total_plan - done)
    pct = done / total_plan * 100
    # 显示: 003096 医药C 280/370元 (76%) 剩90元
```

## 输出的三件套

每份持仓快照生成三个文件并上传R2：
- **CSV** (`portfolio-{date}.csv`): 可导入Excel做分析
- **MD** (`portfolio-{date}.md`): 可读文本，QQ推送用
- **HTML** (`portfolio-{date}.html`): 浏览器预览，数据硬编码(静态度量)

**HTML必须用fetch+marked.js动态渲染MD，还是硬编码数据？**
→ 持仓快照是**每日点快照**，一旦生成不再变化（不像roadmap.md会持续编辑）。所以HTML数据硬编码在页面内，不做fetch引用。这样用户直接打开HTML就能看，不依赖外部MD文件。
