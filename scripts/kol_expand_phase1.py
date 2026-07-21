#!/usr/bin/env python3
"""Phase 1: Expand KOL data - pull page 2 (30 posts each)"""
import sys, json, time
sys.path.insert(0, '/opt/data/scripts')

# Load existing setup
from fund_tools import CREDENTIAL_FILE, KOLS, get_user_weibos as gw

# Load Phase 0 data
phase0 = json.loads(open('/tmp/kol_phase0_raw.json').read())

# For each KOL, get page 2 (posts beyond the first 20)
results = {}
for uid, name in KOLS.items():
    print(f'\n═══ {name} ({uid}) ═══')
    
    # We need to get page 2. The get_user_weibos function uses page=1.
    # Let's directly call the API with page=2
    if not CREDENTIAL_FILE.exists():
        print(f'  ❌ 凭证不存在')
        results[uid] = {'name': name, 'posts': []}
        continue
    
    cred = json.loads(CREDENTIAL_FILE.read_text())
    cookies = cred.get('cookies', {})
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://weibo.com/",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    import requests as req
    page2_data = []
    page3_data = []
    
    # Get page 2 (roughly posts 21-40)
    try:
        r = req.get(
            "https://weibo.com/ajax/statuses/mymblog",
            params={"uid": uid, "page": "2", "feature": "0"},
            cookies=cookies, headers=headers, timeout=15
        )
        data = r.json()
        if data.get("ok") == 1:
            page2_data = data.get("data", {}).get("list", [])
            print(f'  Page 2: {len(page2_data)}条')
        else:
            print(f'  Page 2: ok={data.get("ok")}')
    except Exception as e:
        print(f'  Page 2 失败: {e}')
    
    time.sleep(2)
    
    # Get page 3 (roughly posts 41-60)
    try:
        r = req.get(
            "https://weibo.com/ajax/statuses/mymblog",
            params={"uid": uid, "page": "3", "feature": "0"},
            cookies=cookies, headers=headers, timeout=15
        )
        data = r.json()
        if data.get("ok") == 1:
            page3_data = data.get("data", {}).get("list", [])
            print(f'  Page 3: {len(page3_data)}条')
        else:
            print(f'  Page 3: ok={data.get("ok")}')
    except Exception as e:
        print(f'  Page 3 失败: {e}')
    
    # Format posts like get_user_weibos does
    import re
    posts_p2 = []
    for p in (page2_data + page3_data):
        text = p.get("text_raw", p.get("text", ""))
        text = re.sub(r'<[^>]+>', '', text)
        posts_p2.append({
            'id': p.get('id', ''),
            'mblogid': p.get('mblogid', ''),
            'created_at': p.get('created_at', ''),
            'text': text[:500],
            'reposts_count': p.get('reposts_count', 0),
            'comments_count': p.get('comments_count', 0),
            'attitudes_count': p.get('attitudes_count', 0),
        })
    
    results[uid] = {'name': name, 'posts': posts_p2}
    time.sleep(3)

# Save
outpath = '/tmp/kol_phase1_p2p3.json'
with open(outpath, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'\n✅ Phase 1 data -> {outpath}')

# Stats
for uid, name in KOLS.items():
    existing = len(phase0.get(uid, {}).get('posts', []))
    new_posts = len(results.get(uid, {}).get('posts', []))
    print(f'  {name}: 已有{existing}条 + 新增{new_posts}条 = {existing + new_posts}条')
