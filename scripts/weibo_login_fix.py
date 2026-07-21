#!/usr/bin/env python3
"""微博登录修复版 - v1的header + v2的cookie捕获"""
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
RETCODE_SUCCESS = 20000000
RETCODE_QR_SCANNED = 50114002

CONFIG_DIR = Path.home() / ".config" / "weibo-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": f"{PASSPORT_URL}/sso/signin?entry=miniblog&source=miniblog&url=https://weibo.com/",
}

print("📱 正在获取微博登录二维码...", flush=True)

with httpx.Client(base_url=PASSPORT_URL, headers=dict(HEADERS), follow_redirects=True, timeout=httpx.Timeout(30)) as client:
    # Step 1: CSRF
    resp = client.get(SSO_SIGNIN_URL, params={"entry": "miniblog", "source": "miniblog", "url": "https://weibo.com/"})
    csrf = client.cookies.get("X-CSRF-TOKEN")
    if not csrf:
        print("❌ CSRF token 获取失败")
        sys.exit(1)
    client.headers["x-csrf-token"] = csrf

    # Step 2: 二维码
    resp = client.get(QR_IMAGE_URL, params={"entry": "miniblog", "size": "180"})
    qr_data = resp.json()
    if qr_data.get("retcode") != RETCODE_SUCCESS:
        print(f"❌ 二维码获取失败: {qr_data}")
        sys.exit(1)

    qrid = qr_data["data"]["qrid"]
    image_url = qr_data["data"]["image"]
    parsed = urlparse(image_url)
    qs = parse_qs(parsed.query)
    scan_url = qs.get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]

    qr_img = qrcode.make(scan_url)
    img_path = "/opt/data/image_cache/weibo_qr_login.png"
    qr_img.save(img_path)

    print(f"QR_IMAGE_PATH:{img_path}", flush=True)
    print("⏳ 请用微博APP扫码... (最长4分钟)", flush=True)

    # Step 3: 轮询扫码
    scanned = False
    crossdomain_url = None
    start = time.time()
    while (time.time() - start) < 240:
        time.sleep(2)
        try:
            resp = client.get(QR_CHECK_URL, params={
                "entry": "miniblog", "source": "miniblog",
                "url": "https://weibo.com/", "qrid": qrid, "rid": "", "ver": "20250520",
            })
            check = resp.json()
            rc = check.get("retcode")
            if rc == RETCODE_QR_SCANNED:
                print("📱 已扫码! 手机上点确认...", flush=True)
            elif rc == RETCODE_SUCCESS:
                crossdomain_url = check.get("data", {}).get("crossdomain_url", "")
                print("✅ 登录成功! 获取session...", flush=True)
                scanned = True
                break
        except:
            pass

    if not scanned:
        print("❌ 超时未扫码")
        sys.exit(1)

    # Step 4: 捕获全量cookie
    all_cookies = dict(client.cookies)

    # 4a. 跟随跨域URL
    if crossdomain_url:
        for url in (u.strip() for u in crossdomain_url.split(",") if u.strip()):
            try:
                with httpx.Client(follow_redirects=True, timeout=15) as c:
                    c.get(url)
                    for k, v in c.cookies.items():
                        all_cookies.setdefault(k, v)
            except:
                pass

    # 4b. 访问weibo.com
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as wb:
            wb.headers["User-Agent"] = HEADERS["User-Agent"]
            for k, v in client.cookies.items():
                wb.cookies.set(k, v, domain=".weibo.com")
            wb.get("https://weibo.com/")
            for k in ('SUB','SUBP','SSOLoginState','ALF','SUHB','SCF'):
                v = wb.cookies.get(k)
                if v:
                    all_cookies[k] = v
    except Exception as e:
        print(f"  ⚠️ weibo.com: {e}", flush=True)

    # Step 5: 保存
    credential = {"cookies": all_cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(credential, indent=2))
    CREDENTIAL_FILE.chmod(0o600)

    has_sub = 'SUB' in all_cookies
    print(f"✅ 凭据已保存 ({len(all_cookies)} cookies, 含SUB={has_sub})", flush=True)
    if has_sub:
        print("✅ 微博已就绪!")
    else:
        print("⚠️ 未获取到SUB cookie，请重新登录")
