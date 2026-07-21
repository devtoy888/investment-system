#!/opt/data/.venv/bin/python3
"""sync_ops_to_r2.py — 将操作记录markdown上传到R2"""

import sys, os, subprocess

HERMES = '/opt/data'
OPS_DIR = os.path.join(HERMES, 'fund_system_data', 'operations')
UPLOADER = os.path.join(HERMES, 'r2_uploader.py')

# R2 env
with open(os.path.join(HERMES, 'profiles', 'investment', '.env')) as f:
    for line in f:
        line = line.strip()
        if line.startswith('R2_') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k, v)

if not os.path.isdir(OPS_DIR):
    print("❌ 无操作目录")
    sys.exit(1)

files = sorted([f for f in os.listdir(OPS_DIR) if f.endswith('.md') and f != 'README.md'])
ok = 0
for fn in files:
    local = os.path.join(OPS_DIR, fn)
    key = f'fund-system/operations/{fn}'
    r = subprocess.run([sys.executable, UPLOADER, local, key, 'text/markdown; charset=utf-8'],
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        ok += 1
        print(f"  ✅ {fn}")
    else:
        print(f"  ❌ {fn}: {r.stderr[:100]}")

print(f"\n上传完成: {ok}/{len(files)}")
