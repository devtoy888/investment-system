#!/usr/bin/env python3
"""Pull older pages for Tang (to get historical data for accuracy verification)"""
import sys, json, time, re
sys.path.insert(0, '/opt/data/scripts')
from fund_tools import CREDENTIAL_FILE
import requests

cred = json.loads(CREDENTIAL_FILE.read_text())
cookies = cred.get('cookies', {})
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://weibo.com/",
    "X-Requested-With": "XMLHttpRequest",
}

# Load existing
p0 = json.loads(open('/tmp/kol_phase0_raw.json').read())
p1 = json.loads(open('/tmp/kol_phase1_p2p3.json').read())

def merge_posts(lists):
    seen = set(); all_p = []
    for lst in lists:
        for p in lst:
            if p['id'] not in seen:
                seen.add(p['id']); all_p.append(p)
    all_p.sort(key=lambda x: x['created_at'], reverse=True)
    return all_p

existing_tang = merge_posts([
    p0.get('2014433131',{}).get('posts',[]),
    p1.get('2014433131',{}).get('posts',[])
])

print(f"唐史主任当前已有: {len(existing_tang)}条")

# Pull pages 7-15 for Tang to get older content
all_new = []
for page in range(7, 16):
    try:
        r = requests.get(
            "https://weibo.com/ajax/statuses/mymblog",
            params={"uid": "2014433131", "page": str(page), "feature": "0"},
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
                'id': p.get('id',''), 'mblogid': p.get('mblogid',''),
                'created_at': p.get('created_at',''), 'text': text[:500],
                'reposts_count': p.get('reposts_count',0),
                'comments_count': p.get('comments_count',0),
                'attitudes_count': p.get('attitudes_count',0),
            })
        
        # Show date range of this page
        dates_str = [p.get('created_at','')[:11] for p in items]
        print(f"  Page {page}: {len(items)}条 ({dates_str[-1]} ~ {dates_str[0]}) 累计新{len(all_new)}")
        
        time.sleep(2)
    except Exception as e:
        print(f"  Page {page} 失败: {e}")
        break

# Merge with existing
if all_new:
    full_tang = merge_posts([existing_tang, all_new])
    print(f"\n✅ 唐史主任总计: {len(full_tang)}条 (新增{len(all_new)}条)")
    
    # Date range
    import datetime as dtm
    from datetime import timezone
    dates = []
    for d in [p['created_at'] for p in full_tang]:
        try: dates.append(dtm.datetime.strptime(d, '%a %b %d %H:%M:%S %z %Y'))
        except: pass
    
    if dates:
        # Sort chronologically
        dates.sort()
        print(f"   时间范围: {dates[0].strftime('%Y-%m-%d')} → {dates[-1].strftime('%Y-%m-%d')}")
        print(f"   总跨度: {max(1,(dates[-1]-dates[0]).days)}天")
    
    # Save full dataset
    json.dump({'2014433131': {'name':'唐史主任司马迁','posts':full_tang}},
              open('/tmp/kol_tang_extra.json','w'), ensure_ascii=False, indent=2)
    print(f"   -> /tmp/kol_tang_extra.json")
else:
    print("❌ 未获取到新数据")
    # Fall back to existing
    json.dump({'2014433131': {'name':'唐史主任司马迁','posts':existing_tang}},
              open('/tmp/kol_tang_extra.json','w'), ensure_ascii=False, indent=2)
    print(f"   使用已有数据 -> /tmp/kol_tang_extra.json")
