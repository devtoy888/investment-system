# Conversational KOL Analysis — 内容结构与交付规范

## 适用场景

用户直接在对话中要求分析KOL观点、询问"怎么办"时使用。**区别于**预采集脚本的自动推送。

## 格式铁律

- **禁止**纯文本回复 + markdown表格混合 → 用户明确反馈"太难阅读"
- **必须使用** `send_card_with_tables()`（底层 `_build_card_from_content` → `_parse_table_block`）将GFM表格转为飞书原生 `table` 组件
- **禁止**在卡片 `markdown` 元素内写GFM表格 → 飞书不渲染

## 内容结构（4步法）

| 步骤 | 卡片主题 | 颜色模板 | 内容 |
|:----|:--------|:--------:|:----|
| 1 | 当前持仓/市场数据 | indigo | 拉用户持仓基金今日估值 + 核心指数行情。用数据说话，不猜测。 |
| 2 | KOL完整逻辑链 | wathet | 拉最近3-7天帖子，按时间线排列，证明KOL判断是否一致。一致=可靠，矛盾=警告。 |
| 3 | 具体答案+核心理由 | green | 第一句就回答(持有/观望/买/卖)。后续给≤3条核心逻辑，每条对应KOL原话+当前数据。 |
| 4 | 自检清单/触发条件 | purple | 什么条件下才应该改变方向。让用户自己对照检查，而不是替他决策。 |

## 核心原则

1. **先给结论，再给依据** — 用户不想看长篇推理过程
2. **KOL观点必须跨帖验证** — 不要只引用今天一条帖。跨3-7天的帖子才能判断一致性
3. **必须拉用户实际持仓数据** — 空谈KOL观点没有意义，必须结合具体基金估值
4. **自检清单是关键** — 用户要的是判断框架，不是算命式结论

## 工具代码示例

```python
import sys, os, json, requests, dotenv

# 方式A：用 send_feishu_cards.py（推荐）
sys.path.insert(0, '/opt/data/scripts')
from send_feishu_cards import send_card_with_tables
send_card_with_tables("卡片标题", "markdown+GFM表格", "indigo")

# 方式B：直接调用 sitecustomize（需要发到DM而非群组时）
sys.path.insert(0, '/opt/data/.feishu-deps')
import sitecustomize as sc
card_json = sc._build_card_from_content(content)
parsed = json.loads(card_json)
parsed['header']['template'] = 'indigo'
# ... send via Feishu Open API to open_id
```

## 避坑

- 不要用 `send_card()`（纯markdown模式）发含表格的内容
- 不要全部塞一张卡片 → 拆成3-4张独立卡片，每张聚焦一个主题
- 必须解读KOL原话 + 关联到用户持仓，不要只复制粘贴
