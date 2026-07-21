---
name: investment-dashboard-architecture
title: 投资系统前端看板架构
description: >-
  个人基金投资系统的前端看板设计与技术选型。React 19 + TypeScript + Vite +
  ECharts + Tailwind CSS。部署到Cloudflare Pages，D1数据库，
  Workers API层。
  覆盖：技术选型决策依据、项目结构、数据流三层架构、Worker API端点、
  交互式LLM查询、图表库评估、8页面体系、资讯雷达+KOL展示、已知陷阱。
tags: [dashboard, frontend, react, echarts, cloudflare-pages, d1, architecture]
triggers:
  - 设计看板 / 做可视化 / 画图表
  - 前端框架选型 / React还是Vue / chart库选型
  - 部署到Cloudflare / Pages怎么配 / D1怎么用
  - 看板数据流 / 从服务器到前端的数据链路
  - 怎么展示持仓 / 板块分析可视化
  - 参考Vibe-Research / Vibe-Trading搭看板
  - ECharts还是Recharts / Ant Charts评估
  - 纯HTML还是React / 单页应用SPA
  - 历史趋势页面 / 净值曲线 / 热力图 / 仪表盘
  - 资讯雷达 / KOL信号展示 / 博主画像
  - 交互式LLM / 问AI / Worker调DeepSeek
  - 更新方案文档到R2 / md+html成对上传
---

# 投资系统前端看板架构

## 核心原则（从用户多次纠正中提炼）

### 1. 用成熟框架，不手造轮子

| 错误做法（被纠正过） | 正确做法 |
|-------------------|---------|
| 手写SVG图表 | 用 ECharts（Vibe-Research同款，`echarts ^6.0.0`） |
| 纯HTML/CSS/JS SPA | React 19 + TypeScript + Vite |
| 手写CSS | Tailwind CSS（Vibe-Research同款） |
| 图片图标 | lucide-react（Vibe-Research同款） |

### 2. 用Cloudflare生态，不自己搭服务器

| 服务 | 用途 | 免费额度 | 够用吗 |
|------|------|---------|--------|
| Pages | SPA托管 | 无限站点/带宽 | ✅ 100%够 |
| D1 | 结构化历史数据 | 5GB | ✅ 2MB/年，用1000年 |
| Workers | API查询层 | 10万次/天 | ✅ 500次/天 |
| R2 | 文件/报告存储 | 10GB | ✅ 50MB |

**不需要在Oracle服务器上跑任何前端服务**——构建在Pages CI完成，产物是纯静态文件。

### 3. 基金投资者也需要市场数据

**被用户纠正过**：基金看板不能只看基金净值，需要展示：
- 大盘指数——影响所有基金净值
- 板块资金流——判断赛道冷热（如半导体净流入166亿）
- 行业涨跌排名——交叉验证KOL信号
- 涨跌家数——判断系统性风险
- 北向资金——外资态度（恒生科技直接相关）
- 行业研报——辅助配置决策

**数据来源优先级**（从Oracle ARM实测）：
- push2delay.eastmoney.com → 100%可用 ✅（板块资金流+涨跌排行+涨跌家数+北向）
- push2.eastmoney.com → clist 502, 但 kamt.kline 可用 ✅（不同CDN路由）
- 腾讯 qt.gtimg.cn → 始终可用 ✅（指数行情）

### 4. 代码必须纳入版本控制

155+ Python脚本在服务器上裸奔 → 必须Git管理。每日自动commit，关键修改手动push。

### 5. 所有API推荐前必须从用户服务器实测

**被用户严厉纠正过**：不要只看README就推荐数据源。必须编写测试脚本从服务器真实运行，统计可用率，验证返回格式。

### 6. 方案文档必须md+html成对上传R2

每次修改方案文档后，MD和HTML版本同时生成、同时上传。HTML版用自适应前端（fetch.md+marked.js渲染+深色UI）便于手机查看。

### 7. cron做定时分析，前端做交互式查询，不重复

cron bot已经每天08:00/11:35/16:00调用DeepSeek生成晨/午/收盘分析。前端**不重复调用**这些LLM，而是读取cron的分析结果并展示。前端只做**用户主动触发的交互式问AI**（POST /api/ask）。

## 技术选型评估

### 为什么选React而非纯HTML/CSS/JS

| 维度 | 纯JS | React + TS |
|------|------|-----------|
| 组件复用 | 复制粘贴 | import组件 |
| 状态管理 | window.__DATA全局 | useState + Context |
| 类型安全 | 运行时报错 | 编译期捕获 |
| 代码量 | ~1450行(8页+图表) | ~800行(组件化) |
| 热更新 | 手动刷新 | Vite HMR毫秒级 |
| 参考代码 | 框架不同无法参考 | Vibe-Research同框架可直接参考 |

### 为什么选ECharts而非Recharts/Ant Charts

**你的看板需要的图表类型决定了选型：**

| 图表 | 用途 | ECharts | Recharts | Ant Charts |
|------|------|---------|---------|-----------|
| 面积图 | 组合净值曲线 | ✅ | ✅ | ✅ |
| 饼图 | 行业分布 | ✅ | ✅ | ✅ |
| 柱状图 | 板块资金流 | ✅ | ✅ | ✅ |
| **仪表盘Gauge** | **偏离度84%** | ✅**原生** | ❌**没有** | ✅ |
| **热力图Heatmap** | **板块轮动+相关矩阵** | ✅**原生** | ❌**自己拼** | ✅ |
| **K线图Candlestick** | **扩展用** | ✅**原生** | ❌**没有** | ✅ |

**Recharts被否的核心原因**：缺少Gauge（偏离度仪表盘展示"科技84%超配"）和Heatmap（板块轮动热力图+基金相关性矩阵）。你的看板明确需要这两类图。

### 为什么选TypeScript

fund_tools.py返回的数据结构复杂（嵌套dict、可选字段、多种状态码）。TypeScript可以在编译期捕获：字段名拼写错误、类型不匹配、null/undefined访问。

## 项目结构

```
fund-dashboard/
└── dashboard/                     ← React + TypeScript + Vite
    ├── package.json               ← 依赖见下方
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    ├── _redirects                 ← SPA路由 (/* /index.html 200)
    ├── _worker.js                 ← Workers API层 (D1查询+LLM代理)
    ├── tailwind.config.ts
    └── src/
        ├── main.tsx               ← React入口
        ├── App.tsx                ← 路由(react-router-dom, 8个页面)
        ├── components/
        │   ├── GlassCard.tsx       ← 玻璃卡片(参考Vibe-Research)
        │   ├── PageHeader.tsx      ← 页头(参考Vibe-Research)
        │   ├── DateNav.tsx         ← 日期选择器
        │   └── AskAIButton.tsx     ← 问AI对话框(SSE流式)
        ├── pages/
        │   ├── Dashboard.tsx       ← 🏠 总览
        │   ├── Portfolio.tsx       ← 💼 持仓
        │   ├── Sectors.tsx         ← 📈 板块分析
        │   ├── MarketOverview.tsx  ← 🔍 行情总览 🆕
        │   ├── Intel.tsx           ← 📡 资讯雷达(参考VR Intel.tsx) 🆕
        │   ├── History.tsx         ← 📅 历史趋势
        │   ├── Operations.tsx      ← 📜 操作记录
        │   └── Signals.tsx         ← 🤖 信号系统
        ├── hooks/
        │   └── useDashboardData.ts ← 数据fetch hook
        └── types/
            └── index.ts            ← TS类型定义
```

### 依赖清单

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.1.0",
    "echarts": "^6.0.0",
    "lucide-react": "^0.460.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.6.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "vite": "^6.4.2",
    "@vitejs/plugin-react": "^4.3.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.5.14",
    "autoprefixer": "^10.4.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0"
  }
}
```

## 数据流三层架构

**核心原则**：JSONL是唯一真相源，D1是查询缓存，R2是CDN兜底。cron只写，前端只读。

```
第一层: JSONL（本地磁盘，唯一真相源）
  cron写, 前端不写
  12个文件: morning-briefs / closing-reviews /
  daily-snapshots / signals / signals-resolved(953条) / ...
  D1/R2挂了 → 数据安全（真相源在JSONL）

第二层: D1（Cloudflare SQLite，查询加速）
  sync_to_d1.py定期从JSONL同步
  支持SQL查询: SELECT date, value, profit_pct FROM ...
  免费5GB，用户数据~2MB/年

第三层: R2 JSON（CDN缓存，兜底）
  cron每次推送后同步写 dashboard.json
  前端: 优先D1 → 降级R2 → 极端降级空状态
```

### 前端数据获取代码模式

```typescript
// 三层降级获取
async function fetchDashboard() {
  // 第一层: D1 (Worker查询)
  try {
    const resp = await fetch('/api/dashboard');
    if (resp.ok) return await resp.json();
  } catch {}
  // 第二层: R2 JSON直读
  try {
    const resp = await fetch('https://.../dashboard.json');
    return await resp.json();
  } catch {}
  // 第三层: 空状态
  return null;
}
```

### Worker API端点

| 端点 | 功能 | 数据源 | 时效 |
|------|------|--------|------|
| GET /api/dashboard | 今日聚合数据 | D1→R2 dashboard.json | ~分钟 |
| GET /api/history?days=30 | 历史趋势 | D1 SQL查询 | ~日 |
| GET /api/portfolio?date= | 指定日期持仓 | D1或R2 CSV | ~日 |
| GET /api/kol-signals?days= | KOL信号列表 | JSONL/D1 | ~4h |
| GET /api/analysis/latest | 最新cron分析结果 | JSONL(morning/noon/closing) | ~分钟 |
| **POST /api/ask** | **交互式LLM查询** | **Worker→DeepSeek API** | **实时流式** |

### 交互式LLM查询（Worker代理DeepSeek）

**解决了"前端如何具备LLM分析能力"的问题**：Worker环境变量存DEEPSEEK_API_KEY，前端POST问题+上下文，Worker代理调用DeepSeek，SSE流式返回。

```javascript
// _worker.js POST /api/ask
async function handleAsk(request, env) {
  const { question, context } = await request.json();
  const resp = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.DEEPSEEK_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: '你是基金投资助手。基于以下数据回答问题，不构成投资建议。' },
        { role: 'user', content: `当前数据：${context}\n\n问题：${question}` }
      ],
      stream: true
    })
  });
  return new Response(resp.body, {
    headers: { 'Content-Type': 'text/event-stream' }
  });
}
```

前端每个页面右下角💬问AI按钮，自动拼接当前上下文：

```tsx
function AskAIButton({ pageContext }: { pageContext: string }) {
  const [answer, setAnswer] = useState('');
  const ask = async (question: string) => {
    const resp = await fetch('/api/ask', {
      method: 'POST',
      body: JSON.stringify({ question, context: pageContext })
    });
    const reader = resp.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      setAnswer(prev => prev + new TextDecoder().decode(value));
    }
  };
  return <button onClick={() => setOpen(true)}>💬 问AI</button>;
}
```

| 页面 | 自动拼入的上下文 |
|------|----------------|
| 总览 | 大盘指数+组合盈亏+板块TOP5+涨跌家数 |
| 持仓 | 14基金盈亏+偏离度+建仓进度 |
| 板块 | 50行业涨跌+资金流TOP10+你的持仓板块分布 |
| 资讯 | 最近KOL信号+RSS新闻+你的持仓 |

## 8页面体系

```
🏠 总览 — 大盘+组合+资金流+涨跌家数+cron分析摘要+风险
💼 持仓 — 14基金盈亏表+偏离度仪表(Gauge)+饼图+建仓进度
📈 板块 — 涨跌排名+资金流柱状图+轮动热力图+板块-持仓关联
🔍 行情总览 🆕 — 指数卡片+外盘+估值分位+行业研报列表
📡 资讯雷达 🆕 — KOL时间线+画像ECharts+RSS+AI提炼(Tab切换)
📅 历史趋势 — 净值曲线(AreaChart)+单基金走势+相关性矩阵
📜 操作记录 — 时间线+类型统计
🤖 信号系统 — 引擎状态+KOL验证+准确性追踪
```

### 🔍 行情总览页

参考Vibe-Research StockData.tsx的Metric卡片+研报列表设计：
- 6大指数卡片（同Vibe-Research Metric设计，4列网格）
- 外盘行情（Yahoo数据，带_stale标记）
- 板块估值分位（ECharts条形热力图，绿低估/灰合理/红高估）
- 行业研报列表（东财reportapi，日期+机构+标题）
- 成交额+涨跌家数（市场整体热度）

### 📡 资讯雷达页

参考Vibe-Research Intel.tsx的Tab切换设计：

```
[博主信号] [公开新闻] [AI提炼要点]  ← Tab切换

🟢 博主信号（默认）:
  筛选: [全部] [唐主任] [小浣熊] [看多] [看空]
  
  📅 07-17 周五
  🟢 唐主任 看多→科创50  "昨天半导体情绪很好..."
  🔴 小浣熊 看空→科创50  "AI泡沫现在算炸了吗？..."
  
  博主画像 (ECharts) — 从signals-resolved.jsonl(953条)读取:
  唐主任(441条): 看多30% 中性40% 看空30%
  小浣熊(512条): 看多10% 中性30% 看空60%
  准确性: 唐主任23% 小浣熊13%
```

**数据来源**：`signals-resolved.jsonl`（953条已LLM分析信号，方向/板块/准确性齐全）

## ECharts使用模式

所有图表统一模式：`useRef + useEffect + setOption`

```tsx
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

function NavChart({ data }) {
  const ref = useRef(null);
  useEffect(() => {
    const chart = echarts.init(ref.current!);
    chart.setOption({
      xAxis: { type: 'time', data: data.map(d => d.date) },
      yAxis: { type: 'value' },
      series: [{
        type: 'line', areaStyle: {},
        data: data.map(d => d.value),
        lineStyle: { color: '#f59e0b' }
      }],
      tooltip: { trigger: 'axis' },
      dataZoom: [{ type: 'inside' }]
    });
    return () => chart.dispose();
  }, [data]);
  return <div ref={ref} style={{ height: 300 }} />;
}
```

**需要哪类图表就用ECharts对应的type**：
- 净值曲线: `type: 'line'` + `areaStyle`
- 行业分布: `type: 'pie'`
- 板块资金流: `type: 'bar'`
- **偏离度: `type: 'gauge'`**（ECharts独有，Recharts没有）
- **板块轮动: `type: 'heatmap'`**（ECharts独有，Recharts没有）
- **相关性矩阵: `type: 'heatmap'`**

## 从Vibe-Research可参考的组件

| VR文件 | 你的组件 | 参考内容 |
|--------|---------|---------|
| `GlassCard.tsx` | `GlassCard.tsx` | 暗色卡片+毛玻璃效果 |
| `PageHeader.tsx` | `PageHeader.tsx` | 页头+操作按钮布局 |
| `Portfolio.tsx` | `Portfolio.tsx` | 持仓表格+录入表单逻辑 |
| `DailyReview.tsx` | `Dashboard.tsx` | 指数卡片+板块资金流布局 |
| **`StockData.tsx`** | **`MarketOverview.tsx`** | **Metric卡片+估值分位+研报列表** |
| **`Intel.tsx`** | **`Intel.tsx`** | **Tab切换+AI提炼+RSS新闻** |
| `Sectors.tsx` | `Sectors.tsx` | 板块表格排序 |
| **`AskAiButton`** | **`AskAIButton.tsx`** | **问AI对话框+上下文拼接** |
| `api.ts` | `lib/api.ts` | fetch封装+错误处理+竞态防护 |
| `utils.ts` | `lib/utils.ts` | `cn()` class合并工具 |
| `package.json` | `package.json` | 同款ECharts/lucide-react/Tailwind |

## 竞态防护模式

从Vibe-Research抄来的模式，解决快速切换查询时数据错乱：

```tsx
const runIdRef = useRef(0);
const run = async () => {
  const rid = ++runIdRef.current;
  // ... fetch ...
  const ok = (setter) => (val) => {
    if (rid === runIdRef.current) setter(val);
  };
  // 只有最新一次查询的结果会回填
  api.data().then(ok(setData)).catch(() => {});
};
```

## 部署流程

```
本地开发: npm run dev → localhost:5173
构建:     npm run build → dist/ (纯静态文件)
部署:     git push → Cloudflare Pages自动检测

Pages配置:
  构建命令: npm run build
  输出目录: dist/
  SPA路由: _redirects (/* /index.html 200)
  D1绑定: wrangler.toml配置
```

**服务器不需要Node.js** — 构建在Pages CI环境完成，或本地开发机完成。

## 已知陷阱

1. ❌ 手写SVG图表 → 已被用户纠正。用ECharts。
2. ❌ 纯HTML/CSS/JS → 已被用户纠正。用React+TypeScript+Vite。
3. ❌ 纯R2存数据 → 已被用户纠正。用D1+Workers做可查询API层。
4. ❌ 不建Git仓库 → 已被用户纠正。必须版本控制。
5. ❌ 推荐数据源不实测 → 已被用户严厉纠正。必须先写脚本从服务器跑通。
6. ❌ 先做方案再推荐 → 已被用户纠正。先实测验证，再写入方案。
7. ❌ 认为基金不需要行情数据 → 已被用户纠正。基金看板需要行情/板块/资金流/研报。
8. ⚠️ push2.eastmoney.com clist → Oracle ARM 502。用push2delay替代。
9. ⚠️ push2.eastmoney.com kamt.kline → 通的！（与clist不同CDN路由）
10. ✅ 方案文档必须md+html成对上传R2。

## 参考文件

- `fund-data-sources` skill — 数据源验证细节（含Eastmoney实测报告）
- DASHBOARD_DESIGN_PLAN_v3.md / .html — 完整设计方案文档（R2）

## 实施工作量

4阶段，10-13天：
- 阶段一（2-3天）：Git仓库 + D1 + schema + sync_to_d1.py + Worker API
- 阶段二（4-5天）：SPA骨架 + 7个前端页面（含行情总览+资讯雷达）
- 阶段三（2天）：交互式LLM查询（Worker代理DeepSeek + AskAIButton）
- 阶段四（2-3天）：剩余页面 + cron同步 + 手机优化
