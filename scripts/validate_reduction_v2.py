#!/usr/bin/env python3
"""全量验证 — 腾讯API拉6个月数据，绕开东财限流"""
import sys, os, json, time, subprocess
from pathlib import Path
from datetime import date

sys.path.insert(0, '/opt/data/scripts')
from log_daily_decisions import PORTFOLIO_COST

CACHE = Path("/opt/data/fund_system_data/cache")
CACHE.mkdir(parents=True, exist_ok=True)

# 腾讯代码映射（指数）
TENCENT_INDICES = {
    'sh000688': '科创50', 'sz399967': '中证半导体', 'sz399989': '中证医疗',
    'sz399997': '中证白酒', 'sz399932': '中证消费', 'sh000300': '沪深300',
}

def fetch_tencent_kline(code, start='2026-01-15', end='2026-07-15'):
    """拉腾讯历史日K"""
    cf = CACHE / f"t_kline_{code}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,{start},{end},250,qfq"
    for attempt in range(3):
        try:
            r = subprocess.run(
                ["docker", "exec", "hermes-main", "curl", "-s", "--max-time", "15", url,
                 "-H", "User-Agent: Mozilla/5.0", "-H", "Referer: http://gu.qq.com/"],
                capture_output=True, timeout=20
            )
            txt = r.stdout.decode('utf-8', errors='replace')
            d = json.loads(txt)
            data = d.get('data', {})
            # 遍历找K线数据
            result = None
            for code_key, code_data in data.items():
                if isinstance(code_data, dict):
                    for k, v in code_data.items():
                        if isinstance(v, dict) and 'day' in v:
                            days = v['day']
                            result = [{'date': x[0], 'close': float(x[2])} for x in days]
                            break
                if result:
                    break
            if result:
                cf.write_text(json.dumps(result))
                time.sleep(2)
                return result
        except Exception:
            time.sleep(3)
    return []

def fetch_fund_via_tencent(code):
    """腾讯基金实时估值（替代东财）"""
    url = f"http://qt.gtimg.cn/q=f_{code}"
    r = subprocess.run(
        ["docker", "exec", "hermes-main", "curl", "-s", "--max-time", "10", url],
        capture_output=True, timeout=15
    )
    txt = r.stdout.decode('gbk', errors='replace')
    # 腾讯基金格式: v_f_xxxx="代码~名称~..."

    m = re.search(r'v_f_(\w+)="([^"]+)"', txt)
    if m:
        fields = m.group(2).split('~')
        if len(fields) > 10:
            return {
                'name': fields[1],
                'nav': fields[4],
                'est': fields[5],
                'est_chg': fields[6],
            }
    return None

def calc_metrics(data):
    if len(data) < 10:
        return None
    first = data[0]['close']
    last = data[-1]['close']
    ytd = (last / first - 1) * 100
    peak = 0; mdd = 0
    for d in data:
        if d['close'] > peak:
            peak = d['close']
        dd = (d['close'] - peak) / peak * 100
        if dd < mdd:
            mdd = dd
    # 近20天
    m20_first = data[-20]['close'] if len(data) >= 20 else first
    m20 = (last / m20_first - 1) * 100
    return {'ytd': ytd, 'mdd': mdd, 'm20': m20, 'days': len(data)}

def main():
    import re
    print("="*60)
    print("减仓策略全量验证 — 腾讯API 6个月数据")
    print("="*60)
    
    # ══ 1. 持仓结构 ══
    print("\n【一、当前持仓结构】")
    group_totals = {}
    total = 0
    for code, info in PORTFOLIO_COST.items():
        g = info['group']
        group_totals.setdefault(g, {'total': 0, 'count': 0})
        group_totals[g]['total'] += info['cost_total']
        group_totals[g]['count'] += 1
        total += info['cost_total']
    
    print(f"总市值: {total:.0f}元")
    limits = {'科技/AI': 45, '黄金': 30, '资源/周期': 15, '新能源': 10}
    for g, d in sorted(group_totals.items(), key=lambda x: -x[1]['total']):
        pct = d['total'] / total * 100
        limit = limits.get(g, 15)
        dev = pct - limit
        emoji = '🔴' if dev > 15 else '⚠️' if dev > 5 else '✅'
        print(f"  {g}: {d['count']}支 {d['total']:.0f}元 {pct:.1f}% (上限{limit}%, {emoji}{dev:+.1f}%)")
    
    # ══ 2. 6个月板块轮动 ══
    print("\n【二、近6个月板块轮动（腾讯数据）】")
    print(f"{'板块':<12} {'6月收益':>8} {'近20天':>8} {'最大回撤':>8} {'趋势'}")
    print("-"*50)
    index_metrics = {}
    for sym, name in TENCENT_INDICES.items():
        data = fetch_tencent_kline(sym)
        if data:
            m = calc_metrics(data)
            if m:
                index_metrics[name] = m
                emoji = '🟢' if m['ytd'] > 0 else '🔴'
                trend = '上行' if m['ytd'] > 0 else '下行'
                print(f"  {name:<10} {emoji}{m['ytd']:>+6.1f}% {m['m20']:>+7.1f}% {m['mdd']:>7.1f}% {trend}")
        else:
            print(f"  {name:<10} 数据获取失败")
    
    # ══ 3. 医疗基金用腾讯估值 ══
    print("\n【三、医疗基金当前状态（腾讯实时）】")
    med_funds = {
        '003096': '中欧医疗健康C', '006229': '中欧医疗创新C',
        '012417': '招商国证生物医药C', '012738': '天弘中证创新药C', '012323': '华宝医疗ETF联接C',
    }
    print(f"{'基金':<16} {'实时估值':>8} {'估算涨跌':>8}")
    print("-"*40)
    for code, name in med_funds.items():
        f = fetch_fund_via_tencent(code)
        if f and f.get('est_chg'):
            chg = float(f['est_chg'])
            emoji = '🟢' if chg > 0 else '🔴'
            print(f"  {name:<14} {f.get('est','?'):>6} {emoji}{chg:>+6.2f}%")
        else:
            print(f"  {name:<14} 无实时数据")
        time.sleep(1)
    
    # ══ 4. 科技组持仓（用缓存或重新拉） ══
    print("\n【四、科技组内部重叠（实际季报）】")
    tech_codes = {k: v['name'] for k, v in PORTFOLIO_COST.items() if v['group'] == '科技/AI'}
    all_stocks = {}
    for code, name in tech_codes.items():
        cf = CACHE / f"hold_{code}.json"
        if cf.exists():
            stocks = json.loads(cf.read_text())
            for s in stocks:
                all_stocks.setdefault(s.get('name', ''), []).append(code)
            print(f"  {name}: TOP3={'/'.join([s.get('name','?') for s in stocks[:3]])}")
        else:
            print(f"  {name}: 持仓缓存缺失（需重新拉取）")
    
    overlap = {s: h for s, h in all_stocks.items() if len(h) >= 2}
    print(f"\n  被≥2支持有: {len(overlap)}支")
    for s, h in sorted(overlap.items(), key=lambda x: -len(x[1]))[:8]:
        names = [tech_codes.get(c, c) for c in h]
        print(f"    {s}: {len(h)}支 → {', '.join(names[:3])}")
    
    # ══ 5. 保存结果 ══
    summary = {
        'date': str(date.today()),
        'total_value': total,
        'group_structure': group_totals,
        'index_metrics_6m': index_metrics,
        'tech_overlap_count': len(overlap),
        'tech_fund_count': len(tech_codes),
    }
    (CACHE / "full_validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n✅ 验证完成，结果已缓存")

if __name__ == "__main__":
    import re
    main()
