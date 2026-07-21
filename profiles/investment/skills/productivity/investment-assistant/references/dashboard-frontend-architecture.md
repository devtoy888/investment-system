# 投资看板前端架构设计

> 2026-07-21会话产出。完整方案见R2: fund-system/strategy/DASHBOARD_DESIGN_PLAN_v3.md

## 核心原则

1. cron采集, 前端消费 — 不重复数据采集
2. 三层降级 — Worker/D1 -> R2 JSON -> localStorage缓存
3. 前端只展示, 不执行操作 — 操作通过QQ Bot + cron完成
4. 所有数据源从实际服务器实测验证 — 不基于README推荐

## 数据流

JSONL(本地真相源) -> D1(查询缓存) -> R2(CDN兜底) -> Worker API -> Frontend SPA

- 今日实时数据: R2 dashboard_latest.json (每次推送后更新)
- 历史趋势数据: D1 portfolio_snapshots表 (交易日16:20同步)
- KOL信号: R2 signals-resolved.json (~4小时上传)

## 技术栈

| 层 | 选型 | 理由 |
|---|------|------|
| 框架 | React 19 + TypeScript + Vite | 用户纠正: 纯JS不可维护 |
| 图表 | ECharts 6 | Recharts缺Gauge/Heatmap |
| 样式 | Tailwind CSS | Vibe-Research同款 |
| 图标 | lucide-react | Vibe-Research同款 |
| API | Cloudflare Workers (_worker.js) | 同域部署无CORS |
| 数据库 | Cloudflare D1 | 5GB免费, 1000年够用 |
| 部署 | Cloudflare Pages | auto-deploy from git |

## 8页面清单

1. 总览 - 大盘卡片+组合盈亏+板块TOP5+涨跌家数+cron摘要+风险
2. 持仓 - 14基金表+ECharts Gauge(偏离度84%红针)+饼图+建仓进度
3. 板块 - 涨跌排名+资金流柱状图+轮动热力图+板块-持仓关联
4. 行情总览 - 指数卡片+外盘+估值分位+行业研报列表
5. 资讯雷达 - KOL时间线+画像ECharts+RSS+AI提炼Tab
6. 历史趋势 - 净值曲线+单基金走势+相关性矩阵
7. 操作记录 - 时间线+类型统计
8. 信号系统 - 引擎状态+KOL准确性追踪

## 交互式LLM

Worker代理 POST /api/ask -> DeepSeek API (与cron bot同一Key) -> SSE流式返回
每个页面自动拼接上下文(当前页面数据)随请求发送。

## 数据源验证纪律

1. 从Oracle ARM服务器(152.70.91.4)实际服务器实测
2. 用urllib标准库测试(不依赖requests/akshare)
3. 连续5-10次统计可用率
4. 验证返回数据格式
5. 区分CDN节点问题 vs API不可用
6. 写验证文档

## 已知技术风险

- Worker 30秒CPU限制(免费版): DeepSeek复杂分析约15-25秒, 在限额内
- CORS: Worker和Pages必须同域部署(_worker.js方式, 不单独部署Worker)
- dashboard.json生成时机: 分latest(每次推送)和full(收盘)两版

## 关键纠正(2026-07-21用户指出)

- React可以部署到Cloudflare Pages (Vite build -> dist/)
- ECharts优于Recharts (Gauge仪表盘 + Heatmap热力图)
- 基金投资者也需要市场数据(板块/资金流/行情)
- 不要在prompt中过度约束AI判断
