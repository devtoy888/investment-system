# 系统设计 v5
> 生成日期: 2026-07-15
> 进化: 新增决策日志+修复KOL归因
---

## 本次变更
- 新增 log_daily_decisions.py 每日决策日志+价格快照
- 新增 cron: 决策日志(交易日16:25)
- 修复 resolve_past_signals() 增加magnitude/signal_strength字段

## 自检问题
- decisions.jsonl和daily-snapshots.jsonl均已首次数写入R2
- signals-resolved.jsonl的correct=null问题：neutral方向信号无法自动判断正确/错误，已增加信号强度评估

## 待办
- [ ] 周日20:00周度复盘cron(含KOL准确率排行榜)
- [ ] 改进extract_signals_from_kols的方向检测逻辑，减少neutral误判

---
*参考：R2 fund-system/strategy/SYSTEM_DESIGN_v*