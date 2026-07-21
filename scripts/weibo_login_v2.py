#!/usr/bin/env python3
"""微博登录脚本v2 - 正确捕获session cookie"""
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
}

CONFIG_DIR = Path.home() / ".config" / "weibo-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"

print("📱 正在获取微博登录二维码...", flush=True)

# 使用同一个session，确保cookie一致性
with httpx.Client(
    base_url=PASSPORT_URL,
    headers=dict(HEADERS),
    follow_redirects=True,
    timeout=httpx.Timeout(30),
) as passport_client:
    # Step 1: CSRF
    resp = passport_client.get(SSO_SIGNIN_URL, params={
        "entry": QR_ENTRY, "source": QR_SOURCE, "url": QR_REDIRECT_URL,
    })
    csrf_token = passport_client.cookies.get("X-CSRF-TOKEN")
    if not csrf_token:
        print("❌ CSRF token 获取失败", flush=True)
        sys.exit(1)
    passport_client.headers["x-csrf-token"] = csrf_token

    # Step 2: 获取二维码
    resp = passport_client.get(QR_IMAGE_URL, params={"entry": QR_ENTRY, "size": "180"})
    qr_data = resp.json()
    if qr_data.get("retcode") != RETCODE_SUCCESS:
        print(f"❌ 二维码获取失败: {qr_data}", flush=True)
        sys.exit(1)

    qrid = qr_data["data"]["qrid"]
    image_url = qr_data["data"]["image"]
    parsed = urlparse(image_url)
    qs = parse_qs(parsed.query)
    scan_url = qs.get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]

    # 生成二维码图片
    qr_img = qrcode.make(scan_url)
    img_path = "/opt/data/image_cache/weibo_qr_login.png"
    qr_img.save(img_path)
    
    print(f"QR_IMAGE_PATH:{img_path}", flush=True)
    print(f"⏳ 等待扫码... (最长4分钟)", flush=True)

    # Step 3: 轮询
    start_time = time.time()
    scanned = False
    crossdomain_url = None

    while (time.time() - start_time) < 240:
        time.sleep(2)
        try:
            resp = passport_client.get(QR_CHECK_URL, params={
                "entry": QR_ENTRY, "source": QR_SOURCE,
                "url": QR_REDIRECT_URL, "qrid": qrid,
                "rid": "", "ver": QR_VERSION,
            })
            check_data = resp.json()
            retcode = check_data.get("retcode")
            
            if retcode == RETCODE_QR_SCANNED:
                print("📱 已扫码! 在手机上确认...", flush=True)
            elif retcode == RETCODE_SUCCESS:
                crossdomain_url = check_data.get("data", {}).get("crossdomain_url", "")
                print("✅ 登录成功! 正在获取session...", flush=True)
                scanned = True
                break
        except Exception as e:
            print(f"⚠️ {e}", flush=True)

    if not scanned:
        print("❌ 超时未扫码", flush=True)
        sys.exit(1)

    # Step 4: 跟随跨域URL获取真正的session cookie
    # 这里的crossdomain_url可能包含多个URL，用逗号分隔
    # 我们用独立的session来跟随，确保捕获所有cookie
    all_cookies = {}
    
    # 先捕获passport session的cookies
    for k, v in passport_client.cookies.items():
        all_cookies[k] = v
    
    if crossdomain_url:
        urls = [u.strip() for u in crossdomain_url.split(",") if u.strip()]
        print(f"   跟随 {len(urls)} 个跨域URL获取session...", flush=True)
        for url in urls:
            try:
                # 对每个跨域URL使用独立的client来捕获cookie
                with httpx.Client(follow_redirects=True, timeout=15) as c:
                    c.get(url)
                    for k, v in c.cookies.items():
                        # 只保留有价值的cookie
                        if k in ('SUB', 'SUBP', 'SSOLoginState', 'ALF', 'SUHB'):
                            all_cookies[k] = v
            except Exception as e:
                print(f"   ⚠️ 跨域 {url[:50]}: {e}", flush=True)
    
    # 额外：访问weibo.com主页捕获更多cookie
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as wb:
            wb.headers.update({"User-Agent": HEADERS["User-Agent"]})
            # 把passport的cookie带过去
            for k, v in passport_client.cookies.items():
                wb.cookies.set(k, v, domain=".weibo.com")
            r = wb.get("https://weibo.com/")
            for k, v in wb.cookies.items():
                if k in ('SUB', 'SUBP', 'SSOLoginState', 'ALF', 'SUHB'):
                    all_cookies[k] = v
    except Exception as e:
        print(f"   ⚠️ weibo.com: {e}", flush=True)

    # Step 5: 保存凭据
    credential = {"cookies": all_cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(credential, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    
    has_sub = 'SUB' in all_cookies
    print(f"✅ 凭据已保存 ({len(all_cookies)} cookies)", flush=True)
    print(f"✅ 含SUB cookie: {has_sub}", flush=True)
    if has_sub:
        print("✅ 微博已就绪!", flush=True)
    else:
        print("⚠️ 未获取到SUB cookie，可能需要重新登录", flush=True)

PYEOF
