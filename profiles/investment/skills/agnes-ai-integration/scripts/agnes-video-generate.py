#!/usr/bin/env python3
"""
Agnes Video V2.0 - Generate, poll, download, and optionally upload to R2.

Usage:
    python agnes-video-generate.py "prompt text" [--ratio 9:16] [--resolution 720p] [--upload]

Requires:
    - CUSTOM_AGNES_API_KEY in /opt/data/.env
    - (optional) R2 credentials for upload
"""
import os, sys, json, urllib.request, time, argparse

KEY_VAR = "OPENAI_API_KEY"
ENV_FILE = "/opt/data/.env"
BASE = "https://apihub.agnes-ai.com/v1"
AGNESAPI = "https://apihub.agnes-ai.com"
OUTPUT_DIR = "/opt/data"

def get_env(var):
    return os.popen(f"grep '{var}' {ENV_FILE} | cut -d= -f2-").read().strip()

def post(endpoint, payload, headers_extra=None, timeout=60):
    url = BASE + endpoint
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'Bearer {get_env(KEY_VAR)}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        **(headers_extra or {})
    })
    for attempt in range(3):
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
            return json.loads(resp.read()), resp.status
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            return {"http_code": e.code, "error": body}, e.code
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return {"exception": str(e)}, None
    return {}, None

def poll_task(video_id, max_polls=360, interval=5):
    """Poll using recommended /agnesapi?video_id= endpoint."""
    for i in range(max_polls):
        url = f"{AGNESAPI}/agnesapi?video_id={video_id}"
        data = json.dumps({}).encode()
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {get_env(KEY_VAR)}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read())
        except Exception as e:
            print(f"  Poll #{i+1} error: {e}")
            if i < max_polls - 1:
                time.sleep(interval)
                continue
            return {}

        status = result.get("status", "unknown")
        progress = result.get("progress", 0)
        print(f"  Poll #{i+1}: status={status}, progress={progress}%")
        if status == "completed":
            return result
        if status in ("failed", "error"):
            print(f"  FAILED: {result}")
            return result
        time.sleep(interval)
    print("  Timed out waiting for completion")
    return result

def download_video(url, local_path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    resp = urllib.request.urlopen(req, timeout=60)
    data = resp.read()
    with open(local_path, 'wb') as f:
        f.write(data)
    return len(data)

def upload_to_r2(local_path, key):
    import boto3
    access_key = get_env("R2_ACCESS_KEY_ID")
    secret_key = get_env("R2_SECRET_ACCESS_KEY")
    account_id = get_env("CLOUDFLARE_ACCOUNT_ID") or "a14f5ae92b9406c186b0f7f796fb7c50"
    
    s3 = boto3.client(
        's3',
        endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='auto'
    )
    bucket = "hermes-main"
    s3.upload_file(local_path, bucket, key)
    return f"https://hermes-main-media.devtoy.xyz/{key}"

def main():
    parser = argparse.ArgumentParser(description="Agnes Video V2.0 generator")
    parser.add_argument("prompt", help="Video generation prompt")
    parser.add_argument("--ratio", default="16:9", help="Aspect ratio (9:16, 16:9, 1:1, etc.)")
    parser.add_argument("--resolution", default="720p", help="Resolution (720p, 1080p, 480p)")
    parser.add_argument("--upload", action="store_true", help="Upload to R2 after generation")
    args = parser.parse_args()

    # Step 1: Create video task
    print("=== Creating video task ===")
    result, status = post("/videos", {
        "model": "agnes-video-v2.0",
        "prompt": args.prompt,
        "width": 768,
        "height": 1152,
        "num_frames": 121,
        "frame_rate": 24
    })
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if "exception" in result or "error" in result:
        print("ERROR creating video task")
        sys.exit(1)
    
    video_id = result.get("video_id")
    task_id = result.get("task_id") or result.get("id")
    print(f"Video ID: {video_id}")
    
    # Step 2: Poll for completion
    print("\n=== Polling for completion ===")
    completed = poll_task(video_id)
    
    if completed.get("status") != "completed":
        print("Video generation failed or timed out")
        sys.exit(1)
    
    # Step 3: Get video URL and download
    video_url = completed.get("remixed_from_video_id") or completed.get("video_url")
    if not video_url:
        print("No video URL found in response")
        sys.exit(1)
    
    filename = f"video_{int(time.time())}.mp4"
    local_path = os.path.join(OUTPUT_DIR, filename)
    print(f"\n=== Downloading video ===")
    size = download_video(video_url, local_path)
    print(f"Downloaded: {size} bytes ({size/1024/1024:.1f} MB) -> {local_path}")
    
    # Step 4: Upload to R2 if requested
    if args.upload:
        print(f"\n=== Uploading to R2 ===")
        r2_key = f"generated_videos/{int(time.time())}_{filename}"
        public_url = upload_to_r2(local_path, r2_key)
        print(f"R2 URL: {public_url}")
        print(f"Done! Local: {local_path} | Remote: {public_url}")
    else:
        print(f"\nDone! Video saved to: {local_path}")
        print(f"Video URL: {video_url}")

if __name__ == "__main__":
    main()
