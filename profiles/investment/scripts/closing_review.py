#!/usr/bin/env python3
"""
收盘复盘 - 收盘后验证今日参考的判断
对比早盘预测 vs 收盘实际，含开盘价
"""
import sys, json, os
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import *
from datetime import date, datetime

today = date.today().isoformat()
SUMMARY_DIR = Path("/tmp/fund_data")
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

# 清理旧skip文件，避免非交易日残留阻塞今日推送
for skip_file in ['_closing_skip.txt', '_skip.txt']:
    f = SUMMARY_DIR / skip_file
    if f.exists():
        f.unlink()
        print(f"  🧹 清理旧 {skip_file}")

print(f"📋 收盘复盘 — {today}")
print("=" * 50)

if not is_trading_day():
    msg = f"非交易日，跳过"
    print(msg)
    (SUMMARY_DIR / "_closing_skip.txt").write_text(msg)
    sys.exit(0)

# ── 1. 读取早盘数据 ──
raw_file = SUMMARY_DIR / "_raw_data.json"
morning_data = None
if raw_file.exists():
    morning_data = json.loads(raw_file.read_text())
    print("✅ 已读取早盘数据")
else:
    # 回退：从JSONL归档读取今日早盘数据
    morning_archive = DATA_DIR / "fund_system_data" / "morning-briefs.jsonl"
    if morning_archive.exists():
        for line in reversed(morning_archive.read_text().strip().split('\n')):
            try:
                record = json.loads(line)
                if record.get('_date') == today and record.get('type') == 'morning_brief':
                    morning_data = record
                    print(f"✅ 从归档读取早盘数据 ({today})")
                    break
            except json.JSONDecodeError:
                continue
    if morning_data is None:
        print("⚠️ 未找到早盘数据，跳过对比")

# ── 2. 采集收盘数据（含开盘价）──
print("\n📈 收盘行情:")
quotes_now = get_all_quotes()

print("\n💰 基金收盘估值:")
funds_now = get_all_funds()

# ── 2.1 基金数据交叉验证 ──
# fundgz API 在收盘后初期(15:00~16:00)可能返回不稳定估算值
# 用 ETF 市场价/指数变化验证基金 gszzl
print("  🔍 基金数据交叉验证（ETF市场价对照）:")
for code, fd in list(funds_now.items()):
    if fd is None:
        continue
    name = fd.get('name', '')
    gszzl = fd.get('estimated_change', '0')
    nav = fd.get('nav', '')
    enav = fd.get('estimated_nav', '')
    try:
        gszzl_f = float(gszzl) if gszzl else 0.0
        nav_f = float(nav) if nav else 0.0
        enav_f = float(enav) if enav else 0.0
        # 方法1: 用 gsz/dwjz 计算理论涨跌
        if nav_f > 0 and enav_f > 0:
            computed = (enav_f - nav_f) / nav_f * 100
            if abs(computed - gszzl_f) > 0.5:
                print(f"    ⚠️ {name}: fundgzgszzl={gszzl_f:+.2f}% ≠ 计算值({computed:+.2f}%) → 使用计算值")
                fd['estimated_change'] = f"{computed:.2f}"
                fd['change_source'] = 'computed_from_nav'
                gszzl_f = computed
    except (ValueError, TypeError):
        pass

# 方法2: ETF/标的指数验证
# 各基金跟踪的ETF代码和板块名称
fund_track_map = {
    '011613': ('科创50', 'quotes'),
    '011746': ('科创50', 'quotes'),
    '012800': ('科创50', 'quotes'),
    '016779': ('科创50', 'quotes'),
    '013356': ('科创50', 'quotes'),
    '013161': ('光伏', 'sectors'),
    '016553': ('新能源', 'sectors'),
    '013357': ('新能源', 'sectors'),
    '009478': ('黄金ETF市场价', 'quotes'),
}
for code, fd in list(funds_now.items()):
    if fd is None:
        continue
    name = fd.get('name', '')
    track_info = fund_track_map.get(code)
    if not track_info:
        continue
    track_name, track_type = track_info
    # 获取ETF/指数涨跌
    track_q = None
    if track_type == 'quotes':
        track_q = quotes_now.get(track_name)
    elif track_type == 'sectors':
        track_q = sectors_now.get(track_name)
    if track_q and track_q.get('change_pct') is not None:
        etf_chg = float(track_q['change_pct'])
        gszzl_f = float(fd.get('estimated_change', 0) or 0)
        diff = abs(gszzl_f - etf_chg)
        if diff > 1.5:  # 偏差超过1.5% → 用ETF替代
            print(f"    ⚠️ {name}: fundgz={gszzl_f:+.2f}% vs {track_name}={etf_chg:+.2f}% (偏差{diff:.1f}%) → 使用{track_name}数据")
            fd['estimated_change'] = f"{etf_chg:.2f}"
            fd['change_source'] = f'etf_{track_name}'
        elif diff > 0.5:
            print(f"    ⚠️ {name}: fundgz={gszzl_f:+.2f}% vs {track_name}={etf_chg:+.2f}% (偏差{diff:.1f}%) → 偏差可接受，保留fundgz")
        else:
            print(f"    ✅ {name}: fundgz={gszzl_f:+.2f}% vs {track_name}={etf_chg:+.2f}% ✓")
print(f"    ✅ 基金数据验证完成 ({sum(1 for v in funds_now.values() if v)}只)")

# 回退: 超时的基金用早盘数据兜底
if morning_data and morning_data.get('funds'):
    morning_funds = morning_data['funds']
    for code in FUND_CODES:
        if (code not in funds_now or funds_now[code] is None) and code in morning_funds and morning_funds[code]:
            funds_now[code] = morning_funds[code]
            print(f"  ↩️ 回退 {FUND_CODES[code]} (使用早盘数据)")

# 黄金联接基金(009478): 天天基金gszzl始终为0.00%，用黄金ETF市场价替代
gold_etf_c = quotes_now.get('黄金ETF市场价')
if gold_etf_c and '009478' in funds_now:
    fd = funds_now['009478']
    if fd and (fd.get('estimated_change', '0') == '0.00' or abs(float(fd.get('estimated_change', 0))) < 0.005):
        try:
            g_change = float(gold_etf_c.get('change_pct', 0) or 0)
            fd['estimated_change'] = str(g_change)
            fd['change_source'] = 'gold_etf'
            print(f"  🔄 修正 中银上海金ETF联接C: 黄金ETF{g_change:+.2f}% 替代基金估算0.00%")
        except (ValueError, TypeError):
            pass

# ── 2.5 行业板块收盘涨跌 ──
print("\n📊 行业板块收盘:")
sectors_now = get_sector_quotes()
sector_lines_close = [f"【行业板块收盘排行】"]
for name, q in sorted(sectors_now.items(), key=lambda x: -(x[1]['change_pct'] if x[1] else 0)):
    if q:
        emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
        sector_lines_close.append(f"{emoji} {name}: {q['open']}→{q['price']} ({q['change_pct']:+.2f}%)")
    else:
        sector_lines_close.append(f"❌ {name}: 暂无数据")
(SUMMARY_DIR / "_closing_sector.txt").write_text("\n".join(sector_lines_close))

# ── 2.6 收盘市场总览（成交额+涨跌家数）──
print("\n📊 收盘市场总览:")
overview = get_market_overview()
overview_lines_close = []
if overview.get('rise_count') is not None:
    from fund_tools import get_short_term_sentiment
    overview_lines_close.append(get_short_term_sentiment(overview))
if overview.get('total_turnover', 0) > 0:
    overview_lines_close.append(f"💰 两市成交: {overview['total_turnover']/1e8:.0f}亿 (沪{overview['sh_turnover']/1e8:.0f}亿 深{overview['sz_turnover']/1e8:.0f}亿)")
if overview_lines_close:
    (SUMMARY_DIR / "_closing_overview.txt").write_text("\n".join(overview_lines_close))

# ── 2.7 收盘北向资金 ──
print("\n🌊 收盘北向资金:")
northbound = get_northbound_flow()
nb_lines_close = []
if northbound.get('total') is not None:
    emoji = '🔴' if northbound['total'] > 0 else '🟢' if northbound['total'] < 0 else '🟡'
    nb_lines_close.append(f"{emoji} 北向资金: 沪{northbound['hgt']:+.2f}亿 深{northbound['sgt']:+.2f}亿 合计{northbound['total']:+.2f}亿")
    (SUMMARY_DIR / "_closing_northbound.txt").write_text("\n".join(nb_lines_close))

# ── 3. 对比分析 ──
comparison = {
    'date': today,
    'type': 'closing_review',
    'collected_at': datetime.now().isoformat(),
}

# 大盘对比：开盘方向 vs 收盘方向
if quotes_now:
    market_accuracy = {}
    for name, q_now in quotes_now.items():
        if q_now:
            open_price = float(q_now.get('open', 0) or 0)
            close_price = float(q_now.get('price', 0) or 0)
            prev_close = float(q_now.get('prev_close', 0) or 0)
            open_up = open_price > prev_close
            close_up = close_price > prev_close
            # 开盘方向: 开 vs 昨收
            open_dir = '↑' if open_up else '↓' if open_price < prev_close else '→'
            # 收盘方向: 收 vs 昨收
            close_dir = '↑' if close_up else '↓' if close_price < prev_close else '→'
            # 方向一致判定
            direction_same = open_up == close_up
            market_accuracy[name] = {
                'open_dir': open_dir,
                'close_dir': close_dir,
                'open': q_now.get('open', ''),
                'close': q_now.get('price', ''),
                'high': q_now.get('high', ''),
                'low': q_now.get('low', ''),
                'prev_close': q_now.get('prev_close', ''),
                'close_change_pct': float(q_now.get('change_pct', 0) or 0),
                'direction_same': direction_same,
            }
    comparison['market_accuracy'] = market_accuracy

# ── 4. 统计数据 ──
if 'market_accuracy' in comparison:
    correct = sum(1 for v in comparison['market_accuracy'].values() if v.get('direction_same'))
    total = len(comparison['market_accuracy'])
    comparison['market_score'] = f"{correct}/{total}"
    comparison['market_accuracy_pct'] = round(correct/total*100) if total > 0 else 0

# ── 5. 写复盘摘要文件 ──
review_lines = []
review_lines.append(f"━━━ 收盘复盘 · {today} ━━━")
review_lines.append("")

if 'market_score' in comparison:
    review_lines.append(f"📊 大盘方向判断: {comparison['market_score']} ({comparison['market_accuracy_pct']}%)")
    for name, v in comparison.get('market_accuracy', {}).items():
        emoji = '✅' if v.get('direction_same') else '❌'
        od = v.get('open_dir', '?')
        cd = v.get('close_dir', '?')
        cp = v.get('close_change_pct', 0)
        review_lines.append(f"  {emoji} {name}: 昨收{v['prev_close']} 开{v['open']}{od}→收{v['close']}{cd} 涨跌{cp:+.2f}%")
    review_lines.append("")

# 基金持仓分组表现（含发票表格数据，供AI格式化）
fund_groups_close = group_funds(funds_now)
fund_table_lines = []

# 写基金明细文件：按分组组织，每行 昨收净值→今日估算→涨跌
write_path = SUMMARY_DIR / "_closing_fund.txt"
fund_table_lines = []
for gname in ['黄金', '科技/AI', '资源/周期', '新能源', '医药']:
    gdata = fund_groups_close.get(gname)
    if not gdata or gdata['count'] == 0:
        continue
    fund_table_lines.append(f"【{gname}】")
    for f in gdata['funds']:
        fname = f.get('name', '?')
        nav = f.get('nav', '?')
        enav = f.get('estimated_nav', '?')
        ec = f.get('estimated_change', '?')
        fund_table_lines.append(f"{fname}|{nav}|{enav}|{ec}")
    fund_table_lines.append("")
write_path.write_text("\n".join(fund_table_lines))

# 北向资金（带时间戳）
if northbound.get('total') is not None:
    time_str = northbound.get('time', '收盘')
    emoji = '🔴' if northbound['total'] > 0 else '🟢' if northbound['total'] < 0 else '🟡'
    review_lines.append(f"🌊 **北向资金** ({time_str})")
    review_lines.append(f"  {emoji} 沪股通: {northbound['hgt']:+.2f}亿 | 深股通: {northbound['sgt']:+.2f}亿 | 合计: {northbound['total']:+.2f}亿")
    review_lines.append("")

if 'fund_accuracy' in comparison:
    review_lines.append("💰 基金估值偏差:")
    for code, v in comparison.get('fund_accuracy', {}).items():
        diff = v['now_est'] - v['morning_est']
        review_lines.append(f"  {v['name']}: 早估{v['morning_est']}% → 实际{v['now_est']}% (偏差{diff:+.1f})")

(SUMMARY_DIR / "_closing_summary.txt").write_text("\n".join(review_lines))

# ── 6. 归档到JSONL ──
store_jsonl(comparison, 'closing-reviews.jsonl')

# ── 7. 更新准确率统计 ──
accuracy_file = DATA_DIR / "fund_system_data" / "accuracy.jsonl"
accuracy_entry = {
    'date': today,
    'type': 'accuracy',
    'market_accuracy_pct': comparison.get('market_accuracy_pct', 0),
    'market_score': comparison.get('market_score', ''),
}
with open(accuracy_file, 'a') as f:
    f.write(json.dumps(accuracy_entry, ensure_ascii=False) + '\n')
upload_to_r2(str(accuracy_file), f"{FUND_SYSTEM_PREFIX}/data/accuracy.jsonl", "application/jsonl")

# ── 8. 数据合理性校验 (维度A) ──
closing_raw = {
    'date': today, 'type': 'closing_review',
    'quotes': quotes_now,
    'sectors': sectors_now,
    'market_overview': overview,
    'northbound': northbound,
    'funds': funds_now,
    'kol_posts': {},
}
sanity = run_sanity_checks(closing_raw)
(SUMMARY_DIR / "_closing_sanity.json").write_text(json.dumps(sanity, ensure_ascii=False, indent=2))
if sanity['warnings']:
    print(f"⚠️ 数据异常 {len(sanity['warnings'])} 处:")
    for w in sanity['warnings']:
        print(f"  {w}")

# ── 9. 解析历史信号 (维度B) ──
resolved = resolve_past_signals(quotes=quotes_now)
if resolved:
    print(f"📋 解析 {len(resolved)} 条历史信号")

# ── 10. 生成预格式化推文（LLM直接输出，无需改格式）──
push_lines = []

# 判断特殊日期
date_note = ""
if today.endswith(('03-31', '06-30', '09-30', '12-31')):
    if today.endswith('06-30') or today.endswith('12-31'):
        date_note = "半年收官"
        if today.endswith('06-30'):
            date_note = "上半年收官"
        else:
            date_note = "全年收官"
    else:
        date_note = f"{today[5:7]}月末收官"

push_lines.append(f"━━━ 🌆 收评 · 基金收盘复盘 · {today}({date_note}) ━━━")
push_lines.append("")

# 大盘走势表格
push_lines.append("📊 **大盘走势**")
push_lines.append("| 指数 | 昨收 | 今开 | 收盘 | 涨跌 | 开方向 |")
push_lines.append("|:----|:---:|:---:|:----:|:----:|:-----:|")
for name, v in comparison.get('market_accuracy', {}).items():
    od = v.get('open_dir', '?')
    cd = v.get('close_dir', '?')
    cp = v.get('close_change_pct', 0)
    emoji = '🔴' if cp > 0 else '🟢' if cp < 0 else '🟡'
    push_lines.append(f"| {name} | {v['prev_close']} | {v['open']}{od} | {v['close']}{cd} | {emoji} {cp:+.2f}% | {od} |")
push_lines.append("")
push_lines.append("开方向↑=高于昨收, ↓=低于昨收, →=持平")
push_lines.append("")

# 两市成交
if overview.get('total_turnover', 0) > 0:
    push_lines.append(f"💰 **两市成交**: {overview['total_turnover']/1e8:.0f}亿 (沪{overview['sh_turnover']/1e8:.0f}亿 深{overview['sz_turnover']/1e8:.0f}亿)")
    push_lines.append("")

# 📊 量价分析（今日收盘）——脚本自动生成
try:
    from fund_tools import get_volume_analysis
    prev_turnover = None
    # 尝试读前一日成交额（从昨日snapshot）
    snap_path = SUMMARY_DIR / "_yesterday_snapshot.json"
    if snap_path.exists():
        old_snap = json.loads(snap_path.read_text())
        old_ov = old_snap.get('market_overview', {})
        if old_ov.get('total_turnover', 0) > 0:
            prev_turnover = old_ov['total_turnover'] / 1e8
    va = get_volume_analysis(quotes_now, sectors_now, prev_total_turnover=prev_turnover)
    if va.get('volume_signals'):
        push_lines.append("📊 **量价分析**")
        push_lines.append("| 品种 | 涨跌 | 振幅 | 量价信号 |")
        push_lines.append("|:---|:----:|:----:|:--------:|")
        for s in va['volume_signals'][:12]:
            if s['amplitude'] < 0.1:
                continue
            emoji_ch = '🔴' if s['change_pct'] > 0 else '🟢' if s['change_pct'] < 0 else '🟡'
            push_lines.append(f"| {s['name']} | {emoji_ch} {s['change_pct']:+.2f}% | {s['amplitude']:.1f}% | {s['emoji']} {s['signal']} |")
        push_lines.append(f"| **总量总览** | | | {va['total_signal']} |")
        push_lines.append("")
except Exception as e:
    print(f"  ⚠️ 量价分析失败: {e}")

# 行业板块（3列表格）
sector_items = sorted(sectors_now.items(), key=lambda x: -(x[1]['change_pct'] if x[1] else 0))
if sector_items:
    push_lines.append("📊 **行业板块**")
    push_lines.append("| 板块 | 今开→收盘 | 涨跌 |")
    push_lines.append("|:---|:--------:|:----:|")
    for name, q in sector_items:
        if q:
            emoji = '🔴' if q['change_pct'] > 0 else '🟢' if q['change_pct'] < 0 else '🟡'
            open_v = q.get('open', '?')
            close_v = q.get('price', '?')
            push_lines.append(f"| {name} | {open_v}→{close_v} | {emoji} {q['change_pct']:+.2f}% |")
    push_lines.append("")

# 北向资金
if northbound.get('total') is not None:
    emoji = '🔴' if northbound['total'] > 0 else '🟢' if northbound['total'] < 0 else '🟡'
    push_lines.append(f"🌊 **北向资金**: 沪{northbound['hgt']:+.2f}亿 深{northbound['sgt']:+.2f}亿 合计{emoji}{northbound['total']:+.2f}亿")
    push_lines.append("")

# 基金表格：分组表格
push_lines.append("💰 **持仓基金（收盘估算净值，待晚间确认）**")
fund_groups_push = group_funds(funds_now)
for gname in ['黄金', '科技/AI', '资源/周期', '新能源', '医药']:
    gdata = fund_groups_push.get(gname)
    if not gdata or gdata['count'] == 0:
        continue
    push_lines.append(f"**【{gname}】**")
    push_lines.append("| 基金 | 昨收净值 | 估算净值 | 涨跌 |")
    push_lines.append("|:---|:-------:|:--------:|:----:|")
    for f in gdata['funds']:
        fcode = f.get('code', '')
        fname = FUND_CODES.get(fcode, f.get('name', '?'))
        nav = f.get('nav', '-')
        enav = f.get('estimated_nav', '-')
        ec = f.get('estimated_change', '?')
        try:
            ec_f = float(ec)
            emoji = '📈' if ec_f > 0 else '📉' if ec_f < 0 else '➖'
            push_lines.append(f"| {fcode} {fname[:20]} | {nav} | {enav} | {emoji}{ec_f:+.2f}% |")
        except (ValueError, TypeError):
            push_lines.append(f"| {fname} | {nav} | {enav} | - |")
    push_lines.append("")

# 早盘预测验证（如果预测文件存在）
predict_path = SUMMARY_DIR / "_morning_predictions.json"
if predict_path.exists():
    try:
        pred_data = json.loads(predict_path.read_text())
        preds = pred_data.get('predictions', [])
        if preds:
            push_lines.append("📋 **早盘预测验证**")
            push_lines.append("| 指数 | 开方向预测 | 收盘实际 | 验证 |")
            push_lines.append("|:----|:---------:|:--------:|:----:|")
            correct_pred = 0
            total_pred = len(preds)
            for p in preds:
                idx = p['index']
                pdir = p['predicted_direction']
                reason = p.get('reason', '')
                # 查找该指数的收盘涨跌
                v = comparison.get('market_accuracy', {}).get(idx, {})
                cp = v.get('close_change_pct', 0)
                actual_dir = '↑' if cp > 0 else '↓' if cp < 0 else '→'
                actual_str = f"{cp:+.2f}% {actual_dir}"
                # 验证：预测方向 vs 收盘实际方向
                p_up = pdir == '↑'
                p_down = pdir == '↓'
                a_up = cp > 0
                a_down = cp < 0
                if (p_up and a_up) or (p_down and a_down) or (pdir == '→' and cp == 0):
                    verify = '✅'
                    correct_pred += 1
                elif pdir == '→' and abs(cp) < 0.2:
                    verify = '✅'
                    correct_pred += 1
                else:
                    verify = '❌'
                note = "平开" if pdir == '→' else f"预计{'高' if pdir=='↑' else '低'}开"
                verify_note = "预测正确" if '✅' in verify else "预测失误"
                push_lines.append(f"| {idx} | {note} | {actual_str} | {verify} {verify_note} |")
            acc_pct = round(correct_pred / total_pred * 100) if total_pred > 0 else 0
            push_lines.append(f"**预测准确率：{correct_pred}/{total_pred} ({acc_pct}%)**")
            push_lines.append("")
    except Exception as e:
        push_lines.append(f"⚠️ 早盘预测验证读取失败: {e}")
        push_lines.append("")

# 周五版：增加今晚美股关注
if date.today().weekday() == 4:
    push_lines.append("🌙 **今晚美股关注**")
    push_lines.append("● 21:30 美股开盘，关注科技股走势")
    push_lines.append("● 若有大幅波动，将在周末推送外盘速报")
    push_lines.append("")

# 写预格式化推文
(SUMMARY_DIR / "_closing_tables.md").write_text("\n".join(push_lines))
print(f"   ✅ 预格式化推文已写入 _closing_tables.md ({len(push_lines)}行)")

# ── 11. 保存昨日收盘数据快照（供早报使用）──
# 修正基金涨跌幅：用黄金ETF价格替代009478的0.00%估算
funds_for_snapshot = {}
for code, fd in funds_now.items():
    if fd is not None:
        fcopy = dict(fd)
        # 009478：gold-linked fund, gszzl always 0.00%. Use gold spot instead.
        if code == '009478':
            gold_etf = quotes_now.get('黄金ETF市场价')
            if gold_etf:
                try:
                    g_change = float(gold_etf.get('change_pct', 0) or 0)
                    if fcopy.get('estimated_change', '0') == '0.00' or abs(float(fcopy.get('estimated_change', 0))) < 0.005:
                        fcopy['estimated_change'] = str(g_change)
                        fcopy['change_source'] = 'gold_etf'
                        print(f"  🔄 修正 {fcopy.get('name', code)}: 黄金ETF{g_change:+.2f}% 替代基金估算0.00%")
                except (ValueError, TypeError):
                    pass
        funds_for_snapshot[code] = fcopy
    else:
        funds_for_snapshot[code] = None

yesterday_snapshot = {
    'date': today,
    'quotes': {k: v for k, v in quotes_now.items() if v},
    'sectors': {k: v for k, v in sectors_now.items() if v},
    'market_overview': overview,
    'northbound': northbound,
    'funds': {k: v for k, v in funds_for_snapshot.items() if v},
    'fund_groups': fund_groups_close,
}
(SUMMARY_DIR / "_yesterday_snapshot.json").write_text(json.dumps(yesterday_snapshot, ensure_ascii=False, indent=2))
print(f"   ✅ 昨日收盘快照已写入 _yesterday_snapshot.json")

# ── 12. 趋势记录（收盘后记录各组涨跌，供N日连续评估）──
print("\n📊 趋势记录:")
record_group_trend(funds_now)

# ── 13. 操作评估（读取趋势 + 信号 → 评分）──
print("\n📋 操作评估:")
# 读取早盘KOL信号（如果有）
kol_signal_list = []
if morning_data and 'kol_posts' in morning_data:
    for uid, kd in morning_data['kol_posts'].items():
        for p in kd.get('posts', []):
            kol_signal_list.append({
                'kol_name': kd.get('name', '?'),
                'text_snippet': p.get('text', '')[:120],
                'predicted_direction': 'bullish' if any(w in p.get('text','') for w in ['右侧','加仓','补仓','反弹','建仓']) else
                                       'bearish' if any(w in p.get('text','') for w in ['泡沫','风险','过热','警惕','回调']) else 'neutral',
            })
eval_lines = []
eval_lines.append("📋 **操作评估**")
eval_lines.append("| 组别 | 信号 | 今日操作建议 | 收盘表现 | 评估 | 明日方向 |")
eval_lines.append("|:----|:----:|:-----------:|:--------:|:----:|:--------:|")
group_order = ['科技/AI', '黄金', '资源/周期', '新能源']
for gname in group_order:
    trends = get_group_trend(gname, days=5)
    s = score_group_action(gname, quotes_now, {}, kol_signal_list, trends)
    # 收盘表现 = 今日涨跌
    close_change = 0
    for _, c in trends[-1:]:
        close_change = c
    close_emoji = '🔴' if close_change > 0 else '🟢' if close_change < 0 else '➖'
    # 评估：操作建议 vs 实际表现
    action = s.get('action', '持有')
    if (action in ['增持', '关注'] and close_change > 0):
        eval_result = '✅ 正确'
    elif (action in ['减持', '观望'] and close_change < 0):
        eval_result = '✅ 正确'
    elif action == '持有':
        eval_result = '➖ 中性'
    else:
        eval_result = '❌ 偏差'
    # 明日方向：基于今日趋势推演
    if s['score'] >= 1:
        next_dir = '关注增持'
    elif s['score'] <= -1:
        next_dir = '观望/减持'
    else:
        next_dir = '持有'
    signal_emoji = '🟢' if s['score'] >= 1 else ('🔴' if s['score'] <= -1 else '🟡')
    reasons = '；'.join(s.get('reasons', [])) or '无明显信号'
    eval_lines.append(f"| {gname} | {signal_emoji} | {action} | {close_emoji} {close_change:+.2f}% | {eval_result} | {next_dir} |")
    print(f"  {signal_emoji} {gname}: {action} (收盘{close_change:+.2f}%, 得分{s['score']})")
eval_lines.append("")

# 趋势速览（sparkline 走势图）
eval_lines.append("📊 **本周分组趋势**")
eval_lines.append("| 分组 | 走势 | 本周幅度 |")
eval_lines.append("|:----|:---:|:--------:|")
spark_chars = ['▁','▂','▃','▄','▅','▆','▇','█']
for gname in group_order:
    trends = get_group_trend(gname, days=5)
    if trends:
        vals = [c for _, c in trends]
        if max(vals) == min(vals):
            spark = '▄' * len(vals)
        else:
            rng = max(vals) - min(vals)
            spark = ''.join(spark_chars[min(int((v - min(vals)) / rng * 7), 7)] for v in vals)
        first, last = vals[0], vals[-1]
        week_min, week_max = min(vals), max(vals)
        amplitude = week_max - week_min

        if last > first and last < 0:
            direction = '📈 跌幅收窄'
        elif last < first and last < 0:
            direction = '📉 跌幅扩大'
        elif last > first and last > 0:
            direction = '📈 持续上行'
        elif last < first and last > 0:
            direction = '📉 涨幅收窄'
        elif first < 0 < last:
            direction = '🔄 由跌转升'
        elif first > 0 > last:
            direction = '🔄 由升转跌'
        else:
            direction = '➖ 震荡'
        eval_lines.append(f"| {gname} | {spark} | {first:+.1f}% → {last:+.1f}% (振幅{amplitude:.1f}%) {direction} |")
    else:
        eval_lines.append(f"| {gname} | — | 尚无趋势数据 |")

rebalance_advice = check_rebalance(funds_now)
if rebalance_advice:
    eval_lines.append("")
    for a in rebalance_advice:
        eval_lines.append(f"⚠️ {a['suggestion']}")
else:
    eval_lines.append("")
    eval_lines.append("✅ 再平衡检查：各组占比均在目标范围内")

(SUMMARY_DIR / "_operation_eval.txt").write_text("\n".join(eval_lines))
print(f"   ✅ 操作评估已写入 _operation_eval.txt ({len(eval_lines)}行)")

# ── 结尾 ──
print(f"\n✅ 收盘复盘完成")
print(f"   大盘判断: {comparison.get('market_score', 'N/A')}")
print(f"   准确率: {comparison.get('market_accuracy_pct', 'N/A')}%")
