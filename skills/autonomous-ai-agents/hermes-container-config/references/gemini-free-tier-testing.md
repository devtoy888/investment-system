# Gemini API Free Tier Testing (2026-06-25)

Test results from Oracle Cloud Korea server (152.70.91.4). The user's free-tier Gemini API key was tested against Google's Gemini API directly.

## Available Models on Free Tier

| Model | Result | RPM | Notes |
|-------|--------|-----|-------|
| `gemini-2.5-flash` | ✅ 200 | ~4 | Best quality, supports thinking, 1M ctx |
| `gemini-3.1-flash-lite` | ✅ 200 | ~4+ | Lighter, faster, 1M ctx |
| `gemini-3.5-flash` | ❌ 503 | — | Free tier unavailable |
| `gemini-2.5-flash-lite` | ❌ 503 | — | Free tier unavailable |
| `gemini-2.5-pro` | ❌ paid | — | Not on free tier |
| `gemini-2.0-flash` | ❌ 429 | — | Deprecated/shut down |
| `gemini-2.0-flash-001` | ❌ 429 | — | Deprecated/shut down |

## Rate Limit Profile (gemini-2.5-flash)

```
Call 1: HTTP 200, 2749ms
Call 2: HTTP 200, 1123ms
Call 3: HTTP 200, 3333ms
Call 4: HTTP 200, 1765ms
Call 5: HTTP 429, 177ms    ← rate limited!
```

Free tier allows approximately **4 requests per minute** (slightly more if you pace them). Normal conversational use (1 message per 1-3 minutes) is fine.

## Env Var

```bash
GOOGLE_API_KEY=your_key_here
# GEMINI_API_KEY also works as an alternative name
```

No `providers.gemini.api_key` or `key_env` is needed — the built-in `gemini` provider auto-reads `GOOGLE_API_KEY`.

## Provider Config

```yaml
providers:
  gemini:
    base_url: https://generativelanguage.googleapis.com/v1beta
    model: gemini-2.5-flash
```

## Usage Pattern: Manual Switch

Do NOT put Gemini in the auto fallback chain (4 RPM is too low for reliable fallback). Use manual switch:

```bash
# Enable Gemini
hermes config set model.default gemini-2.5-flash
hermes config set model.provider gemini

# Disable (back to DeepSeek)
hermes config set model.default deepseek-v4-flash
hermes config set model.provider deepseek
```

## Region & IP Notes

- **Oracle server location:** Korea (Seoul) — listed in [Gemini API supported regions](https://ai.google.dev/gemini-api/docs/available-regions)
- **Cloudflare Tunnel:** Only handles inbound traffic (external → your services). Outbound API calls (Hermes → Gemini) go directly from the Oracle server's Korea IP.
- **Region blocking is NOT the cause of 429 errors** — Korea is fully supported. The 429 comes from free tier rate limits.

## Testing Commands

```bash
# List available models
KEY=$(grep GOOGLE_API_KEY /opt/data/.env | cut -d= -f2-)
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$KEY" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for m in d.get('models', []):
    name = m['name'].replace('models/', '')
    methods = m.get('supportedGenerationMethods', [])
    if 'generateContent' in methods:
        print(f'  ✅ {name}')
"

# Test a specific model
time curl -s -w "\nHTTP:%{http_code}" \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"hi"}]}]}' \
  -H "x-goog-api-key: $KEY"
```

## Comparison: Gemini vs Agnes AI Free Tier

| | Gemini 2.5 Flash | Agnes 2.0 Flash |
|---|---|---|
| Latency | 1-3s ✅ | 7s+ ❌ |
| RPM | 4 ❌ | 20 ✅ |
| Quality | High ✅ | Medium |
| Thinking support | ✅ | ❌ |
| 1M context | ✅ | 256K |
| Image input (vision) | ✅ native | ✅ via API |
