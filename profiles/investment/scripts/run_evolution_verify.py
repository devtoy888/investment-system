#!/usr/bin/env python3
"""每日预测验证 — R2推送版"""
import sys, os
from datetime import date

env_path = '/opt/data/profiles/investment/.env'
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('DEEPSEEK_API_KEY='):
            os.environ['DEEPSEEK_API_KEY'] = line.split('=', 1)[1].strip()

sys.path.insert(0, '/opt/data/scripts')

from evolution_engine import verify_yesterday_predictions, accuracy_dashboard, PREDICTIONS_FILE
from push_report_r2 import push_report, upload_to_r2, build_html

results = verify_yesterday_predictions()
dashboard = accuracy_dashboard() if results else "暂无预测记录"

# 也获取今日预测
today_preds = []
if PREDICTIONS_FILE.exists():
    import json
    for line in open(PREDICTIONS_FILE):
        try:
            r = json.loads(line)
            if r.get('date','')[:10] == date.today().isoformat():
                today_preds.append(r)
        except:
            pass

today_str = "\n".join([f"- {p.get('prediction','')[:80]}" for p in today_preds[:5]]) if today_preds else "无"

full_md = f"""# 预测验证看板 · {date.today()}

## 📊 昨日预测准确率

{dashboard}

## 🎯 今日已有预测
{today_str}
"""

# 上传到R2
today = date.today().isoformat()
md_path = f"/tmp/verify_{today}.md"
with open(md_path, 'w') as f:
    f.write(full_md)

upload_to_r2(md_path, f"fund-system/reports/verify_{today}.md")

# 也生成HTML看板
html_content = build_html(full_md, f"预测验证 · {today}")
html_path = f"/tmp/verify_{today}.html"
with open(html_path, 'w') as f:
    f.write(html_content)
upload_to_r2(html_path, f"fund-system/reports/verify_{today}.html", "text/html; charset=utf-8")

base = "https://hermes-main-media.devtoy.xyz/fund-system/reports"
links = f"""📊 **预测验证 · {today}**

📄 [Markdown]({base}/verify_{today}.md)
🌐 [HTML看板]({base}/verify_{today}.html)

{'✅ 预测准确率:' + dashboard[:200] if dashboard else '⏳ 暂无预测记录'}"""

from send_qqbot import _output
_output(links)
