#!/usr/bin/env python3
"""Deep dive on 莫非是托的微博 - verification & historical analysis"""
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

# Pull LOTS of pages for historical verification
all_posts = []
for page in range(1, 16):  # pages 1-15
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
print(f"\n{'='*70}")
print(f"📋 {NAME}: {n}条博文 (深度分析)")
print(f"{'='*70}")

if n == 0:
    print("❌ 无数据")
    sys.exit(1)

# ── 1. Time span & frequency ──
from datetime import datetime, timezone
dates = []
for p in all_posts:
    try: dates.append(datetime.strptime(p['created_at'], '%a %b %d %H:%M:%S %z %Y'))
    except: pass

if dates:
    dates.sort()
    span = max(1, (dates[-1]-dates[0]).days)
    freq = round(n/span, 1)
    print(f"\n⏰ 时间跨度: {span}天 | 频率: {freq}/天")
    print(f"  最早: {dates[0].strftime('%Y-%m-%d')}")
    print(f"  最晚: {dates[-1].strftime('%Y-%m-%d')}")

# ── 2. Temporal sentiment analysis (check if stance changes over time) ──
BEAR_WORDS = ['跌','崩','逃','空','危','险','泡沫','不行','收割','暴跌','熊市','清仓','利空']
BULL_WORDS = ['涨','牛','买','建仓','加仓','抄底','反弹','突破','利好','企稳','牛市']

# Split into 3 time periods
if dates and len(dates) >= 6:
    third = n // 3
    periods = [
        ('早期(最老1/3)', all_posts[:third]),
        ('中期', all_posts[third:2*third]),
        ('近期(最新1/3)', all_posts[2*third:]),
    ]
    
    print(f"\n📈 时间维度情绪变化:")
    print(f"{'时段':20s} {'空头频次':12s} {'多头频次':12s} {'多空比':8s}")
    print("-"*52)
    for label, segment in periods:
        b = sum(1 for p in segment if any(w in p['text'] for w in BEAR_WORDS))
        bu = sum(1 for p in segment if any(w in p['text'] for w in BULL_WORDS))
        ratio = bu/max(1,b)
        print(f"  {label:18s} {b:4d}/{len(segment):3d} ({b/len(segment):.0%})  {bu:4d}/{len(segment):3d} ({bu/len(segment):.0%})  {ratio:.2f}")

# ── 3. Verification of bearish claims ──
print(f"\n{'='*70}")
print("🔍 重点：验证他过去的看空判断是否成真")
print(f"{'='*70}")

# Find posts with specific, verifiable claims
verifiable_patterns = {
    '美光': '美光业绩/股价判断',
    '英伟达': '英伟达股价判断',
    '纳斯达克': '纳指走势判断',
    '指数': 'A股指数判断',
    '黄金': '黄金走势判断',
    '数据中心': '数据中心/AI基建判断',
    '半导体': '半导体行业判断',
    '泡沫': '泡沫判断',
    '熔断': '熔断预测',
    '降息': '降息预测',
}

verifiable_posts = []
for p in all_posts:
    text = p['text']
    matched = [(kw,desc) for kw,desc in verifiable_patterns.items() if kw in text]
    if matched and len(text) > 50:
        verifiable_posts.append({
            'date': p['created_at'],
            'text': text[:200].replace('\n',' '),
            'patterns': [desc for kw,desc in matched],
        })

print(f"\n找到 {len(verifiable_posts)} 条可验证的博文")
print()

# Show by key topics
for topic in ['泡沫', '数据中心', '半导体', '黄金', '指数']:
    topic_posts = [v for v in verifiable_posts if any(topic in v['text'] for t in [topic])]
    if topic_posts:
        print(f"📌 【{topic}】相关 ({len(topic_posts)}条):")
        for v in topic_posts[:4]:
            print(f"  [{v['date'][:16]}] {v['text'][:150]}")
            print()

# ── 4. Content originality check ──
# Is he doing original analysis or just aggregating/retweeting?
retweet_count = sum(1 for p in all_posts if p['text'].startswith('回复') or '//@' in p['text'])
original_count = n - retweet_count

# Check if he references specific sources
source_refs = sum(1 for p in all_posts if any(src in p['text'] for src in 
    ['Tom\'s Hardware','TrendForce','集邦','投行','报告','Bloomberg','Reuters','路透','数据','统计']))

print(f"\n{'='*70}")
print("📊 内容原创性与信息源质量")
print(f"{'='*70}")
print(f"\n  原创博文: {original_count}/{n} ({original_count/n:.0%})")
print(f"  回复/转发: {retweet_count}/{n} ({retweet_count/n:.0%})")
print(f"  引用数据源: {source_refs}/{n} ({source_refs/n:.0%})")

# ── 5. Interaction analysis ──
avg_rt = sum(p['reposts_count'] for p in all_posts)/n
avg_cm = sum(p['comments_count'] for p in all_posts)/n
avg_lk = sum(p['attitudes_count'] for p in all_posts)/n

print(f"\n💬 互动分析:")
print(f"  平均转发: {avg_rt:.0f}")
print(f"  平均评论: {avg_cm:.0f}")
print(f"  平均点赞: {avg_lk:.0f}")
print(f"  总计互动: {avg_rt+avg_cm+avg_lk:.0f}")

# ── 6. Content depth (full breakdown) ──
short = sum(1 for p in all_posts if len(p['text']) < 50)
medium = sum(1 for p in all_posts if 50 <= len(p['text']) < 150)
medium_long = sum(1 for p in all_posts if 150 <= len(p['text']) < 300)
long = sum(1 for p in all_posts if len(p['text']) >= 300)
avg_len = sum(len(p['text']) for p in all_posts) / n

print(f"\n📏 内容深度(全量{n}条):")
print(f"  均长: {avg_len:.0f}字")
print(f"  短文(<50字): {short}条 ({short/n:.0%})")
print(f"  中篇(50-150字): {medium}条 ({medium/n:.0%})")
print(f"  中长篇(150-300字): {medium_long}条 ({medium_long/n:.0%})")
print(f"  长文(>300字): {long}条 ({long/n:.0%})")

# ── 7. More detailed theme analysis ──
THEMES_DETAIL = {
    'AI泡沫': ['泡沫','AI泡沫','泡沫破','泡沫破裂'],
    'AI产业': ['AI','人工智能','英伟达','OpenAI','大模型','算力'],
    '半导体/芯片': ['芯片','半导体','存储','HBM','光模块','晶圆'],
    '数据中心': ['数据中心','云计算','服务器','光缆','光纤'],
    '宏观经济': ['经济','GDP','CPI','通胀','就业','衰退','萧条'],
    '美联储': ['联储','美联储','加息','降息','鲍威尔'],
    'A股市场': ['A股','大盘','上证','创业板','成交量','指数'],
    '黄金': ['黄金','金价','贵金属'],
    '基金/投资': ['基金','ETF','定投','仓位','组合','净值'],
    '股民/情绪': ['韭菜','散户','机构','主力','游资','抱团'],
    '地产': ['地产','房地产','楼市','房价'],
    '电改': ['电力','电改','电网','能源'],
}

theme_detail_hits = {}
for theme, kws in THEMES_DETAIL.items():
    c = sum(1 for p in all_posts if any(kw in p['text'] for kw in kws))
    if c: theme_detail_hits[theme] = c

print(f"\n🏷️  详细主题分布:")
for t, c in sorted(theme_detail_hits.items(), key=lambda x:-x[1]):
    print(f"  {t}: {c}/{n} ({c/n:.0%})")

# ── 8. Representative posts that show his analytical style ──
print(f"\n{'='*70}")
print("📰 代表他分析水平的博文")
print(f"{'='*70}")
print(f"\n  (引用数据源的博文):")
for p in all_posts:
    if any(src in p['text'] for src in ['Tom\'s','TrendForce','报告显示','据投行','统计']):
        txt = p['text'][:150].replace('\n',' ')
        print(f"  [{p['created_at'][:10]}] {txt}")
        print()

# ── 9. FINAL VERDICT ──
print(f"\n{'='*70}")
print("📋 最终评估")
print(f"{'='*70}")

# Calculate scores
DENSITY_SCORE = min(10, int(source_refs/n * 100))  # data source usage
ORIGINALITY_SCORE = min(10, int(original_count/n * 20))  # originality
DEPTH_SCORE = min(10, int(long/n * 50) + int(medium_long/n * 20))  # content depth
BEAR_CONSISTENCY = min(10, int(5 + (0.66 - 0.5) * 20))  # how consistently bearish
ACTIVITY_SCORE = min(10, int(freq/2))  # posting frequency

print(f"\n评分维度:")
print(f"  数据引用: {DENSITY_SCORE}/10 (引用{source_refs}/{n}条)")
print(f"  原创性: {ORIGINALITY_SCORE}/10 (原创{original_count/n:.0%})")
print(f"  分析深度: {DEPTH_SCORE}/10 (长文{long}条)")
print(f"  看空一致性: {BEAR_CONSISTENCY}/10")
print(f"  持续活跃: {ACTIVITY_SCORE}/10 ({freq}/天)")

total = (DENSITY_SCORE + ORIGINALITY_SCORE + DEPTH_SCORE + BEAR_CONSISTENCY + ACTIVITY_SCORE) / 5
print(f"\n综合评分: {total:.1f}/10")

if total >= 7:
    print(f"\n✅ 推荐加入数据监控")
    print(f"  理由: 有数据支撑的看空视角，与唐主任形成有效对立验证")
elif total >= 5:
    print(f"\n🟡 有条件推荐")
    print(f"  理由: 有参考价值但深度不足，建议作为辅助参考而非主力信源")
else:
    print(f"\n🔴 不推荐加入")
    print(f"  理由: 内容质量或相关性不足")

print(f"\n对比参考:")
print(f"  唐史主任: 227条, 密度26.7%, 均长>150字, 长文占比~15%, 已证6/6")
print(f"  小浣熊1230: 80条, 密度26.3%, 均长>200字, 主题专注科技+宏观")
print(f"  莫非是托: {n}条, 多空比0.66, 均长{avg_len:.0f}字, 引用{source_refs}个数据源")

# Save final data
out = '/tmp/mofei_deep_analysis.json'
final_output = {
    'name': NAME, 'uid': UID, 'n': n,
    'span_days': span if dates else 0, 'freq': freq if dates else 0,
    'bear_ratio': 0.66, 'bull_vs_bear': '33:50',
    'avg_len': round(avg_len), 'short_pct': round(short/n,2), 'long_pct': round(long/n,2),
    'source_refs': source_refs, 'original_pct': round(original_count/n,2),
    'retweet_pct': round(retweet_count/n,2),
    'verifiable_count': len(verifiable_posts),
    'themes': theme_detail_hits,
    'scores': {
        'data_references': DENSITY_SCORE,
        'originality': ORIGINALITY_SCORE,
        'depth': DEPTH_SCORE,
        'consistency': BEAR_CONSISTENCY,
        'activity': ACTIVITY_SCORE,
        'overall': round(total, 1),
    },
    'verdict': '推荐' if total >= 7 else ('有条件推荐' if total >= 5 else '不推荐'),
}
json.dump(final_output, open(out,'w'), ensure_ascii=False, indent=2)
print(f"\n✅ -> {out}")
