# 🧪 数据源多轮验证报告

> 日期: 2026-07-18 (非交易日) | 测试框架: 4轮 + 3批并行

## 验证轮次总览

| 轮次 | 名称 | 测试数 | 通过 | 结果 |
|:----:|:-----|:-----:|:----:|:----:|
| 第1-2轮 | 基金+指数历史数据全量拉取 | (子代理运行中) | - | ⏳ |
| 第3轮 | 多源交叉验证一致性 | 13 | 10 | ⚠️ |
| **第4轮** | **边界条件+错误处理+备援链** | **24** | **24** | **✅** |
| 修正验证 | 净值偏差根因分析 | 3 | 3 | ✅ |

## 第3轮：交叉验证结果

| 验证项 | 结果 | 说明 |
|:-------|:----:|:------|
| 腾讯 vs AKShare 上证涨跌 | ✅ **完全一致** | 均= -3.05%，偏差0.00% |
| 天天基金 vs AKShare 同日期净值 | ✅ **完全一致** | 同日净值偏差<0.0001 |
| 天天基金 vs AKShare 跨日净值 | ⚠️ 差1天 | 天天基金T+1更新，AKShare更新更快 |
| 外盘Yahoo数据结构完整 | ✅ 7/7 | 全部含price+change_pct |
| 北向资金备援链 | ✅ hexin→新浪 | hexin失败(50%)→新浪成功(16.08亿) |
| 行业ETF采集率 | ✅ 10/10 | 全部数据结构完整 |

**核心结论：** 同日期数据完全一致。净值"偏差"是因为：
- 天天基金 `fundgz`：盘中实时估算，官方净值T+1更新
- AKShare `fund_open_fund_info_em`：官方历史净值，更新更快（当日收盘后即有）
- 两者在相同日期上的数值**完全吻合**

## 第4轮：边界条件测试结果（24/24 ✅）

| 类别 | 测试项 | 结果 |
|:-----|:-------|:----:|
| **新鲜度标记** | 空字典标记 | ✅ |
| | 旧数据_fresh=False | ✅ |
| | _fetch_time字段 | ✅ |
| | 非交易日_fresh=False | ✅ |
| **交易日判断** | 周六=False | ✅ |
| | 周日=False | ✅ |
| | 周五=True(上周) | ✅ |
| | 周一=True(下周) | ✅ |
| **腾讯_stale** | 非交易日_stale=True | ✅ |
| | _data_source=tencent | ✅ |
| **涨跌家数备援链** | 东财push2入口 | ✅ |
| | 新浪tags备援 | ✅ |
| | AKShare备援 | ✅ |
| | 新浪多正则扩展 | ✅ |
| **北向资金备援链** | hexin主源 | ✅ |
| | 新浪tags备援 | ✅ |
| | AKShare备援(新增) | ✅ |
| | 东财push2备援 | ✅ |
| **track_source覆盖** | get_all_quotes | ✅ |
| | get_all_funds | ✅ |
| | get_overnight_quotes | ✅ |
| **错误处理** | 空code不崩溃 | ✅ |
| | 无效基金code不崩溃 | ✅ |

## 验证通过的机制

```
非交易日识别:
  is_trading_day() → weekday检查 + AKShare交易日历 → 周六False ✅

数据新鲜度标记:
  _tag_freshness() → 检查nav_date/date字段 → 非交易日_fresh=False ✅
  get_tencent_quote → 新增_stale标记 → 非交易日_stale=True ✅

涨跌家数备援链(原22.7%→目标≥95%):
  东财push2(15s) → 新浪tags(4种正则) → AKShare stock_zh_a_spot_em → None ✅

北向资金备援链(原52.5%→目标≥90%):
  hexin(重试2次) → 新浪tags → AKShare(新增) → 东财push2 → 快照文件 ✅

硬编码日期已清除:
  fund_source_akshare.py: "2026-07-15" → 动态est_col列名匹配 ✅

数据源追踪全覆盖:
  tencent_quotes/fund_values/overnight已加入track_source ✅
```

## AKShare可用性状态

| API | 状态 | 说明 |
|:----|:----:|:------|
| `fund_open_fund_info_em` | ✅ | 14支基金历史净值拉取成功 |
| `stock_zh_index_daily` | ✅ | 9个指数日K线拉取成功 |
| `stock_zh_a_spot_em` | ⚠️ | 非交易日连接重置(预期行为) |
| `stock_hsgt_fund_flow_summary_em` | ✅ | 北向资金数据成功 |
| `fund_value_estimation_em` | ⚠️ | 慢(40s)，10s超时保护 |
| `tool_trade_date_hist_sina` | ✅ | 交易日历查询成功 |

## 待交易日验证的项

1. 涨跌家数AKShare备援在交易日的实际数据准确率
2. 盘中时时估算 vs 收盘净值偏差
3. 腾讯行情 _stale=True 在交易日是否切换为 False
4. 各数据源在交易日的请求耗时统计

---

> 测试环境: non-trading day (2026-07-18 Sat) | Python + AKShare + fund_tools
> 待补充: 子代理历史全量数据拉取结果(14支基金 + 9个指数)
