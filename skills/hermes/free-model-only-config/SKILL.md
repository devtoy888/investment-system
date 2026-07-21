---
name: free-model-only-config
description: "Configure Hermes to use ONLY free models as primary, with paid models as last resort only. Based on real availability testing — most OpenRouter free models are broken."
version: 2.1.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, configuration, free-tier, openrouter, providers]
    related_skills: [hermes-container-config, hermes-agent]
---

# Free-Only Model Configuration

Configure Hermes to prioritize **completely free models** via OpenRouter, with paid DeepSeek only as the absolute last resort. **Most OpenRouter free models are NOT functional** — this skill only documents proven-working models.

## 🔥 The Reality of OpenRouter Free Models

Tested 2026-06-22 from Oracle Cloud (x86_64, Singapore region):

| Model | Result | Detail |
|-------|--------|--------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | ❌ TIMEOUT | No response in 20s |
| `nvidia/nemotron-3-super-120b-a12b:free` | ❌ TIMEOUT | No response in 20s |
| `qwen/qwen3-coder:free` | ❌ TIMEOUT | No response in 20s |
| `meta-llama/llama-3.3-70b-instruct:free` | ❌ TIMEOUT | No response in 20s |
| `meta-llama/llama-3.2-3b-instruct:free` | ❌ 429 | Venice upstream rate limit |
| `nousresearch/hermes-3-llama-3.1-405b:free` | ❌ 429 | Venice upstream rate limit |
| `openrouter/free` | ⚠️ ROUTES to content-safety | Routes to `nemotron-3.5-content-safety` — useless for chat |
| **`cohere/north-mini-code:free`** | ✅ WORKS | 30B/3B active, 256K ctx, fast (~1s) |
| **`google/gemma-4-31b-it:free`** | ✅ WORKS | 30.7B dense, 262K ctx, fast (~1s) |
| **`tencent/hy3:free`** | ✅ WORKS (added 2026-07-15) | 295B MoE/21B active, 262K ctx, tool-calling, reasoning — free until Jul 21, 2026 |

**Conclusion: Only 3 of 15+ free text models work. Long fallback chains full of broken models cause multi-minute timeouts.**

## Free Vision Models (OpenRouter)

Hermes uses an **auxiliary vision model** for image analysis (`vision_analyze` tool) when the main model lacks native vision. The default (`google/gemini-2.0-flash-lite`) is often unavailable or deprecated. Configure a working free alternative.

### Availability (tested 2026-06-22)

| Model | Status | Notes |
|-------|--------|-------|
| `google/gemma-4-31b-it:free` | ❌ 429 | Too popular — constant rate limiting |
| `google/gemma-4-26b-a4b-it:free` | ❌ 429 | Same issue |
| **`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`** | ✅ BEST | Text+image+video+audio, most detailed responses |
| **`nvidia/nemotron-nano-12b-v2-vl:free`** | ✅ BACKUP | Dedicated VL model, works but less detailed |

Full test transcripts: `references/openrouter-free-vision-model-tests.md`

### Configuration

```bash
hermes config set auxiliary.vision.model nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
hermes config set auxiliary.vision.provider openrouter

# Verify
hermes config | grep -A 2 "Vision"
# Expected:
#   Vision  provider=openrouter, model=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
```

**⚠️ Session restart required** — the `vision_analyze` tool reads this config at session start. `/reset` (CLI) or `/restart` (gateway) for changes to take effect.

### Testing Vision Models Directly

Before configuring, verify a vision model works with your actual images:

```python
import urllib.request, json, base64

with open('/path/to/image.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

api_key = "<your_openrouter_key>"

payload = json.dumps({
    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image in detail."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]
    }],
    "max_tokens": 512
}).encode()

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=payload,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
)
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(result["choices"][0]["message"]["content"][:200])
```

Run this via terminal. Only keep models that return a coherent description.**

Full test methodology: `references/openrouter-free-model-tests.md`

## Key Configuration

```yaml
model:
  default: cohere/north-mini-code:free    # Proven working, fast, 256K ctx
  provider: openrouter
  base_url: ''                             # Empty = OpenRouter default URL

fallback_providers:
  - provider: openrouter
    model: google/gemma-4-31b-it:free      # Proven working, 262K ctx
  - provider: deepseek
    model: deepseek-v4-flash               # PAID — only when both free fail

## Also set
agent:
  api_max_retries: 3                       # Free tiers need retries
```

## How to Test Free Models Before Configuring

**ALWAYS test free models before adding to config.** Use this Python script:

```python
import urllib.request, json, time

# Read key from .env
with open('/opt/data/.env') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        if k == 'OPENROUTER_API_KEY':
            api_key = v
            break

# Models to test
models_to_test = [
    'cohere/north-mini-code:free',
    'google/gemma-4-31b-it:free',
    # Add any new free model you want to try
]

for model in models_to_test:
    start = time.time()
    try:
        req = urllib.request.Request(
            'https://openrouter.ai/api/v1/chat/completions',
            data=json.dumps({
                'model': model,
                'messages': [{'role': 'user', 'content': 'hi'}],
                'max_tokens': 5
            }).encode(),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        resp = urllib.request.urlopen(req, timeout=15)
        body = json.loads(resp.read())
        elapsed = time.time() - start
        cost = body.get('usage', {}).get('cost', '?')
        print(f'✅ OK  ({elapsed:.1f}s): {model} cost={cost}')
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        print(f'❌ {e.code} ({elapsed:.1f}s): {model} — {e.read().decode()[:150]}')
    except Exception as e:
        elapsed = time.time() - start
        print(f'❌ {type(e).__name__} ({elapsed:.1f}s): {model}')
```

Run it via terminal before changing config. Only add models that return ✅.

## How to Apply Config Changes

In Docker/s6 container (config.yaml is usually 444 read-only):

```python
import os, stat

content = open('/opt/data/config.yaml').read()

# Replace model block
content = content.replace(
    "model:\n  default: OLD_MODEL\n  provider: OLD_PROVIDER\n  base_url: OLD_URL",
    "model:\n  default: cohere/north-mini-code:free\n  provider: openrouter\n  base_url: ''"
)

# Write back
was_writable = os.access('/opt/data/config.yaml', os.W_OK)
if not was_writable:
    os.chmod('/opt/data/config.yaml', 0o644)
with open('/opt/data/config.yaml', 'w') as f:
    f.write(content)
if not was_writable:
    os.chmod('/opt/data/config.yaml', 0o444)
```

Then restart gateway:

```bash
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/
sleep 8 && ps aux | grep "hermes gateway" | grep -v grep
```

## Scheduled Model Switching via Cron

When using a time-limited free model (e.g. `tencent/hy3:free` free until Jul 21), set up a cron job to auto-revert to your paid model on the expiry date:

1. Switch to the free model (see "How to Apply Config Changes" above)
2. Create a cron job that restores the paid config at the expiry date/time:

```bash
# Via the cronjob tool (done in-session):
# cronjob with:
#   action=create
#   name=switch-back-to-paid
#   schedule=2026-07-21T00:00:00  (ISO timestamp — one-shot)
#   deliver=origin
#   prompt="Run: hermes config set model.default deepseek-v4-flash && hermes config set model.provider deepseek && hermes config set model.base_url https://api.deepseek.com. Then verify by reading config.yaml model: section."
```

The cron job runs in a fresh session with full tool access. When using `hermes config set` from cron, the binary must be in PATH — use the full path `/opt/hermes/.venv/bin/hermes` if needed, or check `find / -name hermes -type f 2>/dev/null | head -3` first.

The `deliver=origin` setting sends the cron result back to the session that created the job, so you'll receive a confirmation message when the switch happens.

**Pitfall:** If the gateway restarts before the cron fires, verify the job survived with `hermes cron list`. Cron jobs are stored in the session DB and survive container restarts.

## Pitfalls

- **Most OpenRouter free models are broken.** Only `cohere/north-mini-code:free` and `google/gemma-4-31b-it:free` are known working (2026-06-22). ALWAYS test before configuring.
- **Long broken fallback chains cause pain.** Each broken model times out (20-30s). 5 broken models = 2+ minutes of silence before anything works. Keep the chain short: 2-3 proven free + 1 paid.
- **`openrouter/free` routes to content-safety model.** The meta-router `openrouter/free` chooses `nvidia/nemotron-3.5-content-safety` which refuses normal chat. Do NOT use it.
- **`config.yaml` can be overwritten by concurrent writes.** When multiple sessions edit config, yaml.dump serializes the COMPLETE file — the last write wins. Always verify with `grep -A4 "^model:" /opt/data/config.yaml` after writing.
- **Gemini direct API (provider: gemini) free tier is usable but limited** — `gemini-2.5-flash` and `gemini-3.1-flash-lite` work on free tier with ~4 RPM. `gemini-2.0-flash` is deprecated/shut down (returns 429). `gemini-3.5-flash` and `gemini-2.5-flash-lite` return 503 on free tier. The recommended pattern for this user is **manual switch** — configure Gemini as a secondary provider to occasionally switch to via `hermes config set`, not in the auto fallback chain. This preserves pay-per-use DeepSeek as the primary daily driver while keeping Gemini available for ad-hoc high-quality free usage.
- **Concurrent agent sessions overwrite config** — If two sessions write config.yaml, the last `yaml.dump` wins, reverting earlier changes. Always verify after writing: `grep -A4 "^model:" /opt/data/config.yaml`. If config keeps reverting to deepseek, another session is writing it.
- **Commented-out keys in `.env` break providers silently** — Gateway skips `#`-prefixed lines. `grep -n "^[A-Z]" /opt/data/.env` shows active keys; `grep "# " /opt/data/.env` shows disabled ones.
