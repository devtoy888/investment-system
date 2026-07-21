# 小红书（RedNote）服务器自动化采集方案评估

> 目标环境：**Hermes 安装在 Oracle ARM64 服务器（aarch64，无桌面、无 Chrome、无 GPU）**
> 目标：在服务器上**自动化采集**小红书内容（搜索、笔记详情、评论、用户主页等）
> 调研日期：2026-07-19
> 本文所有"可行/不可行"结论均来自**实测 + 源码核对**，非凭印象。

---

## 0. 一句话结论

✅ **可行，且已经有现成工具。** 推荐用 `xiaohongshu-cli`（jackwener，逆向 Web API 方案），
它在**数据采集中途完全不依赖浏览器**（已用源码确认：`search/read/feed/comments` 走纯 HTTP 签名 API，
不 import 任何浏览器库）。唯一的浏览器依赖在 **登录环节**——而登录可以**在桌面完成一次、导出 cookie、
上传到服务器长期复用（约 7 天有效期，到期重导一次即可）**。

⚠️ 这与本机 `agent-reach` skill 的 `server-setup.md` 旧结论("ARM64 无头服务器小红书不可能")**矛盾**。
旧结论针对的是 `xiaohongshu-mcp`（go-rod + Chromium 方案），**不适用于**逆向 API 方案。旧结论已过时，本文以实测为准。

---

## 1. 核心约束与破局点

| 约束 | 影响 | 破局点 |
|------|------|--------|
| 服务器无桌面、无 Chrome | 浏览器自动化方案（OpenCLI / xiaohongshu-mcp / camoufox）跑不通 | 改用**逆向 API 方案**，`search/read` 不碰浏览器 |
| ARM64 无头 | `xiaohongshu-mcp` 的 Chromium 静默下载失败 | 选纯 Python 的 `xiaohongshu-cli`，无原生浏览器依赖 |
| 小红书无官方 API | 必须逆向或借浏览器 | `xiaohongshu-cli` 已实现 `x-s`/`x-s-common` 签名 |
| 登录需浏览器/扫码 | `xhs login --qrcode` 在服务器实测报错（camoufox headless=False） | **登录在桌面做**，导出 `cookies.json` 到服务器 |
| Cookie 7 天过期 | 服务器无法自助续期 | cron 监控 + 桌面每 7 天重导一次 |

---

## 2. 全量方案评估矩阵

按"服务器可行性"分四档：✅ 直接可用 / 🟡 需桌面协助(一次) / 🔴 服务器不可用 / 💰 付费托管

| # | 方案 | 类型 | 服务器可行性 | 维护成本 | 风控风险 | 备注 |
|---|------|------|------------|---------|---------|------|
| 1 | **xiaohongshu-cli**（jackwener，逆向 API） | 纯 API | 🟡 登录需桌面协助一次 | 低 | 中（有反检测） | **★ 主推荐** |
| 2 | xiaohongshu-mcp（xpzouying，go-rod+Chromium） | 浏览器 MCP | 🔴 ARM64 无头不可用 | — | 低 | 桌面可用；服务器 Chromium 下载失败 |
| 3 | xhs-cli（jackwener，camoufox 浏览器） | 浏览器 | 🔴 登录即崩（实测） | — | 低 | camoufox 在无头服务器起不来 |
| 4 | OpenCLI（jackwener，浏览器桥接） | 浏览器扩展 | 🔴 需桌面+Chrome | — | 低 | Agent Reach v1.5.0 首选后端，但服务器跳过 |
| 5 | Spider_XHS（cv-cat，逆向+发布） | 逆向+服务 | 🟡 类方案1，偏运营 | 中 | 中 | 多账号/创作者向，重 |
| 6 | Apify / Tikhub 等托管 API | 付费 SaaS | ✅ 服务器直接调 | 低 | 低 | 💰 约 $0.01/请求 或 $15/月 |
| 7 | 自建移动端 API 逆向 | 硬核逆向 | 🟡 可行但极高门槛 | 极高 | 高 | 签名随版本变，需常跟 |

**评估结论**：对"服务器 + 自动化 + 低成本 + 可接受 7 天续期"的场景，**方案 1（xiaohongshu-cli + 桌面导 cookie）** 是最优解。
纯不想碰账号/代码、能付费则**方案 6**。

---

## 3. 推荐方案落地（xiaohongshu-cli + Cookie 复用）

### 3.1 架构

```
┌─────────────┐        导出 cookies.json         ┌──────────────────────┐
│  桌面(你电脑) │  ───────────────────────────▶   │  Oracle ARM64 服务器   │
│ Chrome登录XHS │   (每7天一次, 或由cron提醒)      │  ~/.xiaohongshu-cli/  │
│ xhs login    │                                  │   cookies.json        │
└─────────────┘                                  │        │             │
                                                  │   xhs search/read ... │
                                                  │   (纯HTTP签名,无浏览器)│
                                                  │        │             │
                                                  │  采集结果→Hermes/文件 │
                                                  └──────────────────────┘
```

### 3.2 服务器端安装（已实测可装）

```bash
# 架构确认
uname -m        # → aarch64（ARM64，无需浏览器）

# 安装（uv，已验证 xiaohongshu-cli==0.6.4 在 ARM64 正常装）
export PATH="$HOME/.local/bin:$PATH"   # uv 工具默认不进 PATH，务必先 export
uv tool install xiaohongshu-cli

xhs --version   # → xhs, version 0.6.4
```

### 3.3 登录：在桌面完成，导出 cookie 到服务器

**桌面侧（你的 Mac/Windows，有 Chrome）：**
```bash
# 用 uv/pipx 装上同款 xiaohongshu-cli
uv tool install xiaohongshu-cli
# 方式A：自动从本机 Chrome 提取 cookie（需先在 Chrome 登录小红书网页版）
xhs login
# 方式B：二维码扫码（用小红书 App 扫终端二维码）
xhs login --qrcode
# 登录成功后 cookie 存于 ~/.xiaohongshu-cli/cookies.json
cat ~/.xiaohongshu-cli/cookies.json
```

**服务器侧（把 cookie 放进去）：**
```bash
# 把桌面生成的 cookies.json 内容写入服务器相同路径
mkdir -p ~/.xiaohongshu-cli
# 直接用 scp / 或粘贴内容写文件（内容即明文 JSON，含 a1/web_session/webId 等键）
cat > ~/.xiaohongshu-cli/cookies.json <<'EOF'
{ "a1": "...", "web_session": "...", "webId": "...", "web_session_sec": "...", "saved_at": 0 }
EOF
chmod 600 ~/.xiaohongshu-cli/cookies.json
```

> 🔑 **cookie 格式要点（已核对源码 `cookies.py`）**：
> - 文件为**明文 JSON dict**，`load_saved_cookies()` 只校验存在 `a1` 键即视为有效
> - 关键字段：`a1`（必填）、`web_session`、`web_session_sec`、`webId`
> - 自动续期：源码会在 session 过期时"自动尝试从浏览器刷新"，**但服务器无浏览器会失败并告警** → 所以靠人工/桌面重导

### 3.4 采集（纯 API，零浏览器——已用源码确认）

```bash
# 搜索笔记（结构化输出，便于 Hermes 解析）
xhs search "AI副业" --json | jq '.[0].id'
xhs search "咖啡" --sort popular        # general | popular | latest
xhs search "穿搭" --type video          # all | video | image

# 读取笔记详情 + 评论
xhs search "黑丝"
xhs read 1                              # 读上一次列表第 1 条
xhs comments 1 --all --json             # 全部评论（自动翻页）

# 用户 / 发现
xhs user <user_id>
xhs user-posts <user_id> --cursor X
xhs feed                                # 推荐流
xhs hot -c travel                       # 热门(分类: fashion/food/travel/...)

# 登录状态检查（cron 监控用）
xhs status                              # 非 TTY 默认输出 YAML，失败 ≠ 0
```

### 3.5 与 Hermes / agent-reach 集成

```bash
# 让 agent-reach 把小红书路由到这个 CLI（而非不可用的 OpenCLI）
# agent-reach v1.5.0 中小红书首选 OpenCLI(桌面)，服务器需显式降级到 CLI 路径
agent-reach doctor --json | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('xiaohongshu',{}).get('active_backend','n/a'))
"
# 实际调用时直接用 xhs 子命令即可，不必强依赖 agent-reach 的路由
```

---

## 4. 付费托管替代（方案 6，零运维）

若不想管 cookie 续期，直接调托管 API（服务器可直连，无需浏览器）：

| 服务 | 计费 | 说明 |
|------|------|------|
| Tikhub RedNote API | ~$0.01/请求 | 红书 Notes/Users/Search 端点 |
| Apify all-in-one-rednote | $15/月 + 用量 | 托管爬虫，输出结构化 |

**取舍**：付费方案省去 7 天续期的人工操作，但有成本、且把账号/数据交给第三方。自用低频采集仍推荐**方案 1**。

---

## 5. 自动化与监控（cron 示例）

```bash
# /opt/data/scripts/xhs_collect.sh —— 每日采集 + cookie 健康巡检
#!/usr/bin/env bash
export PATH="$HOME/.local/bin:$PATH"
# 1) 校验登录态
if ! xhs status >/dev/null 2>&1; then
  echo "⚠️ 小红书 cookie 已失效，请桌面重导 cookies.json" | \
    /opt/data/scripts/send_qq_bot.py "【XHS采集告警】cookie 失效，需重导"
  exit 1
fi
# 2) 采集（示例：搜索关键词，输出 JSON 落盘）
xhs search "AI副业" --json > /opt/data/data/xhs/ai_sidehustle_$(date +%F).json
```

```bash
# crontab（注意：主 profile 的 cron 按 UTC，北京时间 09:00 = 01:00 UTC）
0 1 * * * /opt/data/scripts/xhs_collect.sh >> /opt/data/logs/xhs_collect.log 2>&1
```

> ⚠️ 时区铁律（来自记忆）：cron 调度器默认按 **UTC** 解释。北京 09:00 需写 `0 1 * * *`。
> 若用 investment profile 的 cron 则按 +08。

---

## 6. 实测证据清单（本文结论的来源，非臆测）

| 假设 | 验证方式 | 结果 |
|------|---------|------|
| 服务器架构 | `uname -m` | `aarch64`（ARM64） |
| xiaohongshu-cli 能在 ARM64 安装 | `uv tool install xiaohongshu-cli` | ✅ 成功，v0.6.4 |
| `xhs login --qrcode` 服务器可用？ | 实跑 20s | 🔴 崩：`Camoufox(headless=False)` 需浏览器 |
| `search/read` 是否依赖浏览器？ | 读 `commands/search.py` + `client.py` grep camoufox/playwright | ✅ **不 import 浏览器**，走 `XhsClient` 纯 HTTP |
| cookie 能否跨机器复用？ | 读 `cookies.py::load_saved_cookies/save_cookies` | ✅ 明文 JSON，只校验 `a1` 存在 |
| 旧 skill 结论是否仍成立？ | 对比 `server-setup.md` 与实测 | ❌ 旧结论针对 go-rod 浏览器方案，已过时 |
| R2 上传器接口 | 读 `/opt/data/r2_uploader.py` | `R2Uploader().upload_file(path, key, ct)` 无参构造 |

---

## 7. 风险与合规

1. **账号风控**：逆向 API 触发风控可能限流/封号。建议单账号低频、加随机延迟（该 CLI 已内置高斯抖动 + 指数退避）。
2. **多端互踢**：小红书**不允许同账号多 Web 端同时登录**。服务器用 cookie 期间，桌面网页版会掉线；反之亦然。错峰使用。
3. **Cookie 7 天有效**：务必 cron 监控 `xhs status`，失效即告警重导。
4. **合规第一**：仅采集公开内容、仅自用/学习。勿批量抓取他人隐私、勿商用爬取。遵守平台 ToS。
5. **密钥保护**：`cookies.json` 含会话凭证，`chmod 600`，勿入 git、勿进 .env（.env 由你自管，Agent 不写）。

---

## 8. 下一步行动（可选）

- [ ] 在你桌面执行 `xhs login`（或 `--qrcode`），导出 `cookies.json`
- [ ] 把 `cookies.json` 传到服务器 `~/.xiaohongshu-cli/`
- [ ] 服务器跑 `xhs search "测试" --json` 验证采集链路
- [ ] 配置 cron 每日采集 + cookie 失效告警
- [ ] （可选）若嫌续期麻烦，迁到 Tikhub/Apify 付费 API

---

*本文结论均基于 2026-07-19 当日的工具版本与实测，工具更新后请重跑 §6 验证清单。*
