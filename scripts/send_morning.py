"""Morning briefing: output formatted Markdown to stdout (QQ Bot push)."""
import sys, os, json
sys.path.insert(0, '/opt/data/scripts')

from send_qqbot import send_card, send_card_with_tables, send_structured_card

SUMMARY_DIR = "/tmp/fund_data"

# Check if skip file exists (non-trading day)
if os.path.exists(f"{SUMMARY_DIR}/_skip.txt"):
    print("Non-trading day, skipping")
    sys.exit(0)

# ── Helper: send card with JSON-level structure (divider, markdown, note) ──


# ── Read the full morning content ──
content = open(f"{SUMMARY_DIR}/_morning_tables.md").read()
lines = content.split("\n")

# Section 1: Title + overnight + A-share
sec1_lines = []
i = 0
tables_found = 0
while i < len(lines) and tables_found < 2:
    sec1_lines.append(lines[i])
    if lines[i].strip().startswith("|") and lines[i].strip().endswith("|") and "---" not in lines[i]:
        if i+1 < len(lines) and "---" in lines[i+1]:
            tables_found += 1 if i > 0 else 0
    i += 1
    if tables_found >= 2 and not lines[i].strip():
        if i+1 < len(lines) and not lines[i+1].startswith("|"):
            sec1_lines.extend(lines[i:i+3])
            i += 3
            break

c1_text = "\n".join(sec1_lines).strip()
if c1_text:
    send_card_with_tables("外盘 & A股 指数", c1_text, "blue")

# Section 2: 量价分析
va_start = content.find("📊 **量价分析")
va_end = content.find("🔥 **板块热度")
if va_start >= 0:
    va_section = content[va_start:va_end].strip() if va_end > va_start else content[va_start:].strip()
    send_card_with_tables("量价分析", va_section, "indigo")

# Section 3: 板块热度
sec_start = content.find("🔥 **板块热度")
sec_end = content.find("💰 **持仓基金")
if sec_start >= 0:
    sec_section = content[sec_start:sec_end].strip() if sec_end > sec_start else content[sec_start:].strip()
    send_card_with_tables("板块热度", sec_section, "red")

# Section 4: 持仓参考
fund_start = content.find("💰 **持仓基金")
if fund_start >= 0:
    fund_section = content[fund_start:].strip()
    send_card_with_tables("持仓参考", fund_section, "green")

# Extra cards
# 操作参考
op_file = f"{SUMMARY_DIR}/_operation_plan.txt"
eval_file = f"{SUMMARY_DIR}/_operation_eval.txt"
if os.path.exists(op_file) and os.path.exists(eval_file):
    op_content = open(op_file).read() + "\n\n" + open(eval_file).read()
    send_card_with_tables("操作参考 & 评估", op_content, "purple")

# ── KOL 赛道共识（简化版）──
consensus_file = f"{SUMMARY_DIR}/_kol_consensus.txt"
if os.path.exists(consensus_file):
    consensus_text = open(consensus_file).read().strip()
    if consensus_text:
        send_structured_card(
            "KOL赛道共识",
            [{"type": "markdown", "content": consensus_text}],
            "purple"
        )

# ── KOL 观点卡片（精简：只看今日观点+趋势参考）──
kol_file = f"{SUMMARY_DIR}/_kol_summary.txt"
if os.path.exists(kol_file):
    kol_text = open(kol_file).read().strip()
    parts = kol_text.split("─── 小浣熊1230")

    if len(parts) > 1:
        tang = parts[0].strip()
        xiong = ("─── 小浣熊1230" + parts[1]).strip()

        # 唐史主任 卡片（直接输出汇总段+今日观点，省去逐条解读）
        if tang:
            # 提取"赛道情绪汇总"段（含"📊"的行到下一个空行）+"今日观点"段
            lines = tang.split("\n")
            summary_lines = []
            in_summary = False
            in_today = False
            for line in lines:
                if line.strip().startswith("📊"):
                    in_summary = True
                if line.strip().startswith("📋"):
                    in_today = True
                    in_summary = False
                if in_summary or in_today:
                    summary_lines.append(line)

            if summary_lines:
                send_structured_card("唐史主任司马迁 观点", [
                    {"type": "markdown", "content": "\n".join(summary_lines)[:3800]},
                ], "wathet")

        # 小浣熊1230 卡片
        if xiong:
            lines = xiong.split("\n")
            summary_lines = []
            in_summary = False
            in_today = False
            for line in lines:
                if line.strip().startswith("📊"):
                    in_summary = True
                if line.strip().startswith("📋"):
                    in_today = True
                    in_summary = False
                if in_summary or in_today:
                    summary_lines.append(line)

            if summary_lines:
                send_structured_card("小浣熊1230 观点", [
                    {"type": "markdown", "content": "\n".join(summary_lines)[:3800]},
                ], "wathet")

# ── RSS 新闻卡片（带翻译后的中文标题）──
rss_file = f"{SUMMARY_DIR}/_rss_news.txt"
if os.path.exists(rss_file):
    rss_text = open(rss_file).read()[:6000]
    if rss_text.strip():
        send_structured_card(
            "隔夜赛道要闻",
            [
                {"type": "markdown", "content": rss_text},
                {"type": "note", "content": "英文标题已自动翻译为中文"},
            ],
            "grey"
            )
  
