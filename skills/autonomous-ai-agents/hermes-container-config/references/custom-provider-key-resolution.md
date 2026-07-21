# Custom Provider API Key Resolution

How Hermes resolves API keys for custom providers (`provider: custom` or `providers.custom.<name>`).

## Source of Truth

From `hermes_cli/runtime_provider.py` (verified against code, not documentation).

## Resolution Order

For a `providers.custom.<name>` entry, Hermes resolves the API key in this priority:

```
1. providers.custom.<name>.api_key           (inline in config.yaml)
2. _getenv(providers.custom.<name>.key_env)  (env var named by key_env field)
3. If base_url matches openai.com → OPENAI_API_KEY
4. If base_url matches openrouter.ai → OPENROUTER_API_KEY
5. Generic fallback: OPENAI_API_KEY → OPENROUTER_API_KEY
```

## Key Fields

| Config field | What it does | Example |
|-------------|--------------|---------|
| `api_key` | Inline key in config.yaml. Used directly when set. | `api_key: sk-xxx` |
| `key_env` | Name of environment variable to read. Overrides `api_key` lookup. | `key_env: AGNES_API_KEY` |
| `api_key_env` | Alias for `key_env` (backward compat). | `api_key_env: MY_CUSTOM_KEY` |

## Common Misconception: The `CUSTOM_` Prefix

**The `CUSTOM_` prefix is NOT a Hermes requirement.** It's a naming convention chosen by `hermes setup` or the agent during initial configuration. The `key_env` field (or `api_key_env`) can point to ANY env var name:

```yaml
# These all work identically:
providers:
  custom:
    my-service:
      base_url: https://api.example.com/v1
      key_env: AGNES_API_KEY          # ✅ Any name works
      # key_env: MY_CUSTOM_KEY        # ✅ Also fine
      # key_env: CUSTOM_AGNES_KEY     # ✅ Also fine
      model: my-model
```

The `.env` file can use any variable name as long as `key_env` matches.

## Scenario Analysis

### Scenario A: Inline api_key, no key_env (common after setup)

```yaml
providers:
  custom:
    agnes:
      base_url: https://apihub.agnes-ai.com/v1
      api_key: sk-xxx                 # ← Used directly
      # key_env: not set              # ← env var NOT read
      model: agnes-2.0-flash
```

**Result:** Uses inline `api_key`. The `.env` variable `CUSTOM_AGNES_API_KEY` (if it exists) is **never read**. It's a harmless leftover from setup.

### Scenario B: key_env set, no inline api_key (preferred pattern)

```yaml
providers:
  custom:
    agnes:
      base_url: https://apihub.agnes-ai.com/v1
      key_env: AGNES_API_KEY          # ← Reads this env var
      # api_key: not set
      model: agnes-2.0-flash
```

```bash
# .env
AGNES_API_KEY=sk-xxx
```

**Result:** Reads from env var. Clean separation of config (goes in git) and secrets (stays on the server).

### Scenario C: Neither set — falls through to OPENAI_API_KEY

```yaml
providers:
  custom:
    agnes:
      base_url: https://apihub.agnes-ai.com/v1
      # api_key: not set
      # key_env: not set
      model: agnes-2.0-flash
```

**Result:** Falls through to `OPENAI_API_KEY` env var. Works if `base_url` looks OpenAI-like. **Fragile** — if another service also uses `OPENAI_API_KEY`, they conflict.

## For the Primary Model (provider: custom, not custom:name)

When `model.provider: custom` is used (not a named custom provider alias), the resolution is slightly different:

```python
# From runtime_provider.py:
api_key_candidates = [
    explicit_api_key,
    model.api_key (from config.yaml model section),
    os.getenv("CUSTOM_BASE_URL") -> env_custom_base_url,
    os.getenv("OPENAI_API_KEY") if base_url looks like OpenAI,
    os.getenv("OPENROUTER_API_KEY") if base_url like OpenRouter,
    os.getenv("OPENAI_API_KEY")    # generic fallback
]
```

## Verification

To verify which key Hermes actually resolves for a custom provider:

```bash
cd /opt/data && . /opt/hermes/.venv/bin/activate && python3 -c "
from hermes_cli.runtime_provider import resolve_runtime_provider
# For named custom provider 'agnes':
r = resolve_runtime_provider(requested='custom:agnes')
print(f'provider={r.get(\"provider\")}')
print(f'base_url={r.get(\"base_url\")}')
print(f'key loaded: {bool(r.get(\"api_key\"))}')
print(f'key length: {len(r.get(\"api_key\", \"\"))}')
# Check first/last 8 chars to confirm it's the right key
k = r.get('api_key', '')
if k:
    print(f'key prefix: {k[:8]}...')
    print(f'key suffix: ...{k[-8:]}')
"
```

The `requested` arg accepts: provider name (`"openrouter"`), custom provider key (`"custom"`), or named custom provider (`"custom:agnes"`), or model name to auto-resolve.
