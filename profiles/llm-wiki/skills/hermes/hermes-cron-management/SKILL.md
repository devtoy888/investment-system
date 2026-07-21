---
name: hermes-cron-management
description: "Manage Hermes Agent cron jobs in Docker deployments — create, migrate from system cron, diagnose failures, consolidate redundant jobs, and verify execution."
version: 1.0.0
author: Hermes Agent
tags: [hermes, cron, scheduling, docker, container]
---

# Hermes Cron Management

Manage Hermes Agent's built-in cron system for scheduled tasks, especially in Docker deployments where `docker restart` calls fail without mounting the Docker socket.

## Cron Job Types

| Type | `no_agent` value | Behavior |
|------|------------------|----------|
| **Script job** | `true` | Runs script directly (shell/Python). Stdout delivered as message. Zero LLM cost. |
| **Agent job** | `false` (default) | Agent receives prompt + loads skills. Higher cost, supports reasoning. |

## Script Discovery Path

Cron scripts are resolved relative to `~/profiles/<profile>/scripts/`:

```bash
# For profile "llm-wiki":
# Script "wiki-push.sh" → /opt/data/profiles/llm-wiki/scripts/wiki-push.sh
# Can also use absolute paths like /llm-wiki/scripts/wiki-push.sh
```

## Docker Integration: Container Restart from Cron

### The Problem

Cron scripts running inside `hermes-main` container cannot call `docker restart llm-wiki` because:

| Check | Status | Why |
|-------|--------|-----|
| `docker` CLI | ✅ Installed | Hermes image bundles it |
| `/var/run/docker.sock` | ❌ Not mounted | Must be added to docker-compose |

### The Fix: Mount Docker Socket

In `docker-compose.yml`, add the socket volume:

```yaml
services:
  hermes-main:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock   # ← Add this
```

Then restart only hermes-main (no `docker compose down` — that doesn't accept service names):

```bash
cd ~/apps/hermes
docker compose up -d hermes-main   # Recreates only hermes-main
```

Verify:

```bash
docker exec hermes-main docker ps
# Should list all containers including llm-wiki
```

### Script Templates for Restart

**Shell:**
```bash
if command -v docker &>/dev/null && docker ps -q --filter name=llm-wiki 2>/dev/null | grep -q .; then
  docker restart llm-wiki >/dev/null 2>&1
else
  echo "WARNING: docker restart failed"
fi
```

**Python:**
```python
import subprocess
r = subprocess.run(['docker', 'restart', 'llm-wiki'],
                    capture_output=True, text=True, timeout=30)
print('restarted' if r.returncode == 0 else f'err: {r.stderr}')
```

## Migration: System Cron → Hermes Cron

### When to Migrate

Prefer Hermes cron when:
- You want a single scheduling system (all cron in one place)
- Scripts need to run inside the container (access to mounted wiki files)
- You want unified error reporting (deliver to chat platform)

Keep system cron when:
- Task truly must run on host (e.g., system-level commands outside Docker)
- The task has no container dependency

### Migration Steps

1. **Create wrapper script** in profile's scripts dir:
   ```bash
   cat > /opt/data/profiles/llm-wiki/scripts/wiki-push.sh << 'EOF'
   #!/bin/bash
   exec /llm-wiki/scripts/wiki-push.sh
   EOF
   chmod +x /opt/data/profiles/llm-wiki/scripts/wiki-push.sh
   ```

2. **Fix container-internal paths** — scripts using `~/` inside the container may resolve differently:
   ```bash
   # Container HOME ≠ host HOME. Inside container:
   # HOME=/opt/data/profiles/llm-wiki/home (NOT /home/devtoy)
   # Always use absolute paths: cd /llm-wiki NOT cd ~/llm-wiki
   ```

3. **Create Hermes cron job**:
   ```
   action=create
   name=wiki-push
   schedule="0 19 * * *"        # UTC = CST 03:00
   script=wiki-push.sh
   no_agent=true
   deliver=local                 # or platform channel
   ```

4. **Delete system crontab entries**:
   ```bash
   crontab -e
   # Remove migrated entries
   ```

## Consolidating Redundant Jobs

### When to Consolidate

Multiple cron jobs that:
- Write to different files but are part of the same logical workflow
- Both trigger a container restart afterward
- Can safely run sequentially

### Pattern: One Job, One Restart

Before (bad — 2 restarts in 30 min):
```
02:00 CST  graph-rebuild  → build graph  → restart llm-wiki
02:30 CST  auto-nav-sync  → update nav   → restart llm-wiki
```

After (good — 1 combined job):
```
02:00 CST  nightly-build  → build graph + update nav → restart llm-wiki (once)
```

### Combined Script Template

```bash
#!/bin/bash
set -e
echo "=== Nightly Build: $(date) ==="

echo "[1/2] Task A..."
python3 /path/to/task-a.py

echo "[2/2] Task B..."
python3 /path/to/task-b.py

echo "Restarting container..."
docker restart llm-wiki

echo "=== Done at $(date) ==="
```

## Timezone Handling

Hermes cron schedules in **UTC**. Convert to/from local time (e.g. CST = UTC+8):

| CST (Beijing) | UTC | Example |
|---------------|-----|---------|
| 02:00 | `0 18 * * *` | Nightly build |
| 03:00 | `0 19 * * *` | Git push |
| Every 6h | `0 */6 * * *` | Cleanup |

## Verification

### Check Scheduled Jobs

```bash
# In Hermes session:
cronjob action=list

# Output shows: job_id, name, schedule (UTC), last_status, next_run_at
```

### Test Run a Script

```bash
# Run once to verify:
docker exec hermes-main /opt/data/profiles/llm-wiki/scripts/nightly-build.sh
```

### Verify Docker Restart

After Docker socket fix:

```bash
# From inside the container:
docker ps --filter name=llm-wiki --format '{{.Names}} {{.Status}}'
# Expected: llm-wiki Up X minutes
```

## Cleanup: Old Cron Jobs

Remove orphan cron jobs (scripts that no longer exist or tasks that were consolidated):

```bash
cronjob action=remove job_id=<id>
```

Old scripts in `~/profiles/<profile>/scripts/` can be cleaned up after verifying no job references them.

## Session Cleanup by Source Platform

Cron jobs and other platform conversations create sessions. Use SQLite queries to batch-delete by `source` field:

```python
import sqlite3, subprocess

HERMES = '/opt/hermes/bin/hermes'
DB = '/opt/data/profiles/llm-wiki/state.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT id, title FROM sessions WHERE source = 'feishu'")
to_delete = cur.fetchall()
conn.close()

for sid, title in to_delete:
    r = subprocess.run([HERMES, 'sessions', 'delete', sid],
                       input='y\n', capture_output=True, text=True, timeout=10)
    status = '✓' if 'Deleted' in r.stdout else '✗'
    print(f'  {status} {sid[:35]} {title or ""}')
```

This pattern avoids the `--older-than` flag's platform filter and allows precise selection.

## Pitfalls

### 1. `docker compose down <service>` does NOT work

```bash
# WRONG — "unknown command"
docker compose down hermes-main   

# CORRECT — recreates only that service
docker compose up -d hermes-main
```

### 2. Container HOME ≠ host HOME

Inside the container, `~` resolves to the profile's home dir, NOT the host user's home:
- Host: `~` = `/home/devtoy`
- Container: `~` = `/opt/data/profiles/llm-wiki/home`

Always use **absolute paths** in cron scripts: `cd /llm-wiki` not `cd ~/llm-wiki`.

### 3. Hermes binary not in PATH

The `hermes` binary may not be in the container's default PATH. Locate it:

```bash
find /opt -name hermes -type f 2>/dev/null
# Usually at: /opt/hermes/bin/hermes
```

### 4. `hermes sessions delete` needs confirmation

```bash
# Without confirmation, deletion is silently cancelled (exit code 0):
hermes sessions delete SESSION_ID   # WON'T actually delete

# CORRECT: pipe 'y' to confirm:
echo 'y' | hermes sessions delete SESSION_ID
```

### 5. Cron script path resolution

Scripts referenced by name (e.g. `script: nightly-build.sh`) are resolved under `~/profiles/<profile>/scripts/`. If the script is elsewhere, use the absolute path or create a thin wrapper.

### 6. System crontab may use different timezone than Hermes

System cron uses **system local time** (usually CST for Chinese users), while Hermes cron uses **UTC**. When migrating, convert the schedule:
- Host `0 3 * * *` (CST) → Hermes `0 19 * * *` (UTC)
