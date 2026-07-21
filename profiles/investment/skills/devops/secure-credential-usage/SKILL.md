---
name: secure-credential-usage
description: "Standardized patterns for secure credential handling — no hardcoded keys, no .env file scraping."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [security, credentials, best-practice, env]
---

# Secure Credential Usage

Standard for all user scripts: never hardcode secrets, never directly read `.env` files.

## ❌ What NOT to do

### 1. Hardcoded credentials in code
```python
# BAD — secret lives in source code
uploader = R2Uploader(
    account_id='a14f5ae92b9406c186b0f7f796fb7c50',
    access_key_id='e3498c2d01404128aa9199a887f568c7',
    secret_access_key='4855275a8e6b96fe31c2c19adea28f4eff60cd0cf17f36152ce798bbd5770742',
)
```
**Risk:** Exposed in git, session logs, backups, code review.

### 2. grep/awk .env directly
```python
# BAD — opens the raw .env file, exposes path in logs
key = os.popen("grep 'CUSTOM_AGNES_API_KEY' /opt/data/.env").read().strip()
```
**Risk:** File path hardcoded, stdout may leak to logs, breaks if env location changes.

### 3. open(.env) full parse
```python
# BAD — reads entire credential store into memory
env = {}
with open('/opt/data/.env') as f:
    for line in f:
        k, v = line.strip().split('=', 1)
        env[k.strip()] = v.strip()
```
**Risk:** Loads ALL secrets (including SSH keys, platform tokens) into Python memory unnecessarily.

## ✅ What to do instead

### For R2 credentials (preferred: use R2Uploader)
```python
from r2_uploader import R2Uploader

# Reads R2_ACCOUNT_ID, R2_BUCKET, R2_ACCESS_KEY_ID,
# R2_SECRET_ACCESS_KEY, R2_PUBLIC_URL, R2_ENDPOINT from env
uploader = R2Uploader()
```

### For any env var (generic pattern)
```python
import os

api_key = os.environ.get('CUSTOM_AGNES_API_KEY', '')
if not api_key:
    print("ERROR: CUSTOM_AGNES_API_KEY not set")
    exit(1)
```

### For boto3 / SDKs
```python
import boto3, os
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
    config=Config(signature_version='s3v4')
)
```

## Environment Variable Sources

| Source | Path | Auto-loaded? | Purpose |
|--------|------|-------------|---------|
| Hermes managed | `~/.hermes/.env` (i.e. `HERMES_HOME/.hermes/.env`) | ✅ Yes, at Hermes startup | API keys used by Hermes providers |
| Root user env | `/opt/data/.env` | ✅ Yes (sourced externally) | R2, Agnes AI, platforms |
| Process env | `os.environ` | ✅ Always available | Both sources merged at runtime |

## Operational Rules

1. **Never** modify `.env` files directly as an agent — use `os.environ.get()` to READ. Only the user edits `.env` via SSH on the host.
2. **Never** hardcode credentials visible in code — they will appear in session transcripts and logs.
3. **Preferred order**: `R2Uploader()` (auto) > `os.environ.get()` > direct API calls with env-read key.
4. **Config validation**: print only truncated info (first N chars), never the full value.
5. **For cron/no_agent scripts**: they run in the same process env, so `os.environ.get()` works the same way.
6. **Test API keys with Hermes built-in tools first** — use `web_search()`/`web_extract()` instead of curl/Python one-liners to verify search/extract keys. Only reach for curl when testing a brand-new key that hasn't been configured in Hermes yet, or debugging a provider Hermes tools can't call directly.

## ⚠️ Self-Consistency: Agent Must Follow Its Own Rules

**Critical pitfall:** This skill says "Never modify .env" — but the agent must also **never suggest** modifying .env as if the agent would do it. If the agent says "let me fix that" about a .env issue, it violates its own standing rule.

**Correct pattern:** When a .env issue is found (corrupted key, wrong value, missing variable):
1. Report the issue clearly: what's wrong, which line, what the expected value should be
2. Say "只由你在宿主机上编辑" / "only you can edit this via SSH on the host"
3. Provide the exact `sed` command or Python one-liner the user can run
4. Do NOT say "let me fix it" or suggest the agent will make the edit

**Why this matters:** The rule exists because past agent-directed .env edits corrupted keys (shell truncation, secret redactor writing `***`, duplicate lines). The agent must enforce this consistently even when it's tempting to say "I'll fix it."

### 🚨 Critical: never ask the user to TELL you a credential in chat

**❌ Wrong:** "拿到 token 告诉我就行，我来配置" / "Tell me the token and I'll set it up"
- The token value would appear in session transcripts and logs
- Even in a private DM, this is bad practice — the user has no guarantee where the value might leak

**❌ Also wrong:** "告诉我，我帮你写到配置里" / "Give it to me and I'll put it in config"
- Same leak risk
- Also violates the "agent doesn't write .env" rule — user has to do that anyway

**✅ Correct:** Define the env var name + config path, let the user add it themselves:
```
# Define env var name and expected usage
CNB_ACCESS_TOKEN — used for CNB API Bearer auth and Git password auth

# Tell user to add it
# "你加到 .env 里就行，我不碰那个文件"
```
Then have the script read from `os.environ.get('CNB_ACCESS_TOKEN')`.

**Why users call this out:** High-signal correction. When a user says "重要配置不要明文配置" / "I thought you knew not to put secrets in chat", they mean it. This is a trust issue — if you're careless with credentials, they won't trust you with more sensitive tasks.

## Verification

After any credential refactor, test by running the script:
```bash
# The script must work without any hardcoded values
/opt/hermes/.venv/bin/python3 path/to/script.py --dry-run

# Check no plaintext secrets in the file
grep -n "api_key\|secret\|token\|password" path/to/script.py
# Should only show os.environ.get() or R2Uploader() patterns
```
