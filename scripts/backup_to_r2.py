#!/opt/hermes/.venv/bin/python3
"""
Hermes Agent daily backup to Cloudflare R2.

Usage:
  /opt/hermes/.venv/bin/python3 /opt/data/scripts/backup_to_r2.py

What it backs up (minimal — only essential recovery files):
  - config.yaml, .env                        Core configuration
  - state.db                                 Session history
  - cron/jobs.json                           Scheduled job definitions
  - pairing/, memories/, plugins/            Auth, memory, extensions
  - Custom scripts (not in any repo)         User's custom tooling
  - Agent-created skills (author: Hermes)    Auto-generated skills

Retention: backups older than 15 days are purged from R2.
Directory: backups/YYYY-MM/YYYY-MM-DD_HHMM.tar.gz
"""
import io, os, sys, tarfile, tempfile
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# ── Paths ──────────────────────────────────────────────────────────
HERMES_HOME = '/opt/data'
SCRIPTS_DIR = os.path.join(HERMES_HOME, 'scripts')
SKILLS_DIR = os.path.join(HERMES_HOME, 'skills')

BACKUP_PREFIX = 'backups'            # R2 root path for backups
RETENTION_DAYS = 7

# Files to always include (relative to HERMES_HOME)
ESSENTIAL_FILES = [
    'config.yaml',
    '.env',
    'cron/jobs.json',
    'state.db',
]

ESSENTIAL_DIRS = [
    'pairing',
    'memories',
    'plugins',
]

# Custom scripts that live outside the skills/ hierarchy


def find_custom_scripts():
    """Find custom .py files: scripts/ dir (all) + known root-level user scripts."""
    results = []
    # All files in scripts/ directory
    scripts_dir = os.path.join(HERMES_HOME, 'scripts')
    if os.path.isdir(scripts_dir):
        for f in os.listdir(scripts_dir):
            if f.endswith('.py'):
                results.append(os.path.join('scripts', f))
    # Known root-level user scripts (manually maintained list — very stable)
    root_scripts = ['r2_uploader.py', 'generate_news_card_v3.py', 'generate_news_card.py']
    for rs in root_scripts:
        if os.path.isfile(os.path.join(HERMES_HOME, rs)):
            results.append(rs)
    return sorted(set(results))


def collect_all_skills(base_dir):
    """Yield (rel_path, abs_path) for every skill directory with a SKILL.md."""
    skills = []
    if not os.path.isdir(base_dir):
        return skills
    for entry in os.scandir(base_dir):
        if not entry.is_dir():
            continue
        # Check subdirectories
        for sub in os.scandir(entry.path):
            if sub.is_dir():
                sk_path = os.path.join(sub.path, 'SKILL.md')
                if os.path.isfile(sk_path):
                    skills.append((os.path.relpath(sub.path, base_dir), sub.path))
        # Also check the parent itself
        sk_path = os.path.join(entry.path, 'SKILL.md')
        if os.path.isfile(sk_path):
            skills.append((entry.name, entry.path))
    return skills


def size_fmt(size_bytes):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f'{size_bytes:.1f}{unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f}TB'


def create_backup_tar():
    """Build an in-memory tar.gz of all essential files."""
    beijing = ZoneInfo('Asia/Shanghai')
    now = datetime.now(beijing)
    ts = now.strftime('%Y%m%d_%H%M')
    date_prefix = now.strftime('%Y-%m-%d')
    r2_path = f'{BACKUP_PREFIX}/{now.strftime("%Y-%m")}/{date_prefix}_{ts}.tar.gz'

    buf = io.BytesIO()
    total_size = 0
    file_count = 0

    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        # Essential files
        for rel in ESSENTIAL_FILES:
            src = os.path.join(HERMES_HOME, rel)
            if os.path.isfile(src):
                tar.add(src, arcname=rel)
                sz = os.path.getsize(src)
                total_size += sz
                file_count += 1
                print(f'  + {rel} ({size_fmt(sz)})')

        # Essential directories
        for rel in ESSENTIAL_DIRS:
            src = os.path.join(HERMES_HOME, rel)
            if os.path.isdir(src):
                tar.add(src, arcname=rel)
                sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(src) for f in fn)
                total_size += sz
                file_count += 1
                print(f'  + {rel}/ ({size_fmt(sz)})')

        # Custom scripts (auto-discovered)
        for rel in find_custom_scripts():
            src = os.path.join(HERMES_HOME, rel)
            if os.path.isfile(src):
                tar.add(src, arcname=f'custom/{os.path.basename(rel)}')
                sz = os.path.getsize(src)
                total_size += sz
                file_count += 1
                print(f'  + custom/{os.path.basename(rel)} ({size_fmt(sz)})')

        # All skills (full directories — SKILL.md + references + scripts + templates)
        skill_count = 0
        for rel_path, abs_path in collect_all_skills(SKILLS_DIR):
            # Add the entire skill directory (small, all critical for recovery)
            tar.add(abs_path, arcname=f'skills/{rel_path}')
            sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(abs_path) for f in fn)
            total_size += sz
            skill_count += 1
            file_count += 1
        print(f'  + skills/ ({skill_count} directories, all files)')

    compressed_size = buf.tell()
    print(f'  ─────────────────')
    print(f'  📦 Total: {file_count} items, {size_fmt(total_size)} raw → {size_fmt(compressed_size)} compressed')
    return buf.getvalue(), r2_path, ts


def cleanup_old_backups(uploader, backup_prefix):
    """Remove backups older than RETENTION_DAYS from R2."""
    beijing = ZoneInfo('Asia/Shanghai')
    cutoff = datetime.now(beijing) - timedelta(days=RETENTION_DAYS)
    deleted = 0

    objects = uploader.list_objects(prefix=backup_prefix, limit=1000)
    to_delete = []
    for obj in objects:
        key = obj['Key']
        # Extract date from key: backups/YYYY-MM/YYYY-MM-DD_HHMM.tar.gz
        parts = key.split('/')
        if len(parts) >= 3:
            date_str = parts[-1][:10]  # YYYY-MM-DD
            try:
                obj_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=beijing)
                if obj_date < cutoff:
                    to_delete.append(key)
            except ValueError:
                continue

    if to_delete:
        # R2 batch delete has 1000 key limit; list_objects already caps there
        uploader.delete_objects(to_delete)
        deleted = len(to_delete)

    return deleted


def main():
    print('═' * 50)
    print('  Hermes Agent — Daily R2 Backup')
    print('═' * 50)
    print()

    # ── Step 1: Build backup archive ──
    print('📦 Creating backup archive...')
    try:
        data, r2_key, ts = create_backup_tar()
    except Exception as e:
        print(f'❌ Failed to create backup: {e}')
        sys.exit(1)

    # ── Step 2: Upload to R2 ──
    print()
    print('☁️  Uploading to R2...')
    try:
        sys.path.insert(0, HERMES_HOME)
        from r2_uploader import R2Uploader
        uploader = R2Uploader()
        url = uploader.upload_bytes(data, r2_key, 'application/gzip')
        print(f'  ✅ Uploaded: {url}')
    except Exception as e:
        print(f'❌ Upload failed: {e}')
        sys.exit(1)

    # ── Step 3: Clean old backups ──
    print()
    print('🧹 Cleaning old backups (>{RETENTION_DAYS}d)...')
    try:
        deleted = cleanup_old_backups(uploader, BACKUP_PREFIX)
        if deleted:
            print(f'  ✅ Removed {deleted} expired backup(s)')
        else:
            print(f'  ✅ No expired backups to remove')
    except Exception as e:
        print(f'  ⚠️  Cleanup failed (non-fatal): {e}')

    print()
    print('✅ Backup complete.')


if __name__ == '__main__':
    main()
