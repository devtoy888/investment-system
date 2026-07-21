# 市场情绪系统设计 (2026-07-06 新增)

## 概述

两层次情绪分析：**大盘分档** (机械阈值) + **短线情绪** (涨停/跌停/成交额)。

## 数据源

| 数据 | 来源 | 字段 | 可达性 (Oracle ARM) |
|------|------|------|:------------------:|
| 上涨/下跌/平盘家数 | 东财 push2 `f169/f170/f171` | 三个int | ❌ 境外间歇超时 |
| 涨停/跌停家数 | 东财 push2 `f167/f168` | 两个int | ❌ 同上 |
| 两市成交额 | 腾讯 `qt.gtimg.cn field[35]` | 三段式价/量/额 | ✅ 稳定 |

**限制：** 东财 push2 从境外 Oracle ARM 访问时常 SSL 超时。系统通过快照机制 (`_yesterday_snapshot.json`) 回退 —— 实盘数据通时用实时、不通时用上次收盘快照。

## 函数

### `grade_market_sentiment(rise_count, fall_count, limit_up=None, limit_down=None)`

5 档机械分档，基于涨跌家数比例 `ratio = rise / (rise + fall)`：

| 阈值 | 档位 | Emoji |
|:----:|:----:|:----:|
| > 0.70 | 普涨 | 🔴 |
| > 0.55 | 偏强 | 🔴 |
| > 0.45 | 中性 | 🟡 |
| > 0.30 | 偏弱 | 🟢 |
| ≤ 0.30 | 冰点 | 🟢 |

附加信息：
- 涨跌比 `rise / fall`
- 涨停/跌停家数
- 短线活跃度：涨停>50且ratio>0.5 → "短线活跃 🔥"; 涨停<15且ratio<0.5 → "短线低迷 ❄️"

### `get_short_term_sentiment(market_overview)`

统一输出三行文本，供预采集脚本写入 overview 文件：

```
📊 大盘情绪: 偏强 🔴 (涨跌比2.60:1 涨停45 跌停5)
💰 成交额: 3182亿
📈 涨停45家 跌停5家 ➖
```

## 推送集成

`_market_overview_summary.txt` (早报) / `_noon_overview.txt` (盘中) / `_closing_overview.txt` (收盘) 均使用 `get_short_term_sentiment()` 生成。LLM 通过 cat 文件自动读取。

## 缺失能力（需代理到腾讯云）

连板梯队 / 封板率 / 炸板率 / 晋级率 / 成交额 TOP20 需要东财 push2ex API，从 Oracle ARM 不可达。
