# GitHub Auth for Agent Reach

## PAT Generation (Mobile-Friendly)

When user is on phone (Feishu/mobile chat), guide them step by step:

### Step 1: Generate Token
1. Open `https://github.com/settings/tokens/new` in phone browser
2. Token name: anything (e.g. `hermes-agent`)
3. Expiration: **No expiration**
4. Check scopes:
   - `repo` (full control)
   - `read:user` (user info)
   - `read:org` (optional)
5. Click green **"Generate token"**
6. Copy the `ghp_...` string

### Step 2: Authenticate
After the real gh CLI is installed (downloaded from releases, NOT uv tool):

```bash
export PATH="/opt/data/home/.local/bin:$PATH"
echo "ghp_XXX" | gh auth login --with-token
```

### Step 3: Verify
```bash
gh auth status  # should show ✓ Logged in
gh api user     # should return JSON with user info
```

## Pitfalls
- **Never use `uv tool install gh`** — it gives a broken v0.0.4 wrapper
- **PAT with full permissions is fine** for agent use — scoped to HTTPS git ops only
- **gh stores tokens in `~/.config/gh/hosts.yml`** — encrypted at rest