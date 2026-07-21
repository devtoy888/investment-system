"""Closing review: format closing data into Markdown for QQ Bot push."""
import sys, os
sys.path.insert(0, '/opt/data/scripts')

from send_qqbot import send_card, send_card_with_tables

SUMMARY_DIR = "/tmp/fund_data"

if os.path.exists(f"{SUMMARY_DIR}/_closing_skip.txt"):
    print("Non-trading day, skipping")
    sys.exit(0)

# Read closing tables
closing_file = f"{SUMMARY_DIR}/_closing_tables.md"
closing_text = open(closing_file).read() if os.path.exists(closing_file) else ""

if not closing_text:
    print("No closing tables data, skipping")
    sys.exit(0)

# Card 1: 大盘走势 + 成交 + 北向
# Find sections
dapan_start = closing_text.find("📊 **大盘走势")
hangye_start = closing_text.find("📊 **行业板块")
north_text = ""
overview_text = ""

# Extract northbound (🌊 line)
for line in closing_text.split("\n"):
    if "北向" in line and ("沪" in line or "深" in line):
        north_text = line.strip()
        break

# Extract turnover (成交 line)  
for line in closing_text.split("\n"):
    if "成交" in line and "亿" in line:
        overview_text = line.strip()

if dapan_start >= 0:
    dapan_section = closing_text[dapan_start:hangye_start].strip() if hangye_start > dapan_start else closing_text[dapan_start:].strip()
    if overview_text:
        dapan_section += f"\n\n💰 {overview_text}"
    if north_text:
        dapan_section += f"\n\n🌊 {north_text}"
    send_card_with_tables("收盘 · 大盘走势", dapan_section, "blue")

# Card 2: 行业板块
if hangye_start >= 0:
    fund_start = closing_text.find("💰 **持仓基金")
    hangye_section = closing_text[hangye_start:fund_start].strip() if fund_start > hangye_start else closing_text[hangye_start:].strip()
    send_card_with_tables("收盘 · 行业板块", hangye_section, "red")

# Card 3: 持仓基金
fund_start = closing_text.find("💰 **持仓基金")
yuce_start = closing_text.find("📋 **早盘预测验证")
if fund_start >= 0:
    fund_section = closing_text[fund_start:yuce_start].strip() if yuce_start > fund_start else closing_text[fund_start:].strip()
    send_card_with_tables("收盘 · 持仓表现", fund_section, "green")

# Card 4: 早盘预测验证
if yuce_start >= 0:
    tuijian_start = closing_text.find("🔮 **后市推演")
    yuce_section = closing_text[yuce_start:tuijian_start].strip() if tuijian_start > yuce_start else closing_text[yuce_start:].strip()
    send_card_with_tables("收盘 · 预测验证", yuce_section, "indigo")

# Card 5: 操作评估
eval_file = f"{SUMMARY_DIR}/_operation_eval.txt"
if os.path.exists(eval_file):
    eval_text = open(eval_file).read().strip()
    send_card_with_tables("操作评估 & 趋势", eval_text, "purple")
  
