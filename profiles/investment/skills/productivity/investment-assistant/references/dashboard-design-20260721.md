# Dashboard 可视化看板设计

> 生成日期：2026-07-21 | 参考：Vibe-Research(UI) + Vibe-Trading(strategy)

## 核心架构

```
generate_dashboard_data.py  ← 交易日16:15 cron运行
     │  聚合8个数据源：fund_tools实时行情 + portfolio快照
     │  + operations/操作记录 + signals + accuracy + risk等
     ▼
dashboard.json → R2 fund-system/data/
     │
     ▼
dashboard/index.html (纯HTML/CSS/JS SPA, 零依赖)
     │
     ▼
fetch(URL) → 渲染6个手机优先页面
```

## 6页面规格

| 页面 | 路由 | P0数据 | 可视化方式 |
|:----|:----|:-------|:----------|
| 🏠 总览 | `#dashboard` | 6指数 + 组合盈亏 + 板块热度 + 5操作 + 风险 | 卡片网格 + 进度条 + 涨跌色块 |
| 💼 持仓 | `#portfolio` | 14基金盈亏表 + 偏离度 + 建仓进度 | 表格(SVG饼图) + 环形仪表 |
| 📈 板块 | `#sectors` | 10行业 + 5日趋势 | 迷你线图 + 可排序表格 |
| 📜 操作 | `#operations` | 完整时间线 + 分类统计 | 时间线 + 柱状图 |
| 🤖 信号 | `#signals` | 引擎状态 + KOL时间线 | 卡片 + 时间轴 |
| 📊 验证 | `#verify` | 准确率 + 数据源可用率 | 折线图 + 状态表 |

## 主题变量

```css
:root {
  --bg-body: #0a0e1a;  --bg-card: rgba(17,24,39,0.8);
  --accent: #f59e0b;   --up: #22c55e;  --down: #ef4444;
  --text-primary: #f3f4f6;  --text-secondary: #9ca3af;
  --radius: 12px;
}
```

## 数据契约

`dashboard.json` 结构（JavaScript消费方视角）：
- `market.indexes[]` → `{code, name, price, change_pct}` 
- `portfolio.funds[]` → `{code, name, cost, nav, shares, value, profit_pct, ratio, status}`
- `sectors[]` → `{name, change_pct, trend_5d: [n1,n2,n3,n4,n5]}`
- `operations[]` → `{date, code, name, action, amount, reason, result}`
- `signals.engine` + `signals.kol[]` 
- `risks[]` → `{level:"warning"|"danger", message}`
- `accuracy` → `{recent_pct, trend:"up"|"down"|"flat", daily: [{date, pct}]}`

## 参考仓库

- Vibe-Research: github.com/simonlin1212/Vibe-Research — UI模式（侧栏导航/玻璃暖橙/卡片布局/响应式网格）
- Vibe-Trading: github.com/HKUDS/Vibe-Trading — 策略框架（信号引擎/因子库/基准对比/组合优化）
