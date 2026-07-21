# 📊 投资实用看板 · 完整设计方案

**评估日期**：2026-07-21  
**参考项目**：[Vibe-Research](https://github.com/simonlin1212/Vibe-Research)（UI/UX）+ [Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)（策略框架）  
**查看链接**：[MD版](https://hermes-main-media.devtoy.xyz/fund-system/strategy/DASHBOARD_DESIGN_PLAN.md) · [HTML版](https://hermes-main-media.devtoy.xyz/fund-system/strategy/DASHBOARD_DESIGN_PLAN.html)

---

## 一句话方案

保持cron数据管道不变，新增 `generate_dashboard_data.py` 聚合所有现有数据为 `dashboard.json`，上传R2；同时开发一个**纯HTML/CSS/JS的SPA**（零依赖），通过fetch该JSON渲染6个手机优先的页面。

## 页面体系

```
🏠 总览（默认）→ 💼 持仓 → 📈 板块 → 📜 操作 → 🤖 信号 → 📊 验证
```

## 核心变更

| 类别 | 变更 | 工作量 |
|------|------|--------|
| 🆕 新增脚本 | `scripts/generate_dashboard_data.py`（数据聚合） | 1天 |
| 🆕 新增前端 | `dashboard/` 目录（index.html + css/js/） | 3-5天 |
| 🔧 修改现有 | `run_closing.py` 末尾增加调用 | 0.5天 |
| 🔧 修改现有 | `portfolio_snapshot.py` 增加JSON输出 | 0.5天 |
| 🔧 修改现有 | `r2_upload_and_verify.py` 增加dashboard同步 | 0.5天 |

## 数据依赖

聚合脚本 `generate_dashboard_data.py` 读取8个现有数据源 → 输出 `dashboard.json` → 前端SPA消费。

## 实施阶段

1. **阶段一**（1-2天）：数据管道 → `dashboard.json`
2. **阶段二**（2-3天）：核心页面 → 总览+持仓
3. **阶段三**（1-2天）：扩展页面 → 板块+操作+信号+验证
4. **阶段四**（1天）：打磨提升 → 动画+缓存+自动化

**总计：5-8天**
