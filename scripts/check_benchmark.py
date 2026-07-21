#!/usr/bin/env python3
"""
基准对比检测 — 组合 vs 沪深300
输出: "今日沪深300涨X%，你的组合涨Y% — 跑赢/跑输Z%"
仅在有数据时输出一行，空=静默不推送。
"""
import sys, json
sys.path.insert(0, '/opt/data/scripts')
from pathlib import Path
from datetime import date
from fund_tools import get_tencent_quote

today = date.today().isoformat()
FUND_SYSTEM_DIR = Path("/opt/data/fund_system_data")

def main():
    # 1. 获取沪深300今日涨跌
    hs300 = get_tencent_quote('sh000300')
    if not hs300:
        hs300 = get_tencent_quote('sz399300')  # 备援
    if not hs300:
        hs300_pct = None
    else:
        hs300_pct = float(hs300.get('change_pct', 0) or 0)
    
    if hs300_pct is None:
        return  # 静默

    # 2. 获取组合今日盈亏（从 daily-snapshots.jsonl 最新一条）
    portfolio_pct = None
    snapshots_file = FUND_SYSTEM_DIR / "daily-snapshots.jsonl"
    if snapshots_file.exists():
        lines = [l.strip() for l in snapshots_file.read_text().split('\n') if l.strip()]
        if lines:
            last = json.loads(lines[-1])
            portfolio_pct = last.get("portfolio_pnl_pct")

    # 3. 如果 snapshots 没有，从 decisions.jsonl 拿
    if portfolio_pct is None:
        decisions_file = FUND_SYSTEM_DIR / "decisions.jsonl"
        if decisions_file.exists():
            lines = [l.strip() for l in decisions_file.read_text().split('\n') if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                portfolio_pct = last.get("portfolio_pnl_pct")

    # 4. 输出
    if portfolio_pct is not None:
        diff = portfolio_pct - hs300_pct
        win = "跑赢" if diff > 0 else "跑输" if diff < 0 else "持平"
        print(f"\n📊 **基准对比 — {today}**")
        print(f"  沪深300: {hs300_pct:+.2f}%")
        print(f"  你的组合: {portfolio_pct:+.2f}%")
        print(f"  {'✅' if diff > 0 else '⚠️' if diff < 0 else '➖'} {win}大盘 {abs(diff):.2f}%")
    else:
        print(f"\n📊 **基准对比 — {today}**")
        print(f"  沪深300: {hs300_pct:+.2f}%")
        print(f"  你的组合: 暂无盈亏数据（运行一次收盘任务后自动生成）")

if __name__ == "__main__":
    main()
