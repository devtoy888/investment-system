#!/usr/bin/env python3
"""午报 — R2推送 + 文本摘要版
Stdout输出：文本摘要 + R2链接（供cron deliver展示到QQ Bot）"""
import subprocess, sys, os, re, io
from pathlib import Path
from datetime import date, datetime

os.chdir('/opt/data/scripts')
SUMMARY_DIR = Path("/tmp/fund_data")

# Step 1: 午盘数据采集
r1 = subprocess.run([sys.executable, 'collect_noon_data.py'], capture_output=True, text=True, timeout=180)
if r1.stderr:
    print(r1.stderr, file=sys.stderr)

# Check if non-trading day
if os.path.exists(f"{SUMMARY_DIR}/_noon_skip.txt"):
    skip_reason = open(f"{SUMMARY_DIR}/_noon_skip.txt").read().strip()
    print(f"⏭️ {skip_reason}")
    sys.exit(0)

# Step 2: 数据表
r2 = subprocess.run([sys.executable, 'send_noon.py'], capture_output=True, text=True, timeout=60)
tables = r2.stdout.strip() if r2.stdout.strip() else ""
if r2.stderr:
    print(r2.stderr, file=sys.stderr)

# Step 3: R2推送LLM分析
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import FUND_CODES
from llm_analysis_v2 import T1_FRAMEWORK, build_noon_data_v2, call_ds, BUILDING_FUNDS
from push_report_r2 import push_report

data = build_noon_data_v2()
# 动态构建持仓列表（从FUND_CODES读取，操作记录驱动）
portfolio_list_lines = []
for code, name in FUND_CODES.items():
    flag = "🏗️建仓期" if code in BUILDING_FUNDS else ""
    portfolio_list_lines.append(f"  {code} {name} {flag}")
portfolio_list = "\n".join(portfolio_list_lines)

prompt = T1_FRAMEWORK + f"""## 【操作约束】
1. 买入卖出按**当日收盘净值**计算，15:00前下单按今日净值，估算净值≠成交价
2. 资金T+2到账。建仓期003096/013403仅允许持有或加仓
3. 所有操作建议标明"15:00前"或"明日计划"

## 【持仓数据】
你管理的全部基金(14支)：
{portfolio_list}

> 📌 建仓期标记🏗️的基金在任何情况下不能建议卖出。
> 📌 推荐基金时**必须使用正确的基金代码**，不得编造或写错代码。

## 【盘中分析指令】
现在是午间休市，基于上午半日数据完成5步分析，**前4步简洁，第5步详细**：

1.【上午复盘】大盘/板块/北向上午走势关键特征
2.【午后推演】按赛道(科技/防御/蓝筹)给出午后方向判断+关键观察
3.【基金影响】各赛道持仓基金的上午表现及午后影响
4.【风险提示】午后最需要关注的3条风险
5.【午后操作方向·详细】
   a)【从现有持仓中】选3支最值得关注的——逐支给名称/代码/判断理由/操作方向/仓位建议
   b)【从现有持仓中】选3支需警惕的——为什么、怎么应对
   c) 对持仓中其余基金做简述
   d) 【可选】如果发现更好的赛道/基金机会（有数据支撑），可以推荐**新基金**，但必须：
      - 明确标注"📌新基金建议"与现有持仓区分
      - 给出完整理由（行业/赛道/趋势数据支撑）
      - 对比说明与现有同赛道持仓的优劣
      - 必须使用正确的基金代码（代码可在持仓外搜索，但别编造）"""

analysis = call_ds(prompt, data, max_tokens=8000, temp=0.3)
md_link = ""
html_link = ""
if analysis:
    analysis = analysis.replace("<br>", "\n")
    # 临时禁用stdout，避免push_report打印旧摘要
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        md_link, html_link = push_report("noon", f"盘中直击 · 基金速递 · {date.today()}", tables, analysis)
    finally:
        sys.stdout = old_stdout
    print(f"✅ 午报已上传: {html_link}", file=sys.stderr)

# ── Step 4: 生成文本摘要（供cron deliver展示到QQ）──
today = date.today()
weekday_cn = ['周一','周二','周三','周四','周五','周六','周日'][today.weekday()]
now_str = datetime.now().strftime('%H:%M')

def read_txt(name):
    p = SUMMARY_DIR / name
    return p.read_text().strip() if p.exists() else ""

market_text = read_txt("_noon_market.txt")
sector_text = read_txt("_noon_sector.txt")
overview_text = read_txt("_noon_overview.txt")
nb_text = read_txt("_noon_northbound.txt")
group_text = read_txt("_noon_group.txt")

# Parse market indices
mkt_parts = []
for line in market_text.split("\n"):
    parts = line.split("|")
    if len(parts) >= 3:
        name = parts[0].strip()
        price = parts[1].strip()
        pct = parts[2].strip().replace('%', '')
        try:
            is_up = float(pct) > 0
        except:
            is_up = pct.startswith('+')
        short = name.replace('上证指数','上证').replace('沪深300','沪深').replace('科创50','科创').replace('创业板指','创业板').replace('上证50','上证50').replace('黄金ETF市场价','黄金')
        emoji = "🔴" if is_up else "🟢"
        mkt_parts.append(f"{short}{price}{emoji}{pct}%")

mkt_summary = " | ".join(mkt_parts[:5]) if mkt_parts else ""

# Parse sector top/bottom
sector_gains = []
sector_losses = []
for line in sector_text.split("\n"):
    m = re.match(r"[🔴🟢🟡]\s*(\S+):.*\(([+-]?\d+\.?\d*)%\)", line)
    if m:
        name = m.group(1)
        pct_raw = m.group(2)  # e.g. "+8.28" or "-1.01"
        try:
            pct_f = float(pct_raw)
        except:
            continue
        if pct_f > 0.5:
            sector_gains.append(f"{name}+{abs(pct_f):.2f}%")
        elif pct_f < -0.5:
            sector_losses.append(f"{name}{pct_f:.2f}%")

gain_str = " ".join(sector_gains[:4]) if sector_gains else ""
loss_str = " ".join(sector_losses[:3]) if sector_losses else ""

# Northbound
nb_clean = ""
for line in nb_text.split("\n"):
    nb_clean = re.sub(r'^[🔴🟢🟡]\s*', '', line).strip()

# Turnover
turnover_str = ""
for line in overview_text.split("\n"):
    m = re.search(r"(\d+)亿", line)
    if m:
        turnover_str = f"半日成交{m.group(1)}亿"
        break

# Fund groups
group_strs = []
for line in group_text.split("\n"):
    m = re.match(r"[🔴🟢🟡]\s*(\S+):\s*([+-]?\d+\.?\d*)%", line)
    if m:
        gname, pct = m.group(1), m.group(2)
        try:
            emoji = "🔴" if float(pct) > 0 else "🟢"
        except:
            emoji = "🟡"
        group_strs.append(f"{gname}{emoji}{pct}%")

# AI analysis short extract
ai_short = ""
if analysis:
    first_para = analysis.split("\n\n")[0] if "\n\n" in analysis else analysis
    first_para = re.sub(r'\*\*', '', first_para)
    ai_short = first_para[:120].strip()
    if len(first_para) > 120:
        ai_short += "..."

# ── Build output lines ──
lines_out = []

# Header (简短标题，无markdown格式)
lines_out.append(f"📈 盘中直击 · {today} {weekday_cn} {now_str}")
lines_out.append("")

# Market
if mkt_summary:
    lines_out.append(f"📊 大盘: {mkt_summary}")

# Sectors
if gain_str:
    lines_out.append(f"🔥 领涨: {gain_str}")
if loss_str:
    lines_out.append(f"🟢 领跌: {loss_str}")

# Northbound
if nb_clean:
    lines_out.append(f"🌊 {nb_clean}")

# Turnover
if turnover_str:
    lines_out.append(f"💰 {turnover_str}")

# Groups
if group_strs:
    lines_out.append(f"📊 持仓: {' | '.join(group_strs)}")

# AI analysis
if ai_short:
    lines_out.append("")
    lines_out.append(f"🤖 {ai_short}")

# R2 links
if md_link and html_link:
    lines_out.append("")
    lines_out.append(f"📄 完整报告: {md_link}")
    lines_out.append(f"🌐 HTML预览: {html_link}")

print("\n".join(lines_out))
