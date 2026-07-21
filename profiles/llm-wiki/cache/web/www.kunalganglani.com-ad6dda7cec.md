[Skip to content](https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base#main-content)

![Computer screens displaying code with neon lighting.](https://img.kunalganglani.com/images/vzekdneq/production/440d5339746278e617b15c8e10db8aa1c0dd09c5-1200x675.webp?auto=format&fit=max&q=75&w=1200)

Listen to this article

--:--1x

An [LLM](https://www.kunalganglani.com/glossary/llm) Wiki is a persistent, structured knowledge base made of interlinked markdown files that an [LLM](https://www.kunalganglani.com/glossary/large-language-model) agent builds and maintains for you. Instead of re-deriving answers from raw documents on every query like [RAG](https://www.kunalganglani.com/glossary/retrieval-augmented-generation), it compiles knowledge once and keeps it current.

Andrej Karpathy posted [a GitHub gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) in April 2026 describing this pattern. It now has 5,000+ stars and 5,000+ forks. I've been running it daily for three months, and I think it's the most [interesting](https://www.kunalganglani.com/blog/yann-lecun-h-ai-startup-paris-funding) shift in personal knowledge management since Obsidian itself. But the gist is a starting point, not a finished product. Here's what actually works after sustained daily use — and where it falls apart.

**Key takeaways:**

- The LLM Wiki pattern compiles knowledge into persistent, interlinked markdown files rather than re-retrieving raw chunks on every query like traditional [RAG](https://www.kunalganglani.com/glossary/rag).
- Setting up your own LLM Wiki requires an Obsidian vault, a coding agent like [Claude Code](https://www.kunalganglani.com/blog/aider-vs-claude-code) or OpenAI Codex, and the Karpathy gist pasted into your agent's system prompt.
- Incremental updates are the killer feature: you point the agent at new source material and it surgically updates only the affected wiki pages.
- The pattern breaks down when your wiki exceeds roughly 200 files and your agent can't hold the full graph in context. Directory-level indexes are the fix.
- There is no official "LLM Wiki v2" — but the community has iterated on the original gist with contradiction-checking prompts and auto-index generation.

> The LLM Wiki is a compiler for knowledge, not a search engine.

## What Is an LLM Wiki and Why Should You Care?

Most engineers have tried uploading documents to ChatGPT or Google's NotebookLM. You drop in 10 PDFs, ask a question, get a synthesized answer from retrieved chunks. It works. But ask a different question tomorrow and the model starts from scratch. No accumulation. No cross-referencing. No compounding understanding.

![silver electrical part](https://img.kunalganglani.com/images/vzekdneq/production/a6b7bd6e69759867f8c8a73c49e2fe9944f1ba7b-1200x675.webp?auto=format&fit=max&q=80&w=900)

The LLM Wiki flips this entirely. As [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), former Director of AI at Tesla and co-founder of OpenAI, puts it: "The knowledge is compiled once and then kept current, not re-derived on every query. This is the key difference: the wiki is a persistent, compounding artifact."

In practice, it's a folder of markdown files that an LLM agent reads, writes, and maintains. Each file represents an entity, topic, or theme. The agent creates cross-links between pages, flags contradictions between sources, and updates summaries as you feed in new material. You never write the wiki yourself. You source, explore, and ask questions. The LLM does the grunt work.

This matters because the gap between "I uploaded some files" and "I have a queryable knowledge base" is enormous. The LLM Wiki pattern bridges it. Based on the search data I track at kunalganglani.com, the query "llm wiki" alone generates over 20,000 impressions per quarter. Thousands of engineers are looking for exactly this kind of structured approach to [local AI](https://www.kunalganglani.com/pillars/local-llms-complete-guide) knowledge management.

## The Karpathy Gist Explained: What It Actually Says

The gist (ID `442a6bf555914893e9891c11519de94f`) is surprisingly short. It's not a tool. Not an installable package. Not even a script. It's a prompt pattern — what Karpathy calls "an idea file, designed to be copy pasted to your own LLM Agent."

![black fan device close-up photography](https://img.kunalganglani.com/images/vzekdneq/production/76beafb78b6f19b7ed6235232857078a023801c2-1200x675.webp?auto=format&fit=max&q=80&w=900)

Here's what the gist actually contains:

1. **The core idea** — a prose explanation of why compiling knowledge into a wiki beats RAG-style retrieval for personal knowledge management.
2. **The workflow description** — Karpathy's split-screen setup with an LLM agent on one side and Obsidian on the other.
3. **Three use cases** — Personal (goals, health, journal entries), Research (papers, articles, evolving thesis), and Book reading (chapter-by-chapter synthesis with character and theme pages).
4. **Implicit instructions for the agent** — the gist is written so that when you paste it into an agent's context, the agent understands what kind of wiki to build, how to structure pages, and how to handle cross-references.

The most important line in the gist is Karpathy's metaphor: "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase." This framing matters because it tells you exactly how to think about the relationship between your tools. You're not "chatting with AI about your notes." You're running a build process that produces a structured artifact.

What the gist does NOT contain: specific directory structures, agent prompt templates, contradiction-handling logic, or guidance on what to do when your wiki grows beyond the agent's context window. Those gaps are where real daily usage teaches you the most.

## The Karpathy Method: Compile Knowledge Once, Query It Forever

The "Karpathy method" — a term the community adopted, not one Karpathy himself uses — boils down to one [architectural](https://www.kunalganglani.com/blog/javascript-bloat-causes-fixes) decision: **treat knowledge management as a compilation step, not a retrieval step.**

![Nvidia logo on a green background with abstract spheres.](https://img.kunalganglani.com/images/vzekdneq/production/0a35f113b2a927c93b894c441a8e48d93a53f915-1200x675.webp?auto=format&fit=max&q=80&w=900)

In traditional [RAG](https://www.kunalganglani.com/blog/fine-tuning-vs-rag-prompt-engineering), you store raw documents, embed chunks into a [vector database](https://www.kunalganglani.com/glossary/vector-database), and retrieve relevant fragments at query time. The model synthesizes on the fly. This is stateless. Every query pays the full synthesis cost.

The Karpathy method inverts this. You pay the synthesis cost once, up front, when you ingest a new source. The agent reads the source, extracts entities and claims, and writes them into the wiki's existing page structure. From that point on, the knowledge is pre-compiled into browsable, interlinked markdown. Querying is just reading.

This connects to something I learned building the RAG pipeline for Walmart's conversational commerce chatbot at Firework: retrieval quality, not model choice, dominated answer quality at scale. We were handling millions of queries daily, and the thing that moved the needle wasn't swapping models — it was improving how we retrieved and structured the context. The LLM Wiki takes that lesson to its logical conclusion: if retrieval quality matters most, why not eliminate retrieval entirely and pre-compile the answers?

Of course, it's not that simple. Pre-compilation works brilliantly for personal knowledge bases where you control all the sources. It doesn't replace RAG for production systems with millions of documents and real-time updates. But for the individual engineer building a research wiki, an architecture decision log, or a reading tracker? The Karpathy method is genuinely better.

📬 Stay in the loop

### Get new posts on AI, engineering, and emerging tech.

One useful email a week — no spam, unsubscribe anytime.

Subscribe

[Free: RAG Architecture Playbook (PDF)](https://www.kunalganglani.com/rag-architecture-playbook) [Or subscribe via RSS](https://www.kunalganglani.com/rss.xml)

## LLM Wiki vs. RAG: The Key Difference

The confusion between LLM Wiki and RAG is understandable. Both involve LLMs and documents. But they're architecturally different in ways that matter for how you build on top of them.

| Dimension | Traditional RAG | LLM Wiki (Karpathy Method) |
| --- | --- | --- |
| \*\*When synthesis happens\*\* | At query time | At ingestion time |
| \*\*Knowledge state\*\* | Stateless — rebuilt per query | Persistent — compounding artifact |
| \*\*Cross-referencing\*\* | Implicit (embedding similarity) | Explicit (markdown links between pages) |
| \*\*Contradiction handling\*\* | None — conflicts surface randomly | Active — agent flags conflicts during ingestion |
| \*\*Infrastructure needed\*\* | Vector DB, embedding model, retrieval pipeline | Markdown folder + LLM agent |
| \*\*Best for\*\* | Large-scale, many-user, real-time systems | Personal/team knowledge bases, research |
| \*\*Scales to\*\* | Millions of documents | Hundreds of pages (context-limited) |
| \*\*Offline capable\*\* | Only with \[local LLM\](/blog/lm-studio-vs-ollama) + local vector DB | Yes, with any local agent |

The critical tradeoff: RAG scales horizontally with more documents. The LLM Wiki scales vertically with deeper synthesis. If you need to search 100,000 support tickets, use RAG. If you need to synthesize 50 research papers into a coherent understanding, the LLM Wiki wins and it's not close.

For a deeper dive on where RAG fits versus other approaches, see my [decision framework](https://www.kunalganglani.com/blog/fine-tuning-vs-rag-prompt-engineering) for fine-tuning vs RAG vs [prompt engineering](https://www.kunalganglani.com/blog/context-engineering-ai-agents).

## Setting Up Your Own LLM Wiki: Step-by-Step

The setup process is deceptively simple. Getting it running takes 15 minutes. Getting it running _well_ takes a few weeks of iteration. Here's the workflow I've settled on:

**Step 1: Create your Obsidian vault.** Make a new vault (or a dedicated subfolder in an existing one). Create three top-level directories: `sources/` for raw input files, `wiki/` for the compiled pages the agent will write, and `_index/` for auto-generated directory listings.

**Step 2: Choose your agent.** You need a coding agent that can read and write local files. [Claude Code](https://www.kunalganglani.com/blog/aider-vs-claude-code-openhands-cli), OpenAI Codex, and Gemini CLI all work. More on which one to pick in the next section.

**Step 3: Paste the Karpathy gist into your agent's system prompt.** Copy the full text from [the gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and add it to your agent's SYSTEM or project instructions. This gives the agent the mental model for how to structure the wiki.

**Step 4: Add your first source.** Drop a document (PDF, markdown, plain text) into `sources/`. Tell the agent: "Read sources/my-paper.pdf and integrate it into the wiki. Create new entity pages as needed, update existing pages if they're affected, and add cross-links."

**Step 5: Review in Obsidian.** Open the graph view. You should see new nodes appearing with links between them. Read through the generated pages. Fair warning: the first ingestion is the messiest. The agent is building the wiki's skeleton from scratch, and it'll make some weird structural choices you'll want to correct.

**Step 6: Iterate.** Ask questions about the material. The agent will sometimes update wiki pages as it discovers gaps. Add more sources. The wiki compounds.

The file structure I've landed on: the `wiki/` directory contains one markdown file per entity or topic (e.g., `wiki/transformer-architecture.md`, `wiki/attention-mechanisms.md`). Each file has a YAML frontmatter block with tags and a last-updated date. The `_index/` directory contains auto-generated listings that help the agent navigate when the wiki grows large.

Here's a video walkthrough that covers the beginner setup visually:

## Which LLM Agents Work Best With the LLM Wiki Pattern

The gist mentions OpenAI Codex, [Claude Code](https://www.kunalganglani.com/blog/cursor-vs-claude-code), and OpenCode by name. I've tested all three plus Gemini CLI. Here's where I've landed:

**Claude Code** is the best option right now. It handles long file reads well, writes clean markdown with proper cross-links, and its agentic loop naturally supports the "read source, update multiple wiki pages" workflow. The 200K context window means it can hold a reasonably large wiki in memory during updates. The downside is obvious: you're paying per token for every wiki maintenance session, and those sessions add up.

**OpenAI Codex** works but has an annoying habit of restructuring existing pages. Where [Claude Code](https://www.kunalganglani.com/pillars/developer-tools-workflow) makes surgical edits, Codex sometimes rewrites entire pages when only a paragraph needed updating. This causes wiki drift over time. It's gotten better since its June 2026 update, but I still get more predictable diffs from Claude Code.

**Gemini CLI** has the largest context window (1M+ tokens), which should make it ideal for large wikis. In practice, the quality of its cross-referencing is weaker. It creates pages but misses obvious links between related entities. For wikis under 50 pages, it's fine. Beyond that, Claude Code produces a better-connected graph.

**Local models via Ollama** — the question I get asked most. Can you run the LLM Wiki pattern with a [local LLM](https://www.kunalganglani.com/pillars/local-llms-complete-guide)? Yes, but with real caveats. You need a model with strong instruction-following and file-editing capabilities. Qwen3 32B and Llama 3 70B (both via [Ollama](https://www.kunalganglani.com/blog/ollama-vs-llama-cpp)) can handle basic wiki maintenance, but they struggle with complex multi-page updates. If you're running on an M4 Max with 64GB unified memory, it's usable. On anything less, the context limitations make it frustrating. See my [local LLM hardware](https://www.kunalganglani.com/blog/local-llm-hardware-requirements-2026) guide for what you actually need.

## How to Update Your LLM Wiki With New Content Without a Full Rewrite

This is the most asked question I see, and the one the original gist barely addresses. The incremental update workflow is the pattern's killer feature once you get it right.

Here's the process that works:

**Drop the new source into \`sources/\`.** Any format your agent can read.

**Have the agent identify affected pages first.** Prompt: "Read sources/new-paper.pdf. List which existing wiki pages would need updates based on this new information. Don't make changes yet." This step matters more than you'd think. Without it, you lose control of the blast radius.

**Review the affected-page list.** Sometimes the agent identifies 15 pages; you might only want 5 updated. This is your chance to scope the update.

**Instruct surgical updates.** Prompt: "Update only wiki/ [transformer](https://www.kunalganglani.com/glossary/transformer)-architecture.md and wiki/attention-mechanisms.md with the new findings from sources/new-paper.pdf. Preserve existing content, add new information, and flag any contradictions."

**Run a contradiction check.** Prompt: "Scan the wiki for any claims that now contradict each other after the latest update. List them with page references."

**Review diffs in Obsidian.** If you're using git (and you should be), `git diff` shows exactly what changed.

The key insight: never tell the agent to "update the wiki" without scoping which pages. An unscoped update on a 100+ page wiki will burn tokens, produce unnecessary rewrites, and introduce subtle inconsistencies. I learned this the hard way. Scoped, surgical updates are how the pattern stays maintainable.

This process takes 2-5 minutes per new source with Claude Code. That's dramatically faster than manually reading a paper and updating your own notes. And the cross-referencing quality is honestly better than what most people would do by hand, myself included.

## LLM Wiki v2: Is There an Updated Version?

Let me be direct: there is no official "LLM Wiki v2." Karpathy's gist has had only one revision since April 4, 2026. The gist is version 1, and it's still the canonical reference.

So why are people searching for "llm wiki v2"?

**Community forks.** With 5,000+ forks, the community has iterated aggressively. The most useful forks add contradiction-checking prompts, auto-index generation scripts, and templates for specific use cases (engineering ADRs, book notes, research synthesis). These are "v2" in spirit, but none is endorsed by Karpathy.

**Agent improvements.** Claude Code, Codex, and Gemini CLI have all shipped meaningful updates since April 2026. The wiki pattern works noticeably better today than it did at launch, not because the pattern changed, but because the agents executing it got smarter. Claude Code's improved file-diff handling in its June 2026 update makes surgical page updates much more reliable.

**Expectation of a formal tool.** Some people searching "llm wiki v2" expect a packaged application with a GUI. That doesn't exist, and I'd argue it shouldn't. The pattern's strength is its simplicity: markdown files, an agent, and a text editor. Wrapping it in a tool would add complexity without earning its keep.

If you want the closest thing to "v2," take the original gist, add the scoped-update workflow from the previous section, and add an auto-generated `_index/master-index.md` file that lists every wiki page with a one-line summary. That index file is the single biggest improvement over the raw gist.

## LLM Wiki vs. Notion AI vs. Obsidian Plugins: What's Actually Different?

**Notion AI** queries your workspace content to generate answers. Convenient, but it's RAG under the hood — stateless retrieval, no persistent synthesis, and your data lives on Notion's servers. If you need [local AI](https://www.kunalganglani.com/blog/self-hosted-ai-tools-replace-saas) and data sovereignty, Notion AI is disqualified immediately.

**Obsidian plugins** (Copilot, Smart Connections, etc.) add LLM capabilities to Obsidian. They can search your vault, generate summaries, and answer questions about your notes. But they don't build or maintain a structured wiki for you. You're still the one creating pages, writing summaries, and managing cross-links. The LLM assists. It doesn't own the knowledge structure.

**The LLM Wiki pattern** inverts the ownership model entirely. The LLM owns the wiki's structure and content. You own the sources and the questions. You become the curator and editor, not the author.

The practical difference after three months: my research wiki has 147 interlinked pages covering distributed systems architecture. I wrote zero of those pages by hand. I added 43 source documents (papers, blog posts, internal ADRs) and asked roughly 200 questions. The wiki built itself. With Notion AI or Obsidian plugins, I'd still be on page 30, writing by hand and hoping I remembered to cross-link everything.

## Common Failure Modes and How to Fix Them

The LLM Wiki pattern is not without real problems. Here's what actually goes wrong in practice:

**Context window overflow.** This is the #1 issue. When your wiki grows past roughly 150-200 pages, most agents can't hold the full wiki in context during an update. The agent starts "forgetting" pages exist and creates duplicates or misses cross-links. **Fix:** Use a master index file (`_index/master-index.md`) that lists every page with a one-line summary. Tell the agent to read the index first, then only load the pages it needs. This keeps context usage manageable even at 300+ pages.

**Wiki drift.** Over time, the agent's writing style shifts. Early pages are terse. Later pages get verbose. Entity naming becomes inconsistent ("transformer" vs "Transformer architecture" vs "the attention model"). **Fix:** Add a style guide to your agent's system prompt. Define naming conventions, page length targets, and structural templates. Review and normalize every 20-30 new sources.

**Contradiction accumulation.** The agent flags contradictions when you explicitly ask, but it doesn't always catch them during routine updates. Contradictory claims can coexist across pages for weeks before you notice. **Fix:** Run a dedicated contradiction-check prompt weekly. Prompt: "Read every page in wiki/ and list any claims that contradict each other, with page references and the source that supports each claim."

**Stale pages.** Some pages get created during early ingestion and never updated, even when later sources contain relevant new information. **Fix:** Track page freshness with YAML frontmatter (`last_updated: 2026-07-10`). Periodically prompt: "List all wiki pages not updated in the last 30 days that have relevant new information in sources added since their last update."

**Over-linking.** The agent sometimes creates links to pages that don't exist yet, or links every single mention of a term even when the link adds nothing. This is the least harmful problem but the most annoying. **Fix:** Tell the agent to only link the first mention of an entity per page, and to never create links to non-existent pages.

## My Honest Assessment After Three Months

When I first wrote about this pattern in April 2026, I'd been using it for two weeks. Now it's July. Here's what changed with sustained daily use.

**What held up:** The core insight — compile, don't retrieve — is sound. My research wiki is genuinely more useful than any RAG-based system I've used for personal work. When I need to understand how a concept connects to 5 other concepts, the wiki already has those connections mapped. That compounding effect is real.

**What surprised me:** The pattern is more useful for engineering work than I expected. I've used it to synthesize architecture decision records, onboarding documentation, and competitive analysis. The "reading a book" use case Karpathy mentions is actually the weakest. Books have a narrative structure that the wiki format flattens in ways that lose important context.

**What disappointed me:** The maintenance burden. Every 2-3 weeks, I spend 30-45 minutes running contradiction checks, normalizing terminology, and cleaning up stale pages. That's not nothing. It's less work than maintaining the wiki manually would be, but "zero maintenance" this is not.

**The honest bottom line:** If you regularly synthesize information from multiple sources — research papers, technical docs, articles, meeting notes — the LLM Wiki pattern will save you hours per week. If you occasionally look something up, stick with [NotebookLM](https://www.kunalganglani.com/blog/notebooklm-agentic-ai-coding-guide) or ChatGPT file uploads. The LLM Wiki rewards consistent use and falls apart under neglect.

Running this blog's own [agent pipeline](https://www.kunalganglani.com/blog/context-engineering-ai-agents) has reinforced something I keep relearning: knowledge artifacts — whether they're wiki pages, prompt templates, or production RAG indexes — compound in value only if you maintain them. The moment you stop feeding new sources and running quality checks, the wiki starts decaying. That's not a flaw in the pattern. That's the nature of any living knowledge system.

## What Comes Next for the LLM Wiki Pattern

Three predictions:

**Agent-native IDEs will absorb the pattern.** Right now, you need to manually set up the Obsidian-plus-agent workflow. Within 6 months, I expect [Claude Code](https://www.kunalganglani.com/blog/free-claude-code-alternatives), Cursor, or Windsurf to ship built-in "wiki mode" features that automate the compilation step. The pattern is too useful and too simple to stay as a gist forever.

**Context windows will make the scaling problem disappear.** The 150-200 page ceiling exists because of context limits. Gemini's 1M+ token window already pushes this higher. When 10M-token windows become standard — likely by early 2027 — the LLM Wiki pattern will scale to thousands of pages without the index workaround.

**The pattern will merge with \[RAG\](/glossary/retrieval-augmented-generation) in production systems.** For enterprise use, pure compilation doesn't scale and pure retrieval lacks depth. The hybrid — a structured wiki layer compiled on top of a RAG-searchable document store — is where this ends up. The wiki handles synthesis and cross-referencing; RAG handles breadth and freshness. Having built RAG pipelines at production scale, I'm convinced neither approach alone is sufficient. The interesting engineering happens at the seam between the two.

Karpathy's gist is three months old and already has 5,000+ forks. That's not hype. That's practitioners voting with their keyboards. The LLM Wiki isn't the future of all knowledge management. But for the individual engineer who's drowning in documents and tired of re-deriving the same answers from scratch, it's the best pattern available right now. Set it up this weekend.

## Frequently Asked Questions

### What is Karpathy's LLM Wiki?

It's a prompt pattern created by Andrej Karpathy for building personal knowledge bases using LLMs. Instead of retrieving document chunks on every query like RAG, an LLM agent compiles your source material into interlinked markdown files that form a persistent, growing wiki. The pattern lives in a GitHub gist with 5,000+ stars.

### How does the LLM Wiki differ from RAG?

RAG retrieves raw document chunks at query time and synthesizes an answer from scratch each time. The LLM Wiki compiles knowledge at ingestion time into structured wiki pages with explicit cross-references. RAG is stateless; the LLM Wiki is a persistent, compounding artifact that gets richer with every source you add.

### Can I run an LLM Wiki with a local model like Ollama?

Yes, but with caveats. You need a model with at least 32B parameters for reliable wiki maintenance. Qwen3 32B and Llama 3 70B work for basic updates but struggle with complex multi-page operations. You'll also need at least 64GB of memory on [Apple Silicon](https://www.kunalganglani.com/pillars/llm-hardware-local-ai) or a GPU with 24GB VRAM. It's usable but noticeably slower and less accurate than cloud agents.

### What happens when my wiki gets too large for the LLM's context window?

At roughly 150-200 pages, most agents can't hold the full wiki in context. The fix is a master index file that lists every page with a one-line summary. You instruct the agent to read the index first, then selectively load only the pages it needs for a given update. This extends practical capacity to 300+ pages.

### Does the LLM Wiki work offline?

If you pair it with a local model running through Ollama or llama.cpp, yes. The wiki itself is just markdown files on your machine. The only cloud dependency is the LLM agent, which can be swapped for a local alternative. Your data never needs to leave your machine.

### What is the Karpathy gist 442a6bf555914893e9891c11519de94f?

It's the GitHub gist ID for Karpathy's original LLM Wiki prompt pattern. The gist contains a prose explanation of the core idea, a workflow description, three use cases, and implicit instructions for an LLM agent. It's designed to be copied directly into your agent's system prompt. There's only been one revision since its April 4, 2026 creation.

Photo by Jakub Żerdzicki on Unsplash.

### Continue reading

[![machine learning python code embeddings nlp screen — illustration for article on RAG Context Window Limits:](https://img.kunalganglani.com/images/vzekdneq/production/62474180f496978c5226f53e6c2cd2ec12f298e7-1200x675.webp?auto=format&fit=max&q=75&w=500)\\
\\
**RAG Context Window Limits: Why Bigger Is Not Better \[2026\]** \\
\\
Expanding your context window from 4K to 128K tokens doesn't fix RAG — it masks retrieval failures with coherent-sounding hallucinations. Here's the measurement framework that actually works.\\
\\
July 15, 2026\\
\\
Read more](https://www.kunalganglani.com/blog/rag-context-window-limitations) [![black laptop computer turned on on table](https://img.kunalganglani.com/images/vzekdneq/production/fe5c4faead41cfc7a9455e18015fde9972097075-1200x675.webp?auto=format&fit=max&q=75&w=500)\\
\\
**Fine-Tuning vs RAG vs Prompt Engineering: Decision Framework \[2026\]** \\
\\
Stop guessing which LLM technique to use. A 2026-updated decision matrix with real cost figures, concrete examples, and a clear flowchart for when fine-tuning beats RAG, when RAG beats both, and when prompt engineering alone is the right answer.\\
\\
July 11, 2026\\
\\
Read more](https://www.kunalganglani.com/blog/fine-tuning-vs-rag-prompt-engineering) [![a close up of a computer motherboard with some wires attached to it](https://img.kunalganglani.com/images/vzekdneq/production/925658aecc55c4287a8a35407d94cc40dbc0beee-1200x675.webp?auto=format&fit=max&q=75&w=500)\\
\\
**Gemma 3 on Raspberry Pi 5: Benchmarked \[2026\]** \\
\\
I benchmarked every runnable Gemma variant on a Raspberry Pi 5 — Gemma 3 1B, 4B, QAT models, and Gemma 3n — with real tokens-per-second numbers, RAM usage, and a definitive size guide for Pi owners.\\
\\
April 12, 2026\\
\\
Read more](https://www.kunalganglani.com/blog/gemma-3-raspberry-pi-5-benchmark)

[#llm](https://www.kunalganglani.com/blog/tags/llm) [#knowledge-base](https://www.kunalganglani.com/blog/tags/knowledge-base) [#karpathy](https://www.kunalganglani.com/blog/tags/karpathy) [#obsidian](https://www.kunalganglani.com/blog/tags/obsidian) [#local-ai](https://www.kunalganglani.com/blog/tags/local-ai) [#rag](https://www.kunalganglani.com/blog/tags/rag) [#personal-knowledge-management](https://www.kunalganglani.com/blog/tags/personal-knowledge-management) [#markdown](https://www.kunalganglani.com/blog/tags/markdown)

FAQ

## Frequently Asked Questions

01What is Karpathy's LLM Wiki?

It's a prompt pattern created by Andrej Karpathy for building personal knowledge bases using LLMs. Instead of retrieving document chunks on every query like RAG, an LLM agent compiles your source material into interlinked markdown files that form a persistent, growing wiki. The pattern lives in a GitHub gist with 5,000+ stars.

02How does the LLM Wiki differ from RAG?

RAG retrieves raw document chunks at query time and synthesizes an answer from scratch each time. The LLM Wiki compiles knowledge at ingestion time into structured wiki pages with explicit cross-references. RAG is stateless; the LLM Wiki is a persistent, compounding artifact that gets richer with every source you add.

03Can I run an LLM Wiki with a local model like Ollama?

Yes, but with caveats. You need a model with at least 32B parameters for reliable wiki maintenance. Qwen3 32B and Llama 3 70B work for basic updates but struggle with complex multi-page operations. You'll also need at least 64GB of memory on Apple Silicon or a GPU with 24GB VRAM.

04What happens when my wiki gets too large for the LLM's context window?

At roughly 150-200 pages, most agents can't hold the full wiki in context. The fix is a master index file that lists every page with a one-line summary. You instruct the agent to read the index first, then selectively load only the pages it needs for a given update. This extends practical capacity to 300+ pages.

05Does the LLM Wiki work offline?

If you pair it with a local model running through Ollama or llama.cpp, yes. The wiki itself is just markdown files on your machine. The only cloud dependency is the LLM agent, which can be swapped for a local alternative. Your data never needs to leave your machine.

06What is the Karpathy gist 442a6bf555914893e9891c11519de94f?

It's the GitHub gist ID for Karpathy's original LLM Wiki prompt pattern. The gist contains a prose explanation of the core idea, a workflow description, three use cases, and implicit instructions for an LLM agent. It's designed to be copied directly into your agent's system prompt.

[![Kunal Ganglani](https://img.kunalganglani.com/images/vzekdneq/production/c74ecc731a051f3b238e0045444dd267f01d1615-800x800.jpg?auto=format&fit=max&q=75&w=160)](https://www.kunalganglani.com/about)

Written by · Published April 15, 2026 · Last reviewed July 11, 2026**[Kunal Ganglani](https://www.kunalganglani.com/about)**

Why trust this I built the /llm-benchmarks dataset (80+ measured rows) and the LLM Hardware Checker. [See proof →](https://www.kunalganglani.com/llm-benchmarks)

Software engineering leader based in Toronto with 10+ years shipping production systems at scale. Specializes in AI engineering, local LLMs, RAG pipelines, and AI agent architecture. Builder of the LLM Benchmarks dataset (80+ measured models), the LLM Hardware Checker, and LLM Prices tracker. Currently building at the intersection of AI and practical infrastructure.

Work with me
I help teams ship AI systems that survive production — architecture reviews, local-LLM
& hardware strategy, advisory calls. [See services →](https://www.kunalganglani.com/services)

[LinkedIn](https://www.linkedin.com/in/kunalganglani)[GitHub](https://github.com/kunalganglani)[Twitter / X](https://x.com/kunalganglani)

Share this post

[Share on X](https://twitter.com/intent/tweet?text=LLM%20Wiki%20Setup%3A%20Karpathy%27s%20Knowledge%20Base%20%5B2026%20Guide%5D&url=https%3A%2F%2Fwww.kunalganglani.com%2Fblog%2Fllm-wiki-karpathy-local-knowledge-base%3Futm_source%3Dtwitter%26utm_medium%3Dsocial%26utm_campaign%3Dblog_share) [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fwww.kunalganglani.com%2Fblog%2Fllm-wiki-karpathy-local-knowledge-base%3Futm_source%3Dlinkedin%26utm_medium%3Dsocial%26utm_campaign%3Dblog_share) [Reddit](https://reddit.com/submit?url=https%3A%2F%2Fwww.kunalganglani.com%2Fblog%2Fllm-wiki-karpathy-local-knowledge-base%3Futm_source%3Dreddit%26utm_medium%3Dsocial%26utm_campaign%3Dblog_share&title=LLM%20Wiki%20Setup%3A%20Karpathy%27s%20Knowledge%20Base%20%5B2026%20Guide%5D) [Hacker News](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fwww.kunalganglani.com%2Fblog%2Fllm-wiki-karpathy-local-knowledge-base%3Futm_source%3Dhackernews%26utm_medium%3Dsocial%26utm_campaign%3Dblog_share&t=LLM%20Wiki%20Setup%3A%20Karpathy%27s%20Knowledge%20Base%20%5B2026%20Guide%5D) Copy Link

Cite this article

APABibTeXMarkdown

```
Kunal Ganglani (2026, April 15). LLM Wiki Setup: Karpathy's Knowledge Base [2026 Guide]. Kunal Ganglani. Retrieved July 18, 2026, from https://www.kunalganglani.com/blog/llm-wiki-karpathy-local-knowledge-base
```

Copy citation

📬 Stay in the loop

### Get new posts on AI, engineering, and emerging tech.

One useful email a week — no spam, unsubscribe anytime.

Subscribe

[Free: RAG Architecture Playbook (PDF)](https://www.kunalganglani.com/rag-architecture-playbook) [Or subscribe via RSS](https://www.kunalganglani.com/rss.xml)