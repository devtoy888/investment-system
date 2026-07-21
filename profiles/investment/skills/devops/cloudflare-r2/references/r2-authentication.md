# R2 Authentication Pitfalls

## Problem: API Token vs Access Key

**Session 2026-06-23:** User provided R2 API Token (`cfut_Qhao5tkJQ3qinlK0rMA8nFUdRIHafSbaz97UQeSZ40115689`) expecting it to work with boto3. It does not.

### Symptoms observed
1. boto3 error: `Credential access key has length 53, should be 32`
2. Direct PUT to S3 endpoint: `Missing x-amz-content-sha256`
3. Adding sha256: `No date provided in x-amz-date nor date header`
4. Cloudflare API v4 endpoint: `7000: No route for that URI`

### Root Cause
R2 API Token (`cfut_` prefix, ~53 chars) is a **Cloudflare API Token**, not an **S3 Access Key**.
- API Token: for Cloudflare REST API v4 (`api.cloudflare.com`)
- Access Key: 32-char ID + secret, for S3-compatible R2 endpoint

### Solution
1. Create separate R2 Access Key from Dashboard → R2 → Manage R2 → Access Keys
2. Use the 32-char Access Key ID + Secret with boto3
3. Always set `region_name='auto'` in boto3 config

### Reference: Official Cloudflare Skill
The official `cloudflare/skills` repo has an R2 reference at `skills/cloudflare/references/r2/` covering:
- S3 SDK setup: `region: 'auto'` is REQUIRED
- API Token scopes: Object Read, Object Write, Admin Read & Write
- CORS, lifecycles, event notifications
