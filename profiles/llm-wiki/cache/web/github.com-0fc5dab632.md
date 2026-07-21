[Skip to content](https://github.com/NousResearch/hermes-agent/issues/46470#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/issues/46470) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/issues/46470) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/issues/46470) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/issues/46470).

[NousResearch](https://github.com/NousResearch)/ **[hermes-agent](https://github.com/NousResearch/hermes-agent)** Public

- [Notifications](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent) You must be signed in to change notification settings
- [Fork\\
39.7k](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent)
- [Star\\
214k](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent)


# \[feishu\] Render all outbound markdown via Card 2.0 interactive cards (unified fix)\#46470

[New issue](https://github.com/login?return_to=https://github.com/NousResearch/hermes-agent/issues/46470)

Copy link

[New issue](https://github.com/login?return_to=https://github.com/NousResearch/hermes-agent/issues/46470)

Copy link

Open

[#46472](https://github.com/NousResearch/hermes-agent/pull/46472)

Open

[\[feishu\] Render all outbound markdown via Card 2.0 interactive cards (unified fix)](https://github.com/NousResearch/hermes-agent/issues/46470#top)#46470

[#46472](https://github.com/NousResearch/hermes-agent/pull/46472)

Copy link

Labels

[P2Medium — degraded but workaround exists](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22P2%22) Medium — degraded but workaround exists [comp/gatewayGateway runner, session dispatch, delivery](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22comp%2Fgateway%22) Gateway runner, session dispatch, delivery [platform/feishuFeishu / Lark adapter](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22platform%2Ffeishu%22) Feishu / Lark adapter [type/featureNew feature or request](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22type%2Ffeature%22) New feature or request

## Description

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4&size=48)](https://github.com/wait4xx)

[wait4xx](https://github.com/wait4xx)

opened [1mo agoon Jun 15, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#issue-4662162194)

Issue body actions

## Problem

Feishu (Lark) outbound messages have multiple rendering issues, all sharing one root cause:

- Markdown tables display as raw `| a | b |` source ([Feishu channel displays markdown tables as raw source code instead of rendering them #25452](https://github.com/NousResearch/hermes-agent/issues/25452), [\[Feishu\] Markdown tables not rendering in Feishu messages #9549](https://github.com/NousResearch/hermes-agent/issues/9549), [Feishu gateway: Markdown tables render as broken plain text #29245](https://github.com/NousResearch/hermes-agent/issues/29245), …)
- Code blocks truncated to ~2 lines ([\[Feishu\] Code blocks cannot be expanded — only first ~2 lines visible #19035](https://github.com/NousResearch/hermes-agent/issues/19035))
- Lists / headings / blockquotes / bold render poorly
- Streaming replies break markdown: first chunk sent as `msg_type=text`, later edits switch type ([\[Feishu\] First chunk of long messages sent as msg\_type=text instead of post, breaking Markdown rendering #26841](https://github.com/NousResearch/hermes-agent/issues/26841), [bug(feishu): first chunk of long messages sent as msg\_type=text, breaking Markdown rendering #29471](https://github.com/NousResearch/hermes-agent/issues/29471))

## Root cause

Feishu has **two** markdown renderers and Hermes uses the stripped one:

| Element | Container | Capability |
| --- | --- | --- |
| `tag:"md"` | `post` message | stripped: links + partial bold only |
| `tag:"markdown"` | Card 2.0 body | full CommonMark (tables, code, lists, headings, …) |

On top of that, `_build_outbound_payload()` picks the msg\_type per chunk independently, so during streaming the first chunk (`text`) and the final edit (`post`/`interactive`) disagree — Feishu rejects the type change.

## Proposal

Route **all** outbound content through Card 2.0 (`tag:"markdown"`, `msg_type=interactive`). One change fixes tables, code blocks, lists, headings, blockquotes **and** the streaming drift — because `send()` and `edit_message()` then always agree on `msg_type`.

Validated by sending real test cards to a live Feishu client: the native `tag:"table"` component does **NOT** support column alignment (API rejects `align`, ErrCode 200621), while the `tag:"markdown"` element supports GFM alignment + full CommonMark + auto-pagination. So no table parsing is needed — the markdown element covers everything.

Feature flag `feishu_interactive_cards` (default `true`) restores legacy `text`/`post` behavior for rollback.

## This continues & supersedes my earlier work

This continues and supersedes my earlier work — issue **[#25452](https://github.com/NousResearch/hermes-agent/issues/25452)** and PR **[#25453](https://github.com/NousResearch/hermes-agent/pull/25453)** — rebuilt on current `main` with expanded scope (all markdown, not just tables) and a streaming `msg_type` fix. (PR [#25453](https://github.com/NousResearch/hermes-agent/pull/25453) was `BLOCKED` on a stale base.)

## Related issues

- **Tables**: [Feishu channel displays markdown tables as raw source code instead of rendering them #25452](https://github.com/NousResearch/hermes-agent/issues/25452)[\[Feishu\] Markdown tables not rendering in Feishu messages #9549](https://github.com/NousResearch/hermes-agent/issues/9549)[Feishu gateway: Markdown tables render as broken plain text #29245](https://github.com/NousResearch/hermes-agent/issues/29245)[feishu: Markdown tables render as garbled text — missing post-format table support #18704](https://github.com/NousResearch/hermes-agent/issues/18704)[Bug Report: Feishu (Lark) Markdown Table Rendering Regression in v0.13.0 #21778](https://github.com/NousResearch/hermes-agent/issues/21778)[Feishu: markdown tables render as raw text instead of using interactive card #21866](https://github.com/NousResearch/hermes-agent/issues/21866)[\[Feishu Bug\] Markdown source code displayed instead of rendered card format #7022](https://github.com/NousResearch/hermes-agent/issues/7022)[fix(feishu): markdown tables not rendering as interactive cards — simplify `_should_send_as_card()` trigger condition #9536](https://github.com/NousResearch/hermes-agent/issues/9536)[\[feishu\] Fix markdown table rendering: use post+tag:md instead of force-text workaround #27529](https://github.com/NousResearch/hermes-agent/issues/27529)[\[feishu\] Remove markdown table force-text workaround — Feishu now supports tables in post format #26658](https://github.com/NousResearch/hermes-agent/issues/26658)
- **Code / other markdown**: [\[Feishu\] Code blocks cannot be expanded — only first ~2 lines visible #19035](https://github.com/NousResearch/hermes-agent/issues/19035)[Feishu/Lark messages poorly formatted due to excessive Markdown escaping #9816](https://github.com/NousResearch/hermes-agent/issues/9816)[Feishu replies render raw Markdown while normal messages render correctly #24319](https://github.com/NousResearch/hermes-agent/issues/24319)
- **Streaming msg\_type (fixed by this)**: [\[Feishu\] First chunk of long messages sent as msg\_type=text instead of post, breaking Markdown rendering #26841](https://github.com/NousResearch/hermes-agent/issues/26841)[bug(feishu): first chunk of long messages sent as msg\_type=text, breaking Markdown rendering #29471](https://github.com/NousResearch/hermes-agent/issues/29471)
- **Unified approach**: [\[feishu\] Unified fix for markdown rendering: inbound escaping + GFM table → Card 2.0 #27469](https://github.com/NousResearch/hermes-agent/issues/27469)
- **Interactive card feature requests**: [feat(feishu): support interactive card messages in send\_message for table rendering #46187](https://github.com/NousResearch/hermes-agent/issues/46187)[\[Feature\] Support Feishu interactive card (msg\_type=interactive) in send\_message #37777](https://github.com/NousResearch/hermes-agent/issues/37777)[\[Feature\]: Native Feishu Interactive Card Support #21873](https://github.com/NousResearch/hermes-agent/issues/21873)[Feature Request: Support Card JSON 2.0 Tables in Feishu Adapter #21326](https://github.com/NousResearch/hermes-agent/issues/21326)

Co-authored-by: GLM 5.2

👍React with 👍2Ranger-zzz and foreverzxc

## Activity

[![](https://avatars.githubusercontent.com/u/51010652?s=64&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)wait4xx](https://github.com/wait4xx)

linked a pull request that will close this issue [1mo agoon Jun 15, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#event-7426425186)

- [fix(feishu): render all markdown via Card 2.0 interactive cards #46472](https://github.com/NousResearch/hermes-agent/pull/46472)


[![](https://avatars.githubusercontent.com/u/51010652?s=64&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)wait4xx](https://github.com/wait4xx)

mentioned this [1mo agoon Jun 15, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#event-7426432035)

- [fix(feishu): render markdown tables as interactive card table components #25453](https://github.com/NousResearch/hermes-agent/pull/25453)

- [Feishu channel displays markdown tables as raw source code instead of rendering them #25452](https://github.com/NousResearch/hermes-agent/issues/25452)


[![](https://avatars.githubusercontent.com/u/52913345?s=64&u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4)alt-glitch](https://github.com/alt-glitch)

added

[type/featureNew feature or request](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22type%2Ffeature%22) New feature or request

[P3Low — cosmetic, nice to have](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22P3%22) Low — cosmetic, nice to have

[comp/gatewayGateway runner, session dispatch, delivery](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22comp%2Fgateway%22) Gateway runner, session dispatch, delivery

[platform/feishuFeishu / Lark adapter](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22platform%2Ffeishu%22) Feishu / Lark adapter

[1mo agoon Jun 15, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#event-26740846764)

### wait4xx commented last monthon Jun 17, 2026

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4&size=48)](https://github.com/wait4xx)

[wait4xx](https://github.com/wait4xx)

[1mo agoon Jun 17, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#issuecomment-4732081991)

Author

More actions

Update: PR [#46472](https://github.com/NousResearch/hermes-agent/pull/46472) has been rebased onto current `main` and now also includes:

- **Mermaid → image** — ```​``mermaid``` blocks render to a transparent PNG via the local `mmdc` CLI, with a tiered fallback (external `mermaid.ink` for browser-less/Docker hosts → fenced code block); non-blocking.
- **Mermaid extraction fix** — the closing-fence regex wasn't `MULTILINE`, so mermaid blocks were never detected (always fell back to code block).
- **Table limit fix** — corrected the per-card GFM table limit to 4 (the markdown-element limit; was using the native `tag:"table"` component's 5).

Details in the PR.

Co-authored-by: GLM 5.2

### wait4xx commented 3 weeks agoon Jun 21, 2026

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4&size=48)](https://github.com/wait4xx)

[wait4xx](https://github.com/wait4xx)

[3w agoon Jun 21, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#issuecomment-4761126979)

Author

More actions

Update: PR [#46472](https://github.com/NousResearch/hermes-agent/pull/46472) has been rebased onto current `main` (resolving the `gateway/platforms/feishu.py` → `plugins/platforms/feishu/adapter.py` module migration cleanly — now **MERGEABLE**) and additionally adds **code-block language tags**: terminal-command previews in tool-progress messages now use a bash-tagged code fence for syntax highlighting on Feishu cards (new `code_block_language_tag` adapter attribute, opt-in per platform; default empty so other platforms are unaffected). 14 stale test imports updated to the new module path; all 218 feishu tests pass.

Co-authored-by: GLM 5.2

👍React with 👍1sacanods

### sacanods commented 2 weeks agoon Jun 25, 2026

[![@sacanods](https://avatars.githubusercontent.com/u/99579879?u=7b5034e621380db0a01701964c882615a22a1477&v=4&size=48)](https://github.com/sacanods)

[sacanods](https://github.com/sacanods)

[2w agoon Jun 25, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#issuecomment-4805930164)

More actions

This issue has been bothering me for a long time. I have to run a patch script after every upgrade to manually fix it. It would be great if the team could consider merging a fix for this.

### BenBenJian commented 2 weeks agoon Jun 28, 2026

[![@BenBenJian](https://avatars.githubusercontent.com/u/96902190?v=4&size=48)](https://github.com/BenBenJian)

[BenBenJian](https://github.com/BenBenJian)

[2w agoon Jun 28, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#issuecomment-4826132407)

More actions

> 这个问题困扰我很久了。每次升级后我都得跑补丁脚本手动修复。如果团队能考虑合并修复方案，那就太好了。

which patch script do you use?

[![](https://avatars.githubusercontent.com/u/52913345?s=64&u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4)alt-glitch](https://github.com/alt-glitch)

added

[P2Medium — degraded but workaround exists](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22P2%22) Medium — degraded but workaround exists

and removed

[P3Low — cosmetic, nice to have](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22P3%22) Low — cosmetic, nice to have

[2w agoon Jun 28, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#event-27298849306)

### alt-glitch commented 2 weeks agoon Jun 28, 2026

[![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4&size=48)](https://github.com/alt-glitch)

[alt-glitch](https://github.com/alt-glitch)

[2w agoon Jun 28, 2026](https://github.com/NousResearch/hermes-agent/issues/46470#issuecomment-4826160329)

Collaborator

More actions

> _This was generated by AI during triage._

Re-triaged to P2 (from P3): two distinct external users confirm recurring pain (manual patch script every upgrade), and this matches the sibling consolidation [#27469](https://github.com/NousResearch/hermes-agent/issues/27469) (P2, lower-traffic core gateway). Related to consolidation [#27469](https://github.com/NousResearch/hermes-agent/issues/27469) and implementing PR [#46472](https://github.com/NousResearch/hermes-agent/pull/46472) (open) — not a duplicate (this has expanded all-markdown + streaming-msg\_type scope). Not closing; cluster pick is for a human.

[Sign up for free](https://github.com/signup?return_to=https://github.com/NousResearch/hermes-agent/issues/46470)**to join this conversation on GitHub.** Already have an account? [Sign in to comment](https://github.com/login?return_to=https://github.com/NousResearch/hermes-agent/issues/46470)

## Metadata

## Metadata

### Assignees

No one assigned

### Labels

[P2Medium — degraded but workaround exists](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22P2%22) Medium — degraded but workaround exists [comp/gatewayGateway runner, session dispatch, delivery](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22comp%2Fgateway%22) Gateway runner, session dispatch, delivery [platform/feishuFeishu / Lark adapter](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22platform%2Ffeishu%22) Feishu / Lark adapter [type/featureNew feature or request](https://github.com/NousResearch/hermes-agent/issues?q=state%3Aopen%20label%3A%22type%2Ffeature%22) New feature or request

### Type

No type

### Fields

No fields configured for issues without a type.

### Projects

No projects

### Milestone

No milestone

### Relationships

None yet

### Development

- [fix(feishu): render all markdown via Card 2.0 interactive cardsNousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/pull/46472)

### Participants

[![@wait4xx](https://avatars.githubusercontent.com/u/51010652?s=64&u=848dfb032733faef1f51817d24efc2fb0789ca1f&v=4)](https://github.com/wait4xx)[![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?s=64&u=b0d1b58e0f8358f695a038e6f8c8dcf02e5963b0&v=4)](https://github.com/alt-glitch)[![@BenBenJian](https://avatars.githubusercontent.com/u/96902190?s=64&v=4)](https://github.com/BenBenJian)[![@sacanods](https://avatars.githubusercontent.com/u/99579879?s=64&u=7b5034e621380db0a01701964c882615a22a1477&v=4)](https://github.com/sacanods)

## Issue actions

- ![](https://github.githubassets.com/assets/github-copilot-app-light-7138e992c731a2bb.png)Open in GitHub Copilot app

You can’t perform that action at this time.