#!/usr/bin/env python3
# scripts/qq_markdown_send.py — Reusable QQ markdown direct-send helper.
#
# WHY THIS EXISTS: Hermes' cron `deliver=qqbot` linkage downgrades markdown to
# plain text on this deployment (verified 2026-07-15). The bot account and the
# markdown syntax are both fine — a raw `{"msg_type":2,"markdown":{"content":...}}`
# POST to the QQ REST API renders correctly. So cron scripts that need markdown on
# QQ should send it themselves and set the cron task `deliver=local`.
#
# USAGE (in a cron --script):
#     from qq_markdown_send import send_markdown_to_default_qq
#     send_markdown_to_default_qq(report_text)   # returns # messages sent
#
# Credentials are read from the deployment .env (QQ_APP_ID / QQ_CLIENT_SECRET) —
# NEVER hardcode. The target openid is the default-profile user's QQ DM chat_id.
import os
import sys
import requests


def _load_qq_env(env_path=None):
    """Read QQ_APP_ID / QQ_CLIENT_SECRET from .env (Hermes loads it but does not
    export to the shell env, so parse the file directly)."""
    if env_path is None:
        # scripts/ lives under <profile>/.hermes/scripts; the .env is ONE level
        # up at <profile>/.hermes/.env (= /opt/data/.env on the standard Docker
        # deploy, where ~/.hermes-main is mounted to /opt/data). The original
        # ".. / .. / .env" was WRONG: it resolved to /opt/.env and silently
        # failed to find creds (the script printed "missing QQ_APP_ID/SECRET"
        # and sent 0 messages). Walk up to find the .env that actually defines
        # QQ_APP_ID so this works regardless of mount layout.
        here = os.path.dirname(os.path.abspath(__file__))
        found = None
        for _ in range(6):
            cand = os.path.join(here, ".env")
            if os.path.exists(cand):
                try:
                    with open(cand) as cf:
                        for cl in cf:
                            if cl.strip().startswith("QQ_APP_ID="):
                                found = cand
                                break
                except Exception:
                    pass
            if found:
                break
            here = os.path.dirname(here)
        env_path = found or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
    env = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("QQ_APP_ID=") or line.startswith("QQ_CLIENT_SECRET="):
                    k, v = line.split("=", 1)
                    env[k] = v.strip().strip('"')
    except Exception:
        pass
    return env.get("QQ_APP_ID"), env.get("QQ_CLIENT_SECRET")


def send_markdown_to_default_qq(markdown_text, openid=None, max_chars=3800):
    """Send markdown text to the default-profile user's QQ DM via raw REST call.
    Splits on `***` blocks so each chunk stays under QQ's length limit.
    Returns number of messages sent (0 on failure)."""
    if openid is None:
        openid = "82BC393B5BF9B2DC01006D6DFA66CB9B"  # default-profile QQ DM chat_id
    app_id, secret = _load_qq_env()
    if not app_id or not secret:
        print("[qq] missing QQ_APP_ID/SECRET, cannot send", file=sys.stderr)
        return 0
    try:
        tok = requests.post("https://bots.qq.com/app/getAppAccessToken",
                            json={"appId": app_id, "clientSecret": secret},
                            timeout=10).json().get("access_token")
        if not tok:
            print("[qq] token fetch failed", file=sys.stderr)
            return 0
        chunks = markdown_text.split("\n***\n") if "\n***\n" in markdown_text else [markdown_text]
        sent = 0
        for i, ch in enumerate(chunks):
            body = ch.strip()
            if not body:
                continue
            if i < len(chunks) - 1:
                body += "\n***"
            if len(body) > max_chars:
                body = body[:max_chars]
            r = requests.post(
                f"https://api.sgroup.qq.com/v2/users/{openid}/messages",
                headers={"Authorization": f"QQBot {tok}", "Content-Type": "application/json"},
                json={"msg_type": 2, "markdown": {"content": body}},
                timeout=15,
            )
            if r.status_code == 200:
                sent += 1
            else:
                print(f"[qq] FAIL {r.status_code} {r.text[:200]}", file=sys.stderr)
        return sent
    except Exception as e:
        print(f"[qq] exception: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    # Smoke test: send a tiny markdown probe.
    n = send_markdown_to_default_qq("# 直连测试\n这是 **加粗**\n- 列表一\n- 列表二")
    print(f"sent {n} message(s)")
