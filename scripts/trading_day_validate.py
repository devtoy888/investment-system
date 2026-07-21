#!/usr/bin/env python3
"""
交易日数据源自动验证脚本
在每个交易日自动运行，验证所有数据源的可用性/准确性/新鲜度

运行方式: cronjob(no_agent=true) + 交易日自检
"""

import sys, os, json, time
from datetime import date, datetime
from collections import defaultdict

sys.path.insert(0, '/opt/data/scripts')
_AKSHARE_DEPS = '/opt/data/akshare-deps'
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)
os.environ['TQDM_DISABLE'] = '1'
os.environ['AKSHARE_RAISE_ERR'] = 'False'

import fund_tools as ft
import akshare as ak

TODAY = date.today()
TODAY_STR = TODAY.isoformat()
WEEKDAY = TODAY.weekday()
WEEKDAY_NAMES = ['周一','周二','周三','周四','周五','周六','周日']

results = []
passed = 0
failed = 0
warnings = []

def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        results.append(f"  ✅ {name}")
    else:
        failed += 1
        results.append(f"  ❌ {name}: {detail}")

def section(title):
    results.append(f"\n## {title}")

# ============================
# 第1轮: 环境检测
# ============================
section("第1轮: 交易日环境检测")

is_trading = ft.is_trading_day(TODAY)
check(f"交易日判断: {TODAY_STR}({WEEKDAY_NAMES[WEEKDAY]})", is_trading)
if not is_trading:
    results.append(f"\n⏭️ 非交易日({TODAY_STR})，跳过数值验证，仅做API可达性测试")

# ============================
# 第2轮: 各数据源可达性 + 新鲜度
# ============================
section("第2轮: 数据源可达性与新鲜度")

# 腾讯行情
q = ft.get_tencent_quote('sh000001')
if q:
    check("腾讯行情可达", True)
    stale = q.get('_stale', '?')
    check(f"腾讯行情_stale={stale}", stale == (not is_trading),
          f"交易日应=False, 非交易日应=True, 当前={stale}")
else:
    check("腾讯行情可达", False, "返回None")

# 天天基金
f = ft.get_fund_value('017103')
if f:
    check("天天基金可达", True)
    nav_date = f.get('nav_date', '?')
    is_fresh = (nav_date == TODAY_STR)
    check(f"天天基金净值日期={nav_date}", 
          is_fresh == is_trading,
          f"交易日应=今日, 非交易日应≠今日")
else:
    check("天天基金可达", False)

# 涨跌家数 (验证备援链)
mo = ft.get_market_overview()
if mo:
    rc = mo.get('rise_count')
    fc = mo.get('fall_count')
    has_data = (rc is not None and fc is not None)
    check(f"涨跌家数: 涨={rc} 跌={fc}", has_data)
    if is_trading:
        total = (rc or 0) + (fc or 0)
        check(f"涨跌合计={total} > 100(交易日应有数据)", total > 100, f"合计={total}")
else:
    check("涨跌家数可达", False)

# 行业ETF
sec = ft.get_sector_quotes()
sec_ok = sum(1 for v in sec.values() if v)
check(f"行业ETF {sec_ok}/{len(sec)}", sec_ok >= 8, f"仅{sec_ok}/{len(sec)}")

# 北向资金
nb = ft.get_northbound_flow()
nb_ok = nb and nb.get('total') is not None
nb_source = nb.get('source', '?') if nb else '?'
check(f"北向资金({nb_source})", nb_ok)

# 外盘
ov = ft.get_overnight_quotes()
ov_ok = sum(1 for v in ov.values() if v and '_stale' in v)
check(f"外盘 {ov_ok}/{len(ov)} 含_stale", ov_ok == len(ov),
      f"仅{ov_ok}/{len(ov)}有_stale")
if ov_ok > 0:
    sample = next((v for v in ov.values() if v), {})
    check(f"外盘_stale类型正确", isinstance(sample.get('_stale'), bool))

# ============================
# 第3轮: 交叉验证 (交易日)
# ============================
if is_trading:
    section("第3轮: 交叉验证（盘中）")
    
    # 腾讯 vs AKShare 上证涨跌
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        if df is not None and len(df) >= 2:
            ak_chg = round((float(df.iloc[-1]['close']) / float(df.iloc[-2]['close']) - 1) * 100, 2)
            tc_chg = float(q['change_pct']) if q else 0
            diff = abs(ak_chg - tc_chg)
            check(f"腾讯vsAKShare涨跌 偏差={diff:.2f}%", diff < 0.5,
                  f"腾讯={tc_chg}% vs AK={ak_chg}%")
    except Exception as e:
        check(f"腾讯vsAKShare涨跌", False, str(e)[:60])
    
    # 天天基金 vs AKShare 净值
    for code in ['017103', '011613', '003096']:
        try:
            ft_val = ft.get_fund_value(code)
            df_ak = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if ft_val and df_ak is not None and not df_ak.empty:
                ft_nav = float(ft_val['nav'])
                ft_date = ft_val.get('nav_date', '')
                ak_nav = float(df_ak.iloc[-1]['单位净值'])
                ak_date = str(df_ak.iloc[-1]['净值日期'])[:10]
                if ft_date == ak_date:
                    diff = abs(ft_nav - ak_nav)
                    check(f"{code} 同日期净值偏差={diff:.4f}", diff < 0.01,
                          f"天天={ft_nav} AK={ak_nav}")
                else:
                    results.append(f"  ⚠️ {code}: 日期不同(天天={ft_date}, AK={ak_date})，跳偏差验证")
        except Exception as e:
            warnings.append(f"{code}交叉验证: {type(e).__name__}")
    
    # 涨跌家数三源对比
    try:
        ak_bf = __import__('fund_source_akshare', fromlist=['get_market_breadth_akshare']).get_market_breadth_akshare()
        if ak_bf and mo:
            check("AKShare vs 东财涨跌数",
                  abs(ak_bf['rise_count'] - (mo.get('rise_count') or 0)) < 500,
                  f"AK={ak_bf['rise_count']} 东财={mo.get('rise_count')}")
    except Exception as e:
        warnings.append(f"涨跌三源对比: {e}")

# ============================
# 第4轮: track_source追踪更新
# ============================
section("第4轮: 归档数据检查")

tracker_path = '/opt/data/fund_system_data/_source_availability.jsonl'
if os.path.exists(tracker_path):
    with open(tracker_path) as f:
        tracker_lines = [l for l in f.read().strip().split('\n') if l.strip()]
    check(f"追踪记录总数: {len(tracker_lines)}", len(tracker_lines) > 0)
    
    # 今天是否有记录
    today_records = [l for l in tracker_lines if TODAY_STR in l]
    if today_records:
        ok_count = sum(1 for l in today_records if '"success": true' in l)
        check(f"今日已追踪: {len(today_records)}条({ok_count}成功)", ok_count > 0)
else:
    check("追踪文件存在", False)

# ============================
# 汇总报告
# ============================
section("📋 验证汇总")

duration = time.time() - __import__('time').time()  # approximate
results.append(f"\n**结果: {passed}/{passed+failed} 通过**")
if failed > 0:
    results.append(f"**{failed} 项失败**")
if warnings:
    results.append(f"\n⚠️ 警告:")
    for w in warnings:
        results.append(f"  {w}")

results.append(f"\n📅 {TODAY_STR} ({WEEKDAY_NAMES[WEEKDAY]})")
if is_trading:
    results.append("📈 交易日 — 完整数值验证已执行")
else:
    results.append("⏭️ 非交易日 — 仅API可达性验证")

print('\n'.join(results))
