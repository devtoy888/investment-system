# 基金系统架构模式（Session 2026-07-15 新增）

## Signal Engine 化

加仓信号从硬编码 if-else 改为 YAML 配置 + 通用评估器。

核心文件：
- `/opt/data/fund_system_data/evolution/signal_rules.yaml` — 规则配置
- `/opt/data/scripts/signal_engine.py` — 通用评估器

每条规则：fund_code + conditions（type/operator/value）+ message 模板。
规则之间 OR，conditions 之间 AND。

支持 conditions type：
- estimated_change, benchmark_price, benchmark_change, benchmark_amplitude

## 数据源降级架构

基金净值：天天基金 → 重试 → AKShare(实时估值) → AKShare(历史净值) → None
涨跌家数：东财push2(502) → 新浪tags文本 → None
北向资金：hexin → 新浪tags → 东财备用 → 快照文件 → None

备援源格式不同时适配层统一输出。备援失败静默返回 None。

## AKShare Docker 集成

安装：pip install --target /opt/data/akshare-deps akshare
发现：fund_source_akshare.py 自动 sys.path.insert
隔离：版本冲突警告可忽略（装在隔离目录，只影响 akshare）

## 外部项目评估（Vibe-Trading）

10 维度全量分析：
1. 整体定位 2. 数据源(loaders/) 3. 交易模型 4. 因子系统(factors/base.py)
5. 回测引擎(backtest/runner.py) 6. 安全模型(security.py) 7. 测试体系(.github/workflows/)
8. 工具系统(tools/) 9. 复盘闭环(shadow_account/) 10. 前端架构(frontend/src/)

## 定时推送审计

检查所有推送脚本是否包含硬编码日期或数值。
审计命令：grep -n "2026-" *.py | grep -v date.today
动态脚本应从 collect_ 输出文件或 JSONL 读取数据。
