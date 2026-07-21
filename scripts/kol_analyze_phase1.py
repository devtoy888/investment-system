#!/usr/bin/env python3
"""Merge Phase 0 + Phase 1 and re-analyze"""
import json, sys
from datetime import datetime, timezone
# Make utcfromtimestamp available since Python 3.12+ compat
if not hasattr(datetime, 'utcfromtimestamp'):
    def utcfromtimestamp(ts): return datetime.fromtimestamp(ts, tz=timezone.utc)
    datetime.utcfromtimestamp = utcfromtimestamp

SIGNAL_WORDS_MAP = {
    '建仓':'buy','加仓':'buy','吸筹':'buy','吸点':'buy','买入':'buy',
    '触底':'buy','右侧':'buy','确定性':'buy','补':'buy','加':'buy',
    '减仓':'sell','出货':'sell','减':'sell','调出':'sell',
    '洗盘':'hold','震荡':'hold','观望':'hold',
    '泡沫':'caution','风险':'caution','谨慎':'caution','小心':'caution',
}

THEME_KW = {
    '科技/半导体':['存储','芯片','半导体','AI','算力','光模块','美光','HBM','fab','封装'],
    '新能源':['新能源','光伏','锂电','功率'],
    '宏观/政策':['联储','美联储','加息','降息','CPI','GDP','美元','利率'],
    '消费/白酒':['白酒','消费'],
    '黄金':['黄金','金价'],
    '军工':['军工','国防'],
    'A股大盘':['A股','大盘','指数','上证','科创','创业板','两市'],
}

# Load both phases
p0 = json.loads(open('/tmp/kol_phase0_raw.json').read())
p1 = json.loads(open('/tmp/kol_phase1_p2p3.json').read())

# Merge: p0 posts + p1 posts (dedup by id)
KOLS = {'2014433131':'唐史主任司马迁','5044466342':'IT精英带你养基','6114912545':'小浣熊1230'}
merged = {}
for uid, name in KOLS.items():
    seen_ids = set()
    all_posts = []
    for p in p0.get(uid,{}).get('posts',[]):
        if p['id'] not in seen_ids:
            seen_ids.add(p['id'])
            all_posts.append(p)
    for p in p1.get(uid,{}).get('posts',[]):
        if p['id'] not in seen_ids:
            seen_ids.add(p['id'])
            all_posts.append(p)
    all_posts.sort(key=lambda x: x['created_at'], reverse=True)
    merged[uid] = {'name':name, 'posts':all_posts, 'deduped':len(seen_ids)}
    print(f"{name}: 合并后 {len(seen_ids)} 条")

# Run analysis on merged data
profiles = {}
for uid, kd in merged.items():
    name = kd['name']
    posts = kd['posts']
    n = len(posts)
    if not posts:
        profiles[uid] = {'name':name,'error':'无数据','needs_more':True}
        continue

    # Time
    dates = []
    for d in [p['created_at'] for p in posts]:
        try: dates.append(datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y'))
        except: pass
    span = max(1,(dates[0]-dates[-1]).days) if dates else 1
    freq = round(n/span,2) if dates else 0
    r3 = sum(1 for d in dates if (dates[0]-d).days<3) if dates else 0

    # Signal
    sigs = {}
    for w, st in SIGNAL_WORDS_MAP.items():
        c = sum(1 for p in posts if w in p['text'])
        if c: sigs[w] = {'count':c, 'type':st}
    sig_posts = [p for p in posts if any(w in p['text'] for w in SIGNAL_WORDS_MAP)]
    density = round(len(sig_posts)/n, 2)

    # Themes
    th = {}
    for t, kw in THEME_KW.items():
        c = sum(1 for p in posts if any(k in p['text'] for k in kw))
        if c: th[t] = c
    top_t = sorted(th.items(), key=lambda x:-x[1])[:5]

    # Style
    t = ' '.join(p['text'] for p in posts)
    styles = []
    if any(w in t for w in ['联储','美联储','宏观']): styles.append('宏观分析型')
    if any(w in t for w in ['买入','卖出','加仓','减仓','调仓','操作']): styles.append('操作信号型')
    if any(w in t for w in ['情绪','格局','方向','坚定','相信']): styles.append('情绪引导型')
    if any(w in t for w in ['无操作','定投']): styles.append('日常定投型')
    if not styles: styles=['待分析']

    bs = sum(v['count'] for v in sigs.values() if v['type']=='buy')
    ss = sum(v['count'] for v in sigs.values() if v['type']=='sell')
    cs = sum(v['count'] for v in sigs.values() if v['type']=='caution')

    # Saturation check - stricter at Phase 1
    # Methodology: compare signal_density stability
    # Split posts into first half and second half, compare densities
    half = n // 2
    first_half = posts[:half]
    second_half = posts[half:]
    
    sig_first = sum(1 for p in first_half if any(w in p['text'] for w in SIGNAL_WORDS_MAP)) / max(1,len(first_half))
    sig_second = sum(1 for p in second_half if any(w in p['text'] for w in SIGNAL_WORDS_MAP)) / max(1,len(second_half))
    stability = round(1 - abs(sig_first - sig_second), 2)

    # Expansion decision with advanced criteria
    reasons = []
    need_ext = True
    
    if n < 80:
        reasons.append(f'样本{n}<80')
    if density < 0.2:
        reasons.append(f'密度{density:.0%}<20%')
    if stability < 0.6:
        reasons.append(f'稳定性{stability:.0%}<60%')
    if freq > 0.5 and n < 100:
        reasons.append(f'高频博主，样本仍需扩展')
    if density > 0.3 and n >= 50 and stability >= 0.6:
        need_ext = False
        reasons = ['已达饱和阈值']
    
    if need_ext and not reasons:
        reasons.append('待进一步验证')
    elif need_ext and reasons:
        pass  # keep reasons
    elif not need_ext and not reasons:
        reasons = ['已达饱和']

    p = {
        'name':name,'uid':uid,'phase':1,'n':n,
        'span_days':span,'freq_day':freq,'recent_3day':r3,
        'signal_density':density,'signal_words':sigs,
        'buy':bs,'sell':ss,'caution':cs,
        'themes':[{'t':t,'c':c} for t,c in top_t],
        'styles':styles,
        'stability':stability,  # 前后半段信号密度一致性
        'first_half_density':round(sig_first,2),
        'second_half_density':round(sig_second,2),
        'needs_more':need_ext,'reason':reasons[0],
        'date':datetime.now().isoformat(),
    }
    profiles[uid] = p

    print(f"\n{'='*55}")
    print(f"📋 V2: {name}")
    print(f"{'='*55}")
    print(f"  📊 {n}条 | {span}天 | {freq}/天 | 近3天{r3}条")
    print(f"  📡 信号密度: {density:.0%} ({len(sig_posts)}/{n}) | 买{bs} 卖{ss} 警{cs}")
    print(f"  📊 稳定性(前后半段): {stability:.0%} (前半{sig_first:.0%} vs 后半{sig_second:.0%})")
    print(f"  🎨 风格: {', '.join(styles)}")
    print(f"  🏷️  主题: {' | '.join(f'{t}({c})' for t,c in top_t[:4])}")
    top_s = sorted(sigs.items(), key=lambda x:-x[1]['count'])[:8]
    sig_strs = [f'「{w}」×{v["count"]}' for w,v in top_s]
    print(f"  🔑 信号词: {' '.join(sig_strs)}")
    print(f"  🔄 扩展: {'⚠️ ' + reasons[0] if need_ext else '✅ 饱和'}")
    
    # Show 2 new posts not in Phase 0
    p0_ids = set(p['id'] for p in p0.get(uid,{}).get('posts',[]))
    new_ones = [p for p in posts if p['id'] not in p0_ids][:3]
    print(f"  📰 新增代表性博文(非Phase0):")
    for np in new_ones:
        txt = np['text'][:60].replace('\n',' ')
        m = '🔴S' if any(w in np['text'] for w in SIGNAL_WORDS_MAP) else '⚪'
        print(f"    {m} [{np['created_at'][:11]}] {txt}")

json.dump(profiles, open('/tmp/kol_profiles_phase1.json','w'), ensure_ascii=False, indent=2)
print(f"\n✅ Phase 1 profiles -> /tmp/kol_profiles_phase1.json")

print(f"\n{'='*55}")
print("📊 饱和判定汇总")
print(f"{'='*55}")
for uid, p in profiles.items():
    st = '✅ 饱和' if not p.get('needs_more') else f"⚠️ 需扩展({p.get('reason','')})"
    print(f"  {p['name']}: {st} | 密度{p['signal_density']:.0%} | {p['n']}条 | 稳定性{p.get('stability',0):.0%}")
