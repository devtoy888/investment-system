# QQ Bot 消息推送 — 合并策略

## 问题：消息过多

早报原逻辑在 `send_morning_cards.py` 中每调用一次 `send_card_with_tables()` 就输出一个 `═══════════════════════════════════` 分隔段，`run_morning.py` 中的 `send_markdown_in_chunks()` 以分隔符为界将每个 card 独立成一条QQ消息 → **8-12条**。

## 修复方案

在 `run_morning.py` → `send_qq_bot.py` 的 `send_markdown_in_chunks()` 中：

1. **不去掉分隔符** — 保留作为视觉分段，但不作为消息切分点
2. **合并所有 card 为一整条消息** — 用一个 `## 📚 {title}` 统一标题
3. **仅按 QQ 3800 字符上限切分** — 超额时在段落边界截断
4. **过滤状态行** — 去掉 "Morning cards done!"、"OK ..." 等辅助输出
5. **加接续标记** — 多段消息标注 📎 接上条 / 📎 续下条

### 效果

| 项目 | 旧 | 新 |
|:---|:---|:---|
| 切分策略 | 按内容主题（分隔符） | 按 **3800字符上限** |
| 标题 | 每条消息一个 `## 财经早餐` | 仅开头一个 `## 📚 财经早餐` |
| 状态行 | 混入消息 | 自动过滤 |
| 消息数（8板块） | **8条** | **2条** |

## 代码位置

- `send_qq_bot.py` — `send_markdown_in_chunks()` 函数（早/午/收三份脚本共用）
- `run_morning.py` / `run_noon.py` / `run_closing.py` — 调用方

## QQ Bot API 限制

- 单条 markdown 消息上限：4000 字符（安全值取 3800）
- token 有效期：7200秒（含自动刷新）
- 发送间隔：0.3s
- API: `POST /v2/users/{openid}/messages` with `msg_type=2`
