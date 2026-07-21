# Weibo QR Login for Headless Servers

## Problem

`weibo login --qrcode` generates a terminal ASCII QR code that can't be scanned when running on a headless Docker server. We need to send the QR as an image to the user.

## Implementation

The QR login flow is reverse-engineered from `passport.weibo.com` (see weibo-cli's `auth.py`):

1. GET passport.weibo.com/sso/signin → get `X-CSRF-TOKEN` cookie
2. GET /sso/v2/qrcode/image (with CSRF token + `size=180`) → get `qrid` + `image` URL
3. Extract `scan_url` from `image` URL's `data` query param
4. Generate QR PNG image from `scan_url` → send to user via MEDIA:
5. Poll /sso/v2/qrcode/check every 2s for up to 4 minutes

## Simpler Approach: Monkey-patch weibo-cli's own login

Instead of implementing the full flow from scratch, monkey-patch weibo-cli's `_display_qr_in_terminal` to also save a PNG. This uses weibo-cli's own tested code for CSRF, polling, and credential capture.

```python
import sys, qrcode
from PIL import Image
sys.path.insert(0, '~/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')
import weibo_cli.auth as auth

_original = auth._display_qr_in_terminal
def _patched(data):
    qrcode.make(data).save('/opt/data/image_cache/weibo_qr_login.png')
    print('MEDIA:/opt/data/image_cache/weibo_qr_login.png', flush=True)
    return _original(data)
auth._display_qr_in_terminal = _patched

cred = auth.qr_login()  # handles everything: CSRF, QR, poll, credential save
```

**Run with:** `PYTHONUNBUFFERED=1 python3 script.py`

A reusable script exists at `scripts/weibo_qr_login.py` in this skill.

## Credential Capture Note

Custom implementations often miss the SUB cookie. The weibo-cli's own `qr_login()` handles cross-domain redirect properly. Without SUB, `weibo status` says "authenticated" but all commands fail.

```python
from urllib.parse import parse_qs, urlparse
import httpx
import qrcode
from PIL import Image

PASSPORT_URL = "https://passport.weibo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": f"{PASSPORT_URL}/sso/signin?entry=miniblog&source=miniblog&url=https://weibo.com/",
    "x-requested-with": "XMLHttpRequest",
}

with httpx.Client(base_url=PASSPORT_URL, headers=dict(HEADERS),
                  follow_redirects=True, timeout=httpx.Timeout(30)) as client:
    # Step 1: Get CSRF token
    resp = client.get("/sso/signin", params={
        "entry": "miniblog", "source": "miniblog", "url": "https://weibo.com/"
    })
    resp.raise_for_status()
    csrf_token = client.cookies.get("X-CSRF-TOKEN")
    client.headers["x-csrf-token"] = csrf_token

    # Step 2: Get QR code
    resp = client.get("/sso/v2/qrcode/image", params={"entry": "miniblog", "size": "180"})
    resp.raise_for_status()
    qr_data = resp.json()
    qrid = qr_data["data"]["qrid"]
    image_url = qr_data["data"]["image"]

    # Step 3: Extract scan URL from image URL
    parsed = urlparse(image_url)
    qs = parse_qs(parsed.query)
    scan_url = qs.get("data", [f"https://passport.weibo.cn/signin/qrcode/scan?qr={qrid}"])[0]

    # Step 4: Generate QR PNG image
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(scan_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("/opt/data/image_cache/weibo_qr_login.png")

    # Send to user
    print("MEDIA:/opt/data/image_cache/weibo_qr_login.png")

    # Step 5: Poll for scan status
    import time
    start = time.time()
    while time.time() - start < 240:
        resp = client.get("/sso/v2/qrcode/check", params={
            "entry": "miniblog", "source": "miniblog",
            "url": "https://weibo.com/", "qrid": qrid,
            "rid": "", "ver": "20250520",
        })
        check = resp.json()
        retcode = check.get("retcode")
        if retcode == 20000000:  # Success
            print("✅ 扫码成功!")
            # Follow crossdomain URL to get session
            break
        elif retcode == 50114001:  # Not scanned
            pass
        elif retcode == 50114002:  # Scanned but not confirmed
            print("📱 已扫码，请在手机上确认登录...")
        time.sleep(2)
```

## Dependencies

```bash
pip install httpx qrcode[pil] Pillow
# or
uv pip install httpx qrcode[pil] Pillow
```

## Troubleshooting

- **size error (retcode 50114017):** Missing `size=180` parameter in the QR image URL request.
- **No CSRF token:** The `/sso/signin` call may need different params. Try with `entry=miniblog` and `source=miniblog`.
- **Only 1 cookie saved:** Custom login scripts often only capture X-CSRF-TOKEN without the real session cookie (SUB). Use the monkey-patch approach (`scripts/weibo_qr_login.py`) which runs weibo-cli's own code that properly follows crossdomain redirects.
- **Search returns ok: -100:** Mobile API needs different session. Try `weibo profile <uid>` or `weibo weibos <uid>` instead of `weibo search`.
- **Background process produces no output:** Use `PYTHONUNBUFFERED=1` and add `flush=True` to print() calls.
- **Network from overseas:** Weibo passport.weibo.com works globally, but weibo.cn API may be blocked.
- **Credential TTL:** Saved credential expires after 7 days. After expiry, weibo-cli will warn but may still work temporarily.
