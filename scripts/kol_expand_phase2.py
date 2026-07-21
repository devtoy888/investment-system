#!/usr/bin/env python3
"""Phase 2: Expand ALL 3 KOLs to ~80-116 posts + verification"""
import sys, json, time, re
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import CREDENTIAL_FILE
import requests

# Load existing data
p0 = json.loads(open('/tmp/kol_phase0_raw.json').read())
p1 = json.loads(open('/tmp/kol_phase1_p2p3.json').read())

def merge_posts(lists):
    seen = set()
    all_p = []
    for lst in lists:
        for p in lst:
            if p['id'] not in seen:
                seen.add(p['id'])
                all_p.append(p)
    all_p.sort(key=lambda x: x['created_at'], reverse=True)
    return all_p

NAMES = {'2014433131':'唐史主任司马迁','5044466342':'IT精英带你养基','6114912545':'小浣熊1230'}
TARGETS = {'2014433131':100, '5044466342':80, '6114912545':80}

# Build known posts so far
known = {}
for uid in NAMES:
    known[uid] = merge_posts([
        p0.get(uid,{}).get('posts',[]),
        p1.get(uid,{}).get('posts',[])
    ])

# Credential
cred = json.loads(CREDENTIAL_FILE.read_text())
cookies = cred.get('cookies', {})
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://weibo.com/",
    "X-Requested-With": "XMLHttpRequest",
}

new_posts = {}

for uid in NAMES:
    name = NAMES[uid]
    current_n = len(known[uid])
    target = TARGETS[uid]
    needed = target - current_n
    
    print(f"\n═══ {name}: 当前{current_n}条, 目标{target}, 需{needed}条 ═══")
    
    if needed <= 0:
        print(f"  ✅ 已达目标, 跳过")
        new_posts[uid] = []
        continue
    
    all_new = []
    # For IT精英, we only pulled pages 1-3 (60 posts), so start at page 4
    # For others, we already pulled more in phase2
    page = 4
    if uid in ('2014433131', '6114912545'):
        # These were already expanded in previous phase2 run
        # But run again to verify we can get more
        pass

    while len(all_new) < needed:
        try:
            r = requests.get(
                "https://weibo.com/ajax/statuses/mymblog",
                params={"uid": uid, "page": str(page), "feature": "0"},
                cookies=cookies, headers=headers, timeout=15
            )
            data = r.json()
            if data.get("ok") != 1:
                print(f"  Page {page}: ok={data.get('ok')} → 停止")
                break
            
            items = data.get("data", {}).get("list", [])
            if not items:
                print(f"  Page {page}: 空页 → 停止")
                break
            
            for p in items:
                text = p.get("text_raw", p.get("text", ""))
                text = re.sub(r'<[^>]+>', '', text)
                all_new.append({
                    'id': p.get('id',''),
                    'mblogid': p.get('mblogid',''),
                    'created_at': p.get('created_at',''),
                    'text': text[:500],
                    'reposts_count': p.get('reposts_count',0),
                    'comments_count': p.get('comments_count',0),
                    'attitudes_count': p.get('attitudes_count',0),
                })
            
            existing_ids = set(p['id'] for p in known[uid])
            new_ids = set(p['id'] for p in all_new)
            overlap = existing_ids & new_ids
            overlap_pct = round(len(overlap)/len(all_new)*100) if all_new else 0
            
            print(f"  Page {page}: {len(items)}条 (累计新{len(all_new)}, 重叠{overlap_pct}%)")
            
            if overlap_pct > 50:
                print(f"  ⚠️ 重叠率>50%, 可能已到边界, 停止")
                break
            
            page += 1
            if page > 25:
                break
        except Exception as e:
            print(f"  Page {page} 失败: {e}")
            break
        time.sleep(2)
    
    new_posts[uid] = all_new
    print(f"  ✅ 新增采集: {len(all_new)}条")

# Merge everything
final_data = {}
for uid in NAMES:
    name = NAMES[uid]
    all_sources = [
        p0.get(uid,{}).get('posts',[]),
        p1.get(uid,{}).get('posts',[])
    ]
    if uid in new_posts and new_posts[uid]:
        all_sources.append(new_posts[uid])
    
    final_posts = merge_posts(all_sources)
    final_data[uid] = {'name': name, 'posts': final_posts}
    
    dates = [p['created_at'] for p in final_posts[:1]] + [p['created_at'] for p in final_posts[-1:]]
    
    print(f"\n📊 {name}: **{len(final_posts)}条**")
    if len(dates) >= 2:
        print(f"   时间: {dates[-1][:10]} ~ {dates[0][:10]}")

# Save
outpath = '/tmp/kol_phase2_final.json'
json.dump(final_data, open(outpath,'w'), ensure_ascii=False, indent=2)
print(f"\n✅ Phase 2 -> {outpath}")
