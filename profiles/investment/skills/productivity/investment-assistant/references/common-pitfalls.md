# 常见陷阱清单

## 1. 硬编码日期

send_noon.py曾有硬编码"2026-07-13"导致推送内容显示2天前的日期。
修复：始终用 date.today() 或 datetime.now() 动态生成。

## 2. 盘中数据冒充昨日收盘

盘中运行早报采集时，腾讯API返回的是今日涨跌幅。
修复：三级降级策略（参见 data-source-fallback.md）

## 3. QQ推送消息过多

旧版按内容主题逐段推送，早报8-12条消息。
修复：合并推送，仅按3800字符切分。

## 4. 同一天多次采集 → 连跌误判

risk_warning.py 检查"连跌N天"时，读 fund-daily-trend.jsonl 的全部记录。该文件一日内被多个脚本各写一次，产生同天8+条记录。
旧代码 `hist = defaultdict(list)` 把这些同天数据当成"连续8天"，输出 `连跌3天: 2026-07-15(-2.69%), 2026-07-15(-2.79%), 2026-07-15(-4.03%)`。
修复：`hist = defaultdict(dict)` 按日期去重，同一天只取最后一次值。

## 5. 修改后必须自测

每次改代码/配置后，必须运行一次验证测试再汇报结果。
- 改 risk_warning.py → 跑 python3 risk_warning.py 看输出
- 改 data source → 跑对应采集脚本
- 改 cron 配置 → 手动触发看一次推送

## 6. 持仓成本更新等收盘

用户加仓/减仓时，cost_total（花出去的钱）可以立刻更新。但 shares（份数）和 cost_price（均价）依赖当日收盘实际净值，不能用盘中估算值算。
正确流程：
1. 第一时间更新 cost_total
2. 等收盘后 log_daily_decisions.py 用实际净值算份数，自动修正

## 7. 执行脚本禁用昨日数据当"今日实时"（2026-07-16 用户纠正）

`get_fund_value(code)` 在非交易时段返回的 `estimated_change` 是**昨天盘中**旧估算
（nav_date≠今日）。若脚本直接把它当"今日涨跌"产出买卖指令，就是**虚假实时**。
必须加 `is_trading_time()` 判定（北京9:30-15:00，排除午休）：
- 盘前/盘后 → 只回看近几日K线(腾讯kline)给预案，**不产假实时指令**
- 交易时段 → 才拉真实盘中估值（腾讯qt.gtimg.cn指数 + 天天基金fundgz基金）
双时点cron模式：09:35开盘后 + 14:30决策点，均 no_agent + deliver=origin。
骨架与接口详见 `references/time-aware-execution.md`。

## 8. "评估配置/哪些板块值得投"必须全行业筛选 + KOL交叉验证

用户问"只加医药合理吗/筛选值得投的板块"时，标准动作（2026-07-15~16 会话确立）：
① AKShare 拉**全行业指数6个月**收益排序（18+板块，不止看单一）；
② 真实接口拉 KOL（主任）近1-2月**全部**微博做赛道提及统计（去重）；
③ 交叉验证：KOL看多方向 vs 实际数据最强方向，冲突点明确说明（如主任只聊科技、
   从未提医药/机器人/航天，而用户想加这些 → 属独立判断，需数据支撑）；
④ 输出多赛道分散方案 + **分批建仓策略**（禁止一次性买入，T+1+波动风险）。
注意：briefs缓存的KOL信号是系统**重复抓取**同一天同内容（202条→去重32条），
真实全量须用 `mymblog` API 多页实时拉（174条→去重140条）。
基金比较必须同一时间窗口（见 fund-holdings-overlap.md 第四节）；
减持留谁必须拉实际持仓重叠（见 fund-holdings-overlap.md）。

## 9. 交易日外盘_stale标记（2026-07-18 新增）
Yahoo Finance在非交易日静默返回旧数据。必须用**时间戳动态判断**（不依赖硬编码日历）：
```python
market_time = meta.get('regularMarketTime')
age_hours = (datetime.now().timestamp() - market_time) / 3600
is_fresh = age_hours < 24
```
返回字段必须包含 `_stale`、`_stale_reason`、`_data_time`、`_fetch_time`。

## 10. push2.eastmoney.com 502 = CDN线路问题（2026-07-18 确认 + 2026-07-21 补充）

海外服务器（Oracle ARM新加坡）上 `push2.eastmoney.com` 约78%请求返回502。
**根因是CDN节点的geo-block，不是IP被封。** 同一IP用 `push2delay.eastmoney.com` 备胎域名100%可达。
修复：在 `get_market_overview()` 中双域名轮换。

### 10a. push2不同端点路由不同：clist被拦但kamt.kline可通（2026-07-21 实测发现）
push2下 `api/qt/clist/get` 和 `api/qt/stock/get` 返回502，但**同一域名**的 `api/qt/kamt.kline/get` 可通。
根因是不同API路径走了不同CDN节点，不是域名级封禁。不能因为一个端点502就放弃整个域名。

### 10b. datacenter-web报表名已失效（2026-07-21 确认）
`datacenter-web.eastmoney.com/api/data/v1/get` 的 `RPT_MUTUAL_DEAL_STOCK` 报表名不再有效，
返回"报表配置不存在"。替代方案：北向数据走 `kamt.kline` 接口即可，不修复datacenter。

### 10c. 指数行情提供主力资金流字段（2026-07-21 发现）
`push2delay.eastmoney.com/api/qt/stock/get` 对1.000001(上证指数)的返回中，
f135-f150字段包含主力/超大单/大单的流入流出数据：
- f135=沪主力流入, f136=沪主力流出, f137=沪主力净额(亿)
- f141=沪超大单流入, f142=沪超大单流出, f143=沪超大单净额(亿)
- f144=深主力流入, f145=深主力流出, f146=深主力净额(亿)

## 14. 推荐数据源前必须从部署服务器实测（2026-07-21 用户纠正）

不要仅凭README、文档、或GitHub项目的描述就推荐某个API/数据源。必须：

1. 从Oracle ARM服务器发真实HTTP请求验证
2. 测试至少5次获取真实可用率（不是单次）
3. 测试多端点（同一域名不同路径可能行为不同）
4. 如果失败：尝试备胎域名（push2delay）、备胎路径（kamt代替clist）
5. 文档说"可用"不代表从你的服务器能访问

本会话教训：Vibe-Research的astock.py文档说东财接口可用，实测push2的clist是502。
但push2delay可用、push2的kamt.kline可用——这是实际测了才知道的。不要假设。

## 11. 修改后必须多轮验证（2026-07-18 用户要求）
用户明确要求：**多轮验证，各轮次覆盖不同维度，不为了通过测试而写测试。**
标准4轮验证框架（每fix必须经过 >=2个独立轮次）：
| 轮次 | 验证内容 | 数量级 |
| 第1轮 | 语法正确性 + 新功能结构 | 5-10项 |
| 第2轮 | 多源交叉验证 + 边界条件 | 15-25项 |
| 第3轮 | 回归测试 | 5-10项 |
| 第4轮 | 一体化全量验证 | 30-40项 |

## 12. 交易日自动验证（2026-07-18 设立）
验证不能等用户提醒。`trading_day_validate.py` 通过3轮cron自动运行：
- 09:35：API可达性 + `_stale`标记检查
- 13:00：交叉验证（腾讯vsAKShare涨跌、天天vsAKShare净值）
- 15:30：收盘数据准确性 + 归档完整性

## 13. 推送渠道统一为QQ Bot（2026-07-18 清理）
废弃飞书卡片路径（`send_morning.py`/`send_noon.py`/`send_closing.py`中的Feishu SDK）。
统一使用 `send_qqbot.py`（print Markdown到stdout，cron deliver=origin 自动投递）。
关键改动：send_*_cards.py删除.feishu-deps引用；run_*.py wrapper删除.feishu-deps环境变量；cron deliver从local改为origin。
