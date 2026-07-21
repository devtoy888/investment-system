#!/usr/bin/env python3
"""
持仓基金加仓信号监控脚本（no_agent模式）
每天收盘后运行，当满足条件时推送提醒。

触发逻辑：
1. 大摩数字经济C(017103): 独立走强 (翻红且半导体<1% independent of sector) 或 单日>+0.5%
2. 天弘光伏C(011103): 放量反弹(涨>2%+振幅>3%) 或 翻红>+0.5% 或 ETF跌至0.75止损线
3. 天弘新能源增强C(012329): 涨>1.5%+振幅>2% 或 翻红>+0.5%
4. 电网设备ETF联接C(025857): 缩量止跌(振幅<2%) 或 ETF回1.95以上

输出为空 = 无信号，不推送；输出非空 = 有信号，推送提醒。

监控cron: 7ea6086a7749 (交易日16:30 CST)
"""
import sys, json, math
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import get_fund_value, get_tencent_quote, get_group_trend
from datetime import date

today = date.today().isoformat()
TRIGGERED = []

# ── 1. 大摩数字经济C(017103) ──
v = get_fund_value('017103')
if v:
    ec = v.get('estimated_change', '?')
    nav = v.get('nav', '?')
    enav = v.get('estimated_nav', '?')
    try:
        ec_f = float(ec)
        if math.isnan(ec_f) or math.isinf(ec_f):
            ec_f = None
    except:
        ec_f = None
    
    if ec_f is not None:
        bq = get_tencent_quote('sz159813')
        semi_pct = float(bq['change_pct']) if bq else 0
        msg_parts = [f"📊 大摩数字经济C: 净值{nav}→{enav} ({ec_f:+.2f}%)"]
        
        if ec_f > 0.5 and semi_pct < 1.0:
            msg_parts.append(f"✅ 独立走强（半导体仅{semi_pct:+.2f}%），资金回流的信号")
            TRIGGERED.append('\n'.join(msg_parts))
        elif ec_f > 0.3:
            msg_parts.append(f"📈 今日翻红，短期企稳信号")
            TRIGGERED.append('\n'.join(msg_parts))

# ── 2. 天弘光伏C(011103) ──
v = get_fund_value('011103')
gq = get_tencent_quote('sz159857')
if v and gq:
    ec = v.get('estimated_change', '?')
    nav = v.get('nav', '?')
    enav = v.get('estimated_nav', '?')
    try:
        ec_f = float(ec)
        if math.isnan(ec_f) or math.isinf(ec_f):
            ec_f = None
    except:
        ec_f = None
    
    gprice = float(gq['price'])
    ghigh = float(gq.get('high', 0) or 0)
    glow = float(gq.get('low', 0) or 0)
    gprev = float(gq.get('prev_close', 0) or 1)
    gamp = (ghigh - glow) / gprev * 100 if gprev > 0 else 0
    
    if ec_f is not None:
        msg_parts = [f"📊 天弘光伏C: 净值{nav}→{enav} ({ec_f:+.2f}%) ETF={gprice}"]
        
        if gprice <= 0.75:
            TRIGGERED.append(f"⚠️ 光伏ETF跌至{gprice}（触及0.75止损线）！建议减仓一半。")
        elif ec_f > 2.0 and gamp > 3:
            msg_parts.append(f"🔥 放量反弹（振幅{gamp:.1f}%）！加仓时机信号")
            TRIGGERED.append('\n'.join(msg_parts))
        elif ec_f > 0.5:
            msg_parts.append(f"📈 今日翻红，短期企稳信号")
            TRIGGERED.append('\n'.join(msg_parts))

# ── 3. 天弘新能源增强C(012329) ──
v = get_fund_value('012329')
nq = get_tencent_quote('sz159752')
if v and nq:
    ec = v.get('estimated_change', '?')
    nav = v.get('nav', '?')
    enav = v.get('estimated_nav', '?')
    try:
        ec_f = float(ec)
        if math.isnan(ec_f) or math.isinf(ec_f):
            ec_f = None
    except:
        ec_f = None
    
    nhigh = float(nq.get('high', 0) or 0)
    nlow = float(nq.get('low', 0) or 0)
    nprev = float(nq.get('prev_close', 0) or 1)
    camp = (nhigh - nlow) / nprev * 100 if nprev > 0 else 0
    
    if ec_f is not None:
        msg_parts = [f"📊 天弘新能源增强C: 净值{nav}→{enav} ({ec_f:+.2f}%)"]
        
        if ec_f > 1.5 and camp > 2:
            msg_parts.append(f"🔥 放量反弹（振幅{camp:.1f}%），可关注加仓")
            TRIGGERED.append('\n'.join(msg_parts))
        elif ec_f > 0.5:
            msg_parts.append(f"📈 今日翻红")
            TRIGGERED.append('\n'.join(msg_parts))

# ── 4. 电网设备联接C(025857) ──
v = get_fund_value('025857')
dq = get_tencent_quote('sz159326')
if v and dq:
    ec = v.get('estimated_change', '?')
    nav = v.get('nav', '?')
    enav = v.get('estimated_nav', '?')
    try:
        ec_f = float(ec)
        if math.isnan(ec_f) or math.isinf(ec_f):
            ec_f = None
    except:
        ec_f = None
    
    dprice = float(dq['price'])
    dhigh = float(dq.get('high', 0) or 0)
    dlow = float(dq.get('low', 0) or 0)
    dprev = float(dq.get('prev_close', 0) or 1)
    damp = (dhigh - dlow) / dprev * 100 if dprev > 0 else 0
    
    if ec_f is not None:
        msg_parts = [f"📊 电网设备联接C: 净值{nav}→{enav} ({ec_f:+.2f}%) ETF={dprice} 振幅{damp:.1f}%"]
        
        if damp < 2 and -0.3 <= ec_f <= 1.0:
            msg_parts.append(f"✅ 缩量止跌（振幅{damp:.1f}%），回调企稳信号，可关注加仓")
            TRIGGERED.append('\n'.join(msg_parts))
        elif ec_f > 2.0:
            msg_parts.append(f"🔥 放量上涨！加仓时机")
            TRIGGERED.append('\n'.join(msg_parts))
        elif dprice > 1.95 and ec_f > 0:
            msg_parts.append(f"📈 在{dprice}企稳回升，关注加仓")
            TRIGGERED.append('\n'.join(msg_parts))

# ── 输出 ──
if TRIGGERED:
    print(f"🔔 {today} 持仓加仓信号监测")
    print("=" * 40)
    for msg in TRIGGERED:
        print()
        print(msg)
