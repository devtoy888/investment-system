# KOL 画像分析与验证报告

> 基于227+80+80条博文的数据驱动分析
> 更新时间：2026-06-26

## 一、核心结论

| 博主 | 条数 | 跨度 | 信号密度 | 已验证准确率 | 推送角色 |
|------|:----:|:----:|:--------:|:----------:|---------|
| 唐史主任司马迁 | 227 | 765天 | 26.7% | 6/6 (100%) | 主力信号源 |
| 小浣熊1230 | 80 | 137天 | 26.3% | 逻辑合理 | 风险警示补充 |
| IT精英带你养基 | 80 | 137天 | 7.5% | N/A（非预言型） | 仓位配比参考 |

## 二、唐史主任准确性验证

| 日期 | 他的说法 | 实际验证 | 来源 | 结果 |
|------|---------|---------|:----:|:----:|
| 2026-06-25 | 美光业绩全超 | Q3营收+346%,毛利率75% | 网易财经 | ✅ |
| 2026-06-23 | 昨天成交3.76万亿 | 6/22 A股历史次高 | 同花顺/Choice | ✅ 精确到数字 |
| 2026-06-23 | 科创综指等都新高 | 6/24科创50涨3.82%再创历史 | 中国新闻网 | ✅ |
| 2026-06-23 | 韩国熔断+国内存储涨 | KOSPI跌8.11%熔断,存储逆势涨 | 财新网/新华网 | ✅ |
| 2026-06-16 | 指数完成回踩 | MACD金叉站上四线 | Black Viper复盘 | ✅ |
| 2026-04-09 | 科技反弹中占优 | Q2科技持续领涨 | 新浪财经 | ✅ |

Verification source URLs (verified 2026-06-26):
- 美光+346%: https://www.163.com/dy/article/L08V5PLD0519D4UH.html
- 韩国熔断8.11%: https://international.caixin.com/2026-06-23/102456625.html
- 成交量3.76万亿: https://m.10jqka.com.cn/20260622/c677622799.shtml
- 科创50再创新高: https://www.chinanews.com.cn/cj/2026/06-24/10646460.shtml
- 指数回踩MACD金叉: https://www.xu81.com/posts/2026/06/a...6%E6%97%A5/

## 三、数据分析方法

工具脚本位于 `/opt/data/scripts/`:
- `kol_analyze_phase0.py` — Phase 0 初始分析
- `kol_expand_phase1.py` — Phase 1 扩展采集
- `kol_expand_phase2.py` — Phase 2 再次扩展
- `kol_analyze_final.py` — 最终画像分析
- `kol_blacktalk_analysis.py` — 黑话统计分析
- `kol_pull_older_tang.py` — 拉取唐史主任历史数据

Web verification performed via web_search for cross-referencing specific claims against market data.
