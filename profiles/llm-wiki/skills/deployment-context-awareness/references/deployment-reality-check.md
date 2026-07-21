# Deployment Reality Check — What Went Wrong This Session

## Symptoms Observed
- Git push to CNB succeeded (commit `502fd37`)
- Live site returned 200 but new Vibe-Trading pages were NOT appearing
- Navigation sidebar showed no "Vibe trading" section after initial push

## Root Cause
Files were written to `/opt/data/llm-wiki/docs/` (inside Hermes data volume)
instead of `/llm-wiki/docs/` (bind mount shared with host MkDocs container).

## Why This Happened
1. Memory entry said `LLM Wiki路径: /opt/data/llm-wiki/docs/` — stale
2. No filesystem verification before writing
3. Did not read the wiki's own setup-guide.md for deployment architecture
4. Assumed Cloudflare Pages instead of checking the actual infrastructure

## Fix Applied
1. Copied files from `/opt/data/llm-wiki/docs/concepts/vibe-trading/` → `/llm-wiki/docs/concepts/vibe-trading/`
2. Updated `/llm-wiki/docs/index.md` and `/llm-wiki/docs/log.md`
3. Git commit + push to CNB (backup only)
4. Waited for host's 15-min crontab `docker restart llm-wiki` cycle
5. Site auto-refreshed after restart → all 7 pages visible

## Verification Steps for Future Sessions
```bash
# 1. Confirm the REAL wiki path
ls -la /llm-wiki/docs/           # Should show concepts/, entities/, index.md

# 2. Confirm the WRONG path differs
ls -la /opt/data/llm-wiki/docs/  # May not exist or be stale

# 3. Check if site is live before/after
curl -s -o /dev/null -w "%{http_code}" https://wiki.devtoy.xyz/concepts/vibe-trading/项目总览/

# 4. Check deployment docs on the live site
curl -s https://wiki.devtoy.xyz/setup-guide/ | grep -c "Docker\|Tunnel\|CNB"
```
