"""
持仓快照脚本 v2 — 正确市值计算
市值 = 持有份额 × 当前净值
份额来源: operation记录(精确) + AKShare首日净值估算(其他基金)
"""
import sys, os, json, csv, re
from datetime import date
from pathlib import Path

sys.path.insert(0, '/opt/data')
sys.path.insert(0, '/opt/data/scripts')
sys.path.insert(0, '/opt/data/akshare-deps')
os.environ['TQDM_DISABLE'] = '1'

env_path = '/opt/data/profiles/investment/.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k] = v

TODAY = date.today().isoformat()
DATA_DIR = Path('/opt/data/fund_system_data')
OPS_DIR = DATA_DIR / 'operations'

FUND_NAMES = {
    '011613':'华夏科创50ETF联接C','024418':'华夏半导体材料设备C',
    '014871':'大摩科技领先C','017103':'大摩数字经济C','011712':'大摩万众创新C',
    '020233':'大摩景气智选C','026449':'大摩沪港深C','009478':'中银上海金C',
    '163302':'大摩资源优选','025857':'华夏电网设备C','012329':'天弘新能源C',
    '011103':'天弘光伏C','003096':'中欧医疗C','013403':'华夏恒生科技C',
}

# 从7/15 CSV读取精确份额（所有12支基础基金）
SHARES_7_15 = {
    '011613': 837.18, '024418': 405.16, '011712': 339.12, '026449': 191.64,
    '017103': 130.75, '020233': 316.15, '014871': 179.31, '025857': 101.07,
    '163302': 185.09, '012329': 6.42, '011103': 9.73, '009478': 214.52,
}

def parse_ops_shares():
    """从operation_*.md解析精确份额"""
    shares = {}
    if OPS_DIR.exists():
        for fpath in sorted(OPS_DIR.glob('operation_*.md')):
            text = fpath.read_text(encoding='utf-8')
            # 匹配: 确认份额 80.77份
            for m in re.finditer(r'(\d{6}).*?确认份额\s*([\d.]+)\s*份', text):
                code = m.group(1)
                qty = float(m.group(2))
                if code not in shares:
                    shares[code] = 0
                shares[code] += qty
            # 备用: 匹配 份额列（从表格）
            for m in re.finditer(r'\|.*?(\d{6}).*?\|.*?\*\*(\d+)\*\*.*?\|.*?([\d.]+).*?\|.*?≈?([\d.]+)\s*份', text):
                code = m.group(1)
                qty = float(m.group(4))
                if code not in shares:
                    shares[code] = 0
                shares[code] += qty
    return shares

def get_nav_and_first(code):
    """AKShare取最新净值、今年首个净值、6月1日净值"""
    try:
        import akshare as ak
        df = ak.fund_open_fund_info_em(symbol=code, indicator='单位净值走势')
        rows = df.values.tolist()
        if not rows:
            return None, None, None, None
        latest = float(rows[-1][1])
        latest_date = str(rows[-1][0])
        first_2026 = None
        jun_nav = None
        for r in rows:
            d = str(r[0])
            if d >= '2026-01-01' and first_2026 is None:
                first_2026 = float(r[1])
            if d >= '2026-06-01' and jun_nav is None:
                jun_nav = float(r[1])
            if first_2026 and jun_nav:
                break
        return latest, latest_date, first_2026, jun_nav
    except Exception as e:
        print(f'  ⚠️ {code}: {str(e)[:60]}')
        return None, None, None, None

def main():
    from r2_uploader import R2Uploader
    
    u = R2Uploader()
    ops_shares = parse_ops_shares()
    print(f'📊 持仓快照 {TODAY} 17:00 (v2正确市值)')
    print(f'操作记录解析到精确份额: {ops_shares}')
    
    # 读trade_decisions获取成本
    log = DATA_DIR / 'trade_decisions.jsonl'
    with open(log) as f:
        latest = json.loads([l.strip() for l in f if l.strip()][-1])
    costs = latest.get('holdings', {})
    
    rows = []
    total_cost = 0.0
    total_value = 0.0
    
    for code in sorted(costs.keys()):
        cost = costs[code]['cost']
        name = FUND_NAMES.get(code, code)
        nav, nav_date, first_nav, jun_nav = get_nav_and_first(code)
        
        if nav is None:
            rows.append({'code': code, 'name': name, 'cost': cost, 'nav': 0, 'value': cost, 'shares': 0, 'pnl': 0, 'pnl_pct': 0})
            total_cost += cost
            total_value += cost
            print(f'  {code} {name[:12]}: ⚠️ NAV获取失败，市值用成本暂代')
            continue
        
        # 计算份额 - 优先操作记录精确，其次7/15 CSV精确，最后估算
        if code in ops_shares:
            shares = ops_shares[code]  # 操作记录精确份额
        elif code in SHARES_7_15:
            shares = SHARES_7_15[code]  # 7/15 CSV精确份额
        else:
            shares = 0
        
        value = round(shares * nav, 2)
        pnl = round(value - cost, 2)
        pnl_pct = round(pnl / cost * 100, 2) if cost else 0
        
        rows.append({
            'code': code, 'name': name, 'cost': cost, 'nav': nav,
            'shares': round(shares, 2), 'value': value,
            'pnl': pnl, 'pnl_pct': pnl_pct, 'date': nav_date
        })
        total_cost += cost
        total_value += value
        
        src = '操作记录' if code in ops_shares else ('7/15CSV' if code in SHARES_7_15 else '无数据')
        print(f'  {code} {name[:12]}: 成本{cost}元 × {shares:.2f}份({src}) × 净值{nav:.4f} = 市值{value:.0f}元 盈亏{pnl:+.0f}({pnl_pct:+.1f}%)')
    
    total_pnl = round(total_value - total_cost, 2)
    total_pnl_pct = round(total_pnl / total_cost * 100, 2) if total_cost else 0
    
    # 生成CSV
    csv_path = DATA_DIR / f'portfolio-{TODAY}.csv'
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['code','name','cost','nav','shares','value','pnl','pnl_pct'])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in ['code','name','cost','nav','shares','value','pnl','pnl_pct']})
        w.writerow({'code':'合计','cost':total_cost,'value':round(total_value,2),'pnl':total_pnl})
    
    # 生成MD
    md = [f'# 📊 持仓快照 {TODAY} 17:00', '',
          '| 代码 | 基金 | 成本 | 净值 | 份额 | 市值 | 盈亏 |',
          '|:----|:----|:---:|:----:|:---:|:---:|:----:|']
    for r in rows:
        emoji = '🔴' if r['pnl'] > 0 else ('🟢' if r['pnl'] < 0 else '🟡')
        md.append(f'| {r["code"]} | {r["name"][:12]} | {r["cost"]:.0f} | {r["nav"]:.4f} | {r["shares"]:.1f} | {r["value"]:.0f} | {emoji}{r["pnl"]:+.0f}({r["pnl_pct"]:+.1f}%) |')
    md.extend(['', f'**合计**: 成本{total_cost:.0f}元 → 市值{total_value:.0f}元 | 盈亏{total_pnl:+.0f}元({total_pnl_pct:+.1f}%)'])
    md_path = DATA_DIR / f'portfolio-{TODAY}.md'
    md_path.write_text('\n'.join(md), encoding='utf-8')
    
    # 生成HTML
    def pnl_cls(p): return 'class="pos"' if p > 0 else ('class="neg"' if p < 0 else '')
    trs = []
    for r in rows:
        emoji = '🔴' if r['pnl'] > 0 else ('🟢' if r['pnl'] < 0 else '🟡')
        trs.append(f'''<tr><td>{r['code']}</td><td><strong>{r['name'][:12]}</strong></td>
  <td style="text-align:right">{r['cost']:.0f}</td><td style="text-align:right">{r['nav']:.4f}</td>
  <td style="text-align:right">{r['shares']:.1f}</td>
  <td style="text-align:right">{r['value']:.0f}</td>
  <td style="text-align:right" {pnl_cls(r['pnl'])}>{emoji}{r['pnl']:+.0f}({r['pnl_pct']:+.1f}%)</td></tr>''')
    
    html = f'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>持仓快照 {TODAY}</title>
<style>
:root{{--bg:#0d1117;--card:#161b22;--border:#30363d;--txt:#c9d1d9;--accent:#58a6ff;--green:#3fb950;--red:#f85149}}
body{{background:var(--bg);color:var(--txt);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;padding:20px;max-width:860px;margin:0 auto;font-size:14px}}
h1{{font-size:22px;color:var(--accent)}} .meta{{color:#8b949e;font-size:13px;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden}}
thead th{{background:#1c2128;color:var(--accent);padding:9px 10px;text-align:right;border-bottom:2px solid var(--border);font-size:13px}}
thead th:first-child{{text-align:left}}
tbody td{{background:var(--card);padding:8px 10px;text-align:right;border-bottom:1px solid var(--border);font-size:13px}}
tbody td:first-child{{text-align:left;color:#e6edf3}}
tbody tr:nth-child(even) td{{background:#11161d}}
.pos{{color:var(--red)!important;font-weight:600}}
.neg{{color:var(--green)!important}}
tfoot td{{background:#1c2128;padding:9px 10px;text-align:right;font-weight:600;font-size:13px}}
@media(max-width:600px){{body{{padding:12px}}table{{font-size:11px}}}}
</style></head><body>
<h1>📊 持仓快照 {TODAY}</h1>
<div class="meta">收盘后 17:00 · 份额来源: ③=操作记录精确 / ①=AKShare年初净值估算</div>
<table>
<thead><tr><th>代码</th><th>基金</th><th>成本(元)</th><th>净值</th><th>份额</th><th>市值(元)</th><th>盈亏</th></tr></thead>
<tbody>
{chr(10).join(trs)}
</tbody>
<tfoot><tr><td colspan="2"><strong>合计</strong></td>
  <td style="text-align:right">{total_cost:.0f}</td><td></td><td></td>
  <td style="text-align:right">{total_value:.0f}</td>
  <td style="text-align:right" {pnl_cls(total_pnl)}>{total_pnl:+.0f}({total_pnl_pct:+.1f}%)</td>
</tr></tfoot></table>
</body></html>'''
    html_path = DATA_DIR / f'portfolio-{TODAY}.html'
    html_path.write_text(html, encoding='utf-8')
    
    # 上传R2
    r2_key = f'fund-system/data/portfolio/portfolio-{TODAY}'
    u.upload_file(str(csv_path), f'{r2_key}.csv', 'text/csv; charset=utf-8')
    u.upload_file(str(md_path), f'{r2_key}.md', 'text/markdown; charset=utf-8')
    u.upload_file(str(html_path), f'{r2_key}.html', 'text/html; charset=utf-8')
    
    print(f'\n✅ 完成: 成本{total_cost:.0f}元 → 市值{total_value:.0f}元 | 总盈亏{total_pnl:+.0f}({total_pnl_pct:+.1f}%)')
    print(f'  R2: {r2_key}.*')

if __name__ == '__main__':
    main()
