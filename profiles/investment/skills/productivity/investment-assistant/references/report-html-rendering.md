# Report HTML Rendering Standards (2026-07-21)

## R2 Push Pattern

All LLM reports use `push_report_r2.push_report(type, title, tables, analysis)`:
1. Saves MD locally at `fund_system_data/reports/{type}_{date}.md`
2. Generates HTML via `_build_html(full_md, title)`
3. Uploads both MD + HTML to R2 `fund-system/reports/{type}_{date}.md/.html`
4. Pushes short summary with R2 links via QQ Bot (NOT full content — 4000 char limit)

## HTML Rendering (`_build_html()`)

### Table Rendering
- NO `white-space: nowrap` on td/th cells (causes horizontal scroll)
- Wrapper div: `.tw` with `overflow-x: auto`
- Skip `:---` markdown separator rows via `all(c in '|:- ' for c in s)` check
- All cells rendered via `_fmt()` for inline markdown

### `_fmt()` Function — Critical Ordering
```python
def _fmt(text: str) -> str:
    t = text
    # 1. Bold FIRST (before escape)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    # 2. Escape remaining HTML
    t = escape(t)
    # 3. Restore preserved strong tags
    t = t.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
    # 4. Color markers
    t = t.replace('🔴', '<span class="up">🔴</span>')
    t = t.replace('🟢', '<span class="down">🟢</span>')
    t = t.replace('📈', '<span class="up">📈</span>')
    t = t.replace('📉', '<span class="down">📉</span>')
    return t
```
WARNING: If `escape()` is called BEFORE the regex, `**` becomes `&ast;&ast;` and `\*\*` regex won't match.

### Dark/Light Mode
- CSS variables on `:root` for light, `.dk` class overrides for dark
- Toggle button: `document.body.classList.toggle('dk')`
- System detection: `window.matchMedia('(prefers-color-scheme:dark)')` on page load
- NO `@media prefers-color-scheme` block — use JS class toggle only
- Variable example: `--bg:#f0f2f5` (light) → `--bg:#0d0d1a` (dark)

### AI Analysis Section Structure
Each step renders as `.st` card with colored border:
| Step | Icon | Border Color |
|------|------|-------------|
| 步骤1/隔夜 | 🌙 | purple (`#6c5ce7`) |
| 步骤2/复盘 | 👁️ | green (`#00b894`) |
| 步骤3/作战 | 🗺️ | yellow (`#fdcb6e`) |
| 步骤4/风险 | ⚠️ | red (`#e17055`) + risk bg |
| 步骤5/优先级/基金 | 🎯 | red (`#e74c3c`) |

### Step Body Rendering Priority
1. `#### text` → `<h4>` (NEVER leave as raw markdown)
2. `### text` → `<h3>`
3. `|table|` → collect rows, skip `:---` separators, render as `<table>`
4. `> text` → `<blockquote>` with left border
5. `⚠️` / `风险` / `最怕` → `<div class="rc">` risk card
6. `- ` / `* ` list items → `<p class="li">` with `▸` bullet
7. `**text**` → `<p class="bl">` bold line
8. Numbered items (`1. `) → `<p class="li">`
9. Regular text → `<p>` with `_fmt()` for inline bold/color
10. `---` → skip entirely

### Fund Operation Table (Step 5)
Special `.ft` table with color-coded columns:
- Priority: `.ph` (最高=red), `.pm` (中=yellow), `.pl` (低=gray)
- Action: `.ab` (加仓=green), `.as` (减仓=red), `.ah` (持有=yellow)
- Reason column truncated to 60 chars
- Change column shows fund P&L with inline color

## Prompt Design Standards

### max_tokens Settings
| Report | max_tokens | Reason |
|--------|-----------|--------|
| morning | 8000 | 5 steps + 14 fund ops |
| noon | 4000 | Shorter midday view |
| closing | 6000 | Full review |
| decision | 4000 | Focused ops |
| weekly | 6000 | Long horizon |

If content ends mid-sentence, increase max_tokens.

### Compact Prompt Strategy
Morning/noon reports should NOT use `FINANCIAL_THEORY_FRAMEWORK`. Use only `T1_FRAMEWORK` (operational constraints) + focused instructions. The theory framework wastes ~700 chars/500 tokens that could go to step 5 fund analysis.

### KOL + P&L Data Injection
- `build_morning_data_v2()` truncates KOL at 1500 chars
- `_kol_summary.txt` has full KOL content (~4000 chars)
- Fix: read KOL file independently, pass up to 3000 chars as separate prompt section
- `build_morning_data_v2()` returns placeholder P&L (0元)
- Fix: read `operations/operation_*.md` independently for real P&L

### Fund Coverage Requirements
Step 5 must cover ALL 14 funds individually (not grouped):
- Each fund gets: name, code, P&L, specific operation direction
- Operation MUST include "15:00前" or "明日计划" label
- Buy/sell signals reference KOL views and trends, not just yesterday's performance

## Daily Review Cycle (review_engine.py)
Runs at 17:00 daily:
1. Quality check: section completeness, min chars, truncation detection
2. Prediction verification: extract predictions → compare vs actual market
3. Backtesting: count buy/sell/hold signal ratios
4. Dashboard: generate `dashboard.html` with accuracy trends
5. Evolution: accuracy trend diagnosis → prompt improvement suggestions

Accuracy data: `evolution/accuracy.jsonl`
Evolution config: `evolution/evolution_config.json`
Dashboard: `reports/dashboard.html` → R2
