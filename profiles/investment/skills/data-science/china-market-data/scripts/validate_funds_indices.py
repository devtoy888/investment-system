#!/usr/bin/env python3
"""
基金+指数全量验证脚本
====================
批量验证基金的 fund_open_fund_info_em 和指数的 stock_zh_index_daily。
检查: 天数、日期范围、YTD、缺口>7天(基金)、涨跌>15%(基金)/>10%(指数)

用法: 修改 FUNDS / INDICES 字典后直接运行
"""

import os
import sys
import json
import time
from datetime import date, datetime, timedelta

_AKSHARE_DEPS = "/opt/data/akshare-deps"
if os.path.isdir(_AKSHARE_DEPS) and _AKSHARE_DEPS not in sys.path:
    sys.path.insert(0, _AKSHARE_DEPS)
os.environ["TQDM_DISABLE"] = "1"

import akshare as ak
import pandas as pd

TODAY = date.today()
YEAR_START = date(TODAY.year, 1, 1)


def fmt_date(d):
    if isinstance(d, (date, datetime)):
        return d.isoformat()
    return str(d)


def check_gaps_and_spikes(df, date_col, nav_col, change_col):
    gaps, spikes = [], []
    df = df.sort_values(date_col).reset_index(drop=True)
    for i in range(1, len(df)):
        d1 = pd.to_datetime(df.iloc[i - 1][date_col]).date()
        d2 = pd.to_datetime(df.iloc[i][date_col]).date()
        diff = (d2 - d1).days
        if diff > 7:
            gaps.append({"from": fmt_date(d1), "to": fmt_date(d2), "gap_days": diff})
    for i in range(len(df)):
        try:
            chg = float(df.iloc[i][change_col])
        except (ValueError, TypeError):
            continue
        if abs(chg) > 15:
            spikes.append({"date": fmt_date(pd.to_datetime(df.iloc[i][date_col]).date()), "change_pct": round(chg, 4)})
    return gaps, spikes


def validate_fund(code, name):
    result = {"code": code, "name": name, "type": "fund", "status": "pending",
              "days": 0, "date_range": {}, "ytd_pct": None,
              "anomalies": {"gaps_gt_7d": [], "spikes_gt_15pct": []}, "error": None}
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is None or df.empty:
            result["status"] = "empty"; result["error"] = "Empty DataFrame"; return result

        # 列名探测：排除"日期"避免 "净值" in "净值日期" 误匹配
        date_col = next((c for c in df.columns if "日期" in c), df.columns[0])
        nav_col = next((c for c in df.columns if "净值" in c and "日期" not in c), None)
        if nav_col is None:
            nav_col = next((c for c in df.columns if "单位" in c and "日期" not in c), df.columns[1])
        change_col = next((c for c in df.columns if "增长" in c or "涨幅" in c or "涨跌" in c), None)

        df_valid = df[df[nav_col].notna() & (df[nav_col] != "")].copy()
        df_valid[date_col] = pd.to_datetime(df_valid[date_col])
        df_valid = df_valid.sort_values(date_col).reset_index(drop=True)

        n = len(df_valid); result["days"] = n
        if n > 0:
            result["date_range"] = {"first": fmt_date(df_valid.iloc[0][date_col].date()),
                                     "last": fmt_date(df_valid.iloc[-1][date_col].date())}
            df_ytd = df_valid[df_valid[date_col].dt.date >= YEAR_START]
            if len(df_ytd) > 0:
                first_nav = float(df_ytd.iloc[0][nav_col])
                last_nav = float(df_ytd.iloc[-1][nav_col])
                result["ytd_pct"] = round((last_nav / first_nav - 1) * 100, 2)
            if change_col and change_col in df_valid.columns:
                gaps, spikes = check_gaps_and_spikes(df_valid, date_col, nav_col, change_col)
                result["anomalies"]["gaps_gt_7d"] = gaps
                result["anomalies"]["spikes_gt_15pct"] = spikes
        result["status"] = "ok"
    except Exception as e:
        result["status"] = "error"; result["error"] = str(e)
    return result


def validate_index(code, name):
    result = {"code": code, "name": name, "type": "index", "status": "pending",
              "days": 0, "date_range": {}, "ytd_pct": None,
              "anomalies": {"spikes_gt_10pct": []}, "error": None}
    try:
        df = ak.stock_zh_index_daily(symbol=code)
        if df is None or df.empty:
            result["status"] = "empty"; result["error"] = "Empty DataFrame"; return result
        date_col = "date" if "date" in df.columns else df.columns[0]
        close_col = "close" if "close" in df.columns else df.columns[4]
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        n = len(df); result["days"] = n
        if n > 0:
            result["date_range"] = {"first": fmt_date(df.iloc[0][date_col].date()),
                                     "last": fmt_date(df.iloc[-1][date_col].date())}
            df_ytd = df[df[date_col].dt.date >= YEAR_START]
            if len(df_ytd) > 0:
                first_close = float(df_ytd.iloc[0][close_col])
                last_close = float(df_ytd.iloc[-1][close_col])
                result["ytd_pct"] = round((last_close / first_close - 1) * 100, 2)
            for i in range(1, n):
                prev_close = float(df.iloc[i - 1][close_col])
                curr_close = float(df.iloc[i][close_col])
                if prev_close > 0:
                    change = (curr_close / prev_close - 1) * 100
                    if abs(change) > 10:
                        result["anomalies"]["spikes_gt_10pct"].append({
                            "date": fmt_date(df.iloc[i][date_col].date()),
                            "change_pct": round(change, 4)
                        })
        result["status"] = "ok"
    except Exception as e:
        result["status"] = "error"; result["error"] = str(e)
    return result


# ═══════ 配置区 ═══════
FUNDS = {
    "009478": "中银上海金ETF联接C",
    "012329": "天弘新能源指数增强C",
    "011103": "天弘中证光伏C",
    "003096": "中欧医疗健康混合C",
}

INDICES = {
    "sh000001": "上证指数",  "sh000300": "沪深300",
    "sh000688": "科创50",   "sz399006": "创业板指",
    "sh000016": "上证50",   "sz399989": "中证医疗",
    "sz399967": "中证半导体", "sz399997": "中证白酒",
    "sz399932": "中证消费",
}


def main():
    output = {"validation_time": datetime.now().isoformat(), "validation_date": fmt_date(TODAY),
              "funds": [], "indices": [], "summary": {}}

    for code, name in FUNDS.items():
        print(f"  [{code}] {name} ...", end=" ", flush=True)
        r = validate_fund(code, name)
        print(f"{r['status'].upper()} | {r['days']}天 | YTD: {r['ytd_pct']}%")
        gaps_n = len(r["anomalies"]["gaps_gt_7d"])
        spikes_n = len(r["anomalies"]["spikes_gt_15pct"])
        if gaps_n: print(f"    ⚠️ 缺口>7天: {gaps_n}处")
        if spikes_n: print(f"    ⚠️ 涨跌>15%: {spikes_n}处")
        if r.get("error"): print(f"    ❌ {r['error'][:100]}")
        output["funds"].append(r)
        time.sleep(1.5)

    for code, name in INDICES.items():
        print(f"  [{code}] {name} ...", end=" ", flush=True)
        r = validate_index(code, name)
        print(f"{r['status'].upper()} | {r['days']}天 | YTD: {r['ytd_pct']}%")
        spikes_n = len(r["anomalies"]["spikes_gt_10pct"])
        if spikes_n: print(f"    ⚠️ 涨跌>10%: {spikes_n}处")
        if r.get("error"): print(f"    ❌ {r['error'][:100]}")
        output["indices"].append(r)
        time.sleep(0.8)

    fund_ok = sum(1 for f in output["funds"] if f["status"] == "ok")
    idx_ok = sum(1 for i in output["indices"] if i["status"] == "ok")
    fund_gaps = sum(len(f["anomalies"].get("gaps_gt_7d", [])) for f in output["funds"])
    fund_spikes = sum(len(f["anomalies"].get("spikes_gt_15pct", [])) for f in output["funds"])
    idx_spikes = sum(len(i["anomalies"].get("spikes_gt_10pct", [])) for i in output["indices"])

    output["summary"] = {
        "funds_ok": fund_ok, "funds_error": len(FUNDS) - fund_ok, "funds_total": len(FUNDS),
        "indices_ok": idx_ok, "indices_error": len(INDICES) - idx_ok, "indices_total": len(INDICES),
        "fund_gaps_gt_7d": fund_gaps, "fund_spikes_gt_15pct": fund_spikes,
        "index_spikes_gt_10pct": idx_spikes,
    }

    out_path = "/tmp/validate_funds_indices.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✅ 完整结果: {out_path}")
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
