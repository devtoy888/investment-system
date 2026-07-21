# 数据源稳健化修复 — 2026-07-18 会话记录

## 背景
数据源系统在约4周运行中暴露了多个问题：
- 东财push2 502（22.7%可用率）
- hexin北向不稳定（52.5%可用率）
- AKShare硬编码日期bug导致备援永久失效
- 外盘Yahoo无新鲜度标记
- 非交易日数据无防护

## 7项修复清单

| # | 修复 | 文件 | 测试验证 |
|:-:|:-----|:-----|:--------:|
| 1 | AKShare硬编码日期修复 | `fund_source_akshare.py` | 14支基金历史净值成功 |
| 2 | 涨跌家数双域名轮换（push2→push2delay） | `fund_tools.py` get_market_overview | push2 ❌→push2delay ✅ |
| 3 | 北向资金AKShare备援 | `fund_tools.py` + `fund_source_akshare.py` | stock_hsgt_fund_flow_summary_em ✅ |
| 4 | Yahoo外盘_stale时间戳标记 | `fund_tools.py` _yahoo_quote | 7/7标的含_stale字段 |
| 5 | 新浪tags涨跌正则增强（1→4种模式） | `fund_tools.py` | 代码结构确认 |
| 6 | _tag_freshness通用新鲜度标记 | `fund_tools.py` | 边界24/24测试 |
| 7 | track_source追踪全覆盖 | `fund_tools.py` | 7个数据源覆盖 |

## 多轮验证过程

4轮测试 + 子代理并行历史数据验证：
- 第1轮：语法 + Yahoo_stale结构 → 5/5 ✅
- 第2-3轮：交叉验证 + 边界条件 → 32/34 ✅（2项测试预期错误）
- 第4轮：一体化全量 → 33/33 ✅
- 边界：24/24 ✅
- 历史数据：14支基金 + 9个指数全量成功

## 东财502根因分析

```
push2.eastmoney.com:    ❌ 502 (nginx geo-block for overseas IPs)
push2delay.eastmoney.com: ✅ 200 (同一服务器120.79.191.232, 不同vhost)
                        ↓
   确认: 是nginx层的virtual host地理拦截，非IP封禁
```

相同IP，不同域名 → 不同结果。不是添加浏览器头/超时能解决的。

## a-stock-data参考源验证

| 源 | 本服务器 | 结论 |
|:---|:--------:|:------|
| push2delay.eastmoney.com | ✅ 100% | 已接入 |
| mootdx TCP连接 | ✅ 10/10可达 | 网络层可用 |
| mootdx库K线接口 | ❌ KeyError | 库bug(pandas 3.0兼容) |
| mootdx finance | ✅ 0.28s/37字段 | 可接入 |
| 同花顺板块 | ❌ geo-block | 海外不可用 |
| 百度K线 | ❌ API已改版 | 不可用 |
| 新浪财报三表 | ✅ 0.52s | 可接入备援 |

## 交易日自动验证

`trading_day_validate.py` 通过3轮cron自动运行：
- 09:35：API可达性 + _stale标记检查
- 13:00：交叉验证（腾讯vsAKShare涨跌、天天vsAKShare净值）
- 15:30：收盘数据准确性 + 归档完整性
