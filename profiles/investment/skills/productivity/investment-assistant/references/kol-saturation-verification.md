# KOL Saturation Verification Methodology

## When Is Data "Enough"?

Methodology: Data Saturation (Guest et al. 2006, Field Methods) — stop expanding when new data no longer changes the profile.

## 4-Criteria Saturation Matrix

| Criterion | Metric | Saturation Threshold | How to Check |
|-----------|--------|:--------------------:|--------------|
| Sample size | Total posts | >= 80 posts | Count |
| Density stability | Quartile density (Q1-Q4) | Max-min < 15% and ratio < 2 | Split posts into 4 quartiles, compute signal density per quartile |
| Signal density | Raw & per-signal counts | > 10% (or classify as 'non-signal source') | SIGNAL_WORDS_MAP hits / total posts |
| Style stability | Style classification | Consistent across 2 consecutive phases | Compare Phase N vs Phase N-1 style tags |

**Saturated** = 3/4 criteria met.

**If NOT saturated:** determine which criterion failed and expand only that dimension (more posts for sample size, or analyze a wider time range for style stability).

## Iterative Collection Protocol

```
Phase 0 (20 posts):
  - Pull page 1 of mymblog API
  - Generate initial profile draft
  - Check: signal density > 20%?
    → Yes: proceed to Phase 1
    → No: need more samples (signal may be real but sparse)

Phase 1 (50 posts cumulative):
  - Pull pages 2-3
  - Re-analyze, compare stability with Phase 0
  - Check: first_half_density vs second_half_density diff < 15%?
    → Yes: pattern stable, proceed
    → No: still evolving, expand more

Phase 2 (80+ posts cumulative):
  - Pull pages 4+, merge
  - Full 4-criteria check
  - Check: pre-judge Phase 2 posts using Phase 1 model
    → Accuracy > 60%: saturated ✓
    → Accuracy <= 60%: expand to 150+

Validation:
  - Expand ONE KOL to 150+ posts
  - Verify 80-post profile matches 150-post profile
  - If consistent, methodology is validated ✓
```

## Recorded Outcomes (2026-06-26)

| KOL | Final N | Density | Saturated? | Notes |
|-----|:-------:|:-------:|:----------:|-------|
| 唐史主任司马迁 | 116 -> 150+ verified | 26.7% | ✅ | Profile at 116 matches 227, validated |
| 小浣熊1230 | 80 | 26.3% | ✅ | Pattern stable, style consistent |
| IT精英带你养基 | 80 | 7.5% | ✅ Non-signal | 137-day span confirms low density is intrinsic |
| 莫非是托的微博 | 300 | 10% | ⚠️ No-depth | 0 long posts, 38-day span only |
