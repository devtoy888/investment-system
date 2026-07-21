# Cron 任务配置 — 2026-07-13

## 配置文件关键设置

**`config.yaml` 中必须配置以下两项才能让定时任务运行：**

```yaml
approvals:
  cron_mode: allow          # ← 默认为 deny！必须改为 allow 才能执行定时任务
timezone: Asia/Shanghai    # ← 默认为空。设置后 cron 调度使用 CST（北京时间）
```

### cron_mode: deny → allow 修复（2026-07-13）

新配置文件默认 `cron_mode: deny`，导致所有已注册的定时任务**从未执行**。修改方法：

```bash
hermes -p investment config set approvals.cron_mode allow
# 然后重启 gateway
```

### timezone: Asia/Shanghai（2026-07-13）

未设置 timezone 时，cron 使用 UTC。设置后调度表达式使用北京时间（CST, UTC+8）：

```bash
hermes -p investment config set timezone Asia/Shanghai
# 然后重启 gateway
```

### 修改后的重启

修改 config.yaml 后需重启 gateway 才能生效：
```bash
kill -15 $(cat /opt/data/profiles/investment/gateway.pid)
# s6 自动重启
```

## 当前活跃任务（2026-07-15 完整列表 — 12个cron）

⚠️ **所有推送模式为 `no_agent=true`**，通过 `run_*.py` 包装脚本。
stdout 被抑制（deliver=local）或由 cron 投递（deliver=origin）。

### 交易日（8个）

| 时间(CST) | 任务 | 包装脚本 | 投递 |
|:---------:|:----|:---------|:----:|
| 08:00 | 财经早餐 | run_morning.py | local |
| 11:35 | 盘中直击 | run_noon.py | local |
| 16:00 | 收盘复盘 | run_closing.py | local |
| 16:10 | 加仓信号监控 | run_buy_signal.py | origin |
| 16:20 | JSONL去重 | run_dedup.py | local |
| 16:25 | 决策日志 | run_decisions.py | local |
| 16:30 | 决策验证 | run_verify.py | local |
| 23:30 | 微博看门狗 | weibo_watchdog.py | origin |

### 每周（4个）

| 时间(CST) | 任务 | 包装脚本 | 投递 |
|:---------:|:----|:---------|:----:|
| 周六 09:00 | 周末外盘速报 | run_weekend.py | origin |
| 周六 10:00 | 数据源验证 | run_validate.py | origin |
| 周六 10:30 | 系统自检 | run_health_audit.py | origin |
| 周日 20:00 | 周度复盘 | run_weekly_review.py | origin |

### wrappers路径
所有 `run_*.py` 位于 `/opt/data/profiles/investment/scripts/`。
实际采集脚本位于 `/opt/data/scripts/`。

## 推送格式（2026-07-15 更新：QQ Bot Markdown）

当前模式：所有内容合并为连续Markdown文本，仅按QQ 3800字符限制切分。
发送：`send_qq_bot.py` → `send_markdown_in_chunks()` → QQ Bot API v2

操作原理：
- 不按 `═══` 分隔符独立拆消息（旧做法产生8-12条）
- 多段时自动加 `_(📎 接上条)_` / `_(📎 续下条)_` 标记
- 自动过滤脚本状态行（`OK`, `FAIL`, `All done` 等）
- 典型：6435字符早报 → **2条消息**（原8条）

### 内容组织原则（跨平台通用）

先给结论（操作）→ 再给理由（数据+分析）→ 最后给参考（新闻+KOL）

### 历史遗留：Feishu卡片格式

2026-07-13 前后曾使用 Feishu API 分块卡片（7张卡片，每张1表格+分析），已废弃。
旧格式细节在 `references/feishu-card-optimization.md`。

## 周一/周五特殊推送规则

### 周一 08:00 — "隔夜"数据实为上周五

外盘数据实际是**上周五**收盘（距推送约76h），需修正：
1. 标注"上周五外盘关盘（周末无交易）"，不说"隔夜"
2. 增加 `web_search` 搜索周末重大事件（政策/地缘/大宗）
3. A50期货使用夜盘收盘

### 周五 16:00 — 增加美股前瞻段

在收盘复盘中追加：
```
🌙 今晚美股关注
● 21:30 美股开盘
● 关注科技股是否延续走势
● 若有大幅波动，将在周六推送外盘速报
```

## 已知问题

1. **QQ Bot 偶有限流** — 日志 `channel=400 c2c=500 group=500`，需考虑重试机制
2. **gateway 重启检查** — 需确认 `config.yaml` 中 `cron_mode: allow` + `timezone: Asia/Shanghai`
3. **08:30 vs 08:00** — 如改早报时间，同时改 cron 调度和 prompt 中的时间声明
