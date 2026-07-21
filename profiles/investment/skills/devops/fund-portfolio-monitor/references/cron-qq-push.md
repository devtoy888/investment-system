# QQ Bot 推送架构 (Cron + send_qq_bot.py)

## 核心原则

**cron 的 deliver 不要设置为 origin 或 qqbot:Home（均 500 失败）**。
QQ 推送的唯一可靠路径：`cron deliver=local` + 脚本内部调用 `send_markdown_in_chunks()`。

## 架构图

```
┌──────────────┐     ┌────────────────────┐     ┌─────────────────┐
│ cron 调度器  │────▶│ run_morning.py     │────▶│ send_qq_bot.py  │
│ deliver=local│     │ (或 run_noon/closing)│     │                 │
│ no_agent=True│     │ 收集→格式化→推送    │     │ QQ Bot API v2   │
└──────────────┘     │ 异常 try/except 保护│     │ openid=硬编码    │
                     └────────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                  用户 QQ 收到消息
```

## Cron 配置

### 正确参数

```yaml
deliver: local           # cron 不参与推送，只存本地日志
no_agent: true           # 直接运行脚本，不走 LLM
script: run_morning.py   # 脚本路径（相对于 profiles/<name>/scripts/）
```

`deliver` 不可用值：
- `origin` → QQ Bot API 500 (`/v2/users/Home/messages`) — 路径不对
- `qqbot:Home` → 同上 500

### 脚本要求

脚本内部必须自己推 QQ，不能依赖 cron 投递：

```python
from send_qq_bot import send_markdown_in_chunks

card_output = r2.stdout.strip()
try:
    sent = send_markdown_in_chunks("标题", card_output)
    print(f"[推送] {sent} 条", file=sys.stderr)
except Exception as e:
    print(f"[推送] 异常: {e}", file=sys.stderr)
# 不要 print(card_output) 到 stdout → 触发 cron 失败投递
```

## send_qq_bot.py 关键细节

- 位于 `/opt/data/scripts/send_qq_bot.py`
- `APP_ID`、`CLIENT_SECRET`、`USER_OPENID` 硬编码在文件中
- 自动管理 Token（7200s 过期，自动刷新）
- `send_markdown()` 网络异常会抛出，调用方需 try/except
- 单条消息限制 3800 字符，超长自动分段
- 过滤掉 "Morning cards done!"、"OK" 等状态行

## 三个推送任务

| Cron ID | 名称 | schedule | script | 
|:--------|:-----|:---------|:-------|
| d41a3db12dda | 📊 财经早餐 | `0 9 * * 1-5` | run_morning.py |
| 30b693051960 | 📈 盘中直击 | `35 11 * * 1-5` | run_noon.py |
| 415fc1837c2b | 📋 收盘复盘 | `0 16 * * 1-5` | run_closing.py |

## 超时限制

- cron 硬限 180 秒（3分钟）
- collect 子进程 ≤150s
- format 子进程 ≤60s
- 合计 ≤210s（实际通常在 90-120s 内）

## 已确认的故障模式

1. **deliver=local 导致用户不知情** — 用户以为 cron 会推，实际只存文件。脚本内 push 失败则完全无声。修复：脚本内 try/except + 明确告知用户架构。
2. **collect 超时** — 昨天(07-15) 08:31 被 SIGTERM 杀掉（exit code -15）。KOL 微博采集慢。修复：k-line API 不可达时跳过，设 150s 超时兜底。
3. **硬编码日期导致内容过期** — send_noon_cards.py 写死 "2026-07-13"。修复：用 `date.today()` 替换。
4. **盘中调用腾讯API返回今日涨跌幅** — 8:30 开盘前正常，盘中需要 prev_close 回退。修复：三级降级（快照→存档→prev_close）。
