#!/opt/hermes/.venv/bin/python3
"""
Hermes Agent — Restore from R2 backup.

Usage:
  /opt/hermes/.venv/bin/python3 /opt/data/scripts/restore_from_r2.py

Downloads the latest backup from R2 and extracts it to /opt/data/.
Run this INSIDE the Docker container.

Docker volume mapping: ~/.hermes-main:/opt/data
"""
import io
import os
import sys
import tarfile
import tempfile

HERMES_HOME = '/opt/data'
BACKUP_PREFIX = 'backups'


def find_latest_backup():
    sys.path.insert(0, HERMES_HOME)
    from r2_uploader import R2Uploader
    import boto3
    from botocore.config import Config

    u = R2Uploader()
    s3 = boto3.client(
        's3',
        endpoint_url=u.endpoint,
        aws_access_key_id=u.access_key_id,
        aws_secret_access_key=u.secret_access_key,
        region_name='auto',
        config=Config(signature_version='s3v4')
    )

    resp = s3.list_objects_v2(Bucket=u.bucket_name, Prefix=BACKUP_PREFIX + '/')
    if 'Contents' not in resp or not resp['Contents']:
        print('❌ No backups found in R2.')
        sys.exit(1)

    latest = sorted(resp['Contents'], key=lambda x: x['Key'])[-1]
    print(f'📦 Found: {latest["Key"]}  ({latest["Size"]/1024/1024:.1f} MB)')
    return u, s3, latest['Key']


def download_backup(s3, bucket, key):
    print(f'⬇️  Downloading...')
    resp = s3.get_object(Bucket=bucket, Key=key)
    data = resp['Body'].read()
    print(f'   ✅ {len(data)/1024/1024:.1f} MB downloaded')
    return data


def verify_backup(data):
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
            members = tar.getmembers()
            print(f'   ✅ Archive valid: {len(members)} files')
            return members
    except Exception as e:
        print(f'❌ Backup file is corrupt: {e}')
        sys.exit(1)


def extract_backup(data):
    target = HERMES_HOME

    # Show what will be restored
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        members = tar.getmembers()

    print()
    print('Files to restore:')
    for m in members:
        sz = f'{m.size/1024:.1f}K' if m.size < 1024**2 else f'{m.size/1024**2:.1f}M'
        print(f'  {m.name}  ({sz})')

    # Extract
    print()
    print(f'📂 Extracting to {target}/...')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        tar.extractall(path=target)
    print('   ✅ Extraction complete')

    # Fix permissions for sensitive files
    sensitive = ['.env']
    for f in sensitive:
        fp = os.path.join(target, f)
        if os.path.isfile(fp):
            os.chmod(fp, 0o600)
            print(f'   🔒 chmod 600 {f}')

    print()
    print('═' * 50)
    print('  ✅ Restore complete!')
    print('═' * 50)
    print()
    print('Next steps:')
    print('  1. Restart Hermes Gateway:  hermes gateway restart')
    print('  2. Verify:                  hermes doctor')
    print('  3. Check cron:              hermes cron list')
    print()
    print('If cron jobs were restored, they will run on their next')
    print('scheduled time. No further action needed.')


def main():
    print('═' * 50)
    print('  Hermes Agent — Restore from R2')
    print('═' * 50)
    print()

    # Check we're in the right place
    if not os.path.isfile(os.path.join(HERMES_HOME, 'config.yaml')):
        print(f'⚠️   Warning: {HERMES_HOME}/config.yaml not found.')
        print('   Are you running inside the Hermes Docker container?')
        resp = input('   Continue anyway? [y/N]: ')
        if resp.lower() != 'y':
            print('Aborted.')
            sys.exit(1)

    u, s3, key = find_latest_backup()
    data = download_backup(s3, u.bucket_name, key)
    verify_backup(data)

    print()
    resp = input('🔄 Restore these files to /opt/data/? [y/N]: ')
    if resp.lower() != 'y':
        print('Aborted.')
        sys.exit(1)

    extract_backup(data)


if __name__ == '__main__':
    main()
