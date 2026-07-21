#!/usr/bin/env python3
"""验证a-stock-data能否拉取我们需要的数据"""
import sys
sys.path.insert(0, '/opt/data')

# a-stock-data 的内核代码：mootdx + 腾讯财经直连
import mootdx
from mootdx.quotes import Quotes
import requests
import pandas as pd

# 初始化通达信行情客户端
client = Quotes.factory(market='std')  # std=标准服务器

print("=" * 60)
print("📊 验证 a-stock-data 数据可用性")
print("=" * 60)

# 1. 大盘指数 - 通过 mootdx
print("\n=== 1. 上证指数 (000001) 最近5天 ===")
try:
    df = client.bars(symbol='000001', frequency=9, offset=0, start=0, count=5)
    # frequency: 9=日线
    if df is not None and len(df) > 0:
        print(df[['open', 'high', 'low', 'close', 'volume']].to_string())
    else:
        print("❌ mootdx 获取上证指数失败")
except Exception as e:
    print(f"❌ mootdx: {e}")

# 2. 腾讯财经获取实时数据（不封IP）
print("\n=== 2. 腾讯财经实时行情 ===")
try:
    # 腾讯行情API: 易方达黄金ETF联接C跟踪的是黄金ETF(159934)
    # 腾讯接口: qt.gtimg.cn
    codes = ['sh000001', 'sz399006', 'sz159934', 'sh000688', 'sz000300']
    url = f"https://qt.gtimg.cn/q={'sh000001'}"
    r = requests.get(f"https://qt.gtimg.cn/q={'|'.join(codes)}", timeout=10)
    # 腾讯返回格式: v_xxx="code~name~open~close~high~low...";
    lines = r.text.strip().split(';')
    for line in lines:
        if '="' in line:
            parts = line.split('="')[1].rstrip('"').split('~')
            name = parts[1]
            price = parts[3]
            change_pct = parts[32] if len(parts) > 32 else 'N/A'
            print(f"  {name}: {price} ({change_pct}%)")
except Exception as e:
    print(f"❌ 腾讯财经: {e}")

# 3. 基金净值 - 天天基金接口
print("\n=== 3. 你的基金净值 ===")
funds = {
    '002963': '易方达黄金ETF联接C',
    '009477': '中银上海金ETF联接C',
    '011613': '华夏科创50ETF联接C',
    '012045': '大摩ESG量化混合C',
    '016803': '大摩沪港深科技混合C',
}
# 天天基金净值API: fundgz.1234567.com.cn
for code, name in funds.items():
    try:
        url = f"https://fundgz.1234567.com.cn/js/{code}.js"
        r = requests.get(url, timeout=5, headers={'Referer': 'https://fund.eastmoney.com/'})
        # 返回格式: jsonpgz({"fundcode":"002963","name":"...","jzrq":"...","dwjz":"...","gsz":"...","gszzl":"..."});
        txt = r.text.strip()
        if 'jsonpgz(' in txt:
            import json
            data = json.loads(txt[txt.index('(')+1:txt.rindex(')')])
            print(f"  {name}({code}): 净值={data.get('dwjz','?')}  估算={data.get('gsz','?')}  估算涨幅={data.get('gszzl','?')}%")
        else:
            print(f"  {name}({code}): ❌ 无数据")
    except Exception as e:
        print(f"  {name}({code}): ❌ {e}")

# 4. ETF实时行情 - 腾讯接口
print("\n=== 4. 相关ETF行情（你的持仓对应ETF） ===")
etf_codes = ['sz159934', 'sz159930', 'sh588000', 'sz159845', 'sz159866']
try:
    url = f"https://qt.gtimg.cn/q={'|'.join(etf_codes)}"
    r = requests.get(url, timeout=10)
    lines = r.text.strip().split(';')
    for line in lines:
        if '="' in line:
            parts = line.split('="')[1].rstrip('"').split('~')
            name = parts[1]
            price = parts[3]
            change_pct = parts[32] if len(parts) > 32 else 'N/A'
            print(f"  {name}: {price} ({change_pct}%)")
except Exception as e:
    print(f"❌ ETF行情: {e}")

print("\n" + "=" * 60)
print("✅ 验证完毕")
print("=" * 60)
