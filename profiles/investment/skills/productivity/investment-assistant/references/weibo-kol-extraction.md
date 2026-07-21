# 微博 KOL 信号实时提取 — 实操要点（2026-07 验证）

主任微博 uid = `2014433131`（唐史主任司马迁）。以下从本会话实测，避免重复踩坑。

## 数据源层级（按可靠性）

1. **实时拉取（首选）**：`/opt/data/scripts/fund_tools.py` → `get_user_weibos(uid, count)`
   - 凭证文件：`$HOME/.config/weibo-cli/credential.json`（CLI 的 HOME = `/opt/data/home`）
   - **必须带环境变量** `HOME=/opt/data/home` 才能找到凭证，否则报"凭据文件不存在"
   - API 返回 `ok=1` 正常；`ok=-100` = **会话过期，需重新登录**
2. **归档文件（次选/补历史）**：
   - `/opt/data/fund_system_data/signals.jsonl` — 系统抓取，但**同一天同内容会被重复抓取 6~7 次**（202条原始 → 去重后仅32条独特）。直接用会虚高频率。
   - ✅ **真正完整的原文在 briefs 的 `kol_posts` 字段**：`morning-briefs.jsonl` / `noon-briefs.jsonl` / `closing-reviews.jsonl` 中每条含 `kol_posts: {uid: {name, posts:[{id, mblogid, created_at, text}]}}`
   - `created_at` 是**英文格式** `Fri Jun 26 10:44:37 +0800 2026`，解析用 `datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')`，**不能**用 `startswith('2026-06')` 前缀匹配（会漏掉全部）。

## 去重 + 赛道提取标准流程

```python
from pathlib import Path
from datetime import datetime
from collections import Counter

data_dir = Path("/opt/data/fund_system_data")
posts = []
for f in ['morning-briefs.jsonl','noon-briefs.jsonl','closing-reviews.jsonl']:
    for l in (data_dir/f).read_text().split('\n'):
        if not l.strip(): continue
        d = json.loads(l)
        for uid, info in d.get('kol_posts', {}).items():
            if '唐史主任' in str(info.get('name','')):
                for p in info.get('posts', []):
                    posts.append({'date': p.get('created_at',''), 'text': p.get('text','')})

def parse(s):
    try: return datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')
    except: return None

parsed = [(parse(p['date']), p['text']) for p in posts if parse(p['date'])]
jj = [(dt,t) for dt,t in parsed if dt.year==2026 and dt.month in (6,7)]
jj.sort(key=lambda x: x[0])
# 去重（同内容前缀50字）
seen=set(); unique=[(dt,t) for dt,t in jj if not (t[:50] in seen or seen.add(t[:50]))]
```

赛道关键词映射到提取函数，统计去重后频次（不是原始条数）。

## 会话过期 → 重新登录

1. 后台跑：`docker exec -e HOME=/opt/data/home -w /opt/data/scripts hermes-main python3 /opt/data/scripts/weibo_login_direct.py`
2. 脚本打印 `QR_READY` 并把二维码存到 `/opt/data/image_cache/weibo_qr_login.png`
3. 把该 PNG 以 `MEDIA:` 发用户扫码 → 脚本轮询 `LOGIN_OK` → 写回 `credential.json` → 验证 `VERIFY=1`
4. 二维码有效期约 4 分钟（脚本等 240s）。

## 本会话交叉验证结论（供参考）

- 主任 6月(17条)+7月(37条) 去重后共 54 条独特微博。
- 赛道频次：科技/科创50 > 流动性 > AI/人工智能 > 长鑫/IPO > 业绩基本面 > 半导体。**从未提过**机器人/商业航天/卫星/医药/新能源/消费/红利。
- 关键观点：科技牛市高波回调，长鑫缴款后打开空间；"龙头爆亏的行业不要碰"；自己也在"减杂毛降融资"。
- 含义：主任框架 = 纯科技（科创50/半导体/AI），与"加医药/机器人/卫星"分散思路正交——后者是用户独立判断，主任不反对也不支持。
