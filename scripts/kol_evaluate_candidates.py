#!/usr/bin/env python3
"""Quick evaluate candidate KOLs - pull 20 posts each, analyze content quality"""
import sys, json, time, re, requests
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import CREDENTIAL_FILE

cred = json.loads(CREDENTIAL_FILE.read_text())
cookies = cred.get('cookies', {})
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://weibo.com/",
    "X-Requested-With": "XMLHttpRequest",
}

CANDIDATES = {
    '2144596567': {'name':'洪榕','desc':'洪攻略极端交易创始人'},
    '1483330984': {'name':'侯宁','desc':'空军司令'},
    '1905549057': {'name':'扬韬','desc':'职业投资者孙成刚'},
    '5828706619': {'name':'狂龙十八段','desc':'资金流派'},
    '7387500655': {'name':'陈果-投资策略','desc':'策略分析师'},
    '7670847417': {'name':'启哥有何妙计','desc':'半导体行业'},
    '3208538825': {'name':'奶员外','desc':'职业投资人'},
    '2861590343': {'name':'震东很耐心','desc':'成功投资人'},
    '1509681674': {'name':'梦想家林奇','desc':'私募'},
    '1714100821': {'name':'但国庆','desc':'私募董事长'},
}

# Signal words (same as used for Tang analysis)
SIGNAL_WORDS = {
    '买':'buy','卖':'sell','加仓':'buy','减仓':'sell','建仓':'buy',
    '清仓':'sell','持有':'hold','观望':'hold','定投':'hold',
    '机会':'buy','风险':'caution','泡沫':'caution','反弹':'hold','回调':'hold',
    '注意':'caution','谨慎':'caution',
}

THEME_KW = {
    '科技/半导体':['半导体','芯片','AI','算力','存储','光模块','英伟达'],
    '新能源':['新能源','光伏','锂电','电动车'],
    '宏观/政策':['美联储','加息','降息','CPI','利率','关税'],
    '消费/白酒':['白酒','消费'],
    '黄金':['黄金','金价'],
    '军工':['军工','国防'],
    'A股大盘':['A股','大盘','指数','上证','科创','创业板'],
    '交易策略':['仓位','策略','趋势','轮动','布局','左侧','右侧','网格'],
    '基金':['基金','ETF','组合','定投','净值'],
}

all_data = {}

for uid, info in CANDIDATES.items():
    name = info['name']
    print(f"\n{'='*60}")
    print(f"📥 采集: {name} ({uid})")
    print(f"{'='*60}")
    
    try:
        r = requests.get(
            "https://weibo.com/ajax/statuses/mymblog",
            params={"uid": uid, "page": "1", "feature": "0"},
            cookies=cookies, headers=headers, timeout=15
        )
        data = r.json()
        if data.get("ok") != 1:
            print(f"  ❌ API失败: ok={data.get('ok')}")
            all_data[uid] = {'name':name,'posts':[],'error':f'ok={data.get("ok")}'}
            time.sleep(3)
            continue
        
        items = data.get("data", {}).get("list", [])
        posts = []
        for p in items[:20]:
            text = p.get("text_raw", p.get("text", ""))
            text = re.sub(r'<[^>]+>', '', text)
            posts.append({
                'id': p.get('id',''),
                'created_at': p.get('created_at',''),
                'text': text[:500],
                'reposts_count': p.get('reposts_count',0),
                'comments_count': p.get('comments_count',0),
                'attitudes_count': p.get('attitudes_count',0),
            })
        
        all_data[uid] = {'name':name,'posts':posts}
        n = len(posts)
        
        if n == 0:
            print(f"  ⚠️ 0条博文")
            time.sleep(3)
            continue
        
        # ── Analysis ──
        # Signal density
        sig_posts = [p for p in posts if any(w in p['text'] for w in SIGNAL_WORDS)]
        density = round(len(sig_posts)/n, 3)
        
        # Buy/sell ratio
        buy = sum(1 for p in posts if any(w in p['text'] for w in ['买','加仓','建仓','机会']))
        sell = sum(1 for p in posts if any(w in p['text'] for w in ['卖','减仓','清仓']))
        caution = sum(1 for p in posts if any(w in p['text'] for w in ['风险','泡沫','谨慎','注意']))
        
        # Themes
        themes = {}
        for theme, kws in THEME_KW.items():
            c = sum(1 for p in posts if any(kw in p['text'] for kw in kws))
            if c: themes[theme] = c
        top_t = sorted(themes.items(), key=lambda x:-x[1])[:4]
        
        # Text length (indicator of depth)
        avg_len = sum(len(p['text']) for p in posts) / max(1, n)
        
        # Interaction (avg)
        avg_interact = sum(p['reposts_count']+p['comments_count']+p['attitudes_count'] for p in posts) / max(1, n)
        
        # Content quality assessment
        has_deep = sum(1 for p in posts if len(p['text']) > 300)
        has_short = sum(1 for p in posts if len(p['text']) < 50)
        
        print(f"  📊 {n}条 | 信号密度: {density:.0%} | 买{buy}卖{sell}警{caution}")
        print(f"  📏 均长: {avg_len:.0f}字 | 深度文(>300字): {has_deep}条 | 短文(<50字): {has_short}条")
        print(f"  💬 平均互动: {avg_interact:.0f}")
        print(f"  🏷️  主题: {' | '.join(f'{t}({c})' for t,c in top_t[:4])}")
        
        # Show first 3 posts
        print(f"  📰 最近博文:")
        for i, p in enumerate(posts[:3]):
            txt = p['text'][:80].replace('\n',' ')
            is_sig = any(w in p['text'] for w in SIGNAL_WORDS)
            m = '🔴SIG' if is_sig else '⚪'
            print(f"    {m} [{p['created_at'][:10]}] {txt}")
        
        # Quality grade
        grade = 'C'
        if density > 0.3 and avg_len > 100 and has_deep > 3:
            grade = 'A'
        elif density > 0.2 or avg_len > 150:
            grade = 'B'
        
        info['grade'] = grade
        info['density'] = density
        info['avg_len'] = round(avg_len)
        info['buy'] = buy
        info['sell'] = sell
        info['caution'] = caution
        info['themes'] = ' '.join(f'{t}({c})' for t,c in top_t[:3])
        info['has_deep'] = has_deep
        print(f"  📊 质量评级: {grade}")
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        all_data[uid] = {'name':name,'posts':[],'error':str(e)}
    
    time.sleep(3)

# Summary
print(f"\n\n{'='*70}")
print("📊 候选博主快速评估汇总")
print(f"{'='*70}")
print(f"{'博主':16s} {'等级':4s} {'密度':6s} {'均长':6s} {'信号分布':16s} {'主题(主要)'}")
print("-"*80)

grade_order = {'A':0, 'B':1, 'C':2}
sorted_cands = sorted(CANDIDATES.items(), key=lambda x: grade_order.get(x[1].get('grade','C'), 99))

for uid, info in sorted_cands:
    g = info.get('grade','?')
    d = f"{info.get('density',0):.0%}" if 'density' in info else '?'
    al = f"{info.get('avg_len','?'):>4}" if 'avg_len' in info else '   ?'
    bs = f"买{info.get('buy',0)}/卖{info.get('sell',0)}/警{info.get('caution',0)}"
    th = info.get('themes','?')
    emoji = {'A':'🟢','B':'🟡','C':'🔴'}.get(g,'⚪')
    print(f"{emoji} {info['name']:14s} {g:4s} {d:>5s} {al:>5s} {bs:16s} {th}")

# Save raw data
outpath = '/tmp/candidate_kols_raw.json'
json.dump(all_data, open(outpath,'w'), ensure_ascii=False, indent=2)
print(f"\n✅ 原始数据 -> {outpath}")
