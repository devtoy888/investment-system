#!/usr/bin/env python3
"""
风险预警系统 — 收盘后运行
检查: 单日跌>5% | 连跌3日
无预警则静默（不输出 = 不推送）
"""
import sys, json, os
sys.path.insert(0, '/opt/data/scripts')
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict

DATA_DIR = Path("/opt/data/fund_system_data")
TREND_FILE = DATA_DIR / "fund-daily-trend.jsonl"

# 监控的全部基金
WATCHED_FUNDS = {
    "011613": "华夏科创50ETF联接C",
    "024418": "华夏上证科创板半导体材料设备ETF联接C",
    "011712": "大摩万众创新混合C",
    "026449": "大摩沪港深科技混合C",
    "017103": "大摩数字经济混合C",
    "020233": "大摩景气智选混合C",
    "014871": "大摩科技领先混合C",
    "025857": "华夏中证电网设备ETF联接C",
    "163302": "大摩资源优选混合(LOF)",
    "012329": "天弘中证新能源指数增强C",
    "011103": "天弘中证光伏C",
    "009478": "中银上海金ETF联接C",
    # 7/16 新增
    "003096": "中欧医疗健康混合C",
    "013403": "华夏恒生科技ETF联接(QDII)C",
}

def out(s=""):
    print(s)

def get_current_fund_changes():
    """从 fund_data 获取今日基金估算涨跌"""
    try:
        from fund_tools import get_fund_value
        changes = {}
        for code, name in WATCHED_FUNDS.items():
            r = get_fund_value(code)
            if r:
                try:
                    est = float(r.get('gszzl', r.get('estimated_change', 0)))
                    changes[code] = est
                except:
                    changes[code] = None
            else:
                changes[code] = None
        return changes
    except Exception as e:
        out(f"  ⚠️ 获取基金数据失败: {e}")
        return {}

def read_trend():
    """读取历史日趋势"""
    if not TREND_FILE.exists():
        return []
    records = []
    for line in TREND_FILE.read_text().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except:
            continue
    return records

def append_trend(today_changes):
    """追加今日趋势数据"""
    record = {
        "_date": date.today().isoformat(),
        "_ts": datetime.now().isoformat(),
        "changes": {k: v for k, v in today_changes.items() if v is not None},
    }
    TREND_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TREND_FILE, 'a') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    return record

def main():
    today = date.today()
    
    # 获取今日涨跌
    changes = get_current_fund_changes()
    if not changes:
        out("")
        return
    
    # 追加趋势
    today_record = append_trend(changes)
    
    # 读取历史趋势
    trend = read_trend()
    
    alerts = []
    
    # 1️⃣ 单日 > 5% 暴跌检测
    for code, chg in changes.items():
        if chg is None:
            continue
        if chg <= -5:
            name = WATCHED_FUNDS.get(code, code)
            alerts.append(f"🔴 {name}({code}) 单日暴跌 {chg:.2f}%，超过5%阈值")
        elif chg <= -3:
            name = WATCHED_FUNDS.get(code, code)
            alerts.append(f"⚠️ {name}({code}) 当日大跌 {chg:.2f}%")
    
    # 2️⃣ 连跌3日检测（同一天多次采集只取最后一次做代表）
    # 按基金代码整理: code -> {date: change}
    hist = defaultdict(dict)
    for rec in trend:
        d = rec.get("_date", "")
        for code, chg in rec.get("changes", {}).items():
            if chg is not None:
                hist[code][d] = chg  # 同一天后来的覆盖前面的
    
    for code, date_changes in hist.items():
        # 按日期排序，取最近5个交易日
        sorted_dates = sorted(date_changes.keys())
        recent = [(d, date_changes[d]) for d in sorted_dates[-5:]]
        if len(recent) < 3:
            continue
        # 取最近连续3天检测
        last3 = recent[-3:]
        # 检查是否连跌3天
        if all(v[1] < 0 for v in last3):
            total_chg = sum(v[1] for v in last3)
            name = WATCHED_FUNDS.get(code, code)
            days_str = ", ".join(f"{v[0]}({v[1]:.2f}%)" for v in last3)
            severity = "🔴" if total_chg <= -10 else "⚠️"
            alerts.append(f"{severity} {name}({code}) 连跌3天: {days_str}, 累计{total_chg:.2f}%")
    
    # 输出
    if not alerts:
        out("")
        return
    
    out(f"🚨 **风险预警 — {today}**")
    out()
    for alert in alerts:
        out(f"  {alert}")
    out()
    out(f"💡 数据来源: 今日基金实时估算 ± {TREND_FILE} 历史趋势")
    
    # 同步到R2
    try:
        from fund_tools import upload_to_r2, FUND_SYSTEM_PREFIX
        upload_to_r2(str(TREND_FILE), f"{FUND_SYSTEM_PREFIX}/data/fund-daily-trend.jsonl", "application/jsonl")
    except:
        pass

if __name__ == "__main__":
    main()
