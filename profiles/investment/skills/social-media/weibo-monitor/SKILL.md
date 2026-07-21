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

## 🔴 长文本获取（2026-07-18新增）

Weibo有两种内容格式：短文本（`text_raw`，约140-200字预览）和长文本（`isLongText=True` 时通过长文本API获取完整内容）。

**必须始终检查 `isLongText` 字段并调用长文本API，否则丢失90%+的实质性内容。**

```python
def get_user_weibos(uid, count=15):
    # ... 初始请求 ...
    for p in posts[:count]:
        text = p.get("text_raw", p.get("text", ""))
        text = re.sub(r'<[^>]+>', '', text).strip()
        
        # ★ 长文本检测（不检测=内容丢失）
        if p.get("isLongText"):
            try:
                lt_url = f"https://weibo.com/ajax/statuses/longtext?id={p.get('id','')}"
                lt_r = requests.get(lt_url, cookies=cred['cookies'], headers=headers, timeout=8)
                lt_data = lt_r.json()
                if lt_data.get("ok") == 1:
                    full_text = lt_data.get("data", {}).get("longTextContent", "")
                    if full_text:
                        text = re.sub(r'<[^>]+>', '', full_text).strip()
            except Exception as e:
                print(f"长文本拉取失败: {e}")
        
        # 放宽截断限制（旧代码text[:500]丢失内容）
        text = text[:2000]
        results.append({
            'id': p.get('id', ''),
            'text': text,
            'is_longtext': p.get('isLongText', False),
            # ... 其他字段
        })
```

**已验证（2026-07-18）**：唐史主任司马迁 15条中有10条长文本(最长570字)，小浣熊1230 15条中有4条长文本(最长689字)。旧代码`text[:500]`截断了这些内容。

## KOL 信号分析框架 v2（2026-07-19更新）

旧版分析仅用关键词匹配（SIGNAL_TRIGGERS/SECTOR_KEYWORDS/DIRECTION_BULLISH），无理论框架、无验证闭环。`kol_analysis.py` v2 提供 **4层架构 + 事实核查 + 赛道→基金映射**：

```
Extractor (提取层)     → 结构化断言{sector, direction, timeframe, claim, confidence}
                       区分 today/soon/long 三个时间窗口，仅today+soon出操作
     ↓
Verifier (验证层)      → 对比腾讯行情数据，标定正确/错误
                       赛道→行情key映射（科技/AI→科创50/半导体）
     ↓
Mapper (操作层)        → 赛道→基金映射（011613/017103/163302…）
                       → 可执行操作{方向, 基金代码, 仓位建议%}
     ↓
format_push (格式化)   → QQ Bot Markdown表格 → 操作建议+信号摘要+统计
```

理论基础：
- 行为金融学：锚定效应、确认偏误（对比多源观点）
- 信号处理：信噪比（区分信息与噪音）、趋势确认
- 博弈论：共识强度（群体智慧加权）、逆向思维

**集成方式（collect_morning_data.py 已自动使用）：**

```python
from kol_analysis import analyze_from_kol_data, format_push

# 完整分析（传入KOL数据+腾讯行情）
analysis = analyze_from_kol_data(kol_data, quotes)

# 格式化推送
push_text = format_push(analysis)  # 含操作建议表格
```

**与v1的关键区别：**

| 维度 | v1 (已移除) | v2 (当前) |
|:-----|:-----------|:----------|
| 类名 | SignalExtractor/ClaimVerifier/KOLScorer/ActionMapper | **Extractor/Verifier/Mapper** |
| 入口函数 | `analyze_kol_posts(kol_data, market_data)` | **`analyze_from_kol_data(kol_data, quotes)`** |
| 格式化 | `format_analysis_for_push(analysis)` | **`format_push(analysis)`** |
| 事实核查 | `market_data.get("科技/AI")` 永远None | 赛道→行情key映射，匹配真实数据 |
| 操作建议 | "看多科技/AI"(无法执行) | **"减仓科技/AI → 011613(5%)"** |
| 时效分筛 | 无 | **today/soon/long** 仅today+soon出操作 |
| 赛道→基金 | 无 | 6个赛道×12支基金映射 |

**文件位置**：`/opt/data/scripts/kol_analysis.py` (14KB, ~350行)
**验证（2026-07-19）**：最终全量 35/35 通过。真实数据测试：29/33信号已核查市场数据，4条操作建议全部带基金映射。

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

## ⚠️ 评论接口坑（2026-07实测）

拉评论区时，**不要**用以下两个接口，均失败（实测）：

1. `weibo.com/ajax/statuses/buildComments` → 返回 `{"ok":0,"message":"参数错误"}`（HTTP 400），无论 `flow`/`st`/`page` 怎么组合。
2. `weibo.com/comments/hotflow` → HTTP 200 但返回 **HTML 登录页**（`Content-Type: text/html`），不是 JSON，cookie 未生效。

**正确做法：直接用 `fund_tools.get_weibo_comments(post_id, count=20)`。** 它内部走 `weibo.com/aj/v6/comment/big`（`ajwvr=6`, `from=singleWeiBo`），用 `credential.json` 的**全部6个cookie**（SUB/SUBP/SCF/ALF/ALC/X-CSRF-TOKEN）。手动只带 SUB+SUBP 调 buildComments 会 404/network-busy。

**评论数限制（重要）：** 该接口限流，单条微博原评数95/321条时实测只返回 3+7 条样本。这是**样本不是全量**，分析时只能说"评论区样本显示…"，不能声称穷尽。传参用 `post['id']`（数字ID，非 mblogid）。

**根因与全量方案见 `references/weibo-comment-limits.md`：** 经实测这不是请求太快（重试+退避+翻页后第2页仍稳定空），而是**网页端 cookie 的评论读取权限被限制在热门评论前几条**；全量在 `m.weibo.cn/comments/hotflow`（移动端接口），但移动端需**单独登录态**（网页cookie不能跨端复用，实测 `m.weibo.cn/api/config` 返回 `login:false`）。要拉全量必须先登录移动端拿 m.weibo.cn cookie。否则只能接受样本限制并在分析中明确标注。

**当日微博拉取：** 用 `mymblog` 遍历 page=1..3，按 `created_at` 解析 `datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')` 过滤当日。feature 必须用 `1`（见前文 CRITICAL 段）。


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

## ⚠️ 开放提取铁律（用户纠正：白名单会漏掉真实赛道）

**绝不能用预设关键词白名单做赛道统计。** 2026-07 分析唐史主任微博时，用白名单（半导体/AI/医药/机器人/航天）过滤，完全漏掉了 **玻璃基板**（实际 19 次提及，是第三高频赛道，主任明确点名"6-7月认知差机会"）。白名单天然遮蔽了不在列表里的真实主题。

**正确做法——开放词库 + 全量扫描：**
1. 先用一个**宽覆盖候选词库**（科技/半导体/玻璃基板/机器人/航天/医药/新能源/军工/消费/红利/资源/金融/地产/汽车/框架词如扩产/流动性/高波/业绩/IPO 等）全量 `text.count()` 统计频次，输出所有 >0 的词。
2. 再对**公司名/标的**（长鑫、美光、康宁、寒武纪…）和**框架词**（扩产、流动性、高波、硅基通胀、云厂…）单独提取——这些比行业桶更能指导配置。
3. 任何"未提及X"的结论都必须基于全量扫描，不能用"白名单里没有"反推。

**玻璃基板实证（141条去重，实时API）：** 主任 6/3、6/17、6/25、7/3 四次讲玻璃基封装载板/玻璃光学桥，明确"全市场集体定价"。A股无独立玻璃基板ETF，对应标的是半导体材料设备主题ETF（如已持有的 024418，今年+101%涨最好），玻璃基板不是新增独立标的而是强化该线逻辑。

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

## ⚠️ 凭证路径二重性（两套文件，互不同步）

**fund_tools.py 与 weibo-cli 命令行写入的是两个不同文件！** 这是最常踩的坑：

| 用途 | 路径 | 更新方式 |
|:----|:-----|:---------|
| **fund_tools.py 读取** | `profiles/investment/home/.config/weibo-cli/credential.json` | 手动复制 |
| **weibo-cli 命令行写入** | `home/.config/weibo-cli/credential.json` | `weibo login --qrcode` |

根因：`fund_tools.py` 用绝对路径写死了 investment profile 的 home 目录，而 `weibo-cli` 二进制写入的是进程 `HOME` 环境变量指向的目录。当 hermes profile 有独立 home 目录时，两者指向不同路径。

**登录后必须手动同步：**
```bash
cp $HOME/.config/weibo-cli/credential.json /opt/data/profiles/investment/home/.config/weibo-cli/credential.json
cp /opt/data/profiles/investment/home/.config/weibo-cli/credential.json /opt/data/weibo_cookies.json
echo '2014433131' > /opt/data/weibo_uid.txt
```

**看门狗`weibo_watchdog.py`的凭证检测逻辑（2026-07-20修复）：**

旧逻辑先看文件年龄>5天→直接判过期，**不调API验证**→误判。修复后逻辑：
1. ❶ 先调真实API验证（不看文件年龄）
2. ❷ API通过后，检查年龄作为预警（12天阈值，不阻塞）

```python
def check_credentials() -> bool:
    if not CREDENTIAL_FILE.exists(): return False
    posts = get_user_weibos('2014433131', count=1)   # ❶ 真实API验证
    if not posts: return False
    age = time.time() - CREDENTIAL_FILE.stat().st_mtime
    if age > 12 * 86400:                              # ❷ 年龄预警（不阻塞）
        print(f"⚠️ 凭证已 {age/86400:.0f} 天，建议扫码续期")
    return True
```

### 修复后验证：全量多轮测试模式（用户要求，2026-07-20）

该用户对任何修复都要求**全量多轮测试**，不能只改完就完事。凭证/看门狗相关修复必须通过以下5轮验证：

| 轮次 | 测试内容 | 验收标准 |
|:----|:---------|:---------|
| **第1轮** 凭证有效性 | `get_user_weibos()` 多用户拉取 + 双路径MD5一致 | API返回ok=1且有内容 |
| **第2轮** 看门狗行为 | 有效凭证→静默退出(exit 0,空stdout)；过期凭证→QR生成(exit 1,含提示) | 正反场景都必须验证 |
| **第3轮** 集成依赖 | 所有依赖`get_user_weibos`的脚本 语法验证+关键函数存在性 | 无语法错误，无静默Bug |
| **第4轮** cron模拟 | cron裸环境(HOME+PATH)运行看门狗 + 双文件一致性 | cron环境不应比交互环境多出错 |
| **第5轮** 边界情况 | 凭证不存在、JSON格式损坏、网络断开 | 脚本不崩溃，优雅降级 |

**2026-07-20实测算例**（凭证双路径修复后）：第1轮发现小浣熊/it精英为空→追踪到`mymblog` API限制；第2轮有效凭证静默退出、过期凭证生成QR通过；第4轮发现纯PATH环境exit 1→定位到HOME依赖→补充HOME后全pass。仅做第1轮是不够的。

### Known credential location（完整路径）

```bash
# fund_tools.py 使用的凭证文件：
/opt/data/profiles/investment/home/.config/weibo-cli/credential.json

# weibo-cli 命令行写入的凭证文件：
$HOME/.config/weibo-cli/credential.json

# Verify:
weibo status  # → authenticated: true, cookie_count: 6+

# On credential expiry (~14-30 days), re-run QR login with:
python3 /opt/data/scripts/weibo_login_direct.py
# (Do NOT use `weibo login --qrcode` — local QR generation has QR ID truncation bug)

# After re-login, verify data collection works:
cd /opt/data && python3 -c "
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

## Pitfalls

9. **`mymblog` API 只返回登录账号自己的微博（2026-07-20实测）** — `/ajax/statuses/mymblog?uid=X` 不管你传什么uid，都只返回**当前登录账号自己发的微博**。如果登录的是「唐史主任司马迁」(2014433131)，传 uid=6274837321(小浣熊) 会返回 `ok=1` 但 **空列表**。这不是凭证问题，是端点本身的限制。**要拉关注博主的微博需用其他端点，但目前微博API没有稳定可用的`home feed`端点。** 实测：`/ajax/feed/hottimeline` 和 `/ajax/statuses/user_timeline` 均返回 `ok=0`。当前系统能力下，`get_user_weibos` 只能拉登录账号自己（即主任）的微博，拉不到小浣熊/it精英。如需拉其他人的，需等微博API恢复或换登录工具。
10. **`feature=1` is required** — `/ajax/statuses/mymblog` with `feature=0` returns 6-month-old pinned/置顶 posts. Always use `feature=1` for fresh content. This is the #1 cause of "old data" complaints.
2. **QR login cookie capture incomplete — need separate `data.url` + `data.alt` exchange** — The passport QR login (`passport.weibo.com`) only yields X-CSRF-TOKEN and basic passport cookies. The actual session cookies (SUB, SUBP, ALF, SCF) are set only after: (a) following `data.url` redirects through crossdomain URLs, AND (b) exchanging `data.alt` at `login.sina.com.cn/sso/login.php?entry=miniblog&alt={alt}&returntype=TEXT`. Use separate `httpx.Client()` instances for each exchange to capture their cookies separately, then merge all. Without this, the credential has only 1-2 passport cookies and `weibo status` shows `authenticated: false`. **Correct approach:** Run `scripts/weibo_login_direct.py` which handles both exchanges and captures 6 cookies (SUB, SUBP, SCF, ALF, ALC, X-CSRF-TOKEN).
3. **Mobile API needs separate auth** — `weibo search`, `weibo weibos`, `weibo profile` commands use `m.weibo.cn` which needs its own cookie. On headless servers, these commands often fail with `ok: -100`. **Fix:** Use desktop API endpoints directly (`weibo.com/ajax/statuses/mymblog`).
4. **Credential dual-path divergence** — `fund_tools.py` reads `/opt/data/profiles/investment/home/.config/weibo-cli/credential.json` (investment profile path), but `weibo login --qrcode` writes to `$HOME/.config/weibo-cli/credential.json` (default HOME). After re-login, always copy the credential both ways:
   ```bash
   cp $HOME/.config/weibo-cli/credential.json /opt/data/profiles/investment/home/.config/weibo-cli/credential.json
   ```
   Also copy to `/opt/data/weibo_cookies.json` for the backup. Without this, cron scripts silently use the stale credential while the CLI works fine — the root cause of "CLI works but watchdog says expired". **Fix: always sync both paths after any re-login.**
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
8. **⛔ wapsso 移动端登录无法解锁全量评论（2026-07-16 实测，浪费两次扫码）**：为拉全量评论改用 `entry=wapsso` 重新扫码登录，登录流程检测 `LOGIN_OK` 成功，但 `m.weibo.cn/api/config` 始终返回 `login:false`，且 `m.weibo.cn/comments/hotflow` 仍返回"新浪通行证"登录页。根因：微博网页端(miniblog)与移动端(wapsso)是**完全隔离的登录体系**，wapsso 扫码拿到的 SUB/SUBP/SCF/ALF/ALC 是网页端 cookie，不含移动端专用 `M_WEIBO_*` cookie；且 wapsso 返回 `url` 里也无 `alt` 参数可补全（脚本已尝试从 url 解析 alt 调 `login.sina.com.cn/sso/login.php?entry=wapsso` 仍无效）。**结论：当前 `kabi-weibo-cli` 工具能力下，无法拉全 416 条评论，只能拿到热门样本（实测 7+3 条）。不要再为用户"拉全量评论"而重复扫码移动端登录——直接接受样本限制并在分析中标注"评论区样本N条(原M条)，非全量"。若要真全量，需替换登录工具或手动导出。**
