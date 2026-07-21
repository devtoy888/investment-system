# KOL分析框架 v2 — 提取→验证→映射→推送

> 2026-07-19 全量重写 | 4层架构+事实核查+赛道→基金映射 | 验证35/35 ✅

## 架构图

```
KOL博文 ──→ Extractor ──→ Verifier ──→ Mapper ──→ format_push ──→ QQ Bot
              │              │            │
              ↓              ↓            ↓
        {赛道,方向,     对比行情数据,   赛道→基金映射,
         时效,置信度}    标定✅/❌      具体仓位建议%
```

## 文件位置

- 主模块: `/opt/data/scripts/kol_analysis.py` (~350行)
- 集成位置: `collect_morning_data.py` 的 `# ── 5.5` 段
- 交易日自动验证: `trading_day_validate.py`

## 核心API

```python
from kol_analysis import analyze_from_kol_data, format_push

# 完整分析
analysis = analyze_from_kol_data(kol_data, quotes)
# analysis = {
#   'signals': [...],   # 所有提取的信号(含verification)
#   'actions': [...],   # 操作建议(含funds映射)
#   'signal_count': N,
#   'action_count': N,
# }

# 格式化推送文本
push_text = format_push(analysis)
# 输出: 操作建议表格 + 信号摘要 + KOL统计
```

## 赛道→行情key映射（Verifier使用）

| 赛道 | 匹配行情key |
|:-----|:-------------|
| 科技/AI | 科创50, 半导体, 通信, 创业板指 |
| 黄金 | 黄金ETF市场价 |
| 资源/周期 | 有色金属 |
| 新能源 | 新能源, 光伏 |
| 医药 | 医药 |
| 消费 | 消费 |
| 市场整体 | 上证指数, 沪深300 |

## 赛道→基金映射（Mapper使用）

| 赛道 | 基金代码 | 仓位建议 |
|:-----|:--------:|:--------:|
| 科技/AI | 011613(科创50ETF联接C) | +5% / -5% |
| 科技/AI | 017103(大摩数字经济混合C) | +5% / -5% |
| 黄金 | 009477(中银上海金ETF联接C) | +3% / -3% |
| 资源/周期 | 163302(大摩资源优选混合) | +3% / -3% |
| 资源/周期 | 021448(华夏中证电网设备ETF联接C) | +3% / -3% |
| 新能源 | 012895(天弘中证新能源指数增强C) | +3% / -3% |
| 新能源 | 013589(天弘中证光伏产业指数C) | +3% / -3% |

## v1→v2 迁移指南

| 旧(v1, 已移除) | 新(v2) |
|:---------------|:--------|
| `SignalExtractor.extract()` | `Extractor.extract()` |
| `ClaimVerifier.verify()` | `Verifier.verify_signal()` |
| `KOLScorer.score()` | 已移除(整合到Mapper) |
| `ActionMapper.map()` | `Mapper.to_actions()` |
| `analyze_kol_posts()` | `analyze_from_kol_data()` |
| `format_analysis_for_push()` | `format_push()` |
| `save_kol_prediction()` | 已移除(由Verifier.fact_check_all替代) |

## 理论框架

- **行为金融学**: 锚定效应(识别KOL的参考锚点)、确认偏误(对比多源观点)
- **信号处理**: 信噪比(区分信息与噪音)、趋势确认(多时间维度)
- **博弈论**: 逆向思维(识别利益立场)、共识强度(群体智慧加权)
- **时间窗口**: today(48h内)/soon(本周)/long(长期), 仅today+soon出操作建议

## 验证历史

| 日期 | 版本 | 通过率 | 关键修复 |
|:----:|:----:|:------:|:---------|
| 07-18 | v1 | 25/25 | 创建框架(提取+评分+操作) |
| 07-19 | v2 | 35/35 | 事实核查修复+赛道→行情key映射+基金映射+时序分筛 |
