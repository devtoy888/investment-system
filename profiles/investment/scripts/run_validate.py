#!/usr/bin/env python3
"""Wrapper: source availability validator.
Prints to stdout → cron no_agent delivers to QQ."""
import subprocess, sys

r = subprocess.run(
    [sys.executable, '/opt/data/scripts/auto_validate_sources.py'],
    capture_output=True, text=True, timeout=120
)
if r.stdout.strip():
    print(r.stdout.strip())
if r.returncode != 0 and r.stderr.strip():
    print(f"[stderr] {r.stderr.strip()}", file=sys.stderr)
