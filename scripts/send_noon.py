"""Noon briefing: format data into Markdown sections for QQ Bot push."""
import sys, os, re
from datetime import date, datetime
sys.path.insert(0, '/opt/data/scripts')

from send_qqbot import send_card, send_card_with_tables

SUMMARY_DIR = "/tmp/fund_data"

if os.path.exists(f"{SUMMARY_DIR}/_noon_skip.txt"):
    print("Non-trading day, skipping")
    sys.exit(0)

today = date.today()
weekday_cn = ['周一','周二','周三','周四','周五','周六','周日'][today.weekday()]
now_str = datetime.now().strftime('%H:%M')

# ── Card 1: 大盘指数 + 量价分析 ──
market_file = f"{SUMMARY_DIR}/_noon_market.txt"
volume_file = f"{SUMMARY_DIR}/_noon_volume.txt"
overview_file = f"{SUMMARY_DIR}/_noon_overview.txt"

market_lines = open(market_file).read().strip().split("\n") if os.path.exists(market_file) else []
volume_lines = open(volume_file).read().strip() if os.path.exists(volume_file) else ""
overview_text = open(overview_file).read().strip() if os.path.exists(overview_file) else ""

# Build market table with correct date
mkt_table = f"**盘中行情** {today} {now_str}\n\n| 指数 | 点位 | 涨跌 |\n|:----|:----:|:----:|\n"
for line in market_lines:
    parts = line.split("|")
    if len(parts) >= 3:
        name = parts[0].strip()
        price = parts[1].strip()
        pct = parts[2].strip().replace('%', '')
        try:
            pct_f = float(pct)
            emoji = "🔴" if pct_f > 0 else "🟢" if pct_f < 0 else "🟡"
        except:
            emoji = "🟡"
        mkt_table += f"| {name} | {price} | {emoji} {pct}% |\n"

# Add overview
if overview_text:
    for l in overview_text.split("\n"):
        mkt_table += f"\n{l}"

c1 = mkt_table + "\n\n" + volume_lines
send_card_with_tables("盘中行情 & 量价分析", c1, "indigo")

# ── Card 2: 板块排行 + 北向 + 持仓分组 ──
sector_file = f"{SUMMARY_DIR}/_noon_sector.txt"
nb_file = f"{SUMMARY_DIR}/_noon_northbound.txt"
group_file = f"{SUMMARY_DIR}/_noon_group.txt"

sector_lines = open(sector_file).read().strip().split("\n") if os.path.exists(sector_file) else []
nb_text = open(nb_file).read().strip() if os.path.exists(nb_file) else ""
group_lines = open(group_file).read().strip().split("\n") if os.path.exists(group_file) else []

# Parse sector data
sectors = []
for line in sector_lines:
    m = re.match(r"[🔴🟢🟡]\s*(\S+):\s*\S+→\S+\s*\(([+-]?[\d.]+%)\)", line)
    if m:
        name, pct = m.group(1), m.group(2)
        emoji = "🔴" if pct.startswith("+") else "🟢"
        sectors.append((float(pct.replace("%","")), f"| {name} | {emoji} {pct} |"))

sectors.sort(key=lambda x: x[0], reverse=True)

c2 = "🔥 **板块排行**\n\n| 板块 | 涨跌 |\n|:---|:----:|\n"
for _, row in sectors:
    c2 += row + "\n"

# Add northbound
if nb_text:
    c2 += f"\n🌊 {nb_text}\n"

# Add overview (turnover)
if overview_text:
    for l in overview_text.split("\n"):
        if "成交" in l:
            c2 += f"\n💰 {l}"

# Add group performance
if group_lines:
    c2 += "\n\n📊 **持仓分组表现**\n\n| 组别 | 涨跌 | 支数 |\n|:---|:----:|:----:|\n"
    for line in group_lines:
        m2 = re.match(r"[🔴🟢🟡]\s*(\S+):\s*([+-]?[\d.]+%)\s*\((\d+)支\)", line)
        if m2:
            gname, pct, count = m2.group(1), m2.group(2), m2.group(3)
            emoji = "🔴" if pct.startswith("+") else "🟢"
            c2 += f"| {gname} | {emoji} {pct} | {count} |\n"

send_card_with_tables("板块 & 北向 & 持仓", c2, "red")

# ── Card 3: 盘中分析（完全数据驱动）──
all_down = all(s[0] < 0 for s in sectors) if sectors else True
up_count = sum(1 for s in sectors if s[0] > 0)
northbound_val = 0
if nb_text:
    m3 = re.search(r"合计.*?([+-]?[\d.]+)亿", nb_text)
    if m3:
        northbound_val = float(m3.group(1))

# 量价信号分析
volume_signals = []
volume_note = ""
if os.path.exists(volume_file):
    vol_text = open(volume_file).read()
    # Extract the total signal line
    for l in vol_text.split("\n"):
        if "总量总览" in l or "总体" in l:
            volume_note = l.split("|")[-1].strip() if "|" in l else l

# 板块情绪
sector_summary = ""
if up_count > len(sectors) / 2:
    sector_summary = f"📊 **多数板块翻红** ({up_count}/{len(sectors)})"
elif up_count < len(sectors) / 3:
    sector_summary = f"⚠️ **多数板块下跌** ({len(sectors)-up_count}/{len(sectors)})"
else:
    sector_summary = f"📊 **板块分化** ({up_count}涨/{len(sectors)-up_count}跌)"

# 持仓影响
group_impact_lines = []
if os.path.exists(group_file):
    for line in group_lines:
        m2 = re.match(r"[🔴🟢🟡]\s*(\S+):\s*([+-]?[\d.]+)%\s*\((\d+)支\)", line)
        if m2:
            gname, pct, count = m2.group(1), m2.group(2), m2.group(3)
            try:
                pct_f = float(pct)
                if pct_f < -2:
                    group_impact_lines.append(f"- **{gname}**: {pct}%，跌幅较大，暂不加仓")
                elif pct_f < 0:
                    group_impact_lines.append(f"- **{gname}**: {pct}%，小幅回调，持有观望")
                else:
                    group_impact_lines.append(f"- **{gname}**: {pct}%，相对强势")
            except:
                pass

# Top/bottom sectors for context
top_sectors = sectors[:3] if sectors else []
bottom_sectors = sectors[-3:] if sectors else []

af_analysis = f"""**盘中分析**

{sector_summary}
{'全市场下挫' if all_down else f'{up_count}个板块翻红, {len(sectors)-up_count}个下跌'}

💰 **成交**: {overview_text}"""

if northbound_val != 0:
    af_analysis += f"\n🌊 **北向**: {'流入' if northbound_val > 0 else '流出'}{abs(northbound_val):.0f}亿"

# 量价信号
if volume_note:
    af_analysis += f"\n\n📊 **量价信号**: {volume_note}"

# 持仓影响
if group_impact_lines:
    af_analysis += "\n\n💰 **持仓影响**:\n" + "\n".join(group_impact_lines)

# 午后策略（基于数据）
afternoon_strategy = []
if all_down or up_count < len(sectors) / 3:
    afternoon_strategy.append("📌 **午后策略**: 整体偏弱，观望为主")
    if northbound_val < -30:
        afternoon_strategy.append("北向大幅流出，不建议加仓")
else:
    afternoon_strategy.append("📌 **午后策略**: 市场平衡，关注午后量能")

if any(s[0] < -3 for s in sectors):
    afternoon_strategy.append("部分板块跌幅>3%，警惕情绪扩散")

af_analysis += "\n\n" + "\n".join(afternoon_strategy)

send_card("盘中分析 & 午后策略", af_analysis, "indigo")
  
