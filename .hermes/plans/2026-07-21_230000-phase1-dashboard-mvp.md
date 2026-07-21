# Phase 1: Dashboard MVP (v0.2.0)

> 总览页：大盘指数 + 组合速览 + 板块资金流 + 涨跌家数 + cron摘要

**架构：** 服务器cron生成数据 → R2 JSON → Worker API → React渲染

---

## 子任务

### Task 1: generate_dashboard_json.py
聚合基金数据/大盘/板块/涨跌家数 → dashboard.json → 上传R2

**输入:** fund_tools.py函数 + local JSONL文件
**输出:** R2 `fund-system/dashboard.json`
**cron:** 交易日每4h运行一次

### Task 2: _worker.js (Pages API层)
4个端点:
- GET /api/dashboard → 今日数据
- GET /api/history?days=N → 历史趋势
- GET /api/analysis/latest → 最新cron分析
- GET /api/sync → 触发数据同步

### Task 3: Dashboard.tsx 重构
原本占位页面→真实数据渲染:
- 指数卡片网格 (6大指数)
- 组合速览卡片
- 板块资金流TOP5 (柱状图)
- 涨跌家数统计
- cron分析摘要
- 三层降级加载 (Worker → R2 → 空状态)

### Task 4: 部署验证
git push → Pages自动部署 → curl验证 → ROADMAP更新
