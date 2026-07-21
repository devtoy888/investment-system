# 小红书（RedNote）Headless ARM64 服务器采集 — 实测参考

> 适用：Oracle ARM64 无桌面/无 Chrome 服务器。来源：2026-07-19 实测 + 源码核对。
> 配套主文档：`server-setup.md` 的「小红书 on Headless ARM64 Servers」一节。

## 核心结论（实证）

| 假设 | 验证方式 | 结果 |
|------|---------|------|
| 服务器架构 | `uname -m` | `aarch64`（ARM64，无需浏览器） |
| xiaohongshu-cli 能在 ARM64 安装 | `uv tool install xiaohongshu-cli` | ✅ 成功，v0.6.4 |
| `xhs login --qrcode` 服务器可用？ | 实跑 | 🔴 崩：`Camoufox(headless=False)` 需浏览器 |
| `search/read` 是否依赖浏览器？ | 读 `commands/search.py` + `client.py` grep camoufox/playwright | ✅ 不 import 浏览器，走 `XhsClient` 纯 HTTP |
| cookie 能否跨机器复用？ | 读 `cookies.py::load_saved_cookies/save_cookies` | ✅ 明文 JSON，只校验 `a1` 存在 |

## 推荐方案：xiaohongshu-cli + Cookie 复用

### 1) 服务器安装（已实测）
```bash
export PATH="$HOME/.local/bin:$PATH"   # uv 工具默认不进 PATH
uv tool install xiaohongshu-cli
xhs --version                          # → xhs, version 0.6.4
```

### 2) 登录在桌面做，导出 cookie 到服务器
桌面（Mac/Windows，有 Chrome）：
```bash
uv tool install xiaohongshu-cli
xhs login            # 自动从本机 Chrome 提取（需先在 Chrome 登录小红书网页版）
# 或 xhs login --qrcode   # 小红书 App 扫终端二维码
cat ~/.xiaohongshu-cli/cookies.json
```
服务器（写入相同路径）：
```bash
mkdir -p ~/.xiaohongshu-cli
cat > ~/.xiaohongshu-cli/cookies.json <<'EOF'
{ "a1": "...", "web_session": "...", "webId": "...", "web_session_sec": "...", "saved_at": 0 }
EOF
chmod 600 ~/.xiaohongshu-cli/cookies.json
```
> cookie 格式要点（源码 `cookies.py`）：明文 JSON dict，`load_saved_cookies()` 仅校验 `a1` 键存在即有效；关键字段 `a1`(必填)/`web_session`/`web_session_sec`/`webId`。自动续期会"尝试从浏览器刷新"，服务器无浏览器会失败并告警 → 靠人工/桌面重导。

### 3) 采集（纯 API，零浏览器）
```bash
xhs search "AI副业" --json | jq '.[0].id'
xhs search "咖啡" --sort popular        # general | popular | latest
xhs search "穿搭" --type video          # all | video | image
xhs read 1                              # 读上一次列表第 1 条
xhs comments 1 --all --json             # 全部评论（自动翻页）
xhs feed ; xhs hot -c travel            # 推荐流 / 热门分类
xhs status                              # 非 TTY 默认 YAML，失败 ≠ 0（cron 监控用）
```

### 4) cron 监控 cookie 失效
```bash
# 主 profile cron 按 UTC：北京 09:00 = 01:00 UTC
0 1 * * * /opt/data/scripts/xhs_collect.sh >> /opt/data/logs/xhs_collect.log 2>&1
# 脚本内：if ! xhs status >/dev/null 2>&1; then 告警"cookie 失效，需桌面重导"; exit 1; fi
```

## 付费托管替代（零运维）
- Tikhub RedNote API：~$0.01/请求
- Apify all-in-one-rednote：$15/月 + 用量
服务器可直连，无需浏览器；取舍是有成本、数据交给第三方。

## 风险与合规
1. 账号风控：逆向 API 可能限流/封号，单账号低频 + CLI 内置高斯抖动/指数退避。
2. 多端互踢：小红书不允许同账号多 Web 端同时登录，服务器用 cookie 时桌面网页版掉线，错峰。
3. Cookie 7 天有效：务必 cron 监控 `xhs status`。
4. 合规第一：仅公开内容、仅自用/学习，遵守平台 ToS。
5. `cookies.json` 含会话凭证，`chmod 600`，勿入 git、勿进 .env（.env 由用户自管）。
