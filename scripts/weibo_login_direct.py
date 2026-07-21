#!/usr/bin/env python3
"""微博登录 - 直接下载微博服务器的二维码图片"""
import sys, json, time
sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')

from urllib.parse import parse_qs, urlparse
import httpx, requests, re
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
    c.get("/sso/signin", params={"entry":"miniblog","source":"miniblog","url":"https://weibo.com/"})
    c.headers["x-csrf-token"] = c.cookies.get("X-CSRF-TOKEN")
    
    r = c.get("/sso/v2/qrcode/image", params={"entry":"miniblog","size":"180"})
    d = r.json()
    qrid = d["data"]["qrid"]
    # 下载微博服务器生成的二维码图片（不是自己生成）
    img_url = d["data"]["image"]
    img_resp = httpx.get(img_url, timeout=15)
    Path("/opt/data/image_cache/weibo_qr_login.png").write_bytes(img_resp.content)
    
    print(f"QRID={qrid}", flush=True)
    print("QR_READY", flush=True)
    
    start = time.time()
    ok = False
    url, alt = None, None
    while time.time() - start < 240:
        time.sleep(2)
        try:
            r = c.get("/sso/v2/qrcode/check", params={
                "entry":"miniblog","source":"miniblog","url":"https://weibo.com/",
                "qrid":qrid,"rid":"","ver":"20250520"
            })
            cd = r.json()
            rc = cd.get("retcode")
            if rc == 20000000:
                url = cd.get("data",{}).get("url","")
                alt = cd.get("data",{}).get("alt","")
                print(f"LOGIN_OK url={bool(url)} alt={bool(alt)}", flush=True)
                ok = True
                break
        except:
            pass
    if not ok:
        print("TIMEOUT", flush=True); sys.exit(1)
    
    # 收集cookie
    cookies = dict(c.cookies)
    if url:
        try:
            with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": HEADERS["User-Agent"]}) as cc:
                cc.get(url)
                cookies.update(dict(cc.cookies))
        except: pass
    if alt:
        try:
            with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": HEADERS["User-Agent"]}) as ac:
                ac.get(f"https://login.sina.com.cn/sso/login.php?entry=miniblog&alt={alt}&returntype=TEXT")
                cookies.update(dict(ac.cookies))
        except: pass
    
    cred = {"cookies": cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(cred, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    print(f"COOKIES={len(cookies)} SUB={'SUB' in cookies}", flush=True)
    for k in sorted(cookies.keys()):
        print(f"  {k}: {cookies[k][:40]}", flush=True)
    
    r = requests.get("https://weibo.com/ajax/statuses/mymblog",
        params={"uid":"2014433131","page":"1","feature":"1"},
        cookies=cookies, headers=HEADERS, timeout=15)
    print(f"VERIFY={r.json().get('ok')}", flush=True)
