"""
Cloudflare R2 Upload utility using S3-compatible API

Credentials resolved in order:
  1. Explicit constructor args (highest priority)
  2. Environment variables R2_ACCOUNT_ID, R2_BUCKET, R2_ACCESS_KEY_ID,
     R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL, R2_ENDPOINT
  3. Default public_url derivation from bucket name
"""
import os
import boto3
from botocore.config import Config


class R2Uploader:
    def __init__(self, account_id=None, bucket_name=None, access_key_id=None,
                 secret_access_key=None, public_url=None, endpoint=None):
        self.account_id = account_id or os.environ.get('R2_ACCOUNT_ID', '')
        self.bucket_name = bucket_name or os.environ.get('R2_BUCKET', '')
        self.access_key_id = access_key_id or os.environ.get('R2_ACCESS_KEY_ID', '')
        self.secret_access_key = secret_access_key or os.environ.get('R2_SECRET_ACCESS_KEY', '')
        domain_suffix = os.environ.get('R2_PUBLIC_URL', '')
        if not domain_suffix and self.bucket_name:
            domain_suffix = f'https://{self.bucket_name}-media.devtoy.xyz'
        self.public_url = public_url or domain_suffix
        endpoint_url = endpoint or os.environ.get('R2_ENDPOINT', '')
        if not endpoint_url and self.account_id:
            endpoint_url = f'https://{self.account_id}.r2.cloudflarestorage.com'
        self.endpoint = endpoint_url

        if not all([self.account_id, self.bucket_name, self.access_key_id, self.secret_access_key]):
            raise ValueError(
                'R2Uploader: missing credentials. Provide via constructor args or set '
                'R2_ACCOUNT_ID, R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY in .env'
            )

        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name='auto',
            config=Config(signature_version='s3v4', retries={'max_attempts': 3})
        )

    def upload_bytes(self, data, key, content_type='application/octet-stream'):
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=data, ContentType=content_type)
        return self.get_public_url(key)

    def upload_file(self, file_path, key, content_type=None):
        if content_type is None:
            ct = {
                'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'gif': 'image/gif', 'pdf': 'application/pdf', 'gz': 'application/gzip',
                'tar': 'application/x-tar', 'md': 'text/markdown',
            }
            content_type = ct.get(key.rsplit('.', 1)[-1].lower(), 'application/octet-stream')
        self.s3.upload_file(file_path, self.bucket_name, key, ExtraArgs={'ContentType': content_type})
        return self.get_public_url(key)

    def list_objects(self, prefix='', limit=1000):
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix, MaxKeys=limit)
        return resp.get('Contents', [])

    def delete_object(self, key):
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)
        return True

    def delete_objects(self, keys):
        """Batch delete up to 1000 keys."""
        if not keys:
            return
        objects = [{'Key': k} for k in keys]
        for i in range(0, len(objects), 1000):
            batch = objects[i:i+1000]
            self.s3.delete_objects(Bucket=self.bucket_name, Delete={'Objects': batch})

    def get_public_url(self, key):
        return f'{self.public_url}/{key}'


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 r2_uploader.py <file_path> <key> [content_type]", file=sys.stderr)
        sys.exit(1)
    file_path = sys.argv[1]
    key = sys.argv[2]
    content_type = sys.argv[3] if len(sys.argv) > 3 else None
    uploader = R2Uploader()
    url = uploader.upload_file(file_path, key, content_type)
    if url:
        print(url)
    else:
        sys.exit(1)
