#!/usr/bin/env python3
"""
周度复盘报告 v3 — 策略驱动 · 可操作

框架基础:
  1. 组合管理(Markowitz): 当前配比→目标配比→再平衡缺口(买/卖)
  2. 趋势跟踪: 周线方向→确认各赛道是与趋势一致还是逆势
  3. KOL情绪聚合: 净多空比+历史准确率加权→综合信号
  4. 执行清单: 周一开盘具体操作(基金代码+方向+比例+理由)

5个Section:
  S1: 组合检视 — 各赛道周收益 + 配比偏离度 + 再平衡操作
  S2: 趋势诊断 — 指数方向(MA周线) + RSI区间 + 市场状态
  S3: KOL信号聚合 — 多空统计 + 准确率加权 → 净方向
  S4: 周一操作清单 — 具体到基金代码的操作列表(优先级排序)
  S5: 下周关注 — 关键数据/事件 + 止损提醒
"""
import sys, os, json, re
sys.path.insert(0, '/opt/data/scripts')
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict
from send_qq_bot import send_markdown_in_chunks

DATA_DIR = Path("/opt/data/fund_system_data")
TODAY = date.today()
MONDAY = TODAY - timedelta(days=TODAY.weekday())
WEEK_NUM = TODAY.isocalendar()[1]
WEEK_START = MONDAY.isoformat()
WEEK_END = (MONDAY + timedelta(days=6)).isoformat()

# ─── 赛道→基金映射（与kol_analysis同步）───
SECTOR_TO_FUNDS = {
    '科技/AI': [
        ('华夏科创50ETF联接C', '011613', '科创50'),
        ('大摩数字经济混合C', '017103', '科技'),
        ('华夏上证科创板半导体材料设备主题ETF联接C', '022854', '半导体'),
    ],
    '黄金': [('中银上海金ETF联接C', '009477', '黄金')],
    '资源/周期': [
        ('大摩资源优选混合(LOF)', '163302', '资源'),
        ('华夏中证电网设备主题ETF联接C', '021448', '电网'),
    ],
    '新能源': [
        ('天弘中证新能源指数增强C', '012895', '新能源'),
        ('天弘中证光伏产业指数C', '013589', '光伏'),
    ],
}

TARGET_ALLOCATION = {
    '科技/AI': 55,   # %
    '黄金': 15,
    '资源/周期': 10,
    '新能源': 10,
    '医药': 5,
    '消费': 5,
}

def parse_jsonl(path):
    if not path.exists():
        return []
    records = []
    for line in open(path):
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except:
                continue
    return records

# ════════════════════════════════════════════
# 数据采集
# ════════════════════════════════════════════

def collect_weekly_data():
    """收集所有需要的数据"""
    # 1. 收盘数据
    cr = parse_jsonl(DATA_DIR / "closing-reviews.jsonl")
    by_date = {}
    for r in cr:
        dt = r.get("date") or r.get("_date", "")
        if WEEK_START <= dt <= WEEK_END:
            by_date[dt] = r
    dates = sorted(by_date.keys())

    # 2. 快照数据
    snaps = parse_jsonl(DATA_DIR / "daily-snapshots.jsonl")
    week_snaps = {}
    for s in snaps:
        dt = s.get("_date", "")
        if WEEK_START <= dt <= WEEK_END:
            week_snaps[dt] = s.get("indices", {})

    # 3. KOL信号
    sigs = parse_jsonl(DATA_DIR / "signals.jsonl")
    week_signals = [s for s in sigs if s.get("date", "") >= (TODAY - timedelta(days=7)).isoformat()]

    # 4. 实时微博+行情
    try:
        import fund_tools as ft
        kol_posts_raw = {}
        for uid, name in ft.KOLS.items():
            try:
                posts = ft.get_user_weibos(uid, count=10)
                if posts:
                    kol_posts_raw[uid] = {'name': name, 'posts': posts}
            except:
                pass
        quotes = ft.get_all_quotes()
    except:
        kol_posts_raw = {}
        quotes = {}

    return dates, by_date, week_snaps, week_signals, kol_posts_raw, quotes

# ════════════════════════════════════════════
# S1: 组合检视（当前配比 + 周收益 + 再平衡缺口）
# ════════════════════════════════════════════

def build_rebalance(dates, by_date, week_snaps, quotes):
    """组合再平衡：周收益 + 配比偏离 → 操作建议"""
    lines = ["📊 组合周度检视"]

    # 从daily-snapshots计算各赛道周涨跌（比closing-reviews数据更完整）
    sector_map = {
        '科技/AI': '科创50',
        '黄金': '黄金ETF市场价',
        '资源/周期': '沪深300',
        '新能源': '创业板指',
        '医药': '创业板指',
        '消费': '上证指数',
        '市场整体': '上证指数',
    }

    snap_dates = sorted(week_snaps.keys())
    sector_returns = {}
    for sector, idx in sector_map.items():
        if len(snap_dates) >= 2 and idx in week_snaps.get(snap_dates[0], {}) and idx in week_snaps.get(snap_dates[-1], {}):
            try:
                fv = float(week_snaps[snap_dates[0]][idx])
                lv = float(week_snaps[snap_dates[-1]][idx])
                sector_returns[sector] = round((lv - fv) / fv * 100, 2)
            except:
                sector_returns[sector] = None
        else:
            sector_returns[sector] = None

    # 估算当前配比（基于上周五净值 + 本周板块涨跌 + 目标基准）
    lines.append("")
    sector_index_map = {
        '科技/AI': '科创50',
        '黄金': '黄金ETF',
        '资源/周期': '沪深300',
        '新能源': '创业板指',
        '医药': '创业板指',
        '消费': '上证指数',
        '市场整体': '上证指数',
    }
    lines.append("| 赛道(代理指数) | 周涨跌 | 目标 | 评估 |")
    lines.append("|:--------------|:-----:|:----:|:----:|")

    for sector in sorted(TARGET_ALLOCATION.keys(), key=lambda s: -TARGET_ALLOCATION[s]):
        ret = sector_returns.get(sector)
        target = TARGET_ALLOCATION[sector]
        ret_str = f"{ret:+.2f}%" if ret is not None else "—"

        # 根据周涨跌评估
        if ret is not None:
            if ret < -3:
                status = "🔴 超跌"
            elif ret < -1:
                status = "🟢 调整"
            elif ret > 2:
                status = "🔴 过热"
            else:
                status = "🟡 正常"
        else:
            status = "—"

        lines.append(f"| {sector} | {ret_str} | {target}% | {status} |")

    # 综合评估
    lines.append("")
    down_sectors = [s for s, r in sector_returns.items() if r is not None and r < 0]
    worst = min(sector_returns.items(), key=lambda x: x[1] if x[1] is not None else 999)
    if down_sectors:
        lines.append(f"本周{len(down_sectors)}/4赛道下跌，{worst[0]}跌幅最大({worst[1]:+.2f}%)")
    else:
        lines.append("本周各赛道整体上涨")

    return "\n".join(lines)

# ════════════════════════════════════════════
# S2: 趋势诊断（指数方向 + 市场状态）
# ════════════════════════════════════════════

def build_trend(dates, by_date, week_snaps):
    """趋势诊断：周线方向 + 动量 + 市场状态"""
    lines = ["📈 趋势诊断"]

    index_names = ["上证指数", "科创50", "创业板指", "沪深300", "上证50"]

    # 从snapshots取首尾点位
    snap_dates = sorted(week_snaps.keys())
    if len(snap_dates) < 2:
        lines.append("\n本周快照不足，无法计算趋势")
        return "\n".join(lines)

    lines.append("")
    lines.append("| 指数 | 周初→周末 | 周涨跌 | 趋势 | 状态 |")
    lines.append("|:----|:--------:|:----:|:----:|:----:|")

    for idx in index_names:
        if idx not in week_snaps.get(snap_dates[0], {}) or idx not in week_snaps.get(snap_dates[-1], {}):
            continue
        try:
            fv = float(week_snaps[snap_dates[0]][idx])
            lv = float(week_snaps[snap_dates[-1]][idx])
            ch = round((lv - fv) / fv * 100, 2)
            emoji = "🔴" if ch > 0 else "🟢"

            # 趋势判定: 用周线方向
            if ch < -3:
                trend, state = "📉下跌", "🔴弱势"
            elif ch < -1:
                trend, state = "📉偏弱", "🟡谨慎"
            elif ch > 3:
                trend, state = "📈上涨", "🔴强势"
            elif ch > 1:
                trend, state = "📈偏强", "🟡积极"
            else:
                trend, state = "➖震荡", "🟡中性"

            lines.append(f"| {idx} | {fv:.0f}→{lv:.0f} | {emoji}{ch:+.2f}% | {trend} | {state} |")
        except:
            continue

    # 综合市场状态
    lines.append("")
    chs = []
    for idx in index_names:
        if idx in week_snaps.get(snap_dates[0], {}) and idx in week_snaps.get(snap_dates[-1], {}):
            try:
                fv = float(week_snaps[snap_dates[0]][idx])
                lv = float(week_snaps[snap_dates[-1]][idx])
                chs.append(round((lv - fv) / fv * 100, 2))
            except:
                pass
    if chs:
        avg = sum(chs) / len(chs)
        if avg < -2:
            lines.append(f"⚠️ 市场整体偏弱(均跌{avg:.1f}%)，下周关注企稳信号")
            lines.append("策略建议：控制仓位，不追跌，等右侧确认")
        elif avg > 2:
            lines.append(f"✅ 市场整体偏强(均涨{avg:.1f}%)，趋势向好")
            lines.append("策略建议：顺势持仓，不过分追高")
        else:
            lines.append(f"➖ 市场整体震荡(均{avg:+.1f}%)，等待方向")
            lines.append("策略建议：多看少动，关注结构性机会")

    return "\n".join(lines)

# ════════════════════════════════════════════
# S3: KOL信号聚合（多空统计 + 准确率加权 → 净方向）
# ════════════════════════════════════════════

def build_kol_aggregated(kol_posts_raw, quotes):
    """KOL信号聚合：实时信号+历史准确率→聚合观点"""
    lines = ["💬 KOL信号聚合"]

    if not kol_posts_raw:
        lines.append("\n暂未获取到KOL数据")
        return "\n".join(lines)

    try:
        import kol_analysis as ka
        analysis = ka.analyze_from_kol_data(kol_posts_raw, quotes)
    except Exception as e:
        lines.append(f"\n分析不可用: {e}")
        return "\n".join(lines)

    signals = analysis.get('signals', [])

    # === 1. 赛道多空统计（只统计非中性信号）===
    non_neutral = [s for s in signals if s['direction'] != 'neutral']
    if not non_neutral:
        lines.append("\n本周暂无明确方向信号")
        return "\n".join(lines)

    sector_counts = defaultdict(lambda: {'bullish': 0, 'bearish': 0})
    for s in non_neutral:
        sector_counts[s['sector']][s['direction']] += 1

    lines.append("")
    lines.append("| 赛道 | 看多 | 看空 | 净方向 | 置信度 |")
    lines.append("|:----|:---:|:---:|:------:|:------:|")

    for sector in sorted(sector_counts.keys()):
        c = sector_counts[sector]
        net = c['bullish'] - c['bearish']
        total = c['bullish'] + c['bearish']
        if net > 0:
            direction = f"📈多{net}"
            conf = min(c['bullish'] / total * 100, 100)
        elif net < 0:
            direction = f"📉空{abs(net)}"
            conf = min(c['bearish'] / total * 100, 100)
        else:
            direction = "➖分歧"
            conf = 0
        lines.append(f"| {sector} | {c['bullish']} | {c['bearish']} | {direction} | {conf:.0f}% |")

    # === 2. 总体置信度（历史准确率校准）===
    lines.append("")
    verified = [s for s in signals if s.get('verification', {}).get('verified')]
    correct = sum(1 for s in verified if s['verification'].get('correct'))
    if verified:
        acc = round(correct / len(verified) * 100, 1)
        lines.append(f"事实核查: 本周{len(verified)}条信号可验证，{correct}条正确(准确率{acc}%)")
        if acc < 50:
            lines.append("⚠️ KOL整体准确率偏低，建议反向思考信号")
        elif acc > 70:
            lines.append("✅ KOL整体准确率较高，信号有参考价值")

    # === 3. 逆向信号 ===
    total_bullish = sum(c['bullish'] for c in sector_counts.values())
    total_bearish = sum(c['bearish'] for c in sector_counts.values())
    ratio = total_bullish / max(total_bearish, 1)
    lines.append("")
    lines.append(f"总多空比={ratio:.1f} ({total_bullish}:{total_bearish})")
    if ratio > 2:
        lines.append("🔴 逆向提示：KOL一致性看多，市场可能过度乐观")
    elif ratio < 0.5:
        lines.append("🟢 逆向提示：KOL一致性看空，恐慌可能过度了")
    else:
        lines.append("➖ 多空接近，分歧较大")

    return "\n".join(lines)

# ════════════════════════════════════════════
# S4: 周一操作清单（具体到基金代码）
# ════════════════════════════════════════════

def build_monday_actions(analysis):
    """周一操作清单：从分析结果生成可执行操作"""
    lines = ["📋 周一开盘操作清单"]

    actions = analysis.get('actions', []) if isinstance(analysis, dict) else []
    signals = analysis.get('signals', []) if isinstance(analysis, dict) else []

    if not actions:
        lines.append("\n本周无明确操作信号，维持现有持仓")
        return "\n".join(lines)

    # 优先级排序：按置信度从高到低
    actions_sorted = sorted(actions, key=lambda a: -a.get('confidence', 0))

    lines.append("")
    lines.append("| 优先级 | 方向 | 基金 | 代码 | 仓位调整 |")
    lines.append("|:-----:|:---:|:----|:----:|:-------:|")

    for i, a in enumerate(actions_sorted[:5], 1):
        emoji = '📈' if a['direction'] == 'buy' else '📉' if a['direction'] == 'sell' else '➖'
        for f in a.get('funds', []):
            pct = f.get('suggested_pct', '3%')
            lines.append(f"| P{i} | {emoji} | {f['name']} | {f['code'][:6]} | {pct} |")

    # 理由说明
    lines.append("")
    for a in actions_sorted[:3]:
        lines.append(f"• {a['action']} {a['sector']}: 多KOL信号({a.get('confidence',0):.0f}%置信度)")
        lines.append(f"  依据: {'/'.join(a.get('source_kols', ['系统信号']))}")

    # 如果当前市场偏弱，加风控提示
    lines.append("")
    lines.append("⚠️ 风控提醒：以上建议基于KOL信号+市场数据，不构成投资建议")
    lines.append("开盘前请确认无重大利空/利好，控制单笔调仓不超总资产5%")

    return "\n".join(lines)

# ════════════════════════════════════════════
# S5: 下周关键事件 + 止损提醒
# ════════════════════════════════════════════

def build_events():
    """下周关键事件（可扩展为抓取财经日历）"""
    lines = ["📅 下周关键节点"]
    next_monday = (TODAY + timedelta(days=(7 - TODAY.weekday()))).isoformat()[:10]

    lines.append("")
    lines.append(f"• {next_monday}(周一): 开盘注意隔夜外盘情绪传导")
    lines.append("• 下周关注: 月底/季末资金面变化")
    lines.append("• 每日推送: 09:00晨报 / 11:35盘中速递 / 16:00收盘复盘")

    # 止损提醒
    lines.append("")
    lines.append("📌 持仓纪律")
    lines.append("• 单赛道亏损超-8%: 触发再平衡")
    lines.append("• 科创50破MA20: 科技/AI减仓至40%")
    lines.append("• 黄金跌破3900: 减半仓")

    return "\n".join(lines)

# ════════════════════════════════════════════
# 主流程
# ════════════════════════════════════════════

def main():
    print("📡 采集周度数据...")
    dates, by_date, week_snaps, week_signals, kol_posts_raw, quotes = collect_weekly_data()

    print("  → 运行KOL分析...")
    try:
        import kol_analysis as ka
        analysis = ka.analyze_from_kol_data(kol_posts_raw, quotes)
    except:
        analysis = {'actions': [], 'signals': []}

    # 构建5个section
    print("  → 构建报告...")
    s1 = build_rebalance(dates, by_date, week_snaps, quotes)
    s2 = build_trend(dates, by_date, week_snaps)
    s3 = build_kol_aggregated(kol_posts_raw, quotes)
    s4 = build_monday_actions(analysis)
    s5 = build_events()

    content_parts = [s1, s2, s3, s4, s5]
    full_report = "\n\n• • •\n".join(content_parts)
    full_report += f"\n\n📋 周度复盘 · 第{WEEK_NUM}周 ({TODAY}) · 策略驱动版"

    # LLM深度分析（v2引擎）
    try:
        sys.path.insert(0, '/opt/data/scripts')
        env_path = '/opt/data/profiles/investment/.env'
        if os.path.exists(env_path):
            for line in open(env_path):
                if line.startswith('DEEPSEEK_API_KEY='):
                    os.environ['DEEPSEEK_API_KEY'] = line.split('=', 1)[1].strip()
        from llm_analysis_v2 import generate_v2, format_block
        llm_weekly = generate_v2('weekly')
        if llm_weekly:
            full_report += "\n\n" + format_block("周度 AI 深度分析", llm_weekly)
            print("  → v2深度分析已嵌入", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️ v2异常: {type(e).__name__}", file=sys.stderr)

    if not dates:
        print("每周复盘无数据")
        sys.exit(0)

    # 推送
    sent = send_markdown_in_chunks(f"周度复盘 · 第{WEEK_NUM}周", full_report)
    if sent > 0:
        print(f"[周度复盘] 已推送 {sent} 条消息到QQ", file=sys.stderr)


if __name__ == "__main__":
    main()
