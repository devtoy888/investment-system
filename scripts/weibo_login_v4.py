#!/usr/bin/env python3
"""微博登录v4 - 调试版，打印crossdomain_url"""
import sys, json, time
sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')

from urllib.parse import parse_qs, urlparse
import httpx, requests as req_lib, re
import qrcode
from pathlib import Path

PASSPORT_URL = "https://passport.weibo.com"
CONFIG_DIR = Path.home() / ".config" / "weibo-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": f"{PASSPORT_URL}/sso/signin?entry=miniblog&source=miniblog&url=https://weibo.com/",
}

print("📱 获取二维码...", flush=True)
with httpx.Client(base_url=PASSPORT_URL, headers=dict(HEADERS), follow_redirects=True, timeout=30) as c:
    c.get("/sso/signin", params={"entry":"miniblog","source":"miniblog","url":"https://weibo.com/"})
    csrf = c.cookies.get("X-CSRF-TOKEN")
    c.headers["x-csrf-token"] = csrf

    resp = c.get("/sso/v2/qrcode/image", params={"entry":"miniblog","size":"180"})
    qr_data = resp.json()
    qrid = qr_data["data"]["qrid"]
    scan_url = parse_qs(urlparse(qr_data["data"]["image"]).query)["data"][0]
    
    qrcode.make(scan_url).save("/opt/data/image_cache/weibo_qr_login.png")
    print(f"QR_IMAGE_PATH:/opt/data/image_cache/weibo_qr_login.png", flush=True)
    print("⏳ 扫码...", flush=True)

    crossdomain_url = None
    start = time.time()
    while time.time() - start < 240:
        time.sleep(2)
        try:
            r = c.get("/sso/v2/qrcode/check", params={"entry":"miniblog","source":"miniblog","url":"https://weibo.com/","qrid":qrid,"rid":"","ver":"20250520"})
            d = r.json()
            if d.get("retcode") == 20000000:
                crossdomain_url = d.get("data",{}).get("crossdomain_url","")
                print(f"✅ 登录成功!", flush=True)
                print(f"🔗 crossdomain_url = {crossdomain_url[:200] if crossdomain_url else '空'}", flush=True)
                break
        except:
            pass
    else:
        print("❌ 超时")
        sys.exit(1)

    # 调试: 打印passport全部cookies
    print(f"  passport cookies: {dict(c.cookies)}", flush=True)

    # 用requests直接跟随跨域
    all_cookies = dict(c.cookies)

    if crossdomain_url:
        for url in (u.strip() for u in crossdomain_url.split(",") if u.strip()):
            print(f"  跨域: {url[:80]}...", flush=True)
            try:
                s = req_lib.Session()
                s.headers.update({"User-Agent": HEADERS["User-Agent"]})
                for k, v in all_cookies.items():
                    s.cookies.set(k, v)
                r = s.get(url, timeout=15)
                print(f"    状态={r.status_code}, new cookies={dict(s.cookies)}", flush=True)
                for k, v in dict(s.cookies).items():
                    all_cookies[k] = v
                s.close()
            except Exception as e:
                print(f"    ⚠️ {e}", flush=True)

    # 访问weibo.com
    try:
        s = req_lib.Session()
        s.headers.update({"User-Agent": HEADERS["User-Agent"], "Referer": "https://weibo.com/"})
        for k, v in all_cookies.items():
            s.cookies.set(k, v, domain=".weibo.com")
        r = s.get("https://weibo.com/", timeout=15)
        print(f"  weibo.com status={r.status_code}, cookies={dict(s.cookies)}", flush=True)
        for k, v in dict(s.cookies).items():
            all_cookies[k] = v
        # 从raw header捕获
        for name, val in r.headers.items():
            if name.lower() == 'set-cookie':
                for m in re.finditer(r'(SUB|SUBP|SCF|ALF|SUHB|SSOLoginState|PC_TOKEN)=([^;]+)', val):
                    all_cookies.setdefault(m.group(1), m.group(2))
        s.close()
    except Exception as e:
        print(f"  ⚠️ {e}", flush=True)

    # 再试一次带X-CSRF-TOKEN
    try:
        s = req_lib.Session()
        s.headers.update({
            "User-Agent": HEADERS["User-Agent"],
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRF-TOKEN": all_cookies.get("X-CSRF-TOKEN",""),
            "Referer": "https://weibo.com/",
        })
        for k, v in all_cookies.items():
            s.cookies.set(k, v, domain=".weibo.com")
        r = s.get("https://weibo.com/ajax/statuses/mymblog?uid=2014433131&page=1&feature=1", timeout=15)
        print(f"  API status={r.status_code}, json={r.text[:200]}", flush=True)
    except Exception as e:
        print(f"  ⚠️ {e}", flush=True)

    # 保存
    cred = {"cookies": all_cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(cred, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    print(f"✅ {len(all_cookies)} cookies, SUB={'SUB' in all_cookies}", flush=True)
