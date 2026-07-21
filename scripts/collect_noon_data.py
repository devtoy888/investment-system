#!/usr/bin/env python3
"""
盘中速递 - 11:35 预采集脚本
边采集边写文件，避免超时丢失数据
"""
import sys, json, os
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import *
from datetime import date

today = date.today().isoformat()
SUMMARY_DIR = Path("/tmp/fund_data")
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

# 清理旧skip文件，避免非交易日残留阻塞今日推送
for skip_file in ['_noon_skip.txt', '_skip.txt', '_closing_skip.txt']:
    f = SUMMARY_DIR / skip_file
    if f.exists():
        f.unlink()

print(f"📊 盘中速递预采集 — {today}")

if not is_trading_day():
    msg = f"{today} 不是交易日，跳过"
    print(msg)
    (SUMMARY_DIR / "_noon_skip.txt").write_text(msg)
    sys.exit(0)

raw_data = {'date': today, 'type': 'noon_brief', 'collected_at': datetime.now().isoformat()}

# ── 1. A股实时行情 ──
print("\n📈 上午A股行情:")
quotes = get_all_quotes()
market_lines = []
for name, q in quotes.items():
    if q:
        market_lines.append(f"{name}|{q['price']}|{q['change_pct']}%")
(SUMMARY_DIR / "_noon_market.txt").write_text("\n".join(market_lines))
raw_data['quotes'] = {k: v for k, v in quotes.items() if v}

# ── 2.5 行业板块上午涨跌（轻量，先于基金采集）──
print("\n📊 行业板块上午涨跌:")
sectors = get_sector_quotes()
sector_lines = []
for name, q in sorted(sectors.items(), key=lambda x: -(x[1]['change_pct'] if x[1] else 0)):
    if q:
        emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
        sector_lines.append(f"{emoji} {name}: {q['open']}→{q['price']} ({q['change_pct']:+.2f}%)")
    else:
        sector_lines.append(f"❌ {name}: 暂无数据")
(SUMMARY_DIR / "_noon_sector.txt").write_text("\n".join(sector_lines))
raw_data['sectors'] = {k: v for k, v in sectors.items() if v}

# ── 2.6 上午市场总览（轻量）──
print("\n📊 上午市场总览:")
overview = get_market_overview()
overview_lines = []
if overview.get('rise_count') is not None:
    from fund_tools import get_short_term_sentiment
    overview_lines.append(get_short_term_sentiment(overview))
if overview.get('total_turnover', 0) > 0:
    overview_lines.append(f"💰 两市成交: {overview['total_turnover']/1e8:.0f}亿 (沪{overview['sh_turnover']/1e8:.0f}亿 深{overview['sz_turnover']/1e8:.0f}亿)")
if overview_lines:
    (SUMMARY_DIR / "_noon_overview.txt").write_text("\n".join(overview_lines))
raw_data['market_overview'] = overview

# ── 2.8 量价分析（上午半日）──
try:
    from fund_tools import get_volume_analysis
    # 昨晚收盘总成交额作为对比基准（从收盘快照）
    prev_turnover = None
    snap_path = SUMMARY_DIR / "_yesterday_snapshot.json"
    if snap_path.exists():
        old_snap = json.loads(snap_path.read_text())
        old_ov = old_snap.get('market_overview', {})
        if old_ov.get('total_turnover', 0) > 0:
            prev_turnover = old_ov['total_turnover'] / 1e8
    va = get_volume_analysis(quotes, sectors, prev_total_turnover=prev_turnover)
    volume_lines = []
    if va.get('volume_signals'):
        volume_lines.append("📊 量价分析（盘中午盘）：")
        volume_lines.append("| 品种 | 涨跌 | 振幅 | 量价信号 |")
        volume_lines.append("|:---|:----:|:----:|:--------:|")
        for s in va['volume_signals'][:10]:
            if s['amplitude'] < 0.1:
                continue
            emoji_ch = '🔴' if s['change_pct'] > 0 else '🟢' if s['change_pct'] < 0 else '🟡'
            volume_lines.append(f"| {s['name']} | {emoji_ch} {s['change_pct']:+.2f}% | {s['amplitude']:.1f}% | {s['emoji']} {s['signal']} |")
        volume_lines.append(f"| 总体 | | | {va['total_signal']} |")
    (SUMMARY_DIR / "_noon_volume.txt").write_text("\n".join(volume_lines))
    print(f"  ✅ 量价分析已写入 _noon_volume.txt ({len(volume_lines)}行)")
except Exception as e:
    print(f"  ⚠️ 量价分析失败: {e}")
    (SUMMARY_DIR / "_noon_volume.txt").write_text("")

# ── 2.7 盘中北向资金（轻量）──
print("\n🌊 盘中北向资金:")
northbound = get_northbound_flow()
nb_lines = []
if northbound.get('total') is not None:
    emoji = '🔴' if northbound['total'] > 0 else '🟢' if northbound['total'] < 0 else '🟡'
    nb_lines.append(f"{emoji} 北向资金: 沪{northbound['hgt']:+.2f}亿 深{northbound['sgt']:+.2f}亿 合计{northbound['total']:+.2f}亿")
    (SUMMARY_DIR / "_noon_northbound.txt").write_text("\n".join(nb_lines))
raw_data['northbound'] = northbound

# ── 3. 基金盘中估算（耗时最长，放后面）──
print("\n💰 基金盘中估算:")
funds = get_all_funds()
fund_lines = []
for code, name in FUND_CODES.items():
    v = funds.get(code)
    if v:
        ec = v.get('estimated_change', 'N/A')
        fund_lines.append(f"{name}|{v['nav']}|{ec}%")
(SUMMARY_DIR / "_noon_fund.txt").write_text("\n".join(fund_lines))
raw_data['funds'] = {k: v for k, v in funds.items() if v}

# 分组
fund_groups = group_funds(funds)
group_lines = []
for gname, gdata in fund_groups.items():
    ac = gdata['avg_change']
    emoji = '🔴' if ac > 0 else '🟢' if ac < 0 else '🟡'
    group_lines.append(f"{emoji} {gname}: {ac}% ({gdata['count']}支)")
(SUMMARY_DIR / "_noon_group.txt").write_text("\n".join(group_lines))
raw_data['fund_groups'] = fund_groups

print("\n✅ 行情数据已写入")

# ── 4. 博主盘中博文 ──
print("\n📰 博主最新博文:")
noon_kols = {'2014433131': '唐史主任司马迁', '6114912545': '小浣熊1230'}
kol_data = {}
for uid, name in noon_kols.items():
    print(f"  采集 {name}({uid})...")
    posts = get_user_weibos(uid, count=15)
    kol_data[uid] = {'name': name, 'posts': posts}
    for p in posts:
        interpretation = interpret_weibo(p['text'], name)
        p['interpretation'] = interpretation
    print(f"    → 获取 {len(posts)} 条")
    # 每采完一个写KOL文件
    kol_lines = []
    for uid2, kd2 in kol_data.items():
        n2 = kd2['name']
        ps2 = kd2['posts']
        kol_lines.append(f"─── {n2} ───")
        if ps2:
            kol_lines.append(f"最新 {len(ps2)} 条:")
            for p in ps2:
                tp = p['text'][:120].replace('\n', ' ')
                kol_lines.append(f"  📝 {tp}")
                if p.get('interpretation'):
                    kol_lines.append(f"  {p['interpretation']}")
                kol_lines.append(f"  🔄{p['reposts_count']} 💬{p['comments_count']} ❤️{p['attitudes_count']}")
                kol_lines.append("")
        else:
            kol_lines.append("  (无最新微博或获取失败)")
        kol_lines.append("")
    (SUMMARY_DIR / "_noon_kol.txt").write_text("\n".join(kol_lines))
    time.sleep(2)

raw_data['kol_posts'] = {uid: {'name': kd['name'], 'posts': kd['posts']} for uid, kd in kol_data.items()}

# ── 4. 保存 + 归档 ──
(SUMMARY_DIR / "_noon_raw.json").write_text(json.dumps(raw_data, ensure_ascii=False, indent=2))
store_jsonl(raw_data, 'noon-briefs.jsonl')

# ── 5. 数据合理性校验 (维度A) ──
sanity = run_sanity_checks(raw_data)
(SUMMARY_DIR / "_noon_sanity.json").write_text(json.dumps(sanity, ensure_ascii=False, indent=2))
if sanity['warnings']:
    print(f"⚠️ 数据异常 {len(sanity['warnings'])} 处:")
    for w in sanity['warnings']:
        print(f"  {w}")

# ── 6. 信号归因提取 (维度B) ──
signals = extract_signals_from_kols(raw_data.get('kol_posts', {}), 'noon_brief', raw_data.get('quotes', {}))
if signals:
    store_signals(signals)
    print(f"📊 提取 {len(signals)} 条信号")

# ── 7. 解析历史信号 ──
resolved = resolve_past_signals(quotes=raw_data.get('quotes', {}))
if resolved:
    print(f"📋 解析 {len(resolved)} 条历史信号")

# ── 8. RSS赛道资讯 ──
try:
    from fund_tools import fetch_rss_news, format_rss_news
    rss_news = fetch_rss_news(max_per_source=3, timeout=10)
    if rss_news:
        rss_text = format_rss_news(rss_news)
    else:
        rss_text = ""
    (SUMMARY_DIR / "_noon_rss.txt").write_text(rss_text)
    if rss_text.strip():
        print(f"   ✅ RSS 新闻已写入 _noon_rss.txt")
    else:
        print(f"   ⚠️ RSS 新闻为空")
except Exception as e:
    (SUMMARY_DIR / "_noon_rss.txt").write_text("")
    print(f"   ⚠️ RSS 采集失败: {e}")

print(f"\\n✅ 盘中速递预采集完成!")
for f in sorted(SUMMARY_DIR.iterdir()):
    if f.name.startswith('_noon'):
        print(f"   {f.name} ({f.stat().st_size} bytes)")
