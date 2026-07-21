#!/usr/bin/env python3
"""数据源交叉验证"""
import sys, json, re
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import FUND_CODES
from pathlib import Path

OPS_DIR = Path("/opt/data/fund_system_data/operations")
SEED_FILE = Path("/opt/data/fund_system_data/seed_portfolio.json")

# 操作记录中的基金
ops_codes = {}
if OPS_DIR.exists():
    for f in sorted(OPS_DIR.glob("operation_*.md")):
        rows = re.findall(r"\|\s*\d+/\d+\s*\|\s*([^|]+)\s*\|\s*(\d{6})", f.read_text())
        for name, code in rows:
            ops_codes[code] = name.strip()

# seed中的基金
seed_codes = {}
if SEED_FILE.exists():
    seed_data = json.loads(SEED_FILE.read_text())
    for code, info in seed_data.get('funds', {}).items():
        seed_codes[code] = info.get('name', '?')

print("=" * 60)
print("权威数据源交叉验证")
print("=" * 60)
print(f"\n操作记录基金: {len(ops_codes)}支")
print(f"种子持仓基金: {len(seed_codes)}支")
print(f"FUND_CODES:   {len(FUND_CODES)}支")
print()

# 全量基金列表（三源合并）
all_codes = sorted(set(list(ops_codes.keys()) + list(seed_codes.keys()) + list(FUND_CODES.keys())))
print(f"{'代码':8s} {'FUND_CODES名称':20s} {'操作记录名称':20s} {'seed名称':16s} {'一致性'}")
print("-" * 80)
inconsistencies = []
for code in all_codes:
    fc_name = FUND_CODES.get(code, '—')
    ops_name = ops_codes.get(code, '—')
    seed_name = seed_codes.get(code, '—')
    
    # 一致性检查
    names = [n for n in [fc_name, ops_name, seed_name] if n and n != '—']
    consistent = "✅" if len(set(names)) <= 1 else "⚠️"
    if consistent == "⚠️":
        inconsistencies.append(f"{code}: FUND_CODES={fc_name}, ops={ops_name}, seed={seed_name}")
    
    has_all = "✅" if (code in FUND_CODES and code in ops_codes) else "❌"
    print(f"{code:8s} {fc_name:20s} {ops_name:20s} {seed_name:16s} {consistent}")

print("\n⚠️ 不一致的基金:")
for i in inconsistencies:
    print(f"  {i}")

# 检查板块映射覆盖率
from pathlib import Path as P2
SUMMARY_DIR = P2("/tmp/fund_data")
sector_text = ""
p = SUMMARY_DIR / "_noon_sector.txt"
if p.exists():
    sector_text = p.read_text()
mkt_text = ""
p2 = SUMMARY_DIR / "_noon_market.txt"
if p2.exists():
    mkt_text = p2.read_text()

# Fund→Sector mapping from execute_today_plan.py
FUND_SECTOR_MAP = {
    '009478': '黄金ETF市场价',
    '011613': '科创50',
    '024418': '半导体',
    '026449': '恒生科技ETF',
    '014871': '半导体',
    '020233': '半导体',
    '017103': '通信',
    '011712': '通信',
    '163302': '有色金属',
    '025857': '新能源',
    '012329': '新能源',
    '011103': '光伏',
    '003096': '医药',
    '013403': '恒生科技ETF',
}

print(f"\n=== 板块代理覆盖率 ===")
covered = 0
for code, sector in sorted(FUND_SECTOR_MAP.items()):
    # Check if sector exists in data
    found = sector in sector_text or sector in mkt_text
    status = "✅" if found else "❌"
    if found: covered += 1
    print(f"  {code} {FUND_CODES.get(code,'?')[:20]:20s} → {sector:12s} {status}")
print(f"覆盖率: {covered}/{len(FUND_SECTOR_MAP)}")
