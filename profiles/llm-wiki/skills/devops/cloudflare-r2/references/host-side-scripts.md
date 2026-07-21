# Running R2 Scripts from the Host
## Problem
R2 scripts (`r2_uploader.py`, `wiki_upload.py`, etc.) running inside the Docker container have env vars available (`R2_ACCOUNT_ID`, etc.). But when run from the host (Termius, crontab, script calls), the env vars are NOT set in the shell.

## Solution: `load_env()`
Add a `load_env()` function at the top of any script that must work both in-container and on-host:
```python
import os, glob

def load_env():
    """Load R2 credentials from .env files if not already in environment."""
    if all(os.environ.get(v) for v in ['R2_ACCOUNT_ID', 'R2_BUCKET',
                                         'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY']):
        return  # Already set — likely running inside Docker
    # ⚠️ 多 profile：凭据按当前 profile 读，禁止跨 profile 读主 profile 的 .env
    # Docker 映射：宿主机 ~/.hermes-main → 容器 /opt/data
    #   主 profile   ：~/.hermes-main/.env          → /opt/data/.env
    #   llm-wiki   ：~/.hermes-main/profiles/llm-wiki/.env → /opt/data/profiles/llm-wiki/.env
    #   其他 profile：~/.hermes-main/profiles/<name>/.env    → /opt/data/profiles/<name>/.env
    # 用 glob 自动覆盖所有 profile，不写死主 profile 路径。
    paths = ['/opt/data/.env'] + sorted(glob.glob('/opt/data/profiles/*/.env'))
    # 兼容宿主机直接运行
    paths += [os.path.expanduser('~/.hermes-main/.env')] + sorted(
        glob.glob(os.path.expanduser('~/.hermes-main/profiles/*/.env')))
    for path in paths:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('R2_') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k, v)
            # 命中一个 profile 即可返回（避免把别的 profile 变量 setdefault 进来导致 bucket 错配）
            return
```

## Usage Pattern
```python
load_env()
from r2_uploader import R2Uploader
uploader = R2Uploader()  # Now reads from env (host) or injected vars (container)
```

## Key Paths
| Environment | Env file location | Script import path |
|-------------|-------------------|-------------------|
| Docker container | `/opt/data/.env` | `/opt/data/r2_uploader.py` |
| Host (Termius) | `~/.hermes-main/.env` | `~/llm-wiki/scripts/r2_uploader.py` |

## Pitfall: `os.environ.setdefault` vs direct assignment
Use `setdefault()` so host-loaded values don't override container-injected values (which have higher priority by design).

## ⚠️ CRITICAL Pitfall (2026-07-18): 跨 profile 读取 .env 是错误
- 原模板写死 `[os.path.expanduser('~/.hermes-main/.env'), '/opt/data/.env']`，**只覆盖主 profile**。
- 实际每个 profile 的凭据在 `~/.hermes-main/profiles/<name>/.env`（容器内 `/opt/data/profiles/<name>/.env`）。
- **错误示例**：llm-wiki profile 的会话里直接套用主 profile 模板 → 读到主 profile 的 R2 凭据（bucket 恰好相同才"碰巧成功"，但属于跨 profile 越权）。
- **正确做法**：用 `glob.glob('/opt/data/profiles/*/.env')` 自动枚举所有 profile，命中第一个存在的即返回；宿主机同理用 `~/.hermes-main/profiles/*/.env`。
- **判定当前 profile**：会话运行于容器内 `/opt/data` 时，优先匹配 `/opt/data/profiles/<当前profile>/.env`。若不确定当前 profile，枚举全部并在日志打印命中的路径。
