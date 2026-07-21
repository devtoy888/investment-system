# Investment Dashboard

个人基金投资辅助系统 · A股基金看板

**架构：** React 19 + TypeScript + Vite + ECharts + Tailwind CSS  
**部署：** Cloudflare Pages + D1 + Workers + R2  
**数据层：** Python采集 (fund_tools.py) → JSONL → D1同步 → 前端展示  

## 目录结构

```
investment-system/
├── scripts/           ← 数据采集脚本
├── dashboard/         ← 前端SPA (v0.1.0+)
├── schema.sql         ← D1数据库表结构
└── README.md
```

## 版本

| 版本 | 说明 | 状态 |
|------|------|------|
| v0.1.0 | 管线就绪 (GitHub+Pages+D1+SPA骨架) | ✅ 2026-07-21 |
| v0.2.0 | SPA骨架+总览页 (MVP) | 🔴 |
| v0.3.0 | 持仓+板块页面 | 🔴 |
| v1.0.0 | 正式上线 | 🔴 |

## 快速开始

```bash
# 服务器端：数据采集
cd /opt/data/scripts
python3 fund_tools.py

# 前端开发
cd dashboard
npm install
npm run dev
```
