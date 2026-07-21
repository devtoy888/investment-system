# Xiaomi MiMo Token Plan — Provider Reference

## Quick Reference

| Item | Value |
|------|-------|
| Env var (key) | `XIAOMI_API_KEY` |
| Env var (base URL) | `XIAOMI_BASE_URL` |
| Provider name | `xiaomi` (aliases: `mimo`, `xiaomi-mimo`) |
| Standard model | `mimo-v2.5` |
| Pro model | `mimo-v2.5-pro` |
| Token Plan Lite | $6/month, 4.1B credits |
| Multimodal | ✅ Image + Video + Audio + Text |
| Context | 1M tokens |

## Token Plan Endpoints

| Region | Base URL |
|--------|----------|
| China | `https://token-plan-cn.xiaomimimo.com/v1` |
| Singapore | `https://token-plan-sgp.xiaomimimo.com/v1` |
| Europe | `https://token-plan-ams.xiaomimimo.com/v1` |

Pay-as-you-go MiMo API uses `https://api.xiaomimimo.com/v1` — DO NOT confuse with Token Plan endpoint.

## Credits Consumption (Token Plan)

| Model | Input (Cache Hit) | Input (Cache Miss) | Output |
|-------|-------------------|-------------------|--------|
| `mimo-v2.5` | 2 Cr/tok | 100 Cr/tok | 200 Cr/tok |
| `mimo-v2.5-pro` | 2.5 Cr/tok | 300 Cr/tok | 600 Cr/tok |

### Lite Plan Capacity Estimation

| Scenario | Monthly usage | % of 4.1B Cr |
|----------|--------------|--------------|
| Light (3 wiki builds/day, 15 rounds) | ~835M Cr | ~20% |
| Medium (10 builds/day, 30 rounds) | ~1,860M Cr | ~45% |
| Heavy (all day, incl. sub-agents) | ~3,500M Cr | ~85% |

Night discount (0:00–8:00 Beijing): 0.8x consumption coefficient.

## Model Capabilities

- Native multimodal: image, video, audio, text input in same conversation
- 1M token context window
- No separate "vision model" needed — the main model handles images natively
- Tool calling: stable (verified in this profile)
- Reasoning: supports configurable reasoning (default: no explicit CoT)

## Hermes Configuration

### .env (user must add)

```
XIAOMI_API_KEY=tp-xxxxx
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

### config.yaml

```yaml
model:
  provider: xiaomi
  default: mimo-v2.5
  base_url: ''           # XIAOMI_BASE_URL handles this

delegation:
  provider: xiaomi
  model: mimo-v2.5

# AUXILIARY should NOT use MiMo — keeps free OpenRouter models
# to avoid wasting Token Plan quota on compression/summary/approval
```

### Direct Connectivity Test

```bash
export HERMES_HOME=/opt/data/profiles/<profile>
/opt/hermes/bin/hermes chat -q "测试连通性，回复OK" --quiet
```

### Common Pitfalls

- **Wrong provider name**: `xiaomi` NOT `mimo` NOT `xiaomi-mimo`
- **Wrong model name**: `mimo-v2.5` NOT `mimo-v2.5-lite` (Lite is plan tier, not model)
- **Wrong base URL**: Token Plan endpoint ≠ Pay-as-you-go endpoint
- **Forgetting delegation**: Changing `model.*` without `delegation.*` — sub-agents keep old model
- **Putting MiMo in auxiliary**: Don't — wastes Token Plan credits on background tasks
- **Missing XIAOMI_BASE_URL**: The `xiaomi` provider's default URL is the pay-as-you-go endpoint, NOT the Token Plan one. Must set `XIAOMI_BASE_URL` in .env
