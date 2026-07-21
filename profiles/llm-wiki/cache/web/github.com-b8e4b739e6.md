[Skip to content](https://github.com/langchain-ai/openwiki#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/langchain-ai/openwiki) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/langchain-ai/openwiki) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/langchain-ai/openwiki) to refresh your session.Dismiss alert

{{ message }}

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/langchain-ai/openwiki).

[langchain-ai](https://github.com/langchain-ai)/ **[openwiki](https://github.com/langchain-ai/openwiki)** Public

- [Notifications](https://github.com/login?return_to=%2Flangchain-ai%2Fopenwiki) You must be signed in to change notification settings
- [Fork\\
865](https://github.com/login?return_to=%2Flangchain-ai%2Fopenwiki)
- [Star\\
12.6k](https://github.com/login?return_to=%2Flangchain-ai%2Fopenwiki)


main

[**15** Branches](https://github.com/langchain-ai/openwiki/branches) [**8** Tags](https://github.com/langchain-ai/openwiki/tags)

[Go to Branches page](https://github.com/langchain-ai/openwiki/branches)[Go to Tags page](https://github.com/langchain-ai/openwiki/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![HwangJohn](https://avatars.githubusercontent.com/u/16890972?v=4&size=40)](https://github.com/HwangJohn)[HwangJohn](https://github.com/langchain-ai/openwiki/commits?author=HwangJohn)<br>[fix: avoid wrapping oauth urls in setup ui (](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717) [#308](https://github.com/langchain-ai/openwiki/pull/308) [)](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717)<br>Open commit detailssuccess<br>5 hours agoJul 20, 2026<br>[e2a7ca5](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717) · 5 hours agoJul 20, 2026<br>## History<br>[158 Commits](https://github.com/langchain-ai/openwiki/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/langchain-ai/openwiki/commits/main/) 158 Commits |
| [.github](https://github.com/langchain-ai/openwiki/tree/main/.github ".github") | [.github](https://github.com/langchain-ai/openwiki/tree/main/.github ".github") | [fix: restrict ~/.openwiki ACLs on Windows where chmod is a no-op (](https://github.com/langchain-ai/openwiki/commit/5b94bacd3a2408b04f8bc4e7c7bbdc3f80240b04 "fix: restrict ~/.openwiki ACLs on Windows where chmod is a no-op (#367)  * fix: restrict ~/.openwiki ACLs on Windows where chmod is a no-op  The OpenWiki home directory is created with mode 0o700 and chmod'd to 0o700 wherever it is ensured, but on Windows Node's chmod only toggles the read-only attribute - the directory holding ~/.openwiki/.env (every provider API key and OAuth refresh token in plaintext), the sqlite chat checkpoints, and raw connector dumps simply inherits whatever ACL its parent grants.  restrictDirToCurrentUser mirrors the existing 0o700 owner-only intent with icacls: grant full control to the current user and SYSTEM (by well-known SID, language-independent), inheritable so new children are covered, then remove inherited ACEs. The grant runs before the inheritance reset so a failed grant can never lock the user out, and the whole helper is best-effort (returns false, never throws) exactly like the surrounding chmod calls. No-op on non-Windows platforms.  Wired into ensureOpenWikiHome and saveOpenWikiEnv, the two places that express the 0o700 intent on the home directory.  Verified on a real Windows 11 machine: a fresh temp directory carrying a dozen inherited modify-rights ACEs was reduced to exactly NT AUTHORITY\SYSTEM and the current user with (OI)(CI)(F).  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>  * skip Trivy sarif upload on fork PRs where the token is read-only  ---------  Co-authored-by: Claude Fable 5 <noreply@anthropic.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com> Co-authored-by: Colin Francis <colin.francis@langchain.dev>") [#367](https://github.com/langchain-ai/openwiki/pull/367) [)](https://github.com/langchain-ai/openwiki/commit/5b94bacd3a2408b04f8bc4e7c7bbdc3f80240b04 "fix: restrict ~/.openwiki ACLs on Windows where chmod is a no-op (#367)  * fix: restrict ~/.openwiki ACLs on Windows where chmod is a no-op  The OpenWiki home directory is created with mode 0o700 and chmod'd to 0o700 wherever it is ensured, but on Windows Node's chmod only toggles the read-only attribute - the directory holding ~/.openwiki/.env (every provider API key and OAuth refresh token in plaintext), the sqlite chat checkpoints, and raw connector dumps simply inherits whatever ACL its parent grants.  restrictDirToCurrentUser mirrors the existing 0o700 owner-only intent with icacls: grant full control to the current user and SYSTEM (by well-known SID, language-independent), inheritable so new children are covered, then remove inherited ACEs. The grant runs before the inheritance reset so a failed grant can never lock the user out, and the whole helper is best-effort (returns false, never throws) exactly like the surrounding chmod calls. No-op on non-Windows platforms.  Wired into ensureOpenWikiHome and saveOpenWikiEnv, the two places that express the 0o700 intent on the home directory.  Verified on a real Windows 11 machine: a fresh temp directory carrying a dozen inherited modify-rights ACEs was reduced to exactly NT AUTHORITY\SYSTEM and the current user with (OI)(CI)(F).  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>  * skip Trivy sarif upload on fork PRs where the token is read-only  ---------  Co-authored-by: Claude Fable 5 <noreply@anthropic.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com> Co-authored-by: Colin Francis <colin.francis@langchain.dev>") | 9 hours agoJul 19, 2026 |
| [examples](https://github.com/langchain-ai/openwiki/tree/main/examples "examples") | [examples](https://github.com/langchain-ai/openwiki/tree/main/examples "examples") | [feat: OKF + telemetry (](https://github.com/langchain-ai/openwiki/commit/d4e94ab513ab13908c6b61346b23dc17bbd59b1f "feat: OKF + telemetry (#345)  * feat: Add support for OKF via prompting (#321)  * feat: Add support for OKF via prompting  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * feat: OKF index.md files (#323)  * feat: Add support for OKF via prompting  * feat: OKF index.md files  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * cr  * cr  * docs: document index middleware helpers  * Update src/agent/prompt.ts  * cr  * make interface  * drop unnecc type  * feat: Add OKF front matter validator (#324)  * feat: Add support for OKF via prompting  * feat: OKF index.md files  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * feat: Add OKF front matter validator  * cr  * cr  * docs: document frontmatter validator helpers  * docs: document index middleware helpers  * Update src/agent/prompt.ts  * cr  * make interface  * drop unnecc type  * cr  * cr  * interfaces  * cr  * cr  * feat: OKF update wiki skill (#339)  * feat: Add support for OKF via prompting  * feat: OKF index.md files  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * feat: Add OKF front matter validator  * cr  * cr  * docs: document frontmatter validator helpers  * docs: document index middleware helpers  * Update src/agent/prompt.ts  * cr  * make interface  * drop unnecc type  * cr  * cr  * interfaces  * cr  * feat: OKF update wiki skill  * update version  * fix: Writing skills (#351)  * fix: prompt agent to write one to two sentence desc instead of just one (#353)  * fix: Better description prompting (#354)  * fix: Better description prompting  * cr  * cr  * feat: implement cli telemetry (#325)  * feat: implement anonymous cli telemetry for run events  * lock file  * chore: bump deepagents to 1.11.0 to restore execute tool via routePrefixes fix (#357)  * ci: fix repository posture checks  * feat: Add trending repo badge to readme (#347)  * chore(deps): bump the major group with 5 updates (#348)  Bumps the major group with 5 updates:  | Package | From | To | | --- | --- | --- | | [actions/checkout](https://github.com/actions/checkout) | `4` | `7` | | [pnpm/action-setup](https://github.com/pnpm/action-setup) | `4.3.0` | `6.0.9` | | [actions/setup-node](https://github.com/actions/setup-node) | `4` | `7` | | [github/codeql-action](https://github.com/github/codeql-action) | `3` | `4` | | [peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request) | `7.0.11` | `8.1.1` |   Updates `actions/checkout` from 4 to 7 - [Release notes](https://github.com/actions/checkout/releases) - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) - [Commits](https://github.com/actions/checkout/compare/v4...v7)  Updates `pnpm/action-setup` from 4.3.0 to 6.0.9 - [Release notes](https://github.com/pnpm/action-setup/releases) - [Commits](https://github.com/pnpm/action-setup/compare/b906affcce14559ad1aafd4ab0e942779e9f58b1...0ebf47130e4866e96fce0953f49152a61190b271)  Updates `actions/setup-node` from 4 to 7 - [Release notes](https://github.com/actions/setup-node/releases) - [Commits](https://github.com/actions/setup-node/compare/v4...v7)  Updates `github/codeql-action` from 3 to 4 - [Release notes](https://github.com/github/codeql-action/releases) - [Changelog](https://github.com/github/codeql-action/blob/main/CHANGELOG.md) - [Commits](https://github.com/github/codeql-action/compare/v3...v4)  Updates `peter-evans/create-pull-request` from 7.0.11 to 8.1.1 - [Release notes](https://github.com/peter-evans/create-pull-request/releases) - [Commits](https://github.com/peter-evans/create-pull-request/compare/22a9089034f40e5a961c8808d113e2c98fb63676...5f6978faf089d4d20b00c7766989d076bb2fc7f1)  --- updated-dependencies: - dependency-name: actions/checkout   dependency-version: '7'   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: pnpm/action-setup   dependency-version: 6.0.9   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: actions/setup-node   dependency-version: '7'   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: github/codeql-action   dependency-version: '4'   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: peter-evans/create-pull-request   dependency-version: 8.1.1   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major ...  Signed-off-by: dependabot[bot] <support@github.com> Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>  * feat: add gemini (ai studio) and gemini enterprise (vertex ai) providers with vertex model-family routing (#154)  * feat: add Gemini providers and consolidate Vertex Claude into gemini-enterprise  Add two Google model providers and route the Vertex AI (now Gemini Enterprise) Model Garden through a single provider:  - `gemini` (AI Studio): Google's Gemini models via one API key (GEMINI_API_KEY). - `gemini-enterprise` (Vertex AI): keyless, ADC-authenticated provider that   routes each model ID to the right Model Garden surface — native Gemini/Gemma   over generateContent, Claude over the Anthropic Vertex SDK, and   partner/open-weight models over the OpenAI-compatible MaaS endpoint   (resolveVertexSurface / createGeminiEnterpriseModel).  This supersedes the discrete `vertex` (Claude-only) provider added in #179: `gemini-enterprise` reaches Claude on Vertex through the same AnthropicVertex construction and ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN env-neutralization, plus publisher-path stripping, so no capability is lost. The rename tracks Google's Cloud Next 2026 rebrand of Vertex AI to the Gemini Enterprise Agent Platform while keeping the unchanged underlying API surface.  Builds on #179's keyless-provider plumbing (projectEnvKey/locationEnvKey/ defaultLocation, getMissingProviderEnvKey, resolveProviderLocation, getProviderCredentialHint) and its gcp-project/gcp-location onboarding steps, which gemini-enterprise inherits — dropping #154's earlier approach of overloading apiKeyEnvKey to carry the non-secret GOOGLE_CLOUD_PROJECT.  Gemini uses disableStreaming + outputVersion \"v0\" to preserve Gemini 3.x thought signatures across multi-turn tool calls (shared GEMINI_THOUGHT_SIGNATURE_OPTIONS across both ChatGoogle surfaces).  The MaaS endpoint and the Gemini surface both special-case the `global` location: MaaS uses the unprefixed aiplatform.googleapis.com host, and the Gemini surface strips a publisher-pathed ID to the bare model the generateContent surface expects. resolveVertexSurface lists `codellama` explicitly so bare codellama-* IDs route to MaaS.  Co-Authored-By: Claude <noreply@anthropic.com>  * test: verify provider retry attempts reach the Gemini constructors  createModel now spreads ...retryOptions into every Gemini surface (the AI Studio ChatGoogle and all three gemini-enterprise clients), which previously omitted it — so OPENWIKI_PROVIDER_RETRY_ATTEMPTS was silently ignored and a 429 failed fast instead of backing off (reported by @avidspartan1 on #154).  maxRetries is not a readable property on the constructed LangChain models, so this asserts it via vi.mock capturing each constructor's options (including that maxRetries: 0 propagates and the AI Studio API key reaches ChatGoogle). Once maxRetries is wired through, @langchain/core's AsyncCaller already honors a server-provided Retry-After (up to 60s), so the existing backoff engages.  Co-Authored-By: Claude <noreply@anthropic.com>  ---------  Co-authored-by: Claude <noreply@anthropic.com>  * bump deepagents to 1.11.0 to restore execute tool via routePrefixes fix  ---------  Signed-off-by: dependabot[bot] <support@github.com> Co-authored-by: John Kennedy <65985482+jkennedyvz@users.noreply.github.com> Co-authored-by: Brace Sproul <braceasproul@gmail.com> Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> Co-authored-by: Brad Huffman <brad.huffman@wellsky.com> Co-authored-by: Claude <noreply@anthropic.com>  * fix: Better relationship prompting (#359)  * chore: Update openwiki to be OKF compliant (#355)  * chore: Update openwiki to be OKF compliant  * add index files  * cr  ---------  Signed-off-by: dependabot[bot] <support@github.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com> Co-authored-by: John Kennedy <65985482+jkennedyvz@users.noreply.github.com> Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> Co-authored-by: Brad Huffman <brad.huffman@wellsky.com> Co-authored-by: Claude <noreply@anthropic.com>") [#345](https://github.com/langchain-ai/openwiki/pull/345) [)](https://github.com/langchain-ai/openwiki/commit/d4e94ab513ab13908c6b61346b23dc17bbd59b1f "feat: OKF + telemetry (#345)  * feat: Add support for OKF via prompting (#321)  * feat: Add support for OKF via prompting  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * feat: OKF index.md files (#323)  * feat: Add support for OKF via prompting  * feat: OKF index.md files  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * cr  * cr  * docs: document index middleware helpers  * Update src/agent/prompt.ts  * cr  * make interface  * drop unnecc type  * feat: Add OKF front matter validator (#324)  * feat: Add support for OKF via prompting  * feat: OKF index.md files  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * feat: Add OKF front matter validator  * cr  * cr  * docs: document frontmatter validator helpers  * docs: document index middleware helpers  * Update src/agent/prompt.ts  * cr  * make interface  * drop unnecc type  * cr  * cr  * interfaces  * cr  * cr  * feat: OKF update wiki skill (#339)  * feat: Add support for OKF via prompting  * feat: OKF index.md files  * Apply suggestions from code review  Co-authored-by: Brace Sproul <braceasproul@gmail.com>  * cr  * feat: Add OKF front matter validator  * cr  * cr  * docs: document frontmatter validator helpers  * docs: document index middleware helpers  * Update src/agent/prompt.ts  * cr  * make interface  * drop unnecc type  * cr  * cr  * interfaces  * cr  * feat: OKF update wiki skill  * update version  * fix: Writing skills (#351)  * fix: prompt agent to write one to two sentence desc instead of just one (#353)  * fix: Better description prompting (#354)  * fix: Better description prompting  * cr  * cr  * feat: implement cli telemetry (#325)  * feat: implement anonymous cli telemetry for run events  * lock file  * chore: bump deepagents to 1.11.0 to restore execute tool via routePrefixes fix (#357)  * ci: fix repository posture checks  * feat: Add trending repo badge to readme (#347)  * chore(deps): bump the major group with 5 updates (#348)  Bumps the major group with 5 updates:  | Package | From | To | | --- | --- | --- | | [actions/checkout](https://github.com/actions/checkout) | `4` | `7` | | [pnpm/action-setup](https://github.com/pnpm/action-setup) | `4.3.0` | `6.0.9` | | [actions/setup-node](https://github.com/actions/setup-node) | `4` | `7` | | [github/codeql-action](https://github.com/github/codeql-action) | `3` | `4` | | [peter-evans/create-pull-request](https://github.com/peter-evans/create-pull-request) | `7.0.11` | `8.1.1` |   Updates `actions/checkout` from 4 to 7 - [Release notes](https://github.com/actions/checkout/releases) - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) - [Commits](https://github.com/actions/checkout/compare/v4...v7)  Updates `pnpm/action-setup` from 4.3.0 to 6.0.9 - [Release notes](https://github.com/pnpm/action-setup/releases) - [Commits](https://github.com/pnpm/action-setup/compare/b906affcce14559ad1aafd4ab0e942779e9f58b1...0ebf47130e4866e96fce0953f49152a61190b271)  Updates `actions/setup-node` from 4 to 7 - [Release notes](https://github.com/actions/setup-node/releases) - [Commits](https://github.com/actions/setup-node/compare/v4...v7)  Updates `github/codeql-action` from 3 to 4 - [Release notes](https://github.com/github/codeql-action/releases) - [Changelog](https://github.com/github/codeql-action/blob/main/CHANGELOG.md) - [Commits](https://github.com/github/codeql-action/compare/v3...v4)  Updates `peter-evans/create-pull-request` from 7.0.11 to 8.1.1 - [Release notes](https://github.com/peter-evans/create-pull-request/releases) - [Commits](https://github.com/peter-evans/create-pull-request/compare/22a9089034f40e5a961c8808d113e2c98fb63676...5f6978faf089d4d20b00c7766989d076bb2fc7f1)  --- updated-dependencies: - dependency-name: actions/checkout   dependency-version: '7'   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: pnpm/action-setup   dependency-version: 6.0.9   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: actions/setup-node   dependency-version: '7'   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: github/codeql-action   dependency-version: '4'   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major - dependency-name: peter-evans/create-pull-request   dependency-version: 8.1.1   dependency-type: direct:production   update-type: version-update:semver-major   dependency-group: major ...  Signed-off-by: dependabot[bot] <support@github.com> Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>  * feat: add gemini (ai studio) and gemini enterprise (vertex ai) providers with vertex model-family routing (#154)  * feat: add Gemini providers and consolidate Vertex Claude into gemini-enterprise  Add two Google model providers and route the Vertex AI (now Gemini Enterprise) Model Garden through a single provider:  - `gemini` (AI Studio): Google's Gemini models via one API key (GEMINI_API_KEY). - `gemini-enterprise` (Vertex AI): keyless, ADC-authenticated provider that   routes each model ID to the right Model Garden surface — native Gemini/Gemma   over generateContent, Claude over the Anthropic Vertex SDK, and   partner/open-weight models over the OpenAI-compatible MaaS endpoint   (resolveVertexSurface / createGeminiEnterpriseModel).  This supersedes the discrete `vertex` (Claude-only) provider added in #179: `gemini-enterprise` reaches Claude on Vertex through the same AnthropicVertex construction and ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN env-neutralization, plus publisher-path stripping, so no capability is lost. The rename tracks Google's Cloud Next 2026 rebrand of Vertex AI to the Gemini Enterprise Agent Platform while keeping the unchanged underlying API surface.  Builds on #179's keyless-provider plumbing (projectEnvKey/locationEnvKey/ defaultLocation, getMissingProviderEnvKey, resolveProviderLocation, getProviderCredentialHint) and its gcp-project/gcp-location onboarding steps, which gemini-enterprise inherits — dropping #154's earlier approach of overloading apiKeyEnvKey to carry the non-secret GOOGLE_CLOUD_PROJECT.  Gemini uses disableStreaming + outputVersion \"v0\" to preserve Gemini 3.x thought signatures across multi-turn tool calls (shared GEMINI_THOUGHT_SIGNATURE_OPTIONS across both ChatGoogle surfaces).  The MaaS endpoint and the Gemini surface both special-case the `global` location: MaaS uses the unprefixed aiplatform.googleapis.com host, and the Gemini surface strips a publisher-pathed ID to the bare model the generateContent surface expects. resolveVertexSurface lists `codellama` explicitly so bare codellama-* IDs route to MaaS.  Co-Authored-By: Claude <noreply@anthropic.com>  * test: verify provider retry attempts reach the Gemini constructors  createModel now spreads ...retryOptions into every Gemini surface (the AI Studio ChatGoogle and all three gemini-enterprise clients), which previously omitted it — so OPENWIKI_PROVIDER_RETRY_ATTEMPTS was silently ignored and a 429 failed fast instead of backing off (reported by @avidspartan1 on #154).  maxRetries is not a readable property on the constructed LangChain models, so this asserts it via vi.mock capturing each constructor's options (including that maxRetries: 0 propagates and the AI Studio API key reaches ChatGoogle). Once maxRetries is wired through, @langchain/core's AsyncCaller already honors a server-provided Retry-After (up to 60s), so the existing backoff engages.  Co-Authored-By: Claude <noreply@anthropic.com>  ---------  Co-authored-by: Claude <noreply@anthropic.com>  * bump deepagents to 1.11.0 to restore execute tool via routePrefixes fix  ---------  Signed-off-by: dependabot[bot] <support@github.com> Co-authored-by: John Kennedy <65985482+jkennedyvz@users.noreply.github.com> Co-authored-by: Brace Sproul <braceasproul@gmail.com> Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> Co-authored-by: Brad Huffman <brad.huffman@wellsky.com> Co-authored-by: Claude <noreply@anthropic.com>  * fix: Better relationship prompting (#359)  * chore: Update openwiki to be OKF compliant (#355)  * chore: Update openwiki to be OKF compliant  * add index files  * cr  ---------  Signed-off-by: dependabot[bot] <support@github.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com> Co-authored-by: John Kennedy <65985482+jkennedyvz@users.noreply.github.com> Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> Co-authored-by: Brad Huffman <brad.huffman@wellsky.com> Co-authored-by: Claude <noreply@anthropic.com>") | 4 days agoJul 16, 2026 |
| [openwiki](https://github.com/langchain-ai/openwiki/tree/main/openwiki "openwiki") | [openwiki](https://github.com/langchain-ai/openwiki/tree/main/openwiki "openwiki") | [docs: update OpenWiki (](https://github.com/langchain-ai/openwiki/commit/221b50de7ef2dc1052413d4640e775c0a0a6e89a "docs: update OpenWiki (#387)  Co-authored-by: bracesproul <46789226+bracesproul@users.noreply.github.com>") [#387](https://github.com/langchain-ai/openwiki/pull/387) [)](https://github.com/langchain-ai/openwiki/commit/221b50de7ef2dc1052413d4640e775c0a0a6e89a "docs: update OpenWiki (#387)  Co-authored-by: bracesproul <46789226+bracesproul@users.noreply.github.com>") | 10 hours agoJul 19, 2026 |
| [skills](https://github.com/langchain-ai/openwiki/tree/main/skills "skills") | [skills](https://github.com/langchain-ai/openwiki/tree/main/skills "skills") | [fix: align OKF output with Google v0.1 (](https://github.com/langchain-ai/openwiki/commit/c55573f19d59e6cbd6349f19f1e770883d7a9108 "fix: align OKF output with Google v0.1 (#373)  Co-authored-by: Ruan Barroso <ruanbarroso@gmail.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") [#373](https://github.com/langchain-ai/openwiki/pull/373) [)](https://github.com/langchain-ai/openwiki/commit/c55573f19d59e6cbd6349f19f1e770883d7a9108 "fix: align OKF output with Google v0.1 (#373)  Co-authored-by: Ruan Barroso <ruanbarroso@gmail.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") | 3 days agoJul 17, 2026 |
| [src](https://github.com/langchain-ai/openwiki/tree/main/src "src") | [src](https://github.com/langchain-ai/openwiki/tree/main/src "src") | [fix: avoid wrapping oauth urls in setup ui (](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717 "fix: avoid wrapping oauth urls in setup ui (#308)  * fix: avoid wrapping OAuth URLs in setup UI  * fix: add OAuth URL fallback command") [#308](https://github.com/langchain-ai/openwiki/pull/308) [)](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717 "fix: avoid wrapping oauth urls in setup ui (#308)  * fix: avoid wrapping OAuth URLs in setup UI  * fix: add OAuth URL fallback command") | 5 hours agoJul 20, 2026 |
| [static](https://github.com/langchain-ai/openwiki/tree/main/static "static") | [static](https://github.com/langchain-ai/openwiki/tree/main/static "static") | [fix: Readme improvements (](https://github.com/langchain-ai/openwiki/commit/14ca04a8b9ddba347ff267eb514d2864e6f55ee8 "fix: Readme improvements (#19)  * fix: Readme improvements  * update image  * cr  * cr  * cr  * cr  * cr  * update ex gh action  * cr  * cr") [#19](https://github.com/langchain-ai/openwiki/pull/19) [)](https://github.com/langchain-ai/openwiki/commit/14ca04a8b9ddba347ff267eb514d2864e6f55ee8 "fix: Readme improvements (#19)  * fix: Readme improvements  * update image  * cr  * cr  * cr  * cr  * cr  * update ex gh action  * cr  * cr") | 3 weeks agoJul 1, 2026 |
| [test](https://github.com/langchain-ai/openwiki/tree/main/test "test") | [test](https://github.com/langchain-ai/openwiki/tree/main/test "test") | [fix: avoid wrapping oauth urls in setup ui (](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717 "fix: avoid wrapping oauth urls in setup ui (#308)  * fix: avoid wrapping OAuth URLs in setup UI  * fix: add OAuth URL fallback command") [#308](https://github.com/langchain-ai/openwiki/pull/308) [)](https://github.com/langchain-ai/openwiki/commit/e2a7ca5d7960b8e49f4c5d23636b1da444540717 "fix: avoid wrapping oauth urls in setup ui (#308)  * fix: avoid wrapping OAuth URLs in setup UI  * fix: add OAuth URL fallback command") | 5 hours agoJul 20, 2026 |
| [.gitignore](https://github.com/langchain-ai/openwiki/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/langchain-ai/openwiki/blob/main/.gitignore ".gitignore") | [feat: Make OpenWiki general purpose (](https://github.com/langchain-ai/openwiki/commit/cb2f20399c2786948b42dd514820a99abca09e22 "feat: Make OpenWiki general purpose (#48)  * feat: Make general purpose  * cr  * cr  * fix gmail  * make it much better  * add cron hooks  * better ngrok  * write wiki to root  * cr  * Harrison/vibe code (#109)  * some vibe coding  * cr  * cr  * cr  * cr  * fix gh action  ---------  Co-authored-by: bracesproul <braceasproul@gmail.com>  * update readme  * fix oauth link clicking  * drop just openwiki --init  * fix: oauth connection flow  * improve prompting  * cr  * cr  * brain->personal (#226)  * cr  * write instructions to INSTRUCTIONS.md file  * cr  ---------  Co-authored-by: Harrison Chase <hw.chase.17@gmail.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") [#48](https://github.com/langchain-ai/openwiki/pull/48) [)](https://github.com/langchain-ai/openwiki/commit/cb2f20399c2786948b42dd514820a99abca09e22 "feat: Make OpenWiki general purpose (#48)  * feat: Make general purpose  * cr  * cr  * fix gmail  * make it much better  * add cron hooks  * better ngrok  * write wiki to root  * cr  * Harrison/vibe code (#109)  * some vibe coding  * cr  * cr  * cr  * cr  * fix gh action  ---------  Co-authored-by: bracesproul <braceasproul@gmail.com>  * update readme  * fix oauth link clicking  * drop just openwiki --init  * fix: oauth connection flow  * improve prompting  * cr  * cr  * brain->personal (#226)  * cr  * write instructions to INSTRUCTIONS.md file  * cr  ---------  Co-authored-by: Harrison Chase <hw.chase.17@gmail.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") | 2 weeks agoJul 9, 2026 |
| [.prettierignore](https://github.com/langchain-ai/openwiki/blob/main/.prettierignore ".prettierignore") | [.prettierignore](https://github.com/langchain-ai/openwiki/blob/main/.prettierignore ".prettierignore") | [refactor, auto-write gh workflow](https://github.com/langchain-ai/openwiki/commit/7bfaeb2cfdaefad4e725756a819d50d1dc0c1b15 "refactor, auto-write gh workflow") | last monthJun 22, 2026 |
| [AGENTS.md](https://github.com/langchain-ai/openwiki/blob/main/AGENTS.md "AGENTS.md") | [AGENTS.md](https://github.com/langchain-ai/openwiki/blob/main/AGENTS.md "AGENTS.md") | [feat: Make OpenWiki general purpose (](https://github.com/langchain-ai/openwiki/commit/cb2f20399c2786948b42dd514820a99abca09e22 "feat: Make OpenWiki general purpose (#48)  * feat: Make general purpose  * cr  * cr  * fix gmail  * make it much better  * add cron hooks  * better ngrok  * write wiki to root  * cr  * Harrison/vibe code (#109)  * some vibe coding  * cr  * cr  * cr  * cr  * fix gh action  ---------  Co-authored-by: bracesproul <braceasproul@gmail.com>  * update readme  * fix oauth link clicking  * drop just openwiki --init  * fix: oauth connection flow  * improve prompting  * cr  * cr  * brain->personal (#226)  * cr  * write instructions to INSTRUCTIONS.md file  * cr  ---------  Co-authored-by: Harrison Chase <hw.chase.17@gmail.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") [#48](https://github.com/langchain-ai/openwiki/pull/48) [)](https://github.com/langchain-ai/openwiki/commit/cb2f20399c2786948b42dd514820a99abca09e22 "feat: Make OpenWiki general purpose (#48)  * feat: Make general purpose  * cr  * cr  * fix gmail  * make it much better  * add cron hooks  * better ngrok  * write wiki to root  * cr  * Harrison/vibe code (#109)  * some vibe coding  * cr  * cr  * cr  * cr  * fix gh action  ---------  Co-authored-by: bracesproul <braceasproul@gmail.com>  * update readme  * fix oauth link clicking  * drop just openwiki --init  * fix: oauth connection flow  * improve prompting  * cr  * cr  * brain->personal (#226)  * cr  * write instructions to INSTRUCTIONS.md file  * cr  ---------  Co-authored-by: Harrison Chase <hw.chase.17@gmail.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") | 2 weeks agoJul 9, 2026 |
| [CLAUDE.md](https://github.com/langchain-ai/openwiki/blob/main/CLAUDE.md "CLAUDE.md") | [CLAUDE.md](https://github.com/langchain-ai/openwiki/blob/main/CLAUDE.md "CLAUDE.md") | [fix: Improve code onboarding, save INSTRUCTIONS.md to openwiki/ (](https://github.com/langchain-ai/openwiki/commit/20c48678a8d493cd3b7b8a078ccfa8d2797cd8c7 "fix: Improve code onboarding, save INSTRUCTIONS.md to openwiki/ (#264)  * fix: Improve code onboarding, save INSTRUCTIONS.md to openwiki/  * cr") [#264](https://github.com/langchain-ai/openwiki/pull/264) [)](https://github.com/langchain-ai/openwiki/commit/20c48678a8d493cd3b7b8a078ccfa8d2797cd8c7 "fix: Improve code onboarding, save INSTRUCTIONS.md to openwiki/ (#264)  * fix: Improve code onboarding, save INSTRUCTIONS.md to openwiki/  * cr") | last weekJul 10, 2026 |
| [CONTRIBUTING.md](https://github.com/langchain-ai/openwiki/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/langchain-ai/openwiki/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [chore: add contributing guidelines via](https://github.com/langchain-ai/openwiki/commit/e276b0876343e46e6b381ea8d5732d64f598c75c "chore: add contributing guidelines via `CONTRIBUTING.md` (#145)  * add contributing guidelines  * formatting  * link contributing from readme")`CONTRIBUTING.md` [(](https://github.com/langchain-ai/openwiki/commit/e276b0876343e46e6b381ea8d5732d64f598c75c "chore: add contributing guidelines via `CONTRIBUTING.md` (#145)  * add contributing guidelines  * formatting  * link contributing from readme") [#145](https://github.com/langchain-ai/openwiki/pull/145) [)](https://github.com/langchain-ai/openwiki/commit/e276b0876343e46e6b381ea8d5732d64f598c75c "chore: add contributing guidelines via `CONTRIBUTING.md` (#145)  * add contributing guidelines  * formatting  * link contributing from readme") | 2 weeks agoJul 6, 2026 |
| [DEVELOPMENT.md](https://github.com/langchain-ai/openwiki/blob/main/DEVELOPMENT.md "DEVELOPMENT.md") | [DEVELOPMENT.md](https://github.com/langchain-ai/openwiki/blob/main/DEVELOPMENT.md "DEVELOPMENT.md") | [chore: engineering-hygiene pass — CI safety net, tests, de-duplication (](https://github.com/langchain-ai/openwiki/commit/a46217fde230ae80071eaabd5c00b9719b77a86d "chore: engineering-hygiene pass — CI safety net, tests, de-duplication (#141)  Enforce and regression-proof the codebase's existing quality without changing agent or CLI behavior.  CI (checks.yml): add build+typecheck and test jobs on a Node 20/22 matrix. Previously CI ran only format:check and lint:check, so a PR could merge with a failing test suite or broken compile. Add `typecheck` and `coverage` scripts.  Tests: 6 -> 80. New suites cover the CLI arg parser (parseCommand), the pure constants validators/resolvers, the .env parse/format round-trip, the shared fs-error helpers, and — most importantly — the security-critical secret redaction (sanitizeDiagnosticText, sanitizeOpenRouterResponseBody, getErrorMessage). Add @vitest/coverage-v8; bump vitest to 4.1.10 to match.  De-duplication: extract isFileNotFoundError / isExpectedSnapshotRaceError into src/fs-errors.ts (were copied verbatim in 3 files); collapse the 3 parallel env-key lists into one source of truth (MANAGED_ENV_KEYS) that derives the diagnostics and debug lists. Extract the redaction helpers into src/diagnostics.ts so they are importable/testable without executing cli.tsx's top-level render.  Config: ESLint -> recommendedTypeChecked and now lints test/** (via tsconfig.eslint.json); fixed the findings this surfaced (a stray async, unsafe any returns in the stream parser, a redundant union). Deferred noUncheckedIndexedAccess (17 errors concentrated in the untested cli.tsx monolith — out of proportion to this pass).  Cleanups: remove a hard-coded personal path from DEVELOPMENT.md; add coverage/ and *.tgz to .gitignore.  Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>") | 2 weeks agoJul 6, 2026 |
| [LICENSE](https://github.com/langchain-ai/openwiki/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/langchain-ai/openwiki/blob/main/LICENSE "LICENSE") | [init commit](https://github.com/langchain-ai/openwiki/commit/ce3c57028a9ff6bed0327ffe31245b986fbc2bdb "init commit") | last monthJun 22, 2026 |
| [README.md](https://github.com/langchain-ai/openwiki/blob/main/README.md "README.md") | [README.md](https://github.com/langchain-ai/openwiki/blob/main/README.md "README.md") | [feat: support OPENAI\_BASE\_URL for the openai provider (](https://github.com/langchain-ai/openwiki/commit/1f37d2a19137cf890ae0816027d08bbf4aee58cd "feat: support OPENAI_BASE_URL for the openai provider (#328)  The `openai` provider had no `baseUrlEnvKey`, so a custom base URL could only reach it implicitly via the OpenAI SDK reading the `OPENAI_BASE_URL` env var. Make this explicit and consistent with the `openai-compatible` and `anthropic` providers:  - Add `OPENAI_BASE_URL_ENV_KEY` and wire it as the `openai` provider's   `baseUrlEnvKey`, so `resolveProviderBaseUrl(\"openai\")` honors it and the   resolved `baseURL` is passed through to the model client. - Register `OPENAI_BASE_URL` in `MANAGED_ENV_KEYS` so it is loaded from   `~/.openwiki/.env`, persisted in stable order, and surfaced in the   credential diagnostics as a non-secret value (like the other base URL keys).  This lets the `openai` provider target an OpenAI-compatible Responses-API gateway (e.g. a Codex-backed proxy) directly from `.env`, instead of forcing users onto the `openai-compatible` provider, which routes tool calls through chat completions and fails on such gateways.  Co-authored-by: Claude Fable 5 <noreply@anthropic.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") [#328](https://github.com/langchain-ai/openwiki/pull/328) [)](https://github.com/langchain-ai/openwiki/commit/1f37d2a19137cf890ae0816027d08bbf4aee58cd "feat: support OPENAI_BASE_URL for the openai provider (#328)  The `openai` provider had no `baseUrlEnvKey`, so a custom base URL could only reach it implicitly via the OpenAI SDK reading the `OPENAI_BASE_URL` env var. Make this explicit and consistent with the `openai-compatible` and `anthropic` providers:  - Add `OPENAI_BASE_URL_ENV_KEY` and wire it as the `openai` provider's   `baseUrlEnvKey`, so `resolveProviderBaseUrl(\"openai\")` honors it and the   resolved `baseURL` is passed through to the model client. - Register `OPENAI_BASE_URL` in `MANAGED_ENV_KEYS` so it is loaded from   `~/.openwiki/.env`, persisted in stable order, and surfaced in the   credential diagnostics as a non-secret value (like the other base URL keys).  This lets the `openai` provider target an OpenAI-compatible Responses-API gateway (e.g. a Codex-backed proxy) directly from `.env`, instead of forcing users onto the `openai-compatible` provider, which routes tool calls through chat completions and fails on such gateways.  Co-authored-by: Claude Fable 5 <noreply@anthropic.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com>") | 8 hours agoJul 19, 2026 |
| [eslint.config.js](https://github.com/langchain-ai/openwiki/blob/main/eslint.config.js "eslint.config.js") | [eslint.config.js](https://github.com/langchain-ai/openwiki/blob/main/eslint.config.js "eslint.config.js") | [docs: document windows bun installation requirements (](https://github.com/langchain-ai/openwiki/commit/90e8b22f562a5c8cf3c7377e081710084db1689f "docs: document windows bun installation requirements (#217)  * fix: warn on Windows Bun installs  * add .cjs to esling config  * fix: document Windows Bun installation requirements  ---------  Co-authored-by: akyourowngames <akyourowngames@users.noreply.github.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com> Co-authored-by: Colin Francis <colin.francis@langchain.dev>") [#217](https://github.com/langchain-ai/openwiki/pull/217) [)](https://github.com/langchain-ai/openwiki/commit/90e8b22f562a5c8cf3c7377e081710084db1689f "docs: document windows bun installation requirements (#217)  * fix: warn on Windows Bun installs  * add .cjs to esling config  * fix: document Windows Bun installation requirements  ---------  Co-authored-by: akyourowngames <akyourowngames@users.noreply.github.com> Co-authored-by: Colin Francis <131073567+colifran@users.noreply.github.com> Co-authored-by: Colin Francis <colin.francis@langchain.dev>") | last weekJul 10, 2026 |
| [package.json](https://github.com/langchain-ai/openwiki/blob/main/package.json "package.json") | [package.json](https://github.com/langchain-ai/openwiki/blob/main/package.json "package.json") | [stop code-mode runs from targeting ~/.openwiki/wiki and bump deepagen…](https://github.com/langchain-ai/openwiki/commit/1f0862e78c39800f2deda036d46690ea4e753992 "stop code-mode runs from targeting ~/.openwiki/wiki and bump deepagents to prevent crashes (#383)") | 2 days agoJul 17, 2026 |
| [pnpm-lock.yaml](https://github.com/langchain-ai/openwiki/blob/main/pnpm-lock.yaml "pnpm-lock.yaml") | [pnpm-lock.yaml](https://github.com/langchain-ai/openwiki/blob/main/pnpm-lock.yaml "pnpm-lock.yaml") | [stop code-mode runs from targeting ~/.openwiki/wiki and bump deepagen…](https://github.com/langchain-ai/openwiki/commit/1f0862e78c39800f2deda036d46690ea4e753992 "stop code-mode runs from targeting ~/.openwiki/wiki and bump deepagents to prevent crashes (#383)") | 2 days agoJul 17, 2026 |
| [pnpm-workspace.yaml](https://github.com/langchain-ai/openwiki/blob/main/pnpm-workspace.yaml "pnpm-workspace.yaml") | [pnpm-workspace.yaml](https://github.com/langchain-ai/openwiki/blob/main/pnpm-workspace.yaml "pnpm-workspace.yaml") | [stop code-mode runs from targeting ~/.openwiki/wiki and bump deepagen…](https://github.com/langchain-ai/openwiki/commit/1f0862e78c39800f2deda036d46690ea4e753992 "stop code-mode runs from targeting ~/.openwiki/wiki and bump deepagents to prevent crashes (#383)") | 2 days agoJul 17, 2026 |
| [tsconfig.eslint.json](https://github.com/langchain-ai/openwiki/blob/main/tsconfig.eslint.json "tsconfig.eslint.json") | [tsconfig.eslint.json](https://github.com/langchain-ai/openwiki/blob/main/tsconfig.eslint.json "tsconfig.eslint.json") | [chore: engineering-hygiene pass — CI safety net, tests, de-duplication (](https://github.com/langchain-ai/openwiki/commit/a46217fde230ae80071eaabd5c00b9719b77a86d "chore: engineering-hygiene pass — CI safety net, tests, de-duplication (#141)  Enforce and regression-proof the codebase's existing quality without changing agent or CLI behavior.  CI (checks.yml): add build+typecheck and test jobs on a Node 20/22 matrix. Previously CI ran only format:check and lint:check, so a PR could merge with a failing test suite or broken compile. Add `typecheck` and `coverage` scripts.  Tests: 6 -> 80. New suites cover the CLI arg parser (parseCommand), the pure constants validators/resolvers, the .env parse/format round-trip, the shared fs-error helpers, and — most importantly — the security-critical secret redaction (sanitizeDiagnosticText, sanitizeOpenRouterResponseBody, getErrorMessage). Add @vitest/coverage-v8; bump vitest to 4.1.10 to match.  De-duplication: extract isFileNotFoundError / isExpectedSnapshotRaceError into src/fs-errors.ts (were copied verbatim in 3 files); collapse the 3 parallel env-key lists into one source of truth (MANAGED_ENV_KEYS) that derives the diagnostics and debug lists. Extract the redaction helpers into src/diagnostics.ts so they are importable/testable without executing cli.tsx's top-level render.  Config: ESLint -> recommendedTypeChecked and now lints test/** (via tsconfig.eslint.json); fixed the findings this surfaced (a stray async, unsafe any returns in the stream parser, a redundant union). Deferred noUncheckedIndexedAccess (17 errors concentrated in the untested cli.tsx monolith — out of proportion to this pass).  Cleanups: remove a hard-coded personal path from DEVELOPMENT.md; add coverage/ and *.tgz to .gitignore.  Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>") | 2 weeks agoJul 6, 2026 |
| [tsconfig.json](https://github.com/langchain-ai/openwiki/blob/main/tsconfig.json "tsconfig.json") | [tsconfig.json](https://github.com/langchain-ai/openwiki/blob/main/tsconfig.json "tsconfig.json") | [init commit](https://github.com/langchain-ai/openwiki/commit/ce3c57028a9ff6bed0327ffe31245b986fbc2bdb "init commit") | last monthJun 22, 2026 |
| View all files |

## Repository files navigation

# OpenWiki

[Permalink: OpenWiki](https://github.com/langchain-ai/openwiki#openwiki)

OpenWiki is a CLI that writes and maintains agent wikis for codebases or purpose memory. It's built specifically for agents, can ingest local knowledge sources through built-in connectors or git repositories and synthesize them into a local wiki.

[![langchain-ai%2Fopenwiki | Trendshift](https://camo.githubusercontent.com/21d52323711d68a857e2192e8ea0fc68488eff5ee4c184c346adbc2954eaa32e/68747470733a2f2f7472656e6473686966742e696f2f6170692f62616467652f7472656e6473686966742f7265706f7369746f726965732f37303333392f6461696c79)](https://trendshift.io/repositories/70339?utm_source=trendshift-badge&utm_medium=badge&utm_campaign=badge-trendshift-70339)

![OpenWiki](https://raw.githubusercontent.com/langchain-ai/openwiki/main/static/openwiki.png)

## Install

[Permalink: Install](https://github.com/langchain-ai/openwiki#install)

```
npm install -g openwiki
```

On Windows, prefer installing OpenWiki with Node.js package managers such as
`npm` or `pnpm`:

```
npm install -g openwiki
# or
pnpm add -g openwiki
```

`bun install -g openwiki` can fall back to compiling OpenWiki's `better-sqlite3`
checkpointing dependency. Before using that path, install Visual Studio Build
Tools with the Desktop development with C++ workload. Bun does not run lifecycle
scripts from installed packages by default, so it cannot display a package-level
warning before that native dependency build starts.

## Quick Start

[Permalink: Quick Start](https://github.com/langchain-ai/openwiki#quick-start)

Initialize OpenWiki in code mode, configure your model and API key, then generate documentation:

```
openwiki --init
```

OpenWiki has two modes:

- **Personal mode** builds a local personal brain wiki in `~/.openwiki/wiki` from
configured sources like local repositories, Gmail, Notion, Web Search, Hacker
News, and X/Twitter.
- **Code mode** builds repository documentation in `openwiki/` for the current
codebase.

Bare `openwiki --init` and `openwiki --update` run in code mode. Use
`openwiki personal --init` or `openwiki personal --update` for the local
personal brain wiki.

Then to ensure your documentation stays up-to-date, add the CI workflow for your Git provider to automatically open a PR or merge request with documentation updates:

- GitHub Actions: copy [openwiki-update.yml](https://github.com/langchain-ai/openwiki/blob/main/examples/openwiki-update.yml) into `.github/workflows/openwiki-update.yml`.
- GitLab CI: copy [openwiki-update.gitlab-ci.yml](https://github.com/langchain-ai/openwiki/blob/main/examples/openwiki-update.gitlab-ci.yml) into `.gitlab-ci.yml` or include it from your existing GitLab pipeline.
- Bitbucket Pipelines: copy [openwiki-update.bitbucket-pipelines.yml](https://github.com/langchain-ai/openwiki/blob/main/examples/openwiki-update.bitbucket-pipelines.yml) into `bitbucket-pipelines.yml`, then schedule the `openwiki-update` custom pipeline from Repository settings > Pipelines > Schedules.

For repository documentation in GitHub Actions, use
`openwiki code --update --print`. You do not need to run `--init` in CI:
`--update` will create the initial `openwiki/` docs if they do not exist yet, as
long as the workflow provides the required provider and model environment
variables.

Scheduled/CI runs send anonymous reliability telemetry. See [Telemetry](https://github.com/langchain-ai/openwiki#telemetry)
for what is collected and how to turn it off (uncomment `OPENWIKI_TELEMETRY_DISABLED`
in the example workflow).

## Open Knowledge Format compatibility

[Permalink: Open Knowledge Format compatibility](https://github.com/langchain-ai/openwiki#open-knowledge-format-compatibility)

OpenWiki emits [Google Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundles in both code and personal modes.

- Every non-reserved Markdown concept has YAML front matter with a non-empty
`type`; all other standard fields are optional.
- Valid `timestamp` values and producer-defined extension fields are accepted
and preserved during updates and migrations.
- `index.md` and `log.md` are reserved documents rather than concepts. Nested
indexes contain no front matter, while the root index declares
`okf_version: "0.1"`.
- Standard Markdown links between concept documents express relationships.

## Usage

[Permalink: Usage](https://github.com/langchain-ai/openwiki#usage)

Start the interactive CLI in code mode for the current repository:

```
openwiki
```

Start OpenWiki with an initial request:

```
openwiki "Please generate documentation for this repository"
```

Start the interactive local personal brain instead:

```
openwiki personal
```

Run a single command and exit:

```
openwiki -p "Summarize what you can do"
```

Initialize OpenWiki:

```
openwiki --init
```

Initialize the local personal brain wiki:

```
openwiki personal --init
```

Update repository code documentation:

```
openwiki --update
```

Update the local personal brain wiki:

```
openwiki personal --update
```

Run an update that can ingest configured local connectors first:

```
openwiki personal --update "Refresh the wiki from configured connectors"
```

Show help:

```
openwiki --help
```

In chat, use `/api-key` to update the current provider API key and
`/langsmith-key` to update or clear LangSmith tracing credentials. Both commands
use masked prompts.

Authenticate a connector provider:

```
openwiki auth slack
openwiki auth gmail
openwiki auth x
openwiki auth notion
```

Start an ngrok tunnel for Slack OAuth:

```
openwiki ngrok start
```

This starts ngrok with a random HTTPS forwarding URL. OpenWiki reads ngrok's
local inspection API, appends `/callback`, and saves
`OPENWIKI_HTTPS_OAUTH_REDIRECT_URI` automatically. Register the printed callback
URL in Slack. If you have a fixed ngrok domain, run
`openwiki ngrok start https://<your-ngrok-domain>`. X/Twitter and Gmail auth
ignore that HTTPS override and keep using the local loopback callback,
`http://127.0.0.1:53682/callback`.

Bare `openwiki` runs in code mode for the current repository. It creates initial repository documentation in `openwiki/` when no wiki exists. Use `openwiki personal` for the local general-purpose wiki in `~/.openwiki/wiki/`. By default, the CLI stays open after each run so you can send follow-up messages. Use `-p` or `--print` for a one-shot non-interactive run that prints the final assistant output.

Bare `openwiki --init` and `openwiki --update` default to code mode and operate on repository documentation. Use the `personal` positional mode or `--mode personal` to initialize or update the local personal brain wiki.

On each `code` run, `openwiki` maintains both an `AGENTS.md` and a `CLAUDE.md` at the repository root, adding prompting that instructs your coding agent to reference the wiki when searching for context. Each file is created if it does not already exist. If a file is present, OpenWiki only rewrites its own `<!-- OPENWIKI:START -->…<!-- OPENWIKI:END -->` block and leaves the rest of your content untouched (appending the block the first time). The scheduled GitHub Actions workflow includes these files, along with the workflow itself, in the documentation pull request.

Repository-specific wiki instructions are stored separately in
`openwiki/INSTRUCTIONS.md`. This file is a shared, user-authored brief for the
repository wiki: OpenWiki reads it for scope and priorities, but it is not
generated documentation and is not rewritten during normal init, update, or chat
runs unless you explicitly ask to change the brief.

On the first interactive run, OpenWiki will have you configure your inference provider, API key, and LLM. You will also be able to set a LangSmith API key to trace your OpenWiki runs to a LangSmith tracing project named "openwiki" (optional).

These configuration options and secrets will be saved to `~/.openwiki/.env` on your local machine.

## Local Connectors

[Permalink: Local Connectors](https://github.com/langchain-ai/openwiki#local-connectors)

OpenWiki's first-run onboarding offers connector setup for local Git repositories, Notion, Gmail, X/Twitter, Web Search, and Hacker News. During an ingestion run, deterministic connector tools write raw data and manifests under `~/.openwiki/connectors/<connector>/raw/`, then source-specific agent runs synthesize the local wiki under `~/.openwiki/wiki/` from those local files.

You can configure the same connector more than once. For example, add one Web
Search source for AI research and another for NBA news; OpenWiki stores them as
separate source instances such as `web-search-1` and `web-search-2`. Run all
instances with `openwiki ingest all`, all instances for one connector with
`openwiki ingest web-search`, or one instance with
`openwiki ingest web-search-2`.

- `git-repo` reads configured local repository paths and writes compact manifests.
- `x` uses the X API directly with OAuth user-context credentials for home timeline, user posts, mentions, bookmarks, and list posts.
- `notion` targets the hosted Notion MCP server, so users should authenticate through Notion OAuth instead of pasting a Notion token into OpenWiki.
- `google` uses the Gmail API directly with OAuth user credentials to fetch recent mail, with room to add Drive, Calendar, and other Google providers later.
- `web-search` uses Tavily through LangChain and requires `TAVILY_API_KEY`.
- `hackernews` uses public Hacker News feed and search APIs, with no credentials required.

Connector secrets are referenced by env var name and stored in `~/.openwiki/.env`; connector config files should never contain raw secret values.

`openwiki auth <provider>` runs a local browser OAuth flow, saves returned tokens into `~/.openwiki/.env`, creates connector config when possible, and discovers MCP tools for MCP-backed providers. Slack and Gmail require app client credentials to already be set in that file; Notion uses dynamic client registration for hosted MCP; X uses OAuth 2.0 with PKCE. After `openwiki auth gmail`, the Google connector can ingest Gmail directly with no MCP transport setup.

`openwiki auth configure <provider>` and `openwiki auth tools <provider>` are advanced/retry commands for regenerating connector config or inspecting live MCP tools.

First-run onboarding also lets users choose a wiki template, customize its scope,
and save per-source ingestion notes and source schedules in
`~/.openwiki/onboarding.json`. The global personal wiki instructions are saved
in `~/.openwiki/INSTRUCTIONS.md`. On macOS, source schedules are installed as
user LaunchAgents under `~/Library/LaunchAgents/` and write logs under
`~/.openwiki/logs/`.

See the OpenWiki operations docs for credential storage and provider setup
notes.

## Customizing

[Permalink: Customizing](https://github.com/langchain-ai/openwiki#customizing)

OpenWiki supports OpenAI (with an API key or a ChatGPT login), OpenRouter, Gemini (AI Studio), Gemini Enterprise (Vertex AI), Nebius Token Factory, Fireworks, Baseten, NVIDIA NIM, an OpenAI-compatible provider, AWS Bedrock, and Anthropic out of the box. The onboarding default is OpenAI with `gpt-5.6-terra`, and each inference provider also includes pre-defined model options plus support for custom model IDs.

### Alternative base URLs

[Permalink: Alternative base URLs](https://github.com/langchain-ai/openwiki#alternative-base-urls)

To route the Anthropic provider at an alternative, Anthropic-compatible endpoint
(for example a self-hosted or proxied gateway) instead of the default API, set
`ANTHROPIC_BASE_URL` alongside `ANTHROPIC_API_KEY`:

```
OPENWIKI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=https://your-gateway.example.com/anthropic
```

The `openai` provider likewise supports an alternative, OpenAI-compatible
endpoint (for example a self-hosted or proxied gateway) via `OPENAI_BASE_URL`,
set alongside `OPENAI_API_KEY`. This is useful for OpenAI-compatible gateways
that expose the Responses API, since the `openai` provider routes tool calls
through the Responses API (`/v1/responses`) rather than chat completions:

```
OPENWIKI_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://your-gateway.example.com/v1
OPENWIKI_MODEL_ID=your-model-name
```

### OpenAI-compatible endpoints

[Permalink: OpenAI-compatible endpoints](https://github.com/langchain-ai/openwiki#openai-compatible-endpoints)

The `openai-compatible` provider targets any OpenAI-compatible chat-completions
endpoint via a required base URL. This can be used for OpenAI-compatible LLM
endpoints like those exposed by a LiteLLM gateway when it is used as a gateway —
letting you reach whatever upstream providers the gateway fronts through a single
OpenAI-shaped API. Set the model ID to whatever name the gateway exposes:

```
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=your-gateway-key
OPENAI_COMPATIBLE_BASE_URL=https://your-gateway.example.com/v1
OPENWIKI_MODEL_ID=your-gateway-model-name
```

Local LLM servers that expose OpenAI-compatible chat completions use the same
provider. The model ID must match a model available from that local server:

```
# Ollama, after `ollama serve` and `ollama pull llama3.2`
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=ollama
OPENAI_COMPATIBLE_BASE_URL=http://localhost:11434/v1
OPENWIKI_MODEL_ID=llama3.2
openwiki --init
```

```
# LM Studio, after starting the local server from the Developer tab
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=lm-studio
OPENAI_COMPATIBLE_BASE_URL=http://localhost:1234/v1
OPENWIKI_MODEL_ID=your-loaded-model-id
openwiki --init
```

For local gateways such as 9Router, use the OpenAI-compatible endpoint URL,
API key, and model ID shown by the gateway:

```
OPENWIKI_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=your-local-gateway-key
OPENAI_COMPATIBLE_BASE_URL=http://localhost:20128/v1
OPENWIKI_MODEL_ID=your-routed-model-id
openwiki --init
```

Some local servers ignore the API key value, but OpenWiki still requires
`OPENAI_COMPATIBLE_API_KEY` because the OpenAI-compatible client expects one.

### AWS Bedrock

[Permalink: AWS Bedrock](https://github.com/langchain-ai/openwiki#aws-bedrock)

The `bedrock` provider calls foundation models hosted on AWS Bedrock using IAM
credentials rather than a single vendor API key. It authenticates with an AWS
access key ID, a secret access key, and a region:

```
OPENWIKI_PROVIDER=bedrock
BEDROCK_AWS_ACCESS_KEY_ID=your-access-key-id
BEDROCK_AWS_SECRET_ACCESS_KEY=your-secret-access-key
BEDROCK_AWS_REGION=us-east-1
OPENWIKI_MODEL_ID=anthropic.claude-sonnet-5
```

Which model IDs are available depends on your AWS account and region (which
foundation models you've enabled in the Bedrock console), so there is no
preset model list — paste the Bedrock model ID directly, as shown above.

Some newer models only accept on-demand invocation through a cross-region
inference profile rather than their bare model ID — if you see `ValidationException: Invocation of model ID ... with on-demand throughput isn't supported`, prefix
the model ID with the profile's region code instead, for example
`us.anthropic.claude-sonnet-5`. Your IAM policy also needs to allow
`bedrock:InvokeModel`/`InvokeModelWithResponseStream` on both the
`foundation-model` and `inference-profile` resource types in that case.

### OpenAI (ChatGPT login)

[Permalink: OpenAI (ChatGPT login)](https://github.com/langchain-ai/openwiki#openai-chatgpt-login)

The `openai-chatgpt` provider calls OpenAI's Codex backend using your ChatGPT
subscription instead of a metered API key. Model usage draws on your ChatGPT
Plus/Pro/Team plan's included Codex usage rather than per-token API billing. It
serves the same model list as the `openai` provider.

Instead of pasting an API key, run the setup wizard and complete a browser
login:

```
OPENWIKI_PROVIDER=openai-chatgpt openwiki code --init
# or
OPENWIKI_PROVIDER=openai-chatgpt openwiki personal --init
```

The wizard opens `https://auth.openai.com` in your browser (and also prints the
URL for headless/SSH use, where you can open it on another machine — or paste the
redirect URL back into the terminal to finish without a callback). After you sign
in with your ChatGPT account, OpenWiki captures the OAuth callback, shows the
signed-in email and plan, and then continues to model and LangSmith selection
just like the other providers. It stores the resulting access token, refresh
token, expiry, account id, email, and plan in `~/.openwiki/.env`
(`OPENAI_CHATGPT_ACCESS_TOKEN`, `OPENAI_CHATGPT_REFRESH_TOKEN`,
`OPENAI_CHATGPT_EXPIRES_AT`, `OPENAI_CHATGPT_ACCOUNT_ID`, `OPENAI_CHATGPT_EMAIL`,
`OPENAI_CHATGPT_PLAN`). These are managed for you — the access token is refreshed
automatically when it expires, so you normally never edit them by hand. Treat the
refresh token like a password.

### Gemini (AI Studio)

[Permalink: Gemini (AI Studio)](https://github.com/langchain-ai/openwiki#gemini-ai-studio)

The `gemini` provider runs Google's Gemini models through the AI Studio API with
a single API key:

```
OPENWIKI_PROVIDER=gemini
GEMINI_API_KEY=your-ai-studio-key
```

### Gemini Enterprise (Vertex AI)

[Permalink: Gemini Enterprise (Vertex AI)](https://github.com/langchain-ai/openwiki#gemini-enterprise-vertex-ai)

The `gemini-enterprise` provider runs models from the Gemini Enterprise Model
Garden (formerly Vertex AI) — Google's own Gemini/Gemma models, Anthropic's
Claude, and partner/open-weight models (Llama, Mistral, DeepSeek, Qwen, …). It
routes each model ID to the right API surface automatically, so one credential
reaches all of them. It uses no API key — authentication happens with Google
Application Default Credentials (ADC), so any of the standard mechanisms work:

- a service account key file via `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`,
- user credentials from `gcloud auth application-default login`, or
- workload identity when running on Google Cloud (GKE, Cloud Run, GCE) or in CI.

```
OPENWIKI_PROVIDER=gemini-enterprise
GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_CLOUD_LOCATION=global   # optional, defaults to global
```

Set `OPENWIKI_MODEL_ID` to any Model Garden model. Gemini and Claude ship as
preset options; partner/open-weight models are reached by pasting their model ID
(for example `publishers/meta/models/llama-3.3-70b-instruct-maas`).

The credentials used need Vertex AI access (`roles/aiplatform.user`) in the
project, and the models you want must be enabled in the Model Garden. The
`global` endpoint serves Gemini and Claude and offers the best availability;
regional endpoints (for example `europe-west1` or `us-east5`) can be set via
`GOOGLE_CLOUD_LOCATION` for data-residency requirements. Partner/open-weight
(MaaS) models are region-specific, so set `GOOGLE_CLOUD_LOCATION` explicitly when
using them.

Note that `GOOGLE_CLOUD_PROJECT` (and `GOOGLE_APPLICATION_CREDENTIALS`, if you
choose to store it there) is persisted to `~/.openwiki/.env` and loaded into the
OpenWiki process environment at startup when not already set — values already
present in your shell always win.

For CI, authenticate before the update job runs — for example with
[`google-github-actions/auth`](https://github.com/google-github-actions/auth)
(workload identity federation) in GitHub Actions — and set
`OPENWIKI_PROVIDER=gemini-enterprise` and `GOOGLE_CLOUD_PROJECT` in the job
environment.

Base URLs (and all credentials) can be set in your environment or stored in `~/.openwiki/.env`.

### OpenRouter provider pinning

[Permalink: OpenRouter provider pinning](https://github.com/langchain-ai/openwiki#openrouter-provider-pinning)

When OpenRouter serves a model through multiple upstream providers, set
`OPENWIKI_OPENROUTER_PROVIDER_ONLY` to restrict routing to one provider or a
comma-separated provider allowlist:

```
OPENWIKI_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
OPENWIKI_OPENROUTER_PROVIDER_ONLY=Novita
```

### Provider retry attempts

[Permalink: Provider retry attempts](https://github.com/langchain-ai/openwiki#provider-retry-attempts)

OpenWiki uses LangChain's built-in retry handling for transient provider errors.
To override the number of retries after the first provider request, set `OPENWIKI_PROVIDER_RETRY_ATTEMPTS`:

```
OPENWIKI_PROVIDER_RETRY_ATTEMPTS=3
```

The value must be a positive integer. If the value is unset, OpenWiki defaults to 3 retries.

If there's an inference provider or model you'd like to see added, please open a PR!

## Telemetry

[Permalink: Telemetry](https://github.com/langchain-ai/openwiki#telemetry)

OpenWiki collects anonymous, aggregate usage data so we can understand how the
tool is used and improve it. Telemetry is on by default and easy to turn off.

**What is collected**, on a single `openwiki_run` event, keyed by a random
install ID stored locally in `~/.openwiki/install-id`:

- Every run: the command (init / update) and the outcome (success / failure /
no-op), plus a coarse error category on failure (never the error message).
Interactive chat, `auth`, and `ingest` are not recorded.
- At setup (on init only): which brain mode (code / personal), the model
provider, and which connectors you configured (connector names only, never
their contents).

**What is never collected:** file contents, repository data or names,
credentials, prompts, model output, connector payloads, error messages, file
paths, URLs, model IDs, run duration, your IP address, or any personal
information. Geoip enrichment is disabled and your IP is never stored. Events
are grouped by your random install ID so we can measure repeat usage, but that
ID contains no personal data.

**Scheduled/CI runs** are collected as anonymous reliability data (tagged so
they can be told apart from human runs), under a shared CI identifier rather than
a per-machine install ID, and never counted as distinct installs. To disable in
CI, set `OPENWIKI_TELEMETRY_DISABLED=1` in your workflow environment.

To see exactly what a run would send, add `--telemetry-file=<path>` to any run.

### Opting out

[Permalink: Opting out](https://github.com/langchain-ai/openwiki#opting-out)

Set either environment variable:

```
export OPENWIKI_TELEMETRY_DISABLED=1
# or the cross-tool standard:
export DO_NOT_TRACK=1
```

To disable permanently, add `OPENWIKI_TELEMETRY_DISABLED=1` to `~/.openwiki/.env`.
In CI, set it in the workflow environment (config files do not persist on
ephemeral runners).

### Seeing exactly what is sent

[Permalink: Seeing exactly what is sent](https://github.com/langchain-ai/openwiki#seeing-exactly-what-is-sent)

Add `--telemetry-file=<path>` to any run to also write the exact payload to a
local JSON file.

## Contributing

[Permalink: Contributing](https://github.com/langchain-ai/openwiki#contributing)

Contributions are welcome! Please read [CONTRIBUTING.md](https://github.com/langchain-ai/openwiki/blob/main/CONTRIBUTING.md) before opening a PR. We intentionally keep PRs tightly scoped to one change each, and PRs that bundle unrelated changes may be closed with a request to split them.

## About

OpenWiki is a CLI that writes and maintains agent documentation for your codebase.


### Resources

[Readme](https://github.com/langchain-ai/openwiki#readme-ov-file)

### License

[MIT license](https://github.com/langchain-ai/openwiki#MIT-1-ov-file)

### Code of conduct

[Code of conduct](https://github.com/langchain-ai/openwiki#coc-ov-file)

### Contributing

[Contributing](https://github.com/langchain-ai/openwiki#contributing-ov-file)

### Security policy

[Security policy](https://github.com/langchain-ai/openwiki#security-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/langchain-ai/openwiki).

[Activity](https://github.com/langchain-ai/openwiki/activity)

[Custom properties](https://github.com/langchain-ai/openwiki/custom-properties)

### Stars

**12.6k**
stars


### Watchers

**39**
watching


### Forks

[**865**\\
forks](https://github.com/langchain-ai/openwiki/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Flangchain-ai%2Fopenwiki&report=langchain-ai+%28user%29)

## [Releases\  8](https://github.com/langchain-ai/openwiki/releases)

[0.2.0\\
Latest\\
\\
4 days agoJul 16, 2026](https://github.com/langchain-ai/openwiki/releases/tag/0.2.0)

[\+ 7 releases](https://github.com/langchain-ai/openwiki/releases)

## [Packages\  0](https://github.com/orgs/langchain-ai/packages?repo_name=openwiki)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/langchain-ai/openwiki).

## [Contributors\  43](https://github.com/langchain-ai/openwiki/graphs/contributors)

- [![@bracesproul](https://avatars.githubusercontent.com/u/46789226?s=64&v=4)](https://github.com/bracesproul)
- [![@colifran](https://avatars.githubusercontent.com/u/131073567?s=64&v=4)](https://github.com/colifran)
- [![@claude](https://avatars.githubusercontent.com/u/81847?s=64&v=4)](https://github.com/claude)
- [![@HwangJohn](https://avatars.githubusercontent.com/u/16890972?s=64&v=4)](https://github.com/HwangJohn)
- [![@github-actions[bot]](https://avatars.githubusercontent.com/in/15368?s=64&v=4)](https://github.com/apps/github-actions)
- [![@himanshu231204](https://avatars.githubusercontent.com/u/145797211?s=64&v=4)](https://github.com/himanshu231204)
- [![@bikeusaland](https://avatars.githubusercontent.com/u/7084906?s=64&v=4)](https://github.com/bikeusaland)
- [![@christian-bromann](https://avatars.githubusercontent.com/u/731337?s=64&v=4)](https://github.com/christian-bromann)
- [![@ppsplus-bradh](https://avatars.githubusercontent.com/u/16724189?s=64&v=4)](https://github.com/ppsplus-bradh)
- [![@jkennedyvz](https://avatars.githubusercontent.com/u/65985482?s=64&v=4)](https://github.com/jkennedyvz)
- [![@jyje](https://avatars.githubusercontent.com/u/109659358?s=64&v=4)](https://github.com/jyje)
- [![@zan22ye](https://avatars.githubusercontent.com/u/116149836?s=64&v=4)](https://github.com/zan22ye)
- [![@varaprasadreddy9676](https://avatars.githubusercontent.com/u/30567269?s=64&v=4)](https://github.com/varaprasadreddy9676)
- [![@dependabot[bot]](https://avatars.githubusercontent.com/in/29110?s=64&v=4)](https://github.com/apps/dependabot)

[\+ 29 contributors](https://github.com/langchain-ai/openwiki/graphs/contributors)

## Languages

- [TypeScript87.5%](https://github.com/langchain-ai/openwiki/search?l=typescript)
- [JavaScript12.5%](https://github.com/langchain-ai/openwiki/search?l=javascript)

You can’t perform that action at this time.