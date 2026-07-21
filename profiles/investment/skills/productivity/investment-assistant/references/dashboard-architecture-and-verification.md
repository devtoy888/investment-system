# 看板架构与数据源验证（2026-07-21 会话总结）

## 核心教训：数据源必须先验证再推荐

**不要只读README就推荐API。必须从服务器实测后再说。** 本会话因推荐东财接口
而未从Oracle ARM验证，被用户指出。

| 必须做 | 不要做 |
|--------|--------|
| `curl` / `urllib` 从服务器真实请求 | 读文档就推荐 |
| 连续请求5次验证可用率 | 一次成功就称"100%可用" |
| 找到备胎/降级路径再推荐 | 只推荐一条路 |
| 给出HTTP状态码+响应内容 | "理论上可用" |

### 实测发现

```
push2.eastmoney.com clist     → 502 (Oracle IP被CDN拦截)
push2delay.eastmoney.com clist → 200 ✅ 100%可用 (替代方案)
push2.eastmoney.com kamt.kline → 200 ✅ (不同CDN节点)
腾讯 qt.gtimg.cn              → 200 ✅ 100%
天天基金 fundgz               → 94%
同花顺 hexin                  → 48% (保留备援)
```

**规律**：同一域名的不同端点可能走不同CDN，需要分开测试。

### 借鉴开源代码原则

参考Vibe-Research/vibe-trading等项目的astock.py时：
1. 提取API地址和参数模式
2. 从你的服务器实测可用性
3. 只有实测通过才用
4. 不要import对方整个代码库，用标准库实现需要的部分
5. 只需3-5个函数，不需要全部40个端点

## 前端看板架构决策

| 决策 | 选型 | 理由 |
|------|------|------|
| 框架 | React 19 + TypeScript + Vite | 组件化、类型安全、参考Vibe-Research |
| 图表 | ECharts ^6.0.0 | 原生Gauge(偏离度)+Heatmap(轮动)+Candlestick(扩展) |
| 部署 | Cloudflare Pages + D1 + Workers | 全免费额度，自动构建 |
| 数据流 | JSONL(真相源) → D1(查询) → R2(兜底) | 三层架构，前端只读不写 |
| 开发 | TDD + 独立审查 + 自动部署 | 按DEVELOPMENT_GUIDE.md流程 |

### 数据架构

```
JSONL（服务器本地，唯一真相源）
  cron写, 前端不写 → 12个文件
  ↓
D1（Cloudflare SQLite，查询加速）
  sync_to_d1.py 每日16:20同步
  D1挂了 → 数据安全（真相源在JSONL）
  ↓
R2（CDN缓存，兜底）
  cron每次推送后写 dashboard_latest.json
  前端: 优先D1 → 降级R2 → 极端降级localStorage
```

### dashboard.json 分两版

| 文件 | 更新时机 | 用途 |
|------|---------|------|
| `dashboard_latest.json` | 每次cron推送后 | 显示最新可用数据，标注时间戳 |
| `dashboard_full.json` | 交易日16:20 | 完整日数据，归档用 |

### 页面体系（8页）

| 页面 | 数据来源 | 图表类型 |
|------|---------|---------|
| 🏠 总览 | R2 dashboard_latest.json | Metric卡片+柱状图 |
| 💼 持仓 | D1 + seed_portfolio | 饼图+Gauge仪表盘(84%红针) |
| 📈 板块 | R2 JSON (50行业) | 柱状图+Heatmap轮动 |
| 🔍 行情总览 🆕 | R2 + 东财 | 估值分位条形图+研报列表 |
| 📡 资讯雷达 🆕 | signals-resolved.jsonl(953条) | ECharts博主画像 |
| 📅 历史趋势 | D1 SQL | AreaChart+Heatmap相关性 |
| 📜 操作记录 | operations/ → D1 | 时间线 |
| 🤖 信号系统 | JSONL + signal_engine | 状态仪表 |

### 开发工作流

```
你发指令 → 评估 → Plan规划 → TDD(红绿) → 代码审查 → git push → Pages自动部署
```

完整开发规范：https://hermes-main-media.devtoy.xyz/fund-system/strategy/DEVELOPMENT_GUIDE.md

### Token要求

| Token | 用途 |
|-------|------|
| `GITHUB_TOKEN` | 创建仓库、push代码 |
| `CLOUDFLARE_API_TOKEN` | Pages+D1管理（权限: Pages Edit + D1 Edit + Workers Scripts Edit） |

### 交互式LLM

```javascript
// _worker.js — POST /api/ask
// Worker环境变量存 DEEPSEEK_API_KEY
// 前端每个页面右下角💬问AI按钮，自动携带当前页面上下文
// SSE流式返回，逐字渲染
```
