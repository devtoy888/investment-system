# 📋 定时任务全量评估报告

> 日期: 2026-07-18 | 审查范围: 15个定时任务 + 18个执行脚本

---

## 1. 审查结论 — 总体良好

核心发现：**所有脚本的数据源修复是自动继承的**。因为数据层的修复在`fund_tools.py`中，而所有脚本都通过调用`fund_tools.*`函数获取数据，所以`push2→push2delay`、`_stale`标记、`AKShare备援`等修复对定时任务**自动生效**。

具体的代码设计中，主要分为两类：

| 类型 | 代表脚本 | 数量 | 数据流 |
|:-----|:---------|:----:|:-------|
| **no_agent数据采集** | `collect_morning_data.py`等 | 6个 | 直接调fund_tools → 写文件 → feishu卡片 |
| **thin wrapper** | `run_morning.py`等 | 12个 | 仅调用子进程，无数据逻辑 |

---

## 2. 数据源利用评估

| 修复项 | 是否被定时任务利用 | 说明 |
|:-------|:----------------:|:------|
| **push2→push2delay** | ✅ **自动继承** | 所有调用`get_market_overview()`的脚本自动使用新域名 |
| **Yahoo _stale标记** | ⚠️ **未被利用** | 外盘数据有`_stale`字段，但脚本只取了`price/change_pct`，丢弃了`_stale` |
| **北向AKShare备援** | ✅ **自动继承** | 调用`get_northbound_flow()`自动使用新降级链 |
| **新浪多正则** | ✅ **自动继承** | 在`fund_tools.py`内部，脚本不需要改动 |
| **track_source** | ✅ **自动继承** | 在`fund_tools.py`内部，脚本不需要改动 |
| **\_stale基金新鲜度** | ⚠️ **部分覆盖** | 基金有自实现的stale逻辑，未使用新的`_fresh`标记体系 |

---

## 3. 发现的具体问题（非严重）

### 3.1 ⚠️ 外盘 _stale 未传递到推送

**文件**: `collect_morning_data.py` L35-L38

```python
# 当前：只取了price/change_pct，丢弃了_stale
for name, q in overnight.items():
    if q:
        overnight_lines.append(f"{name}|{q['price']}|{q['change_pct']:+.2f}%")
```

**影响**: 非交易日美股数据不会标注"⚠️ 非交易日"，用户看到"道琼斯涨X%"不知道是几天前的。
**修复**: 在生成表格时检查`_stale`并添加标注。

### 3.2 ⚠️ 基金stale使用自实现逻辑

**文件**: `collect_morning_data.py` L190-203

```python
# 当前：自实现stale判断
if not fd.get('stale') or fd.get('nav_date', '') >= today:
    continue
```

**影响**: 代码功能正常，但与新的`_fresh`标记体系不统一。新增的`_tag_freshness`（含`_fetch_time/_is_trading_day`）未被利用。
**建议**: 统一使用`_fresh`标记替代自实现逻辑。

### 3.3 ✅ `update_operation_nav.py`的硬编码

**文件**: `update_operation_nav.py` L97-98

```python
yesterday = date(2026, 7, 16)
yesterday_str = "2026-07-16"
```

**结论**: **这是正常的业务需求**，该脚本是一次性的（确认2026-07-16特定操作），硬编码日期对应实际操作日期，不是Bug。

---

## 4. 架构合理性评估

### 4.1 ✅ 做得好的

| 设计 | 评价 |
|:-----|:------|
| **数据采集→卡片发送两层分离** | 采集失败不影响卡片框架，卡片发送失败不影响数据落盘 |
| **中间文件机制** | 写 `/tmp/fund_data/` 中间文件，采集崩了也有部分数据 |
| **交易日自检** | `collect_morning_data.py` 开盘前检查`is_trading_day()`，非交易日跳过 |
| **收盘快照复用** | 利用收盘快照避免9:00再拉取一遍昨收数据，减少请求 |
| **信号提取归因** | `extract_signals_from_kols` + `store_signals` 分离提取与存储 |

### 4.2 ⚠️ 可改进的

| 设计 | 问题 | 建议 |
|:-----|:------|:------|
| **feishu卡片发送** | 依赖`.feishu-deps` + `send_*_cards.py`，feishu在香港不可达 | 改用HTTP API直接推送 |
| **timeout 180s** | 部分脚本设180s，实际采集~25s，遇到微博采集超时可能不够 | 稳定后降到120s |
| **标签/赛道关键词硬编码** | KOL分析关键词（AI/算力/芯片等）硬编码在collect_morning_data.py | 提取到配置文件 |
| **KOL UID硬编码** | 博主UID和名字写在代码里 | 提取到YAML配置 |

---

## 5. 结论

> **系统整体稳健，无阻断性Bug。** 数据源修复自动继承到所有定时任务。
> 待优化的是：外盘_stale利用（优先级低，不影响系统稳定性）。
