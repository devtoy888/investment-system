# Vibe-Research 评估摘要 (2026-07-06)

完整报告：https://hermes-main-media.devtoy.xyz/fund-system/reports/vibe-research-evaluation.md

## 结论：互补而非替代

Vibe-Research 是个人 AI 投研 Web 看板（主动查看），三推送是推送系统（被动接收）。

## 可提取的 3 个模块（高价值，低实现成本）

| # | 模块 | 来源 | 代码量 | Value-Add | 推送位置 | 实施状态 |
|:-:|------|------|:------:|:---------:|---------|:--------:|
| 1 | **短线情绪** — 连板梯队/封板率/炸板率/晋级率 | Vibe `market.py:_emotion()` | ~100行 | **高** | 收盘复盘「短线情绪」板块 | ⏳ **待执行**（东财 push2ex API 在境外服务器不可达，需解决网络问题） |
| 2 | **市场情绪机械分档** — 冰点/偏弱/中性/偏强/普涨 | Vibe 涨跌家数分档 | ~5行 | 中→高 | 现有涨跌家数旁附加 | ✅ **已实施**（P0, 2026-07-06, `grade_market_sentiment()` 已集成到三推送） |
| 3 | **赛道 RSS 资讯** — 108 源按 12 赛道分类 | Vibe `news_sources.json` + `newsradar.py` | ~80行 | **高** | 盘前推送「隔夜赛道要闻」 | ⏳ **待执行**（不受地域限制，可随时接入） |

## 不 fork 全量的理由
- 缺基金净值、缺 KOL 微博、无推送机制
- 19 板块中 17 个是空壳（`verified: false, nodes: []`）
- 东财接口对大陆住宅 IP 有间歇风控

## 设计语言可参考
- GlassCard 组件（CSS 毛玻璃+暖橙主题）
- ValBand 估值分位带（绿灰红三段可视化）
- AI 可插拔架构（CLI/API/MCP 三种模式）
