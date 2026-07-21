[Skip to content](https://github.com/NousResearch/hermes-agent/pull/46472#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/pull/46472) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/pull/46472) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/pull/46472) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

[NousResearch](https://github.com/NousResearch)/ **[hermes-agent](https://github.com/NousResearch/hermes-agent)** Public

- [Notifications](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent) You must be signed in to change notification settings
- [Fork\\
39.7k](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent)
- [Star\\
214k](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent)


## Conversation

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=80&v=4)](https://github.com/wait4xx)

### ![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=48&v=4)**[wait4xx](https://github.com/wait4xx)**     commented   [last monthJun 15, 2026](https://github.com/NousResearch/hermes-agent/pull/46472\#issue-4662164602)


Copy link


Copy Markdown

Fixes [#46470](https://github.com/NousResearch/hermes-agent/issues/46470)

Closes [#25452](https://github.com/NousResearch/hermes-agent/issues/25452)

Closes [#26841](https://github.com/NousResearch/hermes-agent/issues/26841)

Closes [#29471](https://github.com/NousResearch/hermes-agent/issues/29471)

Supersedes [#25453](https://github.com/NousResearch/hermes-agent/pull/25453)

## Summary

Render all Feishu outbound markdown via Card 2.0 interactive cards (`tag:"markdown"`, full CommonMark), replacing the stripped post-type `tag:"md"` renderer. One change fixes table rendering, code blocks, lists, headings, blockquotes — and the streaming `msg_type` drift.

## Why this approach (validated with real test cards)

Sent 5 test cards to a live Feishu client:

| Capability | `tag:"markdown"` (Card 2.0) | `tag:"table"` (native) |
| --- | --- | --- |
| Column alignment (GFM `:---:`) | ✅ renders | ❌ API rejects `align` (ErrCode 200621) |
| Full CommonMark (code/lists/headings) | ✅ | — |
| Long-table pagination | ✅ client auto-paginates | ✅ `page_size` |
| Mixed-format coherence | ✅ single render flow | ⚠️ elements interleave |
| Implementation LoC | ~5 | ~150 |

→ Native table component dropped (YAGNI/DRY): it can't do alignment and the markdown element already covers pagination + full CommonMark.

## Changes

- `_build_markdown_card_payload`: single `tag:"markdown"` element (JSON 2.0)
- `_build_outbound_payload`: route ALL content → `interactive` (flag on), so `send()` and `edit_message()` always agree on `msg_type` — eliminates the streaming drift ([\[Feishu\] First chunk of long messages sent as msg\_type=text instead of post, breaking Markdown rendering #26841](https://github.com/NousResearch/hermes-agent/issues/26841) / [bug(feishu): first chunk of long messages sent as msg\_type=text, breaking Markdown rendering #29471](https://github.com/NousResearch/hermes-agent/issues/29471))
- Feature flag `feishu_interactive_cards` (default `true`) → legacy `text`/`post` on `false`
- Degrade interactive → text on send/edit exception; 100KB capacity guard
- 8 new tests + legacy post/fallback tests moved to flag-off path

## Test plan

- [x] `pytest tests/gateway/test_feishu.py` — **213 passed**, 0 regressions
- [x]  Real test cards verified: tables / code blocks / lists / headings render; GFM alignment works; long tables paginate
- [ ]  CI green

## Related work (comparison)

| PR | Approach | vs this PR |
| --- | --- | --- |
| **[#25453](https://github.com/NousResearch/hermes-agent/pull/25453)** (mine, superseded) | native table, stale base | rebuilt on current main + streaming fix + tests |
| [#45036](https://github.com/NousResearch/hermes-agent/pull/45036) / [#45907](https://github.com/NousResearch/hermes-agent/pull/45907) | Card 2.0 `tag:"markdown"` | same core; **this adds streaming msg\_type fix + flag + unit tests** |
| [#40445](https://github.com/NousResearch/hermes-agent/pull/40445) | native table, 3-layer | simpler here (markdown element, no parsing) |
| [#45583](https://github.com/NousResearch/hermes-agent/pull/45583) | route tables to `post` | post `tag:"md"` is a stripped renderer; Card 2.0 is full CommonMark |
| [#38867](https://github.com/NousResearch/hermes-agent/pull/38867) | always `post` | same — post is stripped |

## What's different (why a Nth PR on this)

1. **Only PR fixing the streaming `msg_type` drift** ([\[Feishu\] First chunk of long messages sent as msg\_type=text instead of post, breaking Markdown rendering #26841](https://github.com/NousResearch/hermes-agent/issues/26841) / [bug(feishu): first chunk of long messages sent as msg\_type=text, breaking Markdown rendering #29471](https://github.com/NousResearch/hermes-agent/issues/29471)) — none of the 9 sibling PRs address it
2. Full CommonMark (fixes code-block truncation [\[Feishu\] Code blocks cannot be expanded — only first ~2 lines visible #19035](https://github.com/NousResearch/hermes-agent/issues/19035))
3. Feature flag for safe rollback
4. 8 unit tests (siblings are mostly manual-only)

Co-authored-by: GLM 5.2

Sorry, something went wrong.


### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

All reactions

This was referenced last monthJun 15, 2026

[fix(feishu): render markdown tables as interactive card table components\\
#25453](https://github.com/NousResearch/hermes-agent/pull/25453)

Open

[Feishu channel displays markdown tables as raw source code instead of rendering them\\
#25452](https://github.com/NousResearch/hermes-agent/issues/25452)

Open

[![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?s=40&u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4)](https://github.com/alt-glitch)[alt-glitch](https://github.com/alt-glitch)

added

[type/bug](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Atype%2Fbug) Something isn't working [P3](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3AP3) Low — cosmetic, nice to have [comp/gateway](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Acomp%2Fgateway) Gateway runner, session dispatch, delivery [platform/feishu](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Aplatform%2Ffeishu) Feishu / Lark adapter [duplicate](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Aduplicate) This issue or pull request already exists

labels

[last monthJun 15, 2026](https://github.com/NousResearch/hermes-agent/pull/46472#event-26740864545)

[![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?s=80&u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4)](https://github.com/alt-glitch)

### **[alt-glitch](https://github.com/alt-glitch)**     commented   [last monthJun 15, 2026](https://github.com/NousResearch/hermes-agent/pull/46472\#issuecomment-4704807773)


Copy link


Copy Markdown

Collaborator

|     |
| --- |
| Duplicate of [#12114](https://github.com/NousResearch/hermes-agent/pull/12114) — enters the saturated Feishu Card 2.0 (tag:"markdown") rendering cluster (canonical [#12114](https://github.com/NousResearch/hermes-agent/pull/12114), consolidation issue [#27469](https://github.com/NousResearch/hermes-agent/issues/27469), 70+ competing PRs). This PR is a clean, well-tested implementation but the same core approach. Supersedes your own [#25453](https://github.com/NousResearch/hermes-agent/pull/25453). |

All reactions

Sorry, something went wrong.


### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

[![tonydwb](https://avatars.githubusercontent.com/u/268165325?s=60&v=4)](https://github.com/tonydwb)

**[tonydwb](https://github.com/tonydwb)**

approved these changes

[last monthJun 15, 2026](https://github.com/NousResearch/hermes-agent/pull/46472#pullrequestreview-4494646850)

[View reviewed changes](https://github.com/NousResearch/hermes-agent/pull/46472/files)

### ![@tonydwb](https://avatars.githubusercontent.com/u/268165325?s=48&v=4)**[tonydwb](https://github.com/tonydwb)**     left a comment


Copy link


Copy Markdown

There was a problem hiding this comment.

### Choose a reason for hiding this comment

The reason will be displayed to describe this comment to others. [Learn more](https://docs.github.com/articles/managing-disruptive-comments/#hiding-a-comment).


Choose a reason
SpamAbuseOff TopicOutdatedDuplicateResolvedLow QualityHide comment

## Code Review Summary

**Verdict: Approved**

Good improvement to Feishu markdown rendering: adds Card 2.0 interactive card support with a 100KB size limit for graceful degradation to plain text. The Card 2.0 tag supports full CommonMark including GFM tables.

### Looks Good

- Clean, well-scoped fix
- Good size-limit guard to prevent oversized payloads
- No security or stability concerns

* * *

_Reviewed by Hermes Agent_

Sorry, something went wrong.


### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

All reactions

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=80&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)

### **[wait4xx](https://github.com/wait4xx)**     commented   [last monthJun 15, 2026](https://github.com/NousResearch/hermes-agent/pull/46472\#issuecomment-4704835410)


Copy link


Copy Markdown

Author

|     |
| --- |
| > Duplicate of [#12114](https://github.com/NousResearch/hermes-agent/pull/12114) — enters the saturated Feishu Card 2.0 (tag:"markdown") rendering cluster (canonical [#12114](https://github.com/NousResearch/hermes-agent/pull/12114), consolidation issue [#27469](https://github.com/NousResearch/hermes-agent/issues/27469), 70+ competing PRs). This PR is a clean, well-tested implementation but the same core approach. Supersedes your own [#25453](https://github.com/NousResearch/hermes-agent/pull/25453).<br>Yes, I have consolidated all issues related to Feishu message rendering. Building upon the issue I previously opened, I have made further refinements and optimizations. I tested two table rendering approaches and ultimately retained the more concise solution. The Feishu message rendering issue remains unresolved on the latest `main` branch, and I hope it can be fixed as soon as possible. |

mxazz123 reacted with thumbs up emoji

All reactions

- ![+1](https://github.githubassets.com/assets/1f44d-41cb66fe1e22.png)1 reaction

Sorry, something went wrong.


### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

[![@teknium1](https://avatars.githubusercontent.com/u/127238744?s=40&v=4)](https://github.com/teknium1)[teknium1](https://github.com/teknium1)

mentioned this pull request
[last monthJun 15, 2026](https://github.com/NousResearch/hermes-agent/pull/46472#ref-pullrequest-4479300276)

[fix(feishu): render markdown tables via cards\\
#28837](https://github.com/NousResearch/hermes-agent/pull/28837)

Open

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=80&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)

### **[wait4xx](https://github.com/wait4xx)**     commented   [last monthJun 17, 2026](https://github.com/NousResearch/hermes-agent/pull/46472\#issuecomment-4732016493)


Copy link


Copy Markdown

Author

|     |
| --- |
| **Update — additional fixes layered on this branch** (`fix/feishu-markdown-interactive-cards`):<br>1. **Mermaid → image**: Feishu does not render mermaid natively (the official card docs list it under "unsupported"). ``````mermaid``` blocks now render to a transparent PNG via the local `mmdc` CLI (Chromium/Chrome auto-detected via `PUPPETEER_EXECUTABLE_PATH`), with a tiered fallback — external `mermaid.ink` for browser-less / Docker hosts, then a fenced code block — so diagrams render on every deployment. Rendering runs off the event loop (`asyncio.to_thread`).<br>2. **Mermaid extraction bug fix**: the closing-fence regex lacked `re.MULTILINE`, so `_extract_mermaid_blocks` never matched the closing fence → every mermaid block silently fell back to a code block. Fixed (`_MERMAID_CLOSE_RE`).<br>3. **Table limit correction**: each card is a single markdown element, which Feishu limits to **4** GFM tables (official card docs). The code was splitting at 5 — the limit for the native `tag:"table"` component, which this path does not use. Now respects the correct 4-per-element limit.<br>Verified by sending real cards to Feishu (transparent 2× mermaid PNG, multi-table splitting).<br>Co-authored-by: GLM 5.2 |

All reactions

Sorry, something went wrong.


### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)[wait4xx](https://github.com/wait4xx) [force-pushed](https://github.com/NousResearch/hermes-agent/compare/fbc266ef10f71038d2dbffb080e0f9615fd1b4e4..0f840c0bb7b5ee7810f45b2cbc985e6c194e5ef2)
the
fix/feishu-markdown-interactive-cards
branch
from
[`fbc266e`](https://github.com/NousResearch/hermes-agent/commit/fbc266ef10f71038d2dbffb080e0f9615fd1b4e4) to
[`0f840c0`](https://github.com/NousResearch/hermes-agent/commit/0f840c0bb7b5ee7810f45b2cbc985e6c194e5ef2) [Compare](https://github.com/NousResearch/hermes-agent/compare/fbc266ef10f71038d2dbffb080e0f9615fd1b4e4..0f840c0bb7b5ee7810f45b2cbc985e6c194e5ef2) [last monthJune 17, 2026 15:11](https://github.com/NousResearch/hermes-agent/pull/46472#event-26867875006)

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)[wait4xx](https://github.com/wait4xx)

mentioned this pull request
[last monthJun 17, 2026](https://github.com/NousResearch/hermes-agent/pull/46472#ref-issue-4662162194)

[\[feishu\] Render all outbound markdown via Card 2.0 interactive cards (unified fix)\\
#46470](https://github.com/NousResearch/hermes-agent/issues/46470)

Open

[wait4xx](https://github.com/wait4xx)


added 8 commits
[3 weeks agoJune 21, 2026 11:20](https://github.com/NousResearch/hermes-agent/pull/46472#commits-pushed-11faf04)

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          feat(feishu): render all outbound markdown via Card 2.0 interactive c…
` …

`
          11faf04
`

```
…ards

Replace the post-type tag:md renderer (stripped: links + partial bold only)
with Card 2.0 tag:markdown (full CommonMark) so tables, code blocks, lists,
headings, and blockquotes all render natively.

- _build_markdown_card_payload: single tag:markdown element (JSON 2.0)
- _build_outbound_payload: route ALL content to interactive card (flag on,
  default) so send() and edit_message() always agree on msg_type — fixes
  the streaming msg_type drift (NousResearch#26841 / NousResearch#29471)
- Feature flag feishu_interactive_cards (default true) restores legacy
  text/post behavior for rollback
- Degrade interactive->text on send/edit exception (transient failures);
  capacity guard at 100KB
- Tests: 8 new (flag/payload/routing/degrade/streaming-consistency) + legacy
  post/fallback tests moved to flag-off path

Native table component was dropped: real test cards showed it does NOT
support column alignment (API rejects `align`) while the markdown element
supports GFM alignment + full CommonMark + auto-pagination — saving ~150
lines of table-parsing code (YAGNI/DRY).

Fixes NousResearch#25452
Supersedes NousResearch#25453

Co-authored-by: GLM 5.2
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          fix(feishu): correct card limits and add table count guard
` …

`
          df769a1
`

```
- Lower _MAX_CARD_JSON_BYTES from 100KB to 30KB (Feishu hard limit)
- Add _MAX_TABLES_PER_CARD=5 and _MAX_TABLES_PER_ELEMENT=4 constants
- Add _MERMAID_BLOCK_RE regex for mermaid code block detection
- Add _count_gfm_tables() helper to count GFM tables in content
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          feat(feishu): split oversized cards respecting 30KB and table limits
` …

`
          f4a32d0
`

```
- Add _MarkdownBlock dataclass and _split_markdown_blocks() to parse
  markdown into atomic units (table, code, mermaid, paragraph)
- Add _split_oversized_table() to split tables by rows with shared headers
- Add _split_oversized_paragraph() to split at paragraph/line/sentence boundaries
- Add _pack_blocks_into_cards() for greedy bin-packing with 30KB + 5-table budget
- Add _build_outbound_payloads() (plural) returning list of card payloads
- Add _inject_card_header() for sequential headers (e.g. Hermes 1/3)
- Modify send() to iterate over multi-card payloads
- edit_message() and streaming path unchanged (single card)
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          feat(feishu): render mermaid code blocks as transparent PNG images in…
` …

`
          6b4919f
`

```
… cards

- Add _extract_mermaid_blocks() to find all mermaid code blocks
- Add _render_mermaid_to_png(): base64 → mermaid.ink ?type=png → Pillow
  de-white-background (R>240,G>240,B>240 → alpha=0)
- Add _upload_mermaid_images() async method: render → upload to Feishu
  → replace with ![mermaid](image_key). Failures leave original block intact.
- Integrate into _build_outbound_payloads() before card splitting
- Zero new dependencies: urllib (stdlib) + Pillow (already installed)
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          fix(prompt): add code block language identifier instruction for Feishu
` …

`
          51aabf9
`

```
Instruct the LLM to always specify the language tag in fenced code blocks
so that Feishu Card 2.0 can apply syntax highlighting.
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          feat(feishu): render mermaid locally + correct card table limit
` …

`
          6b367e6
`

````
Mermaid rendering (```mermaid blocks → image):
- Render to transparent PNG via the local mmdc CLI (Chromium/Chrome
  auto-detected via PUPPETEER_EXECUTABLE_PATH); native transparent
  background (themeVariables.background + -b transparent), no Pillow.
- Tiered for robustness: local mmdc → external mermaid.ink (for
  browser-less / Docker hosts) → fenced code block. Configurable via
  feishu_mermaid_external_fallback (default on).
- Non-blocking: render runs in asyncio.to_thread.
- Fix: mermaid block extraction used a close-fence regex without
  re.MULTILINE, so the closing fence was never matched and blocks were
  always empty (always fell back to code block). Added _MERMAID_CLOSE_RE.

Card table limit:
- Each card is a single markdown element, which Feishu limits to 4 GFM
  tables (official card docs). The code was using 5 — the limit for the
  native tag:"table" component, which this path does not use. Splitting
  now respects the correct 4-table-per-element limit.

Co-authored-by: GLM 5.2
````

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          test(feishu): migrate imports to plugins.platforms.feishu.adapter
` …

`
          9f859fb
`

```
After rebasing onto main (which relocated gateway/platforms/feishu.py to plugins/platforms/feishu/adapter.py), 14 test imports still used the old module path and raised ModuleNotFoundError.

Co-authored-by: GLM 5.2
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&v=4)](https://github.com/wait4xx)

`
          feat(feishu): add bash language tag to tool-progress code blocks
` …

`
          e4784ac
`

```
Card 2.0's markdown element honours fenced-code language tags, so terminal command previews rendered by gateway/run.py now emit a bash-tagged fence for syntax highlighting on Feishu.

- BasePlatformAdapter.code_block_language_tag defaults to empty string (safe for platforms like Slack whose mrkdwn would render a tag as literal text).

- FeishuAdapter overrides it to 'bash'.

- gateway/run.py reads the attribute when building tool-progress code blocks; an empty tag preserves the previous bare-fence behaviour for all other platforms.

Co-authored-by: GLM 5.2
```

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=40&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)[wait4xx](https://github.com/wait4xx) [force-pushed](https://github.com/NousResearch/hermes-agent/compare/0f840c0bb7b5ee7810f45b2cbc985e6c194e5ef2..e4784ac833842b168b9770c971f5ea51b1fbde00)
the
fix/feishu-markdown-interactive-cards
branch
from
[`0f840c0`](https://github.com/NousResearch/hermes-agent/commit/0f840c0bb7b5ee7810f45b2cbc985e6c194e5ef2) to
[`e4784ac`](https://github.com/NousResearch/hermes-agent/commit/e4784ac833842b168b9770c971f5ea51b1fbde00) [Compare](https://github.com/NousResearch/hermes-agent/compare/0f840c0bb7b5ee7810f45b2cbc985e6c194e5ef2..e4784ac833842b168b9770c971f5ea51b1fbde00) [3 weeks agoJune 21, 2026 03:54](https://github.com/NousResearch/hermes-agent/pull/46472#event-27003106101)

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=80&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)

### **[wait4xx](https://github.com/wait4xx)**     commented   [3 weeks agoJun 21, 2026](https://github.com/NousResearch/hermes-agent/pull/46472\#issuecomment-4761126140)


Copy link


Copy Markdown

Author

|     |
| --- |
| **Update — rebased onto latest `main` \+ code-block language tags** (`fix/feishu-markdown-interactive-cards`):<br>1. **Rebased onto current `main`** — the branch was 74 commits behind. Since then `main` relocated `gateway/platforms/feishu.py` to `plugins/platforms/feishu/adapter.py` (the platforms-to-plugins refactor); the rebase applied cleanly with no conflicts, so this PR is now **MERGEABLE** against `main` (previously it would have hit the module-relocation conflict on merge).<br>2. **Fixed stale test imports** — 14 test imports still referenced the old `gateway.platforms.feishu` path and raised `ModuleNotFoundError` after the migration; all updated to `plugins.platforms.feishu.adapter`.<br>3. **Code-block language tags** — added a `code_block_language_tag` adapter attribute (default empty string, safe for platforms like Slack whose mrkdwn would render a tag as literal text). `FeishuAdapter` sets it to `bash`, so terminal-command previews in tool-progress messages now use a bash-tagged code fence — Card 2.0's markdown element honours the language tag for syntax highlighting. `gateway/run.py` reads the attribute when building tool-progress code blocks; an empty tag preserves the previous bare-fence behaviour for every other platform.<br>All 218 feishu tests pass. Ready for re-review after the force-push.<br>Co-authored-by: GLM 5.2 |

All reactions

Sorry, something went wrong.


### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/pull/46472).

[![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?s=40&u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4)](https://github.com/alt-glitch)[alt-glitch](https://github.com/alt-glitch)

mentioned this pull request
[3 weeks agoJun 22, 2026](https://github.com/NousResearch/hermes-agent/pull/46472#ref-pullrequest-4713841422)

[fix(feishu): route markdown tables through post+md instead of forcing text\\
#50640](https://github.com/NousResearch/hermes-agent/pull/50640)

Closed

13 tasks

This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below. To review, open the file in an editor that reveals hidden Unicode characters.
[Learn more about bidirectional Unicode characters](https://github.co/hiddenchars)

[Show hidden characters](https://github.com/NousResearch/hermes-agent/pull/46472)

[Sign up for free](https://github.com/join?source=comment-repo) **to join this conversation on GitHub**.
Already have an account?
[Sign in to comment](https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2FNousResearch%2Fhermes-agent%2Fpull%2F46472)

### Reviewers

1 more reviewer


[![@tonydwb](https://avatars.githubusercontent.com/u/268165325?s=40&v=4)](https://github.com/tonydwb)[tonydwb](https://github.com/tonydwb)tonydwb approved these changes

Reviewers whose approvals may not affect merge requirements

### Assignees

No one assigned

### Labels

[comp/gateway](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Acomp%2Fgateway) Gateway runner, session dispatch, delivery [duplicate](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Aduplicate) This issue or pull request already exists [P3](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3AP3) Low — cosmetic, nice to have [platform/feishu](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Aplatform%2Ffeishu) Feishu / Lark adapter [type/bug](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3Atype%2Fbug) Something isn't working

### Projects

None yet

### Milestone

No milestone

### Development

Successfully merging this pull request may close these issues.

[\[feishu\] Render all outbound markdown via Card 2.0 interactive cards (unified fix)](https://github.com/NousResearch/hermes-agent/issues/46470)[bug(feishu): first chunk of long messages sent as msg\_type=text, breaking Markdown rendering](https://github.com/NousResearch/hermes-agent/issues/29471)[\[Feishu\] First chunk of long messages sent as msg\_type=text instead of post, breaking Markdown rendering](https://github.com/NousResearch/hermes-agent/issues/26841)[Feishu channel displays markdown tables as raw source code instead of rendering them](https://github.com/NousResearch/hermes-agent/issues/25452)

### 3 participants

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=52&v=4)](https://github.com/wait4xx)[![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?s=52&v=4)](https://github.com/alt-glitch)[![@tonydwb](https://avatars.githubusercontent.com/u/268165325?s=52&v=4)](https://github.com/tonydwb)

Add this suggestion to a batch that can be applied as a single commit.This suggestion is invalid because no changes were made to the code.Suggestions cannot be applied while the pull request is closed.Suggestions cannot be applied while viewing a subset of changes.Only one suggestion per line can be applied in a batch.Add this suggestion to a batch that can be applied as a single commit.Applying suggestions on deleted lines is not supported.You must change the existing code in this line in order to create a valid suggestion.Outdated suggestions cannot be applied.This suggestion has been applied or marked resolved.Suggestions cannot be applied from pending reviews.Suggestions cannot be applied on multi-line comments.Suggestions cannot be applied while the pull request is queued to merge.Suggestion cannot be applied right now. Please check back later.

You can’t perform that action at this time.