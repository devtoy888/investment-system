# 基金系统自进化机制 (2026-06-30)

## 维度A: 数据合理性校验

**函数**: `run_sanity_checks(raw_data)` in fund_tools.py

校验所有采集数据的合理性，自动发现API故障、非交易时段、采集异常。写入 `_sanity_report.json` (或 `_noon_sanity.json`, `_closing_sanity.json`)。

### 校验项
| 检查项 | 正常范围 |
|--------|---------|
| 上证指数 | 2500-4500 |
| 科创50 | 800-3000 |
| 创业板指 | 1500-5000 |
| 沪深300 | 3000-6000 |
| 上证50 | 2000-4000 |
| 黄金ETF | 5-15元 |
| 两市成交额 | 500-50000亿 |
| 涨跌家数合计 | >100家 |
| 北向资金 | -200~+200亿 |
| 基金采集率 | >60% |
| 板块采集率 | >50% |
| KOL博文 | >0条 |

### Cron prompt集成
三条prompt末尾加了 `cat /tmp/fund_data/_*_sanity.json` + 标注规则: status=⚠️时推送开头追加警告。

### 基金采集优化历程
| 版本 | 成功率 | 耗时 | 关键改动 |
|:----:|:------:|:----:|---------|
| 串行(5s超时) | ~10/18 | 50-100s | 脚本经常120s超时整体失败 |
| 并行5并发(5s超时) | 12/18 (67%) | ~23s | 脚本不再超时，但个别基金仍丢失 |
| 并行5并发(8s超时, current) | **17/18 (94%)** | ~23s | 提高单请求容错，总耗时不变 |

## 维度B: 信号归因追踪

### 数据流
```
morning/noon → extract_signals_from_kols() → store_signals() → signals.jsonl
                                                                      ↓
                                                          closing → resolve_past_signals() → signals-resolved.jsonl
                                                                                                      ↓
                                                                                         generate_signal_report()
```

### 信号提取
- 扫描每条KOL博文，匹配SIGNALS词典中的黑话关键词
- 区分方向: bullish(右侧/加仓/底/反弹) > bearish(泡沫/风险/守住) → 投票计数
- 映射板块: 科技→科创50, 大盘→上证指数, 创业板→创业板指, 黄金→黄金ETF
- 记录基准价格用于后续准确率验证

### 信号解析
- 收盘复盘时查询3-7天前的未解析信号
- 对比预测方向 vs 实际板块/指数涨跌幅
- 写入signals-resolved.jsonl + R2同步
- **新增JSONL回退（2026-06-30）**: 收盘复盘读取早盘`_raw_data.json`做对比时，如果`/tmp/fund_data/`被清理，回退到`morning-briefs.jsonl`归档读取今日数据

### 准确率报告
- 近30天数据
- 自动分级: ✅≥70%, 🔶50-70%, ❌<50%
- 配套周报cron(待建，可复用auto_validate_sources.py)

## 参数调优记录

### 基金超时优化 (2026-06-30)
| 版本 | 成功/总数 | 耗时 | 关键改动 |
|:----:|:---------:|:----:|---------|
| 串行(timeout=10s) | ~10/18 | 50-100s | 脚本经常整体超时 |
| 并行5并发(timeout=5s) | 12/18 | ~23s | 脚本不再超时，个别基金超时 |
| 并行5并发(timeout=8s) **current** | **17/18 (94%)** | ~23s | 提高至8s，整体耗时不变 |

### 三点启示
1. 单超时是API慢而非限流（每次失败代码随机）
2. 并行采集下提高单timeout不影响总体耗时（慢的是少数，多数在1-2s内完成）
3. 94%成功率对基金采集已可接受——18支中偶尔1支失败不影响整体判断

## JSONL归档回退 (2026-06-30)

**问题**：`closing_review.py` 的早盘对比通过读 `/tmp/fund_data/_raw_data.json` 实现。测试时 `rm -rf /tmp/fund_data/` 清空该文件后，收盘对比为 `N/A`。

**修复**：closing_review.py 增加JSONL回退。如果临时文件不存在，从 `fund_system_data/morning-briefs.jsonl` 读取今天的最新 `morning_brief` 记录（该归档由 `store_jsonl()` 写入并同步R2，不受 `/tmp/` 清理影响）。

**设计原则**：临时文件可被清理 → 但持久化归档不能依赖临时文件的存续。任何"早上采集→收盘读回"的数据模式都需要持久化备份。

## 信号追踪的计时问题 (2026-06-30)

`resolve_past_signals()` 查找3-7天前的信号。部署首日无数据可解析。用户会问"怎么没有输出"——必须在部署时明确告知：
- 第1天：存储信号 → 无解析
- 第2-3天：存储信号 → 仍无解析（不满3天）
- 第4天起：开始产出解析结果
- `generate_signal_report()` 需30天积累才有统计意义

## 文件清单
| 文件 | 位置 | 说明 |
|------|------|------|
| `_sanity_report.json` | `/tmp/fund_data/` | morning写入 |
| `_noon_sanity.json` | 同上 | noon写入 |
| `_closing_sanity.json` | 同上 | closing写入 |
| `signals.jsonl` | `fund_system_data/` | 信号原始数据 |
| `signals-resolved.jsonl` | 同上 | 解析后的预测结果 |
| `generate_signal_report()` | fund_tools.py | 报告生成函数 |
