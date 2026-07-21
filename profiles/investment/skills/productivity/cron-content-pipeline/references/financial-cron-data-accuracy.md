# Financial Cron Data Accuracy Patterns

Three patterns for building reliable financial market monitoring cron jobs that avoid common data-labeling and verification bugs.

## 1. Direction Verification: Predictions vs Actuals (not Open-vs-Close)

**The bug:** A closing review cron compared `morning_change_pct` (the index's change % from prev_close at early-morning collection time) with `closing_change_pct`. But both were positive (the index was volatile intraday but closed higher), so every index was marked ✅ — even those that opened lower and reversed. **This is wrong because the verification should evaluate whether the morning prediction was correct, not whether open/close directions match.**

**The correct question to ask:** Did the morning prediction (e.g. "上证指数开方向↓") match the actual outcome (the index closed ↑ or ↓ relative to prev_close)? This is fundamentally about **prediction accuracy**, not about whether the opening trend continued through the close.

### Architecture: Cross-Job Prediction Handoff

The morning cron generates predictions via LLM, but these predictions live in the AI's output text — invisible to the closing cron's data layer. The fix requires structured data handoff between jobs.

**1. Morning cron saves predictions as JSON** before pushing:

```bash
cat > /tmp/fund_data/_morning_predictions.json << 'PREDEOF'
{
  "date": "2026-06-30",
  "predictions": [
    {"index": "上证指数", "predicted_direction": "↓", "reason": "预计低开"},
    {"index": "科创50", "predicted_direction": "↑", "reason": "预计高开"},
    ...
  ]
}
PREDEOF
```

**2. Closing cron reads predictions and verifies each one:**

For each prediction, compare `predicted_direction` (↑/↓) against the index's actual `change_pct` (positive=↑, negative=↓).

```
验证 ✅ = predicted_direction matches actual change_pct direction
验证 ❌ = predicted_direction mismatches actual change_pct direction
```

**3. The prompt template pattern for the closing cron:**

```markdown
## 验证早盘预测
读取 `/tmp/fund_data/_morning_predictions.json`，对每条预测验证：
- 取 `predicted_direction`（↑/↓）
- 取收盘实际涨跌幅 `change_pct`（正=涨↑, 负=跌↓）
- 如果预测方向与实际方向一致 → ✅；不一致 → ❌
```

**4. Fallback when prediction file is missing** (first day after deployment, manual trigger, /tmp cleaned): The closing cron should gracefully skip the prediction verification section with a note rather than failing or hallucinating predictions.

### Comparison: What NOT to Do (proven wrong patterns)

| Pattern | What it checks | Why it's wrong |
|---------|---------------|----------------|
| Morning change_pct vs closing change_pct | Whether early-morning direction persisted through close | Morning data may be stale or from near-close; both can be positive even when prediction was wrong |
| Open direction vs close direction | Whether opening trend continued | A correct prediction "开方向↓" followed by actual "收盘↑" should be ❌ (prediction wrong), not ✅ |
| Predicted direction vs actual opening direction | Whether opening prediction was correct | Correct, but doesn't tell user about overall day direction |

### Data source for closing change_pct

Closing data from Tencent Finance API (`get_tencent_quote()` in fund_tools.py) includes `price` (close) and `prev_close`. `change_pct = (price / prev_close - 1) * 100`.

### Pitfall — data overwrite

If the morning pre-collection script calls `get_all_quotes()` and also writes to `_raw_data.json`, subsequent runs (noon, closing) will overwrite it with their own data. **The morning cron must save its predictions separately** via `_morning_predictions.json`. Do NOT rely on `_raw_data.json` for cross-job data.

## 2. Data Labeling Accuracy: Estimated vs Confirmed

**The bug:** A "收盘复盘" (closing review) push labeled fund NAV as "今收估算" (today's closing estimate), which felt inaccurate to the reader since it's sent after market close.

**The data reality:** Fund NAV APIs (e.g. 天天基金 `fundgz.1234567.com.cn`) return:
- `gsz` (估算净值, estimated NAV) — real-time estimate based on underlying holdings, updated during trading hours
- `gszzl` (估算涨跌幅, estimated change %) — calculated from estimated NAV vs last confirmed NAV
- `dwjz` (单位净值, unit NAV) — the **last confirmed** NAV (not today's!), from `jzrq` (净值日期, NAV date)

The confirmed NAV is typically published by fund companies between **19:00-20:00 CST** (11:00-12:00 UTC). Any cron job running before that window **must** label its fund data as "estimated" or the user will be misled into thinking they have final settlement prices.

**Prompt template pattern:**
```markdown
基金数据说明：基金净值是"估算净值"（基于ETF持仓盘中实时估算），
天天基金正式净值一般在晚间19:00-20:00公布。这里显示的是收盘时点的估算值。
```

**When to upgrade to confirmed NAV:** The next-morning's 今日参考 cron can use yesterday's confirmed NAV (from `dwjz` + `jzrq` field) for accurate reference, since the previous day's NAV is settled overnight.

## 3. Date Context Awareness: Special Dates in Financial Reporting

**The bug:** A 6/30 (上半年收官日) closing review push said "明日..." (tomorrow...) in its market outlook. 7/1 isn't just "tomorrow" — it's the **first trading day of the second half of the year**.

**The principle:** Financial markets attach special significance to boundary dates. The cron prompt must explicitly tell the agent to check for these dates and use appropriate terminology.

**Date cases to check:**

| Date | Significance | Correct Terminology |
|------|-------------|-------------------|
| Month-end (any month) | Last trading day of month | "下月首个交易日" |
| 3/31, 6/30, 9/30, 12/31 | Quarter-end / half-year-end | "下季度/下半年首个交易日" |
| 12/31 | Year-end (if trading day) | "新年首个交易日" |
| Pre-holiday (e.g. day before 春节) | Last trading day before holiday | "节后首个交易日" |
| Post-holiday first day | First trading day after holiday | "节后首个交易日" |

**Implementation:**
```markdown
## 第三步：判断特殊日期
检查今天日期：如果是月末(如6/30)、季末(3/31,6/30,9/30,12/31)、
半年末(6/30,12/31)，在推演中要用"下半年首个交易日""下月首个交易日"
等准确表述，**不要说"明日"**。
- 今天是6月30日 = **上半年收官日**
- 下一个交易日是7月1日 = **下半年首个交易日**，不是普通的"明日"
```

**Generalization:** This applies to any domain cron job where dates carry semantic meaning beyond the calendar — earning seasons, reporting periods, fiscal years, regulatory deadlines.

## 4. AI Output Self-Verification After Push

**The problem:** Pushed cron output keeps having format issues (missing tables, wrong column count, broken markdown). The user finds these bugs, not the agent.

**The requirement:** After generating but before pushing, the cron agent must self-verify format, data accuracy, and logical consistency.

**Self-check checklist to embed in every cron prompt:**

```markdown
## 格式自检（推送前执行）
1. 表格列对齐：[列出每张表的列数要求]
2. 数据一致性：[检查点，如"所有指数数据与 summary 文件一致"]
3. 预测来源：[如"预测验证列必须从 _morning_predictions.json 读取，不能瞎编"]
4. 涨跌幅符号：正负号 +/-
5. 禁用词：[如"禁止出现'明日'字样"]
6. 非交易日防误判：不要编造行情数据
```

**Why prompt self-check works over script-based validation:** The LLM that generated the output is best positioned to check its own format compliance — it knows what it intended to write and can catch structural mismatches before delivery. A post-hoc script can catch some errors (missing columns, wrong numbers) but cannot judge semantic consistency (e.g. "does the prediction reason match the actual data?").

**However, self-check alone is insufficient for format stability** — see Section 5 for the definitive fix.

## 5. Format Stability: Pre-Generated Output in Pre-Script (Definitive Fix)

**The chronic problem:** Despite explicit table templates, format instructions, and self-check steps, the LLM keeps deviating from the required markdown table format. This happened 3+ times across different cron jobs.

**Root cause:** LLMs are unreliable for strict formatting. Even with verbatim templates, they drift — reordering columns, omitting rows, switching to prose.

**The definitive fix:** Move ALL formatting from the LLM to the pre-script (Python). The pre-script generates a complete, pre-formatted markdown file (`_closing_tables.md`). The AI's only job: output it verbatim + add analysis content (e.g. market outlook).

### Architecture

```
[pre-script (Python)]
    ↓  fetches all data, formats into markdown tables
    ↓  writes _closing_tables.md (all data sections complete)
[LLM step (agent)]
    ↓  reads _closing_tables.md (cat command)
    ↓  outputs it verbatim — NO formatting changes
    ↓  appends analysis section(s) only
[Delivery]
```

### Pre-script responsibilities

The pre-script generates ALL structured sections:
- **大盘走势** — markdown table with 指数/昨收/今开/收盘/涨跌/开方向
- **两市成交** — formatted text
- **行业板块** — inline list with emoji and percentages
- **北向资金** — formatted text
- **持仓基金** — grouped list (not table for fund names with long names)
- **早盘预测验证** — markdown table with 指数/开方向预测/收盘实际/验证

### LLM prompt for this pattern

```markdown
## 第四步：输出推文并添加推演
**重要：表格部分直接输出 _closing_tables.md 的内容，一字不改！不要重新排版！不要改格式！**
**你只需要在预格式化内容的末尾添加 🔮 后市推演 章节。**

完整输出结构：
1. 输出 _closing_tables.md 的全部内容（原样复制，不修改任何数据/格式）
2. 在其后添加：

🔮 **后市推演**
（你的分析内容，结合趋势、成交额、北向信号、特殊日期）
```

### Implementation details (closing_review.py)

The pre-script generates `_closing_tables.md` as follows:

```python
# ── 10. 生成预格式化推文（LLM直接输出，无需改格式）──
push_lines = []

# 判断特殊日期
date_note = ""
if today.endswith(('03-31', '06-30', '09-30', '12/31')):
    ...

push_lines.append("━━━ 🌆 收评 · 基金收盘复盘 · {today}({date_note}) ━━━")
push_lines.append("")

# 大盘走势表格 — script-generated, always correct columns
push_lines.append("📊 **大盘走势**")
push_lines.append("| 指数 | 昨收 | 今开 | 收盘 | 涨跌 | 开方向 |")
push_lines.append("|:----|:---:|:---:|:----:|:----:|:-----:|")
for name, v in market_accuracy.items():
    ...

# 基金表格 — grouped, per-fund detail
push_lines.append("💰 **持仓基金（收盘估算净值，待晚间确认）**")
for gname in GROUPS:
    ...

# 早盘预测验证 — from _morning_predictions.json
predict_path = SUMMARY_DIR / "_morning_predictions.json"
if predict_path.exists():
    ...

(SUMMARY_DIR / "_closing_tables.md").write_text("\n".join(push_lines))
```

### Self-verification still needed

Even with pre-generated output, the LLM might still wrap it in a markdown code block or add decorative lines. The self-check step should verify:

1. The output starts with the correct header (e.g. "━━━ 🌆 收评")
2. No markdown code block wrappers (triple backticks) around the tables
3. The analysis section follows after the pre-generated content
4. No extra columns or formatting artifacts

### When to apply this pattern

| Cron type | Apply pre-generated tables? | LLM-only sections |
|-----------|:--------------------------:|-------------------|
| Closing review (many data sections) | ✅ Yes — all data tables | 后市推演 only |
| Morning brief (prices + funds) | ✅ Yes — data tables | 盘前展望 only |
| Noon flash (real-time) | ✅ Yes — data tables | 下午展望 only |
| Any cron with 3+ structured sections | ✅ Yes | Analysis only |

The guiding principle: **Python formats data, LLM formats prose.** Never ask the LLM to format structured data.

## 6. Feishu Deprecated for This System (2026-07-18)

All delivery is now through QQ Bot only via `send_qqbot.py` (print Markdown to stdout, cron `deliver=origin`). The `send_*_cards.py` scripts had their `.feishu-deps` path removed. Do not add new Feishu delivery code. The main changes:
- `send_morning_cards.py` / `send_noon_cards.py` / `send_closing_cards.py`: removed `.feishu-deps` from sys.path
- `run_morning.py` / `run_noon.py` / `run_closing.py` (wrappers): removed `.feishu-deps` from env
- All 3 cron jobs changed from `deliver: local` to `deliver: origin`

## 7. Trading Day Auto-Validation (2026-07-18)

Set up 3 auto-validation jobs on trading days via `trading_day_validate.py`:
| Job | Time | Validates |
|:----|:----:|:----------|
| Round 1 | 09:35 | API endpoints reachable, _stale flags flipped correctly |
| Round 2 | 13:00 | Cross-validation (Tencent vs AKShare, Tiantian vs AKShare) |
| Round 3 | 15:30 | Closing data accuracy, archive completeness |

Use `no_agent=true` + `script=trading_day_validate.py`. Script self-detects trading days via `fund_tools.is_trading_day()`.
