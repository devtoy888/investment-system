# Gemini NativeClient: The Silent Base URL Requirement

## The Problem

You configure Hermes with:
```yaml
model:
  default: gemini-2.0-flash
  provider: gemini
  base_url: ''   # ← empty or omitted
```

You add `GOOGLE_API_KEY` to `.env`. You test with `curl` — the key works (HTTP 200). You restart the gateway. But every new session still replies "deepseek-v4-flash". No error message appears.

## Root Cause: `is_native_gemini_base_url()` Returns False

Hermes has a **native Gemini adapter** (`GeminiNativeClient`) that speaks Google's REST API directly. But the dispatch logic in `agent/agent_runtime_helpers.py` (line 1397-1410) checks `is_native_gemini_base_url(base_url)` before using it.

### The function (`agent/gemini_native_adapter.py:54-61`):
```python
def is_native_gemini_base_url(base_url: str) -> bool:
    normalized = str(base_url or "").strip().rstrip("/").lower()
    if not normalized:        # ← empty string → returns False
        return False
    if "generativelanguage.googleapis.com" not in normalized:  # ← wrong URL → False
        return False
    return not normalized.endswith("/openai")
```

When `base_url` is `""`:
1. `is_native_gemini_base_url("")` → `False`
2. Hermes skips `GeminiNativeClient`
3. Falls through to standard OpenAI HTTP client
4. Tries `{base_url}/chat/completions` = `"/chat/completions"` → fails
5. **Silently falls through to `fallback_providers`** (e.g. DeepSeek)
6. Response shows `deepseek-v4-flash` — user thinks Gemini is broken

### The GeminiNativeClient itself is fine with empty base_url:
```python
# agent/gemini_native_adapter.py:855
normalized_base = (base_url or DEFAULT_GEMINI_BASE_URL).rstrip("/")
```
Line 855 correctly uses `DEFAULT_GEMINI_BASE_URL` as fallback. But the dispatch logic in `agent_runtime_helpers.py` never reaches this line because `is_native_gemini_base_url` gates entry to the native client.

## The Fix

```yaml
model:
  default: gemini-2.0-flash
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

After adding base_url:
- `is_native_gemini_base_url("https://generativelanguage.googleapis.com/v1beta")` → `True`
- `GeminiNativeClient` is used
- Model name appears correctly in responses

## Verification

```python
# From Hermes venv:
from hermes_cli.runtime_provider import resolve_runtime_provider
result = resolve_runtime_provider(requested='gemini')
print(f"Provider: {result.get('provider')}")
print(f"Base URL: {result.get('base_url')}")
print(f"API key present: {bool(result.get('api_key'))}")
```

Expected output:
```
Provider: gemini
Base URL: https://generativelanguage.googleapis.com/v1beta
API key present: True
```

**Gateway-level verification:**
```bash
GW_PID=$(ps aux | grep 'hermes gateway' | grep -v grep | awk '{print $2}')
cat /proc/$GW_PID/environ | tr '\0' '\n' | grep '^GOOGLE_API_KEY'
```

## Key Files Referenced

| File | Relevant Lines |
|------|---------------|
| `agent/gemini_native_adapter.py` | L54-61 (`is_native_gemini_base_url`), L834-861 (`GeminiNativeClient.__init__`), L855 (base_url default) |
| `agent/agent_runtime_helpers.py` | L1397-1417 (dispatch logic — gates native client on base_url check) |
| `plugins/model-providers/gemini/__init__.py` | L52-60 (GeminiProfile with correct default base_url, but not propagated) |
| `hermes_cli/providers.py` | L46-214 (HERMES_OVERLAYS — note `gemini` is NOT in this dict; it comes from models.dev) |
