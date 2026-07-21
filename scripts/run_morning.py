#!/usr/bin/env python3
"""Wrapper: morning briefing v2 — 动态持仓 + KOL/HTML推送"""
import subprocess, sys, os, json
from pathlib import Path
from datetime import date, timedelta

os.chdir('/opt/data/scripts')

# Step 1: 数据采集
r1 = subprocess.run([sys.executable, 'collect_morning_data.py'], capture_output=True, text=True, timeout=180)
if r1.stderr:
    print(r1.stderr, file=sys.stderr)

# Step 2: 获取数据表
tables = ""
push_file = Path("/tmp/fund_data/_morning_tables.md")
if push_file.exists():
    tables = push_file.read_text().strip()

# Step 3: 构建含完整KOL + 真实持仓的数据
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import FUND_CODES
from llm_analysis_v2 import BUILDING_FUNDS, build_morning_data_v2, call_ds
from push_report_r2 import push_report

# 获取完整KOL内容
kol_full = ""
kol_file = Path("/tmp/fund_data/_kol_summary.txt")
if kol_file.exists():
    kol_full = kol_file.read_text().strip()
kol_full = kol_full[:3000] if len(kol_full) > 3000 else kol_full

# 获取真实持仓盈亏
pnl_data = ""
ops_dir = Path("/opt/data/fund_system_data/operations")
if ops_dir.exists():
    today_str = date.today().isoformat()
    ops_file = ops_dir / f"operation_{today_str}.md"
    if ops_file.exists():
        pnl_data = ops_file.read_text()
    if not pnl_data:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        ops_file = ops_dir / f"operation_{yesterday}.md"
        if ops_file.exists():
            pnl_data = ops_file.read_text()

# 动态构建持仓描述（从FUND_CODES读取，自动反映持仓变化）
sector_map = {
    '009478':'黄金', '011613':'科技', '024418':'科技', '026449':'科技',
    '014871':'科技', '020233':'科技', '017103':'科技', '011712':'科技',
    '163302':'资源', '025857':'资源', '012329':'新能源', '011103':'新能源',
    '003096':'医药', '013403':'恒生科技',
}
sector_counts = {}
for code, sec in sector_map.items():
    sector_counts[sec] = sector_counts.get(sec, 0) + 1
sector_summary = "；".join([f"{sec}{n}支" for sec, n in sector_counts.items()])

building_list = [f"{c} {FUND_CODES[c]}" for c in FUND_CODES if c in BUILDING_FUNDS]
building_str = "、".join(building_list) if building_list else ""
building_note = f"（🏗️建仓中：{building_str}）" if building_str else ""

MORNING_PROMPT = f"""## 【操作约束】
1. 买入卖出按**当日收盘净值**计算，15:00前下单按今日净值
2. 资金T+2到账。建仓期{', '.join(BUILDING_FUNDS)}仅允许持有或加仓
3. 所有操作建议标明"15:00前"还是"明日计划"

## 【持仓数据】
当前持有{len(FUND_CODES)}支基金：{sector_summary}{building_note}

## 【分析指令】
开盘前分析，5步完成。**第5步必须结合具体持仓盈亏和KOL观点来给建议**：

1.【隔夜信号】简要列外盘传导
2.【昨日复盘】特征+预测验证
3.【今日作战】按主线给方向
4.【风险清单】
5.【基金优先级·详细】逐支给出理由+操作方向。**下面的KOL观点和持仓盈亏数据必须被引用到你的分析中，特别是第5步的决策依据里要体现**

## 【今日KOL核心观点】
""" + (kol_full[:2000] if kol_full else "暂无") + """

## 【当前持仓盈亏】
""" + (pnl_data[:1500] if pnl_data else "暂无操作记录，请基于行情数据分析") + """

请给出完整分析，确保第5步每一支基金的操作建议都引用KOL观点或持仓数据作为决策依据。"""

data = build_morning_data_v2()

analysis = call_ds(MORNING_PROMPT, data, max_tokens=8000, temp=0.3)
if analysis:
    analysis = analysis.replace("<br>", "\n")
    md_link, html_link = push_report("morning", f"财经早餐 · 基金参考 · {date.today()}", tables, analysis)
    print(f"✅ 早报已上传: {html_link}", file=sys.stderr)
