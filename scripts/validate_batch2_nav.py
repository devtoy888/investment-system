#!/usr/bin/env python3
"""基金历史净值验证 — 第2批(5支: 华夏+LOF)"""

import sys, os, json, time
from datetime import date, datetime

# AKShare dependencies
_AKSHARE_DEPS = "/opt/data/akshare-deps"
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)

os.environ["TQDM_DISABLE"] = "1"

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError as e:
    print(f"ERROR: Cannot import akshare: {e}")
    sys.exit(1)

FUNDS = {
    "011613": "华夏科创50ETF联接C",
    "024418": "华夏半导体材料ETF联接C",
    "025857": "华夏电网设备ETF联接C",
    "013403": "华夏恒生科技联接C",
    "163302": "大摩资源优选混合LOF",
}

YTD_START = date(2026, 1, 1)
TODAY = date.today()

def validate_fund(code, name):
    """Validate a single fund's historical NAV data."""
    result = {
        "code": code,
        "name": name,
        "status": "ok",
        "errors": [],
        "warnings": [],
    }
    
    try:
        print(f"  Fetching {code} {name} ...", end=" ", flush=True)
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        print(f"got {len(df)} rows")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"API call failed: {e}")
        return result
    
    if df is None or df.empty:
        result["status"] = "error"
        result["errors"].append("Empty dataframe returned")
        return result
    
    # --- Basic stats ---
    result["total_days"] = len(df)
    
    # Columns vary by AKShare version, find the date and NAV columns
    date_col = None
    nav_col = None
    for col in df.columns:
        if "净值日期" in col or col == "净值日期":
            date_col = col
        if "单位净值" in col or col == "单位净值":
            nav_col = col
    
    if date_col is None or nav_col is None:
        result["status"] = "error"
        result["errors"].append(f"Could not find required columns. Got: {list(df.columns)}")
        return result
    
    # Convert date column to datetime.date
    dates_raw = df[date_col]
    try:
        dates = pd.to_datetime(dates_raw).dt.date
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Date conversion failed: {e}")
        return result
    
    # Check date type
    date_type_ok = all(isinstance(d, date) for d in dates)
    result["date_type"] = "datetime.date" if date_type_ok else "MIXED/WRONG"
    if not date_type_ok:
        result["errors"].append(f"date column is not all datetime.date objects")
    
    # Convert NAV to float
    navs = pd.to_numeric(df[nav_col], errors="coerce")
    
    # --- Date checks ---
    result["date_range"] = {
        "earliest": str(dates.min()),
        "latest": str(dates.max()),
    }
    
    # --- NAV range ---
    valid_navs = navs.dropna()
    if len(valid_navs) > 0:
        result["nav_range"] = {
            "min": round(float(valid_navs.min()), 6),
            "max": round(float(valid_navs.max()), 6),
        }
        result["nav_latest"] = round(float(valid_navs.iloc[-1]), 6)
    else:
        result["errors"].append("No valid NAV values")
    
    # --- Gap detection (adjacent days > 7) ---
    sorted_dates = sorted(dates.dropna().unique())
    gaps = []
    for i in range(1, len(sorted_dates)):
        delta = (sorted_dates[i] - sorted_dates[i-1]).days
        if delta > 7:
            gaps.append({
                "from": str(sorted_dates[i-1]),
                "to": str(sorted_dates[i]),
                "gap_days": delta,
            })
    result["gaps"] = gaps
    result["gap_count"] = len(gaps)
    if gaps:
        result["warnings"].append(f"Found {len(gaps)} gaps > 7 days (largest: {max(g['gap_days'] for g in gaps)} days)")
    
    # --- Abnormal daily change (>15%) ---
    anomalies = []
    nav_series = pd.Series(valid_navs.values, index=dates.values) if not valid_navs.empty else pd.Series(dtype=float)
    # Reindex to align with sorted dates
    if len(nav_series) > 1:
        nav_aligned = pd.Series(dtype=float)
        for d in sorted_dates:
            if d in nav_series.index:
                nav_aligned[d] = nav_series[d]
        
        prev_navs = nav_aligned.shift(1)
        pct_changes = (nav_aligned - prev_navs) / prev_navs.abs() * 100
        
        for d, pct in pct_changes.items():
            if pd.notna(pct) and abs(pct) > 15:
                anomalies.append({
                    "date": str(d),
                    "change_pct": round(float(pct), 2),
                    "nav": round(float(nav_aligned[d]), 6),
                    "prev_nav": round(float(prev_navs[d]), 6),
                })
    
    result["anomalies"] = anomalies
    result["anomaly_count"] = len(anomalies)
    if anomalies:
        result["warnings"].append(f"Found {len(anomalies)} daily changes > 15%")
    
    # --- YTD return ---
    ytd_start = max(YTD_START, sorted_dates[0]) if sorted_dates else YTD_START
    # Find closest date to YTD_START
    ytd_rows = [(d, nav_aligned[d]) for d in sorted_dates if d >= ytd_start]
    if len(ytd_rows) >= 2:
        first_ytd_date, first_ytd_nav = ytd_rows[0]
        last_ytd_date, last_ytd_nav = ytd_rows[-1]
        ytd_return = (last_ytd_nav / first_ytd_nav - 1) * 100
        result["ytd"] = {
            "start_date": str(first_ytd_date),
            "start_nav": round(float(first_ytd_nav), 6),
            "end_date": str(last_ytd_date),
            "end_nav": round(float(last_ytd_nav), 6),
            "return_pct": round(float(ytd_return), 2),
            "days_in_range": len(ytd_rows),
        }
    else:
        result["ytd"] = {"error": "Insufficient YTD data"}
    
    return result


if __name__ == "__main__":
    import pandas as pd
    
    results = {}
    
    print(f"=== 基金历史净值验证 — 第2批 (5支) ===")
    print(f"验证日期: {TODAY}\n")
    
    for code, name in FUNDS.items():
        r = validate_fund(code, name)
        results[code] = r
        
        # Print summary
        status_icon = "✅" if r["status"] == "ok" else "❌"
        print(f"  {status_icon} {code} {name}")
        if r["status"] == "ok":
            print(f"    天数: {r['total_days']}, 日期范围: {r['date_range']['earliest']} ~ {r['date_range']['latest']}")
            if "nav_range" in r:
                print(f"    净值范围: {r['nav_range']['min']} ~ {r['nav_range']['max']}, 最新: {r['nav_latest']}")
            print(f"    缺口(>7天): {r['gap_count']}, 异常(>15%): {r['anomaly_count']}")
            if "ytd" in r and "return_pct" in r["ytd"]:
                print(f"    YTD: {r['ytd']['return_pct']:+.2f}% (from {r['ytd']['start_date']}, {r['ytd']['days_in_range']} trading days)")
            elif "ytd" in r:
                print(f"    YTD: {r['ytd'].get('error', 'N/A')}")
            if r["warnings"]:
                for w in r["warnings"]:
                    print(f"    ⚠️  {w}")
        else:
            for e in r["errors"]:
                print(f"    ❌ {e}")
        print()
        
        # Rate limit
        time.sleep(2)
    
    # Save JSON
    output_path = "/opt/data/scripts/batch2_nav_validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n完整结果已保存到: {output_path}")
    
    # Summary
    ok_count = sum(1 for r in results.values() if r["status"] == "ok")
    print(f"\n=== 总结: {ok_count}/{len(results)} 支基金验证通过 ===")
