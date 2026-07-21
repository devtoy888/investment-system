# KOL 分析框架 v2 — 事实核查 + 操作建议 + 基金映射

> 2026-07-19 重写，替换旧版静态关键词匹配。

## 架构总览

```
Extractor (提取) → Verifier (核查) → Mapper (操作映射) → format_push (推送)
```

## 4层设计

### ① Extractor — 信号提取

```python
from kol_analysis import Extractor
signals = Extractor.extract(text, kol_name="唐史主任")
# 返回: [{sector, direction, timeframe, claim, confidence, matched, kol}]
```

- **赛道检测**: 用 `SECTOR_TO_QUOTES` 映射 + 扩展关键词
- **方向检测**: `DIRECTION_KEYWORDS` (bullish 18词 / bearish 22词)
- **时效窗口**: `today`(今天/日内/马上) / `soon`(本周/明天/短期) / `medium` / `long`
- **断言提取**: `_claim_sentence()` 找同时含赛道+方向词的句子

### ② Verifier — 事实核查

```python
verified = Verifier.fact_check_all(signals, quotes)
# 每条 signal 增加 verification: {verified, correct, predicted, actual, actual_change, matched_quote}
```

- **赛道→行情key映射**: 通过 `SECTOR_DATA_MAP` 字典（科技/AI→科创50/半导体）
- **核查逻辑**: compare `signal.direction` vs 实际 `change_pct` 方向
- **正确标记**: `correct=True/False/None`（None=中性预测）

### ③ Mapper — 操作映射

```python
actions = Mapper.to_actions(signals)
# 返回: [{sector, action, direction, funds: [{code, name, tag, suggested_action, suggested_pct}], source_kols}]
```

- **时效过滤**: 只处理 `today` 和 `soon` 窗口的信号
- **基金映射**: `SECTOR_TO_FUNDS` 字典（7个赛道→6支基金代码）
- **力度判断**: net≥2→加仓/减仓, net≥1→增持/减持
- **仓位建议**: 强烈信号5%, 普通3%

### ④ format_push — 推送格式化

```python
push_text = format_push(analysis)
# 输出: 操作建议表格(带基金代码) + 信号摘要(含✅/❌) + KOL统计
```

## QQ Bot 格式规则

- ❌ 不要用 `##` 标题格式（QQ渲染为超大字体）
- ❌ 不要用 `**KOL名**` 加粗格式（QQ渲染为标题）
- ❌ 不要用 `#话题#` 原样输出（清理 markdown 符号）
- ✅ 用 `▸ KOL名` 列表格式
- ✅ 表格用标准 Markdown `|` 分隔
- ✅ 操作建议放最前面（用户最关心的）

## 关键文件

| 文件 | 路径 | 说明 |
|:-----|:-----|:------|
| kol_analysis.py | `/opt/data/scripts/` | 核心框架(350行) |
| fund_tools.py | `/opt/data/scripts/` | get_user_weibos长文本API |
| collect_morning_data.py | `/opt/data/scripts/` | 集成点(#5.5节) |

## Pitfalls

1. **时序窗口** — 只有 `today`/`soon` 信号出操作建议。长期趋势只记录不操作。
2. **ClaimVerifier v1 已废弃** — 旧版用 `market_data.get("科技/AI")` 永远为None（key不匹配）。v2改用 `SECTOR_DATA_MAP` 映射表。
3. **微博长文本** — `text[:500]` 已改为 `text[:2000]`，但长文本API可能失败（超时/限流），此时用短文本回退。
4. **置信度≠准确率** — confidence基于关键词数量+方向明确性，不是基于历史准确率。历史准确率需积累30天以上才有意义。
5. **验证信号前** — `Verifier.fact_check_all()` 依赖行情数据。非交易日/上午9:30前调用时，市场数据可能是昨天的。
