# Weibo Login Maintenance

## The Problem

Weibo API credentials expire ~7 days after login. `get_user_weibos()` returns `ok=-100` → "会话过期，需重新登录" → 0 posts returned.

## Root Cause

The QR login flow at `passport.weibo.com` sets only passport cookies (X-CSRF-TOKEN). The critical **SUB cookie** is set only after following cross-domain redirects AND visiting `weibo.com` with the passport session. The `weibo_login.py` script only saves passport cookies (1 cookie) — insufficient for the desktop API.

## The Fix: Use `weibo_login_direct.py` (2026-07-04 已验证)

**问题根源：** 之前 `weibo login --qrcode` 和手动编写脚本都因 QR ID 截断（仅显示前20字符）导致二维码过期时间极短。多次尝试后，最终**直接下载微博服务器生成的二维码图片**解决。

### 正确流程

```bash
# 无需手动构造二维码，直接运行：
cd /opt/data && python3 scripts/weibo_login_direct.py
```

脚本工作原理：
1. 请求 `passport.weibo.com/sso/v2/qrcode/image` → 拿到完整的 `qrid` + 微博服务器生成的二维码图片 URL
2. **直接下载**微博服务器上的二维码图片到 `/opt/data/image_cache/weibo_qr_login.png`
3. 输出 `QRID=xxx` + `QR_READY` → 此时用 `MEDIA:` 协议发送图片给用户
4. 轮询 `passport.weibo.com/sso/v2/qrcode/check`（2s间隔, 4min超时）
5. 登录成功 → 获取 `data.url` + `data.alt` → 走 cross-domain 交换获取 SUB cookie
6. 保存到 `~/.config/weibo-cli/credential.json`（6个cookie: SUB, SUBP, SCF, ALF, ALC, X-CSRF-TOKEN）
7. 验证：`requests.get("https://weibo.com/ajax/statuses/mymblog")` 返回 `ok=1`

### 关键区别（与传统CLI模式）

| 模式 | QR码来源 | 有效期 | 成功率 |
|------|---------|:-----:|:------:|
| `weibo login --qrcode` | 本地生成(截断QR ID) | 极短 | ❌ 频繁过期 |
| `scripts/weibo_login_v1~v5` | 本地生成或API field名错误 | 不定 | ❌ 缺SUB |
| **`weibo_login_direct.py`** | **微博服务器直接下载** | **正常4分钟** | **✅ 已验证** |

### 成功后同步

```bash
cp ~/.config/weibo-cli/credential.json /opt/data/weibo_cookies.json
echo '2014433131' > /opt/data/weibo_uid.txt
```

`fund_tools.py` 从 `~/.config/weibo-cli/credential.json` 读取凭据，同步后数据采集脚本立即可用。

```python
# Alternative: generate QR image via v1 QR generation, then user scans
python3 scripts/weibo_login.py  # user scans QR image
# BUT: v1 only saves passport cookie! After login, manually capture SUB
```

**Steps to do it properly (use `weibo login --qrcode` as the main flow):**
1. Run `weibo login --qrcode` with `pty=True` in background — it prints text-art QR and waits
2. Get the QR ID from process output (it's truncated to 20 chars for display, but the full QR is generated server-side)
3. BUT: DO NOT construct the QR URL yourself from the truncated QR ID — the image will be wrong
4. Instead, run `scripts/weibo_login_standalone.py` which uses the full qrid from the API to generate the PNG
5. Show the QR image to user with `MEDIA:/opt/data/image_cache/weibo_qr_login.png`
6. Wait for user to scan immediately (4 min timeout)
7. After scanning, verify with `get_user_weibos('2014433131', count=3)` — should return 3 posts

**Do NOT use these (all have QR API or cookie capture bugs):**
- `scripts/weibo_login.py` — v1, passport-only, saves 1 cookie, no SUB
- `scripts/weibo_login_v2.py` — v2, QR API returns non-JSON (missing Referer header from HEADERS)
- `scripts/weibo_login_v3.py` — v3, same QR issue + wrong field name
- `scripts/weibo_login_v4.py` — debug version only

**Key API details discovered from weibo CLI source code (`auth.py`):**
1. The check response field is `data.url` NOT `data.crossdomain_url` — my earlier scripts used the wrong field name
2. There is a SECOND mechanism: `data.alt` must be exchanged at `login.sina.com.cn/sso/login.php?entry=miniblog&alt={alt}&returntype=TEXT` to get the SUB cookie
3. The weibo CLI uses `httpx.Client` for both steps — a separate client for cross-domain redirects and another for alt exchange
4. The QR expire time is 4 minutes (constant `POLL_TIMEOUT_S = 240`)
5. Poll interval is 2 seconds (constant `POLL_INTERVAL_S = 2`)
6. After login, the CLI saves credentials via `save_credential(credential)` which writes to the same `~/.config/weibo-cli/credential.json` file that `fund_tools.py` reads

## Do NOT Use

- `scripts/weibo_login.py` — v1, passport-only, no SUB
- `scripts/weibo_login_v2.py` — v2, QR API returns non-JSON (missing Referer header)
- `scripts/weibo_login_v3.py` — v3, same QR issue
- `scripts/weibo_login_v4.py` — debug version only

## Cookie Structure (healthy state)

A working credential file has 5-7 cookies. Critical ones:

| Cookie | Purpose | How Set |
|--------|---------|---------|
| `SUB` | **Main auth token** (~200 chars, JWT-like) | After QR login + weibo.com visit |
| `SUBP` | Backup auth | Same as SUB |
| `SCF` | Session context | weibo.com visit |
| `X-CSRF-TOKEN` | Passport CSRF | Passport login step 1 |
| `ALF` | Auto-login flag | Cross-domain redirect |
| `SUHB` | Session heartbeat | Cross-domain redirect |

Minimal set for API: `SUB` alone authorizes `weibo.com/ajax/statuses/mymblog`.

## Verification

```python
from fund_tools import get_user_weibos
posts = get_user_weibos('2014433131', count=3)
print(f'{len(posts)} posts')  # Should be 3, not 0
```

If 0 posts with `ok=-100` → SUB cookie missing → re-login.

## ⚠️ Credential Backup Before Re-login

**CRITICAL: Before attempting any re-login, BACK UP the current credential file.** The login scripts (especially the broken ones like v1/v2/v3) OVERWRITE `~/.config/weibo-cli/credential.json` unconditionally. If the old credential was working (just aging), overwriting it means you lose a functional credential and end up with nothing.

```bash
cp ~/.config/weibo-cli/credential.json ~/.config/weibo-cli/credential.json.bak.$(date +%Y%m%d)
```

After login, verify:
```python
from fund_tools import get_user_weibos
posts = get_user_weibos('2014433131', count=3)
```
If 0 posts returned, restore the backup:
```bash
cp ~/.config/weibo-cli/credential.json.bak.* ~/.config/weibo-cli/credential.json
```

## Expected Warning in no_agent Cron Jobs After Expiry

When the weibo credential is expired, `get_user_weibos()` prints `⚠️ UID=xxx: 会话过期` to stdout. This warning appears differently depending on cron mode:

- **no_agent=True** (周末外盘速报, auto_validate_sources): The warning goes into stdout, which IS the delivered message. The user sees "⚠️ UID=2014433131: 会话过期，需重新登录" in the push.
- **LLM-agent mode** (财经早报, 收盘复盘): The warning goes into "Script Output" context. The LLM can read it but the formatted push only shows "（无最新微博或获取失败）" — no raw warning in the user-facing message.

This is by design — no_agent jobs deliver raw script output, so library function warnings are visible. If the warning is disruptive, redirect to stderr in the library function, or add post-processing to the no_agent script.

## Full Login Flow (for debugging)

1. GET passport.weibo.com/sso/signin → X-CSRF-TOKEN cookie set
2. GET passport.weibo.com/sso/v2/qrcode/image → QR image + qrid
3. User scans QR with Weibo app
4. Poll passport.weibo.com/sso/v2/qrcode/check → retcode=20000000 (success) + crossdomain_url
5. Follow crossdomain URLs (login.sina.com.cn etc.) → SUB cookie set
6. GET weibo.com/ → SCF + additional cookies set
7. Save all cookies → credentials.json
