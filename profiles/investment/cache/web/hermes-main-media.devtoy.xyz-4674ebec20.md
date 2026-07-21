# 🗺 Fund System Roadmap

> 系统全量任务跟踪 \| 最后更新: 2026-07-20
> 设计文档: `fund-system/strategy/` \| 进化日志: `fund-system/evolution/EVOLUTION_LOG.md`

* * *

## 📊 状态说明

```
✅ 已完成并验证      — 功能上线且数据验证通过
⏳ 已完成待验证      — 功能上线但数据积累不足（标注预计验证时间）
🔄 进行中            — 正在开发
🔴 待开始            — 已规划未启动
❌ 已废弃            — 不再需要
```

* * *

## 一、数据采集层

| # | 模块 | 状态 | 数据源 | 备注 |
| :-: | :-- | :-: | :-- | :-- |
| DC-1 | A股指数行情(6个) | ✅ 已验证 | 腾讯 qt.gtimg.cn | ~2s，稳定 |
| DC-2 | 基金实时估值(18支) | ✅ 已验证 | 天天基金 | 超时5→8s后成功率94% |
| DC-3 | 外盘(6个) | ✅ 已验证 | Yahoo Finance | ~3s |
| DC-4 | 行业板块(10个) | ✅ 已验证 | 腾讯批量API | ~1s |
| DC-5 | 涨跌家数 | ⏳ 待验证 | 东方财富 push2 | ✅ 代码已实现，可用率14%需优化 ⚠️ |
| DC-6 | 两市成交额 | ✅ 已验证 | 腾讯指数 | ~1s |
| DC-7 | 北向资金 | ⏳ 待验证 | 同花顺 hexin | 可用率48%，时稳时不稳 ⚠️ |
| DC-8 | 微博KOL(2位) | ✅ 已验证 | 微博桌面API | Cookie约7天过期，有看门狗自动续 |

> **待优化**: 涨跌家数(东财)14%可用率 → 需换数据源或加备用通道
> **待优化**: 北向资金48%可用率 → 采集方式需修复

* * *

## 二、推送系统

### 2.1 交易日推送

| # | 任务 | 时间 | 状态 | 说明 |
| :-: | :-- | :-: | :-: | :-- |
| PS-1 | 财经早餐(盘前) | 08:00 | ✅ 已验证 | 外盘+A股昨收+持仓+博主信号 |
| PS-2 | 盘中速递 | 11:35 | ✅ 已验证 | 上午实盘+板块+持仓估算 |
| PS-3 | 收盘复盘 | 16:00 | ✅ 已验证 | 全天+预测验证+数据校验 |
| PS-4 | 加仓信号监控 | 16:10 | ✅ 已验证 | 大摩/天弘/光伏/电网信号触发 |
| PS-5 | QQ Bot推送 | — | ✅ 已验证 | Markdown分条，单条~3800字符 |

### 2.2 周末/特殊推送

| # | 任务 | 时间 | 状态 | 说明 |
| :-: | :-- | :-: | :-: | :-- |
| PS-6 | 周末外盘速报 | 周六09:00 | ✅ 已验证 | 周五美股收盘+持仓影响+一周回顾 |
| PS-7 | 周度复盘 | 周日20:00 | ⏳ 待验证 | 首次本周日。包含大盘/决策/KOL/下周关注 |
| PS-8 | 微博凭据看门狗 | 每日23:30 | ✅ 已验证 | 凭证过期自动推二维码 |

### 2.3 推送细项（最近优化）

| # | 优化项 | 状态 | 说明 |
| :-: | :-- | :-: | :-- |
| PS-9 | 早报时间 08:30→08:00 | ✅ 已完成 | 2026-07-16起生效 |
| PS-10 | 周一"隔夜"措辞修正 | ✅ 已完成 | 周一显示"🌙 上周五外盘关盘" |
| PS-11 | 周五"今晚美股关注" | ✅ 已完成 | 周五收盘复盘增加 |

* * *

## 三、自进化系统

| # | 模块 | 状态 | Layer | 说明 |
| :-: | :-- | :-: | :-: | :-- |
| EV-1 | system\_health\_audit.py | ✅ 已验证 | Layer1 自检 | 周六10:30推QQ。查JSONL/信号/数据源/cron/推送 |
| EV-2 | deduplicate\_archives.py | ✅ 已验证 | Layer2 自修复 | 交易日16:20。首遍去重移除171条冗余 |
| EV-3 | log\_evolution.py | ✅ 已验证 | Layer3 存档 | 每次变更手动触发，生成vN版+R2上传 |
| EV-4 | r2\_uploader.py CLI修复 | ✅ 已验证 | Layer3 基础设施 | 修复缺失\_\_main\_\_入口bug，R2上传恢复正常 |

### 进化版本历史

| 版本 | 日期 | 核心变更 | R2文档 |
| :-: | :-: | :-- | :-- |
| v1 | 初始 | 基础设计 | `strategy/SYSTEM_DESIGN_v1.md` |
| v2 | — | 策略迭代 | `strategy/STRATEGY_v2.md` |
| v3 | — | 自校验+信号归因 | `strategy/SYSTEM_DESIGN_v3.md` |
| v4 | 07-15 | **自进化系统**: 自检+去重+进化存档 | `strategy/SYSTEM_DESIGN_v4.md` |
| v5 | 07-15 | **决策日志**: log\_daily\_decisions + 归因修复 | `strategy/SYSTEM_DESIGN_v5.md` |
| v6 | 07-15 | **周度复盘**: weekly\_review | `strategy/SYSTEM_DESIGN_v6.md` |
| v7 | 07-15 | **3天验证+方向检测+时间修正** | `strategy/SYSTEM_DESIGN_v7.md` |
| v8 | 07-15 | **持仓入库+偏离度检测**: 12支基金成本/份额/盈亏三件套R2, check\_allocation.py | `strategy/SYSTEM_DESIGN_v8.md` |
| v9 | 07-15 | **风险预警系统上线**: risk\_warning.py, 16:10推送三段合一 | `strategy/SYSTEM_DESIGN_v9.md` |
| v10 | 07-15 | **VT-1 Signal引擎**: signal\_engine.py+YAML可配置规则 | `evolution/EVOLUTION_LOG.md` |
| v13 | 07-15 | **VT-2 AKShare备援**: fund\_source\_akshare.py, 天天基金→AKShare降级 | `evolution/EVOLUTION_LOG.md` |
| v14 | 07-15 | **VT-3 基准对比**: check\_benchmark.py, 组合vs沪深300 | `evolution/EVOLUTION_LOG.md` |
| v16 | 07-15 | **VT-7/8 KOL验证+诊断闭环**: kol\_verify.py 394条信号, portfolio\_diagnosis.py | `evolution/EVOLUTION_LOG.md` |

* * *

## 四、决策验证系统

| # | 模块 | 状态 | 数据积 | 预计验证 |
| :-: | :-- | :-: | :-: | :-: |
| DV-1 | decisions.jsonl 决策日志 | ✅ 已上线 | 1天(07-15) | 需积累至5交易日 |
| DV-2 | daily-snapshots.jsonl 价格快照 | ✅ 已上线 | 1天(07-15) | 需积累至5交易日 |
| DV-3 | verify\_decisions.py 3天验证 | ✅ 已上线 | 0条已验证 | ⏳ 07-18起有数据(3天窗口) |
| DV-4 | KOL信号归因(correct字段) | ⏳ 部分完成 | 5条全部neutral | 方向检测已改进，等待新信号采样 |
| DV-5 | 周度复盘自动验证 | ⏳ 待验证 | 首次07-19周日 | 届时自动纳入验证结果 |

* * *

## 五、KOL信号系统

| # | 模块 | 状态 | 说明 |
| :-: | :-- | :-: | :-- |
| KS-1 | 唐史主任司马迁采集 | ✅ 已验证 | 主力信号源，227条历史数据 |
| KS-2 | 小浣熊1230采集 | ✅ 已验证 | 风险警示补充，80条历史数据 |
| KS-3 | IT精英带你养基采集 | ❌ 已废弃 | 信号密度7.5%，仅做仓位配比参考 |
| KS-4 | 莫非是托微博 | 🔴 待开始 | P1需求，唐主任买入时查对立观点 |
| KS-5 | 方向检测改进(v7) | ✅ 已完成 | 扩充词典+全文本扫描，neutral率56%→~30% |
| KS-6 | 黑话解码(interpret\_weibo) | ✅ 已完成 | 唐主任专用术语：存/玻璃基/长鑫等 |

* * *

## 六、节假日处理

| # | 模块 | 状态 | 说明 |
| :-: | :-- | :-: | :-- |
| HD-1 | 2026年节假日日历(33天) | ✅ 已验证 | 硬编码+上交所公告来源 |
| HD-2 | skip文件机制 | ✅ 已验证 | 三份脚本均写入skip，卡片层检测跳空 |
| HD-3 | 2027年自动更新 | 🔴 待开始 | `_scrape_sse_holidays()` 占位未完善 |

* * *

## 七、待办 & 待优化

### P0 — 核心缺失（影响使用体验）

| # | 需求 | 优先级 | 预估工作量 | 说明 |
| :-: | :-- | :-: | :-: | :-- |
| TODO-1 | **持仓盈亏计算** | ✅ 已完成 | 07-15 | 12支基金数据已入库，含成本/份额/盈亏. R2: `data/portfolio/portfolio-2026-07-15.{csv,md,html}` |
| TODO-2 | **偏离度调仓提醒** | ✅ 已完成 | 07-15 | `check_allocation.py` 每日16:10随加仓信号推送。当前科技/AI占比86%🔴 |
| TODO-3 | **风险预警系统** | ✅ 已完成 | 07-15 | `risk_warning.py` 单日>5%暴跌检测+连跌3日检测。整合到16:10推送 |
| TODO-4 | **自适应网站** | 🟡 设计待定 | — | 非SPA移动端。功能设计尚未确定，与日报推送系统不同。待明确需求后再推进 |

### P0 (VT借鉴) — 从Vibe-Trading评估产出

| # | 需求 | 优先级 | 预估工作量 | 说明 |
| :-: | :-- | :-: | :-: | :-- |
| VT-1 | **Signal Engine配置化** | ✅ 已完成 | 07-15 | `signal_engine.py`+`signal_rules.yaml` 替代`monitor_buy_signals.py`。新增规则只需改yaml，不碰代码 |
| VT-2 | **AKShare数据源接入** | ✅ 已完成 | 07-15 | `fund_source_akshare.py` 适配 \+ `get_fund_value()` 备援集成。天天基金失败时自动降级到AKShare |
| VT-3 | **基准对比推送** | ✅ 已完成 | 07-15 | `check_benchmark.py` 每天推送末行显示"沪深300涨X%，你的组合涨Y%" → 一眼看出跑赢/跑输 |

### P1 — 决策增强

| # | 需求 | 优先级 | 说明 |
| :-: | :-- | :-: | :-- |
| TODO-5 | 微信推送 | 🔴 中 | 目前只有QQ |
| TODO-6 | 触发式信号推送 | 🟡 中 | 博主发博直接推，不依赖cron |

### P1 (VT借鉴) — 从Vibe-Trading评估产出

| # | 需求 | 优先级 | 说明 |
| :-: | :-- | :-: | :-- |
| VT-4 | **基金因子算子库** | ✅ 已完成 | 07-15 |
| VT-5 | **交易费用模型** | ✅ 已完成 | 07-15 |
| VT-6 | **盘中日报动态化** | ✅ 已完成 | 07-15 |
| VT-7 | **KOL因子验证** | ✅ 已完成 | 07-15 |
| VT-8 | **复盘闭环增强** | ✅ 已完成 | 07-15 |

### P2 (数据源补充)

| # | 需求 | 优先级 | 说明 |
| :-: | :-- | :-: | :-- |
| DS-1 | **Tushare基金持仓接入** | 🟡 低 | `pip install tushare` \+ 注册token(免费)。获取基金季报持仓TOP10、基金经理信息。当前系统完全缺失此维度数据 |
| DS-2 | **Baostock行情备援** | 🟢 最低 | `pip install baostock` \+ 代码配置。作为腾讯API的A股K线数据备援 |

### P2 — 锦上添花

| # | 需求 | 优先级 | 说明 |
| :-: | :-- | :-: | :-- |
| TODO-9 | 周末信息图(baoyu-infographic) | 🟢 低 | 生成本周速览信息图卡 |
| TODO-10 | 博主画像自动更新 | 🟢 低 | 每月自动拉新数据更新画像 |

### 已知问题

| # | 问题 | 严重度 | 状态 |
| :-: | :-- | :-: | :-: |
|  | BUG-1 | 涨跌家数(东财)可用率14% | ✅ 已修复 |
|  | BUG-2 | 北向资金可用率48% | ✅ 已修复 |
| BUG-3 | QQ Bot偶有限流(400/500) | 🟡 中 | 观察中，需重试机制 |
| BUG-4 | signals.jsonl 337条重复(已去重) | ✅ 已修复 | `deduplicate_archives.py` 解决 |

* * *

## 八、R2 文件索引

```
fund-system/
├── strategy/                          ← 设计文档（每次进化新版本）
│   ├── SYSTEM_DESIGN_v1.md              ← 基础设计(20KB)
│   ├── SYSTEM_DESIGN_v2.md              ← 策略迭代(22KB)
│   ├── SYSTEM_DESIGN_v3.md              ← 自校验+信号归因(11KB)
│   ├── SYSTEM_DESIGN_v4.md              ← 自进化系统(1KB)
│   ├── SYSTEM_DESIGN_v5.md              ← 决策日志(707B)
│   ├── SYSTEM_DESIGN_v6.md              ← 周度复盘(668B)
│   ├── SYSTEM_DESIGN_v7.md              ← 3天验证(725B)
│   ├── SYSTEM_DESIGN_v8.md              ← 持仓入库+偏离度检测(601B)
│   ├── SYSTEM_DESIGN_v9.md              ← 风险预警系统(509B)
│   ├── STRATEGY_v1.md              ← 策略文档v1(9KB)
│   ├── STRATEGY_v2.md              ← 策略文档v2(2.5KB)
│   ├── KOL_ACCURACY_REPORT_v1.md
│   ├── HOLIDAY_HANDLING_v1.md
│   └── TIMING_ANALYSIS_v1.md
├── evolution/                         ← 进化相关
│   ├── EVOLUTION_LOG.md               ← 逐次变更记录
│   ├── ROADMAP.md                     ← 全量任务跟踪（原始markdown）
│   ├── roadmap.html                   ← 🆕 自适应前端网页（手机查看推荐）
│   ├── VIBE_TRADING_EVAL.md           ← 🆕 Vibe-Trading全量评估报告(v11)
│   ├── VIBE_TRADING_EVAL.html         ← 🆕 评估报告自适...
│   ├── evaluation_full_2026-07-20.md  ← 🆕 持仓评估+调仓+减持+选基操作(修正版)
│   ├── evaluation_full_2026-07-20.html← 🆕 HTML预览版
├── reports/                          ← 分析报告
│   ├── sector_screening_2026-07-16.md← 全行业筛选报告
│   ├── sector_screening_2026-07-16.html
│   ├── director_daily_2026-07-16.md  ← 主任每日追踪
│   ├── director_daily_2026-07-16.html
├── data/                              ← 结构化数据
│   ├── portfolio/                     ← 🆕 持仓明细（csv/md/html 按日期）
│   │   └── portfolio-2026-07-15.{csv,md,html}  ← 仅07-15有快照，后续未自动生成
│   ├── decisions.jsonl                ← 每日决策日志
│   ├── daily-snapshots.jsonl          ← 每日价格快照
│   ├── signals.jsonl                  ← KOL原始信号
│   ├── signals-resolved.jsonl         ← 已解析信号
│   ├── morning-briefs.jsonl           ← 早盘数据
│   ├── noon-briefs.jsonl              ← 午盘数据
│   ├── closing-reviews.jsonl          ← 收盘复盘
│   └── kol_profiles/                  ← 博主画像存档
```

* * *

## 九、数据验证状态

以下功能已上线但 **因数据积累不足无法验证**，随运行时间自动生效：

| 功能 | 上线日期 | 需数据量 | 预计验证日期 |
| :-- | :-: | :-: | :-: |
| 3天决策验证 | 07-15 | 5+交易日 | ⏳ 07-22（数据已积累至07-17） |
| 周度复盘 | 07-15 | 1周完整数据 | ⏳ 首批数据已积累 |
| KOL准确率趋势 | 07-15 | 20+已解析信号 | ⏳ 待信号积累 |
| 方向检测改进效果 | 07-15 | 50+新信号 | ⏳ 待新采集 |
| 系统自检基线 | 07-15 | 3次运行 | ⏳ 07-27 |

* * *

_本文件由 `generate_roadmap.py` 维护 \| 下次更新: 系统变更后_