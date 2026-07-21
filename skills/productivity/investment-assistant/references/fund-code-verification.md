# Fund Code Verification Protocol

## Why This Exists

2026-06-26: User provided fund codes from screenshots (蚂蚁财富APP). ~50% of the codes were wrong. The wrong codes caused inaccurate NAV data in the morning briefing.

## Rules

1. **NEVER trust fund codes from screenshots or manual transcription.** Screenshot OCR has unacceptably high error rates.
2. **ALWAYS verify via API before adding to FUND_CODES.** The 天天基金 API confirms both existence and name.
3. **Batch-verify all codes after any bulk update.**

## Verification Script

```bash
python3 /opt/data/scripts/verify_fund_codes.py
```

This iterates FUND_CODES, calls `https://fundgz.1234567.com.cn/js/{code}.js` for each, and prints the API-returned name. Mismatches and failures are flagged.

## What Makes a Code Valid

The API returns:
```
jsonpgz({"fundcode":"026421","name":"大摩ESG量化混合C","jzrq":"2026-06-25","dwjz":"0.5950","gsz":"0.5804","gszzl":"-2.46%"})
```

- `name` must match the expected fund name
- `dwjz` (unit NAV) must be a non-empty number
- `jzrq` (NAV date) should be recent

## Error Patterns

| API Response | Meaning | Action |
|-------------|---------|--------|
| Empty / short response | Invalid code | Remove from FUND_CODES |
| `jsonpgz(...)` with wrong name | Valid code, wrong name | CORRECT the name |
| Timeout (HTTPSConnectionPool) | Rate limit | Retry after 1s delay |
| No `jsonpgz(` in response | Not a fund code | Remove from FUND_CODES |

## Historical Errors Found

| Given Code | Correct Code | Fund Name |
|:----------:|:------------:|-----------|
| 009477 | 009478 | 中银上海金ETF联接C |
| 012045 | 026421 | 大摩ESG量化混合C |
| 016803 | 026449 | 大摩沪港深科技混合C |
| 014280 | 163302 | 大摩资源优选混合(LOF) |
| 012552 | 024418 | 华夏科创板半导体材料ETF联接C |
| 013209 | 012329 | 天弘中证新能源指数增强C |
| 016298 | 024913 | 华夏国证通用航空ETF联接C |
