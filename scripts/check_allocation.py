#!/usr/bin/env python3
"""
组合偏离度检测 — 收盘后运行
检查各分组占比是否超过阈值，超限则输出推送内容

阈值（来自系统设计）:
  黄金 > 20%  → ⚠️
  科技/AI > 45% → ⚠️
  任意分组 > 60% → 🔴 紧急
"""
import sys, json, os
sys.path.insert(0, '/opt/data/scripts')
from pathlib import Path
from datetime import date

# 当前持仓（硬编码，来源 portfolio-2026-07-15）
PORTFOLIO = {
    "科技/AI": ["011613", "024418", "011712", "026449", "017103", "020233", "014871"],
    "黄金": ["009478"],
    "资源/周期": ["163302", "025857"],
    "新能源": ["012329", "011103"],
    "医药": ["003096"],
    "港股科技": ["013403"],
}

# 分组的当日估值字段映射（closing-review 中的 fund_accuracy 字段名）
GROUP_VALUE_KEYS = {
    "黄金": "009478",
    "新能源": "012329",  # 用新能源的第一个基金代表
}

# 偏离度阈值
THRESHOLDS = {
    "黄金": {"max": 20},
    "科技/AI": {"max": 45},
    "医药": {"max": 15},
    "港股科技": {"max": 15},
}

def out(s=""):
    print(s)

def get_fund_values():
    """从最新 closing-reviews.jsonl 读取基金估算涨跌幅"""
    DATA_DIR = Path("/opt/data/fund_system_data")
    path = DATA_DIR / "closing-reviews.jsonl"
    if not path.exists():
        return None
    
    lines = [l.strip() for l in path.read_text().split('\n') if l.strip()]
    if not lines:
        return None
    
    try:
        last = json.loads(lines[-1])
    except:
        return None
    
    fund_acc = last.get("fund_accuracy", {})
    return fund_acc

def estimate_group_values(fund_values):
    """根据基金估算涨跌幅推算各组当前占比"""
    # 用成本占比做近似（当日估值变化不大时成本占比≈市值占比）
    # 成本数据
    cost_map = {
        "011613": 1301.98, "024418": 1125.37, "011712": 517.97,
        "026449": 252.83, "017103": 585.17, "020233": 499.68,
        "014871": 618.05, "163302": 214.46, "025857": 127.09,
        "012329": 5.09, "011103": 8.75, "009478": 439.34,
    }
    
    # 用最新日期的净值涨跌幅调整市值
    group_values = {}
    for gname, codes in PORTFOLIO.items():
        total = 0.0
        for code in codes:
            cost = cost_map.get(code, 0)
            if fund_values and code in fund_values:
                est = fund_values[code].get("now_est")
                if est:
                    try:
                        change = float(est) / 100  # 百分比转小数
                        total += cost * (1 + change)
                        continue
                    except:
                        pass
            total += cost  # 回退到成本
        group_values[gname] = total
    
    return group_values

def main():
    today = date.today().isoformat()
    
    fund_values = get_fund_values()
    group_values = estimate_group_values(fund_values)
    
    total = sum(group_values.values())
    if total == 0:
        out("")
        return
    
    alerts = []
    pcts = {}
    
    for gname, gval in sorted(group_values.items(), key=lambda x: x[1], reverse=True):
        pct = round(gval / total * 100, 1)
        pcts[gname] = pct
        
        # 检查阈值
        if gname in THRESHOLDS:
            max_pct = THRESHOLDS[gname]["max"]
            if pct > max_pct:
                urgency = "🔴" if pct > max_pct * 1.5 else "⚠️"
                alerts.append(f"{urgency} {gname}占比{pct}%，超过阈值{max_pct}%")
        
        # 全局60%紧急线
        if pct > 60:
            alerts.append(f"🔴 {gname}占比{pct}%，超过60%紧急线，建议大幅减仓")
    
    if not alerts:
        out("")
        return
    
    # 输出推送内容
    out(f"📊 **组合偏离度检测 — {today}**")
    out()
    for gname, pct in sorted(pcts.items(), key=lambda x: x[1], reverse=True):
        bar_len = int(pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        out(f"  {bar} {gname:<8} {pct:>5.1f}%")
    out()
    for alert in alerts:
        out(f"  {alert}")
    out()

if __name__ == "__main__":
    main()
