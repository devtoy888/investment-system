---
name: profile-feishu-bot-setup
description: "完整流程：创建Hermes Profile + 配置专用机器人(飞书/QQ Bot/钉钉等) + s6多gateway管理"
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [profile, feishu, qqbot, gateway, s6, docker, multiplex, bot-setup]
---

# Profile + 机器人配置工作流（通用）

适用于 Docker 部署的 Hermes（s6 进程管理），为每个 Profile 配置独立的机器人。

> ⚠️ **虽然技能名含 feishu，但流程适用于所有平台。** 平台差异仅在于注册渠道不同、环境变量名不同。架构步骤完全一致。

## 前置条件
- Docker 部署的 Hermes，容器名通常为 `hermes-main`
- 已在目标平台开放平台注册机器人（飞书: open.feishu.cn, QQ: q.qq.com, 钉钉: open.dingtalk.com）
- HERMES_HOME 映射到宿主机目录（本流程假设宿主机 `~/.hermes-main` → 容器 `/opt/data`）

## 各平台注册指引

## 各平台注册指引

| 平台 | 注册地址 | 所需凭证 | Hermes环境变量 |
|:-----|:---------|:---------|:---------------|
| 飞书 | https://open.feishu.cn/ | App ID + App Secret | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` |
| QQ Bot | https://q.qq.com/ | App ID + Client Secret | `QQ_APP_ID`, `QQ_CLIENT_SECRET` |
| 钉钉 | https://open.dingtalk.com/ | Client ID + Client Secret | `DINGTALK_CLIENT_ID`, `DINGTALK_CLIENT_SECRET` |
| Telegram | @BotFather | Bot Token | `TELEGRAM_BOT_TOKEN` |

### QQ Bot 注册要点
1. 登录 https://q.qq.com/ → 创建机器人应用
2. 获取 **App ID** 和 **App Secret**（注意：环境变量名是 `QQ_APP_ID`/`QQ_CLIENT_SECRET`，不是 `QQBOT_APPID`）
3. 开启 intents：C2C 私聊 + 群 @消息
4. 可选沙箱模式测试，或发布后用于生产
5. 记录机器人的 OpenID（用于 QQBOT_HOME_CHANNEL）

### 完整步骤

### Step 1: 开放平台创建新 Bot

按上方表格选择平台，注册机器人，获取凭证。

**飞书示例：** 登录 https://open.feishu.cn/ → 创建应用 → 企业自建应用 → 记下 App ID/Secret → 开启机器人功能 → 添加权限(`im:message`, `im:message:send_as_bot`) → 添加事件(`im.message.receive_v1`) → 连接方式选 WebSocket → 发布版本

**QQ Bot 示例：** 登录 https://q.qq.com/ → 创建机器人 → 记下 App ID/Secret → 开启 intents(C2C/群@) → 沙箱测试或发布

### Step 2: 创建 Profile（宿主机执行）

```bash
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && hermes profile create 投资-profile名 --clone'
```

> `--clone` 会自动复制 default 的 config.yaml、.env、SOUL.md、skills

### Step 3: 编辑 .env（宿主机直接编辑）

```bash
vi ~/.hermes-main/profiles/投资-profile名/.env
```

**只需要改目标平台相关行**，其他 API Key（DeepSeek、OpenRouter 等）保持不动：

**飞书示例：**
```bash
FEISHU_APP_ID=cli_...新bot的ID
FEISHU_APP_SECRET=***\nFEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOW_ALL_USERS=false
# ⚠️ ALLOWED_USERS 留空！第一次发消息后查日志获取正确 OpenID
# FEISHU_ALLOWED_USERS=
FEISHU_GROUP_POLICY=open
FEISHU_HOME_CHANNEL=
FEISHU_HOME_CHANNEL_THREAD_ID=
```

**QQ Bot 示例：**
```bash
QQ_APP_ID=你的AppID
QQ_CLIENT_SECRET=***
QQBOT_HOME_CHANNEL=用户的OpenID（QQ里发消息后从日志获取）
```

> **关键坑**：不同平台（甚至同一平台不同 Bot）给同一用户的 OpenID 可能不同。先留空 ALLOWED_USERS，发消息后查日志获取。

### Step 4: 编写 SOUL.md

编辑 `~/.hermes-main/profiles/投资-profile名/SOUL.md`，定义该 Profile 的角色和语言偏好。

**语言指令必须放最前面**（深度求索等模型可能忽略后半部分）：

```
【语言指令——必须遵守】
你必须始终使用简体中文回复用户。
即使用户发英文、表情、符号、代码，也必须用中文回答。

# 角色名称
[以下写具体的角色定义]
```

### Step 5: 配置显示语言和人格

```bash
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && \
  hermes -p 投资-profile名 config set display.language zh && \
  hermes -p 投资-profile名 config set display.personality 投资-助手'
```

> personality 需要在 config.yaml 的 `agent.personalities` 段中预先定义。

### Step 6: 禁用无关平台（必做两项）

#### 6a. 编辑 config.yaml

编辑 `~/.hermes-main/profiles/投资-profile名/config.yaml`，只保留需要的平台：

```yaml
platforms:
  feishu:
    enabled: true
```

#### 6b. 清理 .env 中的无关凭证

⚠️ **只改 config.yaml 不够！** Hermes 的 `gateway/config.py` 会在检测到环境变量（FEISHU_APP_ID、QQ_APP_ID 等）时**强制启用**对应平台，无视 config.yaml。

必须在 Profile 的 `.env` 中**只保留**本 profile 需要的平台凭证：

```bash
# ✅ 保留：本 profile 要用的
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=***
# ❌ 删除：其他平台的（注释掉或删掉）
# QQ_APP_ID=xxx
# DINGTALK_CLIENT_ID=xxx
```

> 多 profile 分平台时：哪个 profile 的 .env 有某平台的凭证，该 profile 的 gateway 就会试图连接那个平台。

### Step 7: 替换 Memory

编辑 `~/.hermes-main/profiles/投资-profile名/memories/MEMORY.md` 和 `USER.md`，写入该 Profile 专用的记忆。

MEMORY.md 格式：
```
关键事实1
§
关键事实2
§
关键事实3
```

### Step 8: 启动 Gateway

```bash
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && \
  hermes -p 投资-profile名 gateway start'
```

> ⚠️ **不要设置 `gateway.multiplex_profiles: true`**！Docker s6 架构使用每个 Profile 独立的 gateway 进程，multiplex 会冲突。

### Step 9: 获取用户 OpenID

给新 Bot 发一条消息 → 查看日志获取用户 ID：

**飞书：**
```bash
grep "Unauthorized" /opt/data/profiles/投资-profile名/logs/gateway.log
```
输出示例：`Unauthorized user: ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx on feishu`

**QQ Bot：**
```bash
grep "C2C message" /opt/data/profiles/投资-profile名/logs/gateway.log
```
输出示例：`C2C message: content='hi' attachments=None` → OpenID 在 `chat=C40A1DEC...` 字段

将 OpenID 写入 .env：
```bash
vi ~/.hermes-main/profiles/投资-profile名/.env
# FEISHU_ALLOWED_USERS=ou_xxx
# QQBOT_HOME_CHANNEL=C40A1DEC...   ← QQ用户的OpenID
```

### Step 10: 重启 Gateway

```bash
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && \
  hermes -p 投资-profile名 gateway restart'
```

## 主频道设置：每个 Profile 独立

每个 Hermes Profile（机器人实例）拥有**自己独立的主频道**，互不影响。主频道用于 cron 定时任务投递、系统通知等。

### 查看当前频道注册情况

```bash
python3 -c "
import json
with open('/opt/data/profiles/你的-profile名/channel_directory.json') as f:
    d = json.load(f)
for platform, channels in d.get('platforms', {}).items():
    for ch in channels:
        print(f'{platform}: id={ch[\"id\"]} type={ch.get(\"type\",\"?\")} name={ch.get(\"name\",\"?\")}')
"
```

该文件记录该 Profile 下各平台所有已发生过交互的频道（群聊/DM）。

### 设置当前对话为主频道

在飞书群里直接输入斜杠命令：

```
/sethome
```

这是一个**网关级斜杠命令**，作用范围仅限当前 Profile。之后所有定时任务的 `"feishu"` 投递目标都会发到这个群。

> ⚠️ **区别于 `FEISHU_HOME_CHANNEL`**：后者是通过 `.env` 静态指定主频道 ID（格式 `oc_xxx`）。`/sethome` 是运行时动态设置，效果等价但更简便。两者选其一即可。

### 验证主频道

在 `cronjob` 工具中查看投递选项，确认 `"origin"` 指向当前对话、`"feishu"` 也指向当前对话。

或者在 `.env` 中查看：

```bash
grep FEISHU_HOME_CHANNEL /opt/data/profiles/你的-profile名/.env
```

若值为空，则主频道由 `/sethome` 动态管理。

## 验证清单

- [ ] `ps aux | grep "gateway run"` → 看到新 profile 的 python 进程
- [ ] 飞书 Bot 回复中文
- [ ] 只有被允许的用户能使用
- [ ] s6 自动管理（容器重启后自动恢复）
- [ ] 主频道设置正确（`/sethome` 或 `FEISHU_HOME_CHANNEL`）

## 关键原理（理解以下机制避免踩坑）

### 平台强制启用机制（重要！）

Hermes 的 `gateway/config.py` 中，**环境变量会强制覆盖 config.yaml 的平台启用状态**。即使 config.yaml 里设置了 `qqbot.enabled: false`，只要环境变量中存在 `QQ_APP_ID`，代码就会强制设为 `True`：

```python
# gateway/config.py 中的示例逻辑
qq_app_id = os.getenv("QQ_APP_ID")
if qq_app_id:  # 只要存在就不管 config.yaml
    config.platforms[Platform.QQBOT].enabled = True
```

受影响的所有平台及对应的强制启用环境变量：

| 平台 | 强制启用环境变量 |
|:----|:--------------|
| 飞书 | `FEISHU_APP_ID` + `FEISHU_APP_SECRET` |
| 钉钉 | `DINGTALK_CLIENT_ID` + `DINGTALK_CLIENT_SECRET` |
| 微信 | `WEIXIN_TOKEN` / `WEIXIN_ACCOUNT_ID` |
| Telegram | `TELEGRAM_BOT_TOKEN` |
| QQ Bot | `QQ_APP_ID` / `QQ_CLIENT_SECRET` |
| Slack | `SLACK_BOT_TOKEN` |
| Whatsapp | `WHATSAPP_*` 相关变量 |
| 邮件 | `SMTP_*` / `IMAP_*` 相关变量 |

**这意味着「禁用无关平台」不能只改 config.yaml，还必须确保环境变量不存在。**

### .env 加载机制

Hermes gateway 进程启动时，`gateway/run.py` 会调用 `load_hermes_dotenv()`：

```python
from hermes_constants import get_hermes_home
_hermes_home = get_hermes_home()   # 取决于 HERMES_HOME 环境变量
load_hermes_dotenv(hermes_home=_hermes_home, ...)
```

加载逻辑（`hermes_cli/env_loader.py`）：
1. 优先加载 `$HERMES_HOME/.env`（有则 override=True）
2. 若无则加载 `$HOME/.hermes/.env`

所以 **哪个 .env 被加载取决于 `HERMES_HOME` 环境变量**，不是直接读容器根目录的 .env。

### s6 多 Gateway 架构

当需要**多个 profile 同时运行并各自绑定不同平台**时：

```
/run/service/
  gateway-default/     → hermes gateway run --replace       （default profile）
  gateway-investment/  → hermes -p investment gateway run    （investment profile）
  gateway-llm-wiki/    → hermes -p llm-wiki gateway run      （其他 profile）
```

**关键限制**：
- 每个平台（如飞书、QQ）只能被一个 gateway 连接，否则冲突
- 环境变量是进程级共享的，全局 .env 中的 FEISHU_APP_ID 会被所有 gateway 读到
- s6 服务可以通过 `env/` 目录注入**服务专属**的环境变量覆盖/置空

### s6 env 目录用法

可为每个 gateway 服务设置专属环境变量，覆盖全局值：

```bash
# 创建 env 目录
mkdir -p /run/service/gateway-default/env

# 设置 QQ 凭证（仅 default gateway 能看到）
echo -n "1904452472" > /run/service/gateway-default/env/QQ_APP_ID
echo -n "client_secret值" > /run/service/gateway-default/env/QQ_CLIENT_SECRET

# 置空飞书凭证（阻止 default gateway 连接飞书）
echo -n "" > /run/service/gateway-default/env/FEISHU_APP_ID
```

注意：空文件在 s6 中表示**置空该变量**，而非删除。容器级别的全局变量仍可能在 `load_hermes_dotenv()` 时重新加载回来——**所以光靠 env 目录不够**，详见下方方案。

### 多 Profile 分平台方案

假设需求：investment profile 处理飞书 → default profile 处理 QQ

**方案 A：修改 default 的 .env（推荐）**
1. 从 `/opt/data/.env` 移除 QQ 凭证（防止 investment 加载时读到）
2. 在 default 的 profile home 的 `.env` 中**只放** QQ 凭证
3. 其他平台的凭证（飞书等）在 default 的 .env 中**不要出现**

```bash
# 容器的 HERMES_HOME=/opt/data，default 的 home 在 /opt/data/.hermes/
# → 编辑 /opt/data/.hermes/.env，只保留：
#   QQ_APP_ID=xxx
#   QQ_CLIENT_SECRET=xxx
#   QQBOT_HOME_CHANNEL=xxx
# 不要放 FEISHU_APP_ID、DINGTALK_CLIENT_ID 等
```

**方案 B：修改 run 脚本 unset 平台变量**
在 `/run/service/gateway-default/run` 中添加 `unset`：

```bash
unset FEISHU_APP_ID FEISHU_APP_SECRET
unset DINGTALK_CLIENT_ID DINGTALK_CLIENT_SECRET
unset WEIXIN_TOKEN WEIXIN_ACCOUNT_ID
```

但这种方法**不一定可靠**，因为 `exec hermes` 后 Hermes 会重新调用 `load_hermes_dotenv()` 加载 .env 文件，可能又把变量加回来。

## 验证连接

重启 gateway 后，通过以下方式确认机器人已连接：

### 查看日志
```bash
# 飞书
grep "feishu" /opt/data/profiles/投资-profile名/logs/gateway.log | tail -5
# QQ Bot
grep "QQBot" /opt/data/profiles/投资-profile名/logs/gateway.log | tail -5
```

### 检查进程环境变量
```bash
GW_PID=$(pgrep -f "hermes.*-p.*investment.*gateway" | head -1)
# 检查 QQ 凭证是否被加载
cat /proc/$GW_PID/environ 2>/dev/null | tr '\0' '\n' | grep QQ_
# 检查飞书凭证是否被加载
cat /proc/$GW_PID/environ 2>/dev/null | tr '\0' '\n' | grep FEISHU
```

### 检查 WebSocket 连接（QQ Bot / WebSocket 类平台）
```bash
# 查看进程文件描述符中的 socket 连接
GW_PID=$(pgrep -f "hermes.*gateway.*run" | head -1)
ls -l /proc/$GW_PID/fd/ 2>/dev/null | grep socket
# 查看已建立的 TCP 连接（QQ Bot → api.sgroup.qq.com）
cat /proc/$GW_PID/net/tcp 2>/dev/null | python3 -c "
import sys
for line in sys.stdin:
    parts = line.strip().split()
    if len(parts) > 2 and parts[3] == '01':  # ESTABLISHED
        local = parts[1]
        remote = parts[2]
        # 解析十六进制 IP:端口
        import socket, struct
        rip = remote.split(':')[0]
        rport = int(remote.split(':')[1], 16)
        ip = socket.inet_ntoa(struct.pack('>I', int(rip, 16)))
        print(f'ESTABLISHED: {ip}:{rport}')
"
```

### QQ Bot 日志路径差异
| Profile | 日志路径 |
|:--------|:---------|
| default | `/opt/data/logs/gateway.log`（s6管道） |
| 非default | `/opt/data/profiles/<name>/logs/gateway.log`（直接文件 FD） |
| s6管道 | `/opt/data/logs/gateways/<name>/current`（rotated） |

## 常见坑

| 坑 | 解决 |
|:---|:-----|
| 飞书没回复 | 检查 `FEISHU_CONNECTION_MODE=websocket` 和 `im.message.receive_v1` 事件 |
| 飞书 Unauthorized user | OpenID 不同，查日志获取正确值 |
| QQ Bot 环境变量名用错 | 变量名是 `QQ_APP_ID`/`QQ_CLIENT_SECRET`，不是 `QQBOT_APPID`/`QQBOT_SECRET` |
| Telegram/微信 token 冲突 | 禁用无关平台（Step 6），同时确保环境变量不存在 |
| 平台明明在 config.yaml 禁用了却仍连接 | **环境变量强制启用**——必须清理 .env 和容器 env |
| 回复英文 | SOUL.md 语言指令放最前面 + display.language=zh |
| multiplex 冲突 | 不要设置 multiplex_profiles，s6 原生支持多 gateway |
| `--clone` 后 memory 是 default 的内容 | 必须手动替换为 Profile 专用记忆 |
| 两个 gateway 都连上了飞书 | 飞书凭证在全局 .env 中存在，所有 gateway 共享——需要用 s6 env 置空或分 .env |
| QQ Bot 绑定到错误 profile | QQ 凭证（QQ_APP_ID）在哪个 profile 的 .env 中出现，就绑定到哪个 profile 的 gateway |
| **Gateway 内无法自杀重启** | 在 gateway 进程内部执行 `kill` 会被阻止（终端工具 block），需从外部 docker exec 或写 nohup+disown 脚本 |
| **profile 级 .env 与根 .env 同时存在** | 根 `/opt/data/.env` 和 `/opt/data/profiles/<name>/.env` 是两个独立文件。修改 profile 级 .env 后必须重启对应 gateway 才生效 |
