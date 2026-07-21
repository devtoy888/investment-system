# v2 LLM Analysis Engine Architecture

**Created**: 2026-07-20
**Status**: Active (llm_analysis_v1.py deprecated, kept for compatibility)

## Architecture Overview

```
llm_analysis_v2.py
├── T1_FRAMEWORK           # T+1 fund operation rules (corrected)
├── FINANCIAL_THEORY_FRAMEWORK  # 5 financial theory frameworks
├── call_ds()              # DeepSeek V4 Flash API direct call
├── cache functions        # Per-report-type daily cache in /tmp/llm_analysis_cache/
├── Data builders (6)      # Build structured data for each report type
│   ├── build_closing_data_v2()
│   ├── build_morning_data_v2()
│   ├── build_noon_data_v2()
│   ├── build_decision_data_v2()
│   ├── build_weekly_data_v2()
│   └── build_weekend_data_v2()
├── Prompts (6)            # Each = T1 + Theory + Role + Steps
│   ├── CLOSING_PROMPT_V2  # 6-step:定性→板块→组合→信号→推演→操作
│   ├── MORNING_PROMPT_V2  # 5-step:传导链→复盘→作战→风险→关注
│   ├── NOON_PROMPT_V2     # 5-step:定位→轮动→量价→策略→方向
│   ├── DECISION_PROMPT_V2 # 4-step:画像→赛道→逐基评分→风险检查
│   ├── WEEKLY_PROMPT_V2   # 4-step:全景→归因→KOL→下周策略
│   └── WEEKEND_PROMPT_V2  # 4-step:全球→持仓→KOL→周一策略
├── generate_v2()          # Generic generator + evolution engine
├── format_block()         # Push formatting helper
├── get_multi_day_trend()  # Read daily-snapshots.jsonl for 5-day trend
├── get_portfolio_pnl()    # Read latest portfolio P&L
└── get_news_headlines()   # RSS news from news_sources.json
```

## Prompt Injection Pattern

Each prompt is a concatenation of 3 parts:
```python
PROMPT_V2 = T1_FRAMEWORK + "\n" + FINANCIAL_THEORY_FRAMEWORK + "\n" + """role description + steps"""
```

## Evolution Engine Integration

`generate_v2()` calls `evolution_engine.full_evolution_cycle()` with max_tokens:
```python
from evolution_engine import full_evolution_cycle
analysis, preds = full_evolution_cycle(report_type, data, prompt, max_tokens=max_tok)
```

**⚠️ CRITICAL: evolution_engine.py must NOT hardcode max_tokens.**
- `two_pass_generate()` default `max_out=1500` — but this is overridden by `full_evolution_cycle(max_tokens=...)`
- Pass 1 (draft) and Pass 3 (polish) both use the same `max_out` value
- If analysis gets truncated, check evolution_engine's `max_tokens` parameter first

## Data Flow Per Report

Each report type collects data via:
1. **Wrapper script** (profiles/investment/scripts/run_*.py) — collects data, calls v2
2. **Data collection scripts** (scripts/collect_*.py, closing_review.py etc.)
3. **v2 data builder** reads from `/tmp/fund_data/` files + `_source_availability.jsonl` + `daily-snapshots.jsonl`

### Data Sources Injected Per Report (all 6 types get these)

```
━━━ 多日趋势(5日) ━━━        ← from daily-snapshots.jsonl
━━━ 持仓盈亏 ━━━            ← from daily-snapshots.jsonl (latest)
━━━ 最新市场新闻 ━━━         ← from RSS feeds in news_sources.json
━━━ KOL观点 ━━━             ← from _kol_summary.txt / _noon_kol.txt
━━━ 昨日预测回顾 ━━━         ← from predictions.jsonl
```

## 16-Point Quality Checklist (for evaluation)

Run after every v2 generation:

| # | Check | What to verify |
|---|-------|---------------|
| 1 | Step 1 complete | 全景定性 present |
| 2 | Step 2 complete | 板块轮动解构 |
| 3 | Step 3 complete | 逐基诊断 (fund-level) |
| 4 | Step 4 complete | 关键信号/风险 |
| 5 | Step 5 complete | 明日推演/操作方向 |
| 6 | T+1 mentioned | "T+1" or "15:00" |
| 7 | Risk control analysis | P&L-based threshold judgment present |
| 8 | 建仓期保护 | 003096/013403 not sell |
| 9 | 北向资金 analysis | Northbound data used |
| 10 | 3 scenarios + % | Scenario probability |
| 11 | Fund-level codes | Specific fund codes mentioned |
| 12 | Sector direction | 偏多/偏空 per sector |
| 13 | Position sizing | 减仓/加仓 amounts |
| 14 | Risk warning | 风险 mentioned |
| 15 | Style switch | 风格切换 analysis |
| 16 | >3000 chars | Sufficient depth |

## Scoring Evaluation Parsing

**⚠️ CRITICAL PITFALL (fixed 2026-07-20): Never trust the model's "总分" field directly.**

The DeepSeek model outputs the SUM of 5 dimension scores (e.g. 9+7+8+7+7=37), not the average (7.4). The "总分" field in the model's output is the sum.

**Correct approach:**
```python
# DO: Parse each dimension individually, calculate average
scores['data_accuracy'] = int(match.group(2))  # each dimension 1-10
total = sum(scores.values()) / 5                # calculate average, don't read model's "总分"

# DON'T: Use model's total field
total = model_output.get('total', 0)  # WRONG - this is the sum of 5 dimensions!
```

## Common Problems & Fixes

| Problem | Symptom | Fix |
|---------|---------|-----|
| Analysis truncated mid-sentence | Output ends at ~1500 chars | evolution_engine max_tokens too low (was 1200). Increase via `full_evolution_cycle(..., max_tokens=3500)` |
| Evaluation score >10/10 | Shows 37/10 | Parsing bug: using model's sum as total instead of averaging |
| Scoring 0/10 with good content | Failed JSON parsing | Use regex with dimension names in Chinese: `数据准确性=(\d+)` not JSON extraction |
| T+1 rules wrong | Suggests "today sell, tomorrow money available" | T+1 means trade at unknown closing NAV, not money settlement timing |
