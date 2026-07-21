# QQ Bot API v2 直连推送（绕过 cron deliver 机制）

## 背景

cron 的 `deliver=qqbot:chat_id` 依赖 Hermes Gateway 的消息分发层，但遇到两个问题：

1. **消息长度限制** — QQ Bot API 单条 Markdown 消息限制 4000 字符，长内容会被整体拒绝
2. **`deliver=origin` 歧义** — 在 cron 独立运行环境中可能解析到飞书而非 QQ

解决方案：让 no_agent 脚本 **直接调用 QQ Bot API v2** 发送消息，stdout 静默，cron deliver 设为 `local`。

## 正确端点

| 操作 | 端点 | 说明 |
|:----|:----|:-----|
| 获取 Token | `POST https://bots.qq.com/app/getAppAccessToken` | 不是 `api.sgroup.qq.com/apps/{id}/access_tokens` |
| 发送 C2C 消息 | `POST https://api.sgroup.qq.com/v2/users/{openid}/messages` | 单聊 |
| 发送频道消息 | `POST /channels/{channel_id}/messages` | 子频道 |

## 认证

```python
# 获取 access_token
resp = requests.post(
    "https://bots.qq.com/app/getAppAccessToken",
    json={"appId": APP_ID, "clientSecret": CLIENT_SECRET},
    timeout=10
)
token = resp.json()["access_token"]

# 使用 token（注意前缀是 "QQBot " 不是 Bearer）
headers = {"Authorization": f"QQBot {token}", "Content-Type": "application/json"}
```

⚠️ **关键坑：** Token 端点是 `bots.qq.com` 不是 `api.sgroup.qq.com`。用了错的端点会返回 `"不支持的调用" (code 11001)`。

## Markdown 消息格式

```python
# ✅ 正确的格式
json_data = {
    "msg_type": 2,
    "markdown": {
        "content": "## 标题\n\nMarkdown 内容..."
    }
}

# ❌ 错误的格式（被QQ拒绝：'无效 markdown content'）
json_data = {
    "content": "## 标题\n\nMarkdown 内容...",
    "msg_type": 2
}
```

QQ Bot 的 Markdown 格式相比标准 GFM 有额外要求：
- 支持 `#`/`##` 标题、`**加粗**`、`- 列表`、`| 表格 |`、`[链接](url)`
- **不支持**标准 Markdown 表格的 `:---:` 对齐语法？实测 `|:---|:---:|` 可以工作
- 单条消息 **4000 字符限制**
- 链接在 QQ 上存在域名级限制（详见 `references/qq-link-compatibility.md`）

## 分片发送模式

对于长内容（如财经早餐 10+ 个板块），先合并所有内容，再按 3800 字符（留余量）拆分：

```python
def send_markdown_in_chunks(content, max_chars=3800):
    """合并后按大小拆分，保留内容完整性"""
    if len(content) <= max_chars:
        return send_markdown(content)

    paragraphs = content.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        test = (current + "\n\n" + para).strip() if current else para
        if len(test) > max_chars and current:
            chunks.append(current)
            current = para
        else:
            current = test
    if current:
        chunks.append(current)

    # 加续接标记
    for i, chunk in enumerate(chunks):
        if i > 0:
            chunk = "_(📎 接上条)_\n\n" + chunk
        if i < len(chunks) - 1:
            chunk += "\n\n_(📎 续下条)_"
        send_markdown(chunk)
        time.sleep(0.3)
```

## 脚本架构

```
cron job (no_agent=true, deliver=local)
    │
    ▼
run_*.py  (wrapper)
    │  ├─ 1. 收集数据（子进程调用 collect_*.py）
    │  ├─ 2. 格式化 Markdown（子进程调用 send_*_cards.py → 输出到截获的 stdout）
    │  ├─ 3. 获取格式化的 Markdown 文本
    │  └─ 4. 调用 send_qq_bot.send_markdown_in_chunks() → QQ API
    │
    ▼
stdout 静默（empty → cron 不投递）
```

**关键设计：** 脚本自身处理 QQ 推送，cron 只负责定时触发。stdout 必须为空（静默），否则 cron 的 no_agent 投递机制会尝试再次推送。

## 相关文件

| 文件 | 说明 |
|:----|:-----|
| `/opt/data/scripts/send_qq_bot.py` | QQ API 推送工具（含 token 管理、分片发送） |
| `/opt/data/scripts/run_morning.py` | 财经早餐 wrapper（使用 send_qq_bot） |
| `/opt/data/scripts/run_noon.py` | 盘中直击 wrapper |
| `/opt/data/scripts/run_closing.py` | 收盘复盘 wrapper |

## 与 cron deliver 对比

| 方式 | 优点 | 缺点 |
|:----|:----|:----|
| cron `deliver=qqbot:chat_id` | 零代码，自动处理 | 单条长度限制，不能分片；依赖 gateway |
| **脚本直调 QQ API** (**推荐**) | 可分片、可控、可靠 | 需维护凭证；需自己实现分片 |
