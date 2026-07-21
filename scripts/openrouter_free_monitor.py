#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter 限免模型监测器
=========================
检测 OpenRouter 上"新上线的限时免费模型"（类似 tencent/hy3:free 限免），
生成模型优点说明，并与默认主力模型 deepseek/deepseek-v4-flash 做优缺点对照，
输出到 stdout 供 cron 投递。

用法：
  python3 openrouter_free_monitor.py init      # 静默初始化 state（不通知），仅记录当前已知限免模型
  python3 openrouter_free_monitor.py check     # 默认模式：检测新限免并输出通知报告

设计：
  - 免费判定：pricing.prompt == "0" 且 pricing.completion == "0"
  - 限免判定：免费 且 expiration_date 不为 None 且 过期日 > 现在（未来才免费）
  - 去重：state 文件记录已通知过的限免模型 id，避免重复推送
"""
import json
import os
import sys
import time
import urllib.request
import datetime

API_URL = "https://openrouter.ai/api/v1/models"
STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openrouter_free_state.json")

# 主力模型基准（deepseek/deepseek-v4-flash 的固定规格，作为对照锚点）
# 这些数值来自 OpenRouter API 实测（2026-07-15 抓取），后续若该模型规格变化需手动更新
MAIN_MODEL_ID = "deepseek/deepseek-v4-flash"
MAIN_MODEL_SPEC = {
    "name": "DeepSeek: DeepSeek V4 Flash",
    "context_length": 1048576,          # 1M
    "params_total": "284B",
    "params_active": "13B",
    "arch": "MoE（混合专家）",
    "modality": "text->text",
    "price_prompt_per_M": 0.098,        # 美元 / 百万 token
    "price_completion_per_M": 0.196,
    "notes": "效率优化的 MoE 模型，1M 上下文，极低成本，速度快。",
}

UA = {"User-Agent": "openrouter-free-monitor/1.0"}


def fetch_models():
    req = urllib.request.Request(API_URL, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("data", [])


def parse_expiry(val):
    """OpenRouter 的 expiration_date 可能是：
       - ISO 日期字符串（如 '2026-07-21'）或 ISO 日期时间字符串
       - 毫秒/秒时间戳字符串或数字
       返回带 UTC 时区的 datetime 或 None。"""
    if not val:
        return None
    # 时间戳（数字或纯数字字符串）
    if isinstance(val, (int, float)) or (isinstance(val, str) and val.lstrip("-").isdigit()):
        try:
            v = float(val)
            if v > 1e12:      # 毫秒
                v /= 1000
            return datetime.datetime.fromtimestamp(v, datetime.timezone.utc)
        except (ValueError, TypeError):
            pass
    # ISO 字符串
    if isinstance(val, str):
        try:
            s = val.strip().replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except ValueError:
            pass
    return None


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"seen": [], "init_at": None}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def is_free(m):
    p = m.get("pricing", {})
    return p.get("prompt") == "0" and p.get("completion") == "0"


def free_limited_models(models, now):
    """返回当前处于限免期（免费且有未来过期日）的模型列表。"""
    out = []
    for m in models:
        if not is_free(m):
            continue
        exp = parse_expiry(m.get("expiration_date"))
        if exp is None:
            continue  # 常驻免费池（无过期日）
        if exp > now:
            out.append(m)
    return out


def modality_cn(m):
    arch = m.get("architecture", {}) or {}
    mod = arch.get("modality", "text->text")
    mapping = {
        "text->text": "纯文本",
        "text+image->text": "支持图像输入（多模态视觉）",
        "text->image": "文生图",
        "text->audio": "文生语音",
    }
    return mapping.get(mod, mod)


def summarize_merits(m):
    """基于 API 真实字段提炼优点（中文为主，不编造）。"""
    lines = []
    ctx = m.get("context_length") or 0
    ctx_s = f"{ctx/1024:.0f}K" if ctx < 1_000_000 else f"{ctx/1_000_000:.1f}M"
    lines.append(f"· 上下文窗口：{ctx_s}（主力 DeepSeek V4 Flash 为 1M）")
    lines.append(f"· 模态：{modality_cn(m)}")
    arch = m.get("architecture", {}) or {}
    if arch.get("modality", "").startswith("text+image"):
        lines.append("· 亮点：支持看图输入，主力模型不具备视觉能力")
    # 规模：从厂商描述解析参数规模（中文呈现，去掉又长又丑的英文原句）
    desc = (m.get("description") or "").strip()
    import re
    tot = re.search(r"(\d+\.?\d*)\s*B-parameter", desc, re.I)
    act = re.search(r"(\d+\.?\d*)\s*B active", desc, re.I)
    if tot and act:
        lines.append(f"· 规模：{tot.group(1)}B 总参 / {act.group(1)}B 激活")
    elif tot:
        lines.append(f"· 规模：{tot.group(1)}B 参数")
    tok = arch.get("tokenizer")
    if tok and tok != "Other":
        lines.append(f"· 分词器：{tok}")
    kc = m.get("knowledge_cutoff")
    if kc:
        lines.append(f"· 知识截止：{kc}")
    exp = parse_expiry(m.get("expiration_date"))
    if exp:
        local = exp.astimezone()
        lines.append(f"· 免费截止：{local.strftime('%Y-%m-%d %H:%M')}（之后恢复计费或下线）")
    return "\n".join(lines)


def compare(m):
    """生成与主力模型的优缺点对照（严格基于 API 字段 + 固定基准）。"""
    rows = []
    ctx = m.get("context_length") or 0
    main_ctx = MAIN_MODEL_SPEC["context_length"]
    # 上下文
    if ctx >= main_ctx:
        rows.append(("上下文", f"{ctx/1_000_000:.1f}M" if ctx>=1_000_000 else f"{ctx/1024:.0f}K",
                     "1M", "持平或更大 ✓"))
    else:
        rows.append(("上下文", f"{ctx/1024:.0f}K" if ctx<1_000_000 else f"{ctx/1_000_000:.1f}M",
                     "1M", f"更小（约 {ctx/main_ctx*100:.0f}% 主力）✗"))
    # 免费性
    rows.append(("价格", "免费（限免期）", f"约 ${MAIN_MODEL_SPEC['price_prompt_per_M']}/M 输入",
                 "限免期零成本 ✓；但到期恢复计费/下线 ✗"))
    # 模态
    arch = m.get("architecture", {}) or {}
    mod = arch.get("modality", "text->text")
    main_mod = MAIN_MODEL_SPEC["modality"]
    if mod != main_mod:
        if mod.startswith("text+image"):
            rows.append(("模态", "支持图像输入", "纯文本", "多模态能力更宽 ✓"))
        else:
            rows.append(("模态", modality_cn(m), "纯文本", "能力不同（视具体模态）"))
    else:
        rows.append(("模态", "纯文本", "纯文本", "持平"))
    # 参数规模（若可推断）
    desc = (m.get("description") or "")
    import re
    pm = re.search(r"(\d+\.?\d*)B\s*(?:total|参数|parameters)", desc, re.I)
    if pm:
        rows.append(("规模(描述)", f"{pm.group(1)}B（厂商口径）",
                     f"{MAIN_MODEL_SPEC['params_total']}总/{MAIN_MODEL_SPEC['params_active']}激活",
                     "仅供参考，架构不同难直接比"))
    return rows


def build_report(new_models, demo=False):
    """Markdown 美化版（已用 1904452472 裸 payload 验证可渲染）。
    按官方文档语法：# 标题、**加粗**、- 列表、> 引用、*** 分割线。"""
    now = datetime.datetime.now(datetime.timezone.utc)
    ts = now.astimezone().strftime("%Y-%m-%d %H:%M")
    blocks = []
    blocks.append("# 🆕 OpenRouter 新限免模型提醒")
    if demo:
        blocks.append("> ⚠️ 演示样例（基于当前真实限免数据，非真实新增）")
    blocks.append(f"> 🕐 检测时间：{ts}（北京时间）")
    blocks.append(f"> 📊 共发现 **{len(new_models)}** 个新上线 / 新进入限免期的免费模型")
    blocks.append("")

    for idx, m in enumerate(new_models, 1):
        blocks.append(f"## 【{idx}】{m['id']}")
        blocks.append(f"**名称**：{m.get('name','')}")
        blocks.append("")
        blocks.append("### ✨ 优点")
        blocks.append(summarize_merits(m))
        blocks.append("")
        blocks.append(f"### ⚖️ 与主力 {MAIN_MODEL_ID} 对照")
        blocks.append(compare_md(m))
        blocks.append("")
        blocks.append("***")

    blocks.append("> 📌 监测说明：仅通知带过期日的限时免费模型（如 hy3:free）；常驻免费池不重复提醒。")
    return "\n".join(blocks)


def compare_md(m):
    """Markdown 对照：①②③ 编号；结论用 ✅/⚠️/➖ emoji。"""
    ctx = m.get("context_length") or 0
    main_ctx = MAIN_MODEL_SPEC["context_length"]
    arch = m.get("architecture", {}) or {}
    mod = arch.get("modality", "text->text")
    main_mod = MAIN_MODEL_SPEC["modality"]

    out = []
    if ctx >= main_ctx:
        a_ctx = f"{ctx/1_000_000:.1f}M" if ctx >= 1_000_000 else f"{ctx/1024:.0f}K"
        out.append(f"① **上下文**：本模型 {a_ctx} vs 主力 1M → ✅ 持平或更大")
    else:
        a_ctx = f"{ctx/1024:.0f}K" if ctx < 1_000_000 else f"{ctx/1_000_000:.1f}M"
        out.append(f"① **上下文**：本模型 {a_ctx} vs 主力 1M → ⚠️ 更小（约 {ctx/main_ctx*100:.0f}% 主力）")
    out.append(f"② **价格**：本模型 免费(限免期) vs 主力 ~${MAIN_MODEL_SPEC['price_prompt_per_M']}/M 输入 → ✅ 限免期零成本，⚠️ 到期恢复计费/下线")
    if mod != main_mod:
        if mod.startswith("text+image"):
            out.append(f"③ **模态**：本模型 支持图像输入 vs 主力 纯文本 → ✅ 多模态能力更宽")
        else:
            out.append(f"③ **模态**：本模型 {modality_cn(m)} vs 主力 纯文本 → 能力不同（视具体模态）")
    else:
        out.append(f"③ **模态**：本模型 纯文本 vs 主力 纯文本 → ➖ 持平")
    desc = (m.get("description") or "")
    import re
    pm = re.search(r"(\d+\.?\d*)B\s*(?:total|参数|parameters)", desc, re.I)
    if pm:
        out.append(f"④ **规模(描述)**：{pm.group(1)}B（厂商口径）vs 主力 {MAIN_MODEL_SPEC['params_total']}总/{MAIN_MODEL_SPEC['params_active']}激活 → 仅供参考")
    return "\n".join(out)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    now = datetime.datetime.now(datetime.timezone.utc)
    models = fetch_models()

    if mode == "demo":
        # 演示：取真实当前限免数据前若干条，强制生成报告（不写 state、不推送）
        limited = free_limited_models(models, now)
        # 优先挑有视觉能力或不同模态的，演示更丰富；无则取前 2 条
def _send_to_default_qq(markdown_text: str) -> int:
    """用 .env 的 default QQ 凭据(1904452472)直接发裸 markdown payload 到本对话。
    绕过 Hermes 的 deliver=qqbot（实测它会把 markdown 降级成纯文字）。
    凭据从 .env 读取，不硬编码。超长自动按消息边界分段。"""
    import requests, os
    # 读 .env（Hermes 加载但不 export 到环境，这里直接解析文件）
    env = {}
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("QQ_APP_ID=") or line.startswith("QQ_CLIENT_SECRET="):
                    k, v = line.split("=", 1)
                    env[k] = v.strip().strip('"')
    except Exception:
        pass
    app_id = env.get("QQ_APP_ID")
    secret = env.get("QQ_CLIENT_SECRET")
    if not app_id or not secret:
        print("[send] 未找到 QQ_APP_ID/SECRET，无法发送", file=__import__("sys").stderr)
        return 0
    openid = "82BC393B5BF9B2DC01006D6DFA66CB9B"  # 本对话 chat_id（default QQ DM）
    try:
        tok = requests.post("https://bots.qq.com/app/getAppAccessToken",
                            json={"appId": app_id, "clientSecret": secret}, timeout=10).json().get("access_token")
        if not tok:
            print("[send] 获取 token 失败", file=__import__("sys").stderr)
            return 0
        # 分段：按模型块(*** 分隔)切，单段 < 3800 字符
        chunks = markdown_text.split("\n***\n") if "\n***\n" in markdown_text else [markdown_text]
        sent = 0
        for i, ch in enumerate(chunks):
            body = ch.strip()
            if not body:
                continue
            if i < len(chunks) - 1:
                body += "\n***"
            if len(body) > 3800:
                body = body[:3800]
            r = requests.post(f"https://api.sgroup.qq.com/v2/users/{openid}/messages",
                              headers={"Authorization": f"QQBot {tok}", "Content-Type": "application/json"},
                              json={"msg_type": 2, "markdown": {"content": body}}, timeout=15)
            if r.status_code == 200:
                sent += 1
            else:
                print(f"[send] FAIL {r.status_code} {r.text[:200]}", file=__import__("sys").stderr)
        return sent
    except Exception as e:
        print(f"[send] 异常：{e}", file=__import__("sys").stderr)
        return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    now = datetime.datetime.now(datetime.timezone.utc)
    models = fetch_models()

    if mode == "demo":
        # 演示：取真实当前限免数据，强制生成 markdown 报告并打印（不发送）。
        limited = free_limited_models(models, now)
        demo_models = [m for m in limited if (m.get("architecture", {}) or {}).get("modality", "").startswith("text+image")]
        if len(demo_models) < 2:
            demo_models += [m for m in limited if m not in demo_models]
        demo_models = demo_models[:2]
        print(build_report(demo_models, demo=True))
        return

    if mode == "push":
        # 手动演示发送：生成 markdown 报告并直接发到 default QQ（验证渲染）。
        limited = free_limited_models(models, now)
        demo_models = [m for m in limited if (m.get("architecture", {}) or {}).get("modality", "").startswith("text+image")]
        if len(demo_models) < 2:
            demo_models += [m for m in limited if m not in demo_models]
        demo_models = demo_models[:2]
        report = build_report(demo_models, demo=True)
        n = _send_to_default_qq(report)
        print(f"[push] 已发送 {n} 条 markdown 消息到 default QQ")
        return

    if mode == "init":
        limited = free_limited_models(models, now)
        state = {"seen": [m["id"] for m in limited], "init_at": int(time.time())}
        save_state(state)
        # 静默，不输出（避免 cron init 时误投递）
        return

    # check 模式：检测新限免，有则直接发 markdown 到 default QQ；无则静默。
    state = load_state()
    seen = set(state.get("seen", []))
    limited = free_limited_models(models, now)
    limited_ids = {m["id"] for m in limited}
    new_models = [m for m in limited if m["id"] not in seen]
    state["seen"] = sorted(limited_ids)
    state["updated_at"] = int(time.time())
    save_state(state)
    if not new_models:
        return
    report = build_report(new_models)
    _send_to_default_qq(report)


if __name__ == "__main__":
    main()

