# s6 `down` File: Per-Profile Gateway Control

In Docker s6-overlay deployments, each Hermes profile gets a supervised gateway service at `/run/service/gateway-<name>/`.

## The `down` File

When this directory contains an empty file named `down`, s6 **intentionally stops** that service — it won't start the process.

```bash
# Check if a profile gateway is intentionally stopped
test -f /run/service/gateway-llm-wiki/down && echo "STOPPED by down flag" || echo "RUNNING or not supervised"
```

## When `down` Appears

Setting `gateway.multiplex_profiles: true` causes the boot-time reconciler to flag secondary profiles as `down` (multiplexing mode requires secondary profiles to NOT run their own gateway).

## Fix: Per-Profile Gateway Mode (Docker Recommended)

The official Docker documentation recommends ONE container with per-profile s6-supervised gateways (not multiplexing, not separate containers).

To fix a `down`-flagged secondary profile:

```bash
# 1. Disable multiplex (not needed for Docker s6 architecture)
hermes config set gateway.multiplex_profiles false

# 2. Remove the down flag
rm /run/service/gateway-llm-wiki/down

# 3. Start the gateway (s6 takes over lifecycle)
hermes -p llm-wiki gateway start
```

## Verification

Both gateways should run as separate s6-supervised processes:

```bash
ps aux | grep "gateway run" | grep -v grep
# Expected: TWO python3 hermes processes (default + llm-wiki)

# Check s6 supervisor status
ls /run/service/gateway-llm-wiki/down 2>/dev/null && echo "STOPPED" || echo "ACTIVE"
```

## Lifecycle Commands

From the Docker host:

```bash
# Start
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && hermes -p llm-wiki gateway start'

# Stop
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && hermes -p llm-wiki gateway stop'

# Restart
docker exec hermes-main bash -c 'export PATH=$PATH:/opt/data/.local/bin && hermes -p llm-wiki gateway restart'
```

The `hermes gateway start/stop/restart` commands inside the container are intercepted and routed to `s6-svc` against the right service directory.
