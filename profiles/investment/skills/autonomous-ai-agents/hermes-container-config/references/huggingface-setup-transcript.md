# HuggingFace Hub Setup Session (2026-06-21)

## Context
User already had Gemini 2.0 Flash (free primary) + OpenRouter free models (auxiliary tasks). Wanted to add HuggingFace as another free fallback.

## Steps Taken

### 1. Adding HF_TOKEN to .env
The user provided token: `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`

**Shell escaping issue:** When using `echo 'HF_TOKEN=*** >> /opt/data/.env`, the key got truncated to `***`. 

**Fix: Base64 encoding workaround**
```python
import base64
# First, encode the key: base64.b64encode(b"hf_VKumx...").decode()
encoded_b64 = "aGZfVkt1bXhOTHdXcG5ib2V4dlJtV2hhVnJUYVVIQ3lYQ1RLTg=="
key = base64.b64decode(encoded_b64).decode()
open('/opt/data/.env','a').write('HF_TOKEN=' + key + '\n')
```

**Verification:**
```bash
grep "^HF_TOKEN" /opt/data/.env | od -c
# 0000000   H   F   _   T   O   K   E   N   =   h   f   _   V   K   u   m
# 0000020   x   N   L   w   W   p   n   b   o   e   x   v   R   m   W   h
# 0000040   a   V   r   T   a   U   H   C   y   X   C   T   K   N  \n
# 0000057
```
47 bytes total = 9 (HF_TOKEN=) + 37 (key) + 1 (\n) — correct!

### 2. Tested API Connectivity
```bash
python3 -c "
with open('/opt/data/.env') as f:
    for line in f:
        if line.startswith('HF_TOKEN='):
            token = line.split('=', 1)[1].strip()
import urllib.request, json
req = urllib.request.Request('https://huggingface.co/api/whoami-v2', headers={'Authorization': f'Bearer {token}'})
resp = urllib.request.urlopen(req, timeout=15)
print(f'User: {json.loads(resp.read()).get(\"name\", \"N/A\")}')
"
```
Result: `User: devtoy` ✅ — Token valid, Hub API accessible.

### 3. Checked Inference API DNS
```python
import socket
try:
    socket.getaddrinfo('api-inference.huggingface.co', 443)
    print('available')
except socket.gaierror:
    print('DNS blocked')
```
Result: **DNS blocked** on this Oracle Cloud server (`api-inference.huggingface.co` does not resolve).

Alternative endpoints that DO resolve:
- `huggingface.co` ✅
- `router.huggingface.co` ✅
- `hf.co` ✅

### 4. Tried huggingface_hub library
Installed via `uv pip install huggingface-hub --target /opt/data/.hf-deps`
- Hub API works
- `InferenceClient` fails with "Bad request" — because underlying DNS to `api-inference.huggingface.co` is blocked

### 5. Added to Fallback Chain
Extended the fallback chain in config.yaml:

Old:
```yaml
fallback_providers:
  - provider: deepseek
    model: deepseek-v4-flash
```

New:
```yaml
fallback_providers:
  - provider: deepseek
    model: deepseek-v4-flash
  - provider: huggingface
    model: Qwen/Qwen2.5-1.5B-Instruct
```

### 6. Gateway Restart
```bash
kill -HUP $(ps aux | grep 'hermes gateway' | grep -v grep | awk '{print $2}')
sleep 3
```
PID 6117 → 6764, confirming clean restart.

## Limitations on Oracle Cloud
- HuggingFace Inference API (`api-inference.huggingface.co`) has DNS resolution failure
- Only Hub API (`huggingface.co/api/...`) works
- HF token is useful for model downloads and Hub operations but cannot do real-time inference
- This is a deployment environment limitation, not a token/key issue

## Key Learnings
- **Shell escaping is a real issue for .env keys** — Always verify with `od -c` and `wc -c`
- **Base64 encoding bypasses shell interpretation** — Encode the key in Python, write via Python
- **HuggingFace has separate endpoints** — Hub API and Inference API use different subdomains
- **Oracle Cloud blocks some API subdomains** — `api-inference.huggingface.co` is blocked but general `huggingface.co` is not
- **Multi-level fallback chain** — You can have multiple fallback providers, not just one
