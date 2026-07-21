# Credential Audit Patterns — Reference

Concrete scan patterns and remediation examples from actual audits. Add to this file as new patterns are discovered.

## Scan Templates

### Python files — hardcoded credential literals
```bash
# Find lines where a credential variable is assigned a literal string value
search_files(
    pattern="(api_key|api\\.key|API_KEY|secret|token|password|passwd|credential)\\s*=\\s*['\"][A-Za-z0-9_\\-]{10,}['\"]",
    path="/path/to/scripts",
    file_glob="*.py"
)
```

### Shell files — credential variable assignments
```bash
search_files(
    pattern="(api_key|API_KEY|secret|token|password)\\s*=\\s*['\"][A-Za-z0-9_\\-]{10,}['\"]",
    path="/path/to/scripts",
    file_glob="*.sh"
)
```

### Constructor calls with credential parameters
```bash
search_files(
    pattern="R2Uploader\\(|boto3\\.client\\(|boto3\\.resource\\(",
    path="/path/to/scripts",
    file_glob="*.py"
)
```

### Manual .env grepping at runtime
```bash
search_files(
    pattern="grep.*\\.env|os\\.popen.*env",
    path="/path/to/scripts",
    file_glob="*.py"
)
search_files(
    pattern="grep.*\\.env",
    path="/path/to/scripts",
    file_glob="*.sh"
)
```

## Real Remediations from Session History

### Case: R2Uploader with hardcoded credentials

**Before** (2 files found in audit):
```python
uploader = R2Uploader(
    account_id='a14f5ae92b9406c186b0f7f796fb7c50',
    bucket_name='hermes-main',
    access_key_id='e3498c2d01404128aa9199a887f568c7',
    secret_access_key='4855275a8e6b96fe31c2c19adea28f4eff60cd0cf17f36152ce798bbd5770742',
    public_url='https://hermes-main-media.devtoy.xyz'
)
```

**After**:
```python
uploader = R2Uploader()
```

**Validation**: R2Uploader class reads from env vars `R2_ACCOUNT_ID`, `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_PUBLIC_URL`, `R2_ENDPOINT`. All six are set in `.env` and automatically loaded into Hermes process environment.

## Env Var Names in This Deployment

| Service | Env Var | Set? |
|---------|---------|------|
| R2 Account ID | `R2_ACCOUNT_ID` | Yes |
| R2 Bucket | `R2_BUCKET` | Yes |
| R2 Access Key | `R2_ACCESS_KEY_ID` | Yes |
| R2 Secret Key | `R2_SECRET_ACCESS_KEY` | Yes |
| R2 Public URL | `R2_PUBLIC_URL` | Yes |
| R2 Endpoint | `R2_ENDPOINT` | Yes |
| Agnes AI | Config yaml, not .env | Yes (custom provider) |
| DeepSeek | Config yaml | Yes (main provider) |
| OpenRouter | Config yaml | Yes (fallback) |
