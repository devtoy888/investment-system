"""
Cloudflare R2 Upload utility using S3-compatible API.
Reads credentials from environment variables by default.
"""
import os
import boto3
from botocore.config import Config


class R2Uploader:
    """S3-compatible R2 upload client.

    When called with no arguments, reads credentials from environment:
      R2_ACCOUNT_ID, R2_BUCKET, R2_ACCESS_KEY_ID,
      R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL, R2_ENDPOINT
    """

    def __init__(self, account_id=None, bucket_name=None,
                 access_key_id=None, secret_access_key=None,
                 public_url=None, endpoint=None):
        self.account_id = account_id or os.environ.get('R2_ACCOUNT_ID', '')
        self.bucket_name = bucket_name or os.environ.get('R2_BUCKET', '')
        ak = access_key_id or os.environ.get('R2_ACCESS_KEY_ID', '')
        sk = secret_access_key or os.environ.get('R2_SECRET_ACCESS_KEY', '')
        self.endpoint = endpoint or os.environ.get(
            'R2_ENDPOINT', f'https://{self.account_id}.r2.cloudflarestorage.com')
        self.public_url = public_url or os.environ.get(
            'R2_PUBLIC_URL', f'https://{self.bucket_name}-media.devtoy.xyz')

        if not all([self.account_id, self.bucket_name, ak, sk]):
            missing = [v for v, n in [
                ('R2_ACCOUNT_ID', self.account_id),
                ('R2_BUCKET', self.bucket_name),
                ('R2_ACCESS_KEY_ID', ak),
                ('R2_SECRET_ACCESS_KEY', sk),
            ] if not n]
            raise ValueError(
                f'R2 credentials not configured. Missing: {", ".join(missing)}. '
                'Set these in .env or pass to constructor.'
            )

        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name='auto',
            config=Config(signature_version='s3v4', retries={'max_attempts': 3})
        )

    def upload_bytes(self, data, key, content_type='application/octet-stream'):
        self.s3.put_object(Bucket=self.bucket_name, Key=key,
                           Body=data, ContentType=content_type)
        return self.get_public_url(key)

    def upload_file(self, file_path, key, content_type=None):
        if content_type is None:
            ct_map = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'pdf': 'application/pdf',
                'gz': 'application/gzip',
                'tar.gz': 'application/gzip',
            }
            ext = key.rsplit('.', 1)[-1].lower()
            if key.endswith('.tar.gz'):
                ext = 'tar.gz'
            content_type = ct_map.get(ext, 'application/octet-stream')
        self.s3.upload_file(file_path, self.bucket_name, key,
                            ExtraArgs={'ContentType': content_type})
        return self.get_public_url(key)

    def list_objects(self, prefix='', limit=1000):
        resp = self.s3.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix, MaxKeys=limit)
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
