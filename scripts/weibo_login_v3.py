#!/usr/bin/env python3
"""微博登录v3 - 直接抓Set-Cookie"""
import sys, json, time, os
sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')

from urllib.parse import parse_qs, urlparse
import httpx, re
import qrcode
from pathlib import Path

PASSPORT_URL = "https://passport.weibo.com"
COOKIE_DOMAIN = ".weibo.com"

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
    resp = client.get("/sso/signin", params={"entry": "miniblog", "source": "miniblog", "url": "https://weibo.com/"})
    csrf = client.cookies.get("X-CSRF-TOKEN")
    if not csrf:
        print("❌ CSRF token 获取失败")
        sys.exit(1)
    client.headers["x-csrf-token"] = csrf

    # Step 2: 二维码
    resp = client.get("/sso/v2/qrcode/image", params={"entry": "miniblog", "size": "180"})
    qr_data = resp.json()
    qrid = qr_data["data"]["qrid"]
    image_url = qr_data["data"]["image"]
    parsed = urlparse(image_url)
    qs = parse_qs(parsed.query)
    scan_url = qs.get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]

    qr_img = qrcode.make(scan_url)
    img_path = "/opt/data/image_cache/weibo_qr_login.png"
    qr_img.save(img_path)
    print(f"QR_IMAGE_PATH:{img_path}", flush=True)
    print("⏳ 扫码... 最长4分钟", flush=True)

    # Step 3: 轮询
    crossdomain_url = None
    start = time.time()
    while (time.time() - start) < 240:
        time.sleep(2)
        try:
            resp = client.get("/sso/v2/qrcode/check", params={
                "entry": "miniblog", "source": "miniblog",
                "url": "https://weibo.com/", "qrid": qrid, "rid": "", "ver": "20250520",
            })
            check = resp.json()
            rc = check.get("retcode")
            if rc == 50114002:
                print("📱 已扫码! 确认...", flush=True)
            elif rc == 20000000:
                crossdomain_url = check.get("data", {}).get("crossdomain_url", "")
                print("✅ 登录成功!", flush=True)
                break
        except:
            pass
    else:
        print("❌ 超时")
        sys.exit(1)

    # Step 4: 用requests库替代httpx，因为httpx的自动cookie管理可能有问题
    import requests as req_lib
    
    all_cookies = dict(client.cookies)
    print(f"  passport cookies: {list(all_cookies.keys())}", flush=True)

    # 4a. 跟随跨域 - 用requests.Session正确处理set-cookie
    if crossdomain_url:
        for url in (u.strip() for u in crossdomain_url.split(",") if u.strip()):
            try:
                s = req_lib.Session()
                s.headers.update(HEADERS)
                for k, v in all_cookies.items():
                    s.cookies.set(k, v)
                r = s.get(url, timeout=15)
                for k, v in dict(s.cookies).items():
                    if k not in all_cookies:
                        all_cookies[k] = v
                        print(f"  跨域获取: {k}", flush=True)
                s.close()
            except Exception as e:
                print(f"  ⚠️ 跨域: {e}", flush=True)

    # 4b. 访问weibo.com - 直接捕获Set-Cookie
    try:
        s = req_lib.Session()
        s.headers.update({
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://weibo.com/",
        })
        for k, v in all_cookies.items():
            s.cookies.set(k, v, domain=COOKIE_DOMAIN)
        r = s.get("https://weibo.com/", timeout=15)
        # 直接从响应头抓Set-Cookie
        for k, v in dict(s.cookies).items():
            if k not in all_cookies or k in ('SUB','SUBP','SCF'):
                all_cookies[k] = v
                print(f"  主页获取: {k}", flush=True)
        # 从raw headers再抓一遍
        for name, value in r.headers.items():
            if name.lower() == 'set-cookie':
                for match in re.finditer(r'(SUB|SUBP|SCF|ALF|SUHB)=([^;]+)', value):
                    k, v = match.group(1), match.group(2)
                    all_cookies[k] = v
                    print(f"  header捕获: {k}", flush=True)
        s.close()
    except Exception as e:
        print(f"  ⚠️ weibo: {e}", flush=True)

    # 保存
    credential = {"cookies": all_cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(credential, indent=2))
    CREDENTIAL_FILE.chmod(0o600)

    has_sub = 'SUB' in all_cookies
    print(f"✅ {len(all_cookies)} cookies (SUB={has_sub})", flush=True)
    print("✅ 微博已就绪!" if has_sub else "⚠️ 无SUB", flush=True)
