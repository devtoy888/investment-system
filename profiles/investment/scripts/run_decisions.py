#!/usr/bin/env python3
"""Wrapper: daily decision log. Outputs decisions.jsonl + daily-snapshots.jsonl, uploads to R2."""
import subprocess, sys

r = subprocess.run(
    ['/opt/hermes/.venv/bin/python3', '/opt/data/scripts/log_daily_decisions.py'],
    capture_output=True, text=True, timeout=120
)
if r.stdout.strip():
    print(r.stdout.strip())
if r.returncode != 0 and r.stderr.strip():
    print(f"[stderr] {r.stderr.strip()}", file=sys.stderr)
