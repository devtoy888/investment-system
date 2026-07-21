# QQ 推送策略

> 所有消息通过 `send_qq_bot.py` 的 `send_markdown_in_chunks()` 推送。

## 合并推送（2026-07-15）

**旧行为**: 按内容主题（═════════ 分隔符）逐段推送 → 早报8-12条消息
**新行为**: 合并所有内容为连续消息，仅按 QQ 3800 字符限制分段 → 2-3条

### 实现要点

```python
# send_qq_bot.py — send_markdown_in_chunks()
① 去掉状态行（Morning cards done!, OK ...等）
② 保留分隔线作视觉分隔但不作为切分点
③ 加统一标题 "## 📚 {title}"
④ 超3800字符则按段落切分，加接续标记
   - 首条: _(📎 续下条)_
   - 中段: _(📎 接上条)_ ... _(📎 续下条)_  
   - 末条: _(📎 接上条)_
```

### 流水线

```
collect_morning_data.py → send_morning_cards.py → stdout → run_morning.py
                                                                   ↓
                                                     send_markdown_in_chunks()
                                                                   ↓
                                                     QQ Bot API (v2/users/{openid}/messages)
```

### 推送时间
- 早报: 8:30 (cron 0 8 * * 1-5)
- 午报: 11:35 (cron 35 11 * * 1-5)
- 收盘: 16:00 (cron 0 16 * * 1-5)
