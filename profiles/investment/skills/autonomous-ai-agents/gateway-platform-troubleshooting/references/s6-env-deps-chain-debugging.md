# s6 Environment & Python Deps Chain Debugging

In Docker/s6 container deployments, Hermes dependencies may be spread across 
two Python `site-packages` directories:
- **Read-only**: `/opt/hermes/.venv/lib/python3.13/site-packages/` (owned by root, 
  baked into the Docker image)
- **Writable**: `/opt/data/.feishu-deps/` (user-writable, for lazy-installed extras 
  and manual `--target` installs)

## How the Writable Path Gets Added to sys.path

The chain is non-obvious:

1. Interactive shell sets `PYTHONPATH=/opt/data/home/.venvs/firecrawl/lib/python3.13/site-packages:`
2. Python finds that dir → scans for `.pth` files
3. `/opt/data/home/.venvs/firecrawl/lib/python3.13/site-packages/hermes_feishu_deps.pth` 
   contains the line `/opt/data/.feishu-deps`
4. Python processes the `.pth` → `/opt/data/.feishu-deps/` is added to `sys.path`
5. Package imports resolve to `/opt/data/.feishu-deps/lark_oapi/` etc.

## Why Gateway Can't Find the Deps

The gateway runs under **s6 supervision**, which has its own environment
at `/run/s6/container_environment/`. Two critical gaps exist:

```bash
# Check what s6 passes to the gateway
ls /run/s6/container_environment/
cat /run/s6/container_environment/PYTHONPATH 2>/dev/null
# → (not set) — no PYTHONPATH file exists

cat /run/s6/container_environment/HERMES_DISABLE_LAZY_INSTALLS 2>/dev/null
# → 1 — lazy installs are disabled
```

**Without `PYTHONPATH`:** The `.pth` chain never starts → `.feishu-deps` not on 
`sys.path` → `lark_oapi` is unimportable.

**With `HERMES_DISABLE_LAZY_INSTALLS=1`:** Even if the package were importable,
`ensure_and_bind()` in `tools/lazy_deps.py` checks `_allow_lazy_installs()` first
and exits early before calling the `importer()` function that would import 
`lark_oapi`.

## Diagnostic Commands

```bash
# 1. Check s6 env for PYTHONPATH
cat /run/s6/container_environment/PYTHONPATH 2>/dev/null || echo "NOT SET"

# 2. Check gateway process env
GATEWAY_PID=$(ps aux | grep 'hermes gateway run' | grep -v grep | awk '{print $2}' | head -1)
cat /proc/$GATEWAY_PID/environ 2>/dev/null | tr '\0' '\n' | grep PYTHONPATH || echo "NOT IN PROCESS"

# 3. Check if PYTHONPATH is set in interactive shell (for comparison)
echo "Shell PYTHONPATH: ${PYTHONPATH:-NOT SET}"

# 4. Confirm the .pth chain exists
cat /opt/data/home/.venvs/firecrawl/lib/python3.13/site-packages/hermes_feishu_deps.pth 2>/dev/null
# Expected: /opt/data/.feishu-deps

# 5. Confirm lark_oapi is in .feishu-deps
ls /opt/data/.feishu-deps/lark_oapi 2>/dev/null || echo "NOT FOUND"
ls /opt/data/.feishu-deps/lark_oapi-*.dist-info 2>/dev/null || echo "NOT FOUND"

# 6. Test import using gateway's Python
/opt/hermes/.venv/bin/python3 -c "import lark_oapi; print(lark_oapi.__file__)" 2>&1
```

## Fix

Add `PYTHONPATH` to the s6 container environment so the gateway process 
inherits it:

```bash
echo "/opt/data/home/.venvs/firecrawl/lib/python3.13/site-packages:" \
  > /run/s6/container_environment/PYTHONPATH

# Then restart the gateway (s6 restart, not just gateway restart)
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/

# Wait and verify
sleep 8
grep -i "feishu\|lark" /opt/data/logs/gateway.log | tail -5
```

## How it Worked Before the Restart

The original gateway established Feishu WebSocket connections before the
s6 environment gaps became relevant. After any gateway restart, the adapter
must be created from scratch — which requires satisfying both the PYTHONPATH
and lazy-install checks. This is why Feishu can work for days then stop
working after a single gateway restart with no config changes.
