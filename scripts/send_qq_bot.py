"""
QQ Bot 消息发送工具 — 直接通过 QQ Bot API v2 推送 Markdown 消息。
可用于 cron 脚本中绕过 deliver 机制的限制。
"""
import json, requests, os, time

# QQ Bot API 参数
_APP_ID = "1905190887"
_CLIENT_SECRET = "KZaNvGMOJ2XptjLj"
_USER_OPENID = "C40A1DEC1124496F9034304E31063FB7"
_TOKEN_URL = "https://bots.qq.com/app/getAppAccessToken"
_API_BASE = "https://api.sgroup.qq.com"

_token = None
_token_expires = 0

# QQ Bot API 单条消息限制 4000 字符（markdown）
MAX_MSG_CHARS = 3800


def _ensure_token():
    global _token, _token_expires
    now = time.time()
    if _token and now < _token_expires - 60:
        return
    resp = requests.post(
        _TOKEN_URL,
        json={"appId": _APP_ID, "clientSecret": _CLIENT_SECRET},
        timeout=10,
    )
    data = resp.json()
    _token = data.get("access_token")
    expires_in = int(data.get("expires_in", 7200))
    _token_expires = now + expires_in


def send_markdown(content: str, openid: str = _USER_OPENID) -> bool:
    """发送一条 Markdown 消息到 QQ C2C（msg_type=2，markdown.content 格式）"""
    _ensure_token()
    resp = requests.post(
        f"{_API_BASE}/v2/users/{openid}/messages",
        headers={"Authorization": f"QQBot {_token}", "Content-Type": "application/json"},
        json={"msg_type": 2, "markdown": {"content": content}},
        timeout=15,
    )
    ok = resp.status_code == 200
    if not ok:
        print(f"  [QQ] FAIL {resp.status_code} {resp.text[:200]}", file=__import__('sys').stderr)
    return ok


def send_markdown_in_chunks(title: str, content: str, sep: str = "═══════════════════════════════════"):
    """合并所有内容为连续消息，仅按QQ 3800字符限制分段。
    不按分隔符拆分——将12条消息压缩到2-3条。"""
    # 去掉状态行（如 "Morning cards done!"、"OK ..."）
    lines = [l for l in content.split("\n")
             if not l.strip().startswith(("OK ", "FAIL ", "All done", "Morning cards done", "————"))]
    # 保留分隔线作为视觉分隔，但不作为消息切分点
    full = "\n".join(lines).strip()
    if not full:
        return 0

    # 统一标题头（仅第一个消息带标题，后续用接续标记）
    header = f"📚 {title}\n\n"
    full_msg = header + full

    # 一条消息搞定
    if len(full_msg) <= MAX_MSG_CHARS:
        return 1 if send_markdown(full_msg) else 0

    # 超长：按段落切分，每段不超过 MAX_MSG_CHARS
    paragraphs = full_msg.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        test = (current + "\n\n" + para).strip() if current else para
        if len(test) > MAX_MSG_CHARS and current:
            chunks.append(current)
            current = para
        else:
            current = test
    if current:
        chunks.append(current)

    sent = 0
    for i, chunk in enumerate(chunks):
        # 多段时加接续标记
        if i > 0:
            chunk = "[📎 接上条]\n\n" + chunk
        if i < len(chunks) - 1:
            chunk += "\n\n[📎 续下条]"
        if send_markdown(chunk):
            sent += 1
        time.sleep(0.3)
    return sent
