---
name: remote-server-disk-analysis
description: Connect to remote Linux servers via SSH and analyze disk usage, identify garbage files, and recommend cleanup. Includes SSH key setup from .env, connection debugging, and systematic scanning.
---

# Remote Server Disk Analysis

Connect to a remote Linux host, scan for reclaimable disk space, and produce a prioritized cleanup report.

## Prerequisites

- SSH key stored in `.env` (see `references/ssh-key-from-env.md` for format help)
- Username, IP, and port configured as env variables

> **⚠️ Host vs remote distinction:** The SSH target may be the Docker host of the current container, not an independent server. Always note this relationship in your report so the user knows what machine is being analyzed. When the target is the container's host, cleaning its Docker images can affect the running container.

## SSH Connection Procedure

### 1. Extract SSH key from `.env`

Keys are often stored with literal `\n` escape sequences inside double-quoted values. Handle them with Python:

```python
with open('/opt/data/.env') as f:
    content = f.read()

import re
m = re.search(r'REMOTE_HOST_SSH_KEY="(.*?)"(?:\n|$)', content, re.DOTALL)
if m:
    raw = m.group(1)
    key = raw.replace('\\n', '\n').strip()  # convert literal \n to real newlines

    import os, stat
    os.makedirs(os.path.expanduser('~/.ssh'), mode=0o700, exist_ok=True)
    key_path = os.path.expanduser('~/.ssh/id_rsa')
    with open(key_path, 'w') as f:
        f.write(key)
        if not key.endswith('\n'):
            f.write('\n')  # trailing newline is required
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
```

### 2. Verify key

```bash
ssh-keygen -lf ~/.ssh/id_rsa
```

If this fails, try Python's cryptography library as an alternative validator:
```python
from cryptography.hazmat.primitives import serialization
with open('~/.ssh/id_rsa', 'rb') as f:
    key = serialization.load_ssh_private_key(f.read(), password=None)
```

### 3. Test connection

```bash
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    -o BatchMode=yes -o IdentitiesOnly=yes devtoy@<IP> 'echo SSH_OK'
```

**Debugging tips:**
- If "error in libcrypto" → key file format is corrupted (check `\n` escaping, trailing newline, hidden chars)
- If "Permission denied" after a working connection → the known_hosts or key identity changed; add `-v` to diagnose
- Use `-tt` flag for commands requiring sudo/password on the remote host

## Remote Scanning Checklist

Run the following in order of descending impact:

### 1. Docker waste
```bash
docker system df                          # overview
docker system df -v                       # detailed per-image
docker images                             # list all images
docker ps -a                              # all containers
# Clean unused images:
docker image prune -a                     # removes images with no running container
# Or specific:
docker rmi <repo>:<tag>                   # remove a specific unused image
```

### 2. Journald logs
```bash
journalctl --disk-usage
# Limit size:
sudo journalctl --vacuum-time=7d          # keep 7 days
# Or set permanent limit in /etc/systemd/journald.conf:
# SystemMaxUse=200M
```

### 3. Old kernels
```bash
dpkg -l 'linux-image-*' | grep '^ii' | awk '{print $2, $3}'
sudo apt purge linux-image-<old-version> -y
sudo apt autoremove --purge -y
```

### 4. /var/log - big items
```bash
sudo du -sh /var/log/*/ | sort -rh | head -10
sudo ls -lhS /var/log/*.log | head -10
# /var/log/lastlog can be a large sparse file:
sudo truncate -s 0 /var/log/lastlog
```

### 5. Package cache
```bash
du -sh /var/cache/apt/archives/
sudo apt clean
```

### 6. Home directory waste
```bash
du -sh ~/.npm/ ~/.nvm/ ~/.cache/ ~/tmp/
# npm cache:
rm -rf ~/.npm/_cacache
# nvm - check which Node versions are installed:
ls ~/.nvm/versions/node/
for v in ~/.nvm/versions/node/*/; do echo "$(du -sh "$v" | cut -f1)  $(basename "$v")"; done
# Remove old versions (keep the 2 most recent):
rm -rf ~/.nvm/versions/node/v18* ~/.nvm/versions/node/v20*
# /tmp:
rm -rf ~/tmp/*
```

### 7. Rare check
```bash
snap list 2>/dev/null                     # snap packages (often on Ubuntu)
```

## Reporting Format

Present findings in a table sorted by reclaimable size:

| Item | Size | Status | Command |
|------|------|--------|---------|
| Docker unused images | 3.4 GB | ✅ Actionable | `docker image prune -a` |
| Old kernel 5.19 | 200 MB | ✅ Safe | `apt purge` |
| Journald | 8 MB | ✅ Already clean | — |
| ... | ... | ... | ... |
| **Total** | **~4 GB** | | |

Always note what the user has already cleaned to avoid redundant suggestions.

## Pitfalls

- `.env` shell sourcing can hang on keys with special characters — always use Python for extraction
- The .env key may have a MIX of real newlines AND literal `\n` escapes — use the quote-parsing approach, not `str.replace`
- SSH key file must end with a trailing newline or `ssh-keygen` may reject it (even though `cryptography` may parse it fine)
- Sudo commands on remote host require `-tt` flag for SSH TTY allocation but still need password; skip sudo items if the host requires interactive auth
- `BatchMode=yes` prevents password prompts but also blocks sudo — use separate non-sudo checks first
- Docker images with `<none>` tag may still be in use by running containers — check `docker ps -a` before deleting
- `openclaw` images are large (>3GB) and often Dockerized game servers — confirm no one is using them
- If an SSH connection fails after a successful one, the `IdentitiesOnly=yes` flag can help — the SSH agent may be offering a different key
- The remote host may be the Docker HOST of the current container — cleaning its Docker images can inadvertently impact the running environment
