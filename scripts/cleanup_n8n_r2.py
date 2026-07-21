#!/opt/hermes/.venv/bin/python3
"""
n8n R2 backup cleanup — retains only last 15 days.

Scans devtoy-oracle-n8n-backup bucket and deletes:
  - db/YYYY-MM-DD-*.sqlite  older than 15 days
  - xhs-media/YYYYMMDD/*    older than 15 days

Runs as Hermes cron job (no_agent=True, 0 token cost).
"""
import sys, os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, '/opt/data')
from r2_uploader import R2Uploader

BUCKET = 'devtoy-oracle-n8n-backup'
RETENTION_DAYS = 15


def parse_db_date(key):
    """Extract date from db/YYYY-MM-DD-*.sqlite"""
    parts = key.split('/')
    if len(parts) >= 2:
        # db/2026-06-22-xxx.sqlite → "2026-06-22"
        fn = parts[-1]
        date_str = fn[:10]
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
    return None


def parse_xhs_date(key):
    """Extract date from xhs-media/YYYYMMDD/filename"""
    parts = key.split('/')
    if len(parts) >= 2:
        folder = parts[1]
        if len(folder) == 8 and folder.isdigit():
            # YYYYMMDD → YYYY-MM-DD
            return f'{folder[:4]}-{folder[4:6]}-{folder[6:8]}'
    return None


def main():
    beijing = ZoneInfo('Asia/Shanghai')
    now = datetime.now(beijing)
    cutoff = now - timedelta(days=RETENTION_DAYS)
    cutoff_str = cutoff.strftime('%Y-%m-%d')

    print(f'n8n R2 Cleanup — {now.strftime("%Y-%m-%d %H:%M")} Beijing')
    print(f'Bucket: {BUCKET}')
    print(f'Retention: {RETENTION_DAYS} days (keep after {cutoff_str})')
    print('═' * 50)

    u = R2Uploader(bucket_name=BUCKET)
    objs = u.list_objects(prefix='', limit=1000)
    print(f'Total objects in bucket: {len(objs)}')

    to_delete = []
    kept_db = 0
    kept_xhs = 0

    for o in objs:
        key = o['Key']
        date_str = None

        if key.startswith('db/'):
            date_str = parse_db_date(key)
        elif key.startswith('xhs-media/'):
            date_str = parse_xhs_date(key)

        if date_str:
            try:
                obj_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=beijing)
                if obj_date < cutoff:
                    to_delete.append(key)
                else:
                    if key.startswith('db/'):
                        kept_db += 1
                    else:
                        kept_xhs += 1
            except ValueError:
                pass  # couldn't parse date, keep it

    print()
    if to_delete:
        print(f'To delete: {len(to_delete)} files')
        # Show summary by date
        from collections import Counter
        by_type = Counter()
        for k in to_delete:
            if k.startswith('db/'):
                by_type['db'] += 1
            else:
                by_type['xhs-media'] += 1
        for t, c in by_type.most_common():
            print(f'  {t}: {c} files')
        
        total_sz = sum(o['Size'] for o in objs if o['Key'] in to_delete)
        print(f'  Total size: {total_sz/1024/1024:.1f} MB')
        print()
        print('Deleting...')
        u.delete_objects(to_delete)
        print(f'✅ Deleted {len(to_delete)} old backup file(s)')
    else:
        print('✅ Nothing to delete (all files within retention period)')

    print(f'Kept: {kept_db} db/ + {kept_xhs} xhs-media/ files')
    print('✅ Cleanup complete.')


if __name__ == '__main__':
    main()
