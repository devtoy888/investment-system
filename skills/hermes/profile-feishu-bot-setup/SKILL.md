---
name: profile-feishu-bot-setup
description: "完整流程：创建Hermes Profile + 配置专用飞书机器人 + s6多gateway管理"
version: 1.2.0
author: Hermes Agent
metadata:
  hermes:
    tags: [profile, feishu, gateway, s6, docker, multiplex]
---

# Profile + 飞书机器人配置工作流

适用于 Docker 部署的 Hermes（s6 进程管理），为每个 Profile 配置独立的飞书机器人。

## 前置条件
- Docker 部署的 Hermes，容器名通常为 `hermes-main`
- 已有飞书开放平台账号 https://open.feishu.cn/
- HERMES_HOME 映射到宿主机目录（本流程假设宿主机 `~/.hermes-main` → 容器 `/opt/data`）

## 完整步骤

### Step 1: 飞书开放平台创建新 Bot

1. 登录 https://open.feishu.cn/ → **创建应用** → **企业自建应用**
2. 应用名称自定义（如"投资助手"）
3. **凭证与基础信息** → 记下 `App ID`、`App Secret`
4. **应用功能 → 机器人** → 开启 ✅
5. **权限管理** → 添加：
   - `im:message`（接收消息）
   - `im:message:send_as_bot`（发送消息）
6. **事件与回调** → 连接方式选 **长连接(WebSocket)**
   - **添加事件** → `im.message.receive_v1`（必须！）
7. **版本管理与发布** → 创建版本 → 申请发布 → 审批通过

### Step 2: 创建 Profile

```bash
# 容器内执行
export PATH=$PATH:/opt/hermes/bin
hermes profile create <profile名> --clone
```

> **路径对应：** 宿主机 `~/.hermes-main/profiles/<name>/` = 容器内 `$HERMES_HOME/profiles/<name>/`。
> `--clone` 复制 default 的 config.yaml、.env、SOUL.md、skills。
> profile名必须是英文小写字母/数字/连字符。

### Step 3: 编辑 .env（宿主机直接编辑，或由用户操作）

```bash
vi ~/.hermes-main/profiles/<profile名>/.env
```

**只需要改飞书相关行**，其他 API Key（DeepSeek、OpenRouter 等）保持不动：

```
FEISHU_APP_ID=cli_...新bot的ID
FEISHU_APP_SECRET=***
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOW_ALL_USERS=false
# ⚠️ ALLOWED_USERS 留空！第一次发消息后查日志获取正确 OpenID
# FEISHU_ALLOWED_USERS=
FEISHU_GROUP_POLICY=open
FEISHU_HOME_CHANNEL=
FEISHU_HOME_CHANNEL_THREAD_ID=
```

> **关键坑：** 不同飞书 Bot 给同一用户的 OpenID 可能不同。先留空 ALLOWED_USERS，发消息后查日志获取。
> **安全实践：** 如果用户明确要自己编辑 .env，尊重用户选择。Agent 负责其他配置，用户处理凭据。

### Step 4: 编写 SOUL.md

编辑容器内 `$HERMES_HOME/profiles/<profile名>/SOUL.md`（宿主机 `~/.hermes-main/profiles/<profile名>/SOUL.md`）。

**语言指令必须放最前面：**

```
【语言指令——必须遵守】
你必须始终使用简体中文回复用户。
即使用户发英文、表情、符号、代码，也必须用中文回答。

# 角色名称
[以下写具体的角色定义]
```

> **⚠️ 权限坑：** `--clone` 后的 SOUL.md 默认是只读权限（`r--r--r--` 444）。写入前先 `chmod u+w <path>/SOUL.md`。

### Step 5: 配置显示语言

```bash
export PATH=$PATH:/opt/hermes/bin
hermes -p <profile名> config set display.language zh
```

### Step 6: 禁用无关平台

编辑 `config.yaml`，只保留 feishu，禁用其他平台：

```yaml
platforms:
  feishu:
    enabled: true
  dingtalk:
    enabled: false
  telegram:
    enabled: false
  weixin:
    enabled: false
```

> ⚠️ **注意：`platforms.qqbot.enabled` 不影响 QQ 机器人连接。** QQ 机器人由 `.env` 中的凭据控制——只要 `.env` 里有 `QQ_APP_ID` 和 `QQ_CLIENT_SECRET`，QQ 机器人就会连接，不受 `platforms` 段影响。要禁用 QQ 机器人，需删除 `.env` 中对应行。

### Step 7: 编写 Memory（上下文桥接，关键！）

> **Memory 是跨 Profile 的上下文桥接手段。** 新 Profile 的 Agent 看不到 default profile 的历史会话，但能读到 MEMORY.md 和 USER.md。
>
> 如果用户有正在进行的长期目标（如基金监控系统），必须把关键上下文写进 Memory。

编辑 `$HERMES_HOME/profiles/<profile名>/memories/MEMORY.md`：

```
系统架构: 脚本在 /opt/data/scripts/，核心模块 fund_tools.py
§
数据源状态: fundgz ✅, qt.gtimg ✅, push2.eastmoney ❌ 502
§
已知修复: 009478用黄金ETF替代、北向加标注
§
用户偏好: 简洁直接、不修改.env、偏好官方文档验证
```

编辑 `USER.md`：用户身份、服务器、模型偏好、投资目标等。

### Step 8: 启动 Gateway

```bash
export PATH=$PATH:/opt/hermes/bin
hermes -p <profile名> gateway start
```

> ⚠️ **不要设置 `gateway.multiplex_profiles: true`！** s6 架构下各 Profile 用独立 gateway 进程，multiplex 会冲突。

### Step 8b: 验证运行状态

```bash
hermes profile list
# → Gateway 状态应为 running

ps aux | grep "gateway" | grep -v grep
# → 应有独立的 `-p <profile名> gateway run` 进程
```

### Step 9: 获取用户 OpenID

给新飞书 Bot 发一条消息 → 查日志：

```bash
cat $HERMES_HOME/profiles/<profile名>/logs/gateway.log | grep "Unauthorized"
# 输出: Unauthorized user: ou_xxx on feishu
```

将 OpenID 写入 .env：

```bash
# 宿主机编辑
vi ~/.hermes-main/profiles/<profile名>/.env
# FEISHU_ALLOWED_USERS=ou_xxx
```

### Step 10: 重启 Gateway

```bash
hermes -p <profile名> gateway restart
```

## 验证清单

- [ ] `hermes profile list` → 新 Profile 状态 `running`
- [ ] `ps aux | grep gateway` → 有 `-p <profile名> gateway run` 进程
- [ ] 飞书 Bot 回复中文
- [ ] 只有被允许的用户能使用
- [ ] s6 自动管理（容器重启后自动恢复）

## 跨 Profile 上下文桥接

创建新 Profile 后，用户可能问："之前的任务还能在新 Profile 继续做吗？"

| 能/不能 | 内容 | 原因 |
|:-------:|:----|:-----|
| ✅ | Python 脚本 | 共享文件系统，所有 Profile 都能访问 |
| ✅ | API Key 和模型配置 | `--clone` 复制 |
| ✅ | Skills | `--clone` 复制，可补充 |
| ✅ | 文件和文档 | 共享文件系统 |
| ⚠️ | Cron 任务 | 各 Profile 独立，需重新注册 |
| ❌ | 会话历史（state.db） | 各 Profile 独立 |
| ❌ | Memory（需手动编写） | 各 Profile 独立 |
| ❌ | `session_search` 搜索旧会话 | 只针对当前 Profile |

**桥接策略：** MEMORY.md + USER.md 是主要手段。编写时包含：系统架构、数据源矩阵、已知修复、用户偏好、未完成任务。详见 Step 7。

### Step 11: 注册 Cron 任务（可选）

新 Profile 的 cron 任务独立于 default profile。如果需要自动推送（如基金早报），必须重新注册：

```bash
export PATH=$PATH:/opt/hermes/bin

# ⚠️ 脚本路径必须是相对于 ~/.hermes/scripts/ 的文件名，不是绝对路径
# 先确保脚本存在或建立符号链接：
ln -sf /opt/data/scripts /opt/data/home/.hermes/scripts

hermes -p <profile名> cron create \
  --name "任务名称" \
  --deliver "feishu:<chat_id>" \
  --script collect_morning_data.py \
  "30 0 * * 1-5" \
  "任务提示词, 简短为佳, 过长会导致CLI超时"
```

> **chat_id 获取：** 给新 Bot 发一次消息，在 gateway.log 中查找 `chat_id=oc_xxx`。
> **CLI 注意：** `hermes cron create` 的 prompt 参数不宜过长（超过200字符可能超时），长提示词建议用 `--script` 预采集模式。

### Step 12: 验证运行

```bash
hermes profile list
# → 新 Profile 的 Gateway 应为 running

# 查看新 Profile 的 gateway 日志
tail -20 $HERMES_HOME/profiles/<profile名>/logs/gateway.log
```

## 常见坑

| 坑 | 解决 |
|:---|:-----|
| 飞书没回复 | 检查 `FEISHU_CONNECTION_MODE=websocket` 和 `im.message.receive_v1` 事件 |
| Unauthorized user | OpenID 不同，查日志获取正确值 |
| Telegram/微信 token 冲突 | 禁用无关平台（Step 6），或直接删除 .env 中对应凭据行 |
| 回复英文 | SOUL.md 语言指令放最前面 + display.language=zh |
| multiplex 冲突 | 不要设置 multiplex_profiles，s6 原生支持多 gateway |
| `--clone` 后 memory 是 default 的内容 | 必须手动替换为 Profile 专用记忆 |
| SOUL.md 只读 (444) | 写入前先 `chmod u+w <path>/SOUL.md` |
| .env 凭据的修改 | 如果用户明确要自己改.env，尊重用户，Agent只负责其他配置 |
| 新Profile一问三不知 | 没写 MEMORY.md → 必须桥接上下文，详见 Step 7 |
| `gateway restart` 在gateway进程内失败 | 用 `s6-svc -r /run/service/gateway-<profile名>`，或直接 `kill <PID>`（s6自动重启），或用 `hermes -p <名> gateway start` 在外壳中执行 |
| `cron create --script` 不认绝对路径 | 必须用相对于 `~/.hermes/scripts/` 的文件名，不能写 `/opt/data/scripts/x.py` |
| `hermes cron create` 超时 | prompt太长了。精简到200字符内，或把详细指令写在 `--script` 预采集脚本的 print 输出中 |
| 禁用平台后仍然连接 | `platforms.dingtalk.enabled: false` 只阻止 gateway 注册 listener，如果 .env 中有对应凭据（TOKEN/APP_ID），底层仍会尝试握手。彻底禁用需删除 .env 中对应平台的全部凭据行 |
