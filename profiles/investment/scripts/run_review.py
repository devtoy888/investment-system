#!/usr/bin/env python3
"""每日报告审阅进化 + 报告索引自动更新"""
import sys, os
from pathlib import Path

sys.path.insert(0, '/opt/data/scripts')
from review_engine import full_review_cycle
from datetime import date

# 1. 执行审阅
result = full_review_cycle()
dashboard = result.get("dashboard_url", "")
ver = result.get("verification", {})
evol = result.get("evolution", {})
reviews = result.get("reviews", {})
backtest = result.get("backtest", {})
reports_passed = sum(1 for r in reviews.values() if r.get("passed"))
reports_total = len(reviews)

# 审查详情
detail_lines = []
report_type_labels = {'morning':'晨报','noon':'午报','decision':'14:30决策','closing':'收盘复盘','morning_direction':'09:35方向'}
for rtype, r in sorted(reviews.items()):
    rtype_label = report_type_labels.get(rtype, rtype)
    status = "✅" if r.get("passed") else "❌"
    issues = r.get("issues", [])
    detail = f"{status} {rtype_label}"
    if issues:
        detail += f"  {issues[0][:50]}"
    detail_lines.append(detail)

# 修复建议
fix_lines = []
for rtype, r in sorted(reviews.items()):
    if not r.get("passed"):
        for iss in r.get("issues", []):
            rtype_label = report_type_labels.get(rtype, rtype)
            if "不存在" in iss: fix_lines.append(f"- {rtype_label}: 报告未生成")
            elif "过短" in iss: fix_lines.append(f"- {rtype_label}: 内容不足")
            elif "截断" in iss: fix_lines.append(f"- {rtype_label}: AI分析被截断")
            elif "缺少" in iss: fix_lines.append(f"- {rtype_label}: 章节不完整")

# 输出消息
summary = f"""📊 **每日审阅 · {date.today()}**

📋 **报告审查**  {reports_passed}/{reports_total} 通过
{chr(10).join(detail_lines)}

✅ **预测验证**  {ver.get('correct',0)}/{ver.get('verified',0)} 正确
   准确率 {ver.get('accuracy_pct','N/A')}% | 共{ver.get('total_predictions',0)}条预测

🛠️ **操作信号**  买入{backtest.get('buy_signals',0)} / 卖出{backtest.get('sell_signals',0)} / 持有{backtest.get('hold_signals',0)}"""

if fix_lines:
    summary += f"\n\n🔧 **待修复**\n" + "\n".join(fix_lines)

summary += f"\n\n🌐 {dashboard}"

print(summary)

# 2. 自动更新报告索引
REPORT_DIR = Path("/opt/data/fund_system_data/reports")
BASE_URL = "https://hermes-main-media.devtoy.xyz/fund-system/reports"

reports = {}
# 扫描日期子目录（新格式: 2026/07/21/closing.md）
for sub in sorted(REPORT_DIR.glob("[0-9][0-9][0-9][0-9]/*/*/")):
    rdate = f"{sub.parent.parent.name}-{sub.parent.name}-{sub.name}"
    for f in sub.glob("*.md"):
        rtype = f.stem
        if rtype not in ('morning','noon','decision','closing','weekly','weekend','morning_direction'): continue
        if rdate not in reports: reports[rdate] = {}
        reports[rdate][rtype] = rdate
# 扫描平铺旧版（兼容: closing_2026-07-21.md）
for f in sorted(REPORT_DIR.glob("*_*-*-*.md")):
    name = f.stem
    parts = name.split("_", 1)
    if len(parts) == 2:
        rtype, rdate = parts[0], parts[1]
        if rtype not in ('morning','noon','decision','closing','weekly','weekend','morning_direction'): continue
        if rdate not in reports: reports[rdate] = {}
        if rtype not in reports[rdate]:
            reports[rdate][rtype] = name

today = date.today().isoformat()
labels = {'morning':'晨报','noon':'午报','decision':'14:30决策','closing':'收盘','weekly':'周报','weekend':'外盘','morning_direction':'09:35方向'}
icons = {'morning':'🌤','noon':'📈','decision':'🎯','closing':'🌙','weekly':'📋','weekend':'🌍','morning_direction':'🔔'}

html = """<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>投资系统 · 历史报告</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,'PingFang SC',sans-serif;background:#f0f2f5;color:#1a1a2e;padding:20px;transition:background .3s,color .3s}
h1{text-align:center;margin-bottom:6px;font-size:22px}
.sub{text-align:center;font-size:13px;color:#888;margin-bottom:20px}
.nav{text-align:center;margin-bottom:20px}
.nav a{display:inline-block;background:white;padding:8px 18px;border-radius:8px;text-decoration:none;color:#4a6cf7;font-size:13px;margin:0 4px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.nav a:hover{background:#4a6cf7;color:white}
.date-group{background:white;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,0.06)}
.date-group h2{font-size:15px;margin-bottom:10px;color:#4a6cf7}
.report-row{display:flex;gap:8px;padding:5px 0;flex-wrap:wrap;align-items:center}
.report-row .tag{font-size:12px;font-weight:600;padding:2px 8px;border-radius:4px;min-width:44px;text-align:center}
.tag-morning{background:#e8f5e9;color:#2e7d32}
.tag-noon{background:#fff3e0;color:#e65100}
.tag-decision{background:#e3f2fd;color:#1565c0}
.tag-closing{background:#f3e5f5;color:#7b1fa2}
.tag-weekly{background:#e0f2f1;color:#00695c}
.tag-weekend{background:#fce4ec;color:#c62828}
.report-row a{font-size:13px;color:#4a6cf7;text-decoration:none;padding:2px 6px}
.report-row a:hover{text-decoration:underline}
.report-row .sep{color:#ddd;font-size:11px}
.footer{text-align:center;font-size:12px;color:#999;margin-top:24px}
body.dk{background:#1a1a2e;color:#ddd}
body.dk .nav a{background:#16213e;color:#7a9cf7}
body.dk .nav a:hover{background:#4a6cf7;color:white}
body.dk .date-group{background:#16213e}
body.dk .sub{color:#888}
body.dk .report-row .sep{color:#444}
@media(max-width:600px){.report-row{gap:4px}.report-row a{font-size:12px}}
</style></head><body>
<script>if(window.matchMedia("(prefers-color-scheme:dark)").matches)document.body.classList.add("dk");</script>
<h1>📚 投资系统 · 历史报告</h1>
<div class="sub">共 """ + str(len(reports)) + """ 个交易日 · """ + today + """</div>
<div class="nav">
<a href=\"""" + BASE_URL + """/dashboard.html">📊 看板</a>
<a href="javascript:void(0)" onclick="document.body.classList.toggle('dk')">🌓 切换主题</a>
</div>"""

for rdate in sorted(reports.keys(), reverse=True):
    html += '\n<div class="date-group"><h2>📅 ' + rdate + '</h2>'
    for rtype in ['weekly','weekend','morning','noon','decision','closing']:
        if rtype in reports[rdate]:
            # 新格式: 2026/07/21/closing.md, 旧格式: closing_2026-07-21.md
            val = reports[rdate][rtype]
            if '_' in val and len(val.split('_')) == 2:  # 旧格式: "closing_2026-07-21"
                parts2 = val.split("_", 1)
                md_url = f"{BASE_URL}/{parts2[0]}_{parts2[1]}.md"
                html_url = f"{BASE_URL}/{parts2[0]}_{parts2[1]}.html"
            else:  # 新格式: "2026-07-21" (date string from subdir)
                d_parts = rdate.split('-')
                md_url = f"{BASE_URL}/{d_parts[0]}/{d_parts[1]}/{d_parts[2]}/{rtype}.md"
                html_url = f"{BASE_URL}/{d_parts[0]}/{d_parts[1]}/{d_parts[2]}/{rtype}.html"
            label = labels.get(rtype, rtype)
            icon = icons.get(rtype, '📄')
            html += f'\n<div class="report-row"><span class="tag tag-{rtype}">{icon} {label}</span>'
            html += f'<a href="{md_url}">📄 MD</a><span class="sep">|</span>'
            html += f'<a href="{html_url}">🌐 HTML</a></div>'
    html += '</div>'

html += f'\n<div class="footer">自动生成 · {today}</div></body></html>'

idx_path = REPORT_DIR / "index.html"
idx_path.write_text(html, encoding='utf-8')

# Upload
from fund_tools import upload_to_r2 as up
up(str(idx_path), "fund-system/reports/index.html", "text/html; charset=utf-8")
