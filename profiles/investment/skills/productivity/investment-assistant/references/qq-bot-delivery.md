# QQ Bot 推送方案 (2026-07-14 实施)

## 架构概述

所有定时任务不再依赖 cron 的 `deliver` 机制。脚本直接通过 QQ Bot API v2 推送 Markdown 消息。

```
脚本(run_*.py) → send_qq_bot.py → QQ Bot API v2 → 用户QQ
                                ↓
                     (不依赖 cron deliver)
```

## 关键文件

| 文件 | 路径 | 作用 |
|:----|:-----|:----:|
| `send_qq_bot.py` | `/opt/data/scripts/` | QQ Bot API 推送工具，含 token 管理 + 分条发送 |
| `send_qqbot.py` | `/opt/data/scripts/` | Markdown stdout 输出模块（备用，不调用API） |
| `run_*.py` | `/opt/data/scripts/` | 3个wrapper: 数据采集 → 格式化 → 调API推送 |
| `send_*_cards.py` | `/opt/data/scripts/` | 内容构建器（导入 send_qqbot，输出Markdown到stdout） |

## QQ Bot API v2 调用参数

**Token 获取:**
- 端点: `POST https://bots.qq.com/app/getAppAccessToken`
- 请求体: `{"appId": "...", "clientSecret": "..."}`
- 响应: `{"access_token": "...", "expires_in": 4652}`

**发送消息（C2C）:**
- 端点: `POST https://api.sgroup.qq.com/v2/users/{openid}/messages`
- 请求头: `Authorization: QQBot {token}`
- 请求体: `{"msg_type": 2, "markdown": {"content": "## 标题\n\n内容..."}}`
- 单条限制: ~4000 字符

## 内容完整性原则

**用户明确要求:** 不要截断内容来适配长度限制。如果内容超长，拆分为多条消息发送，保留原文。

分条策略（见 `send_qq_bot.py` 的 `send_markdown_in_chunks()`）:
1. 按 `══════════════════════` 分隔符分割板块
2. 每个板块作为独立消息发送
3. 超长板块（>3800字符）按段落边界进一步拆分
4. 最多拆分到段落粒度，不做字符级截断

## Cron Job 配置规范

所有推送到QQ的 job 使用:
- `no_agent: true` — 脚本自处理，不走LLM
- `deliver: local` — cron 不负责投递（脚本自行调用API）
- `script: run_*.py` — 位于 `profiles/investment/scripts/`

对于 `deliver` 字段:
- ✅ `qqbot:用户OpenID` — 明确指定QQ Bot（推荐）
- ✅ `local` — 本地保存，无投递（脚本自推送时）
- ❌ `origin` — 在cron上下文中可能解析到其他平台（已全部替换）
- ❌ `feishu:群ChatID` — 不再使用

## 平台配置

飞书平台已在 `config.yaml` 中禁用:
```yaml
platforms:
  feishu:
    enabled: false
```

飞书 gateway 实例和 feishu-platform 插件也已移除。

## 测试验证

每次改推送渠道后，至少运行一次 cron job 并用 `delivery_error` 字段确认:
- `delivery_error: null` = 成功
- 如果脚本自己调API，检查 `[收盘复盘] 已推送 N 条消息到QQ` 这类stderr日志
