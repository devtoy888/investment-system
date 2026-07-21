# Visual Model Fallback Configuration (Updated 2026-06-23)

## Problem
OpenRouter auxiliary vision model (Gemma-4 series) returns 404:
```
{'error': {'message': 'This model is unavailable for free. The paid version is available now - use this slug instead: nex-agi/nex-n2-pro', 'code': 404}}
```

## Solutions

### Option 1: Use paid vision model via OpenRouter (Recommended)
Set in `config.yaml`:
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: amazon/nova-lite-v1  # $0.06/M prompt, $0.24/M completion
```
Or via CLI:
```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model amazon/nova-lite-v1
```

### Option 2: Use nex-agi/nex-n2-pro (paid)
```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model nex-agi/nex-n2-pro
```

### Option 3: Use custom provider with vision model
Set up a custom OpenAI-compatible endpoint that serves a vision model.

## Comprehensive Vision Model Pricing (OpenRouter API)

Query all vision-capable models:
```bash
python3 -c "
import os, requests
headers = {'Authorization': f'Bearer {os.environ.get(\"OPENROUTER_API_KEY\", \"\")}'}
resp = requests.get('https://openrouter.ai/api/v1/models', headers=headers, timeout=10)
data = resp.json()
for m in data.get('data', []):
    if 'image' in m.get('architecture', {}).get('modality', '').lower():
        pricing = m.get('pricing', {})
        prompt = float(pricing.get('prompt', 0)) * 1_000_000
        completion = float(pricing.get('completion', 0)) * 1_000_000
        print(f\"{m['id']:50s} prompt=\${prompt:.4f}/M  completion=\${completion:.4f}/M\")
"
```

### Top Recommendations (Paid, Best Value)

| Model | Prompt ($/M) | Completion ($/M) | Context | Best For |
|-------|-------------|-----------------|---------|----------|
| **amazon/nova-lite-v1** | $0.06 | $0.24 | 300K | **Best overall value** |
| qwen/qwen3.5-flash-02-23 | $0.065 | $0.26 | 1M | Chinese text recognition |
| bytedance-seed/seed-1.6-flash | $0.075 | $0.30 | 262K | ByteDance, good balance |
| mistralai/mistral-small-3.2-24b-instruct | $0.075 | $0.20 | 128K | Fast, cheap completion |
| qwen/qwen3-vl-8b-instruct | $0.08 | $0.50 | 256K | Chinese, VL multimodal |
| google/gemma-3-27b-it | $0.08 | $0.16 | 131K | Fast, Google quality |
| bytedance/ui-tars-1.5-7b | $0.10 | $0.20 | 128K | UI/screen understanding |
| google/gemini-2.5-flash-lite | $0.10 | $0.40 | 1M | Strong vision, Google |
| openai/gpt-4.1-nano | $0.10 | $0.40 | 1M | OpenAI quality |
| meta-llama/llama-4-scout | $0.10 | $0.30 | **10M** | Ultra-long context |

### Free Tier (Limited)
| Model | Notes |
|-------|-------|
| nvidia/nemotron-3.5-content-safety:free | Content moderation focused |
| nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free | Already used as primary free model |
| nvidia/nemotron-nano-12b-v2-vl:free | Visual language, 128K context |
| google/gemma-4-31b-it:free | Previously used, now returns 404 |

## Verification After Config Change
Changes to `auxiliary.vision.model` require `/reset` (new session) to take effect. Test with:
```bash
# In a new session, use vision_analyze on a test image
```

## Notes
- Browser CDP may also fail with 502 — use terminal-based verification as backup
- The `nex-agi/nex-n2-pro` model was previously free but is now paid-only
- OpenRouter API pricing field format: `pricing.prompt` is per-token (multiply by 1,000,000 for per-M)
- When API returns empty pricing, check `top_provider` object for context_length and pricing hints
