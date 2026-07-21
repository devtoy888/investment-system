"""Shared Feishu card sender for cron job pre-scripts.
Sends markdown content as Card 2.0 format with native table support.

Usage:
  from send_cards import send_card, send_card_with_tables, send_multiple

  send_card("标题", "**markdown**", "blue")
  send_card_with_tables("标题", "| H1 | H2 |\\n|---|---|\\n| A | B |", "red")
"""
import os, json, requests, dotenv
import sys

# Load once at module level
_dotenv_loaded = False
_token = None
_chat_id = None

def _ensure_auth():
    global _token, _chat_id, _dotenv_loaded
    if _dotenv_loaded and _token:
        return
    dotenv.load_dotenv('/opt/data/profiles/investment/.env')
    app_id = os.environ['FEISHU_APP_ID']
    app_secret = os.environ['FEISHU_APP_SECRET']
    resp = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': app_id, 'app_secret': app_secret},
        timeout=10
    )
    _token = resp.json()['tenant_access_token']
    _chat_id = 'oc_5c176bb1243a1f2d353ed926e62f4d1a'
    _dotenv_loaded = True


def send_card(title, content, template="blue"):
    """Send a pure markdown card (no table parsing)."""
    _ensure_auth()
    title_short = title[:40]
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"content": title_short, "tag": "plain_text"}, "template": template},
        "elements": [{"tag": "markdown", "content": content}],
    }
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 28000:
        card["elements"] = [{"tag": "markdown", "content": content[:4000] + "\n\n...（已截断）"}]
        card_json = json.dumps(card, ensure_ascii=False)
    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        headers={'Authorization': f'Bearer {_token}', 'Content-Type': 'application/json; charset=utf-8'},
        json={'receive_id': _chat_id, 'msg_type': 'interactive', 'content': card_json},
        timeout=15
    )
    r = resp.json()
    ok = r.get('code') == 0
    print(f"  [card] {'OK' if ok else 'FAIL'} {title_short} ({len(card_json)}b) - {r.get('msg')}")
    return ok


def send_card_with_button(title, content, button_text, button_url, template="blue"):
    """Send a markdown card with a jump button at the bottom.

    The button opens the given URL when clicked (Feishu built-in browser).
    """
    _ensure_auth()
    title_short = title[:40]
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"content": title_short, "tag": "plain_text"}, "template": template},
        "elements": [
            {"tag": "markdown", "content": content},
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": button_text},
                        "type": "default",
                        "multi_url": {
                            "url": button_url,
                            "android_url": button_url,
                            "ios_url": button_url,
                        },
                    }
                ],
            },
        ],
    }
    card_json = json.dumps(card, ensure_ascii=False)
    if len(card_json) > 28000:
        card["elements"] = [{"tag": "markdown", "content": content[:3500] + "\n\n（已截断）"}]
        card_json = json.dumps(card, ensure_ascii=False)
    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        headers={'Authorization': f'Bearer {_token}', 'Content-Type': 'application/json; charset=utf-8'},
        json={'receive_id': _chat_id, 'msg_type': 'interactive', 'content': card_json},
        timeout=15
    )
    r = resp.json()
    ok = r.get('code') == 0
    print(f"  [btn-card] {'OK' if ok else 'FAIL'} {title_short} ({len(card_json)}b) - {r.get('msg')}")
    return ok


def send_card_with_tables(title, content, template="blue"):
    """Send a card with native table components for GFM tables in content."""
    _ensure_auth()
    from sitecustomize import _build_card_from_content
    card_json = _build_card_from_content(content)
    parsed = json.loads(card_json)
    parsed['header']['title']['content'] = title[:40]
    if template:
        parsed['header']['template'] = template
    card_json = json.dumps(parsed, ensure_ascii=False)
    
    if len(card_json) > 28000:
        print(f"  WARNING: card too large ({len(card_json)}b), fallback to markdown only")
        return send_card(title, content, template)
    
    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        headers={'Authorization': f'Bearer {_token}', 'Content-Type': 'application/json; charset=utf-8'},
        json={'receive_id': _chat_id, 'msg_type': 'interactive', 'content': card_json},
        timeout=15
    )
    r = resp.json()
    ok = r.get('code') == 0
    print(f"  [table-card] {'OK' if ok else 'FAIL'} {title[:30]} ({len(card_json)}b) - {r.get('msg')}")
    return ok
