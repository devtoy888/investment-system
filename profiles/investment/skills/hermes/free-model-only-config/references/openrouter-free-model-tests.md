# OpenRouter Free Model Availability Tests

Tests conducted 2026-06-22 from Oracle Cloud VM (x86_64, Singapore region).
OpenRouter API key valid, auth endpoint responded OK.

## Test Methodology

```python
import urllib.request, json, time

# Read key from /opt/data/.env
# Test each model with max_tokens=5, timeout=15s
# Measure elapsed time and check response
```

## Results

### Working (✅)

| Model | Time | Cost | Notes |
|-------|------|------|-------|
| `cohere/north-mini-code:free` | ~1s | $0 | 30B/3B active, 256K ctx, fast reliable |
| `google/gemma-4-31b-it:free` | ~1s | $0 | 30.7B dense, 262K ctx, multimodal |

### Timeout (❌ TIMEOUT)

All these models hung with no response within 15-20s:

| Model | Status | Claimed Spec |
|-------|--------|-------------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | TIMEOUT | 550B/55B active, 1M ctx |
| `nvidia/nemotron-3-super-120b-a12b:free` | TIMEOUT | 120B/12B active, 1M ctx |
| `qwen/qwen3-coder:free` | TIMEOUT | 480B/35B active, 1M ctx |
| `meta-llama/llama-3.3-70b-instruct:free` | TIMEOUT | 70B dense, 131K ctx |
| `openai/gpt-oss-120b:free` | TIMEOUT | 117B/5.1B MoE |
| `openai/gpt-oss-20b:free` | TIMEOUT | 21B/3.6B MoE |
| `nex-agi/nex-n2-pro:free` | TIMEOUT | 397B/17B active, vision |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | TIMEOUT | 30B/3B active |
| `poolside/laguna-m.1:free` | TIMEOUT | coding agent |
| `google/gemma-4-26b-a4b-it:free` | NOT TESTED | (tests timed out earlier) |
| `qwen/qwen3-next-80b-a3b-instruct:free` | NOT TESTED | (tests timed out earlier) |

### Rate Limited (❌ 429)

| Model | Error | Source |
|-------|-------|--------|
| `meta-llama/llama-3.2-3b-instruct:free` | 429 | Venice upstream rate limit |
| `nousresearch/hermes-3-llama-3.1-405b:free` | 429 | Venice upstream rate limit |

### Misrouted (⚠️)

| Model | Routes to | Usable? |
|-------|-----------|---------|
| `openrouter/free` | `nvidia/nemotron-3.5-content-safety` | NO — content safety model refuses normal chat |

## Recommendations

1. **Only configure proven-working models.** Adding broken models to fallback chain causes multi-minute delays.
2. **Re-test monthly.** Free model availability on OpenRouter changes.
3. **Keep fallback chain short.** 2-3 proven free + 1 paid is optimal.
4. **Use `api_max_retries: 3`** to handle transient 429s on working models.
