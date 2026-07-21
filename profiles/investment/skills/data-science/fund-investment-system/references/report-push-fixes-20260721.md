Key learnings from 2026-07-21 session:

1. **push_report_r2.py** — shared module for all report MD/HTML generation + R2 upload. Used by run_morning.py, run_noon.py, run_closing.py, run_weekend.py, run_weekly_review.py, run_execute_plan.py, run_evolution_verify.py. All fixes to it benefit all scripts automatically.

2. **HTML rendering critical fix**: `_fmt()` must do `re.sub(r'\*\*(.+?)\*\*', '<strong>\\1</strong>', text)` BEFORE `escape(text)`. If escape runs first, `**` becomes `&ast;&ast;` and the regex won't match. Then restore tags with `replace('&lt;strong&gt;', '<strong>')`.

3. **Table rendering**: NO `white-space: nowrap` on table cells. Use `overflow-x: auto` on wrapper. Skip `:---` markdown separator rows.

4. **Dark/light mode**: CSS variables on `:root`, `.dk` class overrides, JS toggle, system preference detection. No `@media prefers-color-scheme`.

5. **report_manager.py** — structured storage by year/month/day/{type}.md/.html + index.json for historical queries.

6. **review_engine.py** — daily 17:00 review: quality check + prediction verification + backtesting + dashboard + evolution analysis.