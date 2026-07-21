[Skip to content](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account).

[HKUDS](https://github.com/HKUDS)/ **[Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)** Public

- [Notifications](https://github.com/login?return_to=%2FHKUDS%2FVibe-Trading) You must be signed in to change notification settings
- [Fork\\
3.9k](https://github.com/login?return_to=%2FHKUDS%2FVibe-Trading)
- [Star\\
23k](https://github.com/login?return_to=%2FHKUDS%2FVibe-Trading)


## Collapse file tree

## Files

main

Search this repository(forward slash)` forward slash/`

/

# shadow\_account

/

Copy path

## Directory actions

## More options

More options

## Directory actions

## More options

More options

## Latest commit

[![Robin1987China](https://avatars.githubusercontent.com/u/41602358?v=4&size=40)](https://github.com/Robin1987China)[Robin1987China](https://github.com/HKUDS/Vibe-Trading/commits?author=Robin1987China)

[refactor(shadow-account): centralize price feature contract](https://github.com/HKUDS/Vibe-Trading/commit/2acc3b846c72b0959ac848dc47c62158f3c8d773)

Open commit detailssuccess

3 weeks agoJun 27, 2026

[2acc3b8](https://github.com/HKUDS/Vibe-Trading/commit/2acc3b846c72b0959ac848dc47c62158f3c8d773) · 3 weeks agoJun 27, 2026

## History

[History](https://github.com/HKUDS/Vibe-Trading/commits/main/agent/src/shadow_account)

Open commit details

[View commit history for this file.](https://github.com/HKUDS/Vibe-Trading/commits/main/agent/src/shadow_account) History

/

# shadow\_account

/

Copy path

Top

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ### parent directory<br> [..](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src) |
| [templates](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account/templates "templates") | [templates](https://github.com/HKUDS/Vibe-Trading/tree/main/agent/src/shadow_account/templates "templates") | [feat(shadow-account): carry price-condition bounds into extracted rul…](https://github.com/HKUDS/Vibe-Trading/commit/18b6247a602d79eccca099c8f0c94c771dfa1a9e "feat(shadow-account): carry price-condition bounds into extracted rules (#314)  Promoted entry_rsi14 / prior_5d_return bounds now flow into extracted ShadowRules and the generated SignalEngine for real conditional entry. Follows #302. Thanks @Robin1987China.") | 3 weeks agoJun 26, 2026 |
| [\_\_init\_\_.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/__init__.py "__init__.py") | [\_\_init\_\_.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/__init__.py "__init__.py") | [feat: shadow account — extract/backtest/render/scan + HTML report + s…](https://github.com/HKUDS/Vibe-Trading/commit/3b29677a6161af3fe2c02b4c3258660fb3054712 "feat: shadow account — extract/backtest/render/scan + HTML report + skill  - 4 new tools: extract_shadow_strategy, run_shadow_backtest,   render_shadow_report, scan_shadow_signals - src/shadow_account/ package: clustering-based rule extractor, cached   cross-market backtester, 8-section HTML/PDF reporter with attribution   waterfall, signal scanner, Jinja2-rendered signal engine - src/skills/shadow-account/ ships rules + methodology + attribution semantics - API endpoint GET /shadow-reports/<id>?format=html|pdf - Context routing: Shadow block mandates load_skill first - Reused trade_journal_tool.pair_trades_fifo (promoted from private) - 28 new unit tests - Reporter fix: _chart_attribution_waterfall had 6 undefined refs   (_ACCENT/_POS/_NEG/_BG/_GRID/_style_axes) — inlined hex + native mpl - Deps: jinja2, matplotlib, weasyprint (optional; HTML fallback when GTK missing)") | 3 months agoApr 18, 2026 |
| [backtester.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/backtester.py "backtester.py") | [backtester.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/backtester.py "backtester.py") | [chore: cleanup pass — 3 latent bug fixes + 913 LOC net delete](https://github.com/HKUDS/Vibe-Trading/commit/e99444dee725370fbd16e816360e97682c61cef2 "chore: cleanup pass — 3 latent bug fixes + 913 LOC net delete  Bug fixes - CompositeEngine no longer misroutes bare Chinese-futures codes like   RB2410 to GlobalFuturesEngine. _is_china_futures moved into a shared   _market_hooks module with a case-normalized product table and a   non-CN exchange guard. 9 new regression cases (RB2410 / rb2410 /   RB2410.SHFE / CL.NYMEX / M2412.CBOT / CF2412.ICE / AU2412.COMEX /   FG2412.EUREX / bare CN-collision still routes Chinese). - Session FTS5 indexes now persist timestamps so cross-session search   can sort by date. Same path also fixes a re-upsert that was   wall-clocking every session's started_at on title-rename. - Vite dev-mode proxy gained the missing /alpha entry; AlphaZoo page   resolves on npm run dev.  Cleanup - Deleted swarm/api_models.py + swarm/mailbox.py + SwarmDashboard.tsx   (dead modules / orphaned UI after swarm-via-agent flow). - Deleted SessionService.resume_attempt + get_attempts + get_attempt   + SessionStore.list_attempts + Attempt.mark_waiting_user chain   (half-baked human-in-the-loop from initial commit). - Deleted ChatLLM.achat (async sibling never called) and   _extract_balanced_json (only-tested helper). - Deleted american_exercise_value in options_portfolio.py   (driver inlines bs_price logic). - Deleted _compute_ic_series_reference in factor_analysis_core.py   (kept-as-reference, no callers). - Collapsed MEMORY_TYPES duplication between cli.py and   memory.persistent; restored set-equality invariant assert. - Deleted runSwarm (~197 LOC), swarmDash state, swarmCancelRef   write-only ref (orphaned by new agent-driven swarm flow). - Dropped 76 unused 'vw = vwap(...)' boilerplate lines across   gtja191 alphas + their now-unused vwap imports. - Cleared 11 F401 unused-import sites in tools/, agent/, providers/.  Test infrastructure - test_e2e_harness_v2.py (real-LLM e2e) gated behind   VIBE_TRADING_RUN_LIVE_E2E so CI no longer flips shape based on   env-key presence. CI workflow now has explicit --ignore. - test_auto_compact_with_long_history: monkeypatch TOKEN_THRESHOLD so   the test deterministically triggers compact instead of relying on   unrelated LLM behaviour. - test_compact_tool_explicit: assertion corrected — compact tool is   special-cased in loop._process_tool_calls and does NOT emit   tool_call events. Assert on the 'compact' event instead. - TestSwarmE2E: per-test @pytest.mark.timeout overrides matching the   internal 300s poll deadlines; cancel test now polls for terminal   state instead of fixed sleep(3).  Tooling - ruff per-file-ignores for factors/zoo/** (3783 → 0 F401 noise);   F841 stays active in zoo to catch real formula bugs. - frontend tsconfig: noUnusedLocals + noUnusedParameters as   regression guards. - highlight.js hoisted to direct dependency (was transitive via   rehype-highlight). - Vite proxy: dropped unused /run, /skills, /health, /api, /system;   added /alpha.  Annotations - direction parameter renamed to _direction in 6 calc_commission   signatures (reserved for future borrow-fee asymmetry). - _MARGIN_PER_CONTRACT in global_futures.py annotated as reference   data. - Backtest engines' _calc_pct_change variants cross-reference each   other in docstrings.  Docs - 2026-05-18 news entry added to README.md / README_zh.md /   README_ja.md / README_ko.md / README_ar.md; 2026-05-15 entry   rolled into the Earlier news <details>. - Contributors heading: v0.1.7 cycle → v0.1.8 cycle in all 5   READMEs.  126 files changed, +363 / -1276.") | 2 months agoMay 18, 2026 |
| [codegen.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/codegen.py "codegen.py") | [codegen.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/codegen.py "codegen.py") | [refactor(shadow-account): centralize price feature contract](https://github.com/HKUDS/Vibe-Trading/commit/2acc3b846c72b0959ac848dc47c62158f3c8d773 "refactor(shadow-account): centralize price feature contract  Centralize Shadow Account price feature names in models.PRICE_FEATURES so extractor and codegen cannot drift, and keep price-context bounds at four decimals to avoid losing small return thresholds.  Includes regression coverage for feature-name sharing and prior_5d_return precision.  Thanks @Robin1987China.") | 3 weeks agoJun 27, 2026 |
| [extractor.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/extractor.py "extractor.py") | [extractor.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/extractor.py "extractor.py") | [refactor(shadow-account): centralize price feature contract](https://github.com/HKUDS/Vibe-Trading/commit/2acc3b846c72b0959ac848dc47c62158f3c8d773 "refactor(shadow-account): centralize price feature contract  Centralize Shadow Account price feature names in models.PRICE_FEATURES so extractor and codegen cannot drift, and keep price-context bounds at four decimals to avoid losing small return thresholds.  Includes regression coverage for feature-name sharing and prior_5d_return precision.  Thanks @Robin1987China.") | 3 weeks agoJun 27, 2026 |
| [fonts.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/fonts.py "fonts.py") | [fonts.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/fonts.py "fonts.py") | [feat: shadow account — extract/backtest/render/scan + HTML report + s…](https://github.com/HKUDS/Vibe-Trading/commit/3b29677a6161af3fe2c02b4c3258660fb3054712 "feat: shadow account — extract/backtest/render/scan + HTML report + skill  - 4 new tools: extract_shadow_strategy, run_shadow_backtest,   render_shadow_report, scan_shadow_signals - src/shadow_account/ package: clustering-based rule extractor, cached   cross-market backtester, 8-section HTML/PDF reporter with attribution   waterfall, signal scanner, Jinja2-rendered signal engine - src/skills/shadow-account/ ships rules + methodology + attribution semantics - API endpoint GET /shadow-reports/<id>?format=html|pdf - Context routing: Shadow block mandates load_skill first - Reused trade_journal_tool.pair_trades_fifo (promoted from private) - 28 new unit tests - Reporter fix: _chart_attribution_waterfall had 6 undefined refs   (_ACCENT/_POS/_NEG/_BG/_GRID/_style_axes) — inlined hex + native mpl - Deps: jinja2, matplotlib, weasyprint (optional; HTML fallback when GTK missing)") | 3 months agoApr 18, 2026 |
| [models.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/models.py "models.py") | [models.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/models.py "models.py") | [refactor(shadow-account): centralize price feature contract](https://github.com/HKUDS/Vibe-Trading/commit/2acc3b846c72b0959ac848dc47c62158f3c8d773 "refactor(shadow-account): centralize price feature contract  Centralize Shadow Account price feature names in models.PRICE_FEATURES so extractor and codegen cannot drift, and keep price-context bounds at four decimals to avoid losing small return thresholds.  Includes regression coverage for feature-name sharing and prior_5d_return precision.  Thanks @Robin1987China.") | 3 weeks agoJun 27, 2026 |
| [reporter.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/reporter.py "reporter.py") | [reporter.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/reporter.py "reporter.py") | [feat: shadow account — extract/backtest/render/scan + HTML report + s…](https://github.com/HKUDS/Vibe-Trading/commit/3b29677a6161af3fe2c02b4c3258660fb3054712 "feat: shadow account — extract/backtest/render/scan + HTML report + skill  - 4 new tools: extract_shadow_strategy, run_shadow_backtest,   render_shadow_report, scan_shadow_signals - src/shadow_account/ package: clustering-based rule extractor, cached   cross-market backtester, 8-section HTML/PDF reporter with attribution   waterfall, signal scanner, Jinja2-rendered signal engine - src/skills/shadow-account/ ships rules + methodology + attribution semantics - API endpoint GET /shadow-reports/<id>?format=html|pdf - Context routing: Shadow block mandates load_skill first - Reused trade_journal_tool.pair_trades_fifo (promoted from private) - 28 new unit tests - Reporter fix: _chart_attribution_waterfall had 6 undefined refs   (_ACCENT/_POS/_NEG/_BG/_GRID/_style_axes) — inlined hex + native mpl - Deps: jinja2, matplotlib, weasyprint (optional; HTML fallback when GTK missing)") | 3 months agoApr 18, 2026 |
| [scanner.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/scanner.py "scanner.py") | [scanner.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/scanner.py "scanner.py") | [feat(shadow-account): carry price-condition bounds into extracted rul…](https://github.com/HKUDS/Vibe-Trading/commit/18b6247a602d79eccca099c8f0c94c771dfa1a9e "feat(shadow-account): carry price-condition bounds into extracted rules (#314)  Promoted entry_rsi14 / prior_5d_return bounds now flow into extracted ShadowRules and the generated SignalEngine for real conditional entry. Follows #302. Thanks @Robin1987China.") | 3 weeks agoJun 26, 2026 |
| [storage.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/storage.py "storage.py") | [storage.py](https://github.com/HKUDS/Vibe-Trading/blob/main/agent/src/shadow_account/storage.py "storage.py") | [feat: shadow account — extract/backtest/render/scan + HTML report + s…](https://github.com/HKUDS/Vibe-Trading/commit/3b29677a6161af3fe2c02b4c3258660fb3054712 "feat: shadow account — extract/backtest/render/scan + HTML report + skill  - 4 new tools: extract_shadow_strategy, run_shadow_backtest,   render_shadow_report, scan_shadow_signals - src/shadow_account/ package: clustering-based rule extractor, cached   cross-market backtester, 8-section HTML/PDF reporter with attribution   waterfall, signal scanner, Jinja2-rendered signal engine - src/skills/shadow-account/ ships rules + methodology + attribution semantics - API endpoint GET /shadow-reports/<id>?format=html|pdf - Context routing: Shadow block mandates load_skill first - Reused trade_journal_tool.pair_trades_fifo (promoted from private) - 28 new unit tests - Reporter fix: _chart_attribution_waterfall had 6 undefined refs   (_ACCENT/_POS/_NEG/_BG/_GRID/_style_axes) — inlined hex + native mpl - Deps: jinja2, matplotlib, weasyprint (optional; HTML fallback when GTK missing)") | 3 months agoApr 18, 2026 |
| View all files |

You can’t perform that action at this time.