# Weibo Comment Analysis for KOL Signal Enhancement

> Discovered and prototyped 2026-06-26. Triggered analysis pattern, NOT daily scraping.

## Why Comments Matter

KOLs deliberately omit specific sector/position details from public posts (liability reasons, follower management). However, their comment sections reveal:

| What | Example (唐史主任 2026-06-26) | Value |
|------|------------------------------|-------|
| **Sectors users ask about** | "锂电到底怎么了？基本面没有拉胯" | Market attention signal |
| **Author's unreleased views** | 主任 replied: "熬一熬，等出业绩" | Direct investment advice hidden in comments |
| **Follower return verification** | "本季度翻倍" × 4 users | Validates the KOL's direction is working |
| **Sentiment divergence** | 主任 says "小亏" but followers say "翻倍无敌" | Froth indicator when followers are more bullish than the KOL |

## Trigger Condition

Only pull comments when a **signal-class post** is detected. Signal-class means the post text contains keywords from the KOL's known SIGNALS dictionary (in fund_tools.py):

```
SIGNAL_TRIGGERS = ['融资仓', '加仓', '补仓', '右侧', '触底', '底部', '接']
```

Do NOT pull comments on routine posts (daily chat, retweets, celebrations).

## API Details

**Working endpoint:**
```
GET https://weibo.com/aj/v6/comment/big
Params: ajwvr=6, id={post_id}, from=singleWeiBo, page={n}
Headers: same as get_user_weibos() — needs auth cookies
```

**Failed endpoint (do not retry):**
```
https://weibo.com/ajax/statuses/buildComments  → returns "参数错误"
```

The working endpoint returns HTML, not JSON. Parse with regex:
```python
# Extract comment blocks
blocks = re.findall(
    r'node-type="root_comment"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*<div[\s>]',
    html, re.DOTALL
)
for block in blocks:
    # User name
    users = re.findall(r'<a[^>]*>([^<]+)</a>', block)
    user = users[1] if len(users) > 1 else users[0]
    # Text content
    texts = re.findall(r'WB_text[^>]*>(.*?)</div>', block, re.DOTALL)
    text = re.sub(r'<[^>]+>', '', texts[0]).strip() if texts else ''
    # Whether author replied
    has_reply = '唐史主任司马迁' in block
```

## Analysis Protocol (3-Tier Extraction)

When analyzing comments from a signal post, extract in order:

### Tier 1: Author Replies (Highest Weight)
The KOL's own comment replies contain direct investment opinions not in the main post. These are the highest-value signal from comments.

- *Example:* "熬一熬，等出业绩，前提是你买对业绩了" → implies lithium battery sector needs patience, stock picking matters
- *Example:* "有得赚时多赚点，跌起来好有钱亏" → risk management philosophy

### Tier 2: High-Liked Sector Questions
Comments asking about specific sectors with high like counts indicate what the audience is thinking about.

- Filter: `likes > 5` AND `text contains 板块/个股/ETF/基金/赛道/code`
- These reveal what sectors the market is watching

### Tier 3: Follower Return Reports
Follower self-reports of profit/loss serve as crowd-sourced verification of the KOL's direction.

- Filter: `text contains 赚/翻倍/亏/回本/跌/涨`
- Ratio of positive:negative reports indicates how well the KOL's strategy is working in real-world portfolios

## CRITICAL: Cross-Verification Rule

**Do NOT take comment self-reports at face value.** The user explicitly corrected this: "评论里比如有人说挣了翻倍，也要以实际证据交叉验证，如果有人乱说呢。"

| Claim Type | Trust Level | Handling |
|------------|:-----------:|----------|
| KOL's own reply in comments | 🔴 High | Quote directly in push — it's a verifiable quote. Attribute as "[评论区] 主任回复" |
| Sector/stock names mentioned | 🟡 Medium | Use as signal for **what to verify**, not as confirmed fact. Cross-check with actual price/index data |
| Personal return claims ("翻倍了", "亏了多少") | 🟢 Low | **Do NOT include specific numbers in push.** Only use aggregate direction ("评论区多人反映科技方向盈利") when 3+ independent users report the same direction |

**Implementation rule for cron agent:** When reading `_kol_comment_insights.txt`:
- KOL's own replies → quote with source label
- Sector mentions → preface with "评论中发现关注方向" and cross-check
- Personal returns → aggregate only: "评论区情绪偏乐观/悲观", never quote a specific user's claim

## What to Filter (Noise)

Skip these comment types — they add no analytical value:
- Pure praise: "主任厉害", "无敌", "666"
- Emoji-only replies
- Off-topic personal questions (age, family, etc.)
- Repost/retweet references without original comment

## Cost Assessment

- API call: free (uses existing Weibo auth)
- AI analysis: ~500-1000 tokens per 20 comments (negligible)
- Time: ~3-5 seconds per fetch + analysis
- Value: medium-high for signal posts, zero for routine posts

**Verdict from 2026-06-26 prototype:** Worth doing as triggered pattern. Not worth daily scraping.
