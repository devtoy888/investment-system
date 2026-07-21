#!/usr/bin/env python3
"""Analyze IT精英's allocation pattern in detail"""
import json, sys
from datetime import datetime, timezone

data = json.loads(open('/tmp/kol_phase2_final.json').read())
posts = data.get('5044466342', {}).get('posts', [])
name = "IT精英带你养基"

print(f"📋 {name}: {len(posts)}条博文分析")
print(f"{'='*70}")

# ── 1. Extract all allocation-related data ──
alloc_records = []       # 配比声明
operation_records = []   # 每日操作
return_records = []      # 收益声明

for p in posts:
    text = p['text']
    date = p['created_at']
    
    # 配比声明
    if '稳健' in text and ('%' in text or '占比' in text):
        alloc_records.append({'date': date, 'text': text[:200]})
    
    # 操作记录
    if any(w in text for w in ['买入', '卖出', '操作', '调仓']):
        operation_records.append({'date': date, 'text': text[:200]})
    
    # 收益/金额声明
    if any(w in text for w in ['万', '收益', '回血', '亏', '绿了', '总金额']):
        return_records.append({'date': date, 'text': text[:200]})

print(f"\n📊 配比声明: {len(alloc_records)}条")
print(f"📊 操作记录: {len(operation_records)}条")
print(f"📊 收益/金额: {len(return_records)}条")

# ── 2. 配比分析 ──
print(f"\n{'='*70}")
print("🔍 配比声明分析")
print(f"{'='*70}")
for r in alloc_records:
    print(f"\n  [{r['date'][:16]}]")
    print(f"  {r['text']}")

# ── 3. 操作记录分析 ──
print(f"\n{'='*70}")
print("🔍 操作记录逐条分析")
print(f"{'='*70}")

for r in operation_records:
    text = r['text']
    date = r['date'][:16]
    
    # 解析买入金额
    amounts = []
    import re
    for match in re.finditer(r'(\d+(?:\.\d+)?)\s*元', text):
        amounts.append(int(float(match.group(1))))
    
    action = '买入' if '买入' in text else ('卖出' if '卖出' in text else ('无操作' if '无操作' in text else '其他'))
    amount_str = f"{sum(amounts)}元" if amounts else '(未指明)'
    product = '进攻组合' if '进攻' in text else ('防守组合' if '防守' in text else ('组合' if '组合' in text else text[:30]))
    
    print(f"\n  [{date}]")
    print(f"    操作: {action} | 金额: {amount_str} | 产品: {product}")
    print(f"    全文: {text[:120]}")

# ── 4. 收益轨迹重建 ──
print(f"\n{'='*70}")
print("🔍 收益轨迹")
print(f"{'='*70}")

# Sort return records by date
return_records_sorted = sorted(return_records, key=lambda x: x['date'])
for r in return_records_sorted:
    print(f"\n  [{r['date'][:16]}]")
    print(f"  {r['text'][:150]}")

# ── 5. 整体评估 ──
print(f"\n{'='*70}")
print("📋 综合评估")
print(f"{'='*70}")

# 操作频率
total_days = 0
if posts:
    dates = []
    for d in [p['created_at'] for p in posts]:
        try: dates.append(datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y'))
        except: pass
    if dates:
        total_days = max(1, (dates[0] - dates[-1]).days)

has_purchase = sum(1 for r in operation_records if '买入' in r['text'])
has_sell = sum(1 for r in operation_records if '卖出' in r['text'] or '调出' in r['text'])
no_op_count = sum(1 for r in operation_records if '无操作' in r['text'])
total_ops = len(operation_records)

print(f"\n操作统计:")
print(f"  时间跨度: {total_days}天")
print(f"  总操作博文: {total_ops}条")
print(f"    其中买入: {has_purchase}次")
print(f"    其中无操作: {no_op_count}次")
print(f"    其中卖出/调出: {has_sell}次")
print(f"  操作频率: {total_ops/max(1,total_days):.2f}次/天")

# 收益估算
print(f"\n收益估算:")
for r in return_records:
    text = r['text']
    if '总金额' in text:
        print(f"  [{r['date'][:10]}] 总金额提及")
    if '收益' in text:
        print(f"  [{r['date'][:10]}] 收益提及")

# His 60/40 split is theoretical or actual?
print(f"\n评估结论:")
print(f"  配比: 声称稳健60%/波动40%")
has_actual_alloc_data = any('稳健' in r['text'] for r in alloc_records)
print(f"  60/40是恒定比例还是动态调整?")
print(f"    → 从他的博文看，配比是固定声明而非动态调整")
alloc_note = '每次提都是「我作为平衡型投资者」的标准话术'
print(f"    → {alloc_note}")
print(f"  他的收益水平:")
print(f"    → 总资产~290万 (接近300万目标)")
print(f"    → 2026年YTD收益从10万降到8万 (~3%收益率)")
print(f"    → 作为平衡型(60%债)还算合理")
print(f"  参考价值评估:")
print(f"    → 60/40是一个经典平衡策略，但缺乏动态调整依据")
note1 = '他实际上是在做「固定定投」，不是择时'
print(f"    → {note1}")
note2 = '参考价值有限：更多是心理安慰型内容'
print(f"    → {note2}")

# Save analysis
analysis = {
    'total_posts': len(posts),
    'alloc_statements': len(alloc_records),
    'operations': len(operation_records),
    'buy_count': has_purchase,
    'sell_count': has_sell,
    'no_op_count': no_op_count,
    'return_records': [{'date': r['date'], 'text_preview': r['text'][:100]} for r in return_records],
}

json.dump(analysis, open('/tmp/itjingying_analysis.json','w'), ensure_ascii=False, indent=2)
print(f"\n✅ -> /tmp/itjingying_analysis.json")
