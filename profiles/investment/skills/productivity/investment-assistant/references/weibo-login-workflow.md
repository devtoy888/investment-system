# Weibo Credential Re-Login Workflow

## Detection

The pre-collection scripts (`collect_morning_data.py`, `collect_noon_data.py`, `closing_review.py`) output:
```
❌ 微博凭据文件不存在
```
when `~/.config/weibo-cli/credential.json` is missing or expired. The sanity report shows:
```
✅ 📰 KOL: 2位, 0条博文
```
with no error but zero posts — means credential file exists but expired (silent failure).

To verify manually:
```python
from fund_tools import get_user_weibos
posts = get_user_weibos('2014433131', count=3)
# Empty list + no error = credential expired
```

## Automatic Detection (Watchdog)

A no_agent cron (`weibo_watchdog.py`, job ID `eca4c57f4737`) runs daily at **07:30 CST** (23:30 UTC):

- **Credentials valid** → silent exit (no output → no push)
- **Credentials expired** → generates QR code → pushes MEDIA: image to user with scan instructions

The script:
1. Checks `CREDENTIAL_FILE.exists()` and file age (>5 days = proactive refresh)
2. Calls `get_user_weibos('2014433131', count=1)` — empty = expired
3. If expired: launches `weibo_login_direct.py` as subprocess, waits for `QR_READY`
4. Outputs QR image path + scan instructions via MEDIA: protocol
5. The subprocess continues polling in background (up to 4 minutes)
6. User scans → subprocess catches `LOGIN_OK` → auto-saves credential

## Interactive Re-Login Steps

### 1. Run the login script in background

The script generates a QR code and polls for scan (up to 4 minutes). **Must run in background** — foreground timeout (15s) kills the polling loop before the user can scan.

```bash
cd /opt/data/scripts && python3 weibo_login_direct.py
```
Use `pty=true` + `timeout=320` in terminal tool, or `background=true` + `notify_on_complete=true`.

### 2. Send QR image to user

The script downloads Weibo's server-generated QR code to:
```
/opt/data/image_cache/weibo_qr_login.png
```

Wait for `QR_READY` output, then send the image to the user via MEDIA: protocol:
```
MEDIA:/opt/data/image_cache/weibo_qr_login.png
```

**Important:** Each script run generates a **new** QR code. The old QR image is overwritten. If the user needs to re-scan, run a fresh script instance.

### 3. Wait for scan completion

The background process polls `passport.weibo.com/sso/v2/qrcode/check` every 2s for up to 4 minutes.

Success output:
```
LOGIN_OK url=True alt=False
COOKIES=6 SUB=True
  SUB: _2A25...
  SUBP: 0033...
  SCF: AoWY...
  ALF: 02_...
  ALC: ALC-2...
  X-CSRF-TOKEN: CK-Y...
VERIFY=1
```

Key indicators:
- `LOGIN_OK url=True` → QR scan succeeded
- `COOKIES=6 SUB=True` → Got the critical SUB cookie
- `VERIFY=1` → Verification fetch succeeded (pulled posts from weibo.com/ajax/statuses/mymblog)

### 4. Verify credential works

```python
from fund_tools import get_user_weibos, CREDENTIAL_FILE

# Check file exists
print(f"Credential file: {CREDENTIAL_FILE.exists()}")
cred = json.loads(CREDENTIAL_FILE.read_text())
print(f"Cookies: {len(cred.get('cookies',{}))}, SUB: {'SUB' in cred.get('cookies',{})}")

# Test both KOLs
posts_a = get_user_weibos('2014433131', count=3)  # 唐史主任司马迁
posts_b = get_user_weibos('6114912545', count=3)  # 小浣熊1230
```

The API returns `text` field (not `text_raw`) in the response dict. The `get_user_weibos()` function has fallback: `p.get("text_raw", p.get("text", ""))` so it works.

### 5. Verify with a real pre-collection run

After confirmation, re-run `collect_morning_data.py` to verify the full pipeline picks up KOL data:
```bash
cd /opt/data/scripts && python3 collect_morning_data.py 2>&1
```
Check for: `📰 博主微博: 采集 唐史主任司马迁... ✅ N条`

## Credential File Details

- **Path:** `~/.config/weibo-cli/credential.json`
- **Format:** `{"cookies": {...}, "saved_at": <timestamp>}`
- **Permissions:** `chmod 600` (readable by owner only)
- **Expiry:** ~7 days (SUB cookie lifetime)

## Common Pitfalls

1. **First run times out** — The script takes ~4min waiting for scan. Always use background mode + notify_on_complete. Never use foreground with default 15s timeout.

2. **QR image stale** — If you sent the image but the background process was killed, you must generate a NEW QR code (run the script again). Old QR codes are invalidated.

3. **Script path dependency** — Line 4 of `weibo_login_direct.py` uses:
   ```python
   sys.path.insert(0, '/opt/data/home/.local/share/uv/tools/kabi-weibo-cli/lib/python3.13/site-packages')
   ```
   This path must match the actual weibo-cli install location. Verify it exists before running.

4. **Multiple login scripts exist** — `/opt/data/scripts/` has 9 variants (`weibo_login.py` through `weibo_login_v5.py`). Only `weibo_login_direct.py` is current and verified. Do NOT use the others. The watchdog (`weibo_watchdog.py`) automatically uses the correct one.

5. **No browser needed** — The script downloads Weibo's server-generated QR image directly. No Chromium/Chrome dependency. Works on headless servers.

6. **Cookie rotation** — Weibo may rotate SUB/SECRET cross-domain cookies during login. The script handles this by following `data.url` and `data.alt` redirects. If login succeeds but verification fails, the cross-domain cookies (SCF, SUB) may not have been captured — retry from scratch.
