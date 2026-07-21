#!/opt/hermes/.venv/bin/python3
"""
Hermes Agent — Safe periodic cleanup.

Safe cleanups (no user approval needed):
  1. uv cache:    uv cache clean
  2. npm cache:   rm -rf home/.npm/ .npm/
  3. .env.bak:    delete outdated backup copies
  4. /tmp old test artifacts (>24h old, known patterns)
  5. cron output: prune >7 days
  6. logs:        truncate/rotate >30 days

Unsafe candidates (report only, user decides):
  - Unknown large files (>50MB, not in known paths)
  - Stale git repos, old downloads

Usage:
  /opt/hermes/.venv/bin/python3 /opt/data/scripts/auto_cleanup.py
  /opt/hermes/.venv/bin/python3 /opt/data/scripts/auto_cleanup.py --report  (dry run only)
"""
import os, shutil, glob, sys, time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERMES_HOME = '/opt/data'
HOME_DIR    = os.path.join(HERMES_HOME, 'home')
TMP_DIR     = '/tmp'

RETENTION = {
    'cron_output_days': 7,
    'log_days': 30,
}

# ── Safe cleanup targets ──────────────────────────────────────────

SAFE_TMP_PATTERNS = [
    'daily-card*.png',
    'test_*.png',
    '*.mp4',
    'gh_*.tar.gz',
    'gh_*_linux_*',
]

SAFE_CACHE_DIRS = [
    os.path.join(HOME_DIR, '.npm'),
    os.path.join(HERMES_HOME, '.npm'),
]

SAFE_SPECIAL = [
    lambda: cleanup_uv_cache(),
    lambda: cleanup_env_bak(),
    lambda: cleanup_cron_output(),
    lambda: cleanup_logs(),
    lambda: cleanup_tmp_by_age(),
]


def size_fmt(b):
    for u in ('B','KB','MB','GB'):
        if b < 1024: return f'{b:.1f}{u}'
        b /= 1024
    return f'{b:.1f}TB'


def cleanup_uv_cache():
    import subprocess
    result = subprocess.run(['uv', 'cache', 'clean'], capture_output=True, text=True, timeout=30)
    out = result.stdout.strip()
    print(f'  🟢 uv cache cleaned ({out or "ok"})')


def cleanup_env_bak():
    deleted = 0
    for f in os.listdir(HERMES_HOME):
        if f.startswith('.env.bak'):
            os.remove(os.path.join(HERMES_HOME, f))
            deleted += 1
    if deleted:
        print(f'  🟢 Removed {deleted} .env.bak file(s)')


def cleanup_cron_output():
    cron_out = os.path.join(HERMES_HOME, 'cron', 'output')
    if not os.path.isdir(cron_out):
        return
    cutoff = time.time() - RETENTION['cron_output_days'] * 86400
    deleted = 0
    for root, dirs, files in os.walk(cron_out):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.getmtime(fp) < cutoff:
                os.remove(fp)
                deleted += 1
    if deleted:
        print(f'  🟢 Pruned {deleted} cron output file(s) >{RETENTION["cron_output_days"]}d')


def cleanup_logs():
    log_dir = os.path.join(HERMES_HOME, '.hermes', 'logs')
    if not os.path.isdir(log_dir):
        log_dir = os.path.join(HERMES_HOME, 'logs')
    if not os.path.isdir(log_dir):
        return
    cutoff = time.time() - RETENTION['log_days'] * 86400
    deleted = 0
    for f in os.listdir(log_dir):
        fp = os.path.join(log_dir, f)
        if os.path.isfile(fp) and os.path.getmtime(fp) < cutoff:
            os.remove(fp)
            deleted += 1
    if deleted:
        print(f'  🟢 Pruned {deleted} log file(s) >{RETENTION["log_days"]}d')


def cleanup_tmp_by_age():
    cutoff = time.time() - 86400  # >24h
    deleted = 0
    for pattern in SAFE_TMP_PATTERNS:
        for fp in glob.glob(os.path.join(TMP_DIR, pattern)):
            if os.path.isfile(fp) and os.path.getmtime(fp) < cutoff:
                os.remove(fp)
                deleted += 1
    if deleted:
        print(f'  🟢 Removed {deleted} old /tmp test artifact(s) (>24h)')


def clean_npm_cache():
    deleted_size = 0
    for d in SAFE_CACHE_DIRS:
        if os.path.isdir(d):
            sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(d) for f in fn)
            shutil.rmtree(d)
            deleted_size += sz
            print(f'  🟢 Removed npm cache: {d} ({size_fmt(sz)})')


def do_safe_cleanup(report_only=False):
    print('Safe cleanups:')
    if not report_only:
        clean_npm_cache()
        for fn in SAFE_SPECIAL:
            try:
                fn()
            except Exception as e:
                print(f'  ⚠️  {fn.__name__} error: {e}')
    else:
        print('  (report mode — would clean uv, npm, .env.bak, /tmp test artifacts, old cron/logs)')


# ── Unsafe candidates ─────────────────────────────────────────────

def scan_unknown_large_files():
    """Find files >50MB outside known safe paths."""
    candidates = []
    safe_prefixes = [
        HERMES_HOME + '/venv/',
        HERMES_HOME + '/.venv/',
        HERMES_HOME + '/.feishu-deps/',
        HERMES_HOME + '/feishu-deps/',
        HERMES_HOME + '/.hf-deps/',
        HERMES_HOME + '/.local/',
        HERMES_HOME + '/home/.local/',
        HERMES_HOME + '/home/.cache/',
        HERMES_HOME + '/bin/',
    ]

    for root, dirs, files in os.walk(HERMES_HOME):
        # Skip known safe dirs
        if any(root.startswith(p) for p in safe_prefixes):
            continue
        # Skip hidden dirs
        if '/.' in root[len(HERMES_HOME):]:
            continue

        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                if sz > 50 * 1024 * 1024:  # >50MB
                    candidates.append((fp, sz))
            except OSError:
                continue
    return candidates


def do_unsafe_scan():
    print()
    print('Unsafe candidates (large files >50MB, review needed):')
    candidates = scan_unknown_large_files()
    if not candidates:
        print('  ✅ None found')
        return
    for fp, sz in sorted(candidates, key=lambda x: -x[1]):
        rel = os.path.relpath(fp, HERMES_HOME)
        print(f'  🟡 {rel}  ({size_fmt(sz)})')
    print()
    print('These require your review. Run cleanup manually.')


# ── Main ───────────────────────────────────────────────────────────

def main():
    beijing = ZoneInfo('Asia/Shanghai')
    now = datetime.now(beijing).strftime('%Y-%m-%d %H:%M')
    print(f'Hermes Auto Cleanup — {now} (Beijing)')
    print('═' * 50)

    report_only = '--report' in sys.argv

    if report_only:
        print('DRY RUN MODE — no files will be deleted')
        print()

    do_safe_cleanup(report_only)
    do_unsafe_scan()

    print()
    print('✅ Cleanup scan complete.')


if __name__ == '__main__':
    main()
