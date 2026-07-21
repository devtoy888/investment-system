[Skip to content](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20).

[NousResearch](https://github.com/NousResearch)/ **[hermes-agent](https://github.com/NousResearch/hermes-agent)** Public

- [Notifications](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent) You must be signed in to change notification settings
- [Fork\\
41.1k](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent)
- [Star\\
218k](https://github.com/login?return_to=%2FNousResearch%2Fhermes-agent)


# Hermes Agent v0.19.0 (2026.7.20) — The Quicksilver Release

[Latest](https://github.com/NousResearch/hermes-agent/releases/latest)

[Latest](https://github.com/NousResearch/hermes-agent/releases/latest)

Compare

# Choose a tag to compare

## Sorry, something went wrong.

Filter

Loading

## Sorry, something went wrong.

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20).

## No results found

[View all tags](https://github.com/NousResearch/hermes-agent/tags)

![@teknium1](https://avatars.githubusercontent.com/u/127238744?s=40&v=4)[teknium1](https://github.com/teknium1)

released this

8 hours ago
20 Jul 18:35


[v2026.7.20](https://github.com/NousResearch/hermes-agent/tree/v2026.7.20)

This tag was signed with the committer’s **verified signature**.


[![](https://avatars.githubusercontent.com/u/127238744?s=64&v=4)](https://github.com/teknium1)[teknium1](https://github.com/teknium1)
Teknium


SSH Key Fingerprint: x9xNOpeJhoEAY2gWhmWHZROC3QF3VjOEbmNo9vQ8y2A

Verified
on Jul 20, 2026, 02:35 PM

[Learn about vigilant mode](https://docs.github.com/github/authenticating-to-github/displaying-verification-statuses-for-all-of-your-commits).


[`3ef6bbd`](https://github.com/NousResearch/hermes-agent/commit/3ef6bbd201263d354fd83ec55b3c306ded2eb72a)

This commit was created on GitHub.com and signed with GitHub’s **verified signature**.


GPG key ID: B5690EEEBB952194

Verified
on Jul 20, 2026, 02:35 PM

[Learn about vigilant mode](https://docs.github.com/github/authenticating-to-github/displaying-verification-statuses-for-all-of-your-commits).


# Hermes Agent v0.19.0 (v2026.7.20)

**Release Date:** July 20, 2026

**Since v0.18.0:** ~2,245 commits · ~1,065 merged PRs · ~2,465 files changed · ~300,000 insertions · ~36,000 deletions · **~3,300 issues closed** · **450+ community contributors**

> **The Quicksilver Release.** Hermes is the messenger god, and this window we made him move like it. First-turn time-to-first-token dropped **~80% on every platform**, reasoning streams live by default, the desktop app got a ~20-PR speed overhaul (14× faster streaming markdown, virtualized diffs, snappy session switching), and the TUI renders markdown incrementally. Around that speed spine: you can now **manage your Nous subscription without leaving the terminal**, plug **Bitwarden and 1Password** straight into Hermes, let **smart approvals** judge flagged commands for you by default, **watch your subagents work live**, and trust that a finished response **survives a gateway crash** thanks to a durable delivery ledger. This release also rolls up everything from the v0.18.1 and v0.18.2 infrastructure patch tags — those windows are fully documented here.

* * *

## ✨ Highlights

- **Hermes got dramatically faster — first token in a fraction of the time** — Cold-start "Initializing agent..." used to eat ~4.3 seconds before your first turn even reached the model; it's now ~0.9s, an ~80% cut that applies to the CLI, gateway, TUI, desktop, and cron alike. Round 2 attacked what you _see_ while waiting: reasoning models now stream their thinking live by default (no more staring at a spinner for 30 seconds), and the response box paints per token instead of per line. If Hermes ever felt like it took a deep breath before answering, that breath is gone. ( [#59332](https://github.com/NousResearch/hermes-agent/pull/59332), [#59389](https://github.com/NousResearch/hermes-agent/pull/59389) — [@teknium1](https://github.com/teknium1))

- **The desktop app speed wave — 20+ targeted perf PRs** — Long replies used to cost 14× more CPU in the markdown splitter than they do now; giant diffs froze the review pane until we virtualized it; switching sessions thrashes layout no more. Streaming no longer re-renders the sidebar and every tool row per token, profile backends pre-warm on hover intent, and boot-hidden panes mount at idle instead of on the cold-start critical path. The net effect: the desktop app feels like a native app under load, even with huge transcripts and busy agents. ( [#67154](https://github.com/NousResearch/hermes-agent/pull/67154), [#67818](https://github.com/NousResearch/hermes-agent/pull/67818), [#65898](https://github.com/NousResearch/hermes-agent/pull/65898), [#66033](https://github.com/NousResearch/hermes-agent/pull/66033), [#66747](https://github.com/NousResearch/hermes-agent/pull/66747), [#67742](https://github.com/NousResearch/hermes-agent/pull/67742) and more — [@OutThisLife](https://github.com/OutThisLife))

- **Manage your Nous plan from the terminal — `/subscription` and `/topup`** — Changing your subscription used to mean a trip to the billing website. Now `/subscription` opens a full flow right in the TUI or classic CLI: see your plan and remaining allowance, preview exactly what an upgrade costs ("Pay $46.30 & upgrade now") or when a downgrade takes effect, and apply it — with scheduled-change banners and undo. The desktop app got a matching billing settings tab. Your wallet never has to leave the keyboard. ( [#51639](https://github.com/NousResearch/hermes-agent/pull/51639), [#61054](https://github.com/NousResearch/hermes-agent/pull/61054), [#61067](https://github.com/NousResearch/hermes-agent/pull/61067) — [@alt-glitch](https://github.com/alt-glitch))

- **Smart approvals are now the default** — When Hermes wants to run a flagged command, an LLM reviewer now assesses it independently instead of asking you to approve every single one — and each verdict covers only that exact command, so a later command matching the same pattern gets its own review. Combined with the new **user-defined deny rules** (which block commands even under yolo mode) and `/deny <reason>` (which tells the agent _why_ you refused so it course-corrects), day-to-day approval fatigue drops sharply without giving up control. ( [#62661](https://github.com/NousResearch/hermes-agent/pull/62661), [#59164](https://github.com/NousResearch/hermes-agent/pull/59164), [#54518](https://github.com/NousResearch/hermes-agent/pull/54518) — [@teknium1](https://github.com/teknium1))

- **Plug your password manager into Hermes — Bitwarden & 1Password secret sources** — API keys no longer have to live in a plaintext `.env`. A new pluggable `SecretSource` interface lets Hermes fetch secrets from Bitwarden and 1Password (`op://` references) at load time, with multiple vaults enabled simultaneously, deterministic precedence, conflict warnings, and per-variable provenance. This consolidated eleven competing community PRs into one orchestrated interface — future vault providers drop in as plugins. ( [#59498](https://github.com/NousResearch/hermes-agent/pull/59498) — [@teknium1](https://github.com/teknium1), 1Password provider salvaged from [@hwrdprkns](https://github.com/hwrdprkns))

- **Watch your subagents work — live transcripts + durable background delegation** — `delegate_task` dispatches now return live transcript files you can `tail -f` the moment the subagents launch: every tool call, result, and streamed reply, one human-readable log per child. And background delegation completions are now **durable** — if the process restarts mid-run, results are restored and delivered through an ownership-checked ledger instead of vanishing. Fan out a fleet, watch any worker live, and never lose the results. ( [#67479](https://github.com/NousResearch/hermes-agent/pull/67479), [#63494](https://github.com/NousResearch/hermes-agent/pull/63494) — [@teknium1](https://github.com/teknium1))

- **A finished answer can no longer be lost — the delivery-obligation ledger** — If the gateway died between generating your response and confirming the platform actually delivered it, that answer used to be silently gone (and you'd paid for the turn). Final responses are now recorded in a durable ledger in `state.db` around the platform send and **redelivered on the next boot** — closing a P1 silent-loss window for Telegram, Discord, Slack, and every other channel. ( [#67181](https://github.com/NousResearch/hermes-agent/pull/67181) — [@teknium1](https://github.com/teknium1))

- **One gateway, many profiles — profile-based message routing** — A single multiplexed gateway sharing one bot token can now route specific guilds, channels, or threads to different profiles — each with fully isolated config, skills, memory, and secrets. Point your work Discord server at the `work` profile and your hobby server at `personal`, from one bot. A second multiplex hardening wave means one misconfigured profile can no longer take down the whole gateway. ( [#64835](https://github.com/NousResearch/hermes-agent/pull/64835) salvaging [@Burgunthy](https://github.com/Burgunthy), [#65700](https://github.com/NousResearch/hermes-agent/pull/65700), [#60589](https://github.com/NousResearch/hermes-agent/pull/60589) — [@teknium1](https://github.com/teknium1), [@benbarclay](https://github.com/benbarclay) \+ six salvaged contributors)

- **New providers and the newest frontier models** — Fireworks AI and DeepInfra land as first-class providers (Fireworks with cost estimation and a [#2](https://github.com/NousResearch/hermes-agent/pull/2) slot in the provider picker), Upstage Solar joins via salvage, and the model catalogs picked up **GPT-5.6 (Sol/Terra/Luna + Pro variants, wired end-to-end across every route)**, **grok-4.5 (GA)**, **moonshotai/kimi-k3**, **claude-fable-5 / claude-sonnet-5**, and GA **tencent/hy3** — plus LM Studio JIT model loading for local setups. ( [#62593](https://github.com/NousResearch/hermes-agent/pull/62593), [#63969](https://github.com/NousResearch/hermes-agent/pull/63969), [#61616](https://github.com/NousResearch/hermes-agent/pull/61616) — [@kshitijk4poor](https://github.com/kshitijk4poor) completing [@rob-maron](https://github.com/rob-maron)'s [#61578](https://github.com/NousResearch/hermes-agent/pull/61578), [#60887](https://github.com/NousResearch/hermes-agent/pull/60887), [#65913](https://github.com/NousResearch/hermes-agent/pull/65913), [#64541](https://github.com/NousResearch/hermes-agent/pull/64541), [#65472](https://github.com/NousResearch/hermes-agent/pull/65472))

- **Crank the thinking to max — new reasoning effort tiers and per-model control** — Reasoning effort gained `max` and `ultra` levels (GPT-5.6 and Codex's top tiers), selectable everywhere from the CLI to the desktop, with sane clamping on providers with smaller scales. You can now also pin **per-model reasoning-effort overrides** in config, set **per-slot effort in MoA presets** (your advisors think hard, your synthesizer stays fast), and per-task effort for auxiliary models. Thinking depth is now a dial, not a global switch. ( [#62650](https://github.com/NousResearch/hermes-agent/pull/62650), [#64458](https://github.com/NousResearch/hermes-agent/pull/64458), [#64631](https://github.com/NousResearch/hermes-agent/pull/64631), [#64597](https://github.com/NousResearch/hermes-agent/pull/64597) — [@teknium1](https://github.com/teknium1))

- **Your sessions, your data — export everything** — `hermes sessions export` now writes Markdown, Quarto, HTML, prompt-only, and even Hugging Face-ready trace formats, with the full filter surface (age, workspace, platform), an opt-in `--redact` secret-scrubbing pass, and compacted-session lineage stitched into one logical export. Pair with the new prune filters and bulk archive to keep your session store tidy. Your conversation history is a real dataset now, not a black box. ( [#60186](https://github.com/NousResearch/hermes-agent/pull/60186) salvaging [@web3blind](https://github.com/web3blind), [#60492](https://github.com/NousResearch/hermes-agent/pull/60492), [#60507](https://github.com/NousResearch/hermes-agent/pull/60507), [#59327](https://github.com/NousResearch/hermes-agent/pull/59327) — [@teknium1](https://github.com/teknium1))

- **Security hardening round** — This window closed a long list of credential-surface gaps: Vertex credentials scoped away from subprocess env and through profile secret scopes, media/vision/image-gen local-file reads routed through one shared credential-read guard, a webhook body-size-cap sweep across every aiohttp server, bot-token redaction in Telegram transport errors, Fireworks token prefixes added to the redactor, six P1 browser/MEDIA/.env hardening PRs salvaged in one pass, and CI hardened against untrusted-ref interpolation. ( [#57660](https://github.com/NousResearch/hermes-agent/pull/57660), [#58709](https://github.com/NousResearch/hermes-agent/pull/58709), [#59215](https://github.com/NousResearch/hermes-agent/pull/59215), [#56582](https://github.com/NousResearch/hermes-agent/pull/56582), [#57842](https://github.com/NousResearch/hermes-agent/pull/57842) — [@teknium1](https://github.com/teknium1), [@srojk34](https://github.com/srojk34), [@kshitijk4poor](https://github.com/kshitijk4poor), [@jquesnelle](https://github.com/jquesnelle))


* * *

## ⚡ Performance — the speed spine

### First-turn latency (all platforms)

- **~80% TTFT cut** — Discord capability detection off the critical path (token-keyed 24h disk cache + background refresh), Ollama probe skipped for known non-Ollama providers, agent-init blocking work removed; cold submit→dispatch ~4.3s → ~0.9s ( [#59332](https://github.com/NousResearch/hermes-agent/pull/59332) — [@teknium1](https://github.com/teknium1))
- **Perceived-latency round 2** — `display.show_reasoning` default ON (watch the model think instead of a spinner), per-token response-box painting with width-aware force-flush, prompt-build caching, mtime-cached timezone resolution ( [#59389](https://github.com/NousResearch/hermes-agent/pull/59389) — [@teknium1](https://github.com/teknium1))
- Segment mixed tool batches to recover lost concurrency; drop per-call base64 re-serialization from request-size estimates ( [#64460](https://github.com/NousResearch/hermes-agent/pull/64460), [#67788](https://github.com/NousResearch/hermes-agent/pull/67788) — [@teknium1](https://github.com/teknium1), [@OutThisLife](https://github.com/OutThisLife))

### Desktop speed wave

- 14× less splitter CPU via incremental block lexing for streaming markdown; virtualized review-pane diffs (no more full-Shiki freeze); snappy session switching on large transcripts; killed the layout-thrash cascade on session switch ( [#67154](https://github.com/NousResearch/hermes-agent/pull/67154), [#67818](https://github.com/NousResearch/hermes-agent/pull/67818), [#65898](https://github.com/NousResearch/hermes-agent/pull/65898), [#66033](https://github.com/NousResearch/hermes-agent/pull/66033) — [@OutThisLife](https://github.com/OutThisLife))
- Cut startup serialization + per-turn REST amplification; pre-warm profile backends and gateway sockets on hover intent; idle-mount boot-hidden panes; fast model picker + dialogs ( [#66747](https://github.com/NousResearch/hermes-agent/pull/66747), [#66347](https://github.com/NousResearch/hermes-agent/pull/66347), [#67857](https://github.com/NousResearch/hermes-agent/pull/67857), [#66470](https://github.com/NousResearch/hermes-agent/pull/66470) — [@OutThisLife](https://github.com/OutThisLife))
- Stop per-token sidebar + tool-row re-renders during streaming; stop eager JSON.stringify of every tool's args/result; scope tool-diff subscriptions; batch sidebar session slices into one profile-DB pass; targeted file-tree revalidation; rAF-coalesced sash resizes ( [#67742](https://github.com/NousResearch/hermes-agent/pull/67742), [#67842](https://github.com/NousResearch/hermes-agent/pull/67842), [#67195](https://github.com/NousResearch/hermes-agent/pull/67195), [#67245](https://github.com/NousResearch/hermes-agent/pull/67245), [#67824](https://github.com/NousResearch/hermes-agent/pull/67824), [#67838](https://github.com/NousResearch/hermes-agent/pull/67838), [#67844](https://github.com/NousResearch/hermes-agent/pull/67844) — [@OutThisLife](https://github.com/OutThisLife))
- Systematized perf benchmark harness with trustworthy cold-start + first-token measurement, replacing 12 one-off scripts ( [#67466](https://github.com/NousResearch/hermes-agent/pull/67466), [#67697](https://github.com/NousResearch/hermes-agent/pull/67697) — [@OutThisLife](https://github.com/OutThisLife))

### Everywhere else

- TUI renders streamed markdown incrementally per block ( [#67236](https://github.com/NousResearch/hermes-agent/pull/67236) — [@OutThisLife](https://github.com/OutThisLife))
- Skill discovery cached by scan signature; snapshot manifest builds ~5× faster; text prefilter before AST parse in tool discovery ( [#61414](https://github.com/NousResearch/hermes-agent/pull/61414), [#61131](https://github.com/NousResearch/hermes-agent/pull/61131), [#63941](https://github.com/NousResearch/hermes-agent/pull/63941) — [@kshitijk4poor](https://github.com/kshitijk4poor), [@ethernet8023](https://github.com/ethernet8023))
- Copy-on-write message prep instead of full deepcopy; model-metadata probe-cache cluster; gateway `session.resume` model + display history from one SELECT ( [#61133](https://github.com/NousResearch/hermes-agent/pull/61133), [#61368](https://github.com/NousResearch/hermes-agent/pull/61368), [#67247](https://github.com/NousResearch/hermes-agent/pull/67247) — [@kshitijk4poor](https://github.com/kshitijk4poor), [@OutThisLife](https://github.com/OutThisLife))
- `hermes update` skips npm install when Node manifests are unchanged; dashboard session-list payloads trimmed + messages paginated ( [#61580](https://github.com/NousResearch/hermes-agent/pull/61580), [#60883](https://github.com/NousResearch/hermes-agent/pull/60883) — [@kshitijk4poor](https://github.com/kshitijk4poor))
- Byte-stable gateway system prompts — pinned session-context render keeps the prompt cache alive across turns ( [#67403](https://github.com/NousResearch/hermes-agent/pull/67403) — [@kshitijk4poor](https://github.com/kshitijk4poor))

## 🏗️ Core Agent & Architecture

### Providers & models

- **Fireworks AI provider** with cost estimation + cached picker price columns, promoted to [#2](https://github.com/NousResearch/hermes-agent/pull/2) in provider pickers ( [#62593](https://github.com/NousResearch/hermes-agent/pull/62593), [#65476](https://github.com/NousResearch/hermes-agent/pull/65476), [#65214](https://github.com/NousResearch/hermes-agent/pull/65214) — [@teknium1](https://github.com/teknium1))
- **DeepInfra** hardened integration; **Upstage Solar** provider ( [#42231](https://github.com/NousResearch/hermes-agent/pull/42231) salvage) ( [#63969](https://github.com/NousResearch/hermes-agent/pull/63969), [#64541](https://github.com/NousResearch/hermes-agent/pull/64541) — [@kshitijk4poor](https://github.com/kshitijk4poor))
- **GPT-5.6 (Sol/Terra/Luna + Pro) end-to-end** — context lengths, native/Codex catalogs, pricing, compaction caps across every route ( [#61616](https://github.com/NousResearch/hermes-agent/pull/61616) — [@kshitijk4poor](https://github.com/kshitijk4poor), building on [@rob-maron](https://github.com/rob-maron))
- grok-4.5 (GA) catalog + reasoning allowlist; kimi-k3 on Nous Portal + OpenRouter (kimi-k2.x retired) + K3 discovery on the Kimi Coding endpoint; claude-fable-5 / claude-sonnet-5 / fugu-ultra curated; GA tencent/hy3 ( [#60887](https://github.com/NousResearch/hermes-agent/pull/60887), [#65913](https://github.com/NousResearch/hermes-agent/pull/65913), [#65922](https://github.com/NousResearch/hermes-agent/pull/65922), [#56617](https://github.com/NousResearch/hermes-agent/pull/56617), [#60943](https://github.com/NousResearch/hermes-agent/pull/60943) — [@teknium1](https://github.com/teknium1))
- Catalog-labeled silent default (GLM-5.2) + bare-provider `/model` cost-safe routing; LM Studio JIT load mode; adaptive thinking for Kimi-family Anthropic endpoints ( [#64771](https://github.com/NousResearch/hermes-agent/pull/64771), [#65472](https://github.com/NousResearch/hermes-agent/pull/65472), [#67606](https://github.com/NousResearch/hermes-agent/pull/67606) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor))
- GLM-5.2 native reasoning\_effort controls; Gemini request-context improvements; extra HTTP headers for LLM API calls; per-client model routing on the API server ( [#58884](https://github.com/NousResearch/hermes-agent/pull/58884), [#61873](https://github.com/NousResearch/hermes-agent/pull/61873) — [@vishal-dharm](https://github.com/vishal-dharm), [#57038](https://github.com/NousResearch/hermes-agent/pull/57038), [#57028](https://github.com/NousResearch/hermes-agent/pull/57028) — [@teknium1](https://github.com/teknium1))
- **Claude Sonnet 5 fully wired** — curated lists, intro pricing, and metadata across every route ( [#67932](https://github.com/NousResearch/hermes-agent/pull/67932) — [@teknium1](https://github.com/teknium1))
- **Hide providers you don't use** — `enabled: false` per-provider flag + `excluded_providers` config scrub unwanted providers from `/model` pickers and built-in resolution ( [#67971](https://github.com/NousResearch/hermes-agent/pull/67971) — [@teknium1](https://github.com/teknium1))
- Bedrock catalog wave: real context-window probing from the live endpoint, 1M-context rows for current-gen Claude + Fable, geo-prefix parity, versioned profile-ID pricing, Opus 4.8/4.7 rows ( [#68007](https://github.com/NousResearch/hermes-agent/pull/68007), [#67977](https://github.com/NousResearch/hermes-agent/pull/67977), [#68005](https://github.com/NousResearch/hermes-agent/pull/68005), [#67976](https://github.com/NousResearch/hermes-agent/pull/67976) — [@teknium1](https://github.com/teknium1))
- kimi-k3 rollout completed across Kimi-direct catalog surfaces with 1M context on canonical Kimi Coding endpoints ( [#68108](https://github.com/NousResearch/hermes-agent/pull/68108) — [@teknium1](https://github.com/teknium1))
- Provider pickers: Qwen providers folded into one group row; collapsible provider groups in the desktop model picker; friendlier TUI model display grouping same-endpoint providers ( [#67758](https://github.com/NousResearch/hermes-agent/pull/67758), [#67904](https://github.com/NousResearch/hermes-agent/pull/67904), [#67908](https://github.com/NousResearch/hermes-agent/pull/67908) — [@teknium1](https://github.com/teknium1))

### Reasoning & MoA

- `max` \+ `ultra` effort levels across every surface and route ( [#62650](https://github.com/NousResearch/hermes-agent/pull/62650) — [@teknium1](https://github.com/teknium1))
- Per-model reasoning\_effort overrides via a unified resolution chokepoint; per-task auxiliary effort; per-slot MoA preset effort; session-scoped `/reasoning` in the CLI ( [#64458](https://github.com/NousResearch/hermes-agent/pull/64458), [#64597](https://github.com/NousResearch/hermes-agent/pull/64597), [#64631](https://github.com/NousResearch/hermes-agent/pull/64631), [#67946](https://github.com/NousResearch/hermes-agent/pull/67946) — [@teknium1](https://github.com/teknium1))
- MoA: `reference_max_tokens` to cap advisor output and cut latency; per-preset fanout cadence (`user_turn` runs advisors once per user turn); stale presets surfaced without retries; half-filled preset saves rejected at the API boundary; aggregator resolves reasoning like an acting model ( [#56756](https://github.com/NousResearch/hermes-agent/pull/56756), [#57591](https://github.com/NousResearch/hermes-agent/pull/57591), [#64756](https://github.com/NousResearch/hermes-agent/pull/64756) — [@teknium1](https://github.com/teknium1))

### Delegation, approvals & the agent loop

- Live subagent transcripts + durable background completions (see Highlights) ( [#67479](https://github.com/NousResearch/hermes-agent/pull/67479), [#63494](https://github.com/NousResearch/hermes-agent/pull/63494) — [@teknium1](https://github.com/teknium1))
- Smart approvals default; user-defined deny rules (block even under yolo); `/deny <reason>` relays the denial reason; plugin `pre_tool_call` approve action escalates to a human gate (re-landed with rule keys) ( [#62661](https://github.com/NousResearch/hermes-agent/pull/62661), [#59164](https://github.com/NousResearch/hermes-agent/pull/59164), [#54518](https://github.com/NousResearch/hermes-agent/pull/54518), [#60504](https://github.com/NousResearch/hermes-agent/pull/60504) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor))
- Unified delegation concurrency caps (`max_async_children` deprecated); explain long provider waits on the live status line; deterministic tool-output risk exposure ( [#56955](https://github.com/NousResearch/hermes-agent/pull/56955), [#64775](https://github.com/NousResearch/hermes-agent/pull/64775), [#61793](https://github.com/NousResearch/hermes-agent/pull/61793) — [@teknium1](https://github.com/teknium1))
- Codex: live TUI/desktop tool cards for the app-server runtime, commentary streamed as visible interim messages, compaction routed through `thread/compact/start`, max-output truncation recovery, oversized message ids dropped on replay, banked usage-limit resets via `/usage reset` ( [#66514](https://github.com/NousResearch/hermes-agent/pull/66514), [#66115](https://github.com/NousResearch/hermes-agent/pull/66115), [#60114](https://github.com/NousResearch/hermes-agent/pull/60114), [#58155](https://github.com/NousResearch/hermes-agent/pull/58155), [#62225](https://github.com/NousResearch/hermes-agent/pull/62225) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor), [@JoaoMarcos44](https://github.com/JoaoMarcos44), [#64280](https://github.com/NousResearch/hermes-agent/pull/64280) — [@teknium1](https://github.com/teknium1))
- Hooks: oversized hook-injected context spills to disk ( [#20468](https://github.com/NousResearch/hermes-agent/pull/20468) — [@teknium1](https://github.com/teknium1))
- Vibe reactions — floating hearts on affection across CLI/TUI/desktop, token-free core detection ( [#62016](https://github.com/NousResearch/hermes-agent/pull/62016) — [@OutThisLife](https://github.com/OutThisLife))

### Secrets & config

- Pluggable `SecretSource` interface + Bitwarden & 1Password providers (see Highlights) ( [#59498](https://github.com/NousResearch/hermes-agent/pull/59498) — [@teknium1](https://github.com/teknium1), [@hwrdprkns](https://github.com/hwrdprkns))
- `hermes config get` / `unset`; warn on unknown root config keys + doctor deprecated-key reporting; `display.timestamp_format` ( [#65540](https://github.com/NousResearch/hermes-agent/pull/65540), [#67370](https://github.com/NousResearch/hermes-agent/pull/67370), [#40622](https://github.com/NousResearch/hermes-agent/pull/40622) — [@teknium1](https://github.com/teknium1))
- Auxiliary model usage recorded per task in session accounting; conversation-scoped Nous Portal usage tags across aux/MoA/delegate calls; `--usage-file` JSON report for `hermes -z` ( [#65537](https://github.com/NousResearch/hermes-agent/pull/65537), [#65468](https://github.com/NousResearch/hermes-agent/pull/65468), [#59615](https://github.com/NousResearch/hermes-agent/pull/59615) — [@teknium1](https://github.com/teknium1))

### Sessions & compression

- Sessions export: Markdown/QMD/HTML/prompt-only/trace formats, HF upload, `--redact`, unified filters; full prune filter surface + bulk archive; CLI workspace filter + restore-cwd-on-resume ( [#60186](https://github.com/NousResearch/hermes-agent/pull/60186), [#60492](https://github.com/NousResearch/hermes-agent/pull/60492), [#60507](https://github.com/NousResearch/hermes-agent/pull/60507), [#59327](https://github.com/NousResearch/hermes-agent/pull/59327), [#63091](https://github.com/NousResearch/hermes-agent/pull/63091) — [@teknium1](https://github.com/teknium1), [@web3blind](https://github.com/web3blind))
- Compression: preserve human intent and durable handoffs; retain prompt cache when memory is unchanged; flatten multimodal content for the summarizer keeping image handles; gateway compression routing integrity ( [#67275](https://github.com/NousResearch/hermes-agent/pull/67275), [#67916](https://github.com/NousResearch/hermes-agent/pull/67916), [#65046](https://github.com/NousResearch/hermes-agent/pull/65046), [#56868](https://github.com/NousResearch/hermes-agent/pull/56868) — [@kshitijk4poor](https://github.com/kshitijk4poor), [@teknium1](https://github.com/teknium1))
- Gateway session metadata consolidated into state.db; routing index moved to state.db (sessions.json now an optional legacy mirror); exact API bytes persisted in an `api_content` sidecar ( [#58899](https://github.com/NousResearch/hermes-agent/pull/58899), [#59203](https://github.com/NousResearch/hermes-agent/pull/59203), [#67274](https://github.com/NousResearch/hermes-agent/pull/67274) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor))

## 🌐 Gateway, Fleet & Relay

- **Durable delivery-obligation ledger** for final responses (see Highlights) ( [#67181](https://github.com/NousResearch/hermes-agent/pull/67181) — [@teknium1](https://github.com/teknium1))
- **Profile-based routing for inbound messages** \+ multiplex hardening wave 2 + `GATEWAY_MULTIPLEX_PROFILES` override (see Highlights) ( [#64835](https://github.com/NousResearch/hermes-agent/pull/64835), [#65700](https://github.com/NousResearch/hermes-agent/pull/65700), [#60589](https://github.com/NousResearch/hermes-agent/pull/60589) — [@teknium1](https://github.com/teknium1), [@benbarclay](https://github.com/benbarclay) \+ salvaged contributors)
- Per-session turn lease + conversation-scope funnel; unified session reset boundaries (reset sessions stay reset); truthful runtime readiness checks; per-channel model and system prompt overrides; per-session `/model` overrides persist across restarts ( [#67401](https://github.com/NousResearch/hermes-agent/pull/67401), [#65783](https://github.com/NousResearch/hermes-agent/pull/65783), [#62645](https://github.com/NousResearch/hermes-agent/pull/62645), [#56967](https://github.com/NousResearch/hermes-agent/pull/56967), [#57030](https://github.com/NousResearch/hermes-agent/pull/57030) — [@teknium1](https://github.com/teknium1))
- Session auto-reset default off; `/sessions search <query>`; webhook payload filters + route scripts; platform HTTP event callback routing; configurable long-running status phrases ( [#60194](https://github.com/NousResearch/hermes-agent/pull/60194), [#57685](https://github.com/NousResearch/hermes-agent/pull/57685), [#60944](https://github.com/NousResearch/hermes-agent/pull/60944), [#65702](https://github.com/NousResearch/hermes-agent/pull/65702), [#58872](https://github.com/NousResearch/hermes-agent/pull/58872) — [@teknium1](https://github.com/teknium1))
- Relay: generic OIDC client-credentials provisioning (NAS-free), routed profile carried from the connector wire source, channel context consumed from the connector; Nous auth forensics + `nous_session_valid` on `/api/status` for hosted self-heal; Docker re-seeds a terminally-dead Nous bootstrap session on boot ( [#60730](https://github.com/NousResearch/hermes-agent/pull/60730), [#60586](https://github.com/NousResearch/hermes-agent/pull/60586), [#64649](https://github.com/NousResearch/hermes-agent/pull/64649), [#59976](https://github.com/NousResearch/hermes-agent/pull/59976), [#59969](https://github.com/NousResearch/hermes-agent/pull/59969), [#59983](https://github.com/NousResearch/hermes-agent/pull/59983) — [@benbarclay](https://github.com/benbarclay))

## 📱 Messaging Platforms

- **Inline choice pickers** for `/reasoning` and `/fast` on Telegram, Discord, and Matrix — one-tap native buttons instead of typing ( [#65799](https://github.com/NousResearch/hermes-agent/pull/65799) — [@teknium1](https://github.com/teknium1))
- WhatsApp: native Baileys polls (clarify renders as a poll), locations, rich inbound metadata; dashboard pairing flow ( [#58865](https://github.com/NousResearch/hermes-agent/pull/58865), [#60571](https://github.com/NousResearch/hermes-agent/pull/60571) — [@teknium1](https://github.com/teknium1))
- Discord: recover messages missed during reconnect; auto-created threads renamed to generated session titles; configurable interactive view timeout; opt-in owner mentions on exec-approval prompts; optional admin-only gate for approval buttons ( [#66149](https://github.com/NousResearch/hermes-agent/pull/66149), [#60187](https://github.com/NousResearch/hermes-agent/pull/60187), [#60230](https://github.com/NousResearch/hermes-agent/pull/60230), [#60493](https://github.com/NousResearch/hermes-agent/pull/60493), [#51751](https://github.com/NousResearch/hermes-agent/pull/51751) — [@teknium1](https://github.com/teknium1))
- Slack: live per-tool status line ( [#67080](https://github.com/NousResearch/hermes-agent/pull/67080) — [@teknium1](https://github.com/teknium1), salvaging [#62007](https://github.com/NousResearch/hermes-agent/pull/62007))
- Telegram: per-topic free-response allowlist; Google Chat clarify prompts rendered as cards ( [#65543](https://github.com/NousResearch/hermes-agent/pull/65543), [#65546](https://github.com/NousResearch/hermes-agent/pull/65546) — [@teknium1](https://github.com/teknium1))
- Voice: `stt.echo_transcripts` toggle; MEDIA: captions attached to the media bubble on standalone sends; `display.tool_progress: log` option ( [#58859](https://github.com/NousResearch/hermes-agent/pull/58859), [#61415](https://github.com/NousResearch/hermes-agent/pull/61415), [#57014](https://github.com/NousResearch/hermes-agent/pull/57014) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor))

## 🖥️ Hermes Desktop App

- **Contribution-driven shell on a layout-tree model** — panes, zones, and layouts as data; plugin-scoped i18n locale bundles followed ( [#60638](https://github.com/NousResearch/hermes-agent/pull/60638), [#67303](https://github.com/NousResearch/hermes-agent/pull/67303) — [@OutThisLife](https://github.com/OutThisLife))
- **Capabilities page** — Skills/Tools/MCP + Hub in one place, with responsive overlay nav; CLI/dashboard parity for skills hub, MCP test/toggle/catalog, maintenance ops, log filters; five UX fixes from live testing ( [#57590](https://github.com/NousResearch/hermes-agent/pull/57590), [#57441](https://github.com/NousResearch/hermes-agent/pull/57441), [#67482](https://github.com/NousResearch/hermes-agent/pull/67482) — [@OutThisLife](https://github.com/OutThisLife), [@teknium1](https://github.com/teknium1))
- **Hermes Cloud connection mode** (salvage of [#55402](https://github.com/NousResearch/hermes-agent/pull/55402)); soft gateway switch + gateway-settings polish; terminal execution backend picker with health probes ( [#61912](https://github.com/NousResearch/hermes-agent/pull/61912), [#61916](https://github.com/NousResearch/hermes-agent/pull/61916), [#67203](https://github.com/NousResearch/hermes-agent/pull/67203) — [@OutThisLife](https://github.com/OutThisLife), [@teknium1](https://github.com/teknium1))
- Keybind hint tooltips + keybinds settings tab + unified worktree dialog; base-branch picker for new worktrees; green unread dot for background-finished sessions; background-task sidebar indicators; grouped tool calls across text-less messages; auto-scrolling window for long tool-call runs ( [#65204](https://github.com/NousResearch/hermes-agent/pull/65204), [#62243](https://github.com/NousResearch/hermes-agent/pull/62243), [#65109](https://github.com/NousResearch/hermes-agent/pull/65109), [#65174](https://github.com/NousResearch/hermes-agent/pull/65174), [#61147](https://github.com/NousResearch/hermes-agent/pull/61147), [#57913](https://github.com/NousResearch/hermes-agent/pull/57913) — [@ethernet8023](https://github.com/ethernet8023), [@OutThisLife](https://github.com/OutThisLife))
- Session + project color system (inherit from project, per-session override, shared across sidebar/tabs); unified active-project identity in chat status; workspace path status action ( [#67469](https://github.com/NousResearch/hermes-agent/pull/67469), [#67681](https://github.com/NousResearch/hermes-agent/pull/67681), [#67282](https://github.com/NousResearch/hermes-agent/pull/67282), [#63086](https://github.com/NousResearch/hermes-agent/pull/63086) — [@OutThisLife](https://github.com/OutThisLife))
- Declarative memory-provider panel + full-config modal; config-defined TTS/STT providers + xAI TTS params; custom endpoint settings; per-job cron model picker; profile-aware approval mode control; UI scale setting; Ctrl/Cmd+wheel zoom; chat backdrop toggle; `/journey` opens the memory graph overlay ( [#67206](https://github.com/NousResearch/hermes-agent/pull/67206) salvaging [@erosika](https://github.com/erosika), [#67209](https://github.com/NousResearch/hermes-agent/pull/67209), [#67759](https://github.com/NousResearch/hermes-agent/pull/67759) — [@austinpickett](https://github.com/austinpickett), [#67472](https://github.com/NousResearch/hermes-agent/pull/67472), [#63520](https://github.com/NousResearch/hermes-agent/pull/63520), [#60457](https://github.com/NousResearch/hermes-agent/pull/60457), [#67029](https://github.com/NousResearch/hermes-agent/pull/67029), [#64598](https://github.com/NousResearch/hermes-agent/pull/64598), [#57267](https://github.com/NousResearch/hermes-agent/pull/57267) — [@teknium1](https://github.com/teknium1), [@OutThisLife](https://github.com/OutThisLife))
- Full TypeScript conversion of the desktop tree ( [#57855](https://github.com/NousResearch/hermes-agent/pull/57855) — [@ethernet8023](https://github.com/ethernet8023))

## 📊 Web Dashboard

- Memory provider switching; safe session import flow; WhatsApp pairing; Discord-specific toolsets editable from the web UI; clarified manual Telegram bot setup ( [#60569](https://github.com/NousResearch/hermes-agent/pull/60569), [#63699](https://github.com/NousResearch/hermes-agent/pull/63699), [#60571](https://github.com/NousResearch/hermes-agent/pull/60571), [#65361](https://github.com/NousResearch/hermes-agent/pull/65361), [#64636](https://github.com/NousResearch/hermes-agent/pull/64636) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor), [@shannonsands](https://github.com/shannonsands))
- Terminal keep-alive + reattach for dashboard chat sessions; heavy turns isolated in a compute host; paste/drop images into Chat; `browser.headed` schema toggle; profile + gateway topology on `/api/status`; mobile/hosted OpenAI OAuth login ( [#60515](https://github.com/NousResearch/hermes-agent/pull/60515), [#65895](https://github.com/NousResearch/hermes-agent/pull/65895), [#61929](https://github.com/NousResearch/hermes-agent/pull/61929), [#67046](https://github.com/NousResearch/hermes-agent/pull/67046), [#60537](https://github.com/NousResearch/hermes-agent/pull/60537), [#61330](https://github.com/NousResearch/hermes-agent/pull/61330) — [@teknium1](https://github.com/teknium1), [@OutThisLife](https://github.com/OutThisLife), [@benbarclay](https://github.com/benbarclay))
- `hermes serve` is a true headless backend (no web UI build/mount) ( [#55923](https://github.com/NousResearch/hermes-agent/pull/55923) — [@OutThisLife](https://github.com/OutThisLife))

## 🧰 CLI & TUI

- `/subscription` \+ `/topup` terminal billing (see Highlights) ( [#51639](https://github.com/NousResearch/hermes-agent/pull/51639) — [@alt-glitch](https://github.com/alt-glitch))
- **`/model --once`** — one-turn model override that reverts automatically ( [#67113](https://github.com/NousResearch/hermes-agent/pull/67113) — [@teknium1](https://github.com/teknium1), salvaging [#29923](https://github.com/NousResearch/hermes-agent/pull/29923))
- **Stacked slash-skill invocations** — `/skill-a /skill-b do XYZ` loads both skills in order (Claude Code port), with autocomplete + ghost text ( [#57987](https://github.com/NousResearch/hermes-agent/pull/57987), [#58763](https://github.com/NousResearch/hermes-agent/pull/58763) — [@teknium1](https://github.com/teknium1))
- `--safe-mode` troubleshooting flag; uninstall dry-run; TLS failures fail fast with fix hints; `/compact` alias + preview flags; pip/Homebrew installs warned unsupported ( [#45300](https://github.com/NousResearch/hermes-agent/pull/45300), [#60111](https://github.com/NousResearch/hermes-agent/pull/60111), [#57992](https://github.com/NousResearch/hermes-agent/pull/57992), [#57029](https://github.com/NousResearch/hermes-agent/pull/57029), [#57225](https://github.com/NousResearch/hermes-agent/pull/57225) — [@teknium1](https://github.com/teknium1), [@ethernet8023](https://github.com/ethernet8023))
- TUI: model picker refresh support; custom skill bundles dispatched as agent turns; banner sizes skills display to terminal width ( [#59782](https://github.com/NousResearch/hermes-agent/pull/59782) — [@helix4u](https://github.com/helix4u), [#62859](https://github.com/NousResearch/hermes-agent/pull/62859) — [@Adolanium](https://github.com/Adolanium), [#40624](https://github.com/NousResearch/hermes-agent/pull/40624) — [@teknium1](https://github.com/teknium1))
- Hermes Console REPL + perf follow-ups; `hermes curator usage` all-skills view; entry-point plugins surfaced in `hermes plugins list` ( [#57781](https://github.com/NousResearch/hermes-agent/pull/57781) — [@kshitijk4poor](https://github.com/kshitijk4poor), [#36727](https://github.com/NousResearch/hermes-agent/pull/36727), [#40623](https://github.com/NousResearch/hermes-agent/pull/40623) — [@teknium1](https://github.com/teknium1))

## 🔧 Tool System, Skills & MCP

- MCP: `mcp__server__tool` naming convention; server log notifications surfaced in agent.log; hosted OAuth completed across Dashboard + Desktop; configurable `redirect_uri`/`redirect_host` for proxied/WAF setups; OAuth callback port races closed; Blender added to the MCP catalog with a curated 4-tool default ( [#52750](https://github.com/NousResearch/hermes-agent/pull/52750), [#57416](https://github.com/NousResearch/hermes-agent/pull/57416), [#66151](https://github.com/NousResearch/hermes-agent/pull/66151), [#65610](https://github.com/NousResearch/hermes-agent/pull/65610), [#65622](https://github.com/NousResearch/hermes-agent/pull/65622), [#64463](https://github.com/NousResearch/hermes-agent/pull/64463) — [@teknium1](https://github.com/teknium1), [@benbarclay](https://github.com/benbarclay))
- Skills: `security/unbroker` (autonomous data-broker removal) + blind opt-out hardening; `unreal-mcp` companion skill; blender-mcp reworked around the catalog entry; humanizer pattern expansion; `mcp-oauth-remote-gateway` optional skill ( [#57438](https://github.com/NousResearch/hermes-agent/pull/57438), [#57902](https://github.com/NousResearch/hermes-agent/pull/57902), [#65989](https://github.com/NousResearch/hermes-agent/pull/65989), [#64715](https://github.com/NousResearch/hermes-agent/pull/64715) — [@SHL0MS](https://github.com/SHL0MS), [#65066](https://github.com/NousResearch/hermes-agent/pull/65066), [#65486](https://github.com/NousResearch/hermes-agent/pull/65486) — [@teknium1](https://github.com/teknium1))
- Browser: full snapshots stored on truncation, eval denylist opt-in; computer\_use follows cua-driver's verify→escalate ladder ( [#65923](https://github.com/NousResearch/hermes-agent/pull/65923), [#67123](https://github.com/NousResearch/hermes-agent/pull/67123) — [@teknium1](https://github.com/teknium1))
- Kanban: modal create-task dialog + editable board project directory; Done-card results made obvious; grab-to-pan board scrolling; attachment toolset + CLI with SSRF-guarded URL fetch; project directory captured at board creation ( [#66333](https://github.com/NousResearch/hermes-agent/pull/66333), [#63638](https://github.com/NousResearch/hermes-agent/pull/63638), [#60226](https://github.com/NousResearch/hermes-agent/pull/60226), [#65698](https://github.com/NousResearch/hermes-agent/pull/65698), [#63249](https://github.com/NousResearch/hermes-agent/pull/63249) — [@teknium1](https://github.com/teknium1))
- Cron: durable execution audit history; one-shot stale-removal race fixed; run-claim TTL derived from HERMES\_CRON\_TIMEOUT ( [#61791](https://github.com/NousResearch/hermes-agent/pull/61791) — [@teknium1](https://github.com/teknium1), [#62014](https://github.com/NousResearch/hermes-agent/pull/62014) — [@PRATHAMESH75](https://github.com/PRATHAMESH75), [#59567](https://github.com/NousResearch/hermes-agent/pull/59567))
- mem0: self-hosted dashboard backend + recall tuning + setup-wizard mode ( [#56943](https://github.com/NousResearch/hermes-agent/pull/56943), [#60494](https://github.com/NousResearch/hermes-agent/pull/60494) — [@kshitijk4poor](https://github.com/kshitijk4poor), [@teknium1](https://github.com/teknium1))
- Image gen: Codex image inputs; unsupported Codex image accounts classified; tool args recursively normalized by schema (cline port) ( [#57017](https://github.com/NousResearch/hermes-agent/pull/57017), [#63627](https://github.com/NousResearch/hermes-agent/pull/63627), [#52220](https://github.com/NousResearch/hermes-agent/pull/52220) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor))

## 🔒 Security & Reliability

- Vertex: credential/project/region resolution through the profile secret scope; `VERTEX_CREDENTIALS_PATH`/`GOOGLE_APPLICATION_CREDENTIALS` stripped from subprocess env ( [#56680](https://github.com/NousResearch/hermes-agent/pull/56680), [#56582](https://github.com/NousResearch/hermes-agent/pull/56582) — [@srojk34](https://github.com/srojk34))
- Six P1 hardening PRs salvaged in one pass — browser guards, MEDIA anchoring, .env lockdown, delegate ACP transport ( [#57660](https://github.com/NousResearch/hermes-agent/pull/57660) — [@teknium1](https://github.com/teknium1))
- Media/vision/image-gen local-file reads routed through the shared credential-read guard; native image routing guarded by file-safety policy; unified image-source resolver + terminal-backend confinement ( [#58709](https://github.com/NousResearch/hermes-agent/pull/58709), [#58752](https://github.com/NousResearch/hermes-agent/pull/58752), [#57890](https://github.com/NousResearch/hermes-agent/pull/57890) — [@teknium1](https://github.com/teknium1))
- Webhook body-cap sweep: explicit `client_max_size` on 3 uncapped aiohttp servers + completion sweep; Raft chunked-request body limit; timestamp-bound V2 webhook signatures ( [#59180](https://github.com/NousResearch/hermes-agent/pull/59180), [#59215](https://github.com/NousResearch/hermes-agent/pull/59215), [#58902](https://github.com/NousResearch/hermes-agent/pull/58902), [#58508](https://github.com/NousResearch/hermes-agent/pull/58508) — [@teknium1](https://github.com/teknium1), [@srojk34](https://github.com/srojk34))
- Redaction: Fireworks token prefixes + Telegram transport errors; env-lookup false positives fixed for KEY=value and JSON/YAML config fields; bot tokens scrubbed from Telegram connect/send errors ( [#58501](https://github.com/NousResearch/hermes-agent/pull/58501), [#58534](https://github.com/NousResearch/hermes-agent/pull/58534), [#58915](https://github.com/NousResearch/hermes-agent/pull/58915), [#58893](https://github.com/NousResearch/hermes-agent/pull/58893) — [@teknium1](https://github.com/teknium1))
- computer-use: subprocess env sanitized across all five cua-driver spawn sites ( [#58889](https://github.com/NousResearch/hermes-agent/pull/58889), [#59165](https://github.com/NousResearch/hermes-agent/pull/59165) — [@teknium1](https://github.com/teknium1))
- Dashboard: managed-files credential guard widened past .env + dir-tree gap closed; OAuth token TOCTOU closed with atomic 0o600 writes; stale dashboards can't recreate deleted profiles ( [#58222](https://github.com/NousResearch/hermes-agent/pull/58222) — [@kshitijk4poor](https://github.com/kshitijk4poor), [#60236](https://github.com/NousResearch/hermes-agent/pull/60236) — [@teknium1](https://github.com/teknium1), [#49435](https://github.com/NousResearch/hermes-agent/pull/49435) — [@LeonSGP43](https://github.com/LeonSGP43))
- CI: untrusted refs passed through env, not `run:` interpolation; JS/TS tests wired into CI with source-regex tests banned; js-autofix pushes via PR instead of direct-to-main ( [#57842](https://github.com/NousResearch/hermes-agent/pull/57842) — [@jquesnelle](https://github.com/jquesnelle), [#60707](https://github.com/NousResearch/hermes-agent/pull/60707), [#65186](https://github.com/NousResearch/hermes-agent/pull/65186) — [@ethernet8023](https://github.com/ethernet8023))
- Docker: terminal network toggle with full-path coverage; Git Bash Mandatory-ASLR install failures detected; Windows updater console hidden during handoff ( [#59149](https://github.com/NousResearch/hermes-agent/pull/59149) — [@teknium1](https://github.com/teknium1), [#64651](https://github.com/NousResearch/hermes-agent/pull/64651), [#66040](https://github.com/NousResearch/hermes-agent/pull/66040) — [@helix4u](https://github.com/helix4u))
- Anthropic: request-local clients so the stale/interrupt watchdog never corrupts SQLite; per-profile OAuth file; OAuth login 429 fixed (UA must not be claude-code/) ( [#67238](https://github.com/NousResearch/hermes-agent/pull/67238) — [@OutThisLife](https://github.com/OutThisLife), [#59339](https://github.com/NousResearch/hermes-agent/pull/59339), [#58178](https://github.com/NousResearch/hermes-agent/pull/58178) — [@teknium1](https://github.com/teknium1))
- Gateway/agent: tool\_call\_id deduplicated across pre-API sanitizers; background review inherits parent reasoning\_config for Anthropic cache parity; `/new` memory extraction moved off the command path ( [#58350](https://github.com/NousResearch/hermes-agent/pull/58350), [#64379](https://github.com/NousResearch/hermes-agent/pull/64379), [#61139](https://github.com/NousResearch/hermes-agent/pull/61139) — [@teknium1](https://github.com/teknium1), [@kshitijk4poor](https://github.com/kshitijk4poor))

## 🔁 Reverted in this window (for the record)

- iron-proxy credential-injection egress firewall ( [#30179](https://github.com/NousResearch/hermes-agent/pull/30179) → reverted in [#58489](https://github.com/NousResearch/hermes-agent/pull/58489)) — not shipping in this release
- dynamic-workflow orchestration skill (landed, then reverted) — not shipping
- memory provider-actions extension point (landed, then reverted) — not shipping
- Note: the plugin `pre_tool_call` approve escalation was reverted mid-window but **re-landed** in [#60504](https://github.com/NousResearch/hermes-agent/pull/60504) and ships in this release.

## 👥 Contributors

**450+ people** contributed to this release (via commits, co-author trailers, and salvaged PRs) — the biggest contributor window yet. Thank you, all of you.

### Core team

- [@teknium1](https://github.com/teknium1) — release lead; TTFT perf wave, delivery + delegation durability, smart approvals, SecretSource, gateway multiplex + profile routing, sessions export, security round, and a ~290-PR community salvage burn
- [@OutThisLife](https://github.com/OutThisLife) — desktop app (the speed wave, layout-tree shell, Capabilities page, session colors, vibe reactions, TUI incremental markdown, perf harness)
- [@kshitijk4poor](https://github.com/kshitijk4poor) — GPT-5.6 end-to-end, DeepInfra + Upstage Solar providers, perf cluster, compression integrity, mem0, dashboard guards
- [@ethernet8023](https://github.com/ethernet8023) — CI overhaul (JS/TS tests wired in, autofix-via-PR, python speedups), desktop keybinds/worktrees/status indicators, full desktop TypeScript conversion
- [@benbarclay](https://github.com/benbarclay) — relay OIDC provisioning, gateway multiplex override, Nous auth self-heal, hosted MCP OAuth groundwork
- [@alt-glitch](https://github.com/alt-glitch) — terminal billing (`/subscription`, `/topup`), desktop billing tab
- [@helix4u](https://github.com/helix4u) — desktop provider/model UX, TUI model picker refresh, Windows install/updater hardening
- [@austinpickett](https://github.com/austinpickett) — desktop custom endpoint settings
- [@SHL0MS](https://github.com/SHL0MS) — unbroker + unreal-mcp skills, humanizer expansion

### Top community contributors

- [@srojk34](https://github.com/srojk34) — security hardening: Vertex credential/project/region scoping through the profile secret scope, subprocess env stripping, Raft chunked-request body limits
- [@HexLab98](https://github.com/HexLab98) — 11 fixes across MCP capability gating, Windows installer PATH, desktop cron editing, gateway systemd warnings
- [@UnathiCodex](https://github.com/UnathiCodex) — desktop stability: zoom across display moves, LaTeX rendering, resume-stall and runtime-readiness fixes
- [@xxxigm](https://github.com/xxxigm) — `<think>` leak fix after thinking-only retry flush, dashboard auth/theme/PTY fixes
- [@erosika](https://github.com/erosika) — desktop declarative memory-provider panel + honcho recall/timeout correctness
- [@Frowtek](https://github.com/Frowtek) — credential security: master stores never mounted into skill sandboxes, live-transcript redaction, dashboard api\_key precedence
- [@necoweb3](https://github.com/necoweb3) — browser private-page CDP guard, cron one-shot liveness, gateway compression fail-closed
- [@DavidMetcalfe](https://github.com/DavidMetcalfe) — desktop updater version pill, Local/custom endpoint exposure, sidebar collapse behavior
- [@shannonsands](https://github.com/shannonsands) — dashboard: mobile channel setup, Discord toolsets from web UI, Telegram setup clarity
- [@vishal-dharm](https://github.com/vishal-dharm) — Gemini request-context improvements
- [@PRATHAMESH75](https://github.com/PRATHAMESH75) — cron one-shot stale-removal race, dashboard multiplex port-binding guard
- [@alelpoan](https://github.com/alelpoan), [@embwl0x](https://github.com/embwl0x), [@Adolanium](https://github.com/Adolanium), [@giggling-ginger](https://github.com/giggling-ginger), [@Drexuxux](https://github.com/Drexuxux), [@frizikk](https://github.com/frizikk), [@JoaoMarcos44](https://github.com/JoaoMarcos44), @wesleysimplici, [@LeonSGP43](https://github.com/LeonSGP43), [@pierrenode](https://github.com/pierrenode), [@simpolism](https://github.com/simpolism), [@MorAlekss](https://github.com/MorAlekss), [@r266-tech](https://github.com/r266-tech), [@WadydX](https://github.com/WadydX), [@nv-kasikritc](https://github.com/nv-kasikritc) — targeted fixes across desktop, TUI, gateway, cron, webhook, nix, and browser surfaces
- Salvaged-work authors whose PRs were cherry-picked with credit this window: [@Burgunthy](https://github.com/Burgunthy) (profile routing), [@web3blind](https://github.com/web3blind) (sessions export), [@hwrdprkns](https://github.com/hwrdprkns) (1Password), [@Christopher-Schulze](https://github.com/Christopher-Schulze), [@Ahmett101](https://github.com/Ahmett101), [@sjiangtao2024](https://github.com/sjiangtao2024), and many more — see the salvage PR bodies for full attribution

### All contributors

[@0-CYBERDYNE-SYSTEMS-0](https://github.com/0-CYBERDYNE-SYSTEMS-0), [@0disoft](https://github.com/0disoft), [@0xbyt4](https://github.com/0xbyt4), [@100yenadmin](https://github.com/100yenadmin), [@17324393074](https://github.com/17324393074), [@2751738943](https://github.com/2751738943), [@8294](https://github.com/8294), [@abhibansal-sg](https://github.com/abhibansal-sg),

[@adambiggs](https://github.com/adambiggs), [@Adolanium](https://github.com/Adolanium), [@aeyeopsdev](https://github.com/aeyeopsdev), [@aguung](https://github.com/aguung), [@AhmetArif0](https://github.com/AhmetArif0), [@Ahmett101](https://github.com/Ahmett101), [@ai-ag2026](https://github.com/ai-ag2026), [@AIalliAI](https://github.com/AIalliAI), [@ajzrva-sys](https://github.com/ajzrva-sys),

[@alastraz](https://github.com/alastraz), [@alelpoan](https://github.com/alelpoan), [@alex-fireworks](https://github.com/alex-fireworks), [@alex-heritier](https://github.com/alex-heritier), [@alex107ivanov](https://github.com/alex107ivanov), [@AlexFucuson9](https://github.com/AlexFucuson9), [@Alix-007](https://github.com/Alix-007),

[@allenliang2022](https://github.com/allenliang2022), [@Almurat123](https://github.com/Almurat123), [@AlsayedHoota](https://github.com/AlsayedHoota), [@alt-glitch](https://github.com/alt-glitch), [@alvarosanchez](https://github.com/alvarosanchez), [@amanning3390](https://github.com/amanning3390), [@AmAzing129](https://github.com/AmAzing129),

[@AndreasHiltner](https://github.com/AndreasHiltner), [@andrewhomeyer](https://github.com/andrewhomeyer), [@annguyenNous](https://github.com/annguyenNous), [@ansel-f](https://github.com/ansel-f), [@antydizajn](https://github.com/antydizajn), [@arminanton](https://github.com/arminanton), [@arnispiekus](https://github.com/arnispiekus), [@asimons81](https://github.com/asimons81),

[@asscan](https://github.com/asscan), [@ats3v](https://github.com/ats3v), [@austinlaw076](https://github.com/austinlaw076), [@austinpickett](https://github.com/austinpickett), [@avifenesh](https://github.com/avifenesh), [@aydnOktay](https://github.com/aydnOktay), [@Bartok9](https://github.com/Bartok9), [@bautrey](https://github.com/bautrey), [@bbednarski9](https://github.com/bbednarski9),

[@bbopen](https://github.com/bbopen), [@benbarclay](https://github.com/benbarclay), [@bigstar0920](https://github.com/bigstar0920), [@binhnt92](https://github.com/binhnt92), [@bird](https://github.com/bird), [@Black0Fox0](https://github.com/Black0Fox0), [@BlackishGreen33](https://github.com/BlackishGreen33), @bo.fu, [@brendandebeasi](https://github.com/brendandebeasi),

[@briandevans](https://github.com/briandevans), [@BROCCOLO1D](https://github.com/BROCCOLO1D), [@Bruce-anle](https://github.com/Bruce-anle), [@brunz-me](https://github.com/brunz-me), [@Burgunthy](https://github.com/Burgunthy), [@bytesnail](https://github.com/bytesnail), [@catbearlove1-lang](https://github.com/catbearlove1-lang), [@Cdddo](https://github.com/Cdddo),

[@cgarwood82](https://github.com/cgarwood82), [@CharmingGroot](https://github.com/CharmingGroot), [@chouqin](https://github.com/chouqin), [@Christopher-Schulze](https://github.com/Christopher-Schulze), [@claudlos](https://github.com/claudlos), [@CocaKova](https://github.com/CocaKova), [@Code-suphub](https://github.com/Code-suphub), [@CodeForgeNet](https://github.com/CodeForgeNet),

[@craigdfrench](https://github.com/craigdfrench), [@CrazyBoyM](https://github.com/CrazyBoyM), [@crazywriter1](https://github.com/crazywriter1), [@cresslank](https://github.com/cresslank), [@cruzanstx](https://github.com/cruzanstx), [@cyrkstudios](https://github.com/cyrkstudios), [@danilofalcao](https://github.com/danilofalcao),

[@datachainsystems](https://github.com/datachainsystems), [@DatTheMaster](https://github.com/DatTheMaster), [@davidb73-hub](https://github.com/davidb73-hub), [@davidgut1982](https://github.com/davidgut1982), [@DavidMetcalfe](https://github.com/DavidMetcalfe), [@davidrobertson](https://github.com/davidrobertson),

[@deacon-botdoctor](https://github.com/deacon-botdoctor), [@DECK6](https://github.com/DECK6), [@deepujain](https://github.com/deepujain), [@derek2000139](https://github.com/derek2000139), [@designnotdrum](https://github.com/designnotdrum), [@deusyu](https://github.com/deusyu), [@devatnull](https://github.com/devatnull), [@devorun](https://github.com/devorun),

[@dexhunter](https://github.com/dexhunter), [@dfein38347g](https://github.com/dfein38347g), [@Dhravya](https://github.com/Dhravya), [@DictatorBacon](https://github.com/DictatorBacon), [@digitalbase](https://github.com/digitalbase), [@dlkakbs](https://github.com/dlkakbs), [@dmabry](https://github.com/dmabry), [@DNAlec](https://github.com/DNAlec), [@dodo-reach](https://github.com/dodo-reach),

[@doncazper](https://github.com/doncazper), [@dorokuma](https://github.com/dorokuma), [@doxe0x](https://github.com/doxe0x), [@Drexuxux](https://github.com/Drexuxux), [@dschnurbusch](https://github.com/dschnurbusch), [@Dusk1e](https://github.com/Dusk1e), [@EdderTalmor](https://github.com/EdderTalmor), [@egilewski](https://github.com/egilewski), [@elashera](https://github.com/elashera),

[@Elektrofussel](https://github.com/Elektrofussel), [@eliteworkstation94-ai](https://github.com/eliteworkstation94-ai), [@embwl0x](https://github.com/embwl0x), [@emo-eth](https://github.com/emo-eth), [@emozilla](https://github.com/emozilla), [@enzo-adami](https://github.com/enzo-adami), [@Epoxidex](https://github.com/Epoxidex), [@ErnestHysa](https://github.com/ErnestHysa),

[@erosika](https://github.com/erosika), [@esthonjr](https://github.com/esthonjr), [@ethernet8023](https://github.com/ethernet8023), [@evefromwayback](https://github.com/evefromwayback), @evelynburger, [@F4TB0Yz](https://github.com/F4TB0Yz), [@falkoro](https://github.com/falkoro), [@fanyangCS](https://github.com/fanyangCS), [@firefly](https://github.com/firefly),

[@fjlaowan1983](https://github.com/fjlaowan1983), [@flewe](https://github.com/flewe), [@flo1t](https://github.com/flo1t), [@flow-digital-ny](https://github.com/flow-digital-ny), [@floze-the-genius](https://github.com/floze-the-genius), [@frizikk](https://github.com/frizikk), [@Frowtek](https://github.com/Frowtek), [@FuryMartin](https://github.com/FuryMartin),

[@fyzanshaik](https://github.com/fyzanshaik), [@gauravsaxena1997](https://github.com/gauravsaxena1997), [@geoffreybutler94](https://github.com/geoffreybutler94), [@georgedrury](https://github.com/georgedrury), [@gigakun3030](https://github.com/gigakun3030), [@giggling-ginger](https://github.com/giggling-ginger),

[@Git-on-my-level](https://github.com/Git-on-my-level), [@gitcommit90](https://github.com/gitcommit90), [@githubespresso407](https://github.com/githubespresso407), [@gnodet](https://github.com/gnodet), [@GottZ](https://github.com/GottZ), [@Gridzilla](https://github.com/Gridzilla), @grimmjoww578, [@gumclaw](https://github.com/gumclaw),

[@Gutslabs](https://github.com/Gutslabs), [@HaiderSultanArc](https://github.com/HaiderSultanArc), [@harjothkhara](https://github.com/harjothkhara), [@heathley](https://github.com/heathley), [@hejuntt1014](https://github.com/hejuntt1014), [@helix4u](https://github.com/helix4u), [@HeLLGURD](https://github.com/HeLLGURD), [@hellno](https://github.com/hellno),

[@herbalizer404](https://github.com/herbalizer404), [@HexLab98](https://github.com/HexLab98), [@hmirin](https://github.com/hmirin), [@Hopfensaft](https://github.com/Hopfensaft), [@Hotragn](https://github.com/Hotragn), [@hsy5571616](https://github.com/hsy5571616), [@huanshan5195](https://github.com/huanshan5195), [@HumphreySun98](https://github.com/HumphreySun98),

[@hwrdprkns](https://github.com/hwrdprkns), [@hydracoco7](https://github.com/hydracoco7), [@hydraxman](https://github.com/hydraxman), [@iamlukethedev](https://github.com/iamlukethedev), [@iborazzi](https://github.com/iborazzi), [@IgorGanapolsky](https://github.com/IgorGanapolsky), [@iizotov](https://github.com/iizotov), [@ildunari](https://github.com/ildunari),

[@infinitycrew39](https://github.com/infinitycrew39), [@IpastorSan](https://github.com/IpastorSan), @irresi, @isfttr, @isheng-eqi, @itsflownium, @izumi0uu, @Jaaneek, @JacketPants,

@jaisup, @jakelongvu-bot, @jakepresent, @jaketracey, @JAlmanzarMint, @JasonFang1993, @jbbottoms, @jcjc81,

@JiaDe-Wu, @Jiahui-Gu, @Jigoooo, @jingsong-liu, @jneeee, [@JoaoMarcos44](https://github.com/JoaoMarcos44), @joelbrilliant, @John-Lussier, @jplew,

@jtstothard, @juniperbevensee, @Jupiter363, @justinschille, @k4z4n0v4, @kaishi00, @karfly, @kartik-mem0,

@kavioavio, @KCAYAAI, @kenyonxu, @keslerm, @kevinrajaram, @knoal, @kocaemre, @kohoj, @konsisumer, @krowd3v,

[@kshitijk4poor](https://github.com/kshitijk4poor), @kuangmi-bit, @kubolko, @kyssta-exe, @Kyzcreig, @l0h1nth, @labsobsidian, @laurinaitis,

@LavyaTandel, @lawyer112, @lemonwan, [@LeonSGP43](https://github.com/LeonSGP43), @lEWFkRAD, @linfeng961, @liuhao1024, @liuwei666888, @ljy-2000,

@loes5050, @logical-and, @LoicHmh, @loongfay, @lord-dubious, @lost9999, @lucasfdale, @lucaskvasirr,

@luxuguang-leo, @ly-wang19, @m0n5t3r, @m1qaweb, @M1racleShih, @MaartenDMT, @mahdiwafy, @MaheshBhushan,

@ManniBr, @marcelohildebrand, @marcolivierlavoie, @markoub, @MarkVLK, @Marxb85, @matantsevs,

@maxpetrusenkoagent, @mbac, @mdc2122, @mguttmann, @Mibayy, @michaelHMK, @mijanx, @minchang, @momomojo,

[@MorAlekss](https://github.com/MorAlekss), @morluto, @msh01, @mssteuer, @mvanhorn, @nanami7777777, @nankingjing, [@necoweb3](https://github.com/necoweb3), @neo-claw-bot,

@neoguyverx, @nicha16, @nikshepsvn, @nima20002000, @nnnet, @NousResearch, @nullptr0807, [@nv-kasikritc](https://github.com/nv-kasikritc),

@okisdev, @OmarB97, @ooiuuii, @ooovenenoso, @oppih, @Osraka, @ostravajih, @otsune, [@OutThisLife](https://github.com/OutThisLife), @OYLFLMH,

@patrick-muller, @pdmartins, @pedrommaiaa, @Peterskaronis, @petrichor-op, @pgregg88, [@pierrenode](https://github.com/pierrenode), @pixel4039,

@plcunha, @pnascimento9596, @Polyhistor, [@PRATHAMESH75](https://github.com/PRATHAMESH75), @professorpalmer, @Punyko8, @Que0x, @Qwinty,

@r0gersm1th, [@r266-tech](https://github.com/r266-tech), @rabadaki, @ragingbulld, @RainbowAndSun, @rainbowgore, @randimt, @rarf, @rasitakyol,

@rayjun, @raymondyan-zhijie, @re-ITRT, @RenoMG, @Rival, @RKelln, @rlaehddus302, [@rob-maron](https://github.com/rob-maron), @rodboev,

@roryford, @rungmc357, @ruslanvasylev, @s0xn1ck, @s905060, @s96919, @sahibzada-allahyar, @sahil-shubham,

@Sahil-SS9, @SahilRakhaiya05, @sam7894604, @SAMBAS123, @samrusani, @sanidhyasin, @sasquatch9818, @sberan,

@ScotterMonk, @seagpt, @sebastianlutycz, @SemonCat, @setclock, [@shannonsands](https://github.com/shannonsands), @sharziki, @shashwatgokhe,

[@SHL0MS](https://github.com/SHL0MS), @shuangxinniao, @SilentKnight87, @simplast, [@simpolism](https://github.com/simpolism), @SiteupAgencia, [@sjiangtao2024](https://github.com/sjiangtao2024), @sk-holmes,

@slow4cyl, @smtony, @soddy022, @Soju06, @solyanviktor-star, @SongotenU, @spiky02plateau, @sprmn24, @SquabbyZ,

[@srojk34](https://github.com/srojk34), @ssiweifnag, @stantheman0128, @StellarisW, @stephenschoettler, @suninrain086, @superposition,

@Supersynergy, @sweetcornna, @szafranski, @tanmayxchoudhary, @tarunravi, @tcconnally, @terry197913, @Thatgfsj,

@thegoodguysla, @thestudionorth, @TheTom, @TinkerOfThings, @tjboudreaux, @tjp2021, @Tortugasaur, @Tosko4,

@Tranquil-Flow, @trevorgordon981, @trismegistus-wanderer, @tt-a1i, @tuancookiez-hub, @TurgutKural, @Umi4Life,

[@UnathiCodex](https://github.com/UnathiCodex), @unsupportedpastels, @uzaylisak, @valda, @vampyren, @veradim, @victor-kyriazakos, @virtualex-itv,

[@vishal-dharm](https://github.com/vishal-dharm), @Vissirexa, @vizi0uz, @vkkong, @vKongv, @VolodymyrBg, @vortexopenclaw, @VrtxOmega, [@WadydX](https://github.com/WadydX),

@waroffchange, @waseemshahwan, [@web3blind](https://github.com/web3blind), @webtecnica, @wesleion, @wesleysimplicio, @williamumu,

@WilsonKinyua, @wxy-nlp, @wyuebei-cloud, @x7peeps, @x9x9x9x9x9x91, @xuezhaolan, [@xxxigm](https://github.com/xxxigm), @ya-nsh, @yatesjalex,

@ygd58, @yingliang-zhang, @yinkev, @YLChen-007, @yu-xin-c, @yungchentang, @zapabob, @zccyman, @zeapsu,

@ziliangpeng, @zwcf5200, @zzpigpinggai

Also: bo.fu, Paulo Henrique, kyssta-exe 25470058+kyssta-exe.fu, Paulo Henrique, kyssta-exe 25470058+kyssta-exe.

* * *

**Full Changelog**: [v2026.7.1...v2026.7.20](https://github.com/NousResearch/hermes-agent/compare/v2026.7.1...v2026.7.20)

### Contributors

- [![@DavidMetcalfe](https://avatars.githubusercontent.com/u/80915?s=64&v=4)](https://github.com/DavidMetcalfe)
- [![@gnodet](https://avatars.githubusercontent.com/u/84022?s=64&v=4)](https://github.com/gnodet)
- [![@hwrdprkns](https://avatars.githubusercontent.com/u/120890?s=64&v=4)](https://github.com/hwrdprkns)
- [![@alvarosanchez](https://avatars.githubusercontent.com/u/153880?s=64&v=4)](https://github.com/alvarosanchez)
- [![@IgorGanapolsky](https://avatars.githubusercontent.com/u/201209?s=64&v=4)](https://github.com/IgorGanapolsky)
- [![@austinpickett](https://avatars.githubusercontent.com/u/260188?s=64&v=4)](https://github.com/austinpickett)
- [![@deepujain](https://avatars.githubusercontent.com/u/406777?s=64&v=4)](https://github.com/deepujain)
- [![@benbarclay](https://avatars.githubusercontent.com/u/413810?s=64&v=4)](https://github.com/benbarclay)
- [![@GottZ](https://avatars.githubusercontent.com/u/559564?s=64&v=4)](https://github.com/GottZ)
- [![@alex-heritier](https://avatars.githubusercontent.com/u/635304?s=64&v=4)](https://github.com/alex-heritier)
- [![@ethernet8023](https://avatars.githubusercontent.com/u/666465?s=64&v=4)](https://github.com/ethernet8023)
- [![@hellno](https://avatars.githubusercontent.com/u/686075?s=64&v=4)](https://github.com/hellno)
- [![@jquesnelle](https://avatars.githubusercontent.com/u/687076?s=64&v=4)](https://github.com/jquesnelle)
- [![@emozilla](https://avatars.githubusercontent.com/u/693905?s=64&v=4)](https://github.com/emozilla)
- [![@OutThisLife](https://avatars.githubusercontent.com/u/770929?s=64&v=4)](https://github.com/OutThisLife)
- [![@digitalbase](https://avatars.githubusercontent.com/u/849282?s=64&v=4)](https://github.com/digitalbase)
- [![@adambiggs](https://avatars.githubusercontent.com/u/857229?s=64&v=4)](https://github.com/adambiggs)
- [![@egilewski](https://avatars.githubusercontent.com/u/1078345?s=64&v=4)](https://github.com/egilewski)
- [![@georgedrury](https://avatars.githubusercontent.com/u/1198104?s=64&v=4)](https://github.com/georgedrury)
- [![@cgarwood82](https://avatars.githubusercontent.com/u/1246285?s=64&v=4)](https://github.com/cgarwood82)
- [![@hmirin](https://avatars.githubusercontent.com/u/1284876?s=64&v=4)](https://github.com/hmirin)
- [![@chouqin](https://avatars.githubusercontent.com/u/1285855?s=64&v=4)](https://github.com/chouqin)
- [![@ats3v](https://avatars.githubusercontent.com/u/1550392?s=64&v=4)](https://github.com/ats3v)
- [![@designnotdrum](https://avatars.githubusercontent.com/u/1751018?s=64&v=4)](https://github.com/designnotdrum)
- [![@bbopen](https://avatars.githubusercontent.com/u/1772563?s=64&v=4)](https://github.com/bbopen)
- [![@brendandebeasi](https://avatars.githubusercontent.com/u/1968286?s=64&v=4)](https://github.com/brendandebeasi)
- [![@cruzanstx](https://avatars.githubusercontent.com/u/2927083?s=64&v=4)](https://github.com/cruzanstx)
- [![@helix4u](https://avatars.githubusercontent.com/u/4317663?s=64&v=4)](https://github.com/helix4u)
- [![@danilofalcao](https://avatars.githubusercontent.com/u/4456855?s=64&v=4)](https://github.com/danilofalcao)
- [![@Gridzilla](https://avatars.githubusercontent.com/u/4488015?s=64&v=4)](https://github.com/Gridzilla)
- [![@frizikk](https://avatars.githubusercontent.com/u/4850809?s=64&v=4)](https://github.com/frizikk)
- [![@dmabry](https://avatars.githubusercontent.com/u/5330413?s=64&v=4)](https://github.com/dmabry)
- [![@bautrey](https://avatars.githubusercontent.com/u/5750806?s=64&v=4)](https://github.com/bautrey)
- [![@fanyangCS](https://avatars.githubusercontent.com/u/5820832?s=64&v=4)](https://github.com/fanyangCS)
- [![@davidgut1982](https://avatars.githubusercontent.com/u/5985783?s=64&v=4)](https://github.com/davidgut1982)
- [![@emo-eth](https://avatars.githubusercontent.com/u/6371847?s=64&v=4)](https://github.com/emo-eth)
- [![@bird](https://avatars.githubusercontent.com/u/6666242?s=64&v=4)](https://github.com/bird)
- [![@dexhunter](https://avatars.githubusercontent.com/u/6930518?s=64&v=4)](https://github.com/dexhunter)
- [![@iizotov](https://avatars.githubusercontent.com/u/7712335?s=64&v=4)](https://github.com/iizotov)
- [![@shannonsands](https://avatars.githubusercontent.com/u/7897813?s=64&v=4)](https://github.com/shannonsands)
- [![@herbalizer404](https://avatars.githubusercontent.com/u/8180647?s=64&v=4)](https://github.com/herbalizer404)
- [![@davidrobertson](https://avatars.githubusercontent.com/u/8311486?s=64&v=4)](https://github.com/davidrobertson)
- [![@hydraxman](https://avatars.githubusercontent.com/u/8344245?s=64&v=4)](https://github.com/hydraxman)
- [![@HexLab98](https://avatars.githubusercontent.com/u/8422520?s=64&v=4)](https://github.com/HexLab98)
- [![@cresslank](https://avatars.githubusercontent.com/u/9219265?s=64&v=4)](https://github.com/cresslank)
- [![@Git-on-my-level](https://avatars.githubusercontent.com/u/9387252?s=64&v=4)](https://github.com/Git-on-my-level)
- [![@bbednarski9](https://avatars.githubusercontent.com/u/16690530?s=64&v=4)](https://github.com/bbednarski9)
- [![@dorokuma](https://avatars.githubusercontent.com/u/18098088?s=64&v=4)](https://github.com/dorokuma)
- [![@fyzanshaik](https://avatars.githubusercontent.com/u/18377922?s=64&v=4)](https://github.com/fyzanshaik)
- [![@craigdfrench](https://avatars.githubusercontent.com/u/18516125?s=64&v=4)](https://github.com/craigdfrench)
- [![@hejuntt1014](https://avatars.githubusercontent.com/u/19259565?s=64&v=4)](https://github.com/hejuntt1014)
- [![@bytesnail](https://avatars.githubusercontent.com/u/22556004?s=64&v=4)](https://github.com/bytesnail)
- [![@Hopfensaft](https://avatars.githubusercontent.com/u/24845938?s=64&v=4)](https://github.com/Hopfensaft)
- [![@aguung](https://avatars.githubusercontent.com/u/26564966?s=64&v=4)](https://github.com/aguung)
- [![@DictatorBacon](https://avatars.githubusercontent.com/u/28026990?s=64&v=4)](https://github.com/DictatorBacon)
- [![@arminanton](https://avatars.githubusercontent.com/u/29869547?s=64&v=4)](https://github.com/arminanton)
- [![@firefly](https://avatars.githubusercontent.com/u/29965648?s=64&v=4)](https://github.com/firefly)
- [![@alex107ivanov](https://avatars.githubusercontent.com/u/30668368?s=64&v=4)](https://github.com/alex107ivanov)
- [![@esthonjr](https://avatars.githubusercontent.com/u/31424689?s=64&v=4)](https://github.com/esthonjr)
- [![@simpolism](https://avatars.githubusercontent.com/u/32201324?s=64&v=4)](https://github.com/simpolism)
- [![@flo1t](https://avatars.githubusercontent.com/u/32957276?s=64&v=4)](https://github.com/flo1t)
- [![@gauravsaxena1997](https://avatars.githubusercontent.com/u/32961153?s=64&v=4)](https://github.com/gauravsaxena1997)
- [![@8294](https://avatars.githubusercontent.com/u/34885521?s=64&v=4)](https://github.com/8294)
- [![@CrazyBoyM](https://avatars.githubusercontent.com/u/35400185?s=64&v=4)](https://github.com/CrazyBoyM)
- [![@0xbyt4](https://avatars.githubusercontent.com/u/35742124?s=64&v=4)](https://github.com/0xbyt4)
- [![@brunz-me](https://avatars.githubusercontent.com/u/36083598?s=64&v=4)](https://github.com/brunz-me)
- [![@falkoro](https://avatars.githubusercontent.com/u/39274208?s=64&v=4)](https://github.com/falkoro)
- [![@bigstar0920](https://avatars.githubusercontent.com/u/40700577?s=64&v=4)](https://github.com/bigstar0920)
- [![@FuryMartin](https://avatars.githubusercontent.com/u/41051953?s=64&v=4)](https://github.com/FuryMartin)
- [![@2751738943](https://avatars.githubusercontent.com/u/41409874?s=64&v=4)](https://github.com/2751738943)
- [![@alastraz](https://avatars.githubusercontent.com/u/42220940?s=64&v=4)](https://github.com/alastraz)
- [![@deusyu](https://avatars.githubusercontent.com/u/42929363?s=64&v=4)](https://github.com/deusyu)
- [![@EdderTalmor](https://avatars.githubusercontent.com/u/45949729?s=64&v=4)](https://github.com/EdderTalmor)
- [![@harjothkhara](https://avatars.githubusercontent.com/u/48686985?s=64&v=4)](https://github.com/harjothkhara)
- [![@Cdddo](https://avatars.githubusercontent.com/u/48868528?s=64&v=4)](https://github.com/Cdddo)
- [![@alt-glitch](https://avatars.githubusercontent.com/u/52913345?s=64&v=4)](https://github.com/alt-glitch)
- [![@crazywriter1](https://avatars.githubusercontent.com/u/53251494?s=64&v=4)](https://github.com/crazywriter1)
- [![@IpastorSan](https://avatars.githubusercontent.com/u/54788305?s=64&v=4)](https://github.com/IpastorSan)
- [![@xxxigm](https://avatars.githubusercontent.com/u/54813621?s=64&v=4)](https://github.com/xxxigm)
- [![@avifenesh](https://avatars.githubusercontent.com/u/55848801?s=64&v=4)](https://github.com/avifenesh)
- [![@erosika](https://avatars.githubusercontent.com/u/56565191?s=64&v=4)](https://github.com/erosika)
- [![@asscan](https://avatars.githubusercontent.com/u/57783184?s=64&v=4)](https://github.com/asscan)
- [![@HaiderSultanArc](https://avatars.githubusercontent.com/u/59045242?s=64&v=4)](https://github.com/HaiderSultanArc)
- [![@devatnull](https://avatars.githubusercontent.com/u/59279509?s=64&v=4)](https://github.com/devatnull)
- [![@DNAlec](https://avatars.githubusercontent.com/u/59696621?s=64&v=4)](https://github.com/DNAlec)
- [![@ErnestHysa](https://avatars.githubusercontent.com/u/59969602?s=64&v=4)](https://github.com/ErnestHysa)
- [![@vishal-dharm](https://avatars.githubusercontent.com/u/61256217?s=64&v=4)](https://github.com/vishal-dharm)
- [![@Dhravya](https://avatars.githubusercontent.com/u/63950637?s=64&v=4)](https://github.com/Dhravya)
- [![@WadydX](https://avatars.githubusercontent.com/u/65117428?s=64&v=4)](https://github.com/WadydX)
- [![@necoweb3](https://avatars.githubusercontent.com/u/65560494?s=64&v=4)](https://github.com/necoweb3)
- [![@derek2000139](https://avatars.githubusercontent.com/u/69230769?s=64&v=4)](https://github.com/derek2000139)
- [![@CharmingGroot](https://avatars.githubusercontent.com/u/70020572?s=64&v=4)](https://github.com/CharmingGroot)
- [![@17324393074](https://avatars.githubusercontent.com/u/70047132?s=64&v=4)](https://github.com/17324393074)
- [![@Burgunthy](https://avatars.githubusercontent.com/u/71678854?s=64&v=4)](https://github.com/Burgunthy)
- [![@AlsayedHoota](https://avatars.githubusercontent.com/u/78100282?s=64&v=4)](https://github.com/AlsayedHoota)
- [![@Code-suphub](https://avatars.githubusercontent.com/u/78542984?s=64&v=4)](https://github.com/Code-suphub)
- [![@dfein38347g](https://avatars.githubusercontent.com/u/79952941?s=64&v=4)](https://github.com/dfein38347g)
- [![@Elektrofussel](https://avatars.githubusercontent.com/u/80831019?s=64&v=4)](https://github.com/Elektrofussel)
- [![@kshitijk4poor](https://avatars.githubusercontent.com/u/82637225?s=64&v=4)](https://github.com/kshitijk4poor)
- [![@doxe0x](https://avatars.githubusercontent.com/u/84589100?s=64&v=4)](https://github.com/doxe0x)
- [![@binhnt92](https://avatars.githubusercontent.com/u/84617813?s=64&v=4)](https://github.com/binhnt92)
- [![@JoaoMarcos44](https://avatars.githubusercontent.com/u/87440198?s=64&v=4)](https://github.com/JoaoMarcos44)
- [![@floze-the-genius](https://avatars.githubusercontent.com/u/88098863?s=64&v=4)](https://github.com/floze-the-genius)
- [![@Adolanium](https://avatars.githubusercontent.com/u/94890352?s=64&v=4)](https://github.com/Adolanium)
- [![@ildunari](https://avatars.githubusercontent.com/u/95185577?s=64&v=4)](https://github.com/ildunari)
- [![@heathley](https://avatars.githubusercontent.com/u/96010389?s=64&v=4)](https://github.com/heathley)
- [![@CocaKova](https://avatars.githubusercontent.com/u/97927124?s=64&v=4)](https://github.com/CocaKova)
- [![@allenliang2022](https://avatars.githubusercontent.com/u/98301349?s=64&v=4)](https://github.com/allenliang2022)
- [![@0disoft](https://avatars.githubusercontent.com/u/100320863?s=64&v=4)](https://github.com/0disoft)
- [![@BlackishGreen33](https://avatars.githubusercontent.com/u/103036558?s=64&v=4)](https://github.com/BlackishGreen33)
- [![@Hotragn](https://avatars.githubusercontent.com/u/103170876?s=64&v=4)](https://github.com/Hotragn)
- [![@giggling-ginger](https://avatars.githubusercontent.com/u/110955495?s=64&v=4)](https://github.com/giggling-ginger)
- [![@MorAlekss](https://avatars.githubusercontent.com/u/111925348?s=64&v=4)](https://github.com/MorAlekss)
- [![@aydnOktay](https://avatars.githubusercontent.com/u/113846926?s=64&v=4)](https://github.com/aydnOktay)
- [![@AmAzing129](https://avatars.githubusercontent.com/u/115673583?s=64&v=4)](https://github.com/AmAzing129)
- [![@F4TB0Yz](https://avatars.githubusercontent.com/u/117155293?s=64&v=4)](https://github.com/F4TB0Yz)
- [![@PRATHAMESH75](https://avatars.githubusercontent.com/u/118293218?s=64&v=4)](https://github.com/PRATHAMESH75)
- [![@teknium1](https://avatars.githubusercontent.com/u/127238744?s=64&v=4)](https://github.com/teknium1)
- [![@Epoxidex](https://avatars.githubusercontent.com/u/128125134?s=64&v=4)](https://github.com/Epoxidex)
- [![@Gutslabs](https://avatars.githubusercontent.com/u/128259593?s=64&v=4)](https://github.com/Gutslabs)
- [![@HeLLGURD](https://avatars.githubusercontent.com/u/129007007?s=64&v=4)](https://github.com/HeLLGURD)
- [![@devorun](https://avatars.githubusercontent.com/u/130918800?s=64&v=4)](https://github.com/devorun)
- [![@SHL0MS](https://avatars.githubusercontent.com/u/131039422?s=64&v=4)](https://github.com/SHL0MS)
- [![@rob-maron](https://avatars.githubusercontent.com/u/132852777?s=64&v=4)](https://github.com/rob-maron)
- [![@0-CYBERDYNE-SYSTEMS-0](https://avatars.githubusercontent.com/u/134018026?s=64&v=4)](https://github.com/0-CYBERDYNE-SYSTEMS-0)
- [![@fjlaowan1983](https://avatars.githubusercontent.com/u/134226314?s=64&v=4)](https://github.com/fjlaowan1983)
- [![@Dusk1e](https://avatars.githubusercontent.com/u/135010814?s=64&v=4)](https://github.com/Dusk1e)
- [![@ansel-f](https://avatars.githubusercontent.com/u/135129512?s=64&v=4)](https://github.com/ansel-f)
- [![@elashera](https://avatars.githubusercontent.com/u/135239963?s=64&v=4)](https://github.com/elashera)
- [![@dschnurbusch](https://avatars.githubusercontent.com/u/135989441?s=64&v=4)](https://github.com/dschnurbusch)
- [![@dlkakbs](https://avatars.githubusercontent.com/u/140312585?s=64&v=4)](https://github.com/dlkakbs)
- [![@AhmetArif0](https://avatars.githubusercontent.com/u/147827411?s=64&v=4)](https://github.com/AhmetArif0)
- [![@hsy5571616](https://avatars.githubusercontent.com/u/147921023?s=64&v=4)](https://github.com/hsy5571616)
- [![@DECK6](https://avatars.githubusercontent.com/u/153787350?s=64&v=4)](https://github.com/DECK6)
- [![@LeonSGP43](https://avatars.githubusercontent.com/u/154585401?s=64&v=4)](https://github.com/LeonSGP43)
- [![@alelpoan](https://avatars.githubusercontent.com/u/155192176?s=64&v=4)](https://github.com/alelpoan)
- [![@githubespresso407](https://avatars.githubusercontent.com/u/159510138?s=64&v=4)](https://github.com/githubespresso407)
- [![@iborazzi](https://avatars.githubusercontent.com/u/160004724?s=64&v=4)](https://github.com/iborazzi)
- [![@sjiangtao2024](https://avatars.githubusercontent.com/u/163701970?s=64&v=4)](https://github.com/sjiangtao2024)
- [![@Frowtek](https://avatars.githubusercontent.com/u/164990034?s=64&v=4)](https://github.com/Frowtek)
- [![@CodeForgeNet](https://avatars.githubusercontent.com/u/166907114?s=64&v=4)](https://github.com/CodeForgeNet)
- [![@nv-kasikritc](https://avatars.githubusercontent.com/u/169213847?s=64&v=4)](https://github.com/nv-kasikritc)
- [![@Black0Fox0](https://avatars.githubusercontent.com/u/173621087?s=64&v=4)](https://github.com/Black0Fox0)
- [![@arnispiekus](https://avatars.githubusercontent.com/u/177274426?s=64&v=4)](https://github.com/arnispiekus)
- [![@HumphreySun98](https://avatars.githubusercontent.com/u/181440142?s=64&v=4)](https://github.com/HumphreySun98)
- [![@huanshan5195](https://avatars.githubusercontent.com/u/185774421?s=64&v=4)](https://github.com/huanshan5195)
- [![@infinitycrew39](https://avatars.githubusercontent.com/u/185955571?s=64&v=4)](https://github.com/infinitycrew39)
- [![@DatTheMaster](https://avatars.githubusercontent.com/u/199310114?s=64&v=4)](https://github.com/DatTheMaster)
- [![@hydracoco7](https://avatars.githubusercontent.com/u/203604868?s=64&v=4)](https://github.com/hydracoco7)
- [![@antydizajn](https://avatars.githubusercontent.com/u/205542118?s=64&v=4)](https://github.com/antydizajn)
- [![@austinlaw076](https://avatars.githubusercontent.com/u/208390534?s=64&v=4)](https://github.com/austinlaw076)
- [![@Christopher-Schulze](https://avatars.githubusercontent.com/u/210261288?s=64&v=4)](https://github.com/Christopher-Schulze)
- [![@Almurat123](https://avatars.githubusercontent.com/u/211291258?s=64&v=4)](https://github.com/Almurat123)
- [![@amanning3390](https://avatars.githubusercontent.com/u/214713539?s=64&v=4)](https://github.com/amanning3390)
- [![@asimons81](https://avatars.githubusercontent.com/u/214744153?s=64&v=4)](https://github.com/asimons81)
- [![@r266-tech](https://avatars.githubusercontent.com/u/233881301?s=64&v=4)](https://github.com/r266-tech)
- [![@doncazper](https://avatars.githubusercontent.com/u/234816344?s=64&v=4)](https://github.com/doncazper)
- [![@100yenadmin](https://avatars.githubusercontent.com/u/239388517?s=64&v=4)](https://github.com/100yenadmin)
- [![@iamlukethedev](https://avatars.githubusercontent.com/u/252071647?s=64&v=4)](https://github.com/iamlukethedev)
- [![@briandevans](https://avatars.githubusercontent.com/u/252620095?s=64&v=4)](https://github.com/briandevans)
- [![@andrewhomeyer](https://avatars.githubusercontent.com/u/253815949?s=64&v=4)](https://github.com/andrewhomeyer)
- [![@dodo-reach](https://avatars.githubusercontent.com/u/254021826?s=64&v=4)](https://github.com/dodo-reach)
- [![@AndreasHiltner](https://avatars.githubusercontent.com/u/257093716?s=64&v=4)](https://github.com/AndreasHiltner)
- [![@geoffreybutler94](https://avatars.githubusercontent.com/u/257877469?s=64&v=4)](https://github.com/geoffreybutler94)
- [![@Bruce-anle](https://avatars.githubusercontent.com/u/258373146?s=64&v=4)](https://github.com/Bruce-anle)
- [![@claudlos](https://avatars.githubusercontent.com/u/258678933?s=64&v=4)](https://github.com/claudlos)
- [![@davidb73-hub](https://avatars.githubusercontent.com/u/258702686?s=64&v=4)](https://github.com/davidb73-hub)
- [![@Bartok9](https://avatars.githubusercontent.com/u/259807879?s=64&v=4)](https://github.com/Bartok9)
- [![@ai-ag2026](https://avatars.githubusercontent.com/u/261867348?s=64&v=4)](https://github.com/ai-ag2026)
- [![@embwl0x](https://avatars.githubusercontent.com/u/262193448?s=64&v=4)](https://github.com/embwl0x)
- [![@enzo-adami](https://avatars.githubusercontent.com/u/262677699?s=64&v=4)](https://github.com/enzo-adami)
- [![@web3blind](https://avatars.githubusercontent.com/u/264741654?s=64&v=4)](https://github.com/web3blind)
- [![@gumclaw](https://avatars.githubusercontent.com/u/265388744?s=64&v=4)](https://github.com/gumclaw)
- [![@Alix-007](https://avatars.githubusercontent.com/u/267018309?s=64&v=4)](https://github.com/Alix-007)
- [![@abhibansal-sg](https://avatars.githubusercontent.com/u/268141382?s=64&v=4)](https://github.com/abhibansal-sg)
- [![@flewe](https://avatars.githubusercontent.com/u/272789276?s=64&v=4)](https://github.com/flewe)
- [![@aeyeopsdev](https://avatars.githubusercontent.com/u/275853971?s=64&v=4)](https://github.com/aeyeopsdev)
- [![@flow-digital-ny](https://avatars.githubusercontent.com/u/277125060?s=64&v=4)](https://github.com/flow-digital-ny)
- [![@Drexuxux](https://avatars.githubusercontent.com/u/279217086?s=64&v=4)](https://github.com/Drexuxux)
- [![@BROCCOLO1D](https://avatars.githubusercontent.com/u/279959838?s=64&v=4)](https://github.com/BROCCOLO1D)
- [![@alex-fireworks](https://avatars.githubusercontent.com/u/280088690?s=64&v=4)](https://github.com/alex-fireworks)
- [![@UnathiCodex](https://avatars.githubusercontent.com/u/280341956?s=64&v=4)](https://github.com/UnathiCodex)
- [![@evefromwayback](https://avatars.githubusercontent.com/u/281777414?s=64&v=4)](https://github.com/evefromwayback)
- [![@eliteworkstation94-ai](https://avatars.githubusercontent.com/u/282919977?s=64&v=4)](https://github.com/eliteworkstation94-ai)
- [![@catbearlove1-lang](https://avatars.githubusercontent.com/u/285014256?s=64&v=4)](https://github.com/catbearlove1-lang)
- [![@annguyenNous](https://avatars.githubusercontent.com/u/285874597?s=64&v=4)](https://github.com/annguyenNous)
- [![@AIalliAI](https://avatars.githubusercontent.com/u/285906080?s=64&v=4)](https://github.com/AIalliAI)
- [![@srojk34](https://avatars.githubusercontent.com/u/286497132?s=64&v=4)](https://github.com/srojk34)
- [![@cyrkstudios](https://avatars.githubusercontent.com/u/287320462?s=64&v=4)](https://github.com/cyrkstudios)
- [![@deacon-botdoctor](https://avatars.githubusercontent.com/u/291411030?s=64&v=4)](https://github.com/deacon-botdoctor)
- [![@gitcommit90](https://avatars.githubusercontent.com/u/294273268?s=64&v=4)](https://github.com/gitcommit90)
- [![@datachainsystems](https://avatars.githubusercontent.com/u/295084420?s=64&v=4)](https://github.com/datachainsystems)
- [![@AlexFucuson9](https://avatars.githubusercontent.com/u/295703459?s=64&v=4)](https://github.com/AlexFucuson9)
- [![@Ahmett101](https://avatars.githubusercontent.com/u/297889955?s=64&v=4)](https://github.com/Ahmett101)
- [![@pierrenode](https://avatars.githubusercontent.com/u/298902573?s=64&v=4)](https://github.com/pierrenode)
- [![@gigakun3030](https://avatars.githubusercontent.com/u/299163626?s=64&v=4)](https://github.com/gigakun3030)
- [![@ajzrva-sys](https://avatars.githubusercontent.com/u/302567740?s=64&v=4)](https://github.com/ajzrva-sys)

DavidMetcalfe, gnodet, and 195 other contributors


Assets4

Loading

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/NousResearch/hermes-agent/releases/tag/v2026.7.20).

👍27oteissonniere, Dead-Abyss, DesertGun, MiracleOmokaro, M-Server-BOT, manticoreroko, Aitor42, jorden2895, muxinqi, Hash-7777, and 17 more reacted with thumbs up emoji❤️6M-Server-BOT, albari54, Project516, PostboxRetinal, FERNANDOEBR, and PRATHAMESH75 reacted with heart emoji🚀14zunami, K3V1991, alexmartinsgomes, hundehausen, ruangraung, MiracleOmokaro, manticoreroko, JakeBeresford, jemin-023, DevTarlow, and 4 more reacted with rocket emoji👀20xVespertine and GoodieHART reacted with eyes emoji

All reactions

- 👍27 reactions
- ❤️6 reactions
- 🚀14 reactions
- 👀2 reactions

44 people reacted

You can’t perform that action at this time.