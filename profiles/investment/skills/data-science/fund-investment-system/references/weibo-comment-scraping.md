# Weibo Comment Scraping Reference

## Endpoint

```
GET https://weibo.com/aj/v6/comment/big
Params: ajwvr=6, id={post_id_numeric}, from=singleWeiBo, page={page}
Auth: Desktop API cookies (same credential.json as get_user_weibos)
Response: JSON with `data.html` containing HTML comment blocks
```

## Post ID Source

The initial post ID comes from `get_user_weibos()` in `fund_tools.py`,
which returns posts with `id` (numeric, e.g. 5314114466875015) and `mblogid` (string, e.g. R5VbgsQvl).

**Use the numeric `id`, NOT `mblogid`.**

## HTML Parsing

```python
blocks = re.findall(
    r'node-type="root_comment"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*<div[\s>]',
    html, re.DOTALL
)
for block in blocks:
    users = re.findall(r'<a[^>]*>([^<]+)</a>', block)
    user = users[0]
    texts = re.findall(r'WB_text[^>]*>(.*?)</div>', block, re.DOTALL)
    text = re.sub(r'<[^>]+>', '', texts[0]).strip()
    has_reply = '唐史主任司马迁' in block
    likes = re.findall(r'like_counts["\']:\s*(\d+)', block)
    likes_count = int(likes[0]) if likes else 0
```

## Signal Trigger

Only fetch comments when ALL conditions met:
1. Post from 唐史主任司马迁 (uid=2014433131)
2. Post text contains a signal keyword
3. Comments count >= 30

```python
COMMENT_TRIGGER_KEYWORDS = [
    '融资仓', '加仓', '补仓', '接货', '接筹',
    '右侧', '底部', '触底', '反弹', '抄底',
]
```

## Implementation

Function: `get_weibo_comments(post_id, count=20)` in `/opt/data/scripts/fund_tools.py`
Output: `_kol_comment_insights.txt` in `/tmp/fund_data/`

## Agent Usage Rules

1. 主任回复可直接引用（原文可查，标注"评论区回复"）
2. 板块方向需用行情数据交叉验证
3. 个人收益自报不得作为推送内容
4. 单一人说不可信；5+不同ID同方向 = 共识信号
