# QQ Bot Markdown Rendering — Diagnosis & Fix (CORRECTED 2026-07-15)

Verified while building the OpenRouter free-model monitor
(`/opt/data/scripts/openrouter_free_monitor.py`). The earlier "account-dependent"
conclusion in this file was WRONG and is corrected below.

## The symptom
A cron task with `deliver=qqbot` (default profile) pushed a message written in
markdown (`#`/`##`, `**bold**`, `-` lists, `<font>` tags). The user saw **raw plain
text** — every markdown symbol displayed literally.

A separate message pushed through `send_qq_bot.py` (investment profile, app_id
`1905190887`, OPENID `C40A1DEC...`) rendered as **proper markdown** on the same
client.

## Root cause (proven, then CORRECTED)
1. Both profiles have identical `qqbot.markdown_support: true`.
2. Hermes adapter `_build_text_body` (gateway/platforms/qqbot/adapter.py ~L2737):
   when `markdown_support` is true it sends
   `{"markdown": {"content": <text>}, "msg_type": MSG_TYPE_MARKDOWN}` — a valid
   custom-markdown payload per official docs.
3. So the PAYLOAD is correct markdown.
4. **The default bot's real app_id is `1904452472` (from `.env` `QQ_APP_ID`), NOT
   `1905192352`.** `1905192352` is the **llm-wiki** profile's bot — a different
   account. The earlier "default account degrades" claim was caused by this
   misidentification (the llm-wiki gateway log was read instead of the default one).
5. **`1904452472` DOES render markdown** when you POST a raw
   `{"msg_type":2,"markdown":{"content":...}}` to the QQ REST API directly
   (proven: bare payload with/without `msg_seq` both rendered fine on the client).
6. **The degradation happens ONLY through Hermes' `deliver=qqbot` cron delivery
   path.** The bot account and the markdown syntax are both fine; the cron
   delivery linkage downgrades it. The investment bot renders because
   `send_qq_bot.py` calls the QQ REST API directly, bypassing the cron path.

**Conclusion / Fix:** to get markdown on QQ from a cron script, send it yourself via
the REST API (reusable helper `scripts/qq_markdown_send.py`) and set the cron task
`deliver=local` so Hermes does not deliver a second, degraded copy.

## Official syntax that DOES render (when delivered correctly)
From https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/type/markdown.html
(2026-04-23 update: custom markdown open to ALL bots, no template application needed):
- `#` / `##` titles
- `**加粗**`, `_斜体_`, `*斜体*`, `***加粗斜体***`, `~~删除线~~`
- `[文字](url)` links; `<https://...>` bare links
- `![alt #Wpx #Hpx](url)` images (public URL)
- `1.` ordered / `-` unordered lists (nest with 4-space indent)
- `>` blockquote (multi-line)
- `***` horizontal rule
- **`<font color="info|warning|comment">` is NOT in the official syntax and does NOT
  render** — it shows as literal text. Do not use it.

## Direct-send template (the working fix)
`scripts/qq_markdown_send.py` provides `send_markdown_to_default_qq(text)`:
- reads `QQ_APP_ID` / `QQ_CLIENT_SECRET` from `.env` (never hardcodes)
- POSTs `{"msg_type":2,"markdown":{"content":text}}` to
  `https://api.sgroup.qq.com/v2/users/<openid>/messages`
- splits on `\n***\n` so each chunk < 3800 chars
- target openid defaults to the default-profile QQ DM chat_id

In a cron `--script`, call it after building the report, and set the task
`deliver=local`.

## Decision rule
- Unknown delivery path → send ONE real test via the actual path you'll use; let the
  user confirm rendered vs plain text BEFORE investing in markdown layout.
- If `deliver=qqbot` degrades but a direct REST call renders, the fix is to **bypass
  the cron delivery path** (direct send + `deliver=local`), not rewrite the markdown.

## Two-account pitfall (still true, corrected ids)
- default bot: app_id `1904452472` (from `.env`)
- investment bot: app_id `1905190887`, hardcoded in `/opt/data/scripts/send_qq_bot.py`
  (OPENID `C40A1DEC1124496F9034304E31063FB7`)
- llm-wiki bot: app_id `1905192352` (separate account, not the default one)
Calling the hardcoded `send_qq_bot.py` from a default-profile task mis-delivers to the
investment user's QQ. To reach the default user's DM, either use the direct-send
helper (reads `.env`) or `deliver=qqbot` on a default-profile cron task.

## Plain-text-beautiful fallback template (still useful if you want plain text)
Refined 2026-07-15 — emoji conclusion labels read cleaner than `[优势]`/`[注意]`
text labels, and 🅰🅱 badges + 2-space indent give cleaner card hierarchy than
`【N】` numbering.
```
🆕 OpenRouter 新限免模型提醒
🕐 检测时间：2026-07-15 17:57（北京时间）
⚠️ 演示样例（基于当前真实限免数据，非真实新增）
📊 共发现 2 个新上线 / 新进入限免期的免费模型
══════════════════════════════════
🅰  tencent/hy3:free
    名称：Tencent: Hy3 (free)

    ✨ 优点
      · 上下文窗口：256K（主力 DeepSeek V4 Flash 为 1M）
      · 模态：纯文本
      · 规模：295B 总参 / 21B 激活
      · 免费截止：2026-07-21 08:00（之后恢复计费或下线）

    ⚖️ 与主力 deepseek/deepseek-v4-flash 对照
      ① 上下文：本模型 256K vs 主力 1M → ⚠️ 更小（约 25% 主力）
      ② 价格：本模型 免费(限免期) vs 主力 ~$0.098/M 输入 → ✅ 限免期零成本，⚠️ 到期恢复计费/下线
      ③ 模态：本模型 纯文本 vs 主力 纯文本 → ➖ 持平
══════════════════════════════════
🅱  <model id> ...
══════════════════════════════════
📌 监测说明：仅通知带过期日的限时免费模型（如 hy3:free）；常驻免费池不重复提醒。
```
Conventions:
- `═══` ASCII divider per section; `🅰 🅱 🅲 …` badge per item (5 max, fall back to
  `【N】`); 2-space indent under each badge for the body; `✨`/`⚖️`/`📌` emoji markers.
- `·` bullets for merits; `① ② ③ ④` numbering for comparison rows.
- **Conclusion labels use EMOJI, not text**: `✅` = advantage, `⚠️` = caveat,
  `➖` = neutral/equal.
- **Drop English vendor description sentences** — parse structured facts instead
  (e.g. regex `(\d+\.?\d*)\s*B-parameter` / `(\d+\.?\d*)\s*B active` → "295B 总参 /
  21B 激活"). Long English blurbs look ugly in a Chinese report.
- Never use `<font>` (non-standard, shows literally). No `#`/`**`/`` ` `` markdown-only
  syntax (will show literally on degraded delivery paths).
