#!/opt/data/.venv/bin/python3
"""generate_dashboard_json.py — 聚合数据 → dashboard.json → R2

运行:
  /opt/data/.venv/bin/python3 scripts/generate_dashboard_json.py

输出:
  R2 fund-system/dashboard.json (每交易日4h更新)
"""

import sys, os, json, csv, glob, subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

HERMES_HOME = '/opt/data'
SEED_PATH = os.path.join(HERMES_HOME, 'fund_system_data', 'seed_portfolio.json')
SNAPSHOTS_PATH = os.path.join(HERMES_HOME, 'fund_system_data', 'daily-snapshots.jsonl')
OPERATIONS_DIR = os.path.join(HERMES_HOME, 'fund_system_data', 'operations')
CLOSING_PATH = os.path.join(HERMES_HOME, 'fund_system_data', 'closing-reviews.jsonl')
MORNING_PATH = os.path.join(HERMES_HOME, 'fund_system_data', 'morning-briefs.jsonl')
NOON_PATH = os.path.join(HERMES_HOME, 'fund_system_data', 'noon-briefs.jsonl')

# 行业分组
SECTOR_MAP = {
    '003096': '医疗',
    '013403': '恒生科技',
    '011613': '科技', '024418': '科技', '014871': '科技',
    '017103': '科技', '011712': '科技', '020233': '科技', '026449': '科技',
    '163302': '周期', '025857': '周期',
    '009478': '黄金',
    '012329': '新能源', '011103': '新能源',
}
BUILDING_FUNDS = {'003096': {'target': 370}, '013403': {'target': 300}}


def safe_float(v, default=0.0):
    if v is None: return default
    try: return float(v)
    except: return default


def load_portfolio():
    """从最新持仓CSV加载持仓（包含实际份额）"""
    csvs = sorted(glob.glob(os.path.join(HERMES_HOME, 'fund_system_data', 'portfolio-*.csv')), reverse=True)
    if not csvs:
        return load_seed_portfolio()
    result = {}
    with open(csvs[0]) as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get('code', '')
            try:
                result[code] = {
                    'shares': safe_float(row.get('shares', 0)),
                    'cost': safe_float(row.get('cost', 0)),
                    'nav_at_record': safe_float(row.get('nav', 0)),
                }
            except: continue
    return result


def load_jsonl(path, max_lines=1):
    if not os.path.exists(path): return []
    with open(path) as f:
        lines = f.readlines()
    result = []
    for line in lines[-max_lines:]:
        line = line.strip()
        if line: result.append(json.loads(line))
    return result


def collect_portfolio(portfolio):
    """采集基金净值并计算实际盈亏"""
    from fund_tools import FUND_CODES
    from fund_source_akshare import get_fund_history

    now = datetime.now(ZoneInfo('Asia/Shanghai'))
    trading = 570 <= now.hour * 60 + now.minute <= 900

    results = []
    total_cost = total_value = tech_cost = tech_value = 0
    tech_sectors = {'科技', '半导体', '计算机', '电子', '信创'}

    for code in FUND_CODES:
        try:
            pos = portfolio.get(code, {})
            shares = pos.get('shares', 0)
            tc = pos.get('cost', 0)

            if trading:
                from fund_tools import get_fund_value
                data = get_fund_value(code)
                nav = safe_float(data.get('estimated_nav') or data.get('nav', 0)) if data else 0
            else:
                hist = get_fund_history(code, days=1)
                nav = hist[0]['nav'] if hist else 0

            est_value = nav * shares
            profit_amount = est_value - tc
            profit_pct = (profit_amount / tc * 100) if tc else 0

            entry = {
                'code': code, 'name': FUND_CODES[code],
                'cost': round(tc, 2), 'nav': round(nav, 4),
                'shares': round(shares, 2),
                'estimated_value': round(est_value, 2),
                'profit_pct': round(profit_pct, 2),
                'profit_amount': round(profit_amount, 2),
                'sector': SECTOR_MAP.get(code, '其他'),
            }
            results.append(entry)
            total_cost += tc
            total_value += est_value
            if SECTOR_MAP.get(code, '') in tech_sectors:
                tech_cost += tc
                tech_value += est_value
            print(f'  ✅ {FUND_CODES[code][:20]:20s} ×{shares:>6.1f}份 | NAV:{nav:.4f} | ¥{est_value:>7.2f} ({profit_pct:+.1f}%)')
        except Exception as e:
            print(f'  ⚠️ {code} 失败: {e}')

    # 建仓进度
    building = []
    for code, plan in BUILDING_FUNDS.items():
        cur = next((f['estimated_value'] for f in results if f['code'] == code), 0)
        building.append({
            'code': code,
            'name': next((f['name'] for f in results if f['code'] == code), ''),
            'current': round(cur, 2),
            'target': plan['target'],
            'progress_pct': round(cur / plan['target'] * 100, 1) if plan['target'] else 0,
        })

    tech_pct = (tech_cost / total_cost * 100) if total_cost else 0
    deviation_pct = round(tech_pct - 65, 1)

    return {
        'holdings': results,
        'total_cost': round(total_cost, 2),
        'total_value': round(total_value, 2),
        'total_profit_pct': round((total_value - total_cost) / total_cost * 100, 2) if total_cost else 0,
        'tech_deviation_pct': deviation_pct,
        'building_funds': building,
    }


def collect_indices():
    from fund_tools import get_all_quotes
    data = get_all_quotes()
    return [{'code': k, 'name': v.get('name',''), 'price': safe_float(v.get('price',0)),
             'change_pct': safe_float(v.get('change_pct',0))} for k, v in (data or {}).items()]


def collect_sectors():
    result = {'rankings': [], 'fund_flow': []}
    try:
        from fund_tools import get_sector_rankings_em
        rank = get_sector_rankings_em()
        if rank:
            sr = sorted(rank.items(), key=lambda x: safe_float(x[1].get('change_pct',0)), reverse=True)
            result['rankings'] = [{'name': n, 'change_pct': safe_float(d.get('change_pct',0))} for n,d in sr[:20]]
    except Exception as e: print(f'  ⚠️ 板块涨跌: {e}')

    try:
        from fund_tools import get_sector_fund_flow_em
        flow = get_sector_fund_flow_em()
        if flow:
            sf = sorted(flow.items(), key=lambda x: abs(safe_float(x[1].get('net_inflow_yi',0))), reverse=True)
            result['fund_flow'] = [{'name': n, 'change_pct': safe_float(d.get('change_pct',0)),
                                     'net_inflow_yi': safe_float(d.get('net_inflow_yi',0))} for n,d in sf[:10]]
    except Exception as e: print(f'  ⚠️ 资金流: {e}')
    return result


def collect_market():
    from fund_tools import get_market_overview
    mv = get_market_overview()
    return {'advance': mv.get('rise_count',0), 'decline': mv.get('fall_count',0),
            'flat': mv.get('flat_count',0), 'total': mv.get('rise_count',0) + mv.get('fall_count',0) + mv.get('flat_count',0)}


def collect_analysis():
    reports = []
    for path, rtype in [(MORNING_PATH, 'morning'), (NOON_PATH, 'noon'), (CLOSING_PATH, 'closing')]:
        for item in load_jsonl(path, 1):
            reports.append({'type': rtype, 'date': item.get('date',''),
                            'summary': (item.get('summary') or item.get('market_condition') or '')[:200]})
    return reports


def collect_operations():
    ops = []
    if os.path.isdir(OPERATIONS_DIR):
        files = sorted([f for f in os.listdir(OPERATIONS_DIR) if f.endswith('.md') and f != 'README.md'], reverse=True)[:5]
        import re
        for fn in files:
            m = re.match(r'operation_(\d{4}-\d{2}-\d{2})', fn)
            if m: ops.append({'date': m.group(1), 'file': fn})
    return ops


def generate_dashboard():
    print('📊 生成 Dashboard JSON...')
    seed = load_portfolio()
    print(f'📋 持仓: {len(seed)} 支')

    print(f'\n🔍 采集...')
    ts = datetime.now(ZoneInfo('Asia/Shanghai'))

    dashboard = {
        'date': ts.strftime('%Y-%m-%d'),
        'time': ts.strftime('%H:%M'),
        'updated_at': ts.isoformat(),
        'indices': collect_indices(),
        'portfolio': collect_portfolio(seed),
        'sectors': collect_sectors(),
        'market_overview': collect_market(),
        'latest_analysis': collect_analysis(),
        'operations': collect_operations(),
    }

    pf = dashboard['portfolio']
    mv = dashboard['market_overview']
    print(f'\n📊: {len(dashboard["indices"])}指数 | {len(pf["holdings"])}基金 | '
          f'涨{mv.get("advance",0)}/跌{mv.get("decline",0)}')
    print(f'   组合: ¥{pf["total_value"]:,.0f} ({pf["total_profit_pct"]:+.2f}%) | 偏离度: {pf["tech_deviation_pct"]:+.1f}%')

    # 本地写入
    local_path = os.path.join(HERMES_HOME, 'fund_system_data', 'dashboard.json')
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    print(f'\n💾 {local_path} ({os.path.getsize(local_path)/1024:.0f}KB)')

    # R2上传
    print(f'\n☁️ R2...')
    env = os.environ.copy()
    env_path = os.path.join(HERMES_HOME, 'profiles', 'investment', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('R2_') and '=' in line:
                    k, v = line.split('=', 1)
                    if k not in env: env[k] = v
    result = subprocess.run(
        [sys.executable, os.path.join(HERMES_HOME, 'r2_uploader.py'),
         local_path, 'fund-system/dashboard.json', 'application/json; charset=utf-8'],
        capture_output=True, text=True, timeout=30, env=env)
    print(f'   {"✅" if result.returncode == 0 else "❌"} {result.stdout.strip()[:200] if result.returncode == 0 else result.stderr[:200]}')

    print(f'\n✅ 完成')
    return dashboard


if __name__ == '__main__':
    generate_dashboard()
