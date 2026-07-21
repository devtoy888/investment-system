# OpenRouter Free Vision Model Tests

Test date: 2026-06-22
Environment: Oracle Cloud (x86_64, Singapore region)
Primary model: DeepSeek v4 Flash (no native vision — uses auxiliary vision model)

## Initial Configuration

The default auxiliary vision model was `google/gemini-2.0-flash-lite` (likely deprecated by Google). Hermes fallback `vision_analyze` was trying `nex-agi/nex-n2-pro` which is paid-only.

## Discovery Method

1. Query OpenRouter models API: `GET https://openrouter.ai/api/v1/models`
2. Filter for: `pricing.prompt == "0" AND pricing.completion == "0"` (free)
3. Check `modality` field for `image`/`vision`/`multimodal` capabilities

## Free Vision Models Available

```
nvidia/nemotron-3.5-content-safety:free                     # Content guard, not for general vision
nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free          # Text+image+audio+video → text
google/gemma-4-26b-a4b-it:free                              # Text+image+video → text (MoE)
google/gemma-4-31b-it:free                                  # Text+image+video → text (dense)
nvidia/nemotron-nano-12b-v2-vl:free                         # Text+image+video → text (VL-specific)
openrouter/free                                              # Meta-router (routes to content-safety)
```

## Test Results

Test image: A snack food package — "鑫明浩® 芝麻锅巴（韩式酱香味）" (branded sesame-pot-cracker, Korean sauce flavor), white Mylar bag with Chinese text in black/red/orange.

### 1. nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free ✅ BEST

**HTTP:** 200 OK
**Response quality:** Excellent — identified brand name "鑫明浩®", product "芝麻锅巴" (Sesame Pot Cake/Snack), flavor "韩式酱香味" (Korean-style sauce flavor). Detailed description of packaging colors, layout, and visible food texture.
**Length:** 1036 chars
**Latency:** ~5-10s

### 2. nvidia/nemotron-nano-12b-v2-vl:free ✅ WORKS

**HTTP:** 200 OK
**Response quality:** Good — recognized Mylar bag, Chinese text, yellow waffle-like food visible through clear window. Less detail than the Omni model.
**Length:** 624 chars
**Latency:** ~5-10s

### 3. google/gemma-4-31b-it:free ❌ 429

**HTTP:** 429 Too Many Requests
**Detail:** Provider returned error (rate limited). Free tier too popular.
**Note:** Same result for text-only requests — this model is oversubscribed on free tier.

### 4. google/gemma-4-26b-a4b-it:free ❌ 429

**HTTP:** 429 Too Many Requests
**Detail:** Same rate limiting as the 31B variant.

## Recommended Config

```yaml
auxiliary:
  vision:
    provider: openrouter
    model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
    timeout: 120
```

## Pitfalls

- **Vision model config needs session restart.** The `vision_analyze` tool reads `auxiliary.vision.*` at session init, not per-call. After changing config, the agent needs `/reset` (CLI) or `/restart` (gateway).
- **Gemma-4 models 429 consistently.** Do NOT rely on them as vision models. They may become available with a paid tier.
- **`openrouter/free` routes to content-safety.** The meta-router picks `nvidia/nemotron-3.5-content-safety` which is a guardrail model, not a general vision model. Do not use.
- **Image size matters.** Large images (1080×1440+ = ~114KB JPEG) still work but may have higher latency. Both NVIDIA models handled this size fine.
- **base64 encoding via curl is error-prone.** Shell quoting + mid-key truncation in headers causes 401/400 errors. Use Python `urllib` for reliable testing.
- **Mid-session workaround for cached old model.** After config change, `vision_analyze` still uses the cached fallback (nex-agi/nex-n2-pro etc.) until `/reset`. Workaround: call the OpenRouter API directly via `urllib` with the working model. Save the image as base64, construct the payload with `data:image/jpeg;base64,...`, and POST to `https://openrouter.ai/api/v1/chat/completions`. This works immediately without session restart. Once confirmed working, `/reset` at the next opportunity to make `vision_analyze` pick up the new config.
