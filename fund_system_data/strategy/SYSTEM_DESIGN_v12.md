# 系统设计 v12
> 生成日期: 2026-07-15
> 进化: VT-1 Signal Engine化完成
---

## 本次变更
- 新增 signal_engine.py: 通用信号引擎，读取 YAML 规则配置批量评估
- 新增 signal_rules.yaml: 规则配置化(原monitor_buy_signals.py的4基金×10条件)
- run_buy_signal.py 改用 signal_engine.py (yaml驱动, 不改代码加信号)
- 旧 monitor_buy_signals.py 保留不动(回退用)

## 自检问题
- 无严重问题

## 待办
- [ ] VT-2: AKShare数据源接入
- [ ] VT-3: 基准对比推送

---
*参考：R2 fund-system/strategy/SYSTEM_DESIGN_v*