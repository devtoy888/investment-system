# Hermes Agent 恢复指南

> 从 Cloudflare R2 备份恢复 Hermes Agent 配置和数据。
> 备份频率：每天北京时间 00:00 (UTC 16:00)
> R2 保留：15 天

---

## 前提条件

- Hermes Agent 已安装（Docker 部署）
- Docker volume 映射：`~/.hermes-main:/opt/data`
- boto3 已安装：`pip install boto3` 或使用 `/opt/hermes/.venv/bin/python3`
- R2 凭证可访问（通过 `.env` 或环境变量）

所需的 R2 环境变量：
```
R2_ACCOUNT_ID=你的账户ID
R2_BUCKET=hermes-main
R2_ACCESS_KEY_ID=你的AccessKey
R2_SECRET_ACCESS_KEY=你的SecretKey
R2_PUBLIC_URL=https://hermes-main-media.devtoy.xyz
R2_ENDPOINT=https://你的账户ID.r2.cloudflarestorage.com
```

---

## 快速恢复（使用脚本）

```bash
# 1. 下载并运行恢复脚本
/opt/hermes/.venv/bin/python3 /opt/data/scripts/restore_from_r2.py

# 2. 重启 Hermes Gateway
hermes gateway restart

# 3. 验证
hermes doctor
```

---

## 手动恢复步骤

### 1. 列出 R2 中的可用备份

```python
from r2_uploader import R2Uploader
u = R2Uploader()
objs = u.list_objects(prefix='backups/')
for o in sorted(objs, key=lambda x: x['Key']):
    print(f"{o['Key']}  ({o['Size']/1024/1024:.1f} MB)")
```

### 2. 下载最新的备份

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url='https://你的账户ID.r2.cloudflarestorage.com',
    aws_access_key_id='你的AccessKey',
    aws_secret_access_key='你的SecretKey',
    region_name='auto',
    config=Config(signature_version='s3v4')
)

# 找到最新备份
resp = s3.list_objects_v2(Bucket='hermes-main', Prefix='backups/')
latest = sorted(resp['Contents'], key=lambda x: x['Key'])[-1]['Key']

# 下载
s3.download_file('hermes-main', latest, '/tmp/hermes_backup.tar.gz')
print(f'下载完成: {latest}')
```

### 3. 解压到 Docker volume

```bash
# 确保 Docker volume 挂载点正确
# 宿主机: ~/.hermes-main → 容器内: /opt/data

tar xzf /tmp/hermes_backup.tar.gz -C /opt/data/
```

### 4. 恢复配置文件权限

```bash
# 确保关键文件权限正确
chmod 600 /opt/data/.env
chmod 644 /opt/data/config.yaml
```

### 5. 重启 Hermes

```bash
# 容器内
hermes gateway restart

# 或 Docker 层面
docker restart <容器名>
```

### 6. 验证恢复

```bash
hermes doctor
hermes status
hermes cron list    # 检查 cron 作业是否恢复
```

---

## 备份内容说明

| 文件 | 备份位置 | 说明 |
|------|----------|------|
| `config.yaml` | `config.yaml` | Hermes 全配置（provider、平台、工具设置） |
| `.env` | `.env` | API 密钥和秘密（恢复后需 `chmod 600`） |
| `state.db` | `state.db` | 会话历史（SQLite，81MB→31MB 压缩） |
| `cron/jobs.json` | `cron/jobs.json` | 定时作业定义 |
| `pairing/` | `pairing/` | 平台用户授权记录 |
| `memories/` | `memories/` | 持久化记忆（MEMORY.md + USER.md） |
| `plugins/` | `plugins/` | 已安装插件状态 |
| 自定义脚本 | `custom/*.py` | `generate_news_card_v3.py`, `r2_uploader.py`, `collect_daily_data.py` |
| 全部 skill | `skills/*/` | 完整技能目录（含 SKILL.md + references + scripts + templates） |

---

## 恢复后需注意

1. **State.db 较大**：首次加载会话历史可能需要几秒
2. **Cron 作业**：恢复后检查 `hermes cron list`，确认所有作业状态正常
3. **配对记录**：用户授权记录在 `pairing/` 中，恢复后用户无需重新配对
4. **记忆**：`memories/` 恢复后 Hermes 会重新加载跨会话记忆
5. **插件**：插件本身需从 hub 重装，`plugins/` 仅恢复状态文件
6. **Skills**：agent-created skill 的 SKILL.md 已备份，但 hub skill 需 `hermes skills install <id>` 重装
7. **日切时间**：备份在北京时间 00:00 执行，当天新的会话数据可能未包含

---

## 恢复后重建 hub skills

备份中不包含从技能中心安装的 skills。恢复后需要重新安装：

```bash
# 列出备份中的 agent-created skills
# 这些不需要重装，已包含在备份中

# 重新安装常用 hub skills
hermes skills install agent-reach
hermes skills install cross-platform-format

# 查看全部可用 skills
hermes skills browse
```

---

## 故障排除

### R2 凭证错误

```
R2Uploader: missing credentials
```

确保 `.env` 或环境变量中包含：
```
R2_ACCOUNT_ID, R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
```

### boto3 未安装

```bash
/opt/hermes/.venv/bin/pip install boto3
# 或
cd /opt/data && uv pip install boto3
```

### 备份文件损坏

```bash
# 验证 tar.gz 完整性
tar tzf /tmp/hermes_backup.tar.gz > /dev/null && echo "OK" || echo "损坏"

# 如果损坏，尝试前一天的备份
```
