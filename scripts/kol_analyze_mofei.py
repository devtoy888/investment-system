#!/usr/bin/env python3
"""Analyze 莫非是托的微博 - is he a systematic bear? """
import sys, json, time, re, requests
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import CREDENTIAL_FILE

cred = json.loads(CREDENTIAL_FILE.read_text())
cookies = cred.get('cookies', {})
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://weibo.com/',
    'X-Requested-With': 'XMLHttpRequest',
}

UID = '1873999810'
NAME = '莫非是托的微博'

# Pull multiple pages to get enough data
all_posts = []
for page in range(1, 6):
    try:
        r = requests.get(
            f"https://weibo.com/ajax/statuses/mymblog",
            params={"uid": UID, "page": str(page), "feature": "0"},
            cookies=cookies, headers=headers, timeout=15
        )
        data = r.json()
        if data.get("ok") != 1:
            print(f"  Page {page}: ok={data.get('ok')} → stop")
            break
        
        items = data.get("data", {}).get("list", [])
        if not items:
            print(f"  Page {page}: empty → stop")
            break
        
        for p in items:
            text = p.get("text_raw", p.get("text", ""))
            text = re.sub(r'<[^>]+>', '', text)
            all_posts.append({
                'id': p.get('id',''),
                'created_at': p.get('created_at',''),
                'text': text[:500],
                'reposts_count': p.get('reposts_count',0),
                'comments_count': p.get('comments_count',0),
                'attitudes_count': p.get('attitudes_count',0),
            })
        
        dates = [p.get('created_at','')[:11] for p in items]
        print(f"  Page {page}: {len(items)}条 ({dates[-1]} ~ {dates[0]}) 累计{len(all_posts)}")
        time.sleep(2)
        
    except Exception as e:
        print(f"  Page {page}: {e}")
        break

n = len(all_posts)
print(f"\n{'='*60}")
print(f"📋 {NAME}: {n}条博文")
print(f"{'='*60}")

if n == 0:
    print("❌ 无数据")
    sys.exit(1)

# ── 1. TONE ANALYSIS ── (the user's concern: is he a systematic bear?)

# Bear keywords
BEAR_WORDS = [
    '跌', '崩', '逃', '跑', '空', '危', '险', '泡沫', '不行', '完蛋',
    '收割', '骗局', '韭菜', '套牢', '暴跌', '熊市', '清仓', '减仓',
    '风险', '离场', '止损', '不好', '麻烦', '问题', '利空',
]

# Bull keywords
BULL_WORDS = [
    '涨', '牛', '好', '机会', '买', '建仓', '加仓', '抄底',
    '反弹', '突破', '上攻', '拉升', '利好', '支撑', '放量',
    '反攻', '企稳', '走强', '牛市', '做多',
]

# Neutral/analysis keywords
NEUTRAL_WORDS = [
    '分析', '数据', '统计', '历史', '对比', '研究', '观察',
    '关注', '走势', '行情', '指标', '结构', '逻辑', '预计',
]

bear_count = sum(1 for p in all_posts if any(w in p['text'] for w in BEAR_WORDS))
bull_count = sum(1 for p in all_posts if any(w in p['text'] for w in BULL_WORDS))
neutral_count = sum(1 for p in all_posts if any(w in p['text'] for w in NEUTRAL_WORDS))

# Net sentiment score
bear_hits = {}
for w in BEAR_WORDS:
    c = sum(1 for p in all_posts if w in p['text'])
    if c: bear_hits[w] = c

bull_hits = {}
for w in BULL_WORDS:
    c = sum(1 for p in all_posts if w in p['text'])
    if c: bull_hits[w] = c

total_bear = sum(bear_hits.values())
total_bull = sum(bull_hits.values())

print(f"\n📊 情绪分析:")
print(f"  🔴 空头关键词命中: {bear_count}/{n} ({bear_count/n:.0%})")
print(f"  🟢 多头关键词命中: {bull_count}/{n} ({bull_count/n:.0%})")
print(f"  ⚪ 中性分析: {neutral_count}/{n} ({neutral_count/n:.0%})")
print(f"  📊 多空关键词总频次: 空{total_bear} vs 多{total_bull}")
print(f"  📊 多空比值: {total_bull/max(1,total_bear):.2f} (>1=偏多, <1=偏空)")

# Detailed bear word distribution
print(f"\n🔴 空头关键词频次:")
sorted_bear = sorted(bear_hits.items(), key=lambda x:-x[1])
for w, c in sorted_bear[:10]:
    print(f"  「{w}」×{c}")

print(f"\n🟢 多头关键词频次:")
sorted_bull = sorted(bull_hits.items(), key=lambda x:-x[1])
for w, c in sorted_bull[:10]:
    print(f"  「{w}」×{c}")

# ── 2. Content depth analysis ──
short = sum(1 for p in all_posts if len(p['text']) < 30)
medium = sum(1 for p in all_posts if 30 <= len(p['text']) < 200)
long = sum(1 for p in all_posts if len(p['text']) >= 200)
avg_len = sum(len(p['text']) for p in all_posts) / n

print(f"\n📏 内容深度:")
print(f"  均长: {avg_len:.0f}字")
print(f"  短文(<30字): {short}/{n} ({short/n:.0%})")
print(f"  中篇(30-200字): {medium}/{n} ({medium/n:.0%})")
print(f"  长文(>200字): {long}/{n} ({long/n:.0%})")

# ── 3. Time span ──
from datetime import datetime, timezone
dates = []
for p in all_posts:
    try: dates.append(datetime.strptime(p['created_at'], '%a %b %d %H:%M:%S %z %Y'))
    except: pass
if dates:
    span = max(1, (dates[0]-dates[-1]).days)
    freq = round(n/span, 1) if span > 0 else n
    print(f"\n⏰ 时间跨度: {span}天 | 频率: {freq}/天")
    print(f"  最新: {dates[0].strftime('%Y-%m-%d')} | 最老: {dates[-1].strftime('%Y-%m-%d') if dates else '?'}")

# ── 4. Themes ──
THEMES = {
    '科技/AI': ['AI','人工智能','芯片','半导体','科技','算力','英伟达','存储','HBM'],
    '宏观/政策': ['经济','GDP','CPI','利率','加息','降息','联储','通胀','就业'],
    '外资/北向': ['北向','外资','流出','流入','港股','南下'],
    'A股大盘': ['大盘','指数','A股','上证','创业板','沪深300'],
    '地产': ['地产','房地产','楼市','房价','恒大','碧桂园'],
    '贵金属/黄金': ['黄金','金价','白银','贵金属'],
    '板块/行业': ['板块','行业','概念','题材','轮动'],
    '股民情绪': ['韭菜','散户','机构','主力','游资'],
}

theme_hits = {}
for theme, kws in THEMES.items():
    c = sum(1 for p in all_posts if any(kw in p['text'] for kw in kws))
    if c: theme_hits[theme] = c

print(f"\n🏷️  主题分布:")
for t, c in sorted(theme_hits.items(), key=lambda x:-x[1]):
    print(f"  {t}: {c}/{n} ({c/n:.0%})")

# ── 5. Show representative posts ──
print(f"\n📰 代表性博文:")

# Most bearish posts
bear_posts = [p for p in all_posts if any(w in p['text'] for w in ['崩','逃','收割','熊市','暴跌','泡沫','清仓'])]
print(f"\n  🔴 最具空头倾向的博文:")
for p in bear_posts[:4]:
    txt = p['text'][:100].replace('\n',' ')
    print(f"    [{p['created_at'][:10]}] {txt}")

# Most bullish posts
bull_posts = [p for p in all_posts if any(w in p['text'] for w in ['抄底','牛','突破','大涨','拉升','反攻'])]
print(f"\n  🟢 最具多头倾向的博文:")
for p in bull_posts[:4]:
    txt = p['text'][:100].replace('\n',' ')
    print(f"    [{p['created_at'][:10]}] {txt}")

# ── 6. Check specific predictions ──
print(f"\n🔍 可验证的判断:")
verifiable = []
for p in all_posts:
    if any(w in p['text'] for w in ['2026','今年','本周','下月']) and len(p['text']) > 40:
        verifiable.append(p)
for p in verifiable[:5]:
    txt = p['text'][:120].replace('\n',' ')
    print(f"  [{p['created_at'][:10]}] {txt}")

# ── 7. Final assessment ──
print(f"\n{'='*60}")
print("📋 综合评估")
print(f"{'='*60}")

ratio = total_bull / max(1, total_bear)
if ratio < 0.5:
    tone = '🔴 系统性强空头倾向'
elif ratio < 0.8:
    tone = '🟠 偏空头'
elif ratio < 1.2:
    tone = '⚪ 相对均衡'
elif ratio < 1.5:
    tone = '🟢 偏多头'
else:
    tone = '🟢 系统性强多头倾向'

print(f"\n多空关键词比: {total_bull}:{total_bear} = {ratio:.2f}")
print(f"基调判定: {tone}")

if total_bear > total_bull * 2:
    print(f"\n⚠️ 你的直觉验证: 他的空头关键词频次是多头的{ratio:.1f}倍")
    print(f"   → 数据支持你的判断: 他确实有系统性的看空倾向")
    print(f"   → 但他是否'为了唱空而唱空'还需要看他的判断逻辑是否有依据")
elif total_bear > total_bull:
    print(f"\n⚠️ 他的内容偏空, 但并非极端")
else:
    print(f"\n✅ 他并非系统性看空")

# Info density check
print(f"\n信息密度评估:")
post_per_day = freq if dates else n
print(f"  日均发帖: {post_per_day}")
print(f"  长文占比: {long/n:.0%}")
print(f"  多空关键词总量: {total_bear+total_bull}")
if long/n < 0.1 and avg_len < 60:
    print(f"  → ⚠️ 内容偏短, 多为情绪式表达而非深度分析")
elif long/n > 0.3:
    print(f"  → ✅ 有较多深度分析内容")

# Save
out = '/tmp/mofei_analysis.json'
json.dump({
    'uid': UID, 'name': NAME, 'n': n,
    'bear_hits': bear_hits, 'bull_hits': bull_hits,
    'total_bear': total_bear, 'total_bull': total_bull,
    'ratio': ratio, 'avg_len': round(avg_len),
    'short_pct': round(short/n, 2), 'long_pct': round(long/n, 2),
    'themes': theme_hits,
}, open(out,'w'), ensure_ascii=False, indent=2)
print(f"\n✅ -> {out}")
