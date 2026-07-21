#!/usr/bin/env python3
"""微博移动端登录 - 生成二维码 (entry=wapsso)，用于拉取全量评论"""
import sys, json, time
sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')

from urllib.parse import parse_qs, urlparse
import httpx, requests, re
from pathlib import Path

PASSPORT_URL = "https://passport.weibo.com"
CONFIG_DIR = Path.home() / ".config" / "weibo-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "x-requested-with": "XMLHttpRequest",
    "Referer": f"{PASSPORT_URL}/sso/signin?entry=wapsso&source=wapssowb&url=https://m.weibo.cn/",
}

with httpx.Client(base_url=PASSPORT_URL, headers=dict(HEADERS), follow_redirects=True, timeout=30) as c:
    c.get("/sso/signin", params={"entry":"wapsso","source":"wapssowb","url":"https://m.weibo.cn/"})
    c.headers["x-csrf-token"] = c.cookies.get("X-CSRF-TOKEN")

    r = c.get("/sso/v2/qrcode/image", params={"entry":"wapsso","size":"180"})
    d = r.json()
    qrid = d["data"]["qrid"]
    img_url = d["data"]["image"]
    img_resp = httpx.get(img_url, timeout=15)
    Path("/opt/data/image_cache/weibo_qr_mobile.png").write_bytes(img_resp.content)

    print(f"QRID={qrid}", flush=True)
    print("QR_READY", flush=True)

    start = time.time()
    ok = False
    url, alt = None, None
    while time.time() - start < 240:
        time.sleep(2)
        try:
            r = c.get("/sso/v2/qrcode/check", params={
                "entry":"wapsso","source":"wapssowb","url":"https://m.weibo.cn/",
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

    cookies = dict(c.cookies)
    if url:
        try:
            with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": HEADERS["User-Agent"]}) as cc:
                cc.get(url)
                cookies.update(dict(cc.cookies))
        except: pass
    # wapsso的url里带alt参数，解析出来补全移动端cookie
    if url and 'alt=' in url:
        try:
            from urllib.parse import urlparse, parse_qs
            alt_val = parse_qs(urlparse(url).query).get('alt', [None])[0]
            if alt_val:
                with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": HEADERS["User-Agent"]}) as ac:
                    ac.get(f"https://login.sina.com.cn/sso/login.php?entry=wapsso&alt={alt_val}&returntype=TEXT")
                    cookies.update(dict(ac.cookies))
        except: pass
    if alt and not (url and 'alt=' in url):
        try:
            with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": HEADERS["User-Agent"]}) as ac:
                ac.get(f"https://login.sina.com.cn/sso/login.php?entry=wapsso&alt={alt}&returntype=TEXT")
                cookies.update(dict(ac.cookies))
        except: pass

    cred = {"cookies": cookies, "saved_at": time.time(), "entry": "wapsso"}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(cred, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    print(f"COOKIES={len(cookies)} SUB={'SUB' in cookies}", flush=True)

    # 验证移动端登录
    r = requests.get("https://m.weibo.cn/api/config", cookies=cookies, headers=HEADERS, timeout=15)
    try:
        login = r.json().get("data",{}).get("login", False)
        print(f"MOBILE_LOGIN={login}", flush=True)
    except:
        print("MOBILE_LOGIN=verify_failed", flush=True)
