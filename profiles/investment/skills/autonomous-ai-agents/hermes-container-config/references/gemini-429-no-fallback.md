# Gemini 429 — Fallback Fails to Activate: Diagnostic Recipe

> **⚠️ Update (June 2026): Gemini direct API now also returns 403 (project denial), not just 429.**
> If the error is `HTTP 403 PERMISSION_DENIED: Your project has been denied access`, this is NOT rate limiting — it's a permanent project-level block. No config change or retry will fix it. The solution is to migrate to OpenRouter as the primary provider. See the main SKILL.md's "Free Provider Recommendations" section for the OpenRouter-only setup.

When the user reports "Gemini keeps getting 429 and doesn't fall back to another model", the root cause is almost always one of these three config issues, in this priority order.

## Diagnosis Checklist (run in order)

### 1. Is Gemini actually the primary model?

Check `model.default` and `model.provider` — NOT `providers.gemini`.

```bash
grep -A3 "^model:" /opt/data/config.yaml
```

**✅ Working:** `provider: gemini`, `default: gemini-2.0-flash`

**❌ Broken:** `provider: deepseek`, `default: deepseek-v4-flash` (Gemini only in `providers.gemini` sub-block)

The `providers:` section defines provider-specific config overrides — it does NOT set the primary model. If only `providers.gemini` has Gemini config but `model.default` is something else, every `/model gemini-2.0-flash` switch works only for that session, and the next restart resets to the wrong default.

**Fix:**
```bash
sed -i 's/^  default: .*/  default: gemini-2.0-flash/' /opt/data/config.yaml
sed -i 's/^  provider: .*/  provider: gemini/' /opt/data/config.yaml
```

### 2. Is `base_url` set correctly for Gemini?

```bash
grep "^  base_url:" /opt/data/config.yaml
```

**✅ Working:** `base_url: https://generativelanguage.googleapis.com/v1beta`

**❌ Broken:** `base_url: ''` (empty)

When `base_url` is empty, `agent.gemini_native_adapter.is_native_gemini_base_url("")` returns **False**. The Gemini Native Client is skipped entirely. Hermes falls through to the standard OpenAI-compatible HTTP client, which targets `"" + "/chat/completions"` — effectively nothing. The API call fails, and Hermes silently triggers the fallback chain. **The user never sees Gemini respond; the fallback handles every request.** The user perceives this as "Gemini doesn't work" or "fallback always fires", when in reality Gemini was never actually being used.

**Diagnostic verification:**
```bash
cd /opt/data && . /opt/hermes/.venv/bin/activate && python3 -c "
from agent.gemini_native_adapter import is_native_gemini_base_url
print('Native client used:', is_native_gemini_base_url('$BASE_URL'))
"
```

**Fix:**
```bash
sed -i "s|^  base_url: ''|  base_url: https://generativelanguage.googleapis.com/v1beta|" /opt/data/config.yaml
```

### 3. Is there a reliable paid fallback first in the chain?

```bash
grep -A5 "^fallback_providers:" /opt/data/config.yaml
```

**✅ Working:** First entry is a reliable paid provider (e.g. DeepSeek), then OpenRouter free models.

**❌ Broken:** Only OpenRouter free models (they can also be rate-limited, creating a cascade failure).

When both the primary (Gemini, rate-limited) AND the fallback (OpenRouter free, also rate-limited) fail, the user sees "No fallback available" — even though a paid fallback like DeepSeek would have worked fine.

**Fix:** Insert a paid fallback as the first entry:
```python
# Write to /tmp and cp to preserve permissions
import re
with open('/opt/data/config.yaml') as f:
    content = f.read()
old = """fallback_providers:
- provider: openrouter"""
new = """fallback_providers:
- provider: deepseek
  model: deepseek-v4-flash
- provider: openrouter"""
content = content.replace(old, new)
with open('/opt/data/config.yaml', 'w') as f:
    f.write(content)
```

### 4. Restart Gateway (all config changes require restart)

```bash
S6_SVC=$(find / -name "s6-svc" -type f 2>/dev/null | head -1)
"$S6_SVC" -r /run/service/gateway-default/
sleep 10
grep -i "Connected\|ready" /opt/data/logs/gateway.log | tail -3
```

## Common Misdiagnosis

| Symptom | Likely Root Cause | Fix |
|---------|------------------|-----|
| "Gemini always falls through to DeepSeek even without 429" | `base_url` empty → native client bypassed | Set base_url (step 2) |
| "Fallback doesn't work when Gemini gets 429" | Fallback chain only has free/low-reliability models | Add paid fallback first (step 3) |
| "Switching to Gemini via /model works but next day it's back on deepseek" | `model.default` still points to deepseek | Change primary model (step 1) |
| "F5/refresh doesn't show the new model in TUI" | Browser WebSocket cached from old Gateway PID | Close tab entirely and reopen |
