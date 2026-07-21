# Investment Profile 创建记录 (2026-07-13)

## 环境
- Oracle ARM 152.70.91.4, Docker s6 部署
- Hermes v0.17.0 (用户说实际 0.18)
- HERMES_HOME=/opt/data（挂载宿主机 ~/.hermes-main）
- 已有 Profiles: default (running), llm-wiki (running)

## 创建步骤

```bash
hermes profile create investment --clone
```

### .env 用户自行编辑
用户明确要自己管理 .env。创建后通知用户修改：
- FEISHU_APP_ID / FEISHU_APP_SECRET → 新 Bot 凭据
- FEISHU_ALLOWED_USERS → 第一次发消息后查 gateway.log 获取

### config.yaml 修改
platforms 中只保留 feishu，其他设 enabled: false。

### SOUL.md 写入
克隆后 SOUL.md 是 444 只读，先 chmod u+w。
写入投资助手人格（自我介绍、数据驱动、风险意识、输出格式）。

### Memory 编写（关键上下文桥接）
MEMORY.md 包含：Fund monitoring system architecture, 数据源状态(status, 6 APIs), 已修复问题(009478, northbound, fund changes), 基金持仓列表(13 funds), cron任务计划(4 jobs), 未完成任务(3 items), 安全规则。
USER.md 包含：模型偏好、平台分布、服务器信息、投资目标。

### Gateway 启动
hermes -p investment gateway start → 自动创建 s6 服务。
首次启动后需等用户发消息，查 gateway.log 获取 Unauthorized user 的 OpenID。

### Gateway 重启
- `hermes -p investment gateway restart` → ❌ Refusing to restart from inside the gateway process
- 替代方案：`kill <PID>` → s6 自动重启，或 s6-svc -r /run/service/gateway-investment

### Cron 任务注册
```bash
hermes -p investment cron create \
  --name "📊 财经早餐·基金参考" \
  --deliver "feishu:oc_5c176bb1243a1f2d353ed926e62f4d1a" \
  --script collect_morning_data.py \
  "30 0 * * 1-5" \
  "简短prompt"
```

⚠️ `--script` 必须是文件名，不能是绝对路径。需要 ~/.hermes/scripts/ 指向 /opt/data/scripts/。
⚠️ prompt 过长 (200+字符) 会导致 CLI 超时。

注册了 3 个 cron 任务：财经早餐(08:30)、盘中直击(11:35)、收盘复盘(16:00)。

### 注意点
- profile名必须是英文：尝试中文会失败，用了 `investment`
- 关闭 platform 后 gateway 仍尝试连接（.env 中保留的凭据导致），这是无害的日志噪声
- 新 Bot 对话中 Agent 加载 MEMORY.md 后能正确识别角色（投资助手）
