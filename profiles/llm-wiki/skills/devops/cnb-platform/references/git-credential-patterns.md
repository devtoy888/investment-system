# CNB Git Credential Management

> Practical patterns for storing CNB access tokens for Git operations.

## CNB Auth Rules

| Field | Value | Source |
|-------|-------|--------|
| Username | `cnb` (fixed) | [CNB Git Access Docs](https://docs.cnb.cool/zh/guide/git-access.md) |
| Password | Access token (NOT account password) | [CNB Access Token Docs](https://docs.cnb.cool/zh/guide/access-token.md) |
| URL format | `https://cnb.cool/org/repo` (`.git` suffix optional) | CNB Docs & official llms.txt |

**Token != Password**: Confirmed via https://docs.cnb.cool/zh/llms.txt — CNB uses **访问令牌** (Access Token), not the account login password.

## Pattern 1: Token in URL (Simplest, Not Secure)

```bash
git remote add origin https://cnb:TOKEN@cnb.cool/org/repo
```

**Downsides**:
- `git remote -v` exposes plaintext token
- Token appears in shell history
- Token embedded in `.git/config`

## Pattern 2: Git Credential Store (Recommended ✅)

### Variant A — Direct echo (simplest, works reliably)

```bash
# Step 1: Configure credential helper (global)
git config --global credential.helper store

# Step 2: Write credential file directly
echo "https://cnb:YOUR_TOKEN@cnb.cool" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Step 3: VERIFY the credential is readable BEFORE switching URL
printf "protocol=https\nhost=cnb.cool\n" | git credential fill
# Expected output:
#   protocol=https
#   host=cnb.cool
#   username=cnb
#   password=YOUR_TOKEN
# If password line is missing, the file format is wrong.

# Step 4: NOW switch to clean URL
git remote set-url origin https://cnb.cool/org/repo

# Step 5: Final verification
git remote -v              # Should show NO token
git push origin main       # Should succeed (reads from ~/.git-credentials)
```

### Variant B — printf + credential-store (for complex tokens)

```bash
printf 'protocol=https\nhost=cnb.cool\nusername=cnb\npassword=YOUR_TOKEN\n' | \
  git credential-store --file ~/.git-credentials store
chmod 600 ~/.git-credentials
git config --global credential.helper 'store --file ~/.git-credentials'
git remote set-url origin https://cnb.cool/org/repo
```

### ⚠️ CRITICAL: Order of operations

1. Set helper + write the file FIRST
2. **Verify credential is readable** with `printf protocol... | git credential fill`
3. THEN switch to clean URL
4. Then test push

If you switch URL FIRST (before credentials are stored), push fails with "Repository Not Found" because there's no credential to authenticate with. Revert URL temporarily to debug.

### 🔍 Full verification checklist

```bash
# 1. Credential file exists and is locked down
ls -la ~/.git-credentials    # Must show -rw------- (600)

# 2. Git can read the credential
printf "protocol=https\nhost=cnb.cool\n" | git credential fill
# Must show password=YOUR_TOKEN

# 3. Remote URL is clean (no token)
git remote -v

# 4. Push works end-to-end
git push origin main
```

### If push fails with "Repository Not Found"

- **Most likely**: credential not recognized yet
- Check: `git config --global credential.helper` → should show `store`
- Check: `cat ~/.git-credentials` → one line `https://cnb:TOKEN@cnb.cool`
- **Temporary recovery**: Use token-in-URL to unblock, then re-debug:
  ```bash
  git remote set-url origin https://cnb:TOKEN@cnb.cool/org/repo
  git push origin main
  # Then debug the credential setup
  ```

## Pattern 3: url.insteadOf (⚠️ NOT RECOMMENDED — has hidden failures)

```bash
git config --global url."https://cnb:TOKEN@cnb.cool".insteadOf "https://cnb.cool"
git remote set-url origin https://cnb.cool/org/repo
```

**Known problems (confirmed in production):**
- `git remote -v` shows the SUBSTITUTED URL (with token), not the clean URL — cosmetic but confusing
- More critically: `git push origin main` may fail with "Repository Not Found" on certain git versions, even when the substitution is configured correctly
- **Prefer Pattern 2** (credential.helper store) instead — it is the only confirmed reliable approach

## Debugging Authentication

```bash
# Check what credential git would use
printf "protocol=https\nhost=cnb.cool\n" | git credential fill

# Check credential helper config
git config --global credential.helper

# Verify credential file content (should be one line)
cat ~/.git-credentials
# Expected: https://cnb:TOKEN@cnb.cool

# Test direct Git access with tracing
GIT_TRACE=1 git ls-remote https://cnb.cool/org/repo 2>&1 | head -30
```

## Common Pitfalls

1. **Heredoc (`<<<`) quoting**: `git credential-store ... <<< 'protocol=...'` can fail with multi-line pasting in Termius. Use `printf ... | git credential-store` or direct `echo > ~/.git-credentials`.

2. **Token with special chars**: If token contains `/`, `#`, or `@`, URL-encode them in inline URLs or use credential store (Pattern 2 handles this safely).

3. **File not found**: `credential.helper store --file ~/.git-credentials` only works if the file exists and the path is expandable. The simpler `credential.helper store` (no `--file`) uses the default path `~/.git-credentials`.

4. **Global vs local**: `credential.helper` should be set globally (`--global`) to work across repos.

5. **Host matching**: The credential file's `host=` field must match the URL's host exactly. For CNB, use `host=cnb.cool`.

6. **cron jobs**: When pushing from cron, the credential file must be readable by the cron user. `~/.git-credentials` is automatically found if `credential.helper store` is set globally.
