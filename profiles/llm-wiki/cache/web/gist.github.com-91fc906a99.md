[Skip to content](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#start-of-content)

[Gist Homepage ](https://gist.github.com/)

Search Gists

Search Gists

[Gist Homepage ](https://gist.github.com/)

[Sign in](https://gist.github.com/auth/github?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f) [Sign up](https://gist.github.com/join?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f&source=header-gist)

You signed in with another tab or window. [Reload](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) to refresh your session.You signed out in another tab or window. [Reload](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) to refresh your session.You switched accounts on another tab or window. [Reload](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) to refresh your session.Dismiss alert

{{ message }}

Instantly share code, notes, and snippets.


[![@karpathy](https://avatars.githubusercontent.com/u/241138?s=64&v=4)](https://gist.github.com/karpathy)

# [karpathy](https://gist.github.com/karpathy)/ **[llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)**

Created
3 months agoApril 4, 2026 16:25

Show Gist options

- [Download ZIP](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/archive/ac46de1ad27f92b28ac95459c782c07f6b8c964a.zip)

- [Star5,000+(5,000+)](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f) You must be signed in to star a gist
- [Fork5,000+(5,000+)](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f) You must be signed in to fork a gist

- Embed








# Select an option





























  - Embed
    Embed this gist in your website.
  - Share
    Copy sharable link for this gist.
  - Clone via HTTPS
    Clone using the web URL.

## No results found

[Learn more about clone URLs](https://docs.github.com/articles/which-remote-url-should-i-use)

Clone this repository at &lt;script src=&quot;https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f.js&quot;&gt;&lt;/script&gt;

- Save karpathy/442a6bf555914893e9891c11519de94f to your computer and use it in GitHub Desktop.

Embed

# Select an option

- Embed
Embed this gist in your website.
- Share
Copy sharable link for this gist.
- Clone via HTTPS
Clone using the web URL.

## No results found

[Learn more about clone URLs](https://docs.github.com/articles/which-remote-url-should-i-use)

Clone this repository at &lt;script src=&quot;https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f.js&quot;&gt;&lt;/script&gt;

Save karpathy/442a6bf555914893e9891c11519de94f to your computer and use it in GitHub Desktop.

[Download ZIP](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/archive/ac46de1ad27f92b28ac95459c782c07f6b8c964a.zip)

llm-wiki


[Raw](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/raw/ac46de1ad27f92b28ac95459c782c07f6b8c964a/llm-wiki.md)

[**llm-wiki.md**](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#file-llm-wiki-md)

# LLM Wiki

[Permalink: LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#llm-wiki)

A pattern for building personal knowledge bases using LLMs.

This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.). Its goal is to communicate the high level idea, but your agent will build out the specifics in collaboration with you.

## The core idea

[Permalink: The core idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#the-core-idea)

Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up. NotebookLM, ChatGPT file uploads, and most RAG systems work this way.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files that sits between you and the raw sources. When you add a new source, the LLM doesn't just index it for later retrieval. It reads it, extracts the key information, and integrates it into the existing wiki — updating entity pages, revising topic summaries, noting where new data contradicts old claims, strengthening or challenging the evolving synthesis. The knowledge is compiled once and then _kept current_, not re-derived on every query.

This is the key difference: **the wiki is a persistent, compounding artifact.** The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read. The wiki keeps getting richer with every source you add and every question you ask.

You never (or rarely) write the wiki yourself — the LLM writes and maintains all of it. You're in charge of sourcing, exploration, and asking the right questions. The LLM does all the grunt work — the summarizing, cross-referencing, filing, and bookkeeping that makes a knowledge base actually useful over time. In practice, I have the LLM agent open on one side and Obsidian open on the other. The LLM makes edits based on our conversation, and I browse the results in real time — following links, checking the graph view, reading the updated pages. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

This can apply to a lot of different contexts. A few examples:

- **Personal**: tracking your own goals, health, psychology, self-improvement — filing journal entries, articles, podcast notes, and building up a structured picture of yourself over time.
- **Research**: going deep on a topic over weeks or months — reading papers, articles, reports, and incrementally building a comprehensive wiki with an evolving thesis.
- **Reading a book**: filing each chapter as you go, building out pages for characters, themes, plot threads, and how they connect. By the end you have a rich companion wiki. Think of fan wikis like [Tolkien Gateway](https://tolkiengateway.net/wiki/Main_Page) — thousands of interlinked pages covering characters, places, events, languages, built by a community of volunteers over years. You could build something like that personally as you read, with the LLM doing all the cross-referencing and maintenance.
- **Business/team**: an internal wiki maintained by LLMs, fed by Slack threads, meeting transcripts, project documents, customer calls. Possibly with humans in the loop reviewing updates. The wiki stays current because the LLM does the maintenance that no one on the team wants to do.
- **Competitive analysis, due diligence, trip planning, course notes, hobby deep-dives** — anything where you're accumulating knowledge over time and want it organized rather than scattered.

## Architecture

[Permalink: Architecture](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#architecture)

There are three layers:

**Raw sources** — your curated collection of source documents. Articles, papers, images, data files. These are immutable — the LLM reads from them but never modifies them. This is your source of truth.

**The wiki** — a directory of LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it.

**The schema** — a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow when ingesting sources, answering questions, or maintaining the wiki. This is the key configuration file — it's what makes the LLM a disciplined wiki maintainer rather than a generic chatbot. You and the LLM co-evolve this over time as you figure out what works for your domain.

## Operations

[Permalink: Operations](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#operations)

**Ingest.** You drop a new source into the raw collection and tell the LLM to process it. An example flow: the LLM reads the source, discusses key takeaways with you, writes a summary page in the wiki, updates the index, updates relevant entity and concept pages across the wiki, and appends an entry to the log. A single source might touch 10-15 wiki pages. Personally I prefer to ingest sources one at a time and stay involved — I read the summaries, check the updates, and guide the LLM on what to emphasize. But you could also batch-ingest many sources at once with less supervision. It's up to you to develop the workflow that fits your style and document it in the schema for future sessions.

**Query.** You ask questions against the wiki. The LLM searches for relevant pages, reads them, and synthesizes an answer with citations. Answers can take different forms depending on the question — a markdown page, a comparison table, a slide deck (Marp), a chart (matplotlib), a canvas. The important insight: **good answers can be filed back into the wiki as new pages.** A comparison you asked for, an analysis, a connection you discovered — these are valuable and shouldn't disappear into chat history. This way your explorations compound in the knowledge base just like ingested sources do.

**Lint.** Periodically, ask the LLM to health-check the wiki. Look for: contradictions between pages, stale claims that newer sources have superseded, orphan pages with no inbound links, important concepts mentioned but lacking their own page, missing cross-references, data gaps that could be filled with a web search. The LLM is good at suggesting new questions to investigate and new sources to look for. This keeps the wiki healthy as it grows.

## Indexing and logging

[Permalink: Indexing and logging](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#indexing-and-logging)

Two special files help the LLM (and you) navigate the wiki as it grows. They serve different purposes:

**index.md** is content-oriented. It's a catalog of everything in the wiki — each page listed with a link, a one-line summary, and optionally metadata like date or source count. Organized by category (entities, concepts, sources, etc.). The LLM updates it on every ingest. When answering a query, the LLM reads the index first to find relevant pages, then drills into them. This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure.

**log.md** is chronological. It's an append-only record of what happened and when — ingests, queries, lint passes. A useful tip: if each entry starts with a consistent prefix (e.g. `## [2026-04-02] ingest | Article Title`), the log becomes parseable with simple unix tools — `grep "^## \[" log.md | tail -5` gives you the last 5 entries. The log gives you a timeline of the wiki's evolution and helps the LLM understand what's been done recently.\
\
## Optional: CLI tools\
\
[Permalink: Optional: CLI tools](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#optional-cli-tools)\
\
At some point you may want to build small tools that help the LLM operate on the wiki more efficiently. A search engine over the wiki pages is the most obvious one — at small scale the index file is enough, but as the wiki grows you want proper search. [qmd](https://github.com/tobi/qmd) is a good option: it's a local search engine for markdown files with hybrid BM25/vector search and LLM re-ranking, all on-device. It has both a CLI (so the LLM can shell out to it) and an MCP server (so the LLM can use it as a native tool). You could also build something simpler yourself — the LLM can help you vibe-code a naive search script as the need arises.\
\
## Tips and tricks\
\
[Permalink: Tips and tricks](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#tips-and-tricks)\
\
- **Obsidian Web Clipper** is a browser extension that converts web articles to markdown. Very useful for quickly getting sources into your raw collection.\
- **Download images locally.** In Obsidian Settings → Files and links, set "Attachment folder path" to a fixed directory (e.g. `raw/assets/`). Then in Settings → Hotkeys, search for "Download" to find "Download attachments for current file" and bind it to a hotkey (e.g. Ctrl+Shift+D). After clipping an article, hit the hotkey and all images get downloaded to local disk. This is optional but useful — it lets the LLM view and reference images directly instead of relying on URLs that may break. Note that LLMs can't natively read markdown with inline images in one pass — the workaround is to have the LLM read the text first, then view some or all of the referenced images separately to gain additional context. It's a bit clunky but works well enough.\
- **Obsidian's graph view** is the best way to see the shape of your wiki — what's connected to what, which pages are hubs, which are orphans.\
- **Marp** is a markdown-based slide deck format. Obsidian has a plugin for it. Useful for generating presentations directly from wiki content.\
- **Dataview** is an Obsidian plugin that runs queries over page frontmatter. If your LLM adds YAML frontmatter to wiki pages (tags, dates, source counts), Dataview can generate dynamic tables and lists.\
- The wiki is just a git repo of markdown files. You get version history, branching, and collaboration for free.\
\
## Why this works\
\
[Permalink: Why this works](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#why-this-works)\
\
The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping. Updating cross-references, keeping summaries current, noting when new data contradicts old claims, maintaining consistency across dozens of pages. Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass. The wiki stays maintained because the cost of maintenance is near zero.\
\
The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else.\
\
The idea is related in spirit to Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became: private, actively curated, with the connections between documents as valuable as the documents themselves. The part he couldn't solve was who does the maintenance. The LLM handles that.\
\
## Note\
\
[Permalink: Note](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#note)\
\
This document is intentionally abstract. It describes the idea, not a specific implementation. The exact directory structure, the schema conventions, the page formats, the tooling — all of that will depend on your domain, your preferences, and your LLM of choice. Everything mentioned above is optional and modular — pick what's useful, ignore what isn't. For example: your sources might be text-only, so you don't need image handling at all. Your wiki might be small enough that the index file is all you need, no search engine required. You might not care about slide decks and just want markdown pages. You might want a completely different set of output formats. The right way to use this is to share it with your LLM agent and work together to instantiate a version that fits your needs. The document's only job is to communicate the pattern. Your LLM can figure out the rest.\
\
Load earlier comments...\
\
[![@maurizio-persi](https://avatars.githubusercontent.com/u/291724620?s=80&v=4)](https://gist.github.com/maurizio-persi)\
\
### **[maurizio-persi](https://gist.github.com/maurizio-persi)**     commented    [2 weeks agoJun 30, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6224363\#gistcomment-6224363)\
\
\
Copy link\
\
\
Copy Markdown\
\
First of all, thanks to **[@karpathy](https://github.com/karpathy)** for introducing and describing the **LLM-Wiki** paradigm: a simple yet brilliant idea that, in my opinion, will revolutionize corporate document management (replacing heavy, complex knowledge bases), help students avoid superficial LLM usage, and serve as a great ally for methodical learning.\
\
I have built a **Personal LLM-Wiki** prioritizing two fundamental aspects:\
\
1. **Privacy**: All components run completely **offline**.\
2. **Efficiency**: I focused on creating an executable suitable for **modest hardware** (with or without a GPU), making it accessible despite current market prices for graphics cards.\
\
The core concept is straightforward: perform non-LLM-specific operations deterministically using standard Python libraries, which consume significantly fewer resources than a giant language model. It feels inefficient to waste LLM tokens on repetitive tasks that only require classic computational power.\
\
While my initial prototype worked, the model's responses were often too generic or limited to brief definitions. To achieve the exhaustive, structured lessons I envisioned, I integrated a few key components to enrich the context:\
\
### Key Components\
\
- **Graphify**: Maps relationships between Markdown files, SQL schemas, scripts, and PDFs. It improves navigation based on structural relationships rather than just keywords, creating a navigable "map" directly accessible to the AI or via **Obsidian**. This drastically reduced dependency on compute while improving coherence.\
- **ChromaDB**: A lightweight vector database used as the pillar for semantic search and document retrieval, executing operations efficiently on the CPU.\
- **NetworkX**: Manages a dual data structure in memory with a **lazy cache**: an _Undirected Graph ($G$)_ for generic relationships and a _Directed Graph ($DiG$)_ focused exclusively on formative dependencies. This helps identify correlations and cite diverse sources covering the requested topic.\
- **SQLite**: An embedded, serverless relational database dedicated to managing the system's transactional state and audit logs.\
\
### Operational Flow\
\
```\
[Phase 1 (Optional): Pre-processing (Whisper)] ──>\
──> [Phase 2: Synthesis (Qwen3VL)]\
──> [Phase 3: Graph Building (Graphify)]\
──> [Phase 4: Indexing (ChromaDB)]\
──> [Phase 5: Context Assembly]\
──> [Phase 6: Inference (Qwen3.5 9B)]\
```\
\
_Advanced features included: Semantic Query Cache, Cross-Encoder Re-Ranker, and Reciprocal Rank Fusion (RRF) for HyDE._\
\
### Additional Features\
\
- **Localization & UI**: Built a lightweight Flask web page with "on-the-fly" language switching managed via simple `.lng` files.\
- **Secure Telegram Bot**: Accessible without exposing ports or reverse proxies (restricted to authorized Telegram IDs). It includes an interactive poll after each response, allowing the user to save the text, export it as a Marp Markdown presentation, or generate an audio podcast.\
- **Quiz Mode**: Generates multiple-choice questions based on the wiki content with customizable difficulty, evaluating errors and explaining _why_ a specific answer was wrong.\
\
### A Critique of the Paradigm: No New Wiki Pages Without Raw Sources\
\
The only critique I have regarding the baseline LLM-Wiki paradigm concerns **creating new wiki pages derived from LLM responses**.\
\
I don't find it useful to generate additional pages beyond those processed during the **Ingest** phase. Reprocessing existing concepts in different forms consumes resources and slows down the system (more pages to scan per query) without introducing genuinely new information. Since the LLM should not invent anything (avoiding hallucinations), it doesn't enrich the source base.\
\
In my implementation, the only generated pages allowed are the Markdown files exported for **Presentations** (Marp syntax)-treated strictly as "output documents" for the user, rather than being re-fed into the pipeline as wiki sources.\
\
* * *\
\
I haven't published the repository on GitHub yet, as I am still refining the integration to make it as user-friendly as possible. I hope this architecture can serve as inspiration for anyone looking to customize or optimize their local LLM-Wiki setup!\
\
* * *\
\
### Below is an example of an answer to the question “Explain me what Kubernetes is.”\
\
![Personal LLM-WIKI](https://private-user-images.githubusercontent.com/291724620/615299575-1e0a9e98-b758-4292-91c0-34213afbade8.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjAsIm5iZiI6MTc4NDA3OTU2MCwicGF0aCI6Ii8yOTE3MjQ2MjAvNjE1Mjk5NTc1LTFlMGE5ZTk4LWI3NTgtNDI5Mi05MWMwLTM0MjEzYWZiYWRlOC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNzE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDcxNVQwMTM5MjBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03YzRkMDMzNWY1NDg0NTM3Mzg4NDE2MGNmYWZlYzA2NzE4MWQyYjkyZmM2YzgyMGRiNGY5MjkwYmY0MjJiZTBkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.tpSz3zNjSOMjKnUFjgGlWWnk_fX1kpkrGf1v8pf3qYM)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@RightL](https://avatars.githubusercontent.com/u/9251452?s=80&v=4)](https://gist.github.com/RightL)\
\
### **[RightL](https://gist.github.com/RightL)**     commented    [2 weeks agoJul 1, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6224846\#gistcomment-6224846)\
\
\
Copy link\
\
\
Copy Markdown\
\
Love this. I think the key idea is not “chatbot over files,” but “LLM-maintained structure that compounds.” We’re building RightMemory from a very similar motivation, but focused on memory for teams of coding agents.\
\
The core of RightMemory is ordinary Git-backed Markdown, with a small tree + graph schema. The tree gives agents readable local context through headings. The graph gives durable relationships through ids and typed edges, so facts, decisions, preferences, TODOs, and related project knowledge can point across sections and files. The memory stays inspectable as Markdown, but it is structured enough for agents to navigate precisely.\
\
A major design point is that this is not RAG. RightMemory is not primarily a vector database or a chunk retrieval layer. The durable artifact is the maintained Markdown memory itself. Retrieval reads the current structured memory; updates change the memory; consolidation improves it over time. The system is closer to an agent-maintained knowledge graph/wiki than to “embed documents and search at query time.”\
\
Another important part is teams of agents. RightMemory is designed so memory can survive across sessions, devices, agent clients, and collaborating agent teams. Different memory roots can share selected context through controlled shared views, so one project/person/team can expose only the relevant memory to another without dumping the whole private memory store.\
\
We also lean heavily into the CLI direction you mention. The `rightmemory` CLI is the main command surface, so any command-capable coding agent can use the same memory substrate. Codex, Claude Code, and other CLI-style agents can call the same retrieve/update/status/shared-view commands instead of memory being locked into one vendor UI.\
\
One more design choice I care a lot about: the roles are all pure agents with explicit authority boundaries. There is a retriever role for read-oriented memory lookup, an updater role for durable memory edits, a dreamer role for consolidation/restructuring, and a reviewer role for extracting useful memory from prior sessions. The main coding agent does not casually mutate memory while doing unrelated work; memory operations are delegated to the right role.\
\
So the overlap with your LLM Wiki pattern is strong: persistent Markdown, LLM-maintained structure, compounding context, and tooling around the artifact. RightMemory’s specific bet is that coding-agent memory should be tree + graph Markdown, operated through CLI-accessible agent roles, built for teams of agents, and not reduced to a RAG pipeline.\
\
Project: [https://github.com/RightL/RightMemory](https://github.com/RightL/RightMemory)\
\
Example memory file: [https://github.com/RightL/RightMemory/blob/main/MEMORY.example.md](https://github.com/RightL/RightMemory/blob/main/MEMORY.example.md)\
\
Schema: [https://github.com/RightL/RightMemory/blob/main/skills/rightmemory-schema.md](https://github.com/RightL/RightMemory/blob/main/skills/rightmemory-schema.md)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@ojuschugh1](https://avatars.githubusercontent.com/u/79078267?s=80&v=4)](https://gist.github.com/ojuschugh1)\
\
### **[ojuschugh1](https://gist.github.com/ojuschugh1)**     commented    [2 weeks agoJul 1, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6224960\#gistcomment-6224960)\
\
\
Copy link\
\
\
Copy Markdown\
\
```\
  ███████╗ ██████╗ ███████╗\
  ██╔════╝██╔═══██╗╚══███╔╝\
  ███████╗██║   ██║  ███╔╝\
  ╚════██║██║▄▄ ██║ ███╔╝\
  ███████║╚██████╔╝███████╗\
  ╚══════╝ ╚══▀▀═╝ ╚══════╝\
\
```\
\
**Compress LLM context to save tokens and reduce costs**\
\
**Real session stats:**\
3,003 compressions ·\
**178,442 tokens saved** ·\
24.7% avg reduction · up to\
**92%** with dedup\
\
\
[![Featured](https://camo.githubusercontent.com/9f424b754c999087f980222e8f2d783d8a847ade1fc1eb0a60eb6e09e1ab3347/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f253233315f46656174757265642d4e65787447656e5f546563685f496e73696465722d6666363630303f7374796c653d666f722d7468652d6261646765266c6f676f3d6e6577737061706572266c6f676f436f6c6f723d7768697465)](https://thenextgentechinsider.com/pulse/sqz-tool-cuts-llm-token-use-by-92-for-file-heavy-ai-tasks)\
\
[![Crates.io](https://camo.githubusercontent.com/5992ef7d1ecd6fc3dbf18deaf91eb8583cc39920ff9bc2e1f5076f9ac99aa66c/68747470733a2f2f696d672e736869656c64732e696f2f6372617465732f762f73717a2d636c693f6c6f676f3d72757374266c6f676f436f6c6f723d7768697465266c6162656c3d6372617465732e696f26636f6c6f723d653635323263)](https://crates.io/crates/sqz-cli)[![npm](https://camo.githubusercontent.com/cf6b7ae8cc98c0e20e798bd17ed662aad60a4f76da6b4602466f74b539973fb2/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f73717a2d636c693f6c6f676f3d6e706d266c6f676f436f6c6f723d7768697465266c6162656c3d6e706d26636f6c6f723d636233383337)](https://www.npmjs.com/package/sqz-cli)[![PyPI](https://camo.githubusercontent.com/d18c9d3ca7a79bd64676431c7c9cb9b912023a30b0e0d1939aa20525ea72d3ea/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f73717a3f6c6f676f3d707974686f6e266c6f676f436f6c6f723d7768697465266c6162656c3d5079504926636f6c6f723d333737356139)](https://pypi.org/project/sqz/)[![VS Code](https://camo.githubusercontent.com/b235ee4a2e4e94bba32f008f838cb45788954f51c4a005dc7ce02584d9c17708/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5653253230436f64652d4d61726b6574706c6163652d3030376163633f6c6f676f3d76697375616c2d73747564696f2d636f6465266c6f676f436f6c6f723d7768697465)](https://marketplace.visualstudio.com/items?itemName=ojuschugh1.sqz)[![Firefox](https://camo.githubusercontent.com/246171336432b050f4315b52b256f07b3186b9c655bcb2996e3184c5be80cba0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f46697265666f782d4164642d2d6f6e2d6666373133393f6c6f676f3d66697265666f782d62726f77736572266c6f676f436f6c6f723d7768697465)](https://addons.mozilla.org/en-US/firefox/addon/sqz-context-compression/)[![JetBrains](https://camo.githubusercontent.com/ac286c235c41b1a24767e226462f86a633b3eace5f4f2a045fe9be268b3b67d6/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4a6574427261696e732d506c7567696e2d3030303030303f6c6f676f3d6a6574627261696e73266c6f676f436f6c6f723d7768697465)](https://plugins.jetbrains.com/plugin/31240-sqz--context-intelligence/)[![Discord](https://camo.githubusercontent.com/0d826cd7a0ab371a4d9cf81809cd58868592eff15400669a872084e333d7e28c/68747470733a2f2f696d672e736869656c64732e696f2f646973636f72642f313439333235313032393037353233353037363f6c6f676f3d646973636f7264266c6f676f436f6c6f723d7768697465266c6162656c3d446973636f726426636f6c6f723d353836354632)](https://discord.gg/j8EEyH5dSB)[![Homebrew](https://camo.githubusercontent.com/bbe7d020ee9dcb0590a6a321f169a8aad13ad5a467b98fdbeba51d4294172a8c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f486f6d65627265772d7461702d4642423034303f6c6f676f3d686f6d6562726577266c6f676f436f6c6f723d7768697465)](https://github.com/ojuschugh1/homebrew-sqz)\
\
[Install](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#install) ·\
[How It Works](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#how-it-works) ·\
[Supported Tools](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#supported-tools) ·\
[Changelog](https://gist.github.com/karpathy/CHANGELOG.md) ·\
[Discord](https://discord.gg/j8EEyH5dSB)\
\
* * *\
\
sqz compresses command output before it reaches your LLM. Single Rust binary, zero config.\
\
The real win is dedup: when the same file gets read 5 times in a session, sqz sends it once and returns a 13-token reference for every repeat.\
\
```\
Without sqz:                    With sqz:\
\
File read #1:  2,000 tokens     File read #1:  ~800 tokens (compressed)\
File read #2:  2,000 tokens     File read #2:  ~13 tokens  (dedup ref)\
File read #3:  2,000 tokens     File read #3:  ~13 tokens  (dedup ref)\
───────────────────────         ───────────────────────\
Total:         6,000 tokens     Total:         ~826 tokens (86% saved)\
```\
\
## Token Savings\
\
> **24.7%** average reduction across 3,003 real compressions ·\
>\
> **92%** saved on repeated file reads ·\
>\
> **86%** on shell/git output ·\
>\
> **13-token** refs for cached content\
\
One developer's week, measured from actual `sqz gain` output:\
\
```\
$ sqz gain\
sqz token savings (last 7 days)\
──────────────────────────────────────────────────\
  04-13 │                              │   2,329 saved\
  04-14 │                              │       0 saved\
  04-15 │███                           │  12,954 saved\
  04-16 │██                            │   9,223 saved\
  04-17 │████                          │  14,752 saved\
  04-18 │██████████████████████████████│ 105,569 saved\
  04-19 │████████                      │  30,882 saved\
  04-20 │█                             │   4,334 saved\
──────────────────────────────────────────────────\
  Total: 3,003 compressions, 178,442 tokens saved (24.7% avg reduction)\
```\
\
### Per-command compression\
\
Single-command compression (measured via `cargo test -p sqz-engine benchmarks`):\
\
| Content | Before | After | Saved |\
| --- | --: | --: | --: |\
| Repeated log lines | 148 | 62 | **58%** |\
| Large JSON array | 259 | 142 | **45%** |\
| JSON API response | 64 | 53 | **17%** |\
| Git diff | 61 | 54 | **12%** |\
| Prose/docs | 124 | 121 | **2%** |\
| Stack trace (safe mode) | 82 | 82 | **0%** |\
\
### Session-level with dedup\
\
Where the real savings live — the cache sends each file once, repeats cost 13 tokens:\
\
| Scenario | Without sqz | With sqz | Saved |\
| --- | --: | --: | --: |\
| Same file read 5× | 10,000 | 826 | **92%** |\
| Same JSON response 3× | 192 | 79 | **59%** |\
| Test-fix-test cycle (3 runs) | 15,000 | 5,186 | **65%** |\
\
Single-command compression ranges from 2–58% depending on content. Repeated reads drop to 13 tokens each. Your mileage will vary with how repetitive your tool calls are — agentic sessions with many file re-reads see the biggest wins.\
\
## Install\
\
**Prebuilt binaries** (no compiler required — works on every platform):\
\
```\
# macOS / Linux\
curl -fsSL https://raw.githubusercontent.com/ojuschugh1/sqz/main/install.sh | sh\
\
# Windows (PowerShell)\
irm https://raw.githubusercontent.com/ojuschugh1/sqz/main/install.ps1 | iex\
\
# Any platform via npm\
npm install -g sqz-cli\
\
# macOS / Linux via Homebrew\
brew tap ojuschugh1/sqz\
brew install sqz\
```\
\
**Build from source via Cargo:**\
\
```\
cargo install sqz-cli sqz-mcp\
```\
\
`sqz-cli` provides the `sqz` binary; `sqz-mcp` provides the MCP server. `sqz-engine` is a library dependency — it compiles automatically and does not need to be installed separately.\
\
**Build from source** (`cargo install sqz-cli`) works too, but needs a C toolchain:\
\
- Linux: `build-essential` (apt) or equivalent\
- macOS: Xcode Command Line Tools (`xcode-select --install`)\
- **Windows: Visual Studio Build Tools with the "Desktop development with C++" workload.** Without these, `cargo install` fails with `linker link.exe not found`. If you don't already have them, use the PowerShell or npm install above instead.\
\
Then initialize:\
\
```\
sqz init --global     # hooks apply to every project on this machine\
# or\
sqz init              # hooks apply to just this project (.claude/settings.local.json)\
```\
\
`--global` writes to `~/.claude/settings.json` (the user scope per the\
\
[Anthropic scope table](https://docs.claude.com/en/docs/claude-code/settings)),\
\
so the sqz hook fires in every Claude Code session on this machine. This is\
\
the common case on first install. Your existing `permissions`, `env`,\
\
`statusLine`, and unrelated hooks in `~/.claude/settings.json` are\
\
preserved — sqz merges its entries rather than overwriting.\
\
Plain `sqz init` (project scope) is useful when you want sqz active only\
\
inside one repo.\
\
**Only using one agent?** Pass `--only` (or `--skip`) to limit which\
\
configs are written:\
\
```\
sqz init --only opencode              # just OpenCode, nothing else\
sqz init --only opencode,codex        # OpenCode and Codex\
sqz init --skip cursor,windsurf       # everything except Cursor and Windsurf\
```\
\
Accepted names: `claude`, `cursor`, `windsurf`, `cline`, `gemini`,\
\
`kiro`, `opencode`, `codex`. Aliases (`claude-code`, `gemini-cli`, `roo`,\
\
`kiro-cli`) also work. `--only` and `--skip` can't be combined.\
\
### Manual installation (preserve comments in your config)\
\
`sqz init` round-trips your config file through a JSON parser to merge\
\
the sqz entry, which drops any comments in your `opencode.jsonc` (and\
\
the analogous JSON-with-comments files other tools accept). If you've\
\
commented your config carefully and want to keep them, install by hand\
\
instead.\
\
**OpenCode** — two steps:\
\
1. Drop the plugin file in place. `sqz` prints the generated TS to\
\
\
stdout so you don't have to hand-write the path-escaping logic:\
\
\
\
```\
mkdir -p ~/.config/opencode/plugins\
sqz print-opencode-plugin > ~/.config/opencode/plugins/sqz.ts\
```\
\
2. Add the MCP entry to your existing `opencode.jsonc` yourself.\
\
\
Append this block inside the top-level `mcp` object (create the\
\
`mcp` object if it doesn't exist):\
\
\
\
```\
"sqz": {\
     "type": "local",\
     "command": ["sqz-mcp", "--transport", "stdio"],\
     "enabled": true\
}\
```\
\
\
Comments in the rest of your file stay put. OpenCode auto-discovers\
\
the plugin file; no `plugin` array entry needed (adding one causes\
\
double-loading, see issue #10).\
\
**Other tools** — Claude Code, Cursor, Windsurf, Cline, Gemini CLI,\
\
and Codex use plain JSON configs without comment support, so the\
\
automated path is non-destructive there. Use `sqz init --only <tool>`\
\
for those.\
\
That's it. Shell hooks installed, AI tool hooks configured.\
\
## How It Works\
\
![sqz system architecture](https://gist.github.com/karpathy/assets/sqz-architecture.png)\
\
sqz installs a PreToolUse hook that intercepts bash commands before your AI tool runs them. The output gets compressed transparently — the AI tool never knows.\
\
```\
Claude → git status → [sqz hook rewrites] → compressed output (85% smaller)\
```\
\
What gets compressed:\
\
- **Shell output** — 40+ per-command formatters (git, cargo, npm/pnpm/yarn, pytest, ruff, go test, docker, kubectl, aws, terraform, gradle, gh, grep/rg, tree, curl, and more)\
- **JSON** — strips nulls, compact encoding, TOON format\
- **Logs** — collapses repeated lines\
- **Test output** — shows failures only (state-machine parsers for Rust, Go, Python, JS, JVM)\
\
What doesn't get compressed:\
\
- Stack traces, error messages, secrets — routed to safe mode (0% compression)\
- Your prompts and the AI's responses — controlled by the AI tool, not sqz\
\
## Supported Tools\
\
| Tool | Integration | Setup |\
| --- | --- | --- |\
| Claude Code | PreToolUse hook (transparent) | `sqz init` |\
| Cursor | PreToolUse hook (transparent) | `sqz init` |\
| Windsurf | PreToolUse hook (transparent) | `sqz init` |\
| Cline | PreToolUse hook (transparent) | `sqz init` |\
| Gemini CLI | BeforeTool hook (transparent) | `sqz init` |\
| Kiro | PreToolUse hook (transparent) | `sqz init` |\
| OpenCode | TypeScript plugin (transparent) | `sqz init` |\
| VS Code | [Extension](https://marketplace.visualstudio.com/items?itemName=ojuschugh1.sqz) | Install from Marketplace |\
| JetBrains | [Plugin](https://plugins.jetbrains.com/plugin/31240-sqz--context-intelligence/) | Install from Marketplace |\
| Chrome | Browser extension | ChatGPT, Claude.ai, Gemini, Grok, Perplexity |\
| [Firefox](https://addons.mozilla.org/en-US/firefox/addon/sqz-context-compression/) | Browser extension | Same sites |\
\
## CLI\
\
```\
sqz init --global             # Install hooks for every project on this machine\
sqz init                      # Install hooks for just this project\
sqz init --only kiro          # Only configure Kiro (skip the rest)\
sqz init --only opencode      # Only configure OpenCode (skip the rest)\
sqz init --skip cursor        # Configure every agent except Cursor\
sqz compress <text>           # Compress (or pipe from stdin)\
sqz compress --no-cache       # Compress without dedup (always full output)\
sqz expand <ref>              # Recover original content from a §ref:HASH§ token\
sqz compact                   # Evict stale context to free tokens\
sqz reset                     # Clear dedup cache or compression stats\
sqz gain                      # Show daily token savings (bar chart)\
sqz gain --project .          # Per-project daily gains\
sqz gain --days 30            # Last 30 days\
sqz stats                     # Cumulative compression report\
sqz stats --breakdown         # Per-command token usage breakdown\
sqz stats --project .         # Stats for current project only\
sqz stats --project list      # List all tracked projects\
sqz discover                  # Find missed savings\
sqz resume                    # Re-inject session context after compaction\
sqz vizit                     # Live terminal dashboard (like htop for AI agents)\
sqz hook claude               # Process a PreToolUse hook (Claude Code)\
sqz hook kiro                 # Process a PreToolUse hook (Kiro)\
sqz print-opencode-plugin     # Print OpenCode plugin TS for manual install\
sqz proxy --port 8080         # API proxy (compresses full request payloads)\
```\
\
### Dedup Escape Hatch\
\
When sqz sees the same content twice, it returns a compact `§ref:HASH§` token\
\
instead of the full text. Most models handle this fine, but some (e.g., GLM 5.1)\
\
can't parse the ref format and loop. Four ways to work around this:\
\
```\
# 1. Recover original content from a ref\
sqz expand a1b2c3d4              # prefix match\
sqz expand '§ref:a1b2c3d4§'     # paste the whole token\
\
# 2. Compress without dedup (per-invocation)\
echo "..." | sqz compress --no-cache\
\
# 3. Disable dedup globally (env var)\
export SQZ_NO_DEDUP=1\
\
# 4. MCP passthrough tool (returns input byte-exact, zero transforms)\
# Available via tools/list when sqz-mcp is running\
```\
\
## Track Your Own Savings\
\
Run `sqz gain` in your shell any time to see your own daily breakdown (see the\
\
Token Savings section above for what the output looks like), and `sqz stats`\
\
for the full cumulative report:\
\
```\
$ sqz stats\
  📊 sqz compression stats\
  ──────────────────────────────────────────────────\
\
  178,442  tokens saved\
  ↓  24.7% average reduction\
\
  Compressions           3,003\
  Tokens in              721,840\
  Tokens out             543,398\
  Tokens saved           178,442\
  Avg reduction          24.7%\
\
  🗄️  Cache\
  ──────────────────────────────────────────────────\
  Entries                43\
  Size                   39.1 KB\
```\
\
Add `--breakdown` to see exactly which commands consume the most tokens:\
\
```\
$ sqz stats --breakdown\
\
  🔍 Top Token Consumers\
  ──────────────────────────────────────────────────────────────────────\
  command               calls  tokens in        out    saved\
  ──────────────────────────────────────────────────────────────────────\
  dedup                   249      45541       3237      93%\
  stdin                    51      30851      24289      21%\
  auto                    132      18288       7740      58%\
  echo                     17       1050        558      47%\
  ls -la                    8        948        948       0%\
  cargo build               7        170        145      15%\
  git status                4         56          8      86%\
  ──────────────────────────────────────────────────────────────────────\
```\
\
**Per-project filtering:**\
\
```\
sqz stats --project .           # stats for current project only\
sqz stats --project list        # list all tracked projects\
sqz gain --project .            # daily gains for current project\
sqz gain --days 30              # last 30 days instead of 7\
sqz gain --days 30 --project .  # combine both\
```\
\
Stats are stored locally in SQLite under `~/.sqz/sessions.db` — nothing leaves your machine.\
\
## How Compression Works\
\
1. **Per-command formatters** — 40+ commands across 9 ecosystems get purpose-built compression:\
\
\
\
| Ecosystem | Commands |\
| --- | --- |\
| Git | status, log, diff, show, stash, remote, fetch, push, pull, commit |\
| Rust | cargo build/test/clippy/check/nextest |\
| JavaScript | npm/pnpm/yarn/bun install/test/audit/outdated, tsc, eslint, vitest |\
| Python | pytest, ruff, mypy, pip |\
| Go | go test (incl. `-json` stream), go build, go vet, golangci-lint |\
| Cloud | aws, terraform plan/apply/init, gcloud |\
| Containers | docker/podman ps/images/build, kubectl get/describe/logs/apply |\
| JVM | gradle build/test, maven |\
| System | grep/rg, tree, find/fd, ls, curl/wget |\
| GitHub | gh pr/issue/run (JSON + table) |\
\
\
Unknown commands fall through to the generic compression pipeline — no output is ever left uncompressed.\
\
2. **Structural summaries** — code files compressed to imports + function signatures + call graph (~70% reduction). The model sees the architecture, not implementation noise.\
\
3. **Dedup cache** — SHA-256 content hash, persistent across sessions. Second read = 13-token reference.\
\
4. **JSON pipeline** — strip nulls → project out debug fields → flatten → collapse arrays → TOON encoding (lossless compact format)\
\
5. **Safe mode** — stack traces, secrets, migrations detected by entropy analysis and routed through with 0% compression\
\
\
For the full technical details, see [docs/](https://gist.github.com/karpathy/docs/).\
\
## Configuration\
\
```\
# ~/.sqz/presets/default.toml\
[preset]\
name = "default"\
version = "1.0"\
\
[compression.condense]\
enabled = true\
max_repeated_lines = 3\
\
[compression.strip_nulls]\
enabled = true\
\
[budget]\
warning_threshold = 0.70\
default_window_size = 200000\
```\
\
## Privacy\
\
- Zero telemetry — no data transmitted, no crash reports\
- Fully offline — works in air-gapped environments\
- All processing local\
\
## Development\
\
```\
git clone https://github.com/ojuschugh1/sqz.git\
cd sqz\
cargo test --workspace\
cargo build --release\
```\
\
## License\
\
[Elastic License 2.0](https://gist.github.com/karpathy/LICENSE) (ELv2) — use, fork, modify freely. Two restrictions: no competing hosted service, no removing license notices.\
\
## Links\
\
- [White Paper: Pre-Injection Context Compression](https://gist.github.com/karpathy/docs/whitepaper.md)\
- [Benchmark: sqz vs rtk](https://gist.github.com/karpathy/docs/benchmark-vs-rtk.md)\
- [Discord](https://discord.gg/j8EEyH5dSB)\
- [Changelog](https://gist.github.com/karpathy/CHANGELOG.md)\
\
## Star History\
\
[![Star History Chart](https://camo.githubusercontent.com/4d6637722d7c5d9f42a6b84d4d7743fe6b7c0fc0ec10301fed71a84efafeeba7/68747470733a2f2f6170692e737461722d686973746f72792e636f6d2f7376673f7265706f733d6f6a75736368756768312f73717a26747970653d44617465)](https://star-history.com/#ojuschugh1/sqz&Date)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@AliMahmoud15486](https://avatars.githubusercontent.com/u/111673074?s=80&v=4)](https://gist.github.com/AliMahmoud15486)\
\
### **[AliMahmoud15486](https://gist.github.com/AliMahmoud15486)**     commented    [2 weeks agoJul 3, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6230677\#gistcomment-6230677)\
\
\
Copy link\
\
\
Copy Markdown\
\
Thanks for publishing this pattern, Andrej. I instantiated it for product management and open-sourced the result: [https://github.com/AliMahmoud15486/pm-llm-wiki](https://github.com/AliMahmoud15486/pm-llm-wiki)\
\
The PM twist on the entities: problem pages with evidence chains, **decision pages with rationale + reversal conditions** (the "decision memory" the v2 thread flagged as missing — for PMs it is the job), an assumption register (untested/validated/weakening/invalidated, each flip citing its source), and an open-questions queue that turns every contradiction the weekly lint finds into a tagged discovery/interview question. PRDs and stakeholder briefs then become queries against the wiki, every claim source-cited.\
\
The repo has a copy-paste schema (CLAUDE.md), a start-minimal progression plan (4 entity types; schema-defined triggers decide when to add personas/competitors/metrics), and a fully worked fictional pilot (B2C fitness app with a churn problem) showing every mechanic — including the pilot itself being maintained by an agent. Pressure-tested before publishing by handing the schema to a fresh agent with a one-line prompt and auditing the diff.\
\
MIT — forks, field reports, and critique welcome.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@blurman-ai](https://avatars.githubusercontent.com/u/287965768?s=80&v=4)](https://gist.github.com/blurman-ai)\
\
### **[blurman-ai](https://gist.github.com/blurman-ai)**     commented    [2 weeks agoJul 3, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6232070\#gistcomment-6232070)\
\
\
Copy link\
\
\
Copy Markdown\
\
Ran a small controlled experiment applying this pattern to a **code repository** — agent-facing docs for [archcheck](https://github.com/blurman-ai/archcheck), a C++ architecture checker for CI. Measured before adopting. Sharing numbers since the thread has production experience but few measurements.\
\
**Setup.** Built 28 source-backed pages: every claim cites `file:line`, message strings quoted verbatim from code, staleness tracked via a `last_checked_commit` field plus a lint script. Then A/B: same 4 lookup questions, fresh agent per run, isolated checkouts with and without the wiki, transcripts audited so no arm could peek.\
\
**Result: the 28-page wiki saved nothing** versus letting the agent grep the code (marginal tokens, 4 questions summed; correctness 4/4 everywhere):\
\
| arm | tool calls | tokens |\
| --- | --- | --- |\
| grep the code | 10 | 27.3k |\
| wiki, "verify against source" | 10 | 27.6k |\
| wiki, blind trust | 10 | 29.8k |\
\
Two causes: **(1)** in a codebase where one concept = one ~100-line file, per-entity pages came out _larger than the sources they describe_, so compression ≤ 1; **(2)** pages stamped "derived, verify against source" make the agent read both the wiki _and_ the code, so the cache pays twice. Either the wiki is trusted at query time or it shouldn't exist.\
\
**The fix.** Collapsed everything into a single dense table page (rule registry, gate policy, file/test/fixture matrix; zero-hop entry from the agents file; trusted at query time; freshness kept by the lint). Re-measured, plus a heavier 5-part pre-change recon task:\
\
| task | grep the code | one-page map |\
| --- | --- | --- |\
| 4 lookups | 10 calls / 27.3k / 94s | **4 calls / 13.8k / 31s** |\
| recon (5-part) | 12 calls / 16.5k / 53s | **1 call / 7.2k / 13s** |\
\
Correctness unchanged at 100% in both arms.\
\
**Boundary condition in practice:** the pattern pays exactly when a page _compresses_ facts scattered across many sources; mirrors of small greppable files are negative value. Consistent with [@distorx](https://github.com/distorx)'s point that drift is the main failure mode — the linter flagged 8 stale pages on day one after unrelated commits, and that loop is what makes query-time trust viable.\
\
_Measurement footnote:_ sub-agent token totals were ~80% fixed overhead (a do-nothing agent already costs 24.3k tokens), so compare marginal costs or you're comparing a constant.\
\
Full write-up with method and caveats: [agent\_wiki\_economics.md](https://github.com/blurman-ai/archcheck/blob/master/docs/research/agent_wiki_economics.md) · the surviving one-page map: [docs/openwiki/index.md](https://github.com/blurman-ai/archcheck/blob/master/docs/openwiki/index.md)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@gowtham0992](https://avatars.githubusercontent.com/u/15722259?s=80&v=4)](https://gist.github.com/gowtham0992)\
\
### **[gowtham0992](https://gist.github.com/gowtham0992)**     commented    [2 weeks agoJul 3, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6232353\#gistcomment-6232353)\
\
\
Copy link\
\
\
Copy Markdown\
\
Link v1.5.0 is live\
\
Since v1.4.0, most of the work went into making Link more agent-native: less “here is a wiki your agent can browse,” more “your agent has one obvious way to recall, write, review, and verify memory.”\
\
![image](https://private-user-images.githubusercontent.com/15722259/616975937-a9f08169-d7ae-4d5d-8e56-e470395c3306.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjAsIm5iZiI6MTc4NDA3OTU2MCwicGF0aCI6Ii8xNTcyMjI1OS82MTY5NzU5MzctYTlmMDgxNjktZDdhZS00ZDVkLThlNTYtZTQ3MDM5NWMzMzA2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA3MTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNzE1VDAxMzkyMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTZjYTNhMGQyZjRjNzU4ZjdiNTM2MDI4NGZkZDJjNmI4M2VjY2I2YzIzMmQxMGUwM2EwZWYwMDI4NjVkMmQ0NzImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.4pMs6UOGQQ-1kdfBYIF9glkZz3zVxeJFnu_zlZ8On84)\
\
What changed:\
\
- Slim MCP surface. Link used to expose ~37 MCP tools by default. v1.5.0 defaults to six: status, recall, remember, ingest, review, and admin. One obvious read path, one explicit write path. The full tool surface is still available when needed.\
\
- MCP prompts and resources. Link now exposes native MCP prompts/resources where clients support them, so agents can start from Link, recall context, and inspect memory without per-agent glue.\
\
- Honest recall. Every recalled memory now carries a confidence label: strong, moderate, or weak. If everything is weak, the packet tells the agent to verify with the user instead of pretending it knows. Still zero embeddings and zero network calls.\
\
- Day-one seeding. `lnk seed .` reads allowlisted repo context that already exists, like `README`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, and recent git subjects. It secret-scans that input and writes a source-backed page, so the first recall can return actual project context instead of an empty wiki.\
\
- 60-second proof. `brew install gowtham0992/link/link && lnk proof` creates a local workspace, writes one reviewed memory, and recalls it through the same bounded path used by CLI, skills, and MCP.\
\
- Trust plumbing. The audit log is now hash-chained, interrupted multi-file writes leave rollback snapshots, and `lnk benchmark` reports how much context the bounded packet avoided sending versus dumping the whole wiki.\
\
\
Everything remains plain local Markdown: readable in git or Obsidian, no cloud account, no telemetry.\
\
Repo: [https://github.com/gowtham0992/link](https://github.com/gowtham0992/link)\
\
Site: [https://gowtham0992.github.io/link/](https://gowtham0992.github.io/link/)\
\
PyPI: [https://pypi.org/project/link-mcp/](https://pypi.org/project/link-mcp/)\
\
MCP: [https://registry.modelcontextprotocol.io/?q=io.github.gowtham0992%2Flink](https://registry.modelcontextprotocol.io/?q=io.github.gowtham0992%2Flink)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@cobusgreyling](https://avatars.githubusercontent.com/u/7868717?s=80&v=4)](https://gist.github.com/cobusgreyling)\
\
### **[cobusgreyling](https://gist.github.com/cobusgreyling)**     commented    [last weekJul 4, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6234712\#gistcomment-6234712)\
\
\
Copy link\
\
\
Copy Markdown\
\
Reference implementation + tooling for this pattern: [https://github.com/cobusgreyling/llm-wiki](https://github.com/cobusgreyling/llm-wiki)\
\
- `pip install llm-wiki && wiki init my-wiki --git` scaffolds a new wiki\
- CLI (`wiki search`, `wiki lint`, `wiki ingest-status`) \+ MCP server for agents\
- Demo wiki with two ingested sources — synthesis revision + contradictions ledger in `examples/demo/`\
- Domain examples: research papers (`examples/research/`), book notes (`examples/reading/`)\
- Optional qmd backend when the wiki outgrows BM25: `wiki search "query" --backend qmd`\
\
Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@mohammadmaso](https://avatars.githubusercontent.com/u/6130893?s=80&v=4)](https://gist.github.com/mohammadmaso)\
\
### **[mohammadmaso](https://gist.github.com/mohammadmaso)**     commented    [last weekJul 5, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6235417\#gistcomment-6235417)\
\
\
Copy link\
\
\
Copy Markdown\
\
Hi Andrej — thank you for publishing this as an idea file rather than a repo. That framing made it easy to take the pattern seriously and build a concrete version tuned to my workflow.\
\
I implemented it as **EchoWiki**: a local-first, Obsidian-native knowledge compiler.\
\
**Repo:** [https://github.com/mohammadmaso/echowiki](https://github.com/mohammadmaso/echowiki)\
\
### How it maps to your three layers\
\
**Raw sources → `raw/`**\
\
One universal inbox. Voice transcripts and manually dropped `.md`/`.txt` files land in the same folder and go through the same pipeline — no special “voice path” inside compilation logic.\
\
**The wiki → `wiki/`**\
\
The agent maintains the structure you describe:\
\
- `summaries/` — one page per ingested document\
- `concepts/` — cross-document synthesis\
- `entities/` — people, orgs, places, products, works, events, etc.\
- `index.md` — content-oriented catalog\
- `log.md` — append-only operations timeline\
\
Cross-links use Obsidian `[[wikilinks]]`. Pages carry OKF-schema YAML frontmatter so they stay portable outside Obsidian too.\
\
**The schema → `wiki/AGENTS.md`**\
\
Read from disk at runtime, not baked into code. Edit the conventions and the next compilation run picks them up — no redeploy.\
\
### Operations implemented (MVP)\
\
**Ingest**\
\
- Drop a note into `raw/`, or use the Obsidian plugin to send the active note there\
- Record a voice note → STT → transcript written to `raw/` as Markdown\
- Optional folder watcher auto-triggers compilation on new/changed files\
- Optional approval gate before anything is compiled\
\
**Compile (your “ingest” flow, automated)**\
\
Per new `raw/` document, a Mastra agent:\
\
1. Writes a summary\
2. Reads existing concept/entity pages for context\
3. Creates or **updates** matching concept/entity pages (merge, not duplicate)\
4. Updates `index.md` and appends to `log.md`\
\
**Query / Lint**\
\
Not in MVP yet — focused on the compounding wiki foundation first. Stretch goals include query/chat over the compiled wiki and periodic lint reports under `wiki/reports/`.\
\
### Why Mastra + Obsidian\
\
Your gist describes Obsidian as the IDE and the LLM as the programmer. EchoWiki leans into that literally:\
\
- The **repo root is the Obsidian vault** (`raw/` \+ `wiki/` as siblings)\
- An **Obsidian desktop plugin** bundles and runs the Mastra compiler backend locally\
- LLM and STT are **provider-agnostic** — any OpenAI-compatible endpoint, cloud or self-hosted\
- External calls only for STT/LLM steps you explicitly trigger; everything else stays on disk\
\
So the loop is: capture → drop in `raw/` → watch/approve → compile → browse the graph in Obsidian while pages update.\
\
### Architectural lineage\
\
I treated this as a concrete instantiation of your pattern, with [VectifyAI/OpenKB](https://github.com/VectifyAI/OpenKB) as the reference for the `raw/ → wiki/` compilation model (summaries → concepts → entities → index/log). EchoWiki is essentially OpenKB’s wiki foundation reimplemented on **Mastra** (TypeScript) instead of Python, with Obsidian as the primary surface.\
\
### What resonated most from the gist\
\
Two lines that shaped the design:\
\
1. _“The wiki is a persistent, compounding artifact.”_ — That’s the whole product bet: don’t re-derive from raw sources on every question; keep a maintained synthesis that gets richer with each ingest.\
2. _“Humans abandon wikis because the maintenance burden grows faster than the value.”_ — EchoWiki tries to make maintenance near-zero: the agent touches summaries, concepts, entities, index, and log in one pass; the human curates sources and optionally approves before compile.\
\
### Current status\
\
MVP covers the full ingest → compile → Obsidian graph loop for text and voice. Still building toward query/lint parity and broader format support (PDF, URLs, etc.).\
\
If anyone else is instantiating this pattern for Obsidian + local-first capture, happy to compare notes in issues or discussions on the repo.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@cobusgreyling](https://avatars.githubusercontent.com/u/7868717?s=80&v=4)](https://gist.github.com/cobusgreyling)\
\
### **[cobusgreyling](https://gist.github.com/cobusgreyling)**     commented    [last weekJul 5, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6235480\#gistcomment-6235480)\
\
\
Copy link\
\
\
Copy Markdown\
\
Reference implementation + tooling for this pattern: [https://github.com/cobusgreyling/llm-wiki](https://github.com/cobusgreyling/llm-wiki)\
\
- `pip install llm-wiki && wiki init my-wiki --git` scaffolds a new wiki\
- CLI (`wiki search`, `wiki lint`, `wiki ingest-status`) \+ MCP server for agents\
- Demo wiki with **two ingested sources** — synthesis revision + contradictions ledger in `examples/demo/`\
- Domain examples: research papers (`examples/research/`), book notes (`examples/reading/`)\
- Optional qmd backend when the wiki outgrows BM25: `wiki search "query" --backend qmd`\
- Terminal demo: [https://asciinema.org/a/JaIKgBIXHP8nDyw0](https://asciinema.org/a/JaIKgBIXHP8nDyw0)\
\
Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@ikwuoz](https://avatars.githubusercontent.com/u/30737582?s=80&v=4)](https://gist.github.com/ikwuoz)\
\
### **[ikwuoz](https://gist.github.com/ikwuoz)**     commented    [last weekJul 5, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6235645\#gistcomment-6235645)\
\
\
Copy link\
\
\
Copy Markdown\
\
I think this suffices as an in-context memory architecture for the LLMs\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@jpierreribeiro](https://avatars.githubusercontent.com/u/84548936?s=80&v=4)](https://gist.github.com/jpierreribeiro)\
\
### **[jpierreribeiro](https://gist.github.com/jpierreribeiro)**     commented    [last weekJul 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6237720\#gistcomment-6237720)\
\
\
Copy link\
\
\
Copy Markdown\
\
pewdiepie sux\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@XBlueSky](https://avatars.githubusercontent.com/u/30610447?s=80&v=4)](https://gist.github.com/XBlueSky)\
\
### **[XBlueSky](https://gist.github.com/XBlueSky)**     commented    [last weekJul 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6237806\#gistcomment-6237806)\
\
\
Copy link\
\
\
Copy Markdown\
\
This idea really resonated with me.\
\
While using Claude Code, I ran into a similar problem: conversations are valuable, but most of the content is not worth keeping forever.\
\
Simply storing every conversation quickly becomes noisy:\
\
- temporary debugging attempts\
- abandoned approaches\
- outdated assumptions\
\
I ended up building a workflow around this idea: instead of automatically turning conversations into memory, Claude and the user collaboratively distill important knowledge into a curated Markdown knowledge base.\
\
The knowledge stays human-readable, versionable, and can be explored through Obsidian.\
\
I called it Cortexes:\
\
[https://cortexes.pages.dev/](https://cortexes.pages.dev/)\
\
The interesting question for me is not "how do we store more memory?", but "how do we maintain high-quality knowledge over time?"\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@TLiu2014](https://avatars.githubusercontent.com/u/6778087?s=80&v=4)](https://gist.github.com/TLiu2014)\
\
### **[TLiu2014](https://gist.github.com/TLiu2014)**     commented    [last weekJul 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6237828\#gistcomment-6237828)\
\
\
Copy link\
\
\
Copy Markdown\
\
LLM is like CPU and docs/files are like disk. This LLM Wiki is exactly the memory!\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@mas213](https://avatars.githubusercontent.com/u/204853?s=80&v=4)](https://gist.github.com/mas213)\
\
### **[mas213](https://gist.github.com/mas213)**     commented    [last weekJul 7, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6237886\#gistcomment-6237886)\
\
\
Copy link\
\
\
Copy Markdown\
\
Love it. a little late to the party but was headsdown to built something similar.\
\
Applied this pattern to a different domain: behavioral verification of code changes.\
\
The overlap is direct. Same three layers:\
\
> **Raw sources** = PRs, specs, test cases, production incidents (immutable, never modified)\
>\
> **Wiki** = a behavioral knowledge graph. Not how the code is structured, how the system is supposed to behave. Concern pages, flow maps, state transitions, cross-references between what the spec promises and what the tests cover.\
>\
> **Schema** = a concern taxonomy (auth flows, data integrity, state transitions, error propagation, integration contracts, observability) that tells the system what to look for when a PR comes in.\
\
Same three operations:\
\
> **Ingest** = parse a PR with tree-sitter, extract behavioral changes, update the graph. A single PR might touch 5-10 concern pages.\
>\
> **Query** = "what concerns does this change touch? what can break from a user's perspective?"\
>\
> **Lint** = verify the PR against the behavioral graph before merge. Flag drift between what the system promises and what the code actually does.\
\
The compounding effect is the same. Every PR that flows through makes the graph richer. Every production incident that gets filed teaches it a new failure mode. The graph gets better at catching the next thing because it's seen the last hundred things.\
\
The Lint section of your gist describes exactly what's missing from QA tooling. Most test generation tools produce more scripts without understanding what the system is supposed to do. This is the other direction: build the knowledge first, then verify against it.\
\
Open sourced as an MCP server (Claude Code, Cursor, Codex): [https://github.com/OrangeproAI/orangepro-mcp](https://github.com/OrangeproAI/orangepro-mcp)\
\
No API key, no cloud, runs locally. Curious if you've thought about this pattern applied to code specifically.\
\
![opro-karpathy-parallel](https://private-user-images.githubusercontent.com/204853/617990236-43d827e0-5e02-4191-a681-0c85566a1896.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjAsIm5iZiI6MTc4NDA3OTU2MCwicGF0aCI6Ii8yMDQ4NTMvNjE3OTkwMjM2LTQzZDgyN2UwLTVlMDItNDE5MS1hNjgxLTBjODU1NjZhMTg5Ni5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNzE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDcxNVQwMTM5MjBaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0zZTYxYjg4Yjc3Nzc2MmNjMWJlMDI1ZGM5MDZiMmZjYmQ4OTZkNmQwNzJjZDBmZDVkMzE5YjVlNWE5MjUwMWY3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.WgS1NqmZPowBdgESCijMXKuuoO6puLZNjAhgzJbuA6Q)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@LiyuanW21](https://avatars.githubusercontent.com/u/61477247?s=80&v=4)](https://gist.github.com/LiyuanW21)\
\
### **[LiyuanW21](https://gist.github.com/LiyuanW21)**     commented    [last weekJul 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6239784\#gistcomment-6239784)\
\
\
Copy link\
\
\
Copy Markdown\
\
Thanks for sharing this — your `llm-wiki` idea inspired me to package the workflow into a reusable Obsidian + agent skill:\
\
[https://github.com/LiyuanW21/obsidian-wiki-system](https://github.com/LiyuanW21/obsidian-wiki-system)\
\
It supports Codex/OpenCode-style agents, bilingual vault templates, and natural-language install prompts so non-technical users can try the “LLM-maintained personal wiki” pattern more easily.\
\
I credited your gist in the README. Thanks again for the inspiration!\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@phoebe22222](https://avatars.githubusercontent.com/u/264658923?s=80&v=4)](https://gist.github.com/phoebe22222)\
\
### **[phoebe22222](https://gist.github.com/phoebe22222)**     commented    [last weekJul 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6240428\#gistcomment-6240428)\
\
\
Copy link\
\
\
Copy Markdown\
\
> This maps almost 1:1 to a system we have been running in production for ~6 months to manage infrastructure/ops knowledge. A few notes from actually living with the pattern at ~4000+ interlinked concepts:\
>\
> - **The schema file is everything.** Our `CLAUDE.md` is exactly the "disciplined maintainer vs. generic chatbot" config you describe — it encodes the ingest/query/lint workflows + naming conventions, and it co-evolved into the single most important file in the repo.\
> - **index.md at scale:** the flat index works great to a few hundred pages. Past that we added hybrid search (SQLite FTS5 + on-device embeddings, reciprocal-rank-fused) rather than standing up embedding-RAG infra — same spirit as qmd. We expose it as both a CLI (agent shells out) and an MCP server (native tool). ~1ms keyword, ~350ms hybrid.\
> - **New page vs. edit ( [@alinawab](https://github.com/alinawab)):** heuristic that works for us — _new page_ when it is a distinct entity/concept you would link to from elsewhere; _edit in place_ when it is an attribute/update of an existing one. The agent gets this right ~90% of the time once the schema enumerates the page types.\
> - **Team sharing ( [@geetansharora](https://github.com/geetansharora)):** the wiki is just a private git repo, auto-synced. Teammates browse in Obsidian or hit the same MCP server. Git history doubles as the `log.md` audit trail for free.\
> - **Biggest failure mode ( [@alinawab](https://github.com/alinawab)):** drift — the agent under-updating cross-references on ingest, so pages silently go stale. The lint pass is _not_ optional; we run it on a timer (orphan detection + contradiction flagging + stale-claim checks) and that is what keeps the graph healthy.\
>\
> The "compounding artifact" framing is exactly right — after a few thousand concepts the wiki answers questions the raw sources never could, because the synthesis already happened. Thanks for writing it up so cleanly.\
\
[@distorx](https://github.com/distorx) — of everyone here your setup maps closest to mine (team-scale, production, git-backed), so I'd value your take; anyone else who's hit this, welcome too.\
\
Mine is packaged as an agent skill, not a personal wiki: the knowledge lives alongside a SKILL.md — the schema/entry file agents load — as a git repo of markdown. Same three layers you'd recognize: an immutable source-of-truth layer (~30 metadata snapshots auto-pulled from our data platform), an LLM/human-maintained wiki layer derived from it (per-dataset field specs, metric formulas, business logic, query cases; ~450 md pages + ~110 python config files), and the SKILL.md schema + lint rules on top. It's distributed to a whole team, and each person's agent (Claude Code / Cursor / etc.) both uses and edits it.\
\
Two things I can't settle:\
\
1. Size vs. keeping source-of-truth local. The immutable snapshots are the heaviest, churniest part. The gist stresses keeping an immutable raw layer as the foundation, but do you keep raw sources in-repo, or split them out (submodule / LFS / on-demand fetch) to keep the skill light? And does repo size actually hurt agents at query time, or is it purely a human clone/CI cost?\
\
2. Concurrent team maintenance without rot. With multiple people's agents editing the same skill: do they push directly, or through a review gate (PR) before a page lands? How do you stop two agents fighting over the same page / spawning near-duplicates? Who owns the SKILL.md schema when the whole team co-evolves it? And the lint pass — human-triggered, or on a timer / CI hook? You called drift the #1 failure mode, so I'm most curious what actually enforces it at team scale.\
\
\
Trying to avoid the failure mode where a shared wiki slowly rots because no single person owns the bookkeeping. Any pointers appreciated.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@bprice1000](https://avatars.githubusercontent.com/u/77449883?s=80&v=4)](https://gist.github.com/bprice1000)\
\
### **[bprice1000](https://gist.github.com/bprice1000)**     commented    [last weekJul 8, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6241053\#gistcomment-6241053)•   edited      Loading          \#\#\# Uh oh!        There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
\
Copy link\
\
\
Copy Markdown\
\
I build a CMMS with this as a primary influence.\
\
It’s transformative. New levers to lean on, fun and powerful things happening when I do.\
\
you didn’t give us the framework for a document system.\
\
you gave us an engine. Build rules whereby everything is defined, every document has a place on a tree. Segment the tasks. Use skills to hard code workflows, define decision making trees, pool, lever markdown every way possible, guild based agent permissions; then suddenly you’ve got the flattest cmms-wiki all time that has no database or license.\
\
Ty.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@davidlfox](https://avatars.githubusercontent.com/u/5315855?s=80&v=4)](https://gist.github.com/davidlfox)\
\
### **[davidlfox](https://gist.github.com/davidlfox)**     commented    [5 days agoJul 9, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6242506\#gistcomment-6242506)•   edited      Loading          \#\#\# Uh oh!        There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
\
Copy link\
\
\
Copy Markdown\
\
for anyone running this locally/offline--what models are you finding reasonable success with? this feels like it could grow quickly into 2k-10k completions at the ~100 sources, hundreds of pages scale. does this need a 35b model? or would something much smaller suffice, since its only really doing classification? multiple models e.g. small for classification, larger for summaries/connections?\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@gowtham0992](https://avatars.githubusercontent.com/u/15722259?s=80&v=4)](https://gist.github.com/gowtham0992)\
\
### **[gowtham0992](https://gist.github.com/gowtham0992)**     commented    [5 days agoJul 10, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6243458\#gistcomment-6243458)\
\
\
Copy link\
\
\
Copy Markdown\
\
### Link 1.6.0 is out. Two big changes since 1.5.0:\
\
**Memory is now automatic.**`lnk connect claude-code --hooks` (also Codex, Cursor) installs session hooks: a bounded memory brief is injected when a session starts, and proposal-only notes are captured when it ends. The agent no longer has to remember to call its memory — and the review gate still holds, nothing durable is saved without approval. Dogfooding this caught a fun bug worth sharing: the capture pipeline was mining the _assistant's_ prose as if it were my preferences ("you prefer small commits" → saved as my preference). Proposals now come only from the user's own turns.\
\
**Opt-in semantic recall, still fully local.**`pip install "link-mcp[semantic]"` adds a small local embedding model so recall matches paraphrases — embeddings live in plain JSON under .link-cache/, no vector DB, model loads offline-only after a one-time fetch. Lexical stays the default. Measured on a 1,176-case benchmark in the repo: hybrid lifts hit@1 0.589 → 0.703; on third-party LoCoMo (1,536 queries, retrieval-only): any-evidence hit@10 0.578 → 0.685. Ablations that didn't survive measurement are documented too.\
\
Everything still plain Markdown on your machine, zero network in the runtime (CI-enforced).\
\
![lnk recall matches by meaning, then greets your next session with what it learned](https://raw.githubusercontent.com/gowtham0992/link/v1.6.0/docs/assets/link-aha.gif)![lnk recall matches by meaning, then greets your next session with what it learned](https://raw.githubusercontent.com/gowtham0992/link/v1.6.0/docs/assets/link-aha.gif)[Open lnk recall matches by meaning, then greets your next session with what it learned in new window](https://raw.githubusercontent.com/gowtham0992/link/v1.6.0/docs/assets/link-aha.gif)\
\
`brew upgrade link  (or brew install gowtham0992/link/link)`\
\
Release notes: [https://github.com/gowtham0992/link/releases/tag/v1.6.0](https://github.com/gowtham0992/link/releases/tag/v1.6.0)\
\
Repo: [https://github.com/gowtham0992/link](https://github.com/gowtham0992/link)\
\
Site: [https://gowtham0992.github.io/link/](https://gowtham0992.github.io/link/)\
\
PyPI: [https://pypi.org/project/link-mcp/](https://pypi.org/project/link-mcp/)\
\
MCP: [https://registry.modelcontextprotocol.io/?q=io.github.gowtham0992%2Flink](https://registry.modelcontextprotocol.io/?q=io.github.gowtham0992%2Flink)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@turkonthelurk](https://avatars.githubusercontent.com/u/124656542?s=80&v=4)](https://gist.github.com/turkonthelurk)\
\
### **[turkonthelurk](https://gist.github.com/turkonthelurk)**     commented    [5 days agoJul 10, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6243724\#gistcomment-6243724)\
\
\
Copy link\
\
\
Copy Markdown\
\
> Gezz the AI Slop is storing in this one's comment section... I just wanted to point out that NotebookLM is kinda intended to be this way as well, you get sources extract whatever you need make it a source, disable sources you don't need anymore\
\
right - but then you're reliant on google. this setup is model agnostic.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@Drifting12345](https://avatars.githubusercontent.com/u/95027021?s=80&v=4)](https://gist.github.com/Drifting12345)\
\
### **[Drifting12345](https://gist.github.com/Drifting12345)**     commented    [4 days agoJul 10, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6244817\#gistcomment-6244817)\
\
\
Copy link\
\
\
Copy Markdown\
\
# LLMwiki4rolePlay\
\
Incrementally build a novel `.txt` into an **Obsidian knowledge graph**, then use it as context to drive AI **role-play**.\
\
Built on the [LLM Wiki](https://gist.github.com/karpathy/llm-wiki.md) methodology, implemented as a **self-contained Claude Code Skill** — clone it and it just works, no `pip install` required. The Agent is the brain, the tools are the hands: when to create an entity, when to update it, what to retrieve is entirely the Agent's call; tools only execute.\
\
## What it does\
\
Give Claude Code a novel's txt file, and chapter by chapter it will:\
\
- Identify characters / locations / items / events\
- Write each entity as a `.md` page (YAML frontmatter + narrative body)\
- Embed `[[wikilink]]`s in the narrative to naturally form graph edges\
- Incrementally update existing entities by topic section when new information appears\
\
The end result is an Obsidian vault that lets you:\
\
- Browse the graph in Obsidian, jump between pages, view the graph view\
- Have Claude Code answer questions in character as any character (grounded in the wiki content, never breaking character)\
\
## Why it's good\
\
- **Character knowledge isolation**: during role-play, `entity-context` enforces a hard knowledge boundary — entities in the same team (derivative entities under the same main character) are fully readable; characters outside the team only get the paragraphs from the reader's own narrative that mention them. This stops a character from answering with plot information it never actually witnessed just because the Agent happened to read every entity in the book — no breaking character.\
\
- **Two-layer memory: remembers conversations without OOC (out of character)**: the book wiki vault (read-only, long-term memory of in-universe facts) and the memory vault (read-write, the character's relationship history with the user) are physically separated. The character remembers what you've talked about before and how the relationship has progressed — short-term dialogue is stored in `history.txt` and automatically consolidated into topic pages in the memory vault once a threshold is hit; past 200 entities, the least-recently-accessed ones are evicted (LRU). But every answer stays grounded in the book wiki's knowledge graph — remembering conversations never means inventing canon that isn't there.\
\
- **Index + graph traversal retrieval, scales to very long texts**: search first reads candidate ids from `index.md` / `_index-{parent}.md` instead of scanning the whole vault on every call; context lookups follow `[[wikilink]]`s on demand instead of loading everything at once. Derivative documents split out from an oversized entity are only written into their own team's `_index-{parent}.md`, never into the global `index.md` — the deeper the graph gets from splitting, the leaner the global index stays, so lookup speed doesn't degrade as the novel grows. Built for building knowledge graphs out of very long texts.\
\
\
skill here：\
\
[https://github.com/Drifting12345/LLMwiki4rolePlay](https://github.com/Drifting12345/LLMwiki4rolePlay)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@william-Johnason](https://avatars.githubusercontent.com/u/4006820?s=80&v=4)](https://gist.github.com/william-Johnason)\
\
### **[william-Johnason](https://gist.github.com/william-Johnason)**     commented    [4 days agoJul 10, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6245024\#gistcomment-6245024)•   edited      Loading          \#\#\# Uh oh!        There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
\
Copy link\
\
\
Copy Markdown\
\
We ran a 5-model accuracy vs. cost benchmark on a knowledge base QueryAgent (BM25 retrieval + LLM synthesis) across 15 M&A due diligence questions, three complexity tiers including cross-lingual. Results and per-question breakdown: [AquaFlow LLM Evaluation Report](https://github.com/axoviq-ai/synthadoc/blob/main/docs/example/aquaflow/evaluation/report/llm-query-benchmark.md)\
\
Hope the findings are interesting to you as well!\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@pradocabreroalejandro](https://avatars.githubusercontent.com/u/217187462?s=80&v=4)](https://gist.github.com/pradocabreroalejandro)\
\
### **[pradocabreroalejandro](https://gist.github.com/pradocabreroalejandro)**     commented    [3 days agoJul 12, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6247992\#gistcomment-6247992)\
\
\
Copy link\
\
\
Copy Markdown\
\
> phoebe22222\
\
[@phoebe22222](https://github.com/phoebe22222) — running a similar setup in production: a wiki of business rules\
\
extracted from a legacy ERP under active modernization (over a thousand forms,\
\
PL/SQL, DDL; legacy and new stacks coexisting), multiple human operators,\
\
served company-wide through a read-only MCP server. Your two questions are\
\
exactly the ones that shaped our design, so here is what survived contact:\
\
**1\. Size / keeping source-of-truth local: don't copy sources at all.** Our\
\
sources are living code, so any snapshot layer is stale by construction. A\
\
manifest file declares which repo paths count as documentary sources; the\
\
agent reads them in place, and every citation pins a version:\
\
`file@SHA:lines`. Git already guarantees every cited version stays\
\
recoverable, so the "immutable raw layer" becomes a property (version-pinned)\
\
instead of a folder (copied). Bonus: `git diff <last-synced-SHA>..HEAD -- <manifest paths>` IS the re-ingest work list — deterministic, complete, no\
\
judgment. The wiki repo holds only synthesis and stays light.\
\
**1b. What the agent reads is not the raw source — it's a distilled version,**\
\
**and that's a contract, not a convenience.** Raw exports are written for\
\
machines of their era: our form-definition XMLs are mostly layout noise\
\
(coordinates, fonts, visual attributes). A deterministic CI step distills\
\
every source type on every commit — forms XML stripped to triggers/program\
\
units, DDL reduced to logical schema, PL/SQL normalized. On our two largest\
\
forms that's a 4.4MB→975KB and 2.8MB→657KB reduction on disk (haven't\
\
measured tokens rigorously, but the removed content is what the extraction\
\
never needed anyway). Three rules keep it honest: distilled output is\
\
byte-deterministic (or your git-diff work list fills with phantom changes),\
\
every distilled file carries a provenance header (source path, content hash,\
\
distiller version), and changing what a distiller strips is a schema-grade\
\
event — it changes what the model can see, therefore what knowledge can\
\
exist.\
\
**1c. Structured labels in the sources survive distillation and set the trust**\
\
**floor.** We annotate sources with a small closed tag vocabulary the agent is\
\
taught to anchor on — two tiers with strictly separate authorship:\
\
machine-generated hints (pipeline-written, confidence-labeled, generated at\
\
scale to give reviewers a starting point) and human annotations\
\
(PR-reviewed, the only tier that counts as verified provenance). When a\
\
human annotation lands, the pipeline prunes the machine hint — scaffolding\
\
comes down. Extraction provenance then travels on every wiki page\
\
(human-annotated > machine-hinted > raw code reading), and since full\
\
curation of a 200-column table will never happen, a quality score per source\
\
feeds a citizenship gradient instead of a binary gate: low-curation entities\
\
stay readable, but everything derived from them carries the caveat.\
\
**2\. Concurrent maintenance without rot — four mechanisms, all boring:**\
\
- **All wiki writes land via PR.** The serving layer is strictly read-only;\
\
\
consumers physically cannot write. Deploy follows a git ref, so "publish"\
\
\
is an operator blessing (a tag fast-forward), not whatever an agent last\
\
\
did.\
- **One writer per layer.** Extraction agents write rule/entity pages; the\
\
\
synthesis pass writes composite pages and is forbidden from creating atomic\
\
\
ones (it reports findings back down instead). Two agents never contend for\
\
\
the same page because no two roles share a page type.\
- **The schema has an owner and an amendment regime.** Agents propose changes\
\
\
with evidence from the operation log, humans approve, and every change\
\
\
leaves a log entry + an honest commit message. The schema's git history is\
\
\
the experiment's changelog. "Co-evolved by the whole team" without this\
\
\
decays into "describes nothing."\
- **Lint is CI/timer-enforced, and the bookkeeping backlog writes itself.**\
\
\
Beyond the usual checks, the serving layer appends every unanswered query\
\
\
to a miss log; a reconciliation step folds those into a versioned demand\
\
\
ledger. Nobody "owns the bookkeeping" as a chore — the system emits its own\
\
\
todo list, ranked by real demand, and operators just work it.\
\
Agreeing hard with [@distorx](https://github.com/distorx) that drift is the failure mode. Our addition:\
\
grade the trust and make it travel — every page carries status + extraction\
\
provenance, and the MCP attaches the caveats to every payload, so a stale or\
\
disputed page degrades honestly instead of silently. Writing up the full\
\
pattern (what the original assumptions didn't survive: frozen sources, single\
\
user, cheap errors); will share when it's cleaned up.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@gserdyuk](https://avatars.githubusercontent.com/u/91453?s=80&v=4)](https://gist.github.com/gserdyuk)\
\
### **[gserdyuk](https://gist.github.com/gserdyuk)**     commented    [2 days agoJul 13, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6250368\#gistcomment-6250368)•   edited      Loading          \#\#\# Uh oh!        There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
\
Copy link\
\
\
Copy Markdown\
\
Field report from a different starting point: a research repo (simulation-methodology project, twotakt) that converged on this pattern before reading the gist — same mechanics: INDEX.md as the catalog (one pointer line + a one-line hook, never content), an append-only dated log with greppable tags, CLAUDE.md as the schema file, a findings register as the synthesis layer. Coming from research reproducibility rather than PKM, we ended up with two mechanics I haven't seen in the thread, both aimed at the staleness/drift problem [@a-a-k](https://github.com/a-a-k) and others raise:\
\
1. Document passports. Every corpus document opens with a one-line immutable header: > Type: reasoning \| register \| journal \| record — < regime > · born < date >. It tells the reader — human or LLM — how to treat the file: is it append-only, may it contradict newer documents, is it synchronized. Cheap, and it resolves the "is this page current?" ambiguity at read time instead of trying to prevent it at write time.\
\
2. Corpus/surface split. We stopped fighting staleness for most documents. The corpus (log, findings, reasoning docs) accumulates: dated, append-only, internal contradictions are history and never "fixed"; it gets periodically compacted (reviewed, rewritten as vN, previous version archived) rather than patched in place. Only a deliberately small "surface" (README, the schema file) promises currency and is synchronized. We had three current-state documents die of rot before generalizing the rule: staleness is solved by not promising currency — except where you can actually afford the promise.\
\
\
Also +1 to [@nowissan](https://github.com/nowissan) 's "Level" problem: our synthesis layer is claim-first (numbered one-screen claims, each pointing to its long form; refinements are new claims — "refines/supersedes #N" — never edits), and concept-level docs only graduate out of claim clusters that recur. Level falls out structurally: a concept with ten claims under it is heavyweight, one with a single claim is light — importance is measured by the size of the cluster, not assigned by an author.\
\
The mechanics live in CLAUDE.md / INDEX.md / findings.md / dev-log.md here: [https://github.com/gserdyuk/twotakt](https://github.com/gserdyuk/twotakt)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@ANT-CYJ](https://avatars.githubusercontent.com/u/22209359?s=80&v=4)](https://gist.github.com/ANT-CYJ)\
\
### **[ANT-CYJ](https://gist.github.com/ANT-CYJ)**     commented    [2 days agoJul 13, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6250369\#gistcomment-6250369)   via email\
\
\
Copy link\
\
\
Copy Markdown\
\
放心吧，我已经收到啦。\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@bluejaeha](https://avatars.githubusercontent.com/u/212832360?s=80&v=4)](https://gist.github.com/bluejaeha)\
\
### **[bluejaeha](https://gist.github.com/bluejaeha)**     commented    [20 hours agoJul 14, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6253883\#gistcomment-6253883)•   edited      Loading          \#\#\# Uh oh!        There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
\
Copy link\
\
\
Copy Markdown\
\
Thank you for sharing this idea — it changed how I work.\
\
I'm not a developer — I'm an accountant in Korea, doing K-IFRS advisory and audits at an accounting firm. English isn't my strong suit either, so this comment was written with AI help (fitting, given the topic). I've been running my own instance for a while: immutable `sources/`, an agent-maintained `wiki/`, and a CLAUDE.md schema, covering accounting standards plus IT, physics, math, and philosophy as separate domains in one vault.\
\
```\
llm-wiki/\
├── sources/                  # immutable originals — the LLM never edits\
│   ├── inbox/                # unclassified intake (incl. inbox/ai/ for chatbot summaries)\
│   └── domain/               # accounting, capital-market, it, network, physics, math, philosophy...\
│       ├── ai-archive/       # processed AI summaries (still "unverified")\
│       ├── reference/        # full-text library for verification lookups\
│       └── ...               # classified excerpts (standards, rulings, notes...)\
├── wiki/\
│   ├── domain/topics/        # agent-maintained pages, each with a verification status\
│   ├── index.md              # catalog, updated on every ingest\
│   └── open-questions.md     # contradictions and unresolved issues\
├── scratch/                  # human-only notepad, excluded from all workflows\
└── CLAUDE.md                 # the schema\
```\
\
One thing I added, coming from audit work: **a verification status on every page**. AI-generated content enters through a quarantined inbox, is marked `unverified`, and cannot be cited as grounds for any other page until checked against primary sources (accounting standards, paragraph by paragraph). An unverified page citing another unverified page is exactly the circular evidence auditors are trained to reject. Each domain also has its own mandatory citation format — standards paragraph numbers for accounting, RFC numbers for networking, and so on.\
\
Another extension: **conversations with external chatbots are a first-class ingest source**. I keep a standardized prompt (and an agent skill) that distills a ChatGPT/Claude conversation into atomic notes with fixed frontmatter, tags, and naming conventions — which then enter through the same quarantined inbox as any other unverified material. Reading the comments here, it seems several of us converged on this independently.\
\
Watching scattered knowledge compound into something I can actually trust in client work has been a real joy. If this pattern works for a non-developer like me, it can work for anyone. Thanks again for giving this away so generously.\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@HemachandranD](https://avatars.githubusercontent.com/u/24708259?s=80&v=4)](https://gist.github.com/HemachandranD)\
\
### **[HemachandranD](https://gist.github.com/HemachandranD)**     commented    [19 hours agoJul 14, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6253958\#gistcomment-6253958)\
\
\
Copy link\
\
\
Copy Markdown\
\
Built the Notion side of this as a small pull-only bridge: **notionwiki**\
\
[notionwiki](https://github.com/HemachandranD/notionwiki) treats Notion as one feeder into raw/ — a scheduled job polls, converts pages/database rows to flat markdown (hierarchy kept as frontmatter, not folders, so a Notion move never reshuffles the corpus), and archives-on-change rather than overwriting silently. No write-back, no sync/push — Notion stays where you author, and the actual wiki-building (ingest → synthesize → lint) is exactly the loop described here, run by an assistant against CLAUDE.md as the schema. The part I keep coming back to: without a real push mechanism, the corpus is only ever as fresh as the last poll — so "compounding" ends up bounded by pull cadence, not by how fast the model can actually synthesize.\
\
![image](https://private-user-images.githubusercontent.com/24708259/621265458-ae212739-73a7-4b5a-a9a2-1ddd0e300db7.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjEsIm5iZiI6MTc4NDA3OTU2MSwicGF0aCI6Ii8yNDcwODI1OS82MjEyNjU0NTgtYWUyMTI3MzktNzNhNy00YjVhLWE5YTItMWRkZDBlMzAwZGI3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA3MTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNzE1VDAxMzkyMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWM4MTkyZjk4M2MyNjM0ZGRkNDVmYzQxOTUxMTQ1OTUxMTZjZjI5ZjlkYjg5ODdiMGIxOTEzYjkxYmFmYmFhZGEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.4yqASp1FdNWxy4M4JeKIACOEfbTKkRPAuzv06N3QPuw) ![image](https://private-user-images.githubusercontent.com/24708259/621266243-26f07b0d-8299-4799-bdbb-96b75df87ac5.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjEsIm5iZiI6MTc4NDA3OTU2MSwicGF0aCI6Ii8yNDcwODI1OS82MjEyNjYyNDMtMjZmMDdiMGQtODI5OS00Nzk5LWJkYmItOTZiNzVkZjg3YWM1LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA3MTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNzE1VDAxMzkyMVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTI4ZWQzNjAyMTQxNTM4OWQxZGIyZWMzMjliNzMyNDUzMDYzOGJlMThjOWUzNDYxMzZjZjMyZmMyZTJlNGI3NjYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.W5ixCwdUvQWMRCOtsnoM5jULAV4D-QBhaLyIVexKAH0)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@Encod3d-Sec](https://avatars.githubusercontent.com/u/196931983?s=80&v=4)](https://gist.github.com/Encod3d-Sec)\
\
### **[Encod3d-Sec](https://gist.github.com/Encod3d-Sec)**     commented    [14 hours agoJul 14, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6254367\#gistcomment-6254367)\
\
\
Copy link\
\
\
Copy Markdown\
\
Fully Working integration of this:\
\
[https://github.com/Encod3d-Sec/ClaudeBrain](https://github.com/Encod3d-Sec/ClaudeBrain)\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@DaveMikeP](https://avatars.githubusercontent.com/u/178601908?s=80&v=4)](https://gist.github.com/DaveMikeP)\
\
### **[DaveMikeP](https://gist.github.com/DaveMikeP)**     commented    [3 hours agoJul 14, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6255221\#gistcomment-6255221)\
\
\
Copy link\
\
\
Copy Markdown\
\
> First of all, thanks to **[@karpathy](https://github.com/karpathy)** for introducing and describing the **LLM-Wiki** paradigm: a simple yet brilliant idea that, in my opinion, will revolutionize corporate document management (replacing heavy, complex knowledge bases), help students avoid superficial LLM usage, and serve as a great ally for methodical learning.\
>\
> I have built a **Personal LLM-Wiki** prioritizing two fundamental aspects:\
>\
> 1. **Privacy**: All components run completely **offline**.\
> 2. **Efficiency**: I focused on creating an executable suitable for **modest hardware** (with or without a GPU), making it accessible despite current market prices for graphics cards.\
>\
> The core concept is straightforward: perform non-LLM-specific operations deterministically using standard Python libraries, which consume significantly fewer resources than a giant language model. It feels inefficient to waste LLM tokens on repetitive tasks that only require classic computational power.\
>\
> While my initial prototype worked, the model's responses were often too generic or limited to brief definitions. To achieve the exhaustive, structured lessons I envisioned, I integrated a few key components to enrich the context:\
>\
> ### Key Components\
>\
> - **Graphify**: Maps relationships between Markdown files, SQL schemas, scripts, and PDFs. It improves navigation based on structural relationships rather than just keywords, creating a navigable "map" directly accessible to the AI or via **Obsidian**. This drastically reduced dependency on compute while improving coherence.\
> - **ChromaDB**: A lightweight vector database used as the pillar for semantic search and document retrieval, executing operations efficiently on the CPU.\
> - **NetworkX**: Manages a dual data structure in memory with a **lazy cache**: an _Undirected Graph ($G$)_ for generic relationships and a _Directed Graph ($DiG$)_ focused exclusively on formative dependencies. This helps identify correlations and cite diverse sources covering the requested topic.\
> - **SQLite**: An embedded, serverless relational database dedicated to managing the system's transactional state and audit logs.\
>\
> ### Operational Flow\
>\
> ```\
> [Phase 1 (Optional): Pre-processing (Whisper)] ──>\
> ──> [Phase 2: Synthesis (Qwen3VL)]\
> ──> [Phase 3: Graph Building (Graphify)]\
> ──> [Phase 4: Indexing (ChromaDB)]\
> ──> [Phase 5: Context Assembly]\
> ──> [Phase 6: Inference (Qwen3.5 9B)]\
> ```\
>\
> _Advanced features included: Semantic Query Cache, Cross-Encoder Re-Ranker, and Reciprocal Rank Fusion (RRF) for HyDE._\
>\
> ### Additional Features\
>\
> - **Localization & UI**: Built a lightweight Flask web page with "on-the-fly" language switching managed via simple `.lng` files.\
> - **Secure Telegram Bot**: Accessible without exposing ports or reverse proxies (restricted to authorized Telegram IDs). It includes an interactive poll after each response, allowing the user to save the text, export it as a Marp Markdown presentation, or generate an audio podcast.\
> - **Quiz Mode**: Generates multiple-choice questions based on the wiki content with customizable difficulty, evaluating errors and explaining _why_ a specific answer was wrong.\
>\
> ### A Critique of the Paradigm: No New Wiki Pages Without Raw Sources\
>\
> The only critique I have regarding the baseline LLM-Wiki paradigm concerns **creating new wiki pages derived from LLM responses**.\
>\
> I don't find it useful to generate additional pages beyond those processed during the **Ingest** phase. Reprocessing existing concepts in different forms consumes resources and slows down the system (more pages to scan per query) without introducing genuinely new information. Since the LLM should not invent anything (avoiding hallucinations), it doesn't enrich the source base.\
>\
> In my implementation, the only generated pages allowed are the Markdown files exported for **Presentations** (Marp syntax)-treated strictly as "output documents" for the user, rather than being re-fed into the pipeline as wiki sources.\
>\
> I haven't published the repository on GitHub yet, as I am still refining the integration to make it as user-friendly as possible. I hope this architecture can serve as inspiration for anyone looking to customize or optimize their local LLM-Wiki setup!\
>\
> ### Below is an example of an answer to the question “Explain me what Kubernetes is.”\
>\
>  ![Personal LLM-WIKI](https://private-user-images.githubusercontent.com/291724620/615299575-1e0a9e98-b758-4292-91c0-34213afbade8.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNTI1NTMsIm5iZiI6MTc4NDA1MjI1MywicGF0aCI6Ii8yOTE3MjQ2MjAvNjE1Mjk5NTc1LTFlMGE5ZTk4LWI3NTgtNDI5Mi05MWMwLTM0MjEzYWZiYWRlOC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNzE0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDcxNFQxODA0MTNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0wNDYwYTM1MWYyMzQxNTQ1YjE1OWY0OTJhMjY3NTQwMWJlMzE3MzA1MmUzMWQ0ZjI0NWI1Y2E1ZDMwYjZiNjBkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.n8J0o-F9gO_v-wWt7LUfJtRc9kPTXpbOFSUXVCfID6A)\
\
Hi Maurizio, I like the way you implemented this. Well done and inspiring for me.\
\
BR, Mike\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[![@serradura](https://avatars.githubusercontent.com/u/305364?s=80&v=4)](https://gist.github.com/serradura)\
\
### **[serradura](https://gist.github.com/serradura)**     commented    [1 hour agoJul 15, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6255287\#gistcomment-6255287)•   edited      Loading          \#\#\# Uh oh!        There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
\
Copy link\
\
\
Copy Markdown\
\
![image](https://private-user-images.githubusercontent.com/305364/621799636-f0aa295b-6bf3-412e-be4b-3a1564d17cf5.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjEsIm5iZiI6MTc4NDA3OTU2MSwicGF0aCI6Ii8zMDUzNjQvNjIxNzk5NjM2LWYwYWEyOTViLTZiZjMtNDEyZS1iZTRiLTNhMTU2NGQxN2NmNS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNzE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDcxNVQwMTM5MjFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT01NjUzMDA4ZDcxZjhlODUyMTNmOTYzNjI3NjYwNDhhNDZiOTY2M2RmNGY3ZDg5YmQ0NGZlNWRkOTQ2MmM1YWMyJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.Th5KffrqBxpQRfd0BMgRv1BvfX1K9IbbDt1TPsUp7OI)\
\
Hi [@karpathy](https://github.com/karpathy), I implemented a complete toolkit to facilitate the OKF adoption (LLM Wiki ideas), which is composed of three cores:\
\
> An `Agent Skill` (the 🧠 ), a `CLI/Lib` (the 💪 ), and a `Server` (the 📊 )\
\
The agent knows how to author, curate, and, more importantly, how to consume (CLI tools + Server (for humans)).\
\
It is ￼​Open source and runs 100% locally!\
\
Here is the GitHub repo: [https://github.com/serradura/okf-gem](https://github.com/serradura/okf-gem) ( [https://demo.okfgem.com](https://demo.okfgem.com/))\
\
![image](https://private-user-images.githubusercontent.com/305364/621799681-ad4125f2-924c-4710-934c-cc307fa34711.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjEsIm5iZiI6MTc4NDA3OTU2MSwicGF0aCI6Ii8zMDUzNjQvNjIxNzk5NjgxLWFkNDEyNWYyLTkyNGMtNDcxMC05MzRjLWNjMzA3ZmEzNDcxMS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNzE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDcxNVQwMTM5MjFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0xMjlhMjA0MGUzMmQ5OGY4MTEwMjRiMzhjMTZlZjg2OWE2NzgwNTljODhkNzgwOGFlZWRhNmUxMjdkNmEyNzU3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.CXsYayGODfB5N5VYgnD4QTqyGtSYxZeLjdCbBtx9Uvs)\
\
The knowledge graph looks like this:￼​\
\
![image](https://private-user-images.githubusercontent.com/305364/621799720-28846ed1-8f5a-484b-981a-9535bd8d1ab7.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODQwNzk4NjEsIm5iZiI6MTc4NDA3OTU2MSwicGF0aCI6Ii8zMDUzNjQvNjIxNzk5NzIwLTI4ODQ2ZWQxLThmNWEtNDg0Yi05ODFhLTk1MzViZDhkMWFiNy5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNzE1JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDcxNVQwMTM5MjFaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jZjA5OGJhZjQ5MzdhMWU0NGU0ZjA3NjRhMTM3Y2M3NDk1ODYxMjNlNDM3OGU5ZWVmNTk3ZTBhNzc3YzU0ZDk3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZwbmcifQ.ez1OvViR-hk4f-hVKj9W1c_ERNg_N6D0fmJxroVmxpw)\
\
And you can test it here: [https://demo.okfgem.com/](https://demo.okfgem.com/)\
\
**Step by step to experiment with it:**\
\
1. Install the gem: `gem install okf`\
2. Install the skill: `okf skill .claude` (or any other agent)\
3. Start an agent session (`claude`)\
4. Execute `/okf produce based on <path-to-my-existent-docs>`\
\
**Once you have your first bundle, you can do:**\
\
Run the command `/okf maintain` in your agent session to keep it updated. Or, install the [Claude Plugin](https://claude.okfgem.com/), which will run this for you (after triggering the Stop hook).\
\
You can also run `okf server <folder>` to render your live graph locally. Or ask the agent to up it for you.\
\
If you want to know more, please check out these other resources:\
\
- Site: [https://okfgem.com/](https://okfgem.com/)\
- Blog: [https://okfgem.com/blog](https://okfgem.com/blog)\
- Docs: [https://okfgem.com/docs](https://okfgem.com/docs)\
- LLMs.txt: [https://okfgem.com/llms.txt](https://okfgem.com/llms.txt) ( [https://okfgem.com/llms-full.txt](https://okfgem.com/llms-full.txt))\
- Claude Plugin: [https://claude.okfgem.com/](https://claude.okfgem.com/)\
\
Looking forward to your feedback and critiques.\
\
Thanks!\
\
Sorry, something went wrong.\
\
\
### Uh oh!\
\
There was an error while loading. [Please reload this page](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).\
\
[Sign up for free](https://gist.github.com/join?source=comment-gist) **to join this conversation on GitHub**.\
Already have an account?\
[Sign in to comment](https://gist.github.com/login?return_to=https%3A%2F%2Fgist.github.com%2Fkarpathy%2F442a6bf555914893e9891c11519de94f)\
\
You can’t perform that action at this time.