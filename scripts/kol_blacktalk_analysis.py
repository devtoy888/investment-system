#!/usr/bin/env python3
"""Comprehensive 唐史主任黑话分析 + 可验证预言提取"""
import json, sys, re
from datetime import datetime, timezone

data = json.loads(open('/tmp/kol_tang_extra.json').read())
posts = data['2014433131']['posts']
print(f"📚 唐史主任司马迁: {len(posts)}条博文分析")
print(f"{'='*70}")

# ─── 1. 全部信号词/黑话统计 ───
SIGNAL_WORDS = {
    '建仓':'buy-买入', '加仓':'buy-买入', '吸筹':'buy-买入', '吸点':'buy-买入',
    '买入':'buy-买入', '补':'buy-加仓', '加':'buy-加仓', '触底':'buy-到底了',
    '右侧':'buy-趋势确认', '确定性':'buy-确定性机会',
    '减仓':'sell-卖出', '出货':'sell-卖出', '减':'sell-卖出',
    '调出':'sell-卖出', '止盈':'sell-卖出',
    '洗盘':'hold-洗盘', '震荡':'hold-震荡', '观望':'hold-观望',
    '泡沫':'caution-预警', '风险':'caution-预警', '谨慎':'caution-预警',
    '地板':'buy-底部', '天花板':'sell-顶部', '半山腰':'hold-半路',
    '右侧':'buy-趋势确认', '左侧':'buy-抄底区间',
    '村里':'signal-政策层', '上面':'signal-监管层', '大家伙':'signal-国家队',
    '聪明钱':'signal-北向资金', '老乡':'signal-散户',
    '格局':'signal-趋势判断', '风向':'signal-政策导向',
    '吃肉':'buy-有行情', '喝汤':'hold-小涨', '埋单':'caution-被套',
    '抬轿':'caution-追高', '砸盘':'sell-大资金卖出',
    '护盘':'hold-托市', '建仓':'buy-建仓', '洗盘':'hold-洗盘',
    '拉高出货':'sell-拉高卖出', '高低切':'signal-板块轮动',
    '高低切换':'signal-板块轮动',
}

# Extended: unique terms observed in Tang's posts
UNIQUE_TERMS = {
    '玻璃基': '康宁GlassBridge光学桥接技术/AI数据中心互连',
    '玻璃光学桥': 'Corning GlassBridge, 光通信/AI集群光学互连',
    '村龙': '长鑫存储(CXMT) = 国产DRAM龙头',
    '长鑫': '长鑫存储(CXMT), 国产DRAM存储器龙头',
    '伴娘': '供应链companion/配套厂商, "长鑫伴娘"=长鑫的配套供应商',
    '大fab': '大型晶圆代工厂(台积电/中芯等)',
    '小fab': '小型晶圆厂/特色工艺厂',
    '硅基通胀': 'AI算力需求导致硅基芯片/服务器价格全面上涨',
    '硅基': '硅基芯片/半导体产业',
    '存': '存储芯片(主要指DRAM/HBM)',
    '这条线': '某个产业链/投资主线',
    '光的部分': '光通信/光模块产业链',
    '功率': '功率半导体(IGBT/SiC等)',
    '实调': '实地调研/产业调研',
    '确定性的': '有明确逻辑支撑的投资方向',
    '弹性': '高波动性/高beta的品种',
    '核心': '核心持仓/核心方向',
    '补涨': '滞涨股的补涨行情',
    '冲高回落': '技术面短期见顶信号',
    '季末漂移': '基金季末调仓导致的板块异动',
    '季末+月末': '季末和月末叠加的资金面压力',
    '场外资金': '增量资金入场',
    '宽基': '宽基指数ETF(沪深300/中证500等)',
    '低位ETF': '处于低位的ETF品种',
    '降息周期': '美联储降息周期',
    '输入性影响': '外部市场波动对A股的传导',
    '杠杆': '杠杆资金/融资盘风险',
    '流动性': '市场流动性/资金面',
    '拥挤度': '板块交易拥挤度/资金集中度',
    '白线': '大盘权重股指数线',
    '黄线': '中小盘股指数线',
    '沉没成本': '套牢后不愿止损的心态',
    '零和博弈': 'A股结构性特征(部分资金互为对手盘)',
    '主升浪': '主要上升行情',
}

# ── 1.1 统计信号词出现频率 ──
print("\n📊 信号词频率统计")
print("-"*70)
word_stats = {}
for w in SIGNAL_WORDS:
    c = sum(1 for p in posts if w in p['text'])
    if c: word_stats[w] = c

sorted_words = sorted(word_stats.items(), key=lambda x:-x[1])
print(f"{'信号词':12s} {'次数':6s} {'含义'}")
print("-"*50)
for w, c in sorted_words[:25]:
    meaning = SIGNAL_WORDS[w].split('-')[1] if '-' in SIGNAL_WORDS[w] else SIGNAL_WORDS[w]
    cat = SIGNAL_WORDS[w].split('-')[0] if '-' in SIGNAL_WORDS[w] else '?'
    emoji = {'buy':'🟢','sell':'🔴','hold':'🟡','signal':'🔵','caution':'⚠️'}.get(cat,'⚪')
    print(f"  {emoji} {w:10s} {c:3d}次 → {meaning}")

# ── 1.2 独特术语分析 ──
print(f"\n\n📖 独特黑话术语解读")
print("-"*70)
for term, meaning in sorted(UNIQUE_TERMS.items()):
    c = sum(1 for p in posts if term in p['text'])
    if c:
        # Find an example post containing this term
        example = ''
        for p in posts:
            if term in p['text']:
                example = p['text'][:150].replace('\n',' ')
                break
        print(f"\n  {term}")
        print(f"    出现: {c}次")
        print(f"    含义: {meaning}")
        print(f"    示例: \"{example}\"")

# ── 2. 提取可验证的预言/判断 ──
print(f"\n\n{'='*70}")
print("🔍 可验证的预言/判断提取")
print(f"{'='*70}")

# Look for posts containing verifiable claims
VERIFIABLE_PATTERNS = [
    ('美光', '美光科技业绩/股价'),
    ('存储', '存储芯片走势'),
    ('成交', '成交量预判'),
    ('指数', '指数点位判断'),
    ('净值', '净值/仓位判断'),
    ('新高', '创新高判断'),
    ('触底', '触底判断'),
    ('建仓', '建仓时机判断'),
    ('融资', '融资/杠杆判断'),
]

# Find posts with verifiable claims
verified_candidates = []
for i, p in enumerate(posts):
    text = p['text']
    patterns_found = [(pat,desc) for pat,desc in VERIFIABLE_PATTERNS if pat in text]
    if patterns_found and len(text) > 30:
        verified_candidates.append({
            'index': i,
            'date': p['created_at'],
            'text': text[:200].replace('\n',' '),
            'patterns': [d for p,d in patterns_found],
        })

print(f"\n找到 {len(verified_candidates)} 条有可验证内容的博文")
print()

# Show the most verifiable ones (sorted by date - oldest first)
verified_candidates.sort(key=lambda x: x['date'])

# Show by category
print("📌 【存储芯片相关判断】")
for v in verified_candidates:
    if any(p in str(v['patterns']) for p in ['存储','美光']):
        print(f"  [{v['date'][:16]}] {v['text']}")
        print()

print("📌 【指数/大势判断】")
for v in verified_candidates:
    if any(p in str(v['patterns']) for p in ['指数','新高','触底','成交']):
        print(f"  [{v['date'][:16]}] {v['text']}")
        print()

# ── 3. 按时间线整理主要观点 ──
print(f"\n\n{'='*70}")
print("📜 主要判断时间线")
print(f"{'='*70}")

# Sort posts chronologically
sorted_posts = sorted(posts, key=lambda x: x['created_at'])

# Extract and categorize key posts
key_posts = []
for p in sorted_posts:
    text = p['text']
    # Score for "signal-like" content
    score = 0
    signal_found = []
    for w in ['趋势','判断','方向','看','认为','肯定','一定','要涨','要跌','会涨','会跌','应该','建议','操作','加仓','补仓','减仓','清仓','仓位','布局','买入','卖出']:
        if w in text:
            score += 1
            signal_found.append(w)
    
    if score >= 2 and len(text) > 40:
        key_posts.append({
            'date': p['created_at'],
            'text': text[:200].replace('\n',' '),
            'signals': signal_found[:5],
        })

# Show most recent key posts first
key_posts.sort(key=lambda x: x['date'], reverse=True)
print(f"\n近期主要判断 ({len(key_posts)}条):")
print()
for kp in key_posts[:15]:
    signals_str = ','.join(set(kp['signals']))
    print(f"  📅 [{kp['date'][:16]}]")
    print(f"     📝 {kp['text']}")
    print(f"     🔑 {signals_str}")
    print()

# ── 4. 综合评估 ──
print(f"\n{'='*70}")
print("📋 综合统计")
print(f"{'='*70}")
print(f"总博文数: {len(posts)}")
print(f"信号词总数: {sum(word_stats.values())}")
print(f"不同信号词: {len(word_stats)}种")
print(f"独特术语: {len([t for t in UNIQUE_TERMS if sum(1 for p in posts if t in p['text'])])}种出现")
print(f"可验证预言: {len(verified_candidates)}条")
print(f"关键判断: {len(key_posts)}条")

# Save all extracted data
output = {
    'n_posts': len(posts),
    'word_stats': word_stats,
    'unique_terms': {t:{'meaning':m,'count':sum(1 for p in posts if t in p['text'])} for t,m in sorted(UNIQUE_TERMS.items()) if sum(1 for p in posts if t in p['text'])},
    'verified_candidates': verified_candidates,
    'key_posts': key_posts,
    'date_range': {'start': sorted_posts[0]['created_at'][:10] if sorted_posts else '','end': sorted_posts[-1]['created_at'][:10] if sorted_posts else ''},
}
json.dump(output, open('/tmp/kol_blacktalk_analysis.json','w'), ensure_ascii=False, indent=2)
print(f"\n✅ 分析结果 -> /tmp/kol_blacktalk_analysis.json")
