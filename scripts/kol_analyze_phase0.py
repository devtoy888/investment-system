#!/usr/bin/env python3
"""Phase 0 KOL Profile Analysis"""
import json, sys
from datetime import datetime

data = json.loads(open('/tmp/kol_phase0_raw.json').read())

SIGNAL_WORDS_MAP = {
    '建仓': 'buy', '加仓': 'buy', '吸筹': 'buy', '吸点': 'buy', '买入': 'buy',
    '触底': 'buy', '右侧': 'buy', '确定性': 'buy', '补': 'buy',
    '减仓': 'sell', '出货': 'sell', '减': 'sell', '调出': 'sell',
    '洗盘': 'hold', '震荡': 'hold', '观望': 'hold',
    '泡沫': 'caution', '风险': 'caution', '谨慎': 'caution',
}

THEME_KW = {
    '科技/半导体': ['存储','芯片','半导体','AI','算力','光模块','美光','HBM','fab','封装'],
    '新能源': ['新能源','光伏','锂电','功率'],
    '宏观/政策': ['联储','美联储','加息','降息','CPI','GDP','美元','利率'],
    '消费/白酒': ['白酒','消费'],
    '黄金': ['黄金','金价'],
    '军工': ['军工','国防'],
    'A股大盘': ['A股','大盘','指数','上证','科创','创业板'],
}

profiles = {}
for uid, kd in data.items():
    name = kd['name']
    posts = kd['posts']
    if not posts:
        profiles[uid] = {'name':name,'error':'无数据','needs_more_data':True}
        continue

    # Time analysis
    dates = []
    for d in [p['created_at'] for p in posts]:
        try: dates.append(datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y'))
        except: pass
    span = max(1, (dates[0]-dates[-1]).days) if dates else 1
    freq = round(len(dates)/span, 2) if dates else 0
    r3 = sum(1 for d in dates if (dates[0]-d).days<3) if dates else 0

    # Signal
    sigs = {}
    for w, st in SIGNAL_WORDS_MAP.items():
        c = sum(1 for p in posts if w in p['text'])
        if c: sigs[w] = {'count':c, 'type':st}
    sig_posts = [p for p in posts if any(w in p['text'] for w in SIGNAL_WORDS_MAP)]
    density = round(len(sig_posts)/len(posts), 2)

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
    if not styles: styles = ['待分析']

    bs = sum(v['count'] for v in sigs.values() if v['type']=='buy')
    ss = sum(v['count'] for v in sigs.values() if v['type']=='sell')

    # Expansion decision
    reasons = []
    need_ext = True
    if len(posts) < 80: reasons.append(f'样本{len(posts)}<80')
    if density < 0.3: reasons.append(f'密度{density:.0%}<30%')
    if freq > 0.5 and span < 30: reasons.append(f'高频博主仅{span}天数据')
    if not reasons: need_ext = False; reasons = ['已达初步饱和']

    p = {
        'name':name,'uid':uid,'phase':0,'n':len(posts),
        'span_days':span,'freq_day':freq,'recent_3day':r3,
        'signal_density':density,'signal_words':sigs,
        'buy_count':bs,'sell_count':ss,
        'themes':[{'t':t,'c':c} for t,c in top_t],
        'styles':styles,
        'needs_more':need_ext,'reason':reasons[0],
        'date':datetime.now().isoformat(),
    }
    profiles[uid] = p

    print(f"\n{'='*55}")
    print(f"📋 KOL: {name} ({uid})")
    print(f"{'='*55}")
    print(f"  📊 {len(posts)}条 | {span}天 | {freq}/天 | 近3天{r3}条")
    print(f"  📡 信号密度: {density:.0%} ({len(sig_posts)}/{len(posts)}) | 买{bs} 卖{ss}")
    print(f"  🎨 风格: {', '.join(styles)}")
    print(f"  🏷️  主题: {' | '.join(f'{t}({c})' for t,c in top_t[:4])}")
    top_s = sorted(sigs.items(), key=lambda x:-x[1]['count'])[:6]
    parts = [f'「{w}」×{v["count"]}' for w,v in top_s]
    print(f"  🔑 信号词: {' '.join(parts)}")
    print(f"  🔄 扩展: {'⚠️ ' + reasons[0] if need_ext else '✅ 饱和'}")

    shown = set()
    for p2 in posts:
        txt = p2['text'][:60].replace('\n',' ')
        if txt not in shown and len(shown) < 3:
            shown.add(txt)
            m = '🔴S' if any(w in p2['text'] for w in SIGNAL_WORDS_MAP) else '⚪'
            print(f"    {m} {txt}")

json.dump(profiles, open('/tmp/kol_profiles_phase0.json','w'), ensure_ascii=False, indent=2)
print(f"\n✅ → /tmp/kol_profiles_phase0.json")

print(f"\n{'='*55}")
print("📊 饱和度汇总")
print(f"{'='*55}")
for uid, p in profiles.items():
    emoji = '✅' if not p.get('needs_more') else '⚠️'
    print(f"  {emoji} {p['name']}: 密度{p['signal_density']:.0%} | {p.get('n',0)}条 | {p.get('reason','')}")
