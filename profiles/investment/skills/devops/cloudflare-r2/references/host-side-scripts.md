# Running R2 Scripts from the Host

## Problem

R2 scripts (`r2_uploader.py`, `wiki_upload.py`, etc.) running inside the Docker container have env vars available (`R2_ACCOUNT_ID`, etc.). But when run from the host (Termius, crontab, script calls), the env vars are NOT set in the shell.

## Solution: `load_env()`

Add a `load_env()` function at the top of any script that must work both in-container and on-host:

```python
import os

def load_env():
    """Load R2 credentials from .env files if not already in environment."""
    if all(os.environ.get(v) for v in ['R2_ACCOUNT_ID', 'R2_BUCKET',
                                         'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY']):
        return  # Already set — likely running inside Docker
    for path in [os.path.expanduser('~/.hermes-main/.env'), '/opt/data/.env']:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('R2_') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k, v)
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
