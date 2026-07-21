# QQ Bot 推送消息合并规范（2026-07-15）

> 用户反馈：早报刻意分了很多段消息发送，一个早报12条消息太多了

## 核心原则：按长度合并，不按内容主题分拆

`send_qq_bot.py` 中的 `send_markdown_in_chunks()` 函数负责拆分推送。

### 旧行为（已废弃）

以 `═══════════════════════════════════` 分隔符切分内容 → 每个 section 独立成一条QQ消息 → 早报12+条

### 新行为

合并所有内容为连续消息，仅按QQ 3800字符限制分段 → 早报2-3条

打包发送仅处理qq长度限制，不按内容主题分段发送。

### 规则

1. 去掉状态行（`OK `/`FAIL `/`All done`/`Morning cards done`/`————`）
2. 保留 `═══════════════════════════════════` 分隔线作为视觉分隔，不作为消息切分点
3. 仅开头加 `## 📚 {title}` 标题头
4. 超长时按段落边界切分，多段时加接续标记（`📎 接上条` / `📎 续下条`）
5. 切分点在段落边界，不截断表格或句子

## 代码位置

`/opt/data/scripts/send_qq_bot.py` line 52-95, `send_markdown_in_chunks()`函数。

## 覆盖范围

早/午/收三种推送共享该函数，一处修改三份同步受益。

| 推送 | 脚本 | 调用点 |
|:----|:----|:-------|
| 财经早餐 | `run_morning.py` line 33 | `send_markdown_in_chunks("财经早餐", card_output)` |
| 盘中直击 | `run_noon.py` line 33 | `send_markdown_in_chunks("盘中直击", card_output)` |
| 收盘复盘 | `run_closing.py` line 33 | `send_markdown_in_chunks("收盘复盘", card_output)` |
