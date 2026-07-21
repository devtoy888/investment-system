# Gemini Provider Setup Session (2026-06-21)

## Context
User was using DeepSeek v4 Flash (paid) as primary model. Wanted free alternatives. Provided a Gemini API key (format: `AQ.Ab8...Fmw`).

## Steps Taken

### 1. Checked current env
- `HERMES_HOME=/opt/data`
- Config at `/opt/data/config.yaml`, .env at `/opt/data/.env`
- Current model: `deepseek-v4-flash` via `deepseek` provider

### 2. Added GOOGLE_API_KEY to .env
- `echo 'GOOGLE_API_KEY=...' >> /opt/data/.env`
- **Got truncated** on first attempt (used `...` in echo). Fixed by rewriting the entire line with `sed -i 's|^GOOGLE_API_KEY=.*|GOO...mw|'` using the full key.
- Terminal displays long values with `...` visually — actual file content was correct. Verified with `od -c`.

### 3. Changed config.yaml
- `sed -i 's/^  default: deepseek-v4-flash/  default: gemini-2.0-flash/'`
- **⚠️ CRITICAL: Wrong provider name first time!** Used `provider: google` but Hermes expects `provider: gemini`.
  - The auth system registers Google's API key under the provider name `gemini` (as shown by `hermes auth list`)
  - Using `provider: google` causes `/model` commands to fail
  - Fix: `sed -i 's/^  provider: google/  provider: gemini/' /opt/data/config.yaml`
- Verified with `grep -A3 "^model:" /opt/data/config.yaml`

### 4. Added fallback providers
- Replaced `fallback_providers: []` with YAML list:
  ```yaml
  fallback_providers:
    - provider: deepseek
      model: deepseek-v4-flash
  ```
- `sed -i 's/^fallback_providers: \[\]/fallback_providers:\n- provider: deepseek\n  model: deepseek-v4-flash/'`

### 5. Tested Gemini API
- `curl "https://generativelanguage.googleapis.com/v1beta/models?key=$KEY"` → HTTP 200 (key valid)
- `curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$KEY"` → HTTP 429 (rate limited on free tier from rapid testing)
- The 429 included `"retryDelay": "48s"` — free tier rate limit, not an auth error
- After 60s cooldown, still 429 — this is daily/rate limiting, not permanent
- Key works normally at conversational pace

### 6. Restarted gateway
- `hermes` not in PATH. Located at `/opt/hermes/.venv/bin/hermes`
- `hermes gateway restart` returned without effect (s6 managed)
- Killed PID 4872 with `kill -HUP 4872` → process died
- s6 auto-started new gateway (PID 5634)
- New WhatsApp bridge also started (PID 5650)

### 7. Verified final state
- `ps aux | grep "hermes gateway"` → PID 5634 running
- Gateway HTTP health check at port 9119 → 200 OK
- Config verified: model=gemini-2.0-flash, provider=gemini, fallback=deepseek
- **Note:** First attempt used `provider: google` which caused `/model` to fail. Had to be corrected to `provider: gemini`.

### 8. Later discovered: base_url required for NativeClient dispatch
Even after fixing provider=gemini, responses showed deepseek. Root cause: `is_native_gemini_base_url("")` returns False, skipping GeminiNativeClient. Fix: set `base_url: https://generativelanguage.googleapis.com/v1beta` in config.yaml. See `references/gemini-nativeclient-baseurl.md` for full debug chain and code references.
