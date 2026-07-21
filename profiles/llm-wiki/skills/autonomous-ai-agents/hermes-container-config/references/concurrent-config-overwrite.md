# Concurrent Config Overwrite (Discovered 2026-06-22)

## The Bug

Setting `config.yaml` via Python (`yaml.safe_load → modify → yaml.dump`) works at the moment of writing. But if another agent session writes `config.yaml` **after** you, your changes are silently erased.

## Symptoms

1. You set `model.default: nvidia/nemotron-3-ultra-550b-a55b:free` with `provider: openrouter`
2. Verify with `grep -A4 "^model:" config.yaml` — ✅ correct
3. Restart gateway — ✅ still correct
4. Minutes later, someone checks and it's back to `deepseek-v4-flash` with `base_url: https://api.deepseek.com/v1`
5. The fallback chain also changes (e.g. from 5 entries to 22)

## Root Cause

Each agent session that modifies `config.yaml` reads the full config, changes one field, and writes the ENTIRE YAML back. The last writer wins. If session A wrote `model.default = nemotron-ultra-free` and then session B writes the full config (maybe to fix the fallback chain or add a provider), session B overwrites session A's `model.default` back to whatever was in B's copy of the data.

## Mitigations

1. **Use `hermes config set`** when the CLI binary is available and the `hermes` command is in PATH — it uses atomic file operations
2. **Write from a terminal session, not a background agent** — terminal sessions are single-threaded; background agents (delegation/cron) may write concurrently
3. **Always verify after writing**:
   ```bash
   grep -A4 "^model:" /opt/data/config.yaml
   ```
4. **Use a lock file** if multiple agents need to coordinate:
   ```python
   import fcntl
   with open('/opt/data/.config.lock', 'w') as lock:
       fcntl.flock(lock, fcntl.LOCK_EX)
       # read, modify, write config.yaml here
       fcntl.flock(lock, fcntl.LOCK_UN)
   ```

## Detection

After any config.yaml write, immediately verify with:
```bash
cd /opt/data && python3 -c "
import yaml
with open('config.yaml') as f: cfg = yaml.safe_load(f)
print(f'Model: {cfg[\"model\"][\"default\"]} ({cfg[\"model\"][\"provider\"]})')
print(f'Base URL: {cfg[\"model\"][\"base_url\"]}')
print(f'Fallback count: {len(cfg.get(\"fallback_providers\", []))}')
"
```

If the model doesn't match what you just wrote, your write was overwritten.
