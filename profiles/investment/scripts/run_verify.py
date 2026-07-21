#!/usr/bin/env python3
"""Wrapper: verify 3-day old decisions."""
import subprocess, sys
r = subprocess.run([sys.executable, '/opt/data/scripts/verify_decisions.py'],
    capture_output=True, text=True, timeout=120)
if r.stdout.strip(): print(r.stdout.strip())
