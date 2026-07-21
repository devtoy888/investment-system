#!/usr/bin/env python3
"""
List all Feishu/Lark chats the bot can see, with chat_id, name, type, and member count.

Use this after setting up the Feishu platform to find a Chat ID for
FEISHU_HOME_CHANNEL (cron/notification delivery target).

Usage:
    python3 /opt/data/skills/autonomous-ai-agents/gateway-platform-troubleshooting/scripts/list-feishu-chats.py

Dependencies:
    - no extra packages required (stdlib only)
    - The .env file with FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_DOMAIN
"""
import json
import os
import sys
import urllib.request

# --- Config ---
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".env")
# ../
# Or let the caller pass HERMES_HOME
hermes_home = os.environ.get("HERMES_HOME", "")
if hermes_home:
    dotenv_path = os.path.join(hermes_home, ".env")
else:
    # Fall back to common locations
    for candidate in ["/opt/data/.env", os.path.expanduser("~/.hermes/.env")]:
        if os.path.exists(candidate):
            dotenv_path = candidate
            break

# --- Load env ---
env = {}
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = v
else:
    print(f"ERROR: .env not found at {dotenv_path}")
    sys.exit(1)

APP_ID = env.get("FEISHU_APP_ID", "")
APP_SECRET=env.get("FEISHU_APP_SECRET", "")
DOMAIN = env.get("FEISHU_DOMAIN", "feishu")

if not APP_ID or not APP_SECRET:
    print("ERROR: FEISHU_APP_ID or FEISHU_APP_SECRET not set in .env")
    sys.exit(1)

BASE = "https://open.feishu.cn" if DOMAIN == "feishu" else "https://open.larksuite.com"

# --- Step 1: Get tenant access token ---
req = urllib.request.Request(
    f"{BASE}/open-apis/auth/v3/tenant_access_token/internal",
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    resp = json.loads(urllib.request.urlopen(req).read())
except Exception as e:
    print(f"ERROR: Auth request failed: {e}")
    sys.exit(1)

if resp.get("code") != 0:
    print(f"ERROR: Auth failed: {resp.get('msg', 'unknown')}")
    sys.exit(1)

token = resp["tenant_access_token"]
print(f"✓ Authenticated (token expires in {resp.get('expire', '?')}s)")

# --- Step 2: List chats ---
req2 = urllib.request.Request(
    f"{BASE}/open-apis/im/v1/chats?page_size=50",
    headers={"Authorization": f"Bearer {token}"},
)
try:
    resp2 = json.loads(urllib.request.urlopen(req2).read())
except Exception as e:
    print(f"ERROR: List chats failed: {e}")
    sys.exit(1)

if resp2.get("code") != 0:
    print(f"ERROR: List chats failed: {resp2.get('msg', 'unknown')}")
    sys.exit(1)

items = resp2.get("data", {}).get("items", [])
print(f"\nFound {len(items)} chat(s):\n")

for i, chat in enumerate(items, 1):
    chat_id = chat.get("chat_id", "?")
    name = chat.get("name", "(unnamed)")
    chat_type = chat.get("chat_type", "?")
    chat_mode = chat.get("chat_mode", "?")
    members = chat.get("member_count", chat.get("user_count", "?"))
    owner = chat.get("owner_id", "")
    print(f"  {i}. [{chat_type}/{chat_mode}] chat_id={chat_id}")
    print(f"     Name: \"{name}\"  Members: {members}")
    if owner:
        print(f"     Owner: {owner}")
    print()

# If user provides a chat_id as argument, show full details
if len(sys.argv) > 1:
    target_id = sys.argv[1]
    detail_req = urllib.request.Request(
        f"{BASE}/open-apis/im/v1/chats/{target_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        detail_resp = json.loads(urllib.request.urlopen(detail_req).read())
        detail = detail_resp.get("data", {})
        print(f"=== Full Details for {target_id} ===")
        for key in ["name", "chat_mode", "chat_type", "owner_id", "owner_id_type",
                     "member_count", "user_count", "bot_count", "chat_status",
                     "description", "external", "tenant_key"]:
            if key in detail:
                print(f"  {key}: {detail[key]}")
    except Exception as e:
        print(f"Could not fetch details: {e}")