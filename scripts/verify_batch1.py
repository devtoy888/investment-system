#!/usr/bin/env python3
"""
基金历史净值验证 — 第1批(5支大摩系列)
输出: 结构化 JSON
"""
import sys, os, json
from datetime import date, datetime

# AKShare path
_AKSHARE_DEPS = '/opt/data/akshare-deps'
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)
os.environ['TQDM_DISABLE'] = '1'
os.environ['AKSHARE_RAISE_ERR'] = 'False'

import akshare as ak

FUNDS = [
    ("017103", "大摩数字经济混合C"),
    ("011712", "大摩万众创新混合C"),
    ("026449", "大摩沪港深科技混合C"),
    ("014871", "大摩科技领先混合C"),
    ("020233", "大摩景气智选混合C"),
]

YEAR_START = date(2026, 1, 1)

def safe_float(v, default=0.0):
    if v is None:
        return default
    try:
        return float(str(v).replace('%', '').replace(',', ''))
    except:
        return default

def parse_date(d):
    if isinstance(d, (date, datetime)):
        return d if isinstance(d, date) else d.date()
    s = str(d).strip()[:10]
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))

def verify_one(code, name):
    result = {
        "code": code,
        "name": name,
        "status": "ok",
        "n_days": 0,
        "date_range": None,
        "first_date": None,
        "last_date": None,
        "nav_min": None,
        "nav_max": None,
        "nav_range": None,
        "ytd_pct": None,
        "total_ret_pct": None,
        "gaps": [],
        "extremes": [],
        "errors": [],
    }

    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is None or df.empty:
            result["status"] = "error"
            result["errors"].append("API returned empty")
            return result

        # Extract columns by name (not position)
        # Typical columns: 净值日期, 单位净值, 累计净值, 日增长率
        col_date = "净值日期"
        col_nav = "单位净值"

        if col_date not in df.columns or col_nav not in df.columns:
            result["status"] = "error"
            result["errors"].append(f"Missing expected columns. Found: {list(df.columns)}")
            return result

        rows = df.to_dict('records')
        n = len(rows)
        if n == 0:
            result["status"] = "error"
            result["errors"].append("0 rows")
            return result

        # Parse all rows
        nav_dates = []
        nav_values = []
        for row in rows:
            d = parse_date(row[col_date])
            v = safe_float(row[col_nav])
            if v <= 0:
                continue
            nav_dates.append(d)
            nav_values.append(v)

        n = len(nav_dates)
        result["n_days"] = n
        if n < 2:
            result["status"] = "error"
            result["errors"].append(f"Only {n} valid data points after filtering")
            return result

        result["first_date"] = str(nav_dates[0])
        result["last_date"] = str(nav_dates[-1])
        result["date_range"] = f"{nav_dates[0]} ~ {nav_dates[-1]}"
        result["nav_min"] = round(min(nav_values), 4)
        result["nav_max"] = round(max(nav_values), 4)
        result["nav_range"] = f"{result['nav_min']:.4f} ~ {result['nav_max']:.4f}"

        # --- Gap detection (>7 days between adjacent dates) ---
        for i in range(1, n):
            diff = (nav_dates[i] - nav_dates[i-1]).days
            if diff > 7:
                result["gaps"].append({
                    "from": str(nav_dates[i-1]),
                    "to": str(nav_dates[i]),
                    "days": diff,
                })

        # --- Extreme change detection (>15% between adjacent days) ---
        for i in range(1, n):
            if nav_values[i-1] > 0:
                chg = (nav_values[i] / nav_values[i-1] - 1) * 100
                if abs(chg) > 15:
                    result["extremes"].append({
                        "date": str(nav_dates[i]),
                        "change_pct": round(chg, 2),
                    })

        # --- YTD (2026-01-01 onward) ---
        ytd_pairs = [
            (d, v) for d, v in zip(nav_dates, nav_values)
            if d >= YEAR_START
        ]
        if len(ytd_pairs) >= 2:
            result["ytd_pct"] = round(
                (ytd_pairs[-1][1] / ytd_pairs[0][1] - 1) * 100, 2
            )
        elif len(ytd_pairs) == 1:
            result["ytd_pct"] = 0.0
            result["errors"].append("Only 1 YTD data point")

        # --- Total return (all time) ---
        if nav_values[0] > 0:
            result["total_ret_pct"] = round(
                (nav_values[-1] / nav_values[0] - 1) * 100, 2
            )

        # --- Status determination ---
        if result["gaps"] or result["extremes"]:
            result["status"] = "warning"
        if n < 30:
            result["status"] = "warning"
            result["errors"].append(f"Low data count: {n} days")

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"{type(e).__name__}: {str(e)}")

    return result

# ── Main ──
results = []
for code, name in FUNDS:
    print(f"\n{'='*50}")
    print(f"Verifying: [{code}] {name}")
    r = verify_one(code, name)
    results.append(r)

    status_emoji = {"ok": "✅", "warning": "⚠️", "error": "❌"}.get(r["status"], "❓")
    print(f"  Status: {status_emoji} {r['status']}")
    print(f"  Days: {r['n_days']}")
    print(f"  Date Range: {r['date_range']}")
    print(f"  NAV Range: {r['nav_range']}")
    print(f"  YTD: {r['ytd_pct']}%")
    print(f"  Total Return: {r['total_ret_pct']}%")
    print(f"  Gaps: {len(r['gaps'])}")
    if r["gaps"]:
        for g in r["gaps"]:
            print(f"    ⚠ gap {g['from']} → {g['to']} ({g['days']}d)")
    print(f"  Extremes: {len(r['extremes'])}")
    if r["extremes"]:
        for e in r["extremes"]:
            print(f"    ⚠ {e['date']}: {e['change_pct']:+.2f}%")
    if r["errors"]:
        for e in r["errors"]:
            print(f"  ❌ {e}")

# ── Output JSON ──
output_json = {
    "batch": 1,
    "series": "大摩系列",
    "verification_date": str(date.today()),
    "funds": results,
    "summary": {
        "total": len(results),
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "warning": sum(1 for r in results if r["status"] == "warning"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "total_gaps": sum(len(r["gaps"]) for r in results),
        "total_extremes": sum(len(r["extremes"]) for r in results),
    },
}

print(f"\n{'='*60}")
print("SUMMARY")
print(f"  Total: {output_json['summary']['total']}")
print(f"  OK: {output_json['summary']['ok']}")
print(f"  Warning: {output_json['summary']['warning']}")
print(f"  Error: {output_json['summary']['error']}")
print(f"  Total Gaps: {output_json['summary']['total_gaps']}")
print(f"  Total Extremes: {output_json['summary']['total_extremes']}")

# Write JSON file
output_path = "/opt/data/fund_system_data/strategy/batch1_morgan_stanley.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output_json, f, ensure_ascii=False, indent=2)
print(f"\n📄 Results written to: {output_path}")
