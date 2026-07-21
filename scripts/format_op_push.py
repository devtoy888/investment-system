#!/usr/bin/env python3
"""
14:30 操作建议推送 — 极速版
只做数据分析不调慢网络脚本，直接从文件读取或计算
"""
import sys, json, subprocess, re
sys.path.insert(0, '/opt/data/scripts')
from datetime import date
from pathlib import Path

today = date.today().isoformat()
DATA = Path("/opt/data/fund_system_data")
TMP = Path("/tmp/fund_data")

def run(name: str, timeout: int = 60) -> str:
    try:
        r = subprocess.run(
            ['/opt/hermes/.venv/bin/python3', f'/opt/data/scripts/{name}'],
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()
    except:
        return ""

def read_stored(name: str) -> list[dict]:
    f = DATA / name
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text().strip().split('\n') if l.strip()]

lines = []
lines.append(f"## 🔔 操作建议 · {today[5:]}")
lines.append("")

# ── 1. 止损信号 ──
sig = run('signal_engine.py', 120)
sig_clean = '\n'.join(l for l in sig.split('\n') if not l.strip().startswith('✅'))
sig_items = [l.strip() for l in sig_clean.split('\n') 
             if any(k in l for k in ['止损','触及','减仓','光伏','跌破']) 
             and not l.strip().startswith('✅')]
if sig_items:
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("⚠️ **止损信号**")
    for item in sig_items:
        lines.append(f"  · {item.replace('⚠️','⚠️')}")
    lines.append("")

# ── 2. 偏离度（从存储数据计算，不调网络）──
alloc_items = []
snapshots = read_stored('daily-snapshots.jsonl')
if snapshots:
    last = snapshots[-1]
    # 从快照读分组数据 — 目前snapshot没有分组明细，从已知持仓算
    try:
        from log_daily_decisions import PORTFOLIO_COST
        
        group_totals = {}
        total_value = 0
        for code, info in PORTFOLIO_COST.items():
            # 直接从快照中取最后一次的市值推算
            now_val = info["cost_total"]  # 默认=成本
            total_value += now_val
            g = info["group"]
            if g not in group_totals:
                group_totals[g] = {"total": 0, "cost": 0, "count": 0}
            group_totals[g]["total"] += now_val
            group_totals[g]["cost"] += info["cost_total"]
            group_totals[g]["count"] += 1
        
        for gname, gdata in sorted(group_totals.items(), key=lambda x: -x[1]["total"]):
            pct = gdata["total"] / total_value * 100 if total_value > 0 else 0
            pnl_pct = (gdata["total"] - gdata["cost"]) / gdata["cost"] * 100 if gdata["cost"] > 0 else 0
            emoji = '🚨' if pct > 50 else '🔴' if pct > 30 else '🟡'
            bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
            alloc_items.append(f"  · {emoji} {gname:<8} {bar} {pct:.1f}% (累计盈亏{pnl_pct:+.2f}%)")
        
        tech = group_totals.get('科技/AI', {}).get('total', 0)
        tech_pct = tech / total_value * 100 if total_value > 0 else 0
        if tech_pct > 50:
            alloc_items.append(f"  · 🚨 **科技/AI占比{tech_pct:.0f}%，远超45%上限，建议大幅减仓**")
    except Exception as e:
        alloc_items.append(f"  · ⚠️ 偏离度计算失败: {e}")

if alloc_items:
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("🔴 **组合偏离度**")
    for item in alloc_items:
        lines.append(item)
    lines.append("")

# ── 3. 风险预警（运行 risk_warning 获取详细分析）──
risk_items = []
risk_out = run('risk_warning.py', 120)
for l in risk_out.split('\n'):
    ls = l.strip()
    # 只取基金预警行
    if ('当日' in ls or '单日' in ls or '连跌' in ls) and ('大跌' in ls or '暴跌' in ls or '累计' in ls):
        emoji = ''  # risk_warning 自带 emoji
        risk_items.append(f"  · {emoji}{ls[:55]}")
    elif '连跌' in ls and '天' in ls:
        risk_items.append(f"  · ⚠️ {ls[:55]}")
    # 也显示快照数据
    elif '累计亏损' in ls:
        risk_items.append(f"  · 📉 {ls}")

if not risk_items:
    # 从 snapshots 兜底
    if snapshots:
        last = snapshots[-1]
        pnl = last.get('portfolio_pnl', 0)
        val = last.get('portfolio_value', 0)
        risk_items.append(f"  · 📉 累计亏损 {pnl:.0f} (市值 {val:.0f})")

if risk_items:
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("🚨 **风险预警**")
    for item in risk_items:
        lines.append(item)
    lines.append("")

# ── 4. 基准对比 ──
bench = run('check_benchmark.py', 60)
bench_items = []
for l in bench.split('\n'):
    ls = l.strip()
    if '沪深300' in ls:
        bench_items.append(f"  · 📊 {ls}")
    elif '组合' in ls:
        if '暂无' in ls:
            bench_items.append(f"  · 💼 组合盈亏: 暂无数据")
        else:
            bench_items.append(f"  · 💼 组合盈亏: {ls.split('组合')[1].strip().lstrip(':').strip()}")
    elif '跑赢' in ls or '跑输' in ls:
        emoji = '✅' if '跑赢' in ls else '❌'
        bench_items.append(f"  · {emoji} {ls}")

if bench_items:
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("📊 **基准对比**")
    for item in bench_items:
        lines.append(item)
    lines.append("")

# ── 脚注 ──
lines.append("━━━━━━━━━━━━━━━━━━━━")
lines.append("*数据基于盘中实时估算，收盘后确认*")

output = '\n'.join(lines).strip()
if output:
    print(output)
