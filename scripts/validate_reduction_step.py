#!/usr/bin/env python3
"""分步版验证 — 每个数据源独立跑，避免限流"""
import sys, os, json, time, subprocess
from pathlib import Path
from datetime import date, timedelta

CACHE = Path("/opt/data/fund_system_data/cache")
CACHE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, '/opt/data/scripts')
from log_daily_decisions import PORTFOLIO_COST

def akshare_run(code_py, cache_key, timeout=90):
    """在docker内跑AKShare代码，带缓存"""
    cf = CACHE / f"{cache_key}.json"
    if cf.exists():
        return json.loads(cf.read_text())
    
    r = subprocess.run(
        ["docker", "exec", "hermes-main", "python3", "-c", code_py],
        capture_output=True, timeout=timeout
    )
    out = r.stdout.decode('utf-8', errors='replace').strip()
    try:
        data = json.loads(out)
        cf.write_text(json.dumps(data))
        return data
    except:
        return None

def step1_index_trend():
    """拉6个月指数趋势"""
    print("📊 Step1: 拉指数6个月趋势...")
    indices = {
        'sh000688': '科创50', 'sz399967': '中证半导体', 'sz399989': '中证医疗',
        'sz399997': '中证白酒', 'sz399932': '中证消费', 'sh000300': '沪深300',
    }
    result = {}
    for sym, name in indices.items():
        code = f"""import sys, os
os.environ['TQDM_DISABLE']='1'
sys.path.insert(0,'/opt/data/akshare-deps')
import akshare as ak
from datetime import date, timedelta
df=ak.stock_zh_index_daily(symbol='{sym}')
cutoff=date.today()-timedelta(days=186)
df=df[df['date']>=cutoff]
print(json.dumps([{{'date':str(r['date']),'close':float(r['close'])}} for _,r in df.iterrows()]))
"""
        data = akshare_run(code, f"idx_{sym}_6m", 60)
        if data and len(data) >= 10:
            first = data[0]['close']
            last = data[-1]['close']
            ytd = (last/first-1)*100
            peak=0; mdd=0
            for d in data:
                if d['close']>peak: peak=d['close']
                dd=(d['close']-peak)/peak*100
                if dd<mdd: mdd=dd
            result[name] = {'ytd': ytd, 'mdd': mdd, 'days': len(data)}
            print(f"  {name}: 6个月{ytd:+.1f}% 回撤{mdd:.1f}% ({len(data)}天)")
        else:
            print(f"  {name}: 失败")
        time.sleep(3)
    return result

def step2_fund_nav():
    """拉医疗基金6个月净值"""
    print("\n📊 Step2: 拉医疗基金6个月净值...")
    funds = {
        '003096': '中欧医疗健康C', '006229': '中欧医疗创新C',
        '012417': '招商国证生物医药C', '012738': '天弘中证创新药C', '012323': '华宝医疗ETF联接C',
    }
    result = {}
    for code, name in funds.items():
        py = f"""import sys, os
os.environ['TQDM_DISABLE']='1'
sys.path.insert(0,'/opt/data/akshare-deps')
import akshare as ak
from datetime import date, timedelta
df=ak.fund_open_fund_info_em(symbol='{code}',indicator='单位净值走势')
cutoff=date.today()-timedelta(days=186)
rows=df.values.tolist()
res=[]
for r in rows:
    if r[0]>=cutoff and r[1]:
        res.append({{'date':str(r[0]),'nav':float(r[1])}})
print(json.dumps(res))
"""
        data = akshare_run(py, f"nav_{code}_6m", 90)
        if data and len(data) >= 10:
            first = data[0]['nav']
            last = data[-1]['nav']
            m6 = (last/first-1)*100
            m1_first = data[-20]['nav'] if len(data) >= 20 else first
            m1 = (last/m1_first-1)*100
            peak=0; mdd=0
            for d in data:
                if d['nav']>peak: peak=d['nav']
                dd=(d['nav']-peak)/peak*100
                if dd<mdd: mdd=dd
            ftype = '主动' if '中欧' in name else '指数'
            result[code] = {'name': name, 'm6': m6, 'm1': m1, 'mdd': mdd, 'type': ftype}
            print(f"  {name}: 6月{m6:+.1f}% 1月{m1:+.1f}% 回撤{mdd:.1f}% {ftype}")
        else:
            print(f"  {name}: 失败")
        time.sleep(3)
    return result

def step3_holdings():
    """拉科技组持仓（限流友好）"""
    print("\n📊 Step3: 拉科技组持仓（单进程curl）...")
    import re
    tech_codes = {k: v['name'] for k, v in PORTFOLIO_COST.items() if v['group'] == '科技/AI'}
    result = {}
    
    for code, name in tech_codes.items():
        cf = CACHE / f"hold_{code}.json"
        if cf.exists():
            result[code] = json.loads(cf.read_text())
            print(f"  {name}: 缓存命中")
            continue
        
        # 用docker curl，单次请求
        r = subprocess.run(
            ["docker", "exec", "hermes-main", "curl", "-s", "--max-time", "15",
             f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year=&month=",
             "-H", "User-Agent: Mozilla/5.0"],
            capture_output=True, timeout=20
        )
        html = r.stdout.decode('utf-8', errors='replace')
        m = re.search(r'content:"(.*?)",', html, re.DOTALL)
        if m:
            raw = m.group(1).replace('\\r', '').replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            raw = bytes(raw, 'utf-8').decode('unicode_escape')
            stocks = []
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', raw, re.DOTALL)
            for row in rows[1:]:
                cols = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cols]
                if len(clean) >= 3 and clean[0].isdigit():
                    stocks.append({'name': clean[2], 'pct': clean[-2] if len(clean) > 6 else ''})
            result[code] = stocks
            cf.write_text(json.dumps(stocks, ensure_ascii=False))
            top3 = [s['name'] for s in stocks[:3]]
            print(f"  {name}: TOP3={top3}")
        else:
            print(f"  {name}: 限流")
        time.sleep(5)  # 长延迟避免限流
    
    return result

def main():
    print("="*60)
    print("减仓策略全量验证 — 分步执行")
    print("="*60)
    
    idx = step1_index_trend()
    time.sleep(5)
    med = step2_fund_nav()
    time.sleep(5)
    holdings = step3_holdings()
    
    # 重叠分析
    print("\n📊 Step4: 重叠分析...")
    all_stocks = {}
    for code, stocks in holdings.items():
        for s in stocks:
            all_stocks.setdefault(s['name'], []).append(code)
    
    overlap = {s: h for s, h in all_stocks.items() if len(h) >= 2}
    print(f"  被≥2支基金持有: {len(overlap)}支")
    for s, h in sorted(overlap.items(), key=lambda x: -len(x[1]))[:10]:
        names = [PORTFOLIO_COST.get(c, {}).get('name', c) for c in h]
        print(f"    {s}: {len(h)}支 → {names[:3]}")
    
    # 保存综合结果
    summary = {
        'index_trend': idx,
        'medical_funds': med,
        'holdings_overlap': {s: h for s, h in overlap.items()},
        'tech_fund_count': len(holdings),
    }
    (CACHE / "validation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n✅ 验证完成，结果已缓存")

if __name__ == "__main__":
    main()
