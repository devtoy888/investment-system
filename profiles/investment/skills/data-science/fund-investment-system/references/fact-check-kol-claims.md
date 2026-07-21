# KOL 事实核查：fact_check_kol_claims()

> 2026-07-15 新增 — 用户要求"不要完全采信博主，要有事实依据佐证"

## 函数签名

```python
def fact_check_kol_claims(
    text: str,                  # KOL微博原文
    quotes: dict = None,        # {指数名: {change_pct, price, ...}}
    sectors: dict = None,       # {板块名: {change_pct, open, price, ...}}
    market_overview: dict = None, # {total_turnover, sh_turnover, ...}
    northbound: dict = None     # {total, hgt, sgt}
) -> list:                      # 每条形如 "✅ 科创50: 博主说跌3.5%, 实际-3.44%"
```

## 三类验证

### 1. 指数/板块涨跌幅

- 正则匹配: `指数名.*?涨/跌.*?数字%` 或 `数字%.*?指数名`
- 数据源: `quotes` + `sectors` 的 `change_pct` 字段
- 偏差阈值: ✅ <0.3% | ⚠️ 0.3-1.0% | ❌ >1.0%

**示例:**
- 博文: "科创50跌3.5%"
- 实际: 科创50 change_pct=-3.44%
- 结果: ✅ 科创50: 博主说跌3.5%, 实际-3.44%, 一致 ✓

### 2. 成交额

- 正则: `(\d+\.?\d*)\s*万亿` → 转亿比对
- 正则: `[成放量交].*?(\d+\.?\d*)\s*亿` → 仅千亿以上
- 数据源: `market_overview.total_turnover` (从API获取，单位元)
- 偏差阈值: ✅ <2000亿 | ⚠️ ≥2000亿

### 3. 北向资金

- 正则: `北向[流出流入].*?(\d+\.?\d*)\s*亿`
- 数据源: `northbound.total` (正=流入，负=流出)
- 偏差阈值: ✅ <10亿 | ⚠️ ≥10亿

## 数据时点注意事项

- 早报流程(08:30)使用**昨日收盘快照**数据
- KOL说"昨天"时，快照数据时点匹配，核查最准确
- 盘中/收盘核查时应注意数据是否对应同一交易日
- `market_overview` 和 `northbound` 在早盘可能为空 → 跳过对应核查类型

## 集成位置

`collect_morning_data.py` — 信号帖处理流程末尾：

```python
if p['is_signal']:
    interp_parts = []
    interp_parts.append(interpret_weibo(txt, name))      # 黑话破译
    fc = fact_check_kol_claims(txt, quotes, sectors, ...) # 事实核查
    if fc:
        interp_parts.append("📊 **事实核查**\n" + "\n".join(f"> {f}" for f in fc))
    p['interpretation'] = "\n\n".join(interp_parts)
```
