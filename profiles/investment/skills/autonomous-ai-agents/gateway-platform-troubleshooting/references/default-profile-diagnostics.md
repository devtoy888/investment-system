# Default Profile Diagnostics — SOUL.md Read-Only & Missing Platform Config

## Scenario

Docker container deployment (`~/.hermes-main` → `/opt/data`). The default profile's QQ/WeChat/DingTalk channels stopped working. Running `hermes gateway setup` to reconfigure QQ failed with a confusing `PermissionError`.

## Symptom

```
$ hermes gateway setup
...(select QQ Bot, enter appid/secret)...
Traceback (most recent call last):
  File "/opt/hermes/.venv/bin/hermes", line 10, in <module>
    sys.exit(main())
  File "/opt/hermes/hermes_cli/main.py", line 13651, in main
    args.func(args)
  File "/opt/hermes/hermes_cli/main.py", line 2417, in cmd_gateway
    gateway_command(args)
  File "/opt/hermes/hermes_cli/gateway.py", line 6313, in gateway_command
    return _gateway_command_inner(args)
  File "/opt/hermes/hermes_cli/gateway.py", line 6461, in _gateway_command_inner
    gateway_setup()
  File "/opt/hermes/hermes_cli/gateway.py", line 6045, in gateway_setup
    _configure_platform(platforms[choice])
  File "/opt/hermes/hermes_cli/gateway.py", line 5921, in _configure_platform
    fn()
  File "/opt/hermes/hermes_cli/gateway.py", line 5664, in _setup_qqbot
    save_env_value("QQ_APP_ID", credentials["app_id"])
  File "/opt/hermes/hermes_cli/config.py", line 7055, in save_env_value
    ensure_hermes_home()
  File "/opt/hermes/hermes_cli/config.py", line 866, in ensure_hermes_home
    _ensure_default_soul_md(home)
  File "/opt/hermes/hermes_cli/config.py", line 838, in _ensure_default_soul_md
    soul_path.write_text(DEFAULT_SOUL_MD, encoding="utf-8")
  File "/usr/lib/python3.13/pathlib/_local.py", line 557, in write_text
    return PathBase.write_text(self, data, encoding, errors, newline)
  File "/usr/lib/python3.13/pathlib/_abc.py", line 651, in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
  PermissionError: [Errno 13] Permission denied: '/opt/data/SOUL.md'
```

## Root Cause 1: SOUL.md Read-Only

```
$ ls -la /opt/data/SOUL.md
-r--r--r-- 1 hermes hermes 536 Jun 21 13:08 /opt/data/SOUL.md
```

`ensure_hermes_home()` is called by `save_env_value()` every time the CLI needs to write a platform credential to `.env`. It checks if the Hermes home has a valid SOUL.md, and if not (or if the current version differs), tries to write the default one. If SOUL.md is `0444` (read-only for everyone), this fails.

**Fix:**
```bash
chmod 644 /opt/data/SOUL.md
```

## Root Cause 2: Missing `platforms.qqbot.enabled: true`

Even if `.env` has correct `QQ_APP_ID` and `QQ_CLIENT_SECRET`, the gateway process won't initialize QQ Bot if the root config.yaml's `platforms:` section is missing the entry:

```yaml
# In /opt/data/config.yaml's platforms: section
platforms:
  feishu:
    enabled: true
  dingtalk:
    enabled: true
  telegram:
    enabled: true
  weixin:
    enabled: true
  # ❌ qqbot entry MISSING — QQ won't start even if .env has credentials
```

**Fix — add:**
```yaml
  qqbot:
    enabled: true
```

## Architecture: Default Profile = Root Hermes Home

In container deployments:
- `/opt/data/` (mapped from `~/.hermes-main`) **IS** the default profile
- There is NO `/opt/data/profiles/default/` directory
- The root `config.yaml` IS the default profile's config
- Profile directories under `profiles/<name>/` (e.g. `profiles/investment/`) are secondary profiles only

## Gateway-Native vs Plugin Platforms

| Type | Platforms | Needs `plugins.enabled`? | Needs `platforms.xxx.enabled: true`? |
|------|-----------|------------------------|--------------------------------------|
| **Gateway-native** | QQBot, Weixin | ❌ No | ✅ Yes (in root config.yaml's `platforms:` section) |
| **Plugin-based** | Feishu, DingTalk, Telegram, Discord | ✅ Yes | ✅ Yes |

## Diagnostic Checklist

```bash
# 1. Check SOUL.md permissions
ls -la /opt/data/SOUL.md
# Expected: -rw-r--r-- (644), not -r--r--r-- (444)

# 2. Check root config.yaml platforms section
grep -A 30 "^platforms:" /opt/data/config.yaml | head -30

# 3. Check if the platform's credentials exist in .env
grep "QQ_APP_ID\|QQ_CLIENT_SECRET\|WEIXIN" /opt/data/.env

# 4. Check if the platform's entry exists in platforms:
grep -A 30 "^platforms:" /opt/data/config.yaml | grep -B 1 -A 1 "qqbot\|weixin"
```
