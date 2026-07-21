#!/usr/bin/env python3
"""
全量历史数据稳健性验证
测试AKShare历史净值/指数数据的完整性、连续性、合理性
不依赖pandas，仅用标准库
"""
import sys, os, json
from datetime import date, datetime, timedelta

sys.path.insert(0, '/opt/data/scripts')
_AKSHARE_DEPS = '/opt/data/akshare-deps'
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)
os.environ['TQDM_DISABLE'] = '1'
os.environ['AKSHARE_RAISE_ERR'] = 'False'

try:
    import akshare as ak
    HAS_AK = True
except ImportError:
    HAS_AK = False

def safe_float(v, default=0.0):
    if v is None: return default
    try: return float(str(v).replace('%', '').replace(',', ''))
    except: return default

def parse_date(d):
    """统一解析日期为 date 对象"""
    if isinstance(d, date):
        return d
    s = str(d)[:10]
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))

TODAY = date.today()
YEAR_START = date(TODAY.year, 1, 1)

FUND_CODES = {
    '009478': '中银上海金ETF联接C', '011613': '华夏科创50ETF联接C',
    '024418': '华夏半导体材料ETF联接C', '026449': '大摩沪港深科技混合C',
    '014871': '大摩科技领先混合C', '020233': '大摩景气智选混合C',
    '017103': '大摩数字经济混合C', '011712': '大摩万众创新混合C',
    '163302': '大摩资源优选混合LOF', '025857': '华夏电网设备ETF联接C',
    '012329': '天弘新能源指数增强C', '011103': '天弘中证光伏C',
    '003096': '中欧医疗健康混合C', '013403': '华夏恒生科技联接C',
}

INDEX_CODES = {
    '上证指数': 'sh000001', '沪深300': 'sh000300',
    '科创50': 'sh000688', '创业板指': 'sz399006',
    '上证50': 'sh000016',
    '中证医疗': 'sz399989', '中证半导体': 'sz399967',
    '中证白酒': 'sz399997', '中证消费': 'sz399932',
}

passed, failed, errors = 0, 0, []

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        # print(f"  ✅ {name}")
    else:
        failed += 1
        msg = f"{name}: {detail}" if detail else name
        errors.append(msg)
        print(f"  ❌ {msg}")

def check_result(name, cond, detail=""):
    """允许带emoji的check"""
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        errors.append(f"{name}: {detail}" if detail else name)

# ======================================================
# 第一部分: 基金历史净值
# ======================================================
print("=" * 60)
print("📊 第一部分: 基金历史净值验证 (14支)")
print("=" * 60)

fund_stats = {}
for code, name in FUND_CODES.items():
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is None or df.empty:
            errors.append(f"{name}: 返回空")
            failed += 1
            print(f"  ❌ {name}: 返回空")
            continue
        
        rows = df.values
        if len(rows) == 0:
            errors.append(f"{name}: 0行")
            failed += 1; print(f"  ❌ {name}: 0行"); continue
        
        # 提取数据
        nav_dates = []
        nav_values = []
        for r in rows:
            d = r[0] if '净值日期' in df.columns else (r[1] if len(r) > 1 else str(r[0])[:10])
            nd = parse_date(d)
            nv = safe_float(r[1]) if '单位净值' in df.columns else safe_float(r[2] if len(r) > 2 else r[1])
            nav_dates.append(nd)
            nav_values.append(nv)
        
        n = len(nav_dates)
        if n < 10:
            errors.append(f"{name}: 数据太少({n}天)")
            failed += 1; print(f"  ❌ {name}: 仅{n}天数据"); continue
        
        # 基础统计
        nav_min = min(nav_values)
        nav_max = max(nav_values)
        first_date = nav_dates[0]
        last_date = nav_dates[-1]
        
        # 日期连续性检查
        gaps = []
        for i in range(1, n):
            diff = (nav_dates[i] - nav_dates[i-1]).days
            if diff > 7:
                gaps.append((nav_dates[i-1], nav_dates[i], diff))
        
        # 异常涨跌检测: 相邻净值变动>15%
        extremes = []
        for i in range(1, n):
            if nav_values[i-1] > 0:
                chg = (nav_values[i] / nav_values[i-1] - 1) * 100
                if abs(chg) > 15:
                    extremes.append((nav_dates[i], chg))
        
        # YTD计算
        ytd_navs = [(d, v) for d, v in zip(nav_dates, nav_values) if d >= YEAR_START]
        if len(ytd_navs) >= 2:
            ytd = round((ytd_navs[-1][1] / ytd_navs[0][1] - 1) * 100, 2)
        else:
            ytd = None
        
        # 累计收益
        if nav_values[0] > 0:
            total_ret = round((nav_values[-1] / nav_values[0] - 1) * 100, 2)
        else:
            total_ret = None
        
        issues = []
        if len(extremes) > 0:
            issues.append(f"异常涨跌{len(extremes)}次")
        if len(gaps) > 0:
            issues.append(f"缺口{len(gaps)}处(最长{gaps[-1][2]}天)")
        if nav_min <= 0:
            issues.append("净值≤0")
        if n < 30:
            issues.append("天数偏少")
        
        fund_stats[code] = {
            'name': name, 'n_days': n, 'nav_range': f"{nav_min:.4f}~{nav_max:.4f}",
            'date_range': f"{first_date}~{last_date}", 'ytd': ytd,
            'total_ret': total_ret, 'issues': issues,
        }
        
        status = "✅" if not issues else "⚠️"
        detail = f"{n:>4d}天 | YTD={ytd:+.2f}%" if ytd else f"{n:>4d}天"
        print(f"  {status} {name:30s} {detail}")
        if issues:
            for iss in issues:
                print(f"          ⚠️ {iss}")
        
    except Exception as e:
        errors.append(f"{name}({code}): {type(e).__name__}")
        failed += 1
        print(f"  ❌ {name}: {type(e).__name__}")

# ======================================================
# 第二部分: 指数历史数据
# ======================================================
print()
print("=" * 60)
print("📈 第二部分: 指数历史K线验证")
print("=" * 60)

index_stats = {}
for name, symbol in INDEX_CODES.items():
    try:
        df = ak.stock_zh_index_daily(symbol=symbol)
        if df is None or df.empty:
            errors.append(f"指数{name}: 空")
            failed += 1; print(f"  ❌ {name}: 空"); continue
        
        rows = df.values
        n = len(rows)
        closes = [safe_float(r[3]) for r in rows if len(r) > 3]
        
        if n < 10:
            failed += 1; errors.append(f"{name}: 数据太少({n})")
            print(f"  ❌ {name}: 仅{n}行"); continue
        
        # 日期范围
        first_d = parse_date(rows[0][0])
        last_d = parse_date(rows[-1][0])
        
        # YTD
        ytd_closes = [c for c, r in zip(closes, rows) if parse_date(r[0]) >= YEAR_START]
        if len(ytd_closes) >= 2:
            ytd = round((ytd_closes[-1] / ytd_closes[0] - 1) * 100, 2)
        else:
            ytd = None
        
        # 异常日: 单日涨跌>10%
        extremes = []
        for i in range(1, len(closes)):
            if closes[i-1] > 0:
                chg = (closes[i] / closes[i-1] - 1) * 100
                if abs(chg) > 10:
                    extremes.append((parse_date(rows[i][0]), round(chg, 2)))
        
        index_stats[name] = {
            'n_days': n, 'range': f"{first_d}~{last_d}",
            'close_range': f"{min(closes):.0f}~{max(closes):.0f}",
            'ytd': ytd, 'extremes': len(extremes),
        }
        
        ytd_str = f"YTD={ytd:+.2f}%" if ytd else ""
        ext_str = f" | 异常{len(extremes)}天" if extremes else ""
        print(f"  ✅ {name:12s} {n:>4d}天 | 收盘{min(closes):.0f}~{max(closes):.0f} | {ytd_str}{ext_str}")
        
    except Exception as e:
        failed += 1; errors.append(f"指数{name}: {type(e).__name__}")
        print(f"  ❌ {name}: {type(e).__name__}")

# ======================================================
# 汇总报告
# ======================================================
print()
print("=" * 60)
print("📋 历史数据验证报告")
print("=" * 60)
print()
print(f"  基金净值: {len(fund_stats)}/{len(FUND_CODES)} 拉取成功")
print(f"  指数数据: {len(index_stats)}/{len(INDEX_CODES)} 拉取成功")
print()
print("✅ 通过测试:", passed)
print("❌ 失败测试:", failed)
print()

if errors:
    print("错误详情:")
    for e in errors:
        print(f"  {e}")
    print()

# YTD排序
print("📈 YTD表现 (基金):")
ytd_list = [(s['ytd'], s['name']) for s in fund_stats.values() if s['ytd'] is not None]
ytd_list.sort(reverse=True)
for y, n in ytd_list:
    bar = '🔴' if y > 0 else '🟢'
    print(f"  {bar} {n:30s} {y:+.2f}%")

print()
print("📈 YTD表现 (指数):")
ytd_idx = [(s['ytd'], n) for n, s in index_stats.items() if s['ytd'] is not None]
ytd_idx.sort(reverse=True)
for y, n in ytd_idx:
    bar = '🔴' if y > 0 else '🟢'
    print(f"  {bar} {n:12s} {y:+.2f}%")

print()
print("⚠️ 数据问题汇总:")
issue_count = 0
for code, s in fund_stats.items():
    if s['issues']:
        print(f"  ⚠️ {s['name']}: {', '.join(s['issues'])}")
        issue_count += 1
if issue_count == 0:
    print("  ✅ 无数据完整性问题")

# 天数排序
print()
print("📊 数据量排序(天):")
days_list = [(s['n_days'], s['name'], s['date_range']) for s in fund_stats.values()]
days_list.sort()
for nd, nm, dr in days_list:
    print(f"  {nd:>4d}天  {nm:30s}  {dr}")

print()
print("✅" if failed == 0 else "❌", end=" ")
print(f"总结果: {passed}通过/{failed}失败/{len(errors)}错误")
