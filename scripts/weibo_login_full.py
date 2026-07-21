#!/usr/bin/env python3
"""微博登录 - 直接从API获取完整scan URL生成二维码"""
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
    
    # 2. 取二维码 - 取完整信息
    r = c.get("/sso/v2/qrcode/image", params={"entry":"miniblog","size":"180"})
    qr_data = r.json()
    qrid = qr_data["data"]["qrid"]  # 完整QR ID
    img_url = qr_data["data"]["image"]  # 二维码图片URL
    # 从image URL的query参数中提取完整的scan URL
    scan_url = parse_qs(urlparse(img_url).query).get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]
    
    print(f"QRID完整长度={len(qrid)}", flush=True)
    print(f"SCAN_URL完整={scan_url}", flush=True)
    
    # 3. 生成二维码图片
    qrcode.make(scan_url).save("/opt/data/image_cache/weibo_qr_login.png")
    print("QR_CODE_READY", flush=True)
    
    # 4. 等待扫码
    start = time.time()
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
                print("SCANNED", flush=True)
            elif rc == 20000000:
                crossdomain_url = d.get("data",{}).get("crossdomain_url","")
                print("LOGIN_OK", flush=True)
                break
        except:
            pass
    else:
        print("TIMEOUT", flush=True); sys.exit(1)
    
    # 5. 捕获完整cookie
    cookies = dict(c.cookies)
    
    if crossdomain_url:
        for url in (u.strip() for u in crossdomain_url.split(",") if u.strip()):
            try:
                s = requests.Session()
                s.headers.update({"User-Agent": HEADERS["User-Agent"]})
                for k,v in cookies.items():
                    s.cookies.set(k,v)
                s.get(url, timeout=15)
                cookies.update(dict(s.cookies))
                s.close()
            except: pass
    
    try:
        s = requests.Session()
        s.headers.update({"User-Agent": HEADERS["User-Agent"], "Referer": "https://weibo.com/"})
        for k,v in cookies.items():
            s.cookies.set(k, v, domain=".weibo.com")
        r = s.get("https://weibo.com/", timeout=15)
        cookies.update(dict(s.cookies))
        for k,v in r.headers.items():
            if k.lower() == "set-cookie":
                for m in re.finditer(r'(SUB|SUBP|SCF|ALF|SUHB|SSOLoginState|XSRF)=([^;]+)', v):
                    cookies.setdefault(m.group(1), m.group(2))
        s.close()
    except: pass
    
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
    print(f"VERIFY={r.json().get('ok')}", flush=True)
