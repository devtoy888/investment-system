# 系统设计 v6
> 生成日期: 2026-07-15
> 进化: 新增周度复盘功能
---

## 本次变更
- 新增 weekly_review.py 周度复盘脚本(周日20:00推送)
- 新增 cron: 周度复盘(周日20:00)
- 周报自动存档至 R2 fund-system/evolution/weekly-{周数}.md
- 修复 resolve_past_signals() 增加magnitude/signal_strength字段

## 自检问题
- KOL信号correct=null问题: neutral方向信号无法自动判断，已增加信号强度评估

## 待办
- [ ] 改进extract_signals_from_kols方向检测，减少neutral误判
- [ ] 建立3天决策验证机制(手工触发或周日自动运行)

---
*参考：R2 fund-system/strategy/SYSTEM_DESIGN_v*