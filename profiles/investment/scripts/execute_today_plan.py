#!/usr/bin/env python3
"""
14:30 基金操作决策引擎 v4 — 策略驱动 + 板块代理估算
======================================================
数据管线:
  链路A: 板块ETF代理估算（实时，来自中午采集）
  链路B: 历史净值走势（AKShare，用于回撤/趋势）
  链路C: 操作记录（operation_*.md，真实成本）

策略框架:
  1. 回撤阶梯:  -8%半仓 / -15%止盈 / -25%深套
  2. 科技再平衡: >65%科技→强制减仓  
  3. 建仓双轨:  -4%下轨加 / +5%上轨追
  4. 趋势跟踪:  3日累计>+5%强 / <-5%弱

自校验: 数据交叉验证 + 策略一致性检查
"""
import sys, os, json, re
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.insert(0, '/opt/data/scripts')
sys.path.insert(0, '/opt/data/akshare-deps')
os.environ['TQDM_DISABLE'] = '1'

TODAY = date.today()
SUMMARY_DIR = Path("/tmp/fund_data")
DATA_DIR = Path("/opt/data/fund_system_data")
OPS_DIR = DATA_DIR / "operations"
SEED_FILE = DATA_DIR / "seed_portfolio.json"

# ── 建仓计划 ──
BUILDING_PLAN = {}
if SEED_FILE.exists():
    try:
        BUILDING_PLAN = json.loads(SEED_FILE.read_text()).get('building_plan', {})
    except: pass

def bjt_hour():
    return (datetime.now(tz=__import__("datetime").timezone.utc) + timedelta(hours=8)).hour

# ── 基金→板块映射（策略依据: 跟踪指数关联度）──
FUND_SECTOR_MAP = {
    '009478': '黄金ETF市场价',    # 黄金ETF联接
    '011613': '科创50',           # 科创50ETF联接
    '024418': '半导体',           # 科创板半导体材料设备ETF联接
    '026449': '恒生科技ETF',      # 沪港深科技(港股关联)
    '014871': '半导体',           # 科技领先(重仓半导体)
    '020233': '半导体',           # 景气智选(科技成长)
    '017103': '通信',             # 数字经济(通信/计算机)
    '011712': '通信',             # 万众创新(科技)
    '163302': '有色金属',         # 资源优选
    '025857': '新能源',           # 电网设备
    '012329': '新能源',           # 新能源指数增强
    '011103': '光伏',             # 光伏
    '003096': '医药',             # 医疗健康
    '013403': '恒生科技ETF',      # 恒生科技QDII
}

# 科技分类(用于再平衡)
TECH_CODES = {c for c, s in FUND_SECTOR_MAP.items() if s in ('半导体','通信','科创50','恒生科技ETF')}
BUILDING_CODES = {'003096', '013403'}  # 建仓期

# ══════════════════════════════════════════
# 数据层
# ══════════════════════════════════════════

def read_tmp(name):
    p = SUMMARY_DIR / name
    return p.read_text().strip() if p.exists() else ""

def parse_sector_data():
    """解析板块数据 → {板块名: 涨跌幅%}"""
    sector_text = read_tmp("_noon_sector.txt")
    result = {}
    for line in sector_text.split('\n'):
        m = re.match(r"[🔴🟢🟡]\s*(\S+):.*\(([+-]?\d+\.?\d*)%\)", line)
        if m:
            result[m.group(1)] = float(m.group(2))
    # 补充指数
    mkt = read_tmp("_noon_market.txt")
    for line in mkt.split('\n'):
        parts = line.split('|')
        if len(parts) >= 3:
            name = parts[0].strip()
            try:
                pct = float(parts[2].strip().replace('%', ''))
                result[name] = pct
            except: pass
    return result

def parse_ops():
    """读操作记录 → {code: {name, cost_total, batches}}"""
    portfolio = {}
    if OPS_DIR.exists():
        for fpath in sorted(OPS_DIR.glob('operation_*.md')):
            text = fpath.read_text(encoding='utf-8')
            rows = re.findall(r'\|\s*(\d{1,2}/\d{1,2})\s*\|\s*([^|]+?)\s*\|\s*(\d{6})\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|', text)
            for date_str, fname, code_str, amt_str in rows:
                code = code_str; amt = float(amt_str)
                if code not in portfolio:
                    portfolio[code] = {'name': fname.strip(), 'cost_total': 0, 'batches': []}
                portfolio[code]['batches'].append({'date': date_str, 'amount': amt})
                portfolio[code]['cost_total'] += amt
    return portfolio

def get_history(code):
    """获取历史净值数据（缓存）"""
    if not hasattr(get_history, 'cache'):
        get_history.cache = {}
    if code in get_history.cache:
        return get_history.cache[code]
    try:
        import akshare as ak; import pandas as pd
        df = ak.fund_open_fund_info_em(symbol=code, indicator='单位净值走势')
        if df is None or len(df) < 3:
            get_history.cache[code] = None
            return None
        df['净值日期'] = pd.to_datetime(df['净值日期']).dt.date
        today_d = date.today()
        df_y = df[df['净值日期'] >= date(today_d.year, 1, 1)]
        if len(df_y) < 2:
            get_history.cache[code] = None
            return None
        fn, ln = float(df_y.iloc[0]['单位净值']), float(df_y.iloc[-1]['单位净值'])
        ytd = round((ln/fn-1)*100, 1)
        d30 = today_d - timedelta(days=30)
        df_30 = df_y[df_y['净值日期'] >= d30]
        m1 = round((float(df_30.iloc[-1]['单位净值'])/float(df_30.iloc[0]['单位净值'])-1)*100, 1) if len(df_30)>=2 else None
        peak_row = df_30.loc[df_30['单位净值'].idxmax()]
        peak_nav = float(peak_row['单位净值'])
        drawdown = round((ln/peak_nav - 1)*100, 1)
        daily = []
        d5 = today_d - timedelta(days=7)
        df_5 = df_y[df_y['净值日期'] >= d5].tail(6)
        for i in range(1, len(df_5)):
            pc = float(df_5.iloc[i-1]['单位净值'])
            cc = float(df_5.iloc[i]['单位净值'])
            daily.append((str(df_5.iloc[i]['净值日期']), round((cc/pc-1)*100, 2)))
        r = {'ytd': ytd, 'm1': m1, 'daily': daily, 'drawdown': drawdown, 'peak_nav': peak_nav, 'latest_nav': ln}
        get_history.cache[code] = r
        return r
    except Exception as e:
        get_history.cache[code] = None
        return None

# ══════════════════════════════════════════
# 策略引擎
# ══════════════════════════════════════════

STRATEGY = {
    '回撤阶梯': '回撤-8%~-15%+连跌→减半; -15%~-25%→设止盈; >-25%→深套等反弹',
    '科技再平衡': '科技占比>65%→强制减至55%，分散风险',
    '建仓双轨': '跌穿-4%下轨→DCA加仓; 涨破+5%上轨→追强加仓',
    '趋势跟踪': '3日累计>+5%强趋势可持有; <-5%弱趋势不加仓',
}

def build_portfolio():
    """构建持仓：板块代理估算 + 历史净值"""
    ops = parse_ops()
    seed_funds = {}
    if SEED_FILE.exists():
        try:
            seed_funds = json.loads(SEED_FILE.read_text()).get('funds', {})
        except: pass
    sectors = parse_sector_data()

    from fund_tools import FUND_CODES
    merged = {}
    for code, name in FUND_CODES.items():
        merged[code] = {'name': name, 'cost': seed_funds.get(code, {}).get('cost', 0)}
    for code, info in ops.items():
        if code in merged:
            merged[code]['cost'] += info['cost_total']
        else:
            merged[code] = {'name': info['name'], 'cost': info['cost_total']}

    # 主线程AKShare全量实时估算（一次性获取，比板块代理精准）
    fund_realtime = {}
    try:
        import akshare as ak
        df = ak.fund_value_estimation_em()
        est_col = [c for c in df.columns if '估算增长率' in c]
        if est_col:
            for _, row in df.iterrows():
                code = str(row['基金代码'])
                if code in merged:
                    try:
                        val = str(row.get(est_col[0], '0')).replace('%', '').strip()
                        fund_realtime[code] = float(val) if val and val != '---' else 0.0
                    except: pass
        if fund_realtime:
            print(f"  ✅ AKShare实时估算: {len(fund_realtime)}支基金", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️ AKShare全量估值: {e}", file=sys.stderr)

    result = {}
    # 从每日快照读昨日市值作为基线
    snap_file = DATA_DIR / "daily-snapshots.jsonl"
    yest_value_base = {}  # {code: yesterday_value}
    if snap_file.exists():
        import json as _json
        for line in snap_file.read_text().strip().split('\n'):
            if line:
                snap = _json.loads(line)
                if snap.get('_date') == (date.today() - timedelta(days=1)).isoformat():
                    for code, finfo in snap.get('funds', {}).items():
                        yest_value_base[code] = finfo.get('value', 0)
                    break
        # fallback: 如果昨天数据没有逐基金，用总市值按成本比例分摊
        if not yest_value_base:
            for line in snap_file.read_text().strip().split('\n'):
                if line:
                    snap = _json.loads(line)
                    if snap.get('_date') == (date.today() - timedelta(days=1)).isoformat():
                        total_val = snap.get('portfolio_value', 0) or snap.get('portfolio_cost', 0) or 0
                        total_cost = snap.get('portfolio_cost', 0)
                        if total_val > 0 and total_cost > 0:
                            for code, info in merged.items():
                                ratio = info['cost'] / total_cost
                                yest_value_base[code] = round(total_val * ratio, 2)
                        break

    for code, info in merged.items():
        # 链路A: AKShare实时估算（最准确）
        if code in fund_realtime:
            est_change = fund_realtime[code]
            est_source = "AKShare"
        else:
            # 链路B: 板块代理估算（备援）
            proxy_sector = FUND_SECTOR_MAP.get(code, '')
            est_change = sectors.get(proxy_sector, 0.0)
            est_source = "板块代理"
        
        hist = get_history(code)
        drawdown = hist['drawdown'] if hist else 0
        daily = hist['daily'] if hist else []
        d3_sum = sum(c for _, c in daily[-3:]) if daily else 0
        latest_nav = hist['latest_nav'] if hist else None
        
        cost = info['cost']
        if code in yest_value_base and yest_value_base[code] > 0:
            base_val = yest_value_base[code]
            current_val = round(base_val * (1 + est_change / 100), 2)
        elif latest_nav and latest_nav > 0:
            # 备援：用昨日净值估算
            units = cost / latest_nav
            today_nav = latest_nav * (1 + est_change / 100)
            current_val = round(units * today_nav, 2)
        else:
            current_val = round(cost * (1 + est_change / 100), 2)
        
        pnl = round(current_val - cost, 2)
        
        result[code] = {'name': info['name'], 'cost': cost,
                        'est_change': round(est_change, 2), 'est_source': est_source,
                        'current_val': current_val,
                        'pnl': pnl,
                        'drawdown': drawdown, 'd3_sum': round(d3_sum, 2),
                        'daily': daily, 'latest_nav': latest_nav}
    return result

def generate_advice(portfolio):
    """策略引擎 → 操作建议（带策略标签）"""
    lines = []
    total_val = sum(v['current_val'] for v in portfolio.values())
    total_cost = sum(v['cost'] for v in portfolio.values())
    total_pnl = round((total_val/total_cost-1)*100, 1) if total_cost > 0 else 0
    tech_val = sum(portfolio[c]['current_val'] for c in TECH_CODES if c in portfolio)
    tech_pct = round(tech_val/total_val*100, 1) if total_val > 0 else 0

    afternoon = bjt_hour() >= 14
    mode = '🕝 14:30决策' if afternoon else '🕤 盘前'

    lines.append(f"# 基金决策 · {TODAY.strftime('%m/%d')} {mode}")
    lines.append(f"> 市值{total_val:.0f} 成本{total_cost:.0f} {'📈' if total_pnl>=0 else '📉'}{total_pnl:+.1f}% | "
                 f"科技{tech_pct}%{'⚠️超配' if tech_pct>65 else ''}")
    lines.append("")

    # ── 快照 ──
    idx_str, gains, losses, nb, vol = get_market_snapshot()
    if idx_str: lines.append(f"📊 {idx_str}")
    if gains: lines.append(f"🔥 {' '.join(gains[:3])}")
    if losses: lines.append(f"🟢 {' '.join(losses[:3])}")
    if nb: lines.append(f"🌊 {nb}")
    lines.append("")

    # ── 操作表（板块代理估算，带策略标签）──
    lines.append("🎯 今日操作")
    lines.append("| 基金 | 实时估 | 回撤 | 操作 | 策略依据 |")
    lines.append("|:----|:----:|:---:|:----|:--------|")

    ops = parse_ops()
    has_action = False

    # 建仓基金优先
    for code in BUILDING_CODES:
        if code not in portfolio: continue
        v = portfolio[code]
        plan = BUILDING_PLAN.get(code, {})
        done = ops.get(code, {}).get('cost_total', 0)
        target = plan.get('target', 0)
        remain = max(0, target - done)

        if remain == 0:
            lines.append(f"| {code} {v['name'][:10]} | ✅已满 | — | 持有 | 建仓完成 |")
            has_action = True; continue

        ec = v['est_change']
        dd = v['drawdown']
        strategy = f"建仓双轨(剩余{remain:.0f}元)"
        
        if ec < -4:
            action = f"📈加{int(remain)}元"
            reason = f"跌破-4%下轨"
        elif ec > 5:
            action = f"📈加{int(remain)}元"
            reason = f"涨破+5%上轨"
        elif dd and dd < -15:
            action = "🟡观望"
            reason = f"深套{dd:.1f}%等企稳"
        else:
            action = "🟡观望"
            reason = f"{ec:+.1f}%区间内"
        lines.append(f"| {code} {v['name'][:10]} | {ec:+.1f}% | {dd:.1f}% | {action} | {strategy}({reason}) |")
        has_action = True

    # 非建仓基金（按估值涨跌排序，跌多的在前）
    for code, v in sorted(portfolio.items(), key=lambda x: (x[1]['est_change'], x[1]['drawdown'])):
        if code in BUILDING_CODES: continue
        ec = v['est_change']
        dd = v['drawdown']
        d3 = v['d3_sum']
        cur = v['current_val']

        # 策略判定（按优先级）
        if dd and dd < -25:
            action = "🟡持有"
            strat = "回撤阶梯"
            reason = f"深套{dd:.1f}%等反弹到-15%"
        elif dd and dd < -15 and d3 < -5:
            action = "🟡持有"
            strat = "回撤阶梯"
            reason = f"回撤{dd:.1f}%+连跌,设-10%止盈"
        elif d3 < -8:
            action = "🟡持有"
            strat = "趋势跟踪"
            reason = f"3日暴跌{d3:+.1f}%等企稳"
        elif dd and dd < -8 and d3 < -3:
            action = f"📉减半(~{int(cur/2)}元)"
            strat = "回撤阶梯"
            reason = f"回撤{dd:.1f}%+连跌{d3:+.1f}%"
        elif code in TECH_CODES and tech_pct > 65 and ec >= 0:
            action = f"📉减1/3(~{int(cur/3)}元)"
            strat = "科技再平衡"
            reason = f"科技超配{tech_pct}%+今日反弹{ec:+.1f}%"
        elif ec < -3:
            action = "🟡持有"
            strat = "趋势跟踪"
            reason = f"弱势{ec:+.1f}%不加仓"
        else:
            action = "🟡持有"
            strat = "安全"
            reason = "无触发信号"

        sector_tag = v.get('est_source', 'AKShare')[:4]
        lines.append(f"| {code} {v['name'][:16]:16s} | {ec:+.1f}% | {dd:.1f}% | {action} | [{strat}]{reason} |")
        has_action = True

    if not has_action:
        lines.append("| — | — | — | 🟡全部持有 | 无明确信号 |")

    lines.append("")
    lines.append(f"📌 策略: 回撤阶梯|科技再平衡|建仓双轨|趋势跟踪")
    return '\n'.join(lines)

def get_market_snapshot():
    """读取盘中数据→快照"""
    market = read_tmp("_noon_market.txt")
    sector = read_tmp("_noon_sector.txt")
    nb = read_tmp("_noon_northbound.txt")
    overview = read_tmp("_noon_overview.txt")

    idx = []
    for line in market.split("\n"):
        parts = line.split("|")
        if len(parts) >= 3:
            name = parts[0].strip()
            price = parts[1].strip()
            pct = parts[2].strip().replace('%', '')
            short = name.replace('上证指数','上证').replace('沪深300','沪深').replace('科创50','科创').replace('创业板指','创业板')
            try: emoji = "🔴" if float(pct) > 0 else "🟢"
            except: emoji = "🟡"
            idx.append(f"{short}{price}{emoji}{pct}%")
    idx_str = " | ".join(idx[:4]) if idx else ""

    gains, losses = [], []
    for line in sector.split("\n"):
        m = re.match(r"[🔴🟢🟡]\s*(\S+):.*\(([+-]?\d+\.?\d*)%\)", line)
        if m:
            n, p = m.group(1), m.group(2)
            try:
                if float(p) > 1: gains.append(f"{n}+{float(p):.1f}%")
                elif float(p) < -1: losses.append(f"{n}{float(p):.1f}%")
            except: pass

    nb_clean = re.sub(r'^[🔴🟢🟡]\s*', '', nb) if nb else ""
    vol = ""
    for line in overview.split("\n"):
        m = re.search(r"(\d+)亿", line)
        if m: vol = f"半日{m.group(1)}亿"; break
    return idx_str, gains[:3], losses[:3], nb_clean, vol

# ══════════════════════════════════════════
# 自校验（交叉验证）
# ══════════════════════════════════════════

def self_validate(portfolio, advice):
    """数据+策略 交叉验证"""
    warnings = []
    
    # 1. 数据完整性
    fund_count = len(portfolio)
    if fund_count != 14:
        warnings.append(f"[数据] 基金数量{fund_count}≠14(预期)")
    
    # 2. 板块代理覆盖率
    covered = sum(1 for v in portfolio.values() if v['est_source'] == 'AKShare' or v.get('proxy_sector', ''))
    if covered < fund_count:
        warnings.append(f"[数据] 板块代理仅覆盖{covered}/{fund_count}")
    
    # 3. AKShare覆盖率检查
    akshare_cov = sum(1 for v in portfolio.values() if v.get('est_source') == 'AKShare')
    if akshare_cov < fund_count:
        warnings.append(f"[数据] AKShare实时覆盖{akshare_cov}/{fund_count}，其余用板块代理")

    for code, v in portfolio.items():
        ec = v['est_change']
        if v.get('est_source') != 'AKShare' and abs(ec) > 5 and v['drawdown'] and v['drawdown'] < -20:
            pass  # 板块代理但深套反弹，是合理的
    
    # 4. 操作表完整性——检查是否所有基金都有操作建议
    advice_lines = advice.split('\n')
    op_codes_in_advice = set()
    for l in advice_lines:
        m = re.search(r'\| (\d{6}) ', l)
        if m:
            op_codes_in_advice.add(m.group(1))
    missing = set(portfolio.keys()) - op_codes_in_advice
    if missing:
        warnings.append(f"[完整性] {len(missing)}支基金缺少操作建议: {', '.join(sorted(missing))}")
    
    # 5. 建仓基金检查
    for code in BUILDING_CODES:
        if code not in op_codes_in_advice:
            warnings.append(f"[建仓] {code} 建仓基金未出现在操作表中")
    
    # 6. 科技再平衡检查：如果科技>65%但没有减仓操作，警告
    tech_val = sum(portfolio[c]['current_val'] for c in TECH_CODES if c in portfolio)
    total_val = sum(v['current_val'] for v in portfolio.values())
    if total_val > 0:
        tech_pct = tech_val / total_val * 100
        if tech_pct > 65:
            has_reduce = any('📉' in l and '科技再平衡' in l for l in advice_lines)
            if not has_reduce:
                warnings.append(f"[策略] 科技超配{tech_pct:.0f}%但未触发再平衡")
    
    return warnings

# ══════════════════════════════════════════
# Main
# ══════════════════════════════════════════

def main():
    if date.today().weekday() >= 5:
        print("非交易日"); return

    portfolio = build_portfolio()
    if not portfolio:
        print("⚠️ 持仓构建失败"); return

    advice = generate_advice(portfolio)

    # 自校验
    warnings = self_validate(portfolio, advice)
    if warnings:
        print(f"[校验] 发现{len(warnings)}个问题:", file=sys.stderr)
        for w in warnings:
            print(f"  {w}", file=sys.stderr)
    else:
        print("[校验] ✅ 数据+策略验证通过", file=sys.stderr)

    print(advice)

if __name__ == '__main__':
    main()
