#!/usr/bin/env python3
"""微博扫码登录 - 直接生成二维码图片并等待扫码"""
import sys, json, time
sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')

from urllib.parse import parse_qs, urlparse
import httpx, requests, qrcode, re
from pathlib import Path

PASSPORT_URL = "https://passport.weibo.com"
CONFIG_DIR = Path.home() / ".config" / "weibo-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": f"{PASSPORT_URL}/sso/signin?entry=miniblog&source=miniblog&url=https://weibo.com/",
}

with httpx.Client(base_url=PASSPORT_URL, headers=dict(HEADERS), follow_redirects=True, timeout=30) as c:
    # 1. CSRF
    c.get("/sso/signin", params={"entry":"miniblog","source":"miniblog","url":"https://weibo.com/"})
    c.headers["x-csrf-token"] = c.cookies.get("X-CSRF-TOKEN")
    
    # 2. 二维码
    r = c.get("/sso/v2/qrcode/image", params={"entry":"miniblog","size":"180"})
    img_url = r.json()["data"]["image"]
    qrid = r.json()["data"]["qrid"]
    scan_url = parse_qs(urlparse(img_url).query).get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]
    
    # 生成图片
    qrcode.make(scan_url).save("/opt/data/image_cache/weibo_qr_login.png")
    print(f"QRID={qrid}", flush=True)
    print("QR_CODE_READY", flush=True)
    
    # 3. 等待扫码（最多4分钟）
    start = time.time()
    scanned = False
    crossdomain_url = None
    
    while time.time() - start < 240:
        time.sleep(2)
        try:
            r = c.get("/sso/v2/qrcode/check", params={
                "entry":"miniblog","source":"miniblog","url":"https://weibo.com/",
                "qrid":qrid,"rid":"","ver":"20250520"
            })
            d = r.json()
            rc = d.get("retcode")
            if rc == 50114002:
                print("SCANNED_WAIT_CONFIRM", flush=True)
            elif rc == 20000000:
                crossdomain_url = d.get("data",{}).get("crossdomain_url","")
                print("LOGIN_SUCCESS", flush=True)
                scanned = True
                break
        except:
            pass
    
    if not scanned:
        print("QR_TIMEOUT", flush=True)
        sys.exit(1)
    
    # 4. 捕获cookie
    cookies = dict(c.cookies)
    
    # 跨域
    if crossdomain_url:
        for url in (u.strip() for u in crossdomain_url.split(",") if u.strip()):
            try:
                s = requests.Session()
                s.headers.update({"User-Agent": HEADERS["User-Agent"]})
                for k, v in cookies.items():
                    s.cookies.set(k, v)
                s.get(url, timeout=15)
                cookies.update(dict(s.cookies))
                s.close()
            except:
                pass
    
    # weibo.com
    try:
        s = requests.Session()
        s.headers.update({"User-Agent": HEADERS["User-Agent"], "Referer": "https://weibo.com/"})
        for k, v in cookies.items():
            s.cookies.set(k, v, domain=".weibo.com")
        r = s.get("https://weibo.com/", timeout=15)
        cookies.update(dict(s.cookies))
        # Set-Cookie headers
        for name, val in r.headers.items():
            if name.lower() == "set-cookie":
                for m in re.finditer(r'(SUB|SUBP|SCF|ALF|SUHB|SSOLoginState)=([^;]+)', val):
                    cookies.setdefault(m.group(1), m.group(2))
        s.close()
    except:
        pass
    
    # 保存
    cred = {"cookies": cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(cred, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    
    print(f"COOKIES={len(cookies)} SUB={'SUB' in cookies}", flush=True)
    
    # 验证
    r = requests.get("https://weibo.com/ajax/statuses/mymblog",
        params={"uid":"2014433131","page":"1","feature":"1"},
        cookies=cookies, headers=HEADERS, timeout=15)
    ok = r.json().get("ok")
    print(f"VERIFY={ok}", flush=True)
    print("DONE" if ok == 1 else "FAILED", flush=True)
