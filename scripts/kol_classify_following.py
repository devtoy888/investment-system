#!/usr/bin/env python3
"""Classify Tang's followings and find valuable KOLs"""
import json

data = json.loads(open('/tmp/tang_following.json').read())

# Categories
CATEGORIES = {
    '官方/媒体': [
        '中国新闻网', '新浪财经', '凤凰网国际', '商务微新闻', '平安中原',
        '中科院之声', '工信微报', '中国科普博览', '财联社APP', '新浪证券',
        '证券市场周刊', '微博', '微博会员', '小秘书', '专栏', 'VPlus',
        '微博视频', '新浪汽车', '新浪科技', '人民网', '新华网',
        '新浪仓石基金',
    ],
    '知名经济学家/评论员': [
        '李大霄', '胡锡进', '侯宁', '叶檀', '洪榕', '水皮', '吴晓波',
        '马光远', '但斌', '任泽平', '李迅雷',
    ],
    '军事/科技/其他兴趣': [
        '战甲装研菌', '河森堡', '华为中国', '路金波', '王冰汝',
        '营养师顾中一', '车永莉', '理记',
    ],
}

# Keywords to identify financial/investment KOLs
FINANCE_KW = ['投资', '股票', '基金', '财经', '金融', '交易', '策略', '券商', 'A股', '市场', 'ETF']

# Known financial KOLs list
KNOWN_FINANCE = {
    '李大霄': {'type': '股市评论', 'value': '中'},
    '侯宁': {'type': '股市评论(空军司令)', 'value': '中'},
    '叶檀': {'type': '财经评论(宏观)', 'value': '中'},
    '洪榕': {'type': '交易策略(洪攻略)', 'value': '高'},
    '胡锡进': {'type': '时政评论(非专业财经)', 'value': '低'},
    '新浪仓石基金': {'type': '基金销售官方', 'value': '低'},
    '财联社APP': {'type': '财经快讯', 'value': '高(资讯源)'},
    '新浪证券': {'type': '证券资讯官方', 'value': '中'},
    '证券市场周刊': {'type': '财经媒体', 'value': '中'},
}

# Classify all 98 people
classified = {'官方/媒体': [], '知名财经人': [], '可能值得关注': [], '其他': []}

for u in data:
    name = u['screen_name']
    desc = (u['description'] or '').lower()
    followers = u['followers_count']
    
    # Check if it's an official account
    is_official = False
    for kw in ['官方', 'app', '微博', 'vip', '会员', '小秘书', '专栏', 'vplus']:
        if kw in name.lower():
            is_official = True
            break
    
    # Check if financially relevant
    is_finance = False
    for kw in FINANCE_KW:
        if kw in desc or kw in name:
            is_finance = True
            break
    
    if name in KNOWN_FINANCE:
        classified['知名财经人'].append({
            'name': name, 'followers': followers,
            'type': KNOWN_FINANCE[name]['type'],
            'value': KNOWN_FINANCE[name]['value'],
        })
    elif is_official or any(o in name for o in ['新闻网', '证券', '财经', '新浪', '凤凰', '人民', '新华', '华为', '工信', '中科院']):
        classified['官方/媒体'].append({'name': name, 'followers': followers, 'desc': (u['description'] or '')[:50]})
    elif is_finance and followers > 10000:
        classified['可能值得关注'].append({'name': name, 'followers': followers, 'desc': (u['description'] or '')[:80]})
    else:
        classified['其他'].append({'name': name, 'followers': followers, 'desc': (u['description'] or '')[:50]})

# Print report
print("="*70)
print("唐史主任关注列表分类报告")
print("="*70)

print(f"\n🟢 知名财经人 ({len(classified['知名财经人'])}人):")
print("-"*50)
for p in classified['知名财经人']:
    print(f"  {p['name']:12s} | {p['type']:30s} | 价值评估: {p['value']} | 粉丝: {p['followers']/10000:.0f}万")

print(f"\n📰 官方/媒体 ({len(classified['官方/媒体'])}人):")
print("-"*50)
for p in classified['官方/媒体']:
    print(f"  {p['name']:16s} | {p['followers']/10000:.0f}万粉 | {p['desc'][:40]}")

if classified['可能值得关注']:
    print(f"\n🔍 可能值得关注的金融类个人博主 ({len(classified['可能值得关注'])}人):")
    print("-"*50)
    for p in sorted(classified['可能值得关注'], key=lambda x: -x['followers']):
        print(f"  {p['name']:16s} | {p['followers']/10000:.0f}万粉 | {p['desc'][:60]}")

print(f"\n⚪ 其他 ({len(classified['其他'])}人):")
print("-"*50)
for p in classified['其他']:
    print(f"  {p['name']:16s} | {p['followers']/10000:.0f}万粉 | {p['desc'][:50]}")

# ── 2. Deep analysis of the most valuable ones ──
print(f"\n\n{'='*70}")
print("🔍 深度分析：哪些值得进一步关注")
print("="*70)

valuable_candidates = [
    {
        'name': '洪榕',
        'followers': '356万',
        'why': '洪攻略极端交易创始人, 曾任大智慧执行总裁, 有完整交易方法论。和唐史主任风格互补(洪榕偏交易策略, 唐主任偏产业)', 
        'risk': '方法论可能太体系化, 需要投入时间理解',
        'recommendation': '🟢 推荐关注——可能是最有价值的财经KOL补充'
    },
    {
        'name': '侯宁',
        'followers': '424万',
        'why': '"空军司令", 长期看空派。与唐史主任(偏多)形成对立面, 可以帮他看空头逻辑是否存在依据',
        'risk': '空军司令可能有系统性看空偏见',
        'recommendation': '🟡 可以看看——帮你验证空头逻辑'
    },
    {
        'name': '李大霄',
        'followers': '640万',
        'why': '知名股市评论员, "做好人买好股得好报"',
        'risk': '长期喊底, 信号噪音较大, 已经被市场边缘化',
        'recommendation': '🔴 不推荐——信号价值低'
    },
    {
        'name': '叶檀',
        'followers': '383万',
        'why': '曾经的"财经女侠", 宏观视角',
        'risk': '已转型, 近期内容偏生活化而非投资, 信号密度可能不高',
        'recommendation': '🟡 可观察——宏观视角有补充价值但信号可能稀疏'
    },
    {
        'name': '财联社APP',
        'followers': '444万',
        'why': '机构和私募都在用的资讯APP, 实时财经快讯最全',
        'risk': '官方媒体, 无个人判断, 纯资讯',
        'recommendation': '🟢 推荐关注作为资讯源——比博主更快的消息'
    },
    {
        'name': '理记',
        'followers': '541万',
        'why': '硬核理性派, 唐史主任关注的非金融类中最有深度的人',
        'risk': '非财经博主, 内容不聚焦投资',
        'recommendation': '⚪ 不纳入投资信源, 纯兴趣'
    },
    {
        'name': '战甲装研菌',
        'followers': '751万',
        'why': '军事/军品资讯, 唐史主任是军事爱好者, 军工板块也是他关注的方向',
        'risk': '军事资讯, 非直接投资信号',
        'recommendation': '⚪ 可观察——军工板块有参考价值'
    },
]

for v in valuable_candidates:
    print(f"\n{'='*50}")
    print(f"{v['name']} ({v['followers']}粉)")
    print(f"{'='*50}")
    print(f"  为什么值得: {v['why']}")
    print(f"  风险: {v['risk']}")
    print(f"  建议: {v['recommendation']}")

# ── 3. Beyond top 30: check non-obvious ones ──
print(f"\n\n{'='*70}")
print("🔍 TOP30以外检查——可能隐藏的高质量小V")
print("="*70)

# Sort the "可能值得关注" and "其他" by description keywords
non_obvious = [u for u in data if u['followers_count'] < 500000]
non_obvious_finance = [u for u in non_obvious if any(kw in (u.get('description','') or '') for kw in FINANCE_KW)]

if non_obvious_finance:
    print(f"\n📊 粉丝<50万但描述含金融关键词的个人账号:")
    print("-"*70)
    for u in sorted(non_obvious_finance, key=lambda x: -x['followers_count']):
        print(f"  {u['screen_name']:16s} | {u['followers_count']/10000:.1f}万粉 | {(u.get('description','') or '')[:60]}")
else:
    print("  未发现显著的小V账号")

# Also check if there are interesting accounts we might have missed
all_names = [u['screen_name'] for u in data]
print(f"\n完整关注列表 ({len(data)}人):")
for i, u in enumerate(data):
    desc = (u.get('description','') or '')[:40].replace('\n',' ')
    print(f"  {i+1:3d}. {u['screen_name']:18s} | {u['followers_count']/10000:.1f}万 | {desc}")

json.dump(classified, open('/tmp/tang_following_classified.json','w'), ensure_ascii=False, indent=2)
print(f"\n✅ -> /tmp/tang_following_classified.json")
