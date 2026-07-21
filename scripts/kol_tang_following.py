#!/usr/bin/env python3
"""Get Tang's following list from Weibo"""
import json, sys, time
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import CREDENTIAL_FILE
import requests

cred = json.loads(CREDENTIAL_FILE.read_text())
cookies = cred.get('cookies', {})
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://weibo.com/",
    "X-Requested-With": "XMLHttpRequest",
}

TANG_UID = "2014433131"

# Try different API endpoints for getting following list
endpoints = [
    f"https://weibo.com/ajax/friendships/friends?uid={TANG_UID}&page=1",
    f"https://weibo.com/ajax/friendships/friends_concern?uid={TANG_UID}&page=1",
]

all_following = []
source_endpoint = None

for url in endpoints:
    try:
        r = requests.get(url, cookies=cookies, headers=headers, timeout=15)
        data = r.json()
        
        if data.get("ok") == 1:
            users = data.get("data", {}).get("friends", []) or data.get("data", {}).get("users", []) or data.get("users", [])
            total = data.get("data", {}).get("total_number", data.get("total_number", 0))
            print(f"✅ Endpoint works: {url.split('?')[0]}")
            print(f"   返回 {len(users)} 人, 总计约 {total} 人")
            
            if users:
                all_following = users
                source_endpoint = url
                break
        else:
            print(f"❌ {url.split('?')[0]}: ok={data.get('ok')} msg={data.get('msg','')}")
    except Exception as e:
        print(f"❌ {url.split('?')[0]}: {e}")
    time.sleep(1)

# If first page worked, try to get more pages
if source_endpoint and all_following:
    base_url = source_endpoint.split('&page=')[0]
    for page in range(2, 6):  # Try pages 2-5
        try:
            r = requests.get(f"{base_url}&page={page}", cookies=cookies, headers=headers, timeout=15)
            data = r.json()
            if data.get("ok") == 1:
                users = data.get("data", {}).get("friends", []) or data.get("users", [])
                if not users:
                    break
                all_following.extend(users)
                print(f"  Page {page}: +{len(users)}人 (累计{len(all_following)})")
            else:
                break
        except Exception as e:
            print(f"  Page {page}: {e}")
            break
        time.sleep(1)

# If we got following data, analyze it
if all_following:
    print(f"\n{'='*70}")
    print(f"📋 唐史主任关注了 {len(all_following)} 人")
    print(f"{'='*70}")
    
    # Sort by followers count (descending) to find the most notable ones
    followers_sorted = sorted(all_following, key=lambda u: u.get('followers_count', 0), reverse=True)
    
    print(f"\n📊 按粉丝数排序 TOP 30:")
    print(f"{'排名':4s} {'昵称':20s} {'粉丝':10s} {'关注':8s} {'微博':8s} {'简介'}")
    print("-"*80)
    for i, u in enumerate(followers_sorted[:30]):
        name = u.get('screen_name', '?')
        desc = (u.get('description', '') or '')[:40].replace('\n',' ')
        followers = u.get('followers_count', 0)
        friends = u.get('friends_count', 0)
        statuses = u.get('statuses_count', 0)
        verified = u.get('verified', False)
        vtype = u.get('verified_type', -1)
        
        # Format counts
        def fmt(n):
            if n >= 10000000: return f"{n/10000000:.1f}千万"
            if n >= 10000: return f"{n/10000:.1f}万"
            return str(n)
        
        mark = '🟢' if verified else '⚪'
        print(f"  {i+1:2d}. {mark} {name:20s} {fmt(followers):>10s} {fmt(friends):>8s} {fmt(statuses):>8s} {desc}")
    
    # Save all following data
    out = '/tmp/tang_following.json'
    # Keep only essential fields
    simplified = []
    for u in all_following:
        simplified.append({
            'id': u.get('id', u.get('idstr', '')),
            'screen_name': u.get('screen_name', ''),
            'description': (u.get('description', '') or '')[:200],
            'followers_count': u.get('followers_count', 0),
            'friends_count': u.get('friends_count', 0),
            'statuses_count': u.get('statuses_count', 0),
            'verified': u.get('verified', False),
            'verified_type': u.get('verified_type', -1),
            'verified_reason': u.get('verified_reason', '') or '',
            'gender': u.get('gender', ''),
            'profile_url': u.get('profile_url', ''),
        })
    
    json.dump(simplified, open(out,'w'), ensure_ascii=False, indent=2)
    print(f"\n✅ 保存到 {out} ({len(simplified)}人)")
    
else:
    print("\n❌ 无法获取关注列表，尝试其他方法")
