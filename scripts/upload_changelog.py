#!/opt/hermes/.venv/bin/python3
"""Upload changelog to R2"""
import sys
sys.path.insert(0, '/opt/data')
from r2_uploader import R2Uploader

change_log = open('/opt/data/fund_system_timing_v1.md', 'rb').read()

u = R2Uploader()
url = u.upload_bytes(change_log, 'fund-system/strategy/CHANGELOG_20250626_TIMING_FIX.md', content_type='text/markdown; charset=utf-8')
print('URL:', url)
