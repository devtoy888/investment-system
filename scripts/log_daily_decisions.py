#!/usr/bin/env python3
"""
每日决策日志 + 价格快照 + 持仓市值追踪
收盘后运行，产出:
  1. decisions.jsonl — 当日决策记录（含持仓市值快照）
  2. daily-snapshots.jsonl — 去重价格快照
  3. portfolio-{日期}.md — 当日持仓市值明细
  4. 自动上传R2
"""
import sys, os, json, math
sys.path.insert(0, '/opt/data/scripts')
from pathlib import Path
from datetime import date, datetime, timedelta
from fund_tools import upload_to_r2, FUND_SYSTEM_PREFIX, get_fund_value

DATA_DIR = Path("/opt/data/fund_system_data")
TODAY = date.today().isoformat()

# 持仓成本数据（来源: portfolio-2026-07-15）
PORTFOLIO_COST = {
    "011613": {"name": "华夏科创50ETF联接C", "group": "科技/AI", "shares": 837.18, "cost_price": 1.5552, "cost_total": 1401.98},
    "024418": {"name": "华夏上证科创板半导体材料设备ETF联接C", "group": "科技/AI", "shares": 405.16, "cost_price": 2.7776, "cost_total": 1325.37},
    "011712": {"name": "大摩万众创新混合C", "group": "科技/AI", "shares": 339.12, "cost_price": 1.5274, "cost_total": 517.97},
    "026449": {"name": "大摩沪港深科技混合C", "group": "科技/AI", "shares": 191.64, "cost_price": 1.3193, "cost_total": 252.83},
    "017103": {"name": "大摩数字经济混合C", "group": "科技/AI", "shares": 130.75, "cost_price": 4.4755, "cost_total": 585.17},
    "020233": {"name": "大摩景气智选混合C", "group": "科技/AI", "shares": 316.15, "cost_price": 1.5805, "cost_total": 499.68},
    "014871": {"name": "大摩科技领先混合C", "group": "科技/AI", "shares": 179.31, "cost_price": 3.4468, "cost_total": 618.05},
    "025857": {"name": "华夏中证电网设备ETF联接C", "group": "资源/周期", "shares": 101.07, "cost_price": 1.2574, "cost_total": 127.09},
    "163302": {"name": "大摩资源优选混合(LOF)", "group": "资源/周期", "shares": 185.09, "cost_price": 1.1587, "cost_total": 214.46},
    "012329": {"name": "天弘中证新能源指数增强C", "group": "新能源", "shares": 6.42, "cost_price": 0.7925, "cost_total": 5.09},
    "011103": {"name": "天弘中证光伏C", "group": "新能源", "shares": 9.73, "cost_price": 0.8994, "cost_total": 8.75},
    "009478": {"name": "中银上海金ETF联接C", "group": "黄金", "shares": 214.52, "cost_price": 2.0480, "cost_total": 439.34},
    # 7/16 新增建仓
    "003096": {"name": "中欧医疗健康混合C", "group": "医药", "shares": 80.77, "cost_price": 1.9810, "cost_total": 160.00},
    "013403": {"name": "华夏恒生科技ETF联接(QDII)C", "group": "港股科技", "shares": 0, "cost_price": 0, "cost_total": 150.00},
}

def out(s=""):
    print(s)

def get_latest_closing():
    """从 closing-reviews.jsonl 读取最新有效收盘数据"""
    path = DATA_DIR / "closing-reviews.jsonl"
    if not path.exists():
        return None
    lines = [l.strip() for l in path.read_text().split('\n') if l.strip()]
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except:
        return None

def calc_portfolio_value():
    """获取今日基金估算涨跌，计算持仓市值"""
    now_values = {}
    for code, info in PORTFOLIO_COST.items():
        r = get_fund_value(code)
        if r:
            try:
                est = float(r.get('gszzl', r.get('estimated_change', 0)))
            except:
                est = 0
            # 市值 = 昨日市值 × (1 + 今日估算涨跌幅)
            # 首次就用成本价 × 份额
            now_value = info["cost_total"] * (1 + est / 100)
        else:
            est = None
            now_value = info["cost_total"]
        now_values[code] = {
            "name": info["name"],
            "group": info["group"],
            "cost_total": info["cost_total"],
            "today_change_pct": est,
            "now_value": round(now_value, 2),
            "pnl": round(now_value - info["cost_total"], 2),
        }
    return now_values

def build_price_snapshot():
    """构建价格快照"""
    closing = get_latest_closing()
    if not closing:
        return None
    snapshot = {"_date": TODAY, "_ts": datetime.now().isoformat()}
    accuracy = closing.get("market_accuracy", {})
    indices = {}
    for idx_name, data in accuracy.items():
        if isinstance(data, dict):
            try:
                indices[idx_name] = float(data.get("close", data.get("now", 0)))
            except:
                pass
    if indices:
        snapshot["indices"] = indices
    snapshot["market_accuracy_pct"] = closing.get("market_accuracy_pct")
    snapshot["market_score"] = closing.get("market_score")
    overnight = closing.get("overnight", {})
    if overnight:
        snapshot["overnight"] = {k: {"price": v.get("price"), "change": v.get("change_pct")} for k, v in overnight.items()}
    return snapshot

def build_portfolio_md(values):
    """生成持仓市值明细MD"""
    lines = []
    lines.append(f"# 📊 持仓市值 · {TODAY}")
    lines.append(f"> 每日自动更新 | 基于基金实时估算涨跌幅")
    lines.append("")
    
    groups = {}
    total_now = 0
    total_cost = 0
    for code, v in values.items():
        g = v["group"]
        groups.setdefault(g, {"funds": [], "total_now": 0, "total_cost": 0})
        groups[g]["funds"].append((code, v))
        groups[g]["total_now"] += v["now_value"]
        groups[g]["total_cost"] += v["cost_total"]
        total_now += v["now_value"]
        total_cost += v["cost_total"]
    
    for gname, gdata in sorted(groups.items(), key=lambda x: x[1]["total_now"], reverse=True):
        gpnl = round(gdata["total_now"] - gdata["total_cost"], 2)
        pct = round(gdata["total_now"] / total_now * 100, 1)
        lines.append(f"### {gname}（{pct}%）")
        lines.append(f"| 基金 | 成本 | 当前市值 | 今日涨跌 | 盈亏 |")
        lines.append(f"|:----|:---:|:--------:|:--------:|:----:|")
        for code, v in sorted(gdata["funds"], key=lambda x: x[1]["now_value"], reverse=True):
            chg = f"{v['today_change_pct']:+.2f}%" if v['today_change_pct'] is not None else "-"
            emoji = "📈" if v['pnl'] > 0 else "📉"
            lines.append(f"| {v['name']} | {v['cost_total']:.2f} | {v['now_value']:.2f} | {chg} | {emoji}{v['pnl']:+.2f} |")
        lines.append(f"| **小计** | **{gdata['total_cost']:.2f}** | **{gdata['total_now']:.2f}** | | **{emoji}{gpnl:+.2f}** |")
        lines.append("")
    
    total_pnl = round(total_now - total_cost, 2)
    
    # 费用预估（假设全部赎回）
    from fund_fee_model import FEE_TABLE, calc_net_pnl
    total_fee = 0.0
    for code, v in values.items():
        info = FEE_TABLE.get(code)
        if info:
            # 假设持有≥7天（正常情况）
            fee = v["now_value"] * info["sell_pct_ge7d"] / 100.0
            total_fee += fee
    net_pnl = round(total_pnl - total_fee, 2)
    
    lines.append("---")
    lines.append(f"**总市值**: {total_now:.2f} 元 | **总成本**: {total_cost:.2f} 元 | **总盈亏**: {'📈' if total_pnl>=0 else '📉'}{total_pnl:+.2f} ({total_pnl/total_cost*100:+.2f}%)")
    if total_fee > 0:
        lines.append(f"  *(赎回过户费估约 {total_fee:.2f} 元, 净盈亏约 {net_pnl:+.2f})*")
    lines.append(f"*更新于 {datetime.now().isoformat()}*")
    return "\n".join(lines)

def main():
    print(f"📝 每日日志+市值 — {TODAY}")
    print()
    
    # 1. 计算持仓市值
    print("💰 计算持仓市值...")
    values = calc_portfolio_value()
    total_now = sum(v["now_value"] for v in values.values())
    total_cost = sum(v["cost_total"] for v in values.values())
    total_pnl = round(total_now - total_cost, 2)
    print(f"   总市值: {total_now:.2f}  总成本: {total_cost:.2f}  {'📈' if total_pnl>=0 else '📉'}{total_pnl:+.2f}")
    
    # 2. 生成持仓MD
    portfolio_md = build_portfolio_md(values)
    port_path = DATA_DIR / "portfolio" / f"portfolio-{TODAY}.md"
    port_path.parent.mkdir(parents=True, exist_ok=True)
    port_path.write_text(portfolio_md)
    r2_url = upload_to_r2(str(port_path), f"{FUND_SYSTEM_PREFIX}/data/portfolio/portfolio-{TODAY}.md", "text/markdown; charset=utf-8")
    print(f"   持仓MD -> {r2_url or 'ok'}")
    
    # 3. 价格快照
    snapshot = build_price_snapshot()
    snapshot["portfolio_value"] = round(total_now, 2)
    snapshot["portfolio_cost"] = round(total_cost, 2)
    snapshot["portfolio_pnl"] = round(total_pnl, 2)
    # 费用信息
    from fund_fee_model import FEE_TABLE
    total_fee = sum(v["now_value"] * FEE_TABLE.get(code, {}).get("sell_pct_ge7d", 0) / 100.0 
                     for code, v in values.items())
    snapshot["portfolio_fee_estimate"] = round(total_fee, 2)
    snapshot["portfolio_net_pnl"] = round(total_pnl - total_fee, 2)
    snapshot["portfolio_pnl_pct"] = round(total_pnl / total_cost * 100, 2) if total_cost > 0 else 0.0
    
    snap_path = DATA_DIR / "daily-snapshots.jsonl"
    with open(snap_path, 'a') as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + '\n')
    print(f"   快照已追加")
    r2_url = upload_to_r2(str(snap_path), f"{FUND_SYSTEM_PREFIX}/data/daily-snapshots.jsonl", "application/jsonl")
    
    # 4. 决策日志
    closing = get_latest_closing()
    decision = {
        "_date": TODAY,
        "_ts": datetime.now().isoformat(),
        "portfolio": {
            "total_value": round(total_now, 2),
            "total_cost": round(total_cost, 2),
            "total_pnl": total_pnl,
            "funds": {code: {"name": v["name"], "group": v["group"], "value": v["now_value"], "pnl": v["pnl"], "change_pct": v["today_change_pct"]} for code, v in values.items()},
        },
        "market_direction_accuracy": {
            "score": closing.get("market_score", "?"),
            "pct": closing.get("market_accuracy_pct"),
        } if closing else None,
        "verification_3d": "pending",
    }
    dec_path = DATA_DIR / "decisions.jsonl"
    with open(dec_path, 'a') as f:
        f.write(json.dumps(decision, ensure_ascii=False) + '\n')
    print(f"   决策日志已追加")
    r2_url = upload_to_r2(str(dec_path), f"{FUND_SYSTEM_PREFIX}/data/decisions.jsonl", "application/jsonl")
    
    print()
    print(f"📊 总市值: {total_now:.2f}  总盈亏: {total_pnl:+.2f}  {'📈' if total_pnl>=0 else '📉'}")

if __name__ == "__main__":
    main()
