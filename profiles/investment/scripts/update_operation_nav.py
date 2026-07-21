#!/usr/bin/env python3
"""Wrapper: run update_operation_nav from /opt/data/scripts"""
import subprocess, sys, os
os.chdir('/opt/data/scripts')
result = subprocess.run([sys.executable, '/opt/data/scripts/update_operation_nav.py'],
                       capture_output=True, text=True, timeout=180)
if result.stdout:
    print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
