#!/usr/bin/env python3
"""Wrapper: 14:30操作建议推送 — 信号+偏离度+风险+基准，格式化输出"""
import subprocess, sys

PY = sys.executable
SCRIPTS = "/opt/data/scripts"

r = subprocess.run([PY, f'{SCRIPTS}/format_op_push.py'], capture_output=True, text=True, timeout=180)
if r.stdout.strip():
    print(r.stdout.strip())
else:
    # 无数据时静默
    pass

if r.returncode != 0 and r.stderr.strip():
    print(f"[format_op_push stderr] {r.stderr.strip()}", file=sys.stderr)
