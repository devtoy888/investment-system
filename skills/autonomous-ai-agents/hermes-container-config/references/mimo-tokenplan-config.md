# Xiaomi MiMo Token Plan — Configuration

MiMo (小米 MiMo) is a built-in Hermes provider. The **Token Plan** subscription (Lite/Standard/Pro/Max) uses a **different endpoint and API key format** than the standard pay-as-you-go API.

## Quick Reference

| Item | Value |
|------|-------|
| **Provider name** | `xiaomi` (aliases: `mimo`, `xiaomi-mimo`) |
| **Env var** | `XIAOMI_API_KEY` |
| **Base URL override** | `XIAOMI_BASE_URL` (in `.env`) |
| **Token Plan endpoint** | `https://token-plan-cn.xiaomimimo.com/v1` |
| **Key format** | `tp-xxxxx` (Token Plan) vs `sk-xxxxx` (standard) |
| **Recommended model** | `mimo-v2.5` — multimodal (image/audio/video), 1M ctx, 128K output |
| **Pro model** | `mimo-v2.5-pro` — text + deep reasoning, 1M ctx, 128K output |

## .env Configuration

```bash
XIAOMI_API_KEY=tp-your-token-plan-key-here
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

- `XIAOMI_BASE_URL` overrides the built-in endpoint (default: `https://api.xiaomimimo.com/v1`). Token Plan **must** use the `token-plan-cn` URL.
- Token Plan keys start with `tp-`, not `sk-`.

## Hermes config.yaml

```yaml
model:
  default: mimo-v2.5
  provider: xiaomi
  supports_vision: true   # enables native multimodal (images sent directly)
```

- `supports_vision: true` — MiMo `mimo-v2.5` handles images natively (as `image_url` parts). Without it, Hermes pre-describes images through the auxiliary vision model.
- `base_url: ''` — leave empty; the env var `XIAOMI_BASE_URL` provides the override.

## Model Capabilities

| Model | Multimodal | Reasoning | Tool calling | Structured output |
|-------|-----------|-----------|-------------|-------------------|
| `mimo-v2.5` | ✅ image/audio/video | ✅ deep thinking | ✅ | ✅ |
| `mimo-v2.5-pro` | ❌ text only | ✅ deep thinking | ✅ | ✅ |

For Hermes' agentic use, `mimo-v2.5` is recommended due to multimodal support.

## Token Plan Pricing (Lite)

| Plan | Monthly | Credits | Mimo-v2.5 input | Mimo-v2.5 output |
|------|---------|---------|-----------------|------------------|
| **Lite** | $6 / ¥39 | 4.1B | 100 credits/token | 200 credits/token |
| **Standard** | $16 / ¥99 | 11B | 100 credits/token | 200 credits/token |
| **Pro** | $50 / ¥329 | 38B | 100 credits/token | 200 credits/token |
| **Max** | $100 / ¥659 | 82B | 100 credits/token | 200 credits/token |

- Night discount (00:00-08:00 Beijing): 0.8x consumption
- Cache hit: 2 credits/token (vs 100 for uncached input)
- Lite tier ≈ 200 medium-complex tasks per month with `mimo-v2.5`

## Testing

```bash
# Direct curl test
curl -s --location --request POST 'https://token-plan-cn.xiaomimimo.com/v1/chat/completions' \
  --header "api-key: $XIAOMI_API_KEY" \
  --header "Content-Type: application/json" \
  --data-raw '{
    "model": "mimo-v2.5",
    "messages": [{"role": "user", "content": "hi"}],
    "max_completion_tokens": 50
  }' | python3 -m json.tool

# Via Hermes
hermes chat -q 'test' --model mimo-v2.5 --provider xiaomi -Q
```

Note: the MiMo docs use `api-key` header (NOT `Authorization: Bearer`). Hermes' built-in `xiaomi` provider handles this automatically.

## Pitfalls

- **Token Plan API key (`tp-xxxxx`) won't work on the standard endpoint** — you MUST set `XIAOMI_BASE_URL` to the Token Plan URL.
- **`mimo-v2.5-pro` does NOT support multimodal.** If you need vision/image input, use `mimo-v2.5`.
- **Credits across models are pooled**, not independent. A single plan pays for all models out of the same credit pool.
- **Lite plan only ≈200 tasks/month.** Hermes agent loops use many tokens per turn (system prompt + tools + conversation). May burn through credits faster than expected for heavy use.
- **MiMo returns `reasoning_content` in responses** for deep-thinking mode. Hermes handles this transparently.
- **`mimo-v2-pro` / `mimo-v2-omni` (V2 series) deprecated 2026-06-30** — use `mimo-v2.5` series only.
