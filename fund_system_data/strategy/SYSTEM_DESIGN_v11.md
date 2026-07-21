# 系统设计 v11
> 生成日期: 2026-07-15
> 进化: Vibe-Trading评估+数据源修复
---

## 本次变更
- 完成Vibe-Trading完整评估: 数据降级/Signal Engine/MCP/Shadow Account四方面借鉴
- 评估报告+HTML已上传R2: fund-system/evolution/VIBE_TRADING_EVAL
- 涨跌家数: 东财502已通过新浪tags备援修复(4200涨/4600跌)
- 北向资金: hexin超时已通过新浪tags备援修复(26.45亿)
- 决策日志增强: 每日自动计算持仓市值+分组盈亏

## 自检问题
- 无严重问题

## 待办
- [ ] Signal Engine化: 信号规则可配置(monitor_buy_signals.py改造)
- [ ] MCP工具注册: 暴露分析能力

---
*参考：R2 fund-system/strategy/SYSTEM_DESIGN_v*