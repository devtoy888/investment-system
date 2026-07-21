---
name: weibo-monitor
description: Monitor Weibo (微博) users for posts and signals — install, authenticate, collect posts from followed bloggers via CLI. Integrates with cron-content-pipeline for automated signal detection.
category: social-media
---

# Weibo Monitor

Monitor specific Weibo users' posts for investment signals, market commentary, or content curation. Uses [weibo-cli](https://github.com/jackwener/weibo-cli) (`kabi-weibo-cli` on PyPI) as the backend.

## When to Activate

- User wants to collect posts from specific Weibo bloggers
- User needs to monitor Weibo for signals (investment tips, market views)
- User wants to integrate Weibo data into a daily briefing or cron pipeline
- Keywords: 微博, weibo, 博主, signal, monitoring, 唐史主任司马迁

## Prerequisites

```bash
uv tool install kabi-weibo-cli
```

## Authentication (Headless Server)

Weibo requires login. On a headless server (no browser), use QR code login:

```bash
weibo login --qrcode
```

**Problem:** The QR code renders as ASCII art in the terminal. On platforms like QQ/WeChat, ASCII QR codes are not scannable.

**Fix (2026-07-04 verified): Use `scripts/weibo_login_direct.py`** — this script **downloads the QR image directly from Weibo's server** (`passport.weibo.com/sso/v2/qrcode/image`), avoiding the QR ID truncation bug that caused rapid expiry in local-generation approaches:

```bash
cd /opt/data && python3 scripts/weibo_login_direct.py
# → downloads QR from Weibo server → /opt/data/image_cache/weibo_qr_login.png
# → polls for scan (2s interval, 4min timeout)
# → captures 6 cookies including SUB → saves to ~/.config/weibo-cli/credential.json
```

**Why local QR generation fails:** When generating the QR code locally with the `qrcode` library from the `scan_url` parameter, the QR ID printed to console is truncated to 20 characters (for display) while the actual QR ID is ~45 chars. The locally-generated QR image uses the truncated ID → server doesn't recognize it → QR expires within seconds.

**Key lesson for remote-platform login:** When the QR image must transit through a messaging platform (QQ delay, user's scanning delay), never use locally-generated QR codes. Always download the QR image from the server's `/sso/v2/qrcode/image` endpoint — the full QR ID is embedded server-side and survives the transit time.

```python
# Correct approach: download QR from Weibo server's image URL
import httpx
resp = client.get("/sso/v2/qrcode/image", params={"entry": "miniblog", "size": "180"})
data = resp.json()
qrid = data["data"]["qrid"]  # ~45 chars, full ID
img_url = data["data"]["image"]  # Weibo server's QR image URL
# Download it directly — don't re-encode locally
img_data = httpx.get(img_url, timeout=15)
Path("/tmp/weibo_qr.png").write_bytes(img_data.content)
```

### Verify Authentication

```bash
weibo status
# Expected: authenticated: true, cookie_count: 6+

# Test: fetch hot search (desktop API, no auth needed)
weibo hot --count 3
```

## Finding User IDs

Weibo uses numeric user IDs (UIDs). The `weibo search` command uses the mobile API which requires separate authentication — it often fails on headless servers.

**Best approach:** Ask the user for the UIDs directly. They can find them from the Weibo app: open the blogger's profile → tap "..." → copy link → the `/u/` number is the UID.

**Alternative (requires desktop auth):** Use the confirmed desktop API directly:

```python
import httpx, json
cred = json.loads(open(CREDENTIAL_FILE).read())
headers = {"User-Agent": "Mozilla/5.0 ...", "X-Requested-With": "XMLHttpRequest"}
# CRITICAL: feature=1 returns latest posts (feature=0 returns 6-month-old pinned posts)
r = httpx.get("https://weibo.com/ajax/statuses/mymblog",
    params={"uid": "2014433131", "page": "1", "feature": "1"},
    cookies=cred["cookies"], headers=headers)
# r.json()["data"]["list"] → posts
```

## CRITICAL: `feature` parameter

The `/ajax/statuses/mymblog` endpoint's `feature` parameter controls post freshness:

| value | behavior |
|-------|----------|
| `0` | Returns pinned/old posts — **useless for real-time monitoring** (returns posts from 6+ months ago) |
| `1` | Returns actual latest posts — **always use this** |
| `7` | Same as `0` |

**This is a critical bug.** `feature=0` returns 6-month-old "置顶帖" instead of today's market commentary. Always use `feature=1`.

```python
# CORRECT — returns fresh posts
params={"uid": uid, "page": "1", "feature": "1"}

# WRONG — returns 6-month-old pinned posts
params={"uid": uid, "page": "1", "feature": "0"}
```

## Collecting User Posts (Desktop API)

The desktop API (`weibo.com/ajax/statuses/mymblog`) works reliably with the QR-login credentials. Use direct Python calls rather than the CLI for automated scripts:

```python
def get_user_weibos(uid, page=1):
    cred = json.loads(open(CREDENTIAL_FILE).read())
    r = httpx.get("https://weibo.com/ajax/statuses/mymblog",
        params={"uid": uid, "page": str(page), "feature": "1"},  # ← MUST be 1, not 0
        cookies=cred["cookies"],
        headers={"User-Agent": "Mozilla/5.0 ...", "X-Requested-With": "XMLHttpRequest"})
    return r.json()["data"]["list"]

# Extract key info from each weibo:
# post["id"], post["text_raw"] (pure text, no HTML), post["created_at"], post["reposts_count"], post["comments_count"]

**Count parameter guidance:** For monitoring active KOLs, use `count=15` (not the default 3) to ensure coverage of yesterday's posts + today's real-time content. With `count=3`, an active blogger posting 5+ times today will have ALL slots taken by today's posts, completely missing yesterday's analysis. The API returns ~20 posts per page, so count=15 is well within the page boundary.
```

### Comment Analysis (Signal Posts Only)

For KOLs like 唐史主任司马迁, the comments section often contains useful signals (stock codes, sector mentions, author's replies to followers). Scrape comments only on signal-bearing posts to avoid rate limits:

```python
def get_weibo_comments(post_id: str, count: int = 20) -> list:
    """拉取指定博文的评论区。post_id=数字ID"""
    if not CREDENTIAL_FILE.exists():
        return []
    cred = json.loads(CREDENTIAL_FILE.read_text())
    headers = {"User-Agent": "...", "X-Requested-With": "XMLHttpRequest"}
    all_comments = []
    for page in range(1, 4):  # max 3 pages
        r = requests.get('https://weibo.com/aj/v6/comment/big',
            params={'ajwvr': 6, 'id': post_id, 'from': 'singleWeiBo', 'page': page},
            cookies=cred['cookies'], headers=headers, timeout=15)
        html = r.json().get('data', {}).get('html', '')
        if not html: break
        # Parse each comment block from HTML
        # Fields: user (str), text (str), has_zr_reply (bool), likes (int)
        time.sleep(0.3)
    # Deduplicate, return top `count` by likes
    return unique[:count]
```

Trigger: only scrape comments when `comments_count >= 30` AND post text contains signal keywords like `融资仓`, `加仓`, `右侧`, `建仓`, `触底`, `抄底`.

## Known Users (UIDs)

| 昵称 | UID | 粉丝 | 认证 |
|------|-----|------|------|
| 唐史主任司马迁 | 2014433131 | 4900万+ | 财经博主 |
| IT精英带你养基 | 5044466342 | 160万 | 财经博主,微博原创视频博主 | ⚠️ 已验证无信号价值,不采集 |
| 小浣熊1230 | 6114912545 | 4.5万 | 投资内容创作者,财经观察官 |

## Expanded Black Talk Dictionary (唐史主任司马迁-Specific)

Analysis of 227 posts (2024-05 to 2026-06) revealed unique industry-specific vocabulary:

| Term | Meaning | Context |
|------|---------|---------|
| **玻璃基** | Corning GlassBridge, AI数据中心光学互连技术 | 光通信/AI集群互连 |
| **长鑫** | 长鑫存储（CXMT）, 国产DRAM龙头 | 国产替代核心 |
| **伴娘** | 供应链配套厂商 | "长鑫伴娘"=长鑫的供应商 |
| **大fab / 小fab** | 大型/小型晶圆代工厂 | 产业链细分 |
| **硅基通胀** | AI算力推高芯片全链条价格 | 整体涨价逻辑 |
| **存** | 存储芯片（DRAM/HBM） | 出现16次，核心赛道 |
| **实调** | 实地调研、产业调研 | 信息来源标记 |
| **拥挤度** | 板块交易集中度高 | 回调预警信号 |
| **场外资金** | 增量机构资金入场 | 做多信号 |
| **宽基** | 宽基ETF（沪深300/中证500等） | 资金流向指标 |
| **季末漂移** | 基金季末调仓导致的板块异动 | 短期噪音 |
| **低位ETF** | 低位ETF品种，机构抄底 | 做多信号 |
| **功率** | 功率半导体（IGBT/SiC） | 科技细分赛道 |

Full black talk analysis: `kol_blacktalk_analysis.json` on R2 at `fund-system/data/`.

## Getting Following List

To analyze who a user follows:

```python
# Desktop API endpoint
url = "https://weibo.com/ajax/friendships/friends"
params = {"uid": TARGET_UID, "page": "1"}

# Returns per page (~20 users), paginate with &page=N
# Fields: screen_name, followers_count, friends_count, statuses_count, 
#         verified, description, verified_reason
# Endpoint maxes out at ~25 pages (~500 users) before returning empty
```

Scripts used: `/opt/data/scripts/kol_tang_following.py`, `/opt/data/scripts/kol_classify_following.py`, `/opt/data/scripts/kol_evaluate_candidates.py`

财经博主（尤其是唐史主任司马迁）常用暗语/黑话代指市场术语。采集帖子后做 AI 解读能大幅提升信号价值。

### 内置关键词规则（轻量版，适合预采集脚本）

```python
SIGNAL_MAP = {
    '村里': '政策层面/监管层',
    '上面': '高层/监管机构',
    '大家伙': '大资金/机构/国家队',
    '聪明钱': '北向资金/外资',
    '老乡': '散户投资者',
    '掌柜': '基金经理/操盘手',
    '开会': '政策会议/重要消息即将发布',
    '风向': '政策导向/市场趋势',
    '地板': '股价处于底部区域',
    '天花板': '股价到达顶部区域',
    '半山腰': '股价处于中间位置，可上可下',
    '吃肉': '有盈利空间/行情启动',
    '抬轿': '追高买入/给别人抬价格',
    '砸盘': '大资金卖出打压股价',
    '护盘': '资金托市/维稳',
    '出货': '主力卖出离场',
    '建仓': '主力开始买入',
    '洗盘': '主力震荡清洗散户筹码',
    '右侧': '趋势确认后的上涨阶段',
    '左侧': '趋势尚未确认的底部阶段',
    '确定性': '有明确逻辑支撑的投资机会',
    '弹性': '涨跌幅大的品种/高风险高收益',
    '高低切': '资金从高位板块流向低位板块',
    '高低切换': '板块轮动/风格转换',
}
```

### AI 深度解读（完整版，适合 cron agent）

在 cron agent prompt 中要求模型对微博原文做解读，效果比关键词规则好。完整词典见 `references/weibo-black-talk.md`。

```
对唐史主任司马迁的最新微博做解读：
- 他用了什么暗语/黑话？实际含义是什么？
- 他整体传递了什么市场观点？
- 这个观点对你的持仓有什么影响？
```

## Known credential location

```bash
# Credential file auto-saved at:
~/.config/weibo-cli/credential.json

# Verify:
weibo status  # → authenticated: true, cookie_count: 6+

# On credential expiry (~7 days), re-run QR login with:
python3 /opt/data/scripts/weibo_login_direct.py
# (Do NOT use `weibo login --qrcode` — local QR generation has QR ID truncation bug)

# After re-login, verify data collection works:
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from fund_tools import get_user_weibos
posts = get_user_weibos('2014433131', count=3)
print(f'{len(posts)} posts')
"

# Expected output after successful login:
#   QRID=3ZWNqSHIzABWSDOc3FDnZnM-3D6lLqJ8dBnFyY29kZQ..
#   QR_READY
#   LOGIN_OK url=True alt=True
#   COOKIES=6 SUB=True  ← critical: SUB must be True
#   VERIFY=1  ← API call returns ok=1
```

**Critical: Export cookie for cron scripts that read `/opt/data/weibo_cookies.json`:**
```bash
cp ~/.config/weibo-cli/credential.json /opt/data/weibo_cookies.json
echo '2014433131' > /opt/data/weibo_uid.txt
```

## Pitfalls

1. **`feature=1` is required** — `/ajax/statuses/mymblog` with `feature=0` returns 6-month-old pinned/置顶 posts. Always use `feature=1` for fresh content. This is the #1 cause of "old data" complaints.
2. **QR login cookie capture incomplete — need separate `data.url` + `data.alt` exchange** — The passport QR login (`passport.weibo.com`) only yields X-CSRF-TOKEN and basic passport cookies. The actual session cookies (SUB, SUBP, ALF, SCF) are set only after: (a) following `data.url` redirects through crossdomain URLs, AND (b) exchanging `data.alt` at `login.sina.com.cn/sso/login.php?entry=miniblog&alt={alt}&returntype=TEXT`. Use separate `httpx.Client()` instances for each exchange to capture their cookies separately, then merge all. Without this, the credential has only 1-2 passport cookies and `weibo status` shows `authenticated: false`. **Correct approach:** Run `scripts/weibo_login_direct.py` which handles both exchanges and captures 6 cookies (SUB, SUBP, SCF, ALF, ALC, X-CSRF-TOKEN).
3. **Mobile API needs separate auth** — `weibo search`, `weibo weibos`, `weibo profile` commands use `m.weibo.cn` which needs its own cookie. On headless servers, these commands often fail with `ok: -100`. **Fix:** Use desktop API endpoints directly (`weibo.com/ajax/statuses/mymblog`).
4. **Cookie expiration** — Credentials last ~7 days. Re-run QR login when `weibo status` shows `authenticated: false`.
5. **ASCII QR in terminal** — Never assume the user can scan ASCII QR codes from chat platforms. Always save a PNG image.
6. **Overseas network** — `passport.weibo.com` and `weibo.cn` may be slow or timeout from overseas servers. Desktop API (`weibo.com`) is more reliable.
7. **Famous ≠ valuable** — Follower count does not predict signal quality.
   Tested this hypothesis (2026-06): pulled 20 recent posts from 10 well-known financial KOLs (356K-640K followers) that 唐史主任 follows. 
   **Result:** Signal density ranged 0-10% for 9/10. Most have stopped posting substantive content or only share personal life. 
   **Meaning:** Do not assume popular KOLs produce actionable signals. Always measure: pull 20 posts, compute actual signal density, check posting recency. 
   The one exception (梦想家林奇, 30% density) had also stopped posting since Oct 2025. 
   **Conclusion:** 唐史主任 + 小浣熊 already provide the best available signal coverage on Weibo. Adding more from the following list yields diminishing returns.
8. **Comment API needs ALL 6 cookies, not just SUB** — The old AJAX endpoint `weibo.com/aj/v6/comment/big` is more authentication-strict than the new desktop API `weibo.com/ajax/statuses/mymblog`. If you manually curl with only SUB+SUBP cookies, it returns 404/network-busy. **Fix:** always use `requests` or `httpx` with the FULL cookie dict from `credential.json` (all 6: SUB, SUBP, SCF, ALF, ALC, X-CSRF-TOKEN). The `fund_tools.get_weibo_comments()` function handles this correctly.
7. **Following list API** — `weibo.com/ajax/friendships/friends?uid={UID}&page={N}` returns up to ~500 users (25 pages × 20). Works with QR-login cookies.
