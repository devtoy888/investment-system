#!/usr/bin/env python3
"""微博登录v5 - 修复：url字段 + alt交换获取SUB"""
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
    qr_data = r.json()
    qrid = qr_data["data"]["qrid"]
    scan_url = parse_qs(urlparse(qr_data["data"]["image"]).query)["data"][0]
    qrcode.make(scan_url).save("/opt/data/image_cache/weibo_qr_login.png")
    print("QR_CODE_READY", flush=True)
    
    # 3. 等待扫码
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
            d = r.json()
            rc = d.get("retcode")
            if rc == 50114002:
                pass
            elif rc == 20000000:
                url = d.get("data", {}).get("url", "")
                alt = d.get("data", {}).get("alt", "")
                print("LOGIN_OK", flush=True)
                ok = True
                break
        except:
            pass
    
    if not ok:
        print("TIMEOUT", flush=True); sys.exit(1)
    
    # 4. 捕获cookie（完全对齐weibo CLI的方式）
    cookies = dict(c.cookies)
    
    # 4a. 跟随cross_url
    if url:
        try:
            with httpx.Client(follow_redirects=True, timeout=30,
                              headers={"User-Agent": HEADERS["User-Agent"]}) as cc:
                cr = cc.get(url)
                for k, v in cr.cookies.items():
                    cookies[k] = v
                for k, v in cc.cookies.items():
                    cookies[k] = v
        except:
            pass
    
    # 4b. alt交换 - 这是获取SUB的关键！
    if alt:
        try:
            alt_url = f"https://login.sina.com.cn/sso/login.php?entry=miniblog&alt={alt}&returntype=TEXT"
            with httpx.Client(follow_redirects=True, timeout=30,
                              headers={"User-Agent": HEADERS["User-Agent"]}) as ac:
                ar = ac.get(alt_url)
                for k, v in ar.cookies.items():
                    cookies[k] = v
                for k, v in ac.cookies.items():
                    cookies[k] = v
        except:
            pass
    
    # 保存
    cred = {"cookies": cookies, "saved_at": time.time()}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIAL_FILE.write_text(json.dumps(cred, indent=2))
    CREDENTIAL_FILE.chmod(0o600)
    
    print(f"COOKIES={len(cookies)} SUB={'SUB' in cookies}", flush=True)
    for k in sorted(cookies.keys()):
        v = cookies[k]
        print(f"  {k}: {v[:40]}...", flush=True)
    
    # 验证
    r = requests.get("https://weibo.com/ajax/statuses/mymblog",
        params={"uid":"2014433131","page":"1","feature":"1"},
        cookies=cookies, headers=HEADERS, timeout=15)
    print(f"VERIFY={r.json().get('ok')}", flush=True)
