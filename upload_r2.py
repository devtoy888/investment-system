#!/usr/bin/env python3
import os, json, time, hashlib

# R2 credentials
r2_access_key = os.popen("grep 'R2_ACCESS_KEY_ID' /opt/data/.env | cut -d= -f2-").read().strip()
r2_secret = os.popen("grep 'R2_SECRET_ACCESS_KEY' /opt/data/.env | cut -d= -f2-").read().strip()
r2_account_id = os.popen("grep 'CLOUDFLARE_ACCOUNT_ID' /opt/data/.env | cut -d= -f2-").read().strip()

# If no CLOUDFLARE_ACCOUNT_ID, try the known one from memory
if not r2_account_id:
    r2_account_id = "a14f5ae92b9406c186b0f7f796fb7c50"

print(f"R2 Account ID: {r2_account_id}")
print(f"R2 Access Key: {r2_access_key}")
print(f"R2 Secret length: {len(r2_secret)}")

# Upload to R2 using boto3
import boto3

s3 = boto3.client(
    's3',
    endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
    aws_access_key_id=r2_access_key,
    aws_secret_access_key=r2_secret,
    region_name='auto'
)

bucket = "hermes-main"
timestamp = int(time.time())
key = f"generated_videos/{timestamp}_chinese_woman.mp4"

local_path = "/opt/data/generated_video.mp4"

print(f"\nUploading to R2: {bucket}/{key}")
s3.upload_file(local_path, bucket, key)
public_url = f"https://hermes-main-media.devtoy.xyz/{key}"
print(f"Public URL: {public_url}")
