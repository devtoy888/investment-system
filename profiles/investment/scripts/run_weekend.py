#!/usr/bin/env python3
"""周末外盘 — R2推送版"""
import subprocess, sys, os
from datetime import date

os.chdir('/opt/data/scripts')

# Step 1: 数据采集
r1 = subprocess.run([sys.executable, 'collect_weekend_data.py'], capture_output=True, text=True, timeout=120)
tables = r1.stdout.strip() if r1.stdout.strip() else ""
if r1.stderr:
    print(r1.stderr, file=sys.stderr)

# Step 2: R2推送
sys.path.insert(0, '/opt/data/scripts')
from llm_analysis_v2 import T1_FRAMEWORK, generate_v2
from push_report_r2 import push_report

analysis = generate_v2('weekend', use_cache=False)
if analysis:
    analysis = analysis.replace("<br>", "\n")
    md, html = push_report("weekend", f"周末外盘速报 · {date.today()}", tables, analysis)
    print(f"✅ 周末已上传: {html}", file=sys.stderr)
