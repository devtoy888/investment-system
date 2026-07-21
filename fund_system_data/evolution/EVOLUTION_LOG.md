# 系统进化日志

> 首次创建: 2026-07-15
> 每次系统变更自动追加记录
---

## v4 → 下一版 (2026-07-15)
### 变更：新增自进化系统: 自检+去重+进化存档

- 注册 cron: 系统自检(周六10:30)

### 自检发现
- decisions.jsonl 决策日志不存在

### 待办
- [ ] 注册 deduplicate_archives.py 每日去重cron

## v4 → 下一版 (2026-07-15)
### 变更：新增自进化系统: 自检+去重+进化存档

- 新增 system_health_audit.py 每周自检脚本(Layer1)
- 新增 deduplicate_archives.py 自动去重脚本(Layer2自修复)
- 新增 log_evolution.py 进化记录+R2存档(Layer3架构进化)
- 注册 cron: 周末外盘速报(周六09:00)
- 注册 cron: 数据源验证(周六10:00)
- 注册 cron: 加仓信号监控(交易日16:10)
- 注册 cron: JSONL去重(交易日16:20)
- 注册 cron: 系统自检(周六10:30)
- 修复 r2_uploader.py 缺失__main__入口的bug

### 自检发现
- KOL信号归因: signals-resolved.jsonl全部5条correct=null
- morning-briefs重复率高达453%(已去重修复)
- r2_uploader.py无CLI入口导致上传返回None(已修复)

### 待办
- [ ] 修复 resolve_past_signals() 涨跌判断正确/错误逻辑
- [ ] 创建 log_daily_decisions.py 每日决策日志(correct字段)
- [ ] 创建 collect_daily_snapshot.py 每日价格快照

## v5 → 下一版 (2026-07-15)
### 变更：新增决策日志+修复KOL归因

- 新增 log_daily_decisions.py 每日决策日志+价格快照
- 新增 cron: 决策日志(交易日16:25)
- 修复 resolve_past_signals() 增加magnitude/signal_strength字段

### 自检发现
- decisions.jsonl和daily-snapshots.jsonl均已首次数写入R2
- signals-resolved.jsonl的correct=null问题：neutral方向信号无法自动判断正确/错误，已增加信号强度评估

### 待办
- [ ] 周日20:00周度复盘cron(含KOL准确率排行榜)
- [ ] 改进extract_signals_from_kols的方向检测逻辑，减少neutral误判

## v6 → 下一版 (2026-07-15)
### 变更：新增周度复盘功能

- 新增 weekly_review.py 周度复盘脚本(周日20:00推送)
- 新增 cron: 周度复盘(周日20:00)
- 周报自动存档至 R2 fund-system/evolution/weekly-{周数}.md
- 修复 resolve_past_signals() 增加magnitude/signal_strength字段

### 自检发现
- KOL信号correct=null问题: neutral方向信号无法自动判断，已增加信号强度评估

### 待办
- [ ] 改进extract_signals_from_kols方向检测，减少neutral误判
- [ ] 建立3天决策验证机制(手工触发或周日自动运行)

## v7 → 下一版 (2026-07-15)
### 变更：3天验证+方向检测改进+时间修正

- 新增 verify_decisions.py 3天决策验证(交易日16:30)
- 改进 KOL方向检测: 扩充_DIRECTION_BULLISH_FULL/_DIRECTION_BEARISH_FULL词典, 增加全文本扫描
- 周五收盘增加'今晚美股关注'段
- 早报时间 08:30→08:00

### 自检发现
- 经测试: 方向检测neutral率从56%降至约30%, '趋势向下注意风险'从neutral正确识别为bearish

### 待办
- [ ] 3天验证需等待数据积累(首条决策2026-07-15, 3天后即07-18方可验证)
- [ ] 周日周度复盘会自动验证本周决策, 下次周日20:00见

## v8 → 下一版 (2026-07-15)
### 变更：持仓入库+偏离度检测

- 持仓数据入库: 12支基金含成本/份额/盈亏, 三件套(csv/md/html)存R2
- 新增 check_allocation.py 组合偏离度检测, 整合到16:10推送
- 当前科技/AI占比86%触发🔴紧急线, 每日收盘自动提醒

### 自检发现
- 基金参考文档已同步更新, 清仓6支已标注

### 待办
- [ ] 风险预警系统(单日>5%/连跌3日自动推QQ)
- [ ] 持仓市值每日自动更新(整合到log_daily_decisions)

## v9 → 下一版 (2026-07-15)
### 变更：风险预警系统上线

- 新增 risk_warning.py: 单日>5%暴跌检测+连跌3日检测
- 16:10推送三段合一: 加仓信号+偏离度检测+风险预警
- 新增 fund-daily-trend.jsonl 日趋势追踪R2同步

### 待办
- [ ] SPA移动端(实时仪表盘)
- [ ] 3天决策验证(07-18起有数据)
- [ ] 周日20:00第一份周度复盘

## v9 → 下一版 (2026-07-15)
### 变更：风险预警系统上线

- 新增 risk_warning.py: 单日>5%暴跌检测+连跌3日检测
- 16:10推送三段合一: 加仓信号+偏离度检测+风险预警
- 新增 fund-daily-trend.jsonl 日趋势追踪R2同步

### 待办
- [ ] SPA移动端(实时仪表盘)
- [ ] 3天决策验证(07-18起有数据)
- [ ] 周日20:00第一份周度复盘

## v9 → 下一版 (2026-07-15)
### 变更：风险预警系统上线

- 新增 risk_warning.py: 单日>5%暴跌检测+连跌3日检测
- 16:10推送三段合一: 加仓信号+偏离度检测+风险预警
- 新增 fund-daily-trend.jsonl 日趋势追踪R2同步

### 待办
- [ ] SPA移动端(实时仪表盘)
- [ ] 3天决策验证(07-18起有数据)
- [ ] 周日20:00第一份周度复盘

## v10 → 下一版 (2026-07-15)
### 变更：数据源修复+决策日志增强

- 涨跌家数: 东财API 502, 新增新浪tags备援(正则提取涨跌家数)
- 北向资金: 修复hexin超时, 新增新浪tags每日净流入提取(26.45亿)
- 决策日志增强: 新增持仓市值每日追踪, 含分组汇总/日盈亏
- 每日自动生成 portfolio-{日期}.md 并上传R2

### 自检发现
- 东财push2全线502(已2小时+)需持续观察

### 待办
- [ ] 研究Vibe Trading出评估报告

## v11 → 下一版 (2026-07-15)
### 变更：Vibe-Trading评估+数据源修复

- 完成Vibe-Trading完整评估: 数据降级/Signal Engine/MCP/Shadow Account四方面借鉴
- 评估报告+HTML已上传R2: fund-system/evolution/VIBE_TRADING_EVAL
- 涨跌家数: 东财502已通过新浪tags备援修复(4200涨/4600跌)
- 北向资金: hexin超时已通过新浪tags备援修复(26.45亿)
- 决策日志增强: 每日自动计算持仓市值+分组盈亏

### 待办
- [ ] Signal Engine化: 信号规则可配置(monitor_buy_signals.py改造)
- [ ] MCP工具注册: 暴露分析能力

## v12 → 下一版 (2026-07-15)
### 变更：VT-1 Signal Engine化完成

- 新增 signal_engine.py: 通用信号引擎，读取 YAML 规则配置批量评估
- 新增 signal_rules.yaml: 规则配置化(原monitor_buy_signals.py的4基金×10条件)
- run_buy_signal.py 改用 signal_engine.py (yaml驱动, 不改代码加信号)
- 旧 monitor_buy_signals.py 保留不动(回退用)

### 待办
- [ ] VT-2: AKShare数据源接入
- [ ] VT-3: 基准对比推送

## v13 → 下一版 (2026-07-15)
### 变更：VT-2 AKShare数据源接入完成

- 新增 fund_source_akshare.py: AKShare适配器(基金估值/北向/板块/历史净值)
- get_fund_value() 加入AKShare备援: 天天基金→重试→AKShare→None
- AKShare未安装时不报错, 优雅降级(需pip install akshare后自动生效)

### 待办
- [ ] VT-3: 基准对比推送(组合vs沪深300)

## v14 → 下一版 (2026-07-15)
### 变更：VT-3 基准对比推送完成

- 新增 check_benchmark.py: 沪深300 vs 组合盈亏对比
- 16:10推送增加第4段: 基准对比(跑赢/跑输大盘X%)
- VT借鉴P0全部完成(1.SignalEngine 2.AKShare 3.基准对比)

### 待办
- [ ] VT-6: MCP Tool注册
- [ ] VT-7: KOL因子验证

## v16 → 下一版 (2026-07-15)
### 变更：VT-7/8 KOL验证+诊断闭环完成

- kol_verify.py: 394条信号×2KOL, 准确率/IC/IR/板块命中率/案例, 自动上传R2
- 小浣熊1230: 看空100%准确率, IC 0.3565有效正相关
- portfolio_diagnosis.py: 胜率/止损/集中度/偏差/综合评分(0/8)
- VT借鉴P0-P1全部完成(8项)

### 待办
- [ ] DS-1: Tushare基金持仓
- [ ] DS-2: Baostock行情备援
