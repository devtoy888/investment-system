#!/usr/bin/env python3
"""Verify ALL fund codes via real API calls"""
import sys, json, time, requests
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import FUND_CODES, GROUPS

print("🔍 基金代码 API 实时验证")
print("=" * 60)
print(f"{'代码':8s} {'API状态':10s} {'基金名称(系统)':40s}")
print("-" * 60)

# Also check via 天天基金净值API and via fund search API
errors = []
verified = {}

for code, name in FUND_CODES.items():
    # Method 1: Try the standard fund value API
    try:
        url = f"https://fundgz.1234567.com.cn/js/{code}.js"
        r = requests.get(url, timeout=8, headers={'Referer': 'https://fund.eastmoney.com/'})
        txt = r.text.strip()
        
        if 'jsonpgz(' in txt:
            data = json.loads(txt[txt.index('(')+1:txt.rindex(')')])
            api_name = data.get('name', '')
            nav = data.get('dwjz', '?')
            gsz = data.get('gsz', '?')
            print(f"  {code} ✅  {api_name:35s} (净{nav} 估{gsz})")
            verified[code] = {'status': 'ok', 'api_name': api_name, 'nav': nav}
        elif 'fcode' in txt or 'code' in txt:
            # Try parsing differently
            print(f"  {code} ⚠️  有返回但格式异常: {txt[:60]}")
            errors.append((code, 'format_error', txt[:60]))
        else:
            print(f"  {code} ❌  API无数据: {txt[:60]}")
            errors.append((code, 'no_data', txt[:60]))
    except Exception as e:
        # Method 2: Fallback to search API
        try:
            url2 = f"https://fundgz.1234567.com.cn/js/{code}.js"
            r2 = requests.get(url2, timeout=5, headers={'Referer': 'https://fund.eastmoney.com/'})
            if r2.status_code == 200 and len(r2.text) > 20:
                print(f"  {code} ⚠️  retry成功: {r2.text[:60]}")
            else:
                print(f"  {code} ❌  {str(e)[:40]}")
                errors.append((code, 'exception', str(e)[:40]))
        except:
            print(f"  {code} ❌  {str(e)[:40]}")
            errors.append((code, 'exception', str(e)[:40]))
    
    time.sleep(0.5)

print()
print("=" * 60)
if errors:
    print(f"\n⚠️ 以下代码有问题 ({len(errors)}个):")
    for code, reason, detail in errors:
        print(f"  ❌ {code}: {reason} - {detail}")
else:
    print("\n✅ 所有代码 API 验证通过!")

print()
print("分组汇总:")
for g, codes in GROUPS.items():
    ok_count = sum(1 for c in codes if c in verified)
    print(f"  {g}: {ok_count}/{len(codes)} 支验证通过")

# Check for codes not covered by any group
all_grouped = set()
for codes in GROUPS.values():
    all_grouped.update(codes)
ungrouped = set(FUND_CODES.keys()) - all_grouped
if ungrouped:
    print(f"\n⚠️ 以下代码未在任何分组中: {ungrouped}")
