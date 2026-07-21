# Cron 任务配置 — 2026-06-30

当前活跃任务：

| 任务 | Job ID | 调度(UTC) | CST | 脚本 | 类型 |
|------|--------|-----------|-----|------|------|
| 今日参考 | d7b0ad464c01 | 0 0 * * 1-5 | 08:00 交易日 | collect_morning_data.py | AI agent |
| 盘中速递 | d29e6063c469 | 35 3 * * 1-5 | 11:35 交易日 | collect_noon_data.py | AI agent |
| 收盘复盘 | 7a165a5748ce | 0 8 * * 1-5 | 16:00 交易日 | closing_review.py | AI agent |
| 周末外盘速报 | 68ca7f4fcf2a | 0 1 * * 6 | 09:00 周六 | collect_weekend_data.py | no_agent |
| 数据源可用性验证 | a1193d2964a1 | 0 2 * * 6 | 10:00 周六 | auto_validate_sources.py | no_agent（报告到QQ）|

### Prompt 说明

三个 AI agent 任务的 prompt 都在 Hermes cron 中配置，包含：
1. 检查交易日（跳过文件协议）
2. 读取预采集数据文件
3. 格式化成 markdown 表格推送

每个 prompt 有独立的模板（板块排行/成交额/北向资金段落）。修改 prompt 需通过 `cronjob action=update` 进行。
