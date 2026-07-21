#!/usr/bin/env python3
"""Wrapper: closing review — collect data + format + LLM分析 → stdout → QQ Bot (备用路径)
实际cron走profiles/investment/scripts/run_closing.py"""
import subprocess, sys, os
os.chdir('/opt/data/scripts')

r1 = subprocess.run([sys.executable, 'closing_review.py'], capture_output=True, text=True, timeout=180)
if r1.stderr:
    print(r1.stderr, file=sys.stderr)

r2 = subprocess.run([sys.executable, 'send_closing.py'], capture_output=True, text=True, timeout=60)
if r2.stdout.strip():
    print(r2.stdout.strip())
if r2.stderr:
    print(r2.stderr, file=sys.stderr)

try:
    env_path = '/opt/data/profiles/investment/.env'
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith('DEEPSEEK_API_KEY='):
                os.environ['DEEPSEEK_API_KEY'] = line.split('=', 1)[1].strip()
    sys.path.insert(0, '/opt/data/scripts')
    from llm_analysis import generate_closing_analysis
    analysis = generate_closing_analysis()
    if analysis:
        print(f"\n## 📌 收盘 AI 深度解读\n\n{analysis}")
except Exception as e:
    print(f"[run_closing] LLM分析异常: {type(e).__name__}", file=sys.stderr)
