#!/usr/bin/env python3
"""微博登录脚本 - 生成二维码并等待扫码"""
import sys, json, time, os
sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')

from urllib.parse import parse_qs, urlparse
import httpx
import qrcode
from pathlib import Path

PASSPORT_URL = "https://passport.weibo.com"
QR_IMAGE_URL = "/sso/v2/qrcode/image"
QR_CHECK_URL = "/sso/v2/qrcode/check"
SSO_SIGNIN_URL = "/sso/signin"
QR_ENTRY = "miniblog"
QR_SOURCE = "miniblog"
QR_REDIRECT_URL = "https://weibo.com/"
QR_VERSION = "20250520"
RETCODE_SUCCESS = 20000000
RETCODE_QR_NOT_SCANNED = 50114001
RETCODE_QR_SCANNED = 50114002

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": f"{PASSPORT_URL}/sso/signin?entry=miniblog&source=miniblog&url=https://weibo.com/",
}

CONFIG_DIR = Path.home() / ".config" / "weibo-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"

print("📱 正在获取微博登录二维码...", flush=True)

with httpx.Client(
    base_url=PASSPORT_URL,
    headers=dict(HEADERS),
    follow_redirects=True,
    timeout=httpx.Timeout(30),
) as client:
    # Step 1: CSRF
    resp = client.get(SSO_SIGNIN_URL, params={
        "entry": QR_ENTRY, "source": QR_SOURCE, "url": QR_REDIRECT_URL,
    })
    csrf_token = client.cookies.get("X-CSRF-TOKEN")
    if not csrf_token:
        print("❌ CSRF token 获取失败", flush=True)
        sys.exit(1)
    client.headers["x-csrf-token"] = csrf_token

    # Step 2: 获取二维码
    resp = client.get(QR_IMAGE_URL, params={"entry": QR_ENTRY, "size": "180"})
    qr_data = resp.json()
    if qr_data.get("retcode") != RETCODE_SUCCESS:
        print(f"❌ 二维码获取失败: {qr_data}", flush=True)
        sys.exit(1)

    qrid = qr_data["data"]["qrid"]
    image_url = qr_data["data"]["image"]
    parsed = urlparse(image_url)
    qs = parse_qs(parsed.query)
    scan_url = qs.get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]

    # 保存二维码图片
    qr_img = qrcode.make(scan_url)
    img_path = "/opt/data/image_cache/weibo_qr_login.png"
    qr_img.save(img_path)
    
    print(f"QR_IMAGE_PATH:{img_path}", flush=True)
    print(f"⏳ 请用微博APP扫描上方二维码... (最长4分钟)", flush=True)
    print(f"   Qrid: {qrid[:20]}...", flush=True)

    # Step 3: 轮询等待
    start_time = time.time()
    scanned = False
    crossdomain_url = None

    while (time.time() - start_time) < 240:
        time.sleep(2)
        try:
            resp = client.get(QR_CHECK_URL, params={
                "entry": QR_ENTRY, "source": QR_SOURCE,
                "url": QR_REDIRECT_URL, "qrid": qrid,
                "rid": "", "ver": QR_VERSION,
            })
            check_data = resp.json()
            retcode = check_data.get("retcode")
            
            if retcode == RETCODE_QR_SCANNED:
                print("📱 已扫码! 请在手机上点击确认...", flush=True)
            elif retcode == RETCODE_SUCCESS:
                crossdomain_url = check_data.get("data", {}).get("crossdomain_url", "")
                print("✅ 登录成功!", flush=True)
                scanned = True
                break
        except Exception as e:
            pass

    if not scanned:
        print("❌ 超时未扫码", flush=True)
        sys.exit(1)

    # Step 4: 跟随跨域URL获取session
    if crossdomain_url:
        for url in crossdomain_url.split(","):
            url = url.strip()
            if url:
                try:
                    client.get(url, follow_redirects=True, timeout=10)
                except:
                    pass

    # Step 5: 保存凭据
    cookies = dict(client.cookies)
    credential = {"cookies": cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(credential, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    print(f"✅ 凭据已保存 ({len(cookies)} cookies)", flush=True)
    print(f"✅ 微博已就绪!", flush=True)
