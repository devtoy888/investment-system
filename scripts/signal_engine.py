#!/usr/bin/env python3
"""
Signal Engine — 通用加仓信号引擎
读取 signal_rules.yaml 配置，批量评估所有信号规则。
输出为空 = 无信号；输出非空 = 有信号要推送。
"""
import os, sys, json, math, yaml
sys.path.insert(0, '/opt/data/scripts')
from pathlib import Path
from datetime import date
from typing import Any
from fund_tools import get_fund_value, get_tencent_quote

# ── 配置路径 ──
RULES_PATH = Path("/opt/data/fund_system_data/evolution/signal_rules.yaml")
today = date.today().isoformat()

# ── 条件评估器 ──
def _get_fund_ctx(code: str) -> dict | None:
    """获取一只基金的上下文数据（净值/估算/涨跌）"""
    v = get_fund_value(code)
    if not v:
        return None
    try:
        ec = float(v.get('estimated_change', '?'))
        if math.isnan(ec) or math.isinf(ec):
            ec = None
    except:
        ec = None
    return {
        "nav": v.get('nav', '?'),
        "enav": v.get('estimated_nav', '?'),
        "ec": ec,
    }

def _get_benchmark_ctx(code: str) -> dict | None:
    """获取基准ETF的上下文数据"""
    if not code:
        return None
    q = get_tencent_quote(code)
    if not q:
        return None
    price = float(q.get('price', 0) or 0)
    high = float(q.get('high', 0) or 0)
    low = float(q.get('low', 0) or 0)
    prev = float(q.get('prev_close', 0) or 1)
    amp = (high - low) / prev * 100 if prev > 0 else 0
    chg = float(q.get('change_pct', 0) or 0)
    return {"price": price, "high": high, "low": low, "amp": amp, "pct": chg}

def _eval_cond(cond: dict, fund_ctx: dict, bench_ctx: dict | None) -> bool:
    """评估单条条件"""
    typ = cond.get("type", "")
    op = cond.get("operator", "==")
    val = cond.get("value", 0)

    # 获取条件所需的实际值
    if typ == "estimated_change":
        actual = fund_ctx.get("ec")
    elif typ == "benchmark_price":
        actual = bench_ctx.get("price") if bench_ctx else None
    elif typ == "benchmark_change":
        actual = bench_ctx.get("pct") if bench_ctx else None
    elif typ == "benchmark_amplitude":
        actual = bench_ctx.get("amp") if bench_ctx else None
    else:
        return False

    if actual is None:
        return False

    try:
        actual_f = float(actual)
    except:
        return False

    if op == ">":    return actual_f > val
    if op == ">=":   return actual_f >= val
    if op == "<":    return actual_f < val
    if op == "<=":   return actual_f <= val
    if op == "==":   return math.isclose(actual_f, val, rel_tol=1e-6)
    return False

def _fmt_msg(template: str, fund_ctx: dict, bench_ctx: dict | None) -> str:
    """格式化消息模板"""
    fmt = {
        "nav": fund_ctx.get("nav", "?"),
        "enav": fund_ctx.get("enav", "?"),
        "ec": fund_ctx.get("ec") or 0,
        "bk_price": bench_ctx.get("price", "?") if bench_ctx else "?",
        "bk_pct": bench_ctx.get("pct", 0) if bench_ctx else 0,
        "bk_amp": bench_ctx.get("amp", 0) if bench_ctx else 0,
    }
    return template.format(**fmt)

def main():
    # 加载规则
    if not RULES_PATH.exists():
        print(f"[ERR] 规则文件不存在: {RULES_PATH}")
        return
    rules = yaml.safe_load(RULES_PATH.read_text()).get("rules", [])

    triggered = []

    # 逐条评估规则
    for rule in rules:
        rid = rule.get("id", "?")
        fcode = rule.get("fund_code")
        bcode = rule.get("benchmark_code")

        fund_ctx = _get_fund_ctx(fcode)
        if fund_ctx is None:
            continue

        bench_ctx = _get_benchmark_ctx(bcode) if bcode else None

        # 评估全部条件（AND逻辑）
        all_pass = True
        for cond in rule.get("conditions", []):
            if not _eval_cond(cond, fund_ctx, bench_ctx):
                all_pass = False
                break

        if all_pass:
            msg = _fmt_msg(rule.get("message", ""), fund_ctx, bench_ctx)
            triggered.append(msg)

    # 输出
    if triggered:
        print(f"🔔 {today} 持仓加仓信号监测")
        print("=" * 40)
        for msg in triggered:
            print()
            print(msg)
    # else: 静默，不推送

if __name__ == "__main__":
    main()
