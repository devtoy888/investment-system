#!/usr/bin/env python3
"""
今日参考(盘前版) - 预采集脚本
边采集边写文件，避免超时丢失数据
"""
import sys, json, os, math
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import *
from datetime import date

today = date.today().isoformat()
SUMMARY_DIR = Path("/tmp/fund_data")
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

# 清理旧skip文件，避免非交易日残留阻塞今日推送
for skip_file in ['_skip.txt', '_closing_skip.txt']:
    f = SUMMARY_DIR / skip_file
    if f.exists():
        f.unlink()
        
print(f"📊 今日参考预采集 — {today}")

if not is_trading_day():
    msg = f"{today} 不是交易日，跳过"
    print(msg)
    (SUMMARY_DIR / "_skip.txt").write_text(msg)
    sys.exit(0)

raw_data = {'date': today, 'type': 'morning_brief', 'collected_at': datetime.now().isoformat()}

# ── 1. 隔夜外盘（先写文件）──
print("\n🌙 外盘采集:")
overnight = get_overnight_quotes()
overnight_lines = []
for name, q in overnight.items():
    if q:
        overnight_lines.append(f"{name}|{q['price']}|{q['change_pct']:+.2f}%")
(SUMMARY_DIR / "_overnight_summary.txt").write_text("\n".join(overnight_lines))
raw_data['overnight'] = {k: v for k, v in overnight.items() if v}

# ── 2. A股行情（优先读昨日收盘快照）──
snapshot_path = SUMMARY_DIR / "_yesterday_snapshot.json"
use_snapshot = snapshot_path.exists()
quotes = {}
sectors = {}
overview = {}
northbound = {}
yesterday_data_source = ""

if use_snapshot:
    snap = json.loads(snapshot_path.read_text())
    quotes = snap.get('quotes', {})
    sectors = snap.get('sectors', {})
    overview = snap.get('market_overview', {})
    northbound = snap.get('northbound', {})
    print(f"  ✅ 从收盘快照读取 {len(quotes)} 条行情 + {len(sectors)} 个板块 ({snap.get('date','?')})")
    yesterday_data_source = f"收盘快照({snap.get('date','?')})"
else:
    print("  ⚠️ 无收盘快照，尝试从早报存档恢复昨日行情...")
    # 从 morning-briefs.jsonl 找最新的非今日数据
    archive_path = Path('/opt/data/fund_system_data/morning-briefs.jsonl')
    today_str = date.today().isoformat()
    if archive_path.exists():
        records = [json.loads(l) for l in archive_path.read_text().strip().split('\n') if l.strip()]
        # 从后往前找第一个日期不等于今天的
        for r in reversed(records):
            r_date = r.get('date', '')
            if r_date and r_date != today_str:
                # 检查是否有行情数据
                if r.get('quotes') or r.get('sectors'):
                    quotes = {k: v for k, v in r.get('quotes', {}).items() if v}
                    sectors = {k: v for k, v in r.get('sectors', {}).items() if v}
                    overview = r.get('market_overview', {})
                    northbound = r.get('northbound', {})
                    print(f"  ✅ 从存档恢复 {r_date} 行情: {len(quotes)} 条指数 + {len(sectors)} 个板块")
                    yesterday_data_source = f"存档数据({r_date})"
                    break
    if not quotes:
        print("  ⚠️ 快照和存档都不可用，直接从腾讯API获取...")
        quotes = get_all_quotes()
        sectors = get_sector_quotes()
        overview = get_market_overview()
        northbound = get_northbound_flow()
        # 判断是否在盘中交易时段（9:30-11:30, 13:00-15:00）
        now_hour = datetime.now().hour
        now_min = datetime.now().minute
        in_market = (now_hour == 9 and now_min >= 30) or (10 <= now_hour <= 10) or \
                    (now_hour == 11) or (13 <= now_hour <= 14)
        if in_market and quotes:
            print("  ⚠️ 盘中时段！用prev_close替代当前价作为昨日收盘")
            for name, q in quotes.items():
                if q and q.get('prev_close'):
                    q['price'] = q['prev_close']  # 昨收=正确收盘价
                    q['change_pct'] = '0.00'       # 涨跌幅暂缺
            for name, q in sectors.items():
                if q and q.get('prev_close'):
                    q['price'] = q['prev_close']
                    q['change_pct'] = 0.0
            yesterday_data_source = "腾讯API prev_close(昨收价✓,涨跌幅暂缺)"
        else:
            yesterday_data_source = "实时API(非盘中时段,数据可信)"
market_lines = []
for name, q in quotes.items():
    if q:
        market_lines.append(f"{name}|{q['price']}|{q['change_pct']}%")
(SUMMARY_DIR / "_market_summary.txt").write_text("\n".join(market_lines))
raw_data['quotes'] = {k: v for k, v in quotes.items() if v}

# ── 3.5 行业板块昨收 ──
if not sectors:
    if use_snapshot:
        sectors = snap.get('sectors', {})
        print(f"  ✅ 从收盘快照读取 {len(sectors)} 个板块")
    else:
        print("  ⚠️ 无收盘快照，回退实时API")
        sectors = get_sector_quotes()
else:
    print(f"  ✅ 板块数据: {len(sectors)} 个（来自{yesterday_data_source}）")
sector_lines = []
for name, q in sorted(sectors.items(), key=lambda x: -(x[1]['change_pct'] if x[1] else 0)):
    if q:
        emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
        sector_lines.append(f"{emoji} {name}: {q['open']}→{q['price']} ({q['change_pct']:+.2f}%)")
    else:
        sector_lines.append(f"❌ {name}: 暂无数据")
(SUMMARY_DIR / "_sector_summary.txt").write_text("\n".join(sector_lines))
raw_data['sectors'] = {k: v for k, v in sectors.items() if v}

# ── 3.6 昨日市场总览 ──
if not overview:
    if use_snapshot:
        overview = snap.get('market_overview', {})
        print(f"  ✅ 从收盘快照读取市场总览")
    else:
        print("  ⚠️ 无收盘快照，回退实时API")
        overview = get_market_overview()
else:
    print(f"  ✅ 市场总览: 来自{yesterday_data_source}")
overview_lines = []
if overview.get('rise_count') is not None:
    from fund_tools import get_short_term_sentiment
    overview_lines.append(get_short_term_sentiment(overview))
if overview.get('total_turnover', 0) > 0:
    overview_lines.append(f"💰 两市成交: {overview['total_turnover']/1e8:.0f}亿 (沪{overview['sh_turnover']/1e8:.0f}亿 深{overview['sz_turnover']/1e8:.0f}亿)")
if overview_lines:
    (SUMMARY_DIR / "_market_overview_summary.txt").write_text("\n".join(overview_lines))
raw_data['market_overview'] = overview

# ── 3.7 昨日北向资金 ──
if not northbound:
    if use_snapshot:
        northbound = snap.get('northbound', {})
        print(f"  ✅ 从收盘快照读取北向资金")
    else:
        print("  ⚠️ 无收盘快照，回退实时API")
        northbound = get_northbound_flow()
else:
    nb_total = northbound.get('total')
    if nb_total is not None:
        print(f"  ✅ 北向资金: 合计{nb_total:+.2f}亿（来自{yesterday_data_source}）")
    else:
        print(f"  ✅ 北向数据: 来自{yesterday_data_source}")
nb_lines = []
if northbound.get('total') is not None:
    emoji = '🔴' if northbound['total'] > 0 else '🟢' if northbound['total'] < 0 else '🟡'
    nb_lines.append(f"{emoji} 北向资金: 沪{northbound['hgt']:+.2f}亿 深{northbound['sgt']:+.2f}亿 合计{northbound['total']:+.2f}亿")
    (SUMMARY_DIR / "_northbound_summary.txt").write_text("\n".join(nb_lines))
raw_data['northbound'] = northbound

# ── 4. 基金净值（优先读快照）──
funds = {}
prev_funds = {}  # 前日快照中的基金净值（用于计算实际涨跌幅）
if use_snapshot:
    funds = snap.get('funds', {})
    # 保存快照中的净值作为"前日净值"
    prev_funds = {k: {'nav': v.get('nav', '?')} for k, v in funds.items() if v}
    print(f"  ✅ 从收盘快照读取 {len(funds)} 支基金")
else:
    print("  ⚠️ 无收盘快照，回退实时API")
    funds = get_all_funds()

# ── 4.1 修正基金涨跌幅：用官方净值差替代收盘估算 ──
# 8:30 BJT 时官方净值已发布，用 (今日官方dwjz - 前日dwjz) 得到准确涨跌幅
corrected_count = 0
for code in list(funds.keys()):
    fd = funds.get(code)
    if not fd:
        continue
    # 如果快照显示nav_date非今日，尝试获取最新官方净值
    if not fd.get('stale') or fd.get('nav_date', '') >= today:
        continue  # 数据已经是最新的
    try:
        current = get_fund_value(code)
        if current and current.get('nav_date', '') > fd.get('nav_date', ''):
            # 官方净值已更新！计算实际涨跌幅
            old_nav = float(fd.get('nav', 0))
            new_nav = float(current['nav'])
            if old_nav > 0 and new_nav > 0 and abs(old_nav - new_nav) > 0.0001:
                actual_change = (new_nav - old_nav) / old_nav * 100
                funds[code]['nav'] = current['nav']  # 更新为最新官方净值
                funds[code]['estimated_change'] = f"{actual_change:.2f}"
                funds[code]['nav_date'] = current['nav_date']
                funds[code]['stale'] = False
                funds[code]['change_confirmed'] = True
                corrected_count += 1
                print(f"  ✅ 修正 {fd.get('name', code)}: {old_nav}→{new_nav} ({actual_change:+.2f}%)")
    except Exception as e:
        print(f"  ⚠️ 修正 {code}: {e}")

if corrected_count > 0:
    print(f"  ✅ 共修正 {corrected_count} 支基金的涨跌幅（官方净值替代收盘估算）")
fund_lines = []
for code, name in FUND_CODES.items():
    v = funds.get(code)
    if v:
        ec = v.get('estimated_change', 'N/A')
        fund_lines.append(f"{name}|{v['nav']}|{ec}%")
(SUMMARY_DIR / "_fund_summary.txt").write_text("\n".join(fund_lines))
raw_data['funds'] = {k: v for k, v in funds.items() if v}

# 分组（纯计算）
fund_groups = group_funds(funds)
group_lines = []
for gname, gdata in fund_groups.items():
    ac = gdata['avg_change']
    emoji = '🔴' if ac > 0 else '🟢' if ac < 0 else '🟡'
    group_lines.append(f"{emoji} {gname}: {ac}% ({gdata['count']}支)")
(SUMMARY_DIR / "_group_summary.txt").write_text("\n".join(group_lines))
raw_data['fund_groups'] = fund_groups

print("\n✅ 行情数据已写入摘要文件")

# ── 5. 博主微博 ──
print("\n📰 博主微博:")
kol_data = {}

# Weibo日期解析: "Sat Dec 28 20:44:17 +0800 2024"
def _is_today_post(post: dict) -> bool:
    try:
        d = datetime.strptime(post.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y').date()
        return d == date.today()
    except:
        return False

# 信号关键词：只在帖子包含这些词时才做深度解读
SIGNAL_TRIGGERS = ['加仓','减仓','清仓','抄底','反弹','底部','泡沫','风险',
                   'ICU','KTV','IPO','放量','缩量','格局','右侧','机会','警惕',
                   '止损','触底','泡沫','过热','扫货','建仓','离场','逃顶']

SECTOR_KEYWORDS = {
    '科技/AI': ['AI','人工智能','算力','芯片','半导体','大模型','机器人','数据','软件','算法','GPU','华为','英伟达','deepseek','智能体'],
    '黄金': ['黄金','金价','贵金属','有色','金矿','Au'],
    '资源/周期': ['资源','周期','铜','铝','锂','稀土','煤炭','钢铁','化工','有色','商品','大宗'],
    '新能源': ['新能源','光伏','锂电','电池','储能','新能源车','电车','太阳能','风电','氢能'],
    '医药': ['医药','医疗','创新药','CXO','医保','药'],
    '消费': ['消费','白酒','食品','家电','汽车','零售'],
    '市场整体': ['大盘','指数','行情','市场','A股','创业板','科创板','上证','趋势'],
}
DIRECTION_BULLISH = ['加仓','补仓','右侧','底部','触底','反弹','抄底','建仓','看多','看好','确定性','吃肉','弹性','格局','扫货','拿住','定投','不慌','机会']
DIRECTION_BEARISH = ['减仓','清仓','风险','警惕','回调','泡沫','过热','出货','砸盘','逃顶','止损','谨慎','离场','回避','空仓','别追','小心','等待','观望']

for uid, name in KOLS.items():
    print(f"  采集 {name}({uid})...")
    posts = get_user_weibos(uid, count=15)
    kol_data[uid] = {'name': name, 'posts': posts}

    for p in posts:
        # 赛道+方向分析（所有帖子均做，用于趋势判断）
        text_lower = p['text'].lower()
        detected_sectors = {}
        for sector, kws in SECTOR_KEYWORDS.items():
            matched = [kw for kw in kws if kw.lower() in text_lower]
            if matched:
                is_bullish = any(w in p['text'] for w in DIRECTION_BULLISH)
                is_bearish = any(w in p['text'] for w in DIRECTION_BEARISH)
                direction = 'bullish' if is_bullish else ('bearish' if is_bearish else 'neutral')
                detected_sectors[sector] = {'direction': direction, 'keywords': matched}
        p['sector_analysis'] = detected_sectors

        # 仅对今日信号帖做深度解读（黑话破译）+ 事实核查
        p['is_signal'] = any(kw in p['text'] for kw in SIGNAL_TRIGGERS) and _is_today_post(p)
        if p['is_signal']:
            try:
                interp_parts = []
                # 黑话破译
                interpretation = interpret_weibo(p['text'], name)
                if interpretation:
                    interp_parts.append(interpretation)
                # 事实核查：对照行情数据验证数值断言
                fc = fact_check_kol_claims(p['text'], quotes, sectors,
                                           locals().get('overview'), locals().get('northbound'))
                if fc:
                    interp_parts.append("📊 **事实核查**\n" + "\n".join(f"> {f}" for f in fc))
                if interp_parts:
                    p['interpretation'] = "\n\n".join(interp_parts)
            except Exception as e:
                print(f"  ⚠️ 信号处理异常: {e}")

    print(f"    → 获取 {len(posts)} 条")

    # 写KOL摘要文件（精简版：今日分析 + 近期趋势，无互动数）
    kol_lines = []
    for uid2, kd2 in kol_data.items():
        n2 = kd2['name']
        ps2 = kd2['posts']
        kol_lines.append(f"─── {n2} ───")
        if not ps2:
            kol_lines.append("  (无最新微博或获取失败)\n")
            continue

        # 按日期分类
        today_posts = [p for p in ps2 if _is_today_post(p)]
        recent_posts = [p for p in ps2 if not _is_today_post(p)]

        # 汇总：博主整体赛道情绪（基于所有帖子，看一致性）
        sector_counts = {}
        for p in ps2:
            for sector, info in p.get('sector_analysis', {}).items():
                if sector not in sector_counts:
                    sector_counts[sector] = {'bullish': 0, 'bearish': 0, 'neutral': 0}
                sector_counts[sector][info['direction']] += 1
        if sector_counts:
            kol_lines.append("📊 **赛道情绪汇总**")
            for sector, counts in sorted(sector_counts.items()):
                net = counts['bullish'] - counts['bearish']
                emoji = '🔴' if net > 0 else ('🟢' if net < 0 else '🟡')
                kol_lines.append(f"  {emoji} {sector}: 📈{counts['bullish']} 📉{counts['bearish']} (净{net:+d})")
            kol_lines.append("")

        # 今日重点分析
        if today_posts:
            kol_lines.append(f"📋 **今日观点 ({len(today_posts)}条)**")
            for p in today_posts:
                tp = p['text'][:200].replace('\n', ' ')
                kol_lines.append(f"  📝 {tp}")
                if p.get('is_signal') and p.get('interpretation'):
                    kol_lines.append(f"  {p['interpretation']}")
                # 赛道标签
                tags = []
                for sector, info in p.get('sector_analysis', {}).items():
                    dir_emoji = '📈' if info['direction'] == 'bullish' else ('📉' if info['direction'] == 'bearish' else '➖')
                    tags.append(f"{dir_emoji}{sector}")
                if tags:
                    kol_lines.append(f"  🏷️ {' '.join(tags)}")
                kol_lines.append("")

        # 近期趋势参考（精简，仅文本+赛道，不解读）
        if recent_posts:
            kol_lines.append(f"📈 **近期趋势参考 ({len(recent_posts)}条)**")
            for p in recent_posts[:5]:
                tp = p['text'][:120].replace('\n', ' ')
                kol_lines.append(f"  📝 {tp}")
                tags = []
                for sector, info in p.get('sector_analysis', {}).items():
                    dir_emoji = '📈' if info['direction'] == 'bullish' else ('📉' if info['direction'] == 'bearish' else '➖')
                    tags.append(f"{dir_emoji}{sector}")
                if tags:
                    kol_lines.append(f"  🏷️ {' '.join(tags)}")
                kol_lines.append("")
        kol_lines.append("")
    (SUMMARY_DIR / "_kol_summary.txt").write_text("\n".join(kol_lines))
    time.sleep(1)

# ── 4.5 评论补充分析（仅对今日信号博文，低权重）──
comment_insights = []
for uid, kd in kol_data.items():
    if uid == '2014433131':  # 仅唐史主任（粉丝多，评论质量高）
        for p in kd['posts']:
            if not p.get('is_signal') or not _is_today_post(p):
                continue
            # 检测到信号博文，拉取评论作参考
            print(f"\n💬 检测到信号博文，拉取评论区补充分析...")
            try:
                comments = get_weibo_comments(str(p['id']), count=15)
                if comments:
                    zr_replies = [c for c in comments if c['has_zr_reply']]
                    # 提取有价值的评论（有主任回复的，或讨论具体方向的）
                    insight_lines = []
                    if zr_replies:
                        insight_lines.append(f"💬 主任回复参考 ({len(zr_replies)}条):")
                        for zc in zr_replies[:3]:
                            insight_lines.append(f"  [{zc['user']}] {zc['text'][:120]}")
                    if insight_lines:
                        comment_insights.extend(insight_lines)
                else:
                    print("  (无评论数据)")
            except Exception as e:
                print(f"  ⚠️ 评论拉取异常: {e}")
            break  # 只处理第一条信号博文
    if comment_insights:
        break

if comment_insights:
    (SUMMARY_DIR / "_kol_comment_insights.txt").write_text("\n".join(comment_insights))
    raw_data['comment_analysis'] = comment_insights

raw_data['kol_posts'] = {uid: {'name': kd['name'], 'posts': kd['posts']} for uid, kd in kol_data.items()}

# ── 5.5 KOL深度分析 v2：事实核查+操作建议 + 当日/今日分筛 ──
kol_analysis_result = {}
try:
    from kol_analysis import analyze_from_kol_data, format_push
    
    analysis = analyze_from_kol_data(kol_data, quotes)
    kol_analysis_result = analysis
    
    # 写推送文本
    analysis_text = format_push(analysis)
    (SUMMARY_DIR / "_kol_consensus.txt").write_text(analysis_text)
    raw_data['kol_analysis'] = kol_analysis_result
    print(f"  ✅ KOL深度分析v2: {analysis['signal_count']}条信号, {analysis['action_count']}条操作建议")
    if analysis.get('actions'):
        print(f"    操作建议:")
        for a in analysis['actions']:
            funds_str = '、'.join(f"{f['code']}" for f in a['funds'][:3])
            print(f"      {a['action']} {a['sector']} → {funds_str}")
    
    # 事实核查结果
    verified = [s for s in analysis['signals'] if s.get('verification',{}).get('verified')]
    correct = sum(1 for s in verified if s['verification'].get('correct'))
    print(f"    事实核查: {len(verified)}条已验证, {correct}条正确")
    
except Exception as e:
    print(f"  ⚠️ KOL深度分析失败: {type(e).__name__}: {e}")
    # 回退：简单统计赛道提及频次
    consensus_lines = ["📊 **KOL 赛道热度**（回退模式）"]
    sector_freq = {}
    for uid, kd in kol_data.items():
        for p in kd.get('posts', []):
            for sector, kws in {'科技/AI':['AI','芯片','半导体'], '黄金':['黄金'], '市场':['大盘','市场']}.items():
                if any(kw.lower() in p.get('text','').lower() for kw in kws):
                    sector_freq[sector] = sector_freq.get(sector, 0) + 1
    for sector, freq in sorted(sector_freq.items(), key=lambda x: -x[1]):
        consensus_lines.append(f"  📊 {sector}: 提及{freq}次")
    if consensus_lines[1:]:
        (SUMMARY_DIR / "_kol_consensus.txt").write_text("\n".join(consensus_lines))
        raw_data['kol_consensus'] = consensus_lines
        print("  ⚠️ 已回退到简单热度统计")


# ── 5. 保存原始数据 + 归档 ──
(SUMMARY_DIR / "_raw_data.json").write_text(json.dumps(raw_data, ensure_ascii=False, indent=2))
store_jsonl(raw_data, 'morning-briefs.jsonl')

# ── 6. 数据合理性校验 (维度A) ──
sanity = run_sanity_checks(raw_data)
(SUMMARY_DIR / "_sanity_report.json").write_text(json.dumps(sanity, ensure_ascii=False, indent=2))
if sanity['warnings']:
    print(f"⚠️ 数据异常 {len(sanity['warnings'])} 处:")
    for w in sanity['warnings']:
        print(f"  {w}")

# ── 7. 信号归因提取 (维度B) ──
signals = extract_signals_from_kols(raw_data.get('kol_posts', {}), 'morning_brief', raw_data.get('quotes', {}))
if signals:
    store_signals(signals)
    print(f"📊 提取 {len(signals)} 条信号")

print(f"\\n✅ 预采集完成!")
for f in sorted(SUMMARY_DIR.iterdir()):
    print(f"   {f.name} ({f.stat().st_size} bytes)")

# ── 8. 生成预格式化推文（供AI直接输出）──
morning_push = []

# 星期
weekday_cn = ['周一','周二','周三','周四','周五','周六','周日'][date.today().weekday()]
is_monday = date.today().weekday() == 0
overnight_label = "🌙 上周五外盘关盘" if is_monday else "📊 **隔夜外盘**"
a_share_label = "📈 上周五A股收盘" if is_monday else "📈 **A股昨收**"
fund_label = "💰 **持仓基金（上周五行情参考）**" if is_monday else "💰 **持仓基金（昨日行情参考）**"

morning_push.append(f"**📊 财经早餐 · 基金参考 · {today}({weekday_cn})**")
morning_push.append("")

# 隔夜外盘表格
morning_push.append(overnight_label)
morning_push.append("| 指数 | 收盘 | 涨跌 |")
morning_push.append("|:----|:----:|:----:|")
for name, q in overnight.items():
    if q:
        emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
        morning_push.append(f"| {name} | {q['price']} | {emoji} {q['change_pct']:+.2f}% |")
morning_push.append("")

# A股昨收表格
morning_push.append(a_share_label)
morning_push.append("| 指数 | 点位 | 涨跌 |")
morning_push.append("|:----|:----:|:----:|")
for name, q in sorted(quotes.items(), key=lambda x: -abs(float(x[1]['change_pct'])) if x[1] else 0):
    if q:
        emoji = '🔴' if float(q['change_pct']) > 0 else '🟢' if float(q['change_pct']) < 0 else '🟡'
        morning_push.append(f"| {name} | {q['price']} | {emoji} {q['change_pct']}% |")
morning_push.append("")

# 两市成交 + 北向
summary_parts = []
if overview.get('total_turnover', 0) > 0:
    summary_parts.append(f"💰 两市成交 {overview['total_turnover']/1e8:.0f}亿")
if northbound.get('total') is not None:
    nb_emoji = '🔴' if northbound['total'] > 0 else '🟢' if northbound['total'] < 0 else '🟡'
    # 如果是从快照读取的数据（非今日），标注昨日
    nb_stale = '（昨日）' if northbound.get('stale') or (use_snapshot and not northbound.get('time', '').startswith('09')) else ''
    summary_parts.append(f"🌊 北向 {nb_emoji}{northbound['total']:+.2f}亿{nb_stale}")
if summary_parts:
    morning_push.append(" | ".join(summary_parts))
    morning_push.append("")

# 📊 量价分析（基于昨日收盘数据）——脚本自动生成
try:
    from fund_tools import get_volume_analysis
    prev_turnover = overview.get('total_turnover', 0) / 1e8 if overview.get('total_turnover', 0) > 0 else None
    va = get_volume_analysis(quotes, sectors, prev_total_turnover=prev_turnover)
    if va.get('volume_signals'):
        morning_push.append("📊 **量价分析（昨日）**")
        morning_push.append("| 品种 | 涨跌 | 振幅 | 量价信号 |")
        morning_push.append("|:---|:----:|:----:|:--------:|")
        for s in va['volume_signals']:
            if s['amplitude'] < 0.1:  # 无振幅数据（如旧快照中板块），跳过
                continue
            emoji_ch = '🔴' if s['change_pct'] > 0 else '🟢' if s['change_pct'] < 0 else '🟡'
            morning_push.append(f"| {s['name']} | {emoji_ch} {s['change_pct']:+.2f}% | {s['amplitude']:.1f}% | {s['emoji']} {s['signal']} |")
        morning_push.append(f"| **总量总览** | | | {va['total_signal']} |")
        morning_push.append("")
except Exception as e:
    print(f"  ⚠️ 量价分析失败: {e}")

# 行业板块表格
sector_items = sorted(sectors.items(), key=lambda x: -(x[1]['change_pct'] if x[1] else 0))
if sector_items:
    morning_push.append("🔥 **板块热度**")
    morning_push.append("| 板块 | 今开→收盘 | 涨跌 |")
    morning_push.append("|:---|:--------:|:----:|")
    for name, q in sector_items:
        if q:
            emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
            open_v = q.get('open', '?')
            close_v = q.get('price', '?')
            morning_push.append(f"| {name} | {open_v}→{close_v} | {emoji} {q['change_pct']:+.2f}% |")
    morning_push.append("")

# 持仓基金分组表格（精简版：前日净值+昨日涨跌）
morning_push.append(fund_label)
fund_groups_m = group_funds(funds)
for gname in ['黄金', '科技/AI', '资源/周期', '新能源', '医药']:
    gdata = fund_groups_m.get(gname)
    if not gdata or gdata['count'] == 0:
        continue
    morning_push.append(f"**【{gname}】**")
    morning_push.append("| 基金 | 前日净值 | 昨日涨跌 |")
    morning_push.append("|:---|:-------:|:--------:|")
    for f in gdata['funds']:
        fname = f.get('name', '?')
        nav = f.get('nav', '-')
        ec = f.get('estimated_change', '?')
        try:
            ec_f = float(ec)
            if math.isnan(ec_f) or math.isinf(ec_f):
                morning_push.append(f"| {fname} | {nav} | - |")
            else:
                emoji = '📈' if ec_f > 0 else '📉' if ec_f < 0 else '➖'
                morning_push.append(f"| {fname} | {nav} | {emoji}{ec_f:+.2f}% |")
        except (ValueError, TypeError):
            morning_push.append(f"| {fname} | {nav} | - |")
    morning_push.append("")

# ── 保存预格式化推文到中间文件（供wrapper读取 → QQ Bot投递）──
if morning_push:
    (SUMMARY_DIR / "_morning_tables.md").write_text("\n".join(morning_push))
    print(f"   ✅ 预格式化推文已写入 _morning_tables.md ({len(morning_push)}行)")
else:
    print("  ❌ 推送文本为空")

# ── 8.5 赛道 RSS 新闻采集 ──
print("\n📡 赛道新闻采集:")
try:
    from fund_tools import fetch_rss_news, format_rss_news
    rss_news = fetch_rss_news(max_per_source=3, timeout=10)
    if rss_news:
        rss_text = format_rss_news(rss_news)
        (SUMMARY_DIR / "_rss_news.txt").write_text(rss_text)
        print(f"   ✅ RSS 新闻已写入 _rss_news.txt")
    else:
        (SUMMARY_DIR / "_rss_news.txt").write_text("")
        print("   ⚠️ RSS 新闻为空")
except Exception as e:
    print(f"   ⚠️ RSS 采集异常: {e}")
    (SUMMARY_DIR / "_rss_news.txt").write_text("")

# ── 9. 操作参考（再平衡检查 + 组别方向）──
print("\n📋 操作参考:")
# 9a. 再平衡检查
rebalance_advice = check_rebalance(funds)
if rebalance_advice:
    print(f"  ✅ 再平衡检查: {len(rebalance_advice)} 条建议")
else:
    print("  ✅ 再平衡检查: 各组占比在目标范围内")
# 9b. 从KOL信号提取作为 score_group_action 输入
kol_signal_list = []
for uid, kd in kol_data.items():
    for p in kd.get('posts', []):
        if p.get('interpretation'):
            kol_signal_list.append({
                'kol_name': kd['name'],
                'text_snippet': p['text'][:120],
                'predicted_direction': 'bullish' if any(w in p['text'] for w in ['右侧','加仓','补仓','反弹','建仓']) else
                                       'bearish' if any(w in p['text'] for w in ['泡沫','风险','过热','警惕','回调']) else 'neutral',
            })
# 注：开盘前用近3日趋势数据
group_scores = {}
for gname in ['黄金', '科技/AI', '资源/周期', '新能源', '医药']:
    trend = get_group_trend(gname, days=3)
    s = score_group_action(gname, quotes, {}, kol_signal_list, trend)
    group_scores[gname] = s
    emoji = '🟢' if s['score'] >= 1 else ('🔴' if s['score'] <= -1 else '🟡')
    print(f"  {emoji} {gname}: {s['action']} (得分{s['score']})")

# 写操作参考文件（供AI prompt读取）
action_lines = []
action_lines.append("📋 **今日操作参考**")
action_lines.append("| 组别 | 方向 | 建议 | 理由 |")
action_lines.append("|:----|:----:|:----|:-----|")
group_order = ['科技/AI', '黄金', '资源/周期', '新能源']
for gname in group_order:
    s = group_scores.get(gname, {})
    emoji = '🟢' if s.get('score', 0) >= 1 else ('🔴' if s.get('score', 0) <= -1 else '🟡')
    reasons = '；'.join(s.get('reasons', [])) or '无明显信号'
    action_lines.append(f"| {gname} | {emoji} | {s.get('action', '持有')} | {reasons} |")

if rebalance_advice:
    action_lines.append("")
    for a in rebalance_advice:
        action_lines.append(f"⚠️ {a['suggestion']}")
else:
    action_lines.append("")
    action_lines.append("✅ 再平衡检查：各组占比均在目标范围内，无需调整")

(SUMMARY_DIR / "_operation_plan.txt").write_text("\n".join(action_lines))
print(f"   ✅ 操作参考已写入 _operation_plan.txt ({len(action_lines)}行)")
raw_data['operation_plan'] = group_scores
raw_data['rebalance_advice'] = rebalance_advice
