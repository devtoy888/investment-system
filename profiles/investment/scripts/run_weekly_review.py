#!/usr/bin/env python3
"""周度复盘 — R2推送版"""
import subprocess, sys, os
from datetime import date

r = subprocess.run(
    [sys.executable, '/opt/data/scripts/weekly_review.py'],
    capture_output=True, text=True, timeout=180
)
tables = r.stdout.strip() if r.stdout.strip() else ""
if r.stderr:
    print(r.stderr.strip(), file=sys.stderr)

# R2推送
sys.path.insert(0, '/opt/data/scripts')
from push_report_r2 import push_report

# 读缓存中的周度分析
cache_path = "/opt/data/fund_system_data/llm_analysis_cache"
weekly_file = f"{cache_path}/weekly_{date.today().isoformat()}.txt"

# 先尝试从cache读取 (由generate_v2写入)
analysis = ""
import os as _os
if _os.path.exists(weekly_file):
    with open(weekly_file) as f:
        analysis = f.read().strip()

# 如果缓存没有，用generate_v2生成
if not analysis:
    from llm_analysis_v2 import generate_v2
    analysis = generate_v2('weekly', use_cache=False)
    
if analysis:
    analysis = analysis.replace("<br>", "\n")
    md, html = push_report("weekly", f"周度复盘 · {date.today()}", tables, analysis)
    print(f"✅ 周度已上传: {html}", file=sys.stderr)
