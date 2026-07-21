"""Push remaining morning briefing content as Feishu cards."""
import os, json, requests, dotenv
import sys
sys.path.insert(0, '/opt/data/.feishu-deps')

dotenv.load_dotenv('/opt/data/profiles/investment/.env')
app_id = os.environ['FEISHU_APP_ID']
app_secret = os.environ['FEISHU_APP_SECRET']

resp = requests.post(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret}
)
token = resp.json()['tenant_access_token']
chat_id = 'oc_5c176bb1243a1f2d353ed926e62f4d1a'


def send_card(title, content, template="blue"):
    """Build and send a Feishu card with markdown content (no table parsing)."""
    title_short = title[:30]
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"content": title_short, "tag": "plain_text"},
            "template": template,
        },
        "elements": [
            {"tag": "markdown", "content": content},
        ],
    }
    card_json = json.dumps(card, ensure_ascii=False)
    
    # Check card size
    if len(card_json) > 28000:
        print(f"  WARNING: card too large ({len(card_json)} bytes), truncating")
        # Truncate content to fit
        max_content = len(content) - (len(card_json) - 27000)
        content = content[:max_content] + "\n\n...(已截断)"
        card["elements"] = [{"tag": "markdown", "content": content}]
        card_json = json.dumps(card, ensure_ascii=False)
    
    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=utf-8'},
        json={'receive_id': chat_id, 'msg_type': 'interactive', 'content': card_json}
    )
    r = resp.json()
    ok = r.get('code') == 0
    print(f"{'OK' if ok else 'FAIL'} {title_short} - {r.get('msg')} ({len(card_json)} bytes)")
    return ok


def send_card_with_tables(title, content, template="blue"):
    """Build and send a Feishu card with native table support."""
    from sitecustomize import _build_card_from_content
    card_json = _build_card_from_content(content)
    parsed = json.loads(card_json)
    parsed['header']['title']['content'] = title
    if template:
        parsed['header']['template'] = template
    card_json = json.dumps(parsed, ensure_ascii=False)
    
    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=utf-8'},
        json={'receive_id': chat_id, 'msg_type': 'interactive', 'content': card_json}
    )
    r = resp.json()
    ok = r.get('code') == 0
    print(f"{'OK' if ok else 'FAIL'} {title} - {r.get('msg')} ({len(card_json)} bytes)")
    return ok


# Card 5: Operation plan + evaluation (has tables)
c5 = open('/tmp/fund_data/_operation_plan.txt').read() + "\n\n" + open('/tmp/fund_data/_operation_eval.txt').read()
send_card_with_tables("操作参考 & 评估", c5, "purple")

# Card 6: KOL - 唐史主任司马迁 (top posts)
kol_tang = open('/tmp/fund_data/_kol_summary.txt').read()
# Split at the second KOL marker
parts = kol_tang.split("─── 小浣熊1230 ───")
tang_content = parts[0].strip() if len(parts) > 1 else kol_tang.strip()
xiong_content = ("─── 小浣熊1230 ───\n" + parts[1]).strip() if len(parts) > 1 else ""

send_card("唐史主任司马迁 观点", tang_content[:6000], "wathet")

# Card 7: KOL - 小浣熊1230
if xiong_content:
    send_card("小浣熊1230 观点", xiong_content[:6000], "wathet")

# Card 8: RSS news
rss = open('/tmp/fund_data/_rss_news.txt').read()
send_card("隔夜赛道要闻", rss[:6000], "grey")

print("All extra cards done!")
