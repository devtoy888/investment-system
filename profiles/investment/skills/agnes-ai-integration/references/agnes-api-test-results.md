# Agnes AI API Test Results (2026-06-23)

## Session: Configure Agnes AI as Primary Free Provider

### Test Results Summary

| Test | Result | Latency | Notes |
|------|:------:|:-------:|-------|
| Basic chat (agnes-2.0-flash, Chinese) | ✅ | ~14s | Fluent, accurate |
| Basic chat (agnes-1.5-flash) | ✅ | ~12s | Works, routes to 2.0 internally |
| Long context (553 tokens) | ✅ | ~15s | Normal |
| Streaming | ✅ | ~5.6s avg | 10 requests, 1 outlier at 15s |
| Image generation (2.1-flash) | ✅ | ~7s | Returns URL successfully |
| Models list (/v1/models) | ✅ | <1s | Returns all 5 models |
| Tool calling | ⚠️ | Timeout | Frequent timeouts, unreliable |
| Vision (base64 image) | ❌ | N/A | 413 Payload Too Large (image too big) |
| Vision (resized image) | ✅ | ~10s | 800x800 thumbnail works |

### API Key Verification

- Key length: 51 characters
- Format: `sk-jFc...EPa1` (terminal truncates middle, actual key is complete)
- Stored in: `.env` as `OPENAI_API_KEY` (required for custom provider)
- Also stored in: `.env` as `CUSTOM_AGNES_API_KEY` (not used by Hermes)

### Key Configuration

```yaml
model:
  default: agnes-2.0-flash
  provider: custom
  base_url: https://apihub.agnes-ai.com/v1

fallback_providers:
  - provider: custom
    model: agnes-1.5-flash
  - provider: openrouter
    model: cohere/north-mini-code:free
  - provider: openrouter
    model: google/gemma-4-31b-it:free
  - provider: openrouter
    model: deepseek/deepseek-v4-flash
```

### Important Findings

1. **`hermes config set` corrupts API keys** — Secret redaction replaces real key with `***`. Must write key directly via Python or `printf`.

2. **Terminal display is misleading** — `grep` shows `sk-jFc...EPa1` but the actual stored value is the full 51-char key. Use `od -c` or Python hex dump to verify.

3. **Image base64 payloads over 4MB fail** — Agnes AI returns 413. Must resize images before encoding.

4. **Tool calling is unreliable** — Frequently times out (>15s). Not recommended for production use yet.

5. **All models work at conversational pace** — No rate limiting issues at normal usage. Burst testing (10 requests in 60s) triggers 429.