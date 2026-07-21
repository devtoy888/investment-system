# 系统设计 v13
> 生成日期: 2026-07-15
> 进化: VT-2 AKShare数据源接入完成
---

## 本次变更
- 新增 fund_source_akshare.py: AKShare适配器(基金估值/北向/板块/历史净值)
- get_fund_value() 加入AKShare备援: 天天基金→重试→AKShare→None
- AKShare未安装时不报错, 优雅降级(需pip install akshare后自动生效)

## 自检问题
- 无严重问题

## 待办
- [ ] VT-3: 基准对比推送(组合vs沪深300)

---
*参考：R2 fund-system/strategy/SYSTEM_DESIGN_v*