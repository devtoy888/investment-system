# Fund System R2 Documentation Index

All documents stored under `fund-system/` path on R2 (https://hermes-main-media.devtoy.xyz/).

## Evolution / Versioning

| File | Description |
|------|-------------|
| `fund-system/evolution/ROADMAP.md` | **全量任务跟踪** — 已完成/待办/待验证/已知问题/文件索引 |
| `fund-system/evolution/roadmap.html` | **自适应前端仪表盘** — 手机查看推荐（fetch.md + marked.js渲染） |
| `fund-system/evolution/EVOLUTION_LOG.md` | **进化日志** — 每次系统变更自动追加记录 |
| `fund-system/evolution/weekly-{N}.md` | 周度复盘（每周日自动生成） |
| `fund-system/evolution/VIBE_TRADING_EVAL.md` | Vibe-Trading完整评估报告 |
| `fund-system/evolution/VIBE_TRADING_EVAL.html` | Vibe-Trading评估报告前端页面 |
| `fund-system/strategy/SYSTEM_DESIGN_v11.md` | **最新** v11 — Vibe-Trading评估+数据源修复 |
| `fund-system/strategy/SYSTEM_DESIGN_v10.md` | v10 — 数据源修复+决策日志增强 |
| `fund-system/strategy/SYSTEM_DESIGN_v9.md` | v9 — 风险预警系统上线 |
| `fund-system/strategy/SYSTEM_DESIGN_v8.md` | v8 — 持仓入库+偏离度检测 |
| `fund-system/strategy/SYSTEM_DESIGN_v7.md` | v7 — 3天验证+方向检测+时间修正 |
| `fund-system/strategy/SYSTEM_DESIGN_v6.md` | v6 — 周度复盘+决策日志 |
| `fund-system/strategy/SYSTEM_DESIGN_v5.md` | v5 — 决策日志+KOL归因修复 |
| `fund-system/strategy/SYSTEM_DESIGN_v4.md` | v4 — 自进化系统（自检+去重+进化存档） |
| `fund-system/strategy/SYSTEM_DESIGN_v3.md` | v3 — 并行采集+自校验+信号归因 |
| `fund-system/strategy/SYSTEM_DESIGN_v2.md` | v2 — 迭代版 |
| `fund-system/strategy/SYSTEM_DESIGN_v1.md` | v1 — 初始设计 |

## Strategy / Design

| File | Description |
|------|-------------|
| `fund-system/strategy/TIMING_ANALYSIS_v1.md` | US/A-share timezone gap analysis and fixes |
| `fund-system/strategy/HOLIDAY_HANDLING_v1.md` | Chinese holiday calendar and is_trading_day() logic |
| `fund-system/strategy/STRATEGY_v2.md` | Investment strategy document |
| `fund-system/strategy/KOL_ACCURACY_REPORT_v1.md` | 6/6 主任 prediction verification + 小浣熊画像 |

## Data Files (daily)

| File | Description |
|------|-------------|
| `fund-system/data/portfolio/portfolio-2026-07-15.{csv,md,html}` | **持仓明细** — 12支基金含成本/份额/盈亏（三件套） |
| `fund-system/data/decisions.jsonl` | 每日决策日志（交易日16:25，含持仓市值快照） |
| `fund-system/data/daily-snapshots.jsonl` | 每日收盘价格快照（含portfolio_value） |
| `fund-system/data/fund-daily-trend.jsonl` | 基金日趋势追踪（risk_warning.py每日写入） |
| `fund-system/data/morning-briefs.jsonl` | 早盘归档（已去重） |
| `fund-system/data/noon-briefs.jsonl` | 午盘归档（已去重） |
| `fund-system/data/closing-reviews.jsonl` | 收盘归档（已去重，含market_accuracy） |
| `fund-system/data/signals.jsonl` | 原始KOL信号 |
| `fund-system/data/signals-resolved.jsonl` | 已解析信号（含magnitude/signal_strength） |

## KOL Profiles

| File | Description |
|------|-------------|
| `fund-system/data/kol_profiles/final_profiles.json` | All KOL profile data |
| `fund-system/data/kol_profiles/xueqiu_tang_analysis.md` | 主任's 雪球 account analysis |

## How to query

```bash
# Latest design doc
curl -s https://hermes-main-media.devtoy.xyz/fund-system/strategy/SYSTEM_DESIGN_v11.md

# ROADMAP (markdown original)
curl -s https://hermes-main-media.devtoy.xyz/fund-system/evolution/ROADMAP.md

# ROADMAP (adaptive HTML — mobile recommended)
# Just open in browser: https://hermes-main-media.devtoy.xyz/fund-system/evolution/roadmap.html

# Evolution log
curl -s https://hermes-main-media.devtoy.xyz/fund-system/evolution/EVOLUTION_LOG.md

# Vibe-Trading Evaluation (markdown)
curl -s https://hermes-main-media.devtoy.xyz/fund-system/evolution/VIBE_TRADING_EVAL.md

# Vibe-Trading Evaluation (HTML)
# Open in browser: https://hermes-main-media.devtoy.xyz/fund-system/evolution/VIBE_TRADING_EVAL.html

# This week's review (if exists)
curl -s https://hermes-main-media.devtoy.xyz/fund-system/evolution/weekly-$(date +%V).md

# Decision log (latest 5 lines)
curl -s https://hermes-main-media.devtoy.xyz/fund-system/data/decisions.jsonl | tail -5

# Daily snapshots (latest 5 lines)
curl -s https://hermes-main-media.devtoy.xyz/fund-system/data/daily-snapshots.jsonl | tail -5

# Portfolio (CSV — import into spreadsheet)
curl -s https://hermes-main-media.devtoy.xyz/fund-system/data/portfolio/portfolio-2026-07-15.csv
```
