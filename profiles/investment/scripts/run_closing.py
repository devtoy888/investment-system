#!/usr/bin/env python3
"""Wrapper: closing review v2 — R2推送版"""
import subprocess, sys, os
from pathlib import Path
from datetime import date

os.chdir('/opt/data/scripts')

# Step 1: 收盘数据采集
r1 = subprocess.run([sys.executable, 'closing_review.py'], capture_output=True, text=True, timeout=180)
if r1.stderr:
    print(r1.stderr, file=sys.stderr)

# Step 2: 数据表推送
r2 = subprocess.run([sys.executable, 'send_closing.py'], capture_output=True, text=True, timeout=60)
data_tables = r2.stdout.strip() if r2.stdout.strip() else ""
if r2.stderr:
    print(r2.stderr, file=sys.stderr)

# Step 3: R2推送深度分析
sys.path.insert(0, '/opt/data/scripts')
from llm_analysis_v2 import generate_v2, build_closing_data_v2, CLOSING_PROMPT_V2, call_ds
from push_report_r2 import push_report

analysis = generate_v2("closing", use_cache=False)
if analysis:
    analysis = analysis.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    md_link, html_link = push_report(
        report_type="closing",
        title=f"收盘复盘 · {date.today().isoformat()}",
        data_tables=data_tables,
        analysis=analysis
    )
    print(f"✅ 收盘报告已上传: {html_link}", file=sys.stderr)
else:
    print("[run_closing] ❌ 分析生成失败", file=sys.stderr)
