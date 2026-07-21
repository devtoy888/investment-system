# Docker Compose 升级流程

适用于 Docker Compose 部署的 Hermes 实例（非 pip/源码安装）。

## 标准升级步骤

```bash
cd /path/to/your/docker-compose-dir
docker compose pull    # 拉最新镜像
docker compose up -d   # 重建容器
```

> **注意：** `:latest` tag 追踪的是 GitHub 主分支，不一定是正式 release。`hermes --version` 显示的还是旧版本号（如 0.17.0），但 `importlib.metadata.version('hermes-agent')` 显示的实际版本可能是 0.18.0。如果想升级到特定 release，在 compose 的 `image:` 里改用具体 tag（如 `nousresearch/hermes-agent:v2026.7.1`）。
>
> **坑：** `latest` tag 和 `v2026.7.1` tag 可能是**两套不同的镜像**（digest 不同）。`docker compose pull` 多次后 build SHA 会变（新 commit），但版本号可能一直不变。用特定 tag 确保拿到 release 版本。

## 升级后检查清单

```bash
# 1. 版本确认
hermes --version

# 2. 所有平台是否在线
# 查看 gateway.log: "Gateway running with N platform(s)"

# 3. Dashboard 是否可访问
curl -s -o /dev/null -w "%{http_code}" http://localhost:9119/

# 4. 飞书/钉钉等懒安装依赖是否正常
# 检查 gateway.log 是否有 "✓ feishu connected"
```

## 已知 Breaking Changes

### v0.18.0: `HERMES_DASHBOARD_INSECURE` 废弃

Dashboard 不再接受 `HERMES_DASHBOARD_INSECURE=1` 跳过认证。
非 loopback 地址（`0.0.0.0`）绑定需要：
- **方案A（Basic Auth）：**
  ```yaml
  environment:
    - HERMES_DASHBOARD_BASIC_AUTH_USERNAME=你的用户名
    - HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=你的密码
  ```
- **方案B（`--insecure`，不推荐）：**
  修改 s6 Dashboard 启动脚本加入 `--insecure` 参数

### Docker 环境 PYTHONPATH 要求

Docker 镜像的 venv 是只读的（`chmod -R a-w /opt/hermes`），懒安装不可用（`HERMES_DISABLE_LAZY_INSTALLS=1`）。依赖懒安装的插件（飞书 `lark-oapi`、钉钉 `dingtalk-stream`）需要通过 PYTHONPATH 加载：

```yaml
environment:
  - "PYTHONPATH=/opt/data/home/.venvs/firecrawl/lib/python3.13/site-packages:"
```

这条必须配在 `docker-compose.yml` 的 `environment` 里（才能被 Python 解释器在初始化时读到），配在容器内部的 `.env` 文件无效——因为 `.env` 在 Python 启动后才加载，来不及影响 `sys.path`。

## Dashboard 502 排查流程

1. 检查容器内 Dashboard 是否响应：`curl -s http://localhost:9119/`
2. 检查 Dashboard 进程状态：`ps aux | grep dashboard`
3. 检查是否有端口监听：`cat /proc/net/tcp | grep 239F`（239F = 9119 的十六进制）
4. 手动运行排查报错：`hermes dashboard --host 0.0.0.0 --port 9119 --no-open`
5. 常见原因：auth gate 阻止绑定（v0.18.0+）、进程卡死（100% CPU 无端口监听）
