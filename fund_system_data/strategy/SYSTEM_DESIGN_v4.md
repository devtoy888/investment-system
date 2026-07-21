# 系统设计 v4
> 生成日期: 2026-07-15
> 进化: 新增自进化系统: 自检+去重+进化存档
---

## 本次变更
- 新增 system_health_audit.py 每周自检脚本(Layer1)
- 新增 deduplicate_archives.py 自动去重脚本(Layer2自修复)
- 新增 log_evolution.py 进化记录+R2存档(Layer3架构进化)
- 注册 cron: 周末外盘速报(周六09:00)
- 注册 cron: 数据源验证(周六10:00)
- 注册 cron: 加仓信号监控(交易日16:10)
- 注册 cron: JSONL去重(交易日16:20)
- 注册 cron: 系统自检(周六10:30)
- 修复 r2_uploader.py 缺失__main__入口的bug

## 自检问题
- KOL信号归因: signals-resolved.jsonl全部5条correct=null
- morning-briefs重复率高达453%(已去重修复)
- r2_uploader.py无CLI入口导致上传返回None(已修复)

## 待办
- [ ] 修复 resolve_past_signals() 涨跌判断正确/错误逻辑
- [ ] 创建 log_daily_decisions.py 每日决策日志(correct字段)
- [ ] 创建 collect_daily_snapshot.py 每日价格快照

---
*参考：R2 fund-system/strategy/SYSTEM_DESIGN_v*