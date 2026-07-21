# Nous Portal Free Models — Research (2026-06-23)

## Source
Query: `curl -s "https://inference-api.nousresearch.com/v1/models"` (OpenAI-compatible API, 268 models total)

## Truly Free Models (prompt=$0 AND completion=$0)

| Model | Context | Notes |
|-------|---------|-------|
| `openrouter/owl-alpha` | ~1M tokens | OpenRouter's own free model, longest context |
| `stepfun/step-3.7-flash:free` | 256K | StepFun (阶跃星辰) — Chinese-capable |

## Previously Free — Now Paid

| Model | Prompt | Completion | Status |
|-------|--------|-----------|--------|
| `xiaomi/mimo-v2.5-pro` | $0.000000435 | $0.00000087 | Was free, now paid |
| `xiaomi/mimo-v2.5` | $0.00000014 | $0.00000028 | Was free, now paid |

## Cheapest Paid Models (< $0.000001/prompt token)

| Model | Prompt | Completion | Notes |
|-------|--------|-----------|-------|
| `inclusionai/ling-2.6-flash` | $7.5e-8 | $6.25e-7 | Cheapest LLM |
| `meta-llama/llama-3.1-8b-instruct` | $2e-8 | $3e-8 | Meta open model |
| `nousresearch/hermes-4-70B` | $5e-8 | $2e-7 | 128K ctx |
| `nousresearch/hermes-4-405B` | $9e-8 | $3.7e-7 | 128K ctx |

## Subscription Tiers

| Tier | Monthly | Model Access | Tool Access | Credits |
|------|---------|-------------|-------------|---------|
| Free | $0/mo | Free models + pay-per-use | Pay-per-use | None |
| Plus | $20/mo | 300+ models | Hosted tools | $22 (10% bonus) |
| Super | $100/mo | 300+ models | Hosted tools | $110 (10% bonus) |
| Ultra | $200/mo | 300+ models | Hosted tools | $220 (10% bonus) |

## API Rate Limits (by tier)

| Tier | RPM | TPM |
|------|-----|-----|
| Ultra | 1,600 | 16,000,000 |
| Free | 50 | 500,000 |
| Super | 800 | 8,000,000 |
| Plus | 400 | 4,000,000 |
| Default paid | 180 | 720,000 |

## Key Takeaways

1. **Nous Portal is NOT a free service** — the "Free" tier is pay-per-use
2. Only 2 truly free models exist (OWL-Alpha, Step-3.7-Flash:free)
3. Xiaomi MiMo was previously free but is now paid — limited-time promotions expire
4. Hermes-4 series available but **not recommended for Hermes Agent** (agentic models preferred)
5. For truly free Hermes Agent setup, use OpenRouter free models + Agnes AI instead

## Verification Commands

```bash
# List all free models
curl -s "https://inference-api.nousresearch.com/v1/models" | \
  python3 -c "
import json,sys
for m in json.load(sys.stdin).get('data',[]):
    p=float(m['pricing']['prompt']); c=float(m['pricing']['completion'])
    if p==0 and c==0: print(f'{m[\"id\"]} ctx={m.get(\"context_length\",\"?\")}')
"

# Check for :free suffixed models
curl -s "https://inference-api.nousresearch.com/v1/models" | \
  python3 -c "
import json,sys
for m in json.load(sys.stdin).get('data',[]):
    if ':free' in m['id']: print(f'{m[\"id\"]} ctx={m.get(\"context_length\",\"?\")}')
"
```
