#!/usr/bin/env python3
"""Wrapper: deduplicate JSONL archives."""
import subprocess, sys

r = subprocess.run(
    [sys.executable, '/opt/data/scripts/deduplicate_archives.py'],
    capture_output=True, text=True, timeout=120
)
if r.stdout.strip():
    print(r.stdout.strip())
if r.returncode != 0 and r.stderr.strip():
    print(f"[stderr] {r.stderr.strip()}", file=sys.stderr)
