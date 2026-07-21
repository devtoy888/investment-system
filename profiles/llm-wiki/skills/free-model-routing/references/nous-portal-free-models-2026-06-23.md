# Nous Portal Free Model Research (2026-06-23)

## Summary

Nous Portal has 268 models but only **2 are truly free** (prompt=$0 + completion=$0):

| Model | Context | Notes |
|-------|---------|-------|
| `openrouter/owl-alpha` | 1,048,756 | OpenRouter's own free model, 1M context |
| `stepfun/step-3.7-flash:free` | 256,000 | 阶跃星辰 free model |

## Xiaomi MiMo — NOT Free Anymore

Previously had limited-time free offers, but as of 2026-06-23:
- `xiaomi/mimo-v2.5-pro` — prompt $0.000000435 / completion $0.00000087
- `xiaomi/mimo-v2.5` — prompt $0.00000014 / completion $0.00000028

## Cheapest Paid Models (near-free)

| Model | Prompt | Completion | Notes |
|-------|--------|-----------|-------|
| `inclusionai/ling-2.6-flash` | $0.00000001 | $0.00000003 | Cheapest overall |
| `meta-llama/llama-3.1-8b-instruct` | $0.00000002 | $0.00000003 | Meta open-source |
| `nousresearch/hermes-4-70B` | $0.00000005 | $0.00000020 | Hermes Agent's own |
| `nousresearch/hermes-4-405B` | $0.00000009 | $0.00000037 | Hermes flagship |

## Stability Assessment for Hermes Agent

- **Free model count**: Only 2 — very limited choice
- **OWL-Alpha**: 1M context — good for long documents
- **Step-3.7-Flash:free**: 256K context — decent Chinese capability
- **Free tier sustainability**: Limited-time free offers have ended before (MiMo example)
- **Recommendation**: OpenRouter free models (Nemotron, Gemma) are more mature/stable for Hermes Agent than Nous Portal free models

## Verification Command

```bash
curl -s "https://inference-api.nousresearch.com/v1/models" | python3 -c "
import sys, json
data = json.load(sys.stdin)
models = data.get('data', [])
truly_free = []
for m in models:
    name = m.get('id', '?')
    pricing = m.get('pricing', {})
    p_str = pricing.get('prompt', '1')
    c_str = pricing.get('completion', '1')
    try:
        p = float(p_str) if p_str not in (None, 'N/A', '') else 1
        c = float(c_str) if c_str not in (None, 'N/A', '') else 1
    except:
        continue
    if p == 0 and c == 0:
        ctx = m.get('context_length', '?')
        truly_free.append((name, p, c, ctx))
for name, p, c, ctx in sorted(truly_free, key=lambda x: -x[3]):
    print(f'  {name} | ctx: {ctx:,}')
"
```