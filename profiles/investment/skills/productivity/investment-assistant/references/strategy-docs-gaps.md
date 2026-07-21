# 策略文档索引 & 实现差距

## 5份核心策略文档

所有文档托管在 `https://hermes-main-media.devtoy.xyz/fund-system/strategy/`：

| 文档 | 内容摘要 | 上次更新 |
|:----|:--------|:--------:|
| `SYSTEM_DESIGN_v3.md` | 系统架构、3条推送时间线、自校验系统、信号归因、P0/P1/P2待建清单 | 2026-06-30 |
| `STRATEGY_v2.md` | 信源权重(唐主任60%/小浣熊25%/莫非15%)、R2归档路径、代码清单 | 2026-06-26 |
| `KOL_ACCURACY_REPORT_v1.md` | 唐主任6/6命中✅、小浣熊逻辑自洽、IT精英为非信号源、黑话词汇表 | 2026-06-26 |
| `HOLIDAY_HANDLING_v1.md` | 2026年33个节假日硬编码、skip文件机制、2027年自动抓取占位 | 2026-06-26 |
| `TIMING_ANALYSIS_v1.md` | 周一数据空洞(76h旧数据)→修正方案、周六速报→新增cron、周五美股前瞻 | 2026-06-26 |

> 这些文档构成了整个系统的**设计说明书**。实际实现与设计存在以下差距。

---

## 推送流程的实际链路

```
cron触发 → run_*.py → collect_*.py (数据采集) → send_*_cards.py (格式化为Markdown)
                                                → send_qq_bot.py (分块推送)
```

所有任务均为 `no_agent=true` 模式，无需 LLM 参与。

---

## 实现差距全表

### Level 1：有脚本未注册（优先级最高）

| 设计文档要求 | 脚本情况 | 行动 |
|:------------|:--------|:----|
| 周六09:00 周末外盘速报 | `collect_weekend_data.py`✅ 已写239行 | 注册cron |
| 周六10:00 数据源验证 | `auto_validate_sources.py`✅ 已写229行 | 注册cron |
| 收盘后加仓信号监控 | `monitor_buy_signals.py`✅ 已写171行 | 注册cron |

### Level 2：代码已实现但未接cron

| 功能 | 位置 | 行动 |
|:----|:----|:----|
| KOL准确率周报生成 | `fund_tools.py:1895` `generate_signal_report()` | 写调用脚本+注册cron |
| 信号归因追踪 | `resolve_past_signals()` 已在收盘/午盘调用，但结果仅归档未推送 | 可选：加入周五/AI周报 |

### Level 3：设计差异需修正

| 项目 | 设计 | 实际 | 推荐修正 |
|:----|:----|:----|:--------|
| 早报时间 | 08:00 CST | 08:30 CST | cron改 `0 8 * * 1-5` |
| 周一外盘措辞 | 标注"上周五" | 未特殊处理 | 推送模板增加周一检测 |
| 周五收盘美股前瞻 | 增加"今晚美股关注" | 未实现 | send_closing_cards.py 加周五段 |

### Level 4：P0-P2 待开发

| 优先级 | 需求 | 说明 |
|:------:|:----|:------|
| 🔴 P0 | SPA移动端仪表盘 | 实时看持仓/板块/信号 |
| 🔴 P0 | 微信推送 | 目前只有QQ |
| 🔴 P0 | 触发式信号推送 | 非cron轮询，有信号主动推 |
| 🟡 P1 | 持仓盈亏计算 | `_user_portfolio.json` 不存在/空 |
| 🟡 P1 | 偏离度调仓提醒 | 黄金>20%、科技>45%预警 |
| 🟡 P1 | 新赛道发现 | 未持仓板块连续走强提示 |
| 🟡 P1 | 莫非是托接入 | 唐主任买入信号时查对立观点 |
| 🟢 P2 | 周末回顾信息图 | baoyu-infographic生成 |
| 🟢 P2 | 博主画像月更新 | 自动拉新数据 |
| 🟢 P2 | 风险预警系统 | 单日跌5%/连跌3日告警 |

---

## 关键约束与边界

| 约束 | 说明 |
|:----|:------|
| 数据源 | 腾讯API → A股行情/板块/成交额/涨跌家数；天天基金 → 基金估值；Yahoo → 外盘；微博桌面API → KOL |
| 节假日 | `is_trading_day()` 检查周末 + 2026年33个法定假日，非交易日写 `_skip.txt`/`_noon_skip.txt`/`_closing_skip.txt` |
| 微博凭据 | ~7天过期，看门狗每天23:30检测，过期生成二维码推送到主频道 |
| 腾讯API局限 | `prev_close`盘中可获取，但昨日涨跌幅无法从实时API推导（需前日收盘对比） |
| 数据降级 | 昨日数据恢复: 快照→JSONL存档→prev_close盘中保底 |
| 推送平台 | QQ Bot API v2，分块 ≤3800字符/条，`send_qq_bot.py` 管理 |

---

## 脚本目录总览

```
/opt/data/scripts/
├── fund_tools.py          # 核心库：采集+自校验+信号归因+量价分析
├── run_morning.py         # 早报wrapper (no_agent)
├── run_noon.py            # 午报wrapper (no_agent)
├── run_closing.py         # 收评wrapper (no_agent)
├── collect_morning_data.py  # 早盘采集
├── collect_noon_data.py     # 午盘采集
├── closing_review.py        # 收盘复盘
├── send_morning_cards.py    # 早报格式
├── send_noon_cards.py       # 午报格式
├── send_closing_cards.py    # 收评格式
├── send_qq_bot.py           # QQ API推送
├── weibo_watchdog.py        # 微博凭据看门狗
├── collect_weekend_data.py  # 周六外盘速报（🟡 未注册cron）
├── auto_validate_sources.py # 数据源验证（🟡 未注册cron）
├── monitor_buy_signals.py   # 加仓信号监控（🟡 未注册cron）
└── kol_*.py                 # 博主分析工具集
```
