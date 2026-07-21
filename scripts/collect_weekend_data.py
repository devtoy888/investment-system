#!/usr/bin/env python3
"""
周末外盘速报 v2 — 采集周五美股收盘 + 持仓影响分析 + KOL信号方向
周六 09:00 CST 运行，stdout=推送内容
"""
import sys, json, os, time
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import OVERNIGHT_SYMBOLS, _yahoo_quote, KOLS, get_user_weibos, interpret_weibo, get_group_trend
from datetime import datetime, date, timezone, timedelta

today = date.today()
WEEKDAY_CN = ["一","二","三","四","五","六","日"]
wd = WEEKDAY_CN[today.weekday()]

# 取周五
friday = today - timedelta(days=1) if today.weekday() == 5 else today - timedelta(days=2) if today.weekday() == 6 else today
fw = WEEKDAY_CN[friday.weekday()]

lines = []
def out(s=""):
    lines.append(s)

# ── 持仓影响映射规则 ──
OVERNIGHT_IMPACT_MAP = [
    ('黄金期货', '黄金', '黄金组', lambda p: p, '直连'),
    ('纳斯达克', '科技/AI', '科技/AI组', lambda p: p * 0.4, '弱相关（A股科技独立行情更强）'),
    ('标普500', '大盘', '大盘方向', lambda p: p * 0.3, '弱相关'),
    ('美元指数', '资源/周期', '资源/周期组', lambda p: -p * 0.5, '反向（美元强→商品弱）'),
    ('道琼斯', '大盘', '大盘情绪', lambda p: p * 0.2, '弱相关'),
    ('恒生指数', '科技/AI', '恒生科技方向', lambda p: p * 0.3, '弱相关'),
]

def assess_impact(name, q, quotes):
    """Return (group, emoji, description)"""
    pct = q['change_pct']
    for key, group, label, weight, note in OVERNIGHT_IMPACT_MAP:
        if name == key:
            weighted = round(weight(pct), 2)
            # 如果这个组已经出过评估，跳过
            if group == '大盘' and name not in ('道琼斯', '标普500'):
                return (label, '🟡', f'暂无数据')
            if group == '大盘':
                # 只用道琼斯评估大盘情绪，标普500跳过
                if name == '标普500':
                    return (f'{name}', '🟡', f'标普{name[-3:]} {pct:+.2f}% → 参考道琼斯')
            weighted = round(weight(pct), 2)
            if group == '黄金':
                if pct > 1:     return (label, '🔴', f'金价大涨 {pct:+.2f}% → {label}显著利好')
                if pct > 0.3:   return (label, '🔴', f'金价上涨 {pct:+.2f}% → {label}偏多')
                if pct > -0.3:  return (label, '🟡', f'金价微调 {pct:+.2f}% → {label}影响有限')
                return (label, '🟢', f'金价下跌 {pct:+.2f}% → {label}承压')
            elif group == '科技/AI':
                if pct > 2:     return (label, '🔴', f'{name}大涨 {pct:+.2f}% → {label}情绪利好')
                if pct > 0:     return (label, '🔴', f'{name}上涨 {pct:+.2f}% → {label}偏多')
                if pct > -1.5:  return (label, '🟡', f'{name}微跌 {pct:+.2f}% → 影响有限，看A股自身')
                return (label, '🟢', f'{name}大跌 {pct:+.2f}% → {label}承压')
            elif group == '资源/周期':
                if pct > 0.5:   return (label, '🟢', f'美元走强 {pct:+.2f}% → {label}承压(商品弱)')
                if pct > -0.5:  return (label, '🟡', f'美元 {pct:+.2f}% → {label}影响中性')
                return (label, '🔴', f'美元走弱 {pct:+.2f}% → {label}利好(商品强)')
            else:
                # 大盘情绪
                if pct > 1:     return (label, '🔴', f'{name}大涨 {pct:+.2f}% → 大盘情绪偏暖')
                if pct > 0:     return (label, '🔴', f'{name}上涨 {pct:+.2f}% → 大盘情绪中性偏暖')
                if pct > -1:    return (label, '🟢', f'{name}微跌 {pct:+.2f}% → 影响有限')
                return (label, '🟢', f'{name}下跌 {pct:+.2f}% → 大盘情绪偏弱')
    return (f'{name}影响', '🟡', f'{name} {pct:+.2f}% → 影响待观察')

def score_signal_direction(text):
    """简单信号方向判断"""
    bull = ['看多','买入','加仓','增持','机会','利好','右侧','地板','吃肉']
    bear = ['看空','卖出','减仓','减持','风险','利空','出货','砸盘','天花板']
    text_lower = text.lower()
    b = sum(1 for w in bull if w in text_lower)
    s = sum(1 for w in bear if w in text_lower)
    if b > s + 1: return '🔴', '偏多'
    if s > b + 1: return '🟢', '偏空/提示风险'
    return '🟡', '中性/观察'

# ── 标题 ──
out(f"━━━ 周末外盘速报 · {today.month}月{today.day}日({wd}) ━━━")
out()

# ═══ 1. 外盘收盘 ═══
out(f"🌙 上周{fw}美股收盘")
quotes = {}
has_data = False
for name, symbol in OVERNIGHT_SYMBOLS.items():
    q = _yahoo_quote(symbol)
    if q:
        quotes[name] = q
        emoji = '🔴' if q['change_pct'] > 0 else ('🟢' if q['change_pct'] < 0 else '🟡')
        price_fmt = f"{q['price']:,.2f}" if isinstance(q['price'], (int, float)) else str(q['price'])
        out(f"  {emoji} {name}: {price_fmt}  ({q['change_pct']:+.2f}%)")
        has_data = True
    else:
        out(f"  ❌ {name}: 数据获取失败")
    time.sleep(0.3)
if not has_data:
    out("  ⚠️ 外盘数据全部获取失败，稍后手动检查")
out()

# ═══ 2. 持仓影响评估（新增）═══
if has_data:
    out("📊 **持仓影响评估**")
    assessed = set()
    for name, q in quotes.items():
        label, emoji, desc = assess_impact(name, q, quotes)
        if label not in assessed:
            out(f"  {emoji} {label}: {desc}")
            assessed.add(label)
    out()

# ═══ 3. 一周回顾（外盘周比 + 分组趋势）═══
if has_data:
    out("📈 **一周回顾**")
    # 外盘周同比（用markdown表格）
    prev_file = "/tmp/fund_data/_weekend_prev.json"
    save_data = {name: q['change_pct'] for name, q in quotes.items()}
    if os.path.exists(prev_file):
        try:
            prev = json.loads(open(prev_file).read())
            out("| 品种 | 上周 | 本周 | 变化 |")
            out("|------|:---:|:---:|:----:|")
            for name, q in quotes.items():
                prev_pct = prev.get(name)
                if prev_pct is not None:
                    diff = q['change_pct'] - prev_pct
                    direction = "📈 扩大涨幅" if q['change_pct'] > 0 and diff > 0 else \
                                "📉 收窄涨幅" if q['change_pct'] > 0 and diff < 0 else \
                                "📉 跌幅扩大" if q['change_pct'] < 0 and diff < 0 else \
                                "📈 跌幅收窄" if q['change_pct'] < 0 and diff > 0 else \
                                "➖ 基本持平"
                    emoji = '🔴' if q['change_pct'] > 0 else ('🟢' if q['change_pct'] < 0 else '🟡')
                    out(f"| {emoji} {name} | {prev_pct:+.2f}% | {q['change_pct']:+.2f}% | {direction} |")
        except: pass
        out()
    # 分组趋势（markdown表格 + sparkline）
    out("📊 **分组本周趋势**")
    found_trend = False
    spark_chars = ['▁','▂','▃','▄','▅','▆','▇','█']
    for gname in ['黄金', '科技/AI', '资源/周期', '新能源', '医药']:
        trend = get_group_trend(gname, 5)
        if trend:
            if not found_trend:
                out("| 分组 | 走势 | 本周幅度 |")
                out("|:----|:---:|:--------:|")
                found_trend = True
            vals = [d[1] for d in trend]
            if max(vals) == min(vals):
                spark = '▄' * len(vals)
            else:
                rng = max(vals) - min(vals)
                spark = ''.join(spark_chars[min(int((v - min(vals)) / rng * 7), 7)] for v in vals)
            # 趋势方向描述
            first, last = vals[0], vals[-1]
            if last > first * 1.1 and last < 0:
                direction = '📈 跌幅收窄'
            elif last < first and last < 0:
                direction = '📉 跌幅扩大'
            elif last > first and last > 0:
                direction = '📈 持续上行'
            elif last < first and last > 0:
                direction = '📉 涨幅收窄'
            else:
                direction = '➖ 震荡'
            out(f"| {gname} | {spark} | {min(vals):+.1f}% → {max(vals):+.1f}% {direction} |")
    if not found_trend:
        out("  （暂无趋势数据）")
    # 保存本周数据供下周对比
    try:
        with open(prev_file, 'w') as f:
            json.dump(save_data, f)
    except: pass
    out()

# ═══ 4. 博主信号（增强版）═══
out("📰 **博主信号**")
kol_found = False
skip_keywords = ["置顶", "简单说明", "帮我点", "点赞", "助威", "大家好"]

for uid, name in KOLS.items():
    if name == "IT精英带你养基":
        continue
    posts = get_user_weibos(uid, count=5)
    if not posts:
        continue
    for p in posts:
        text = p.get('text', '').strip()
        if not text:
            continue
        if any(kw in text[:30] for kw in skip_keywords):
            continue
        text_clean = text.replace('\n', ' ').strip()
        dot_pos = text_clean.find('。')
        if dot_pos > 10 and dot_pos < 80:
            excerpt = text_clean[:dot_pos+1]
        else:
            excerpt = text_clean[:60]
            if len(text_clean) > 60:
                excerpt += "…"
        # 信号方向
        emoji, direction = score_signal_direction(text)
        # 关键黑话解读
        blacktalk = interpret_weibo(text, name)
        out(f"  [{name}] {excerpt}")
        out(f"   → {emoji} 信号方向: {direction}")
        if blacktalk:
            out(f"  {blacktalk}")
        kol_found = True
        break

    if not kol_found:
        out("  （周末暂无博主新信号）")
out()

# ═══ 5. 周一关注（增强版）═══
out("📌 **周一关注**")
out("  ● 以上为周五收盘，周一A50开盘将反映外盘变化")
# 基于金价的方向性提示
if '黄金期货' in quotes:
    gp = quotes['黄金期货']['change_pct']
    if gp > 0.5:
        out("  ● 🔴 黄金强势 → 持仓黄金组有望继续领涨")
    elif gp > -0.3:
        out("  ● 🟡 黄金企稳 → 黄金组持仓不变")
    else:
        out("  ● 🟢 黄金回调 → 观察是否跌破支撑")
if '纳斯达克' in quotes:
    np = quotes['纳斯达克']['change_pct']
    if np > 1:
        out("  ● 🔴 纳指上涨 → 科技/AI组周一有望高开")
    elif np < -1.5:
        out("  ● 🟢 纳指回落 → 科技/AI组关注低开后的承接")
    else:
        out("  ● 🟡 纳指震荡 → 科技组关注A股自身趋势")
out("  ● ⚡ 周末重大事件将于周一「今日参考」更新")

print("\n".join(lines))
