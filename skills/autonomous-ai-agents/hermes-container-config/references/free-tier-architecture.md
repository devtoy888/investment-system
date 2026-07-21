# Free-Tier Model Architecture (OpenRouter All-Free-First Approach)

## Overall Model Routing

```
User message
  │
  ▼
OpenRouter + Nemotron 3 Ultra 550B (free, 1M ctx, top quality)
  │
  ├── 429/403/error → Multi-tier free fallback chain:
  │
  │   Tier 1 (1M ctx, best):
  │   ├── nvidia/nemotron-3-super-120b-a12b:free
  │   └── qwen/qwen3-coder:free
  │
  │   Tier 2 (256K ctx, strong):
  │   ├── qwen/qwen3-next-80b-a3b-instruct:free
  │   ├── google/gemma-4-31b-it:free  (multimodal)
  │   ├── nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
  │   └── poolside/laguna-m.1:free
  │
  │   Tier 3 (131K ctx, solid):
  │   ├── meta-llama/llama-3.3-70b-instruct:free
  │   ├── nousresearch/hermes-3-llama-3.1-405b:free
  │   ├── openai/gpt-oss-120b:free
  │   └── openai/gpt-oss-20b:free
  │
  │   Tier 4 (fast fallbacks):
  │   ├── cohere/north-mini-code:free
  │   ├── google/gemma-4-26b-a4b-it:free
  │   ├── poolside/laguna-xs.2:free
  │   └── nex-agi/nex-n2-pro:free (vision)
  │
  │   Tier 5 (small models):
  │   ├── nvidia/nemotron-nano-9b-v2:free
  │   ├── nvidia/nemotron-nano-12b-v2-vl:free
  │   ├── nvidia/nemotron-3-nano-30b-a3b:free
  │   ├── meta-llama/llama-3.2-3b-instruct:free
  │   ├── cognitivecomputations/dolphin-mistral-24b-venice-edition:free
  │   ├── liquid/lfm-2.5-1.2b-thinking:free
  │   └── liquid/lfm-2.5-1.2b-instruct:free
  │
  └── ALL FREE FAILED → deepseek-v4-flash (PAID — last resort)

Auxiliary tasks → OpenRouter free models:
  ├── vision:       nex-agi/nex-n2-pro:free  (vision-capable free model)
  ├── compression:  cohere/north-mini-code:free
  ├── web_extract:  cohere/north-mini-code:free
  ├── skills_hub:   cohere/north-mini-code:free
  ├── approval:     cohere/north-mini-code:free
  ├── title_gen:    cohere/north-mini-code:free
  └── curator:      cohere/north-mini-code:free

Delegation → OpenRouter + nvidia/nemotron-3-ultra-550b-a55b:free
```

## Provider Names in Hermes

| Service | config.yaml `provider` | Env var | Notes |
|---------|----------------------|---------|-------|
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` | All free models end with `:free` suffix |
| Google Gemini | `gemini` (NOT `google`) | `GOOGLE_API_KEY` or `GEMINI_API_KEY` | ⚠️ Direct API unreliable (403 project denial) |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` | Paid — use as absolute last resort |
| HuggingFace | `huggingface` | `HF_TOKEN` | Inference API may be DNS-blocked on Oracle Cloud |

## Key Settings

| Setting | Value | Reason |
|---------|-------|--------|
| `model.default` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Best free model |
| `model.provider` | `openrouter` | Route through OpenRouter, not direct |
| `model.base_url` | `''` (empty) | Defaults to OpenRouter API URL |
| `agent.api_max_retries` | `3` | Free tiers need more retries |
| `delegation.model` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Subagents use same best free model |
| `delegation.provider` | `openrouter` | Subagents route through OpenRouter |
| `auxiliary.vision.model` | `nex-agi/nex-n2-pro:free` | Free vision-capable model |

## .env File Layout

```
# === LLM Provider Keys ===
OPENROUTER_API_KEY=sk-or-v1-...  # OpenRouter (primary provider)
DEEPSEEK_API_KEY=sk-...          # DeepSeek (paid, last resort)
GOOGLE_API_KEY=...               # Google Gemini (403 unreliable, keep for emergency)
```

**Important:** `HF_TOKEN` and `GEMINI_API_KEY` are OPTIONAL. OpenRouter handles all free model routing with just `OPENROUTER_API_KEY`.

## Gateway Restart

```bash
# Method A (preferred if s6 is available)
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/

# Method B (fallback)
kill -HUP $(ps aux | grep 'hermes gateway run' | grep -v grep | awk '{print $2}')
sleep 8
ps aux | grep "hermes gateway" | grep -v grep | awk '{print "Gateway PID:", $2}'
```

## Verification

```bash
# Verify config was applied
cd /opt/data && . /opt/hermes/.venv/bin/activate && python3 -c "
from tui_gateway.server import _make_agent
a = _make_agent(sid='v', key='v', model_override=None, provider_override=None)
print(f'Model: {a.model}')
print(f'Provider: {a.provider}')
print(f'Base URL: {a.base_url}')
print(f'API key: {bool(a.api_key)}')
"
# Expected:
#   Model: nvidia/nemotron-3-ultra-550b-a55b:free
#   Provider: openrouter
#   Base URL: https://openrouter.ai/api/v1
#   API key: True
```

## Troubleshooting: Browser Still Shows Old Model

After restarting the gateway with new config:
1. Close the browser tab COMPLETELY and open a fresh one (not F5, not Ctrl+F5)
2. Old `tui_gateway.slash_worker` processes may linger — kill them: `ps aux | grep slash_worker | grep -v grep`
3. Verify with `_make_agent` test above before asking user to refresh
