#!/usr/bin/env python3
"""重新生成收盘复盘R2报告（修正版）"""
import sys, os
sys.path.insert(0, '/opt/data/scripts')
os.chdir('/opt/data/scripts')

from push_report_r2 import push_report
from datetime import date
from llm_analysis_v2 import generate_v2

# 清除缓存
cache_dir = '/opt/data/fund_system_data/llm_analysis_cache'
for f in os.listdir(cache_dir):
    if f.startswith('closing'):
        os.remove(os.path.join(cache_dir, f))
        print(f"  🧹 清除缓存: {f}")

# 重新生成数据（grab the already-fixed data from close_review.py）
tables_path = '/tmp/fund_data/_closing_tables.md'
if not os.path.exists(tables_path):
    print("⚠️ _closing_tables.md 不存在")
    sys.exit(1)

tables = open(tables_path).read()
print(f"  ✅ 数据表: {len(tables)}字节")
print(f"  ✅ 024418数据: {'+15.80%' if '+15.80%' in tables else '❌ 数据错误'}")
print(f"  ✅ 基金名: {'009478 中银上海金' if '009478 中银上海金' in tables else '❌ 无基金名'}")

# AI分析（无缓存，用新prompt）
analysis = generate_v2('closing', use_cache=False)
if analysis:
    # 检查AI是否违反了深套约束
    if '止盈' in analysis and ('024418' in analysis or '011712' in analysis):
        print("⚠️ 可能违反深套约束！重新生成...")
        # 强制再生成
        analysis = generate_v2('closing', use_cache=False)
    print(f"  ✅ AI分析: {len(analysis)}字")
    has_hold = '持有' in analysis or '不动' in analysis
    has_wrong = '止盈' in analysis and '024418' in analysis
    print(f"  ✅ 包含'持有/不动': {has_hold}, 包含'止盈+024418': {has_wrong}")
else:
    print("⚠️ AI分析为空")

# 推送R2
md, html = push_report('closing', f'收盘复盘 · {date.today()}', tables, analysis or '')
print(f"\n📄 R2报告:")
print(f"  MD: {md}")
print(f"  HTML: {html}")
