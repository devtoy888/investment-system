# Gateway Config Not Taking Effect — Debugging Guide

## The Problem

You edited `config.yaml` and/or `.env`, verified the values are correct, created a new TUI session (`/new`), but the session still uses the old model (e.g. `deepseek-chat` instead of `gemini-2.0-flash`).

## Root Causes (in order of likelihood)

### 1. Gateway process didn't restart (MOST COMMON)
The Gateway loads config at startup. Editing config.yaml does NOT cause it to re-read. You must restart it.

**Check:**
```bash
# Has the Gateway PID changed since you edited config?
ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2}'
```

**Fix:** Kill the gateway — s6 auto-restarts with new config:
```bash
kill -KILL $(ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2}')
sleep 8
ps aux | grep "hermes gateway" | grep -v grep  # Should show NEW PID
```

### 2. Gateway process doesn't have the API key in its env

Even if `.env` has the key, the Gateway may not load it.

**Check:**
```bash
GW_PID=$(ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2}')
cat /proc/$GW_PID/environ 2>/dev/null | tr '\0' '\n' | grep 'GOOGLE_API_KEY\|OPENROUTER'
```
If empty → the s6 run script is the issue.

**Fix:** See `s6-gateway-env-loading.md` for the correct run script.

### 3. base_url is empty (Gemini-specific)

When `model.base_url: ''` in config.yaml, `is_native_gemini_base_url("")` returns False.
The Gemini Native Client is bypassed, standard HTTP client targets empty URL → fails → falls to DeepSeek.

**Check:**
```bash
grep "base_url:" /opt/data/config.yaml
```

**Fix:** Set the correct base_url:
```yaml
model:
  default: gemini-2.0-flash
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

### 4. Provider name is wrong

Use `gemini`, NOT `google`.

**Check:**
```bash
grep "provider:" /opt/data/config.yaml
```

**Fix:** `sed -i 's/provider: google/provider: gemini/' /opt/data/config.yaml`

### 5. Session was created before Gateway restart

Old TUI sessions persist with their startup config. `/new` in TUI still uses the old Gateway config if the Gateway wasn't restarted. Close the TUI and reopen.

## End-to-End Verification Script

```bash
#!/bin/bash
echo "=== 1. Config ==="
grep -A4 "^model:" /opt/data/config.yaml

echo "=== 2. Gateway PID ==="
GW_PID=$(ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2}')
echo "PID: $GW_PID"

echo "=== 3. Gateway Env Keys ==="
cat /proc/$GW_PID/environ 2>/dev/null | tr '\0' '\n' | grep -E 'GOOGLE|OPENROUTER|DEEPSEEK|HF_TOKEN' || echo "NONE FOUND"

echo "=== 4. Runtime Resolution ==="
cd /opt/data && . /opt/hermes/.venv/bin/activate && python3 -c "
from hermes_cli.runtime_provider import resolve_runtime_provider
r = resolve_runtime_provider(requested=None)
print(f'provider={r.get(\"provider\")}, base_url={r.get(\"base_url\")}')
print(f'api_key present: {bool(r.get(\"api_key\"))}')
"

echo "=== 5. Gemini Native Client Check ==="
cd /opt/data && . /opt/hermes/.venv/bin/activate && python3 -c "
from agent.gemini_native_adapter import is_native_gemini_base_url
url = open('/opt/data/config.yaml').read().split(\"base_url:\")[1].s...\\n').strip()
print(f'Will use native client: {is_native_gemini_base_url(url)}')
"
```
