![Thumbnail (1920x1080)](https://i.ytimg.com/vi/ZKZLko9kLm4/maxresdefault.jpg)
# [Hermes Agent Masterclass: 3. Memory, Plugins, Honcho, and Obsidian](https://www.youtube.com/watch?v=ZKZLko9kLm4)

**Visibility**: Public
**Uploaded by**: [Tonbi's AI Garage](https://www.youtube.com/@TonbisAIGarage)
**Uploaded at**: 2026-05-18
**Published at**: 
**Length**: 34:20
**Views**: 27709
**Likes**: 688
**Category**: Science & Technology

## Description

```
Module 3 of the Hermes Agent Masterclass — opening up Hermes' built-in memory system and stacking three more layers on top of it.

Sign up for my FREE weekly newsletter, where I spill my unfiltered thoughts on the latest AI news, cool research, and projects I'm building: https://www.onchainaigarage.com/

🐦 Follow Tonbi on X for real-time AI x blockchain updates! https://x.com/tonbistudio

Modules 1 and 2 got Hermes running, sandboxed, always-on, and reachable from your phone via Telegram and Discord. What you might not have realized is that Hermes' memory system has been quietly doing work the whole time. This module opens it up: how the built-in markdown memory actually works, the frozen-snapshot pattern that lets it stay cache-friendly, the four invisible safety features (cap-as-feature, save/skip policy, silent dedupe, injection scanning) that keep it from collapsing into a junk drawer, and then three more layers that stack on top — FTS5 session search over every prior conversation, the pluggable memory provider ecosystem (Honcho, Mem0, Hindsight, SuperMemory and more), and the Obsidian skill for long-form structured knowledge. Ends with a working setup of Honcho on a real agent and the Obsidian skill writing a multi-file vault for the HVAC-quotes project we've been building across the masterclass.

✅ Layer 1 + 2 deep dive — memory.md and user.md (the two markdown files in .hermes/memories), how they auto-load into the system prompt at session start, the frozen-snapshot pattern (writes hit disk live but only show up in the next session, so prompt caching stays valid), the three-action memory tool (add/replace/remove, no read), and the four design choices that make a 1,300-token cap actually work. Plus FTS5 session search across every prior CLI/gateway conversation in state.db, with the v0.11+ auto-prune+vacuum on startup so the DB self-maintains.
✅ Layer 3 — provider plugin landscape and a full Honcho walkthrough. Comparison of the main options (Mem0's server-side LLM extraction, Hindsight's knowledge graph + Reflect synthesis, SuperMemory's multi-container partitioning, and Honcho's dialectic user modeling), then `hermes memory setup` end-to-end against Honcho cloud — workspace/peer/session hierarchy, the four Honcho tools (conclude, context, profile, search), recall and write-frequency config, and a live test where the agent stores and recalls a name through the Honcho conclude path.
✅ Layer 4 — Obsidian skill (not a plugin, a bundled skill at skills/note-taking/obsidian) writing real Wikilink-cross-referenced markdown into an actual Obsidian vault. Used it for the HVAC-quotes project from the previous module: ten Bay Area HVAC providers researched into per-company notes plus an equipment-models index, all queryable by the agent on future sessions. Good fit for project-scale long-form knowledge that's too detailed for the 1,300-token markdown cap.

💻 Tonbi's GitHub: https://github.com/tonbistudio
🌐 Portfolio: https://www.tonbistudio.com

Resources:
🔗 Honcho (cloud): https://app.honcho.dev/
🔗 Nous Research: https://nousresearch.com/
🔗 Obsidian: https://obsidian.md/
🔗 Mem0: https://mem0.ai/

Timestamps:
0:00 - Intro and the four memory layers
1:30 - Layer 1: memory.md and user.md walkthrough
6:00 - Frozen snapshot pattern and the four safety features
12:00 - Layer 2: FTS5 session search and auto-prune
15:00 - Provider plugin landscape: Mem0, Hindsight, SuperMemory
21:00 - Honcho setup, dialectic reasoning, live test
26:00 - Layer 4: Obsidian skill on the HVAC project
33:00 - Wrap up and what's next

Coming Next:
Module 4 — Skills. Memory is what Hermes knows; skills are what Hermes does. We'll dig into the bundled skill catalog, the custom-skill workflow that lets your agent grow new capabilities over time, and continue building out the HVAC enhanced-quotes project with skills wired in. 👀

How are you handling memory in your agent setup — built-in markdown, a provider plugin, an Obsidian-style vault, or something else entirely? If you're running Honcho, Mem0, Hindsight, or SuperMemory in production, drop your verdict in the comments. If this masterclass series is useful, please like, subscribe, and hit the bell for Module 4! 🦐✨

#HermesAgent #HermesMasterclass #AIMemory #Honcho #Obsidian #Mem0 #LocalLLM #AITools #VibeCoding
```

## Transcript

Welcome to module three of my Hermes
agent masterclass. This video is going
to be on memory, very important topic.
So, modules one and two got Hermes
running, sandboxed, always on, reachable
from your phone, from Telegram or from
Discord. What you might not realize is
that Hermes memory system has been
quietly working the whole time.
Today we open it up, explain exactly how
the built-in memory works, demonstrate
it live, and then look at three more
layers you can use to extend it. So,
this is module three
of my Hermes agent masterclass.
So, here's how Hermes remembers.
There's a built-in memory layer. You can
see it this directory,
{dot}hermes/memories.
And the two main markdown files are
memory.md and user.md. And these are the
core parts of the built-in Hermes memory
system.
And these have been active since the
first time we booted Hermes up and
started talking to it. The agent's been
reading from them at the start of every
session and writing to them as we've
been using it. That's the built-in
memory system.
So, let's take a quick look of an actual
agent and the memory.md and user.md
file.
Before we get into that, we should note
So, the memory system is small. It's
about 1,300 tokens of system prompt
budget across both files. It's bounded.
Hard character limits force the agent to
curate rather than accumulate.
Well-designed, every constraint has a
reason, and we'll get into that in a few
slides.
And most people who use Hermes never
actually understand what's going on
inside it. So, today we're going to fix
that.
So, in the first half of this module,
we're going to take apart this layer
one, the built-in markdown, cover how it
loads, how the agent writes to it, the
frozen snapshot pattern, the hidden
safety features that make it work, and
how to seed it deliberately.
Then the second half, we're going to
look at three more layers that extend
layer one of the memory.
FTS-5 session search lets the agent dig
through any prior conversation.
Then you have external provider plugins,
Honcho, Memo, etc.
They add semantic recall and identity
modeling. And then there's the Obsidian
skill, which turns the agent into a
curator of a structured knowledge base.
But each one solves a problem layer one
can't.
But let's start there with the built-in
memory system.
And you can see it here down on layer
one,
the memory.md and user.md files. Then
you see layer two, the session search.
And this is full text recall over every
prior conversation. And this is built in
the agent and it's always on. Layer
three, like I said, external provider
plugins, Honcho, Memo, Hindsight.
There's eight options right now, and
there's always new ones coming out. So,
semantic recall plus identity modeling.
Layer four is Obsidian vault. So, this
one's different. It's not a plugin, it's
a skill. The agent writes structured
notes you can curate in your actual
Obsidian app.
And the nice thing is that these aren't
really alternatives, they stack. Each
one is additive. By the end of this
episode, all four are going to be
running at the same time. But first,
let's get to layer one more.
The built-in markdown files.
So, there's two files, and like I said,
both live at
{dot}hermes/memories.
So, the two files are memory.md, and
this is the agent's notes about
projects, environment, decisions,
lessons learned, 2,200 characters, about
800 tokens of system prompt budget.
User.md, this is the agent's model of
who you are, your role preferences,
communication style, about 375
characters, about 500 tokens.
Let me take give you a look at these
files in one of my real agents.
This is the memory.md file, and you can
see it's 24 lines of just plain
markdown. Um each section is segmented
by this section, this little S
uh character.
And all these are about things I've
discussed with this Hermes agent
instance. You can see
um
different projects that I've been
working on. When I gave it a task for
summarizing papers, you know, it has a
list here of priorities.
It has a list of my environment that I'm
working on, workflow preferences,
evaluation metrics that I'm looking at,
and then some of the different projects
I'm working on, like this visualization
tool for DLM
and pools on Solana.
Then there's the user.md file,
and this is about me, about Tom Bi,
from its perspective. You can see core
persona,
uh technical researcher valuing
detailed, reproducible memory, and
Windows-aware paper walkthroughs.
So, this is about me and what I've asked
it to do. Now, I didn't tell it to
specifically
put these in its memories. This is just
what it wrote down from our
conversations together.
You can see user prefers blank, minimal
project starts over pre-built templates
or branded defaults.
User expects thorough, proper
implementations with no shortcuts or
hacks.
So, those are the memory.md and user.md
files, and both of those load into the
system prompt at the start of every
session. So, that's it. That's the whole
magic of the system, just plain markdown
files.
And you can set the caps in your config
file under memory. You can set a memory
character limit and user character
limit. But the defaults are are fine for
most people. If you make this too long,
obviously you'll have more memories you
can store, but then every time you start
a new session, you're loading all of
this into the context. And if they get
too unwieldy, then your context is going
to get half filled up by your memory
files and not by actual work.
And since these are just plain
uh markdown files, you can edit them
yourself.
You can audit them, look at them like we
just did.
See if there's any contradictions.
They're also portable. You can move them
easily between different agents.
But there's one important mechanism that
you should understand.
So, that's the frozen snapshot pattern.
So, at the start of every session,
memory.md and user.md are loaded from
the disk and are rendered into the
system prompt. So, just once, that's the
frozen snapshot.
So, the agent has a memory tool.
In mid-session, it can call memory and
some type of action. So, this means the
disk is updated immediately, but the
system prompt does not update until the
next session.
So, why is it set up like this?
Performance.
The system prompt is what gets cache
control applied to it for prompt
caching. So, if it's changed
mid-session, you'd invalidate the cache
on every single memory write.
Caching is what makes long sessions
affordable. So, Hermes trades freshness
for speed.
So, keep this in mind, memory writes
don't show up in the same session, only
in the next one.
So, tool responses show live state,
system prompt is the boot snapshot.
So, now let's look at what this memory
tool actually does.
So, the memory tool has three actions,
add,
replace, remove. There's no read action,
content is auto-injected into the system
prompt at session start, like we said.
So, entries in the file are separated by
this little S.
This is the section sign character,
um and you we just saw it before.
So, you replace and remove entries using
a substring matching
uh via the old text parameter. You don't
have to quote the full entry, short
unique substring is enough.
If your substring matches multiple
entries, you get an error and the agent
has to be more specific, and duplicate
detection is automatic. Adding identical
content returns success with no
duplicate added.
So, memory entries get scanned for
prompt injection patterns and credential
exfiltration before being accepted. So,
Hermes won't let the agent write
something that looks like an attempt to
compromise the next session, and that's
a key security feature.
So, here's a real example of this. This
is my
um Hermes agent Scampi that's on one of
my laptops, and we were discussing this
paper
um about multi-agent systems. So, we had
a long conversation about it, and I
said, "Okay, save this paper for when I
get back to this."
So, it used
this memory, plus memory, user wants to
track
the paper.
And it added this memory, so it had it.
But in order to add this, it had to
remove something from shorter memory.
So, you can see it saved it.
Um
also cleaned up one duplicate Open
Writer video studio memory entry to make
room.
That was a little bit of maintenance,
right? You can see here this minus
memory.
So, it had to it reviewed its memories
and said, "Okay, this one's kind of a
duplicate about this one project.
Let me remove this while I add this."
So, why does this work? You have two
markdown files with 2,200 character cap,
plain text, no vector store, no
embedding model.
On paper, this shouldn't work. And the
reason it does is that every constraint
has a reason. There are four invisible
safety features holding it all together.
So, cap as a feature. The character
limit isn't an annoyance, it's actually
a design. Every system prompt header
shows current usage as a percentage.
When the agent tries to add past the
cap, the tool returns an error.
So, the agent has to actively decide
what to consolidate, and the cap is what
stops memory.md from becoming a junk
drawer. You take the cap out and the
system collapses into noise.
So, training train save skip policy.
The agent isn't deciding from scratch
what's memory-worthy. It ships with
clear policy. Save preferences,
environment, facts, corrections,
conventions, completed work, explicit
user requests. So, skip trivial
questions, web-searchable facts, raw
data dumps, session-specific
randomness.
This is why you don't need a separate
memory
manager agent. The main agent already
knows.
So, duplicate detection is no-op,
not an error. If the agent tries to add
content identical to an existing entry,
the tool returns success with no
duplicate added. It's silent. So, this
matters because LLMs retry.
Without this, every retry would fill
memory MD with the same fact written
four slightly different ways. The dedupe
keeps things clean.
And then injection scanning before
write.
Memory entries entries get injected into
the system prompt of every future
session. So, if an attacker
So, if an attacker could trick the agent
into writing a malicious memory, they'd
have persistent access across every
session would load the payload. Hermes
scans entries before accepting them
looking for prompt injection credential
exfiltration patterns like SSH keys
baked into facts and invisible Unicode
errors, so that vector is closed for
attacks.
So, the agent will fill out user MD um
automatically
as you talk to it and as you work with
it, but it's good as well to consider
seeding it yourself with just a couple
main facts about yourself.
What your
short-term goals are, what projects
you're working on.
So, that it has good context of why
you're working together and what you'll
be using the agent for.
You should note that the user MD file is
capped at uh 1,375 characters by
default.
So, keep that in mind while you're doing
it. You can't write your whole
personal history in there.
Okay, so that was layer one. Let's get
into part two, layer two here.
And that is FTS5 session search.
So, every CLI and gateway session is
indexed in this dot Hermes {slash}
state.db.
And this has everything. Every Telegram
message, every Discord exchange,
everything. It's indexed into this
SQLite
uh database.
The agent has a session search tool
and it can query its own conversational
history full text.
Results come back with uh Gemini flash
summarization layer on top. So, the
agent doesn't have to re-read raw
transcripts.
So, the agent calls to this autonomously
when it expects a prior conversation
might be relevant and you don't have to
prompt for it.
And in the newest version of Hermes
agent, it added this kind of nice
feature
auto prune plus vacuum on state.db at
startup. So,
that database used to grow unbounded for
heavy users. Now, it self-maintains. So,
if you were planning to set up a cron
job for to prune sessions, you can skip
it. It will just do it automatically.
So, let me show you session search in
action here. So, I'm here with Scampi
and you could see I'm asking it, "What
were the top 10 name suggestions
for the luxury bag and watch app that we
were discussing?" So, this was part of a
brainstorming session.
And something like this shouldn't be in
its memory file.
Let me see if it actually uses session
search here.
There you go.
This session search recall luxury bag
watch app name.
Cuz this is a kind of a small detail and
I brainstorm a lot with this agent. So,
this wouldn't be in the main memory.md
file, so it has to search that database.
The um state.db.
And you can see how it's searching here.
Luxury bag watch app name, watch or
watches or bag.
Trying to get more specific about that
topic.
And you could see here these were the
top 10 suggestions for this project.
And you see memories updated down here.
Um but it was able to go back and fetch
these memories.
So, here's a little comparison between
the persistent memory and what we had to
do right here, which was session search.
So, the persistent memory, that's the
two markdown files. This is capped at
around 1,300 tokens
total. Session search should be
unlimited for all sessions. Everything
should be stored there. Speed, it's
instant already in the context. Um this
did take a little bit. It was a search
and then a summarization.
Um use case, key facts are always
available.
And use case for this is something like
I just showed you. You know, did we
discuss X last week?
Management, created by the agent.
This is automatic. Every session is
stored.
Token cost is fixed because the the
total size of it is fixed.
And you know, token cost is on demand,
only when you have to search it.
And depending on that search, it would
probably cost more in terms of tokens.
So, these are the two main built-in
memory functions and they're pretty
great, actually.
I would was pretty impressed with both
of them.
So, you don't have to necessarily go out
and go to other plugins for most people.
The built-in memory function is plenty,
but there are a lot of
provider plugins and community-built
plugins for memory since it's a common
issue and really a critical part of what
makes an agent functional as an agent.
So, this is how it works and in version
three uh version
in version seven of Hermes agent they
introduced a pluggable memory provider
ABC.
Third-party backends implement a simple
interface and register through a Hermes
plugin loader.
So, you can only have one provider
active at a time.
And this is the rule. You can't run
Hancho and Memo simultaneously.
Pick one, run it, switch later if
needed. Uh switching does not migrate
the data.
And this sometimes trips people up.
If you've been using Hancho for 3 months
and you flip to Memo, all of your Hancho
stored memories don't follow you
necessarily.
Uh so, plan carefully.
The built-in markdown layer is always
on, even with a provider configured. So,
layer one doesn't go away. It's just
that this kind of plugin memory
augments it.
When a provider is active
when a provider is active, Hermes does
five things automatically.
Injects provider context into the system
prompt.
Prefetches relevant memories before each
turn. Syncs conversation turns to the
provider after each response. Extracts
memories on session end and adds
provider-specific tools.
You can see the setup commands here.
Hermes memory setup. Hermes memory
status. Hermes memory off.
So, you can have this plugin provider
and still use the the built-in memory.
So, here's a little bit of the
landscape. There's a lot of
different providers. A lot of community
members and developers have been
developing memory systems.
So,
there's a lot more beyond beyond this,
but this is just what my Hermes agent
found in its research.
So, very quickly um Memo is probably the
most well-known.
Just in general, it has the most uh repo
stars here, but you could see
it's probably one of the most well-known
and the unique feature of this is that
it has a server-side LLM extraction.
Um but there's other providers like
Supermemory here
which uses multi-container partitioning.
Hindsight which uses a knowledge graph
and reflect synthesis.
The one we're going to be trying out
today is Hancho uh which is very popular
in the Hermes agent community.
It's a new research-maintained
first-party integration.
It has its own dedicated Hermes Hancho
CLI surface.
So, no other provider has that one.
And it's particularly interesting
because it has dialectic user modeling.
So, it takes a unique approach about
really learning about you as the user.
So, I obviously can't run through all of
these different plugins. So, to
represent it, we're just going to try
Hancho
and I will walk you through how to set
it up and
what its features are.
So, Hancho, which is the one we're going
to be actually demoing here, this is the
card for it.
Um the model that it uses dialectic
reasoning. The agent derives
conclusions, which are insights about
the you as the user. These accumulate.
The agent isn't just remembering facts
you stated. It's building a running
model of your preferences, communication
patterns, and goals.
So, here's the hierarchy. Workspace
contains peers. Each peer has sessions.
And each session has messages.
Each Hermes profile gets its own AI peer
in a shared workspace.
So, for instance, a coder profile and a
writer profile will see the same user
representation. But each agent builds
its own identity.
So, there's four main tools here.
Hancho conclude, Hancho contacts, Hancho
profile, Hancho search.
Hancho conclude triggers server-side
dialectic reasoning.
Hancho contacts retrieves relevant
context for the current conversation.
Hancho profile views or updates the
user's profile. Hancho search does
semantic search across stored
conclusions and observations.
So, the config file is going to live at
your
Hermes {underscore} home
hancho.json.
And the key options in the config worth
knowing are recall mode, which controls
whether context auto injects.
Um
write frequency, which controls when
conclusions get computed. Async per
turn, per session, per end turns.
Dialectic reasoning level is a depth
dial. So, minimal up to max. And it
should be noted that the latest version
version 0.11.0
it shipped a major Hancho overhaul.
Context injection auto handling per
turn, cost safety to prevent runaway
think calls, session isolation.
So, it's a very nice upgrade and
hosting, you can do it by cloud
which is the app.hancho.dev or you can
self-host it for free.
So, Hancho models you, not just facts
about you.
The dialectic update is closer to how
humans build mental models of people.
So, very quickly I'm going to run
through some of the bigger memory plugin
providers.
We're going to be demoing Hancho, so I
won't go in as depth much depth, but I
wanted to touch on a few of these and
how they approach memory in different
ways.
So, Memo, which is a very popular one,
um like I said,
it uses server-side LLM extraction and
this is kind of the distinctive thing
about this. When Memo ingest ingest a
conversation an LLM extracts discrete
facts. Then a second LLM pass per fact
decides, "Is this new? You can insert
it, update, modify existing entries,
delete a contradict something, or no-op.
But, it's already known.
And deduplication is automatic.
So, what makes it distinctive is that
other backends embed embed raw text.
Memo embeds extracted facts. So, less
recall noise, but adds LM cost on every
write cuz there's a second pass there.
Then we have Hindsight, and their model
is a knowledge graph plus entity
resolution plus multi-strategy
retrieval.
This is the structurally densest of the
four options we're going to be looking
at. And Hindsight stores conversation
turns with metadata, builds entity
relationships, and offers three
different retrieval strategies.
You can see the different tools here,
but what makes it unique is that it
Hindsight auto retains full conversation
turns, including tool calls. So, session
level document tracking is also
included.
If you need a knowledge graph with
explicit entity relationships, this is
your pick.
Hindsight is really the one that
synthesizes across memories, and the
Reflect tool is generally different from
anything else in the ecosystem.
Um the last one we're going to look at
individually is Supermemory, and this is
a multi-container memory partitioning.
Uh so, the containers are first-class.
Each container gets its own retention,
search mode, identity. If you need five
memory namespaces per client, per
project, per team, Supermemory is the
cleanest fit for that.
So, what makes it kind of distinctive is
two things.
Context fencing. It strips already
recalled memories from captured turns to
prevent recursive memory pollution. And
session graph ingest.
So, at session end, the Supermemory
ingests the conversation as a graph for
richer future retrieval.
There's a couple others that my agent
found here, um and probably more are
going to be coming out.
Let's try installing one and see how how
it works. And we're going to be doing
Honcho.
And you're going to need an API key for
this to do the cloud version, which
we're going to do. So, this is
app.honcho.dev
to log in here.
Okay, so we're going to set up our
organization.
So, if you add a credit card, they'll
give you 100 credits for free for now at
least. I'm not sure
if that promotion will continue. But,
you can see I got 100, and I just added
my credit card.
Okay, I got my API key.
So, this is how we install it. Hermes
memory setup.
Pick memory provider as Honcho, add the
API key.
And that should be it.
Um let's try it. Okay, I did Hermes
memory setup.
And then you can see all the providers
here
um that they have built in. Some of the
ones we were talking about, right? Memo,
Hindsight, Supermemory, some of the
other ones as well, the smaller ones.
Um
built-in only
is the by default always selected.
But, let's try Honcho.
So, cloud or local?
Cloud.
So, the API key, and you just paste it
in here.
Okay, I did that. Username.
Uh Tom B.
AI peer name.
Hermes.
Um Hermes, let's just do that.
Workspace ID Hermes.
So, Honcho gives Hermes
persistent cross-session memory.
Like I said, this honcho.json file.
And then observational mode directional.
All observations on.
Each AI peer builds its own view, which
is the default.
And then unified shared pool. User
observes self, AI observes others only.
So, I guess we'll try the
directional, the default one.
Write frequency.
No token cost. Async. Yeah, that's fine.
Recall mode.
Let's do the default hybrid.
And then uncapped.
Dialectic cadence. How often Honcho
rebuilds its user model.
One every turn.
Two every other turn. So, it's
recommending
uh let's do two cuz that's the
recommendation here.
Dialectic reasoning level.
So, this is the depth Honcho uses when
synthesizing user context
on auto-injected calls.
Low.
Uh medium.
Max.
So, reasoning level
I don't think we need to lower. I think
should be okay.
Session strategy.
Per session, per directory, per repo.
We'll do per session.
Keeping most of these as defaults here.
There we go.
These are the Honcho Honcho tools
available in the chat. So, my agent can
now have access to these tools, and
these are the other commands that I can
do for it.
Showing the config. Hermes Honcho mode
changer. Recall change the recall
observation modes. The stuff that we
just set.
Um
update peer names.
Hermes Honcho map. Map this directory to
a session name.
Okay.
Okay, so I'm going to do have some
natural conversations. I actually wanted
to do some research, so this is a good
opportunity.
So, I'm going to have a couple
conversations with Hermes agent. I'm in
You see the the TUI right here.
And I'm going to talk to it now and see
how much from Honcho it remembers.
Let me do a little research on my own
right now.
Okay, so I had a little bit of a
conversation with it about different
project ideas.
Um so, then I checked Hermes Honcho
status.
And we can see
it had some explicit observations.
And this is about Blender MCP, which is
something I was asking it about.
Um that was an observation, and then I
checked Hermes Honcho peer.
This is my identity.
And this is the AI peer identity,
Hermes.
You can see it's working.
Okay, so we're going to be seeing Honcho
more in the coming modules, but just to
show you one little tool call I did.
I asked it what my name is, and it said
um I haven't told it explicitly.
So, it says I don't know your name yet
map for memory yet, but it used this
Honcho
tool call here to try to remember it.
You can see Honcho conclude right there.
I told it my name is Tom B.
And it used that Honcho conclude. It's
also you can see this is both the
built-in memory itself
Got it, Tom B. I'll remember that. Good.
So, you can see this is a good case of
the both the built-in memory itself
adding this to the
um this is probably going to be the
user.md file.
And also the Honcho memory learning
about me as we go.
But, like I said, as we continue to work
through this masterclass, you're going
to see Honcho in action. But, this is
how you set it up
and get it working.
So, the last memory tool we're going to
discuss is not actually a plugin. It's a
skill. And this is Obsidian, which is
very popular to use as a memory tool.
Um
you may have noticed that Obsidian was
not with the other providers, and that's
because it's not a plugin.
It's not in the same slot as Honcho or
Memo. It's a bundled skill
at skills/note-taking/obsidian.
And it uses these kind of tool calls
against the vaults.
Environmental variables Obsidian vault
path, and this is the default.
It's a file system-based
skill. There's no MCP server needed. Uh
no Obsidian app needed.
It's just headless Linux, so
the app couldn't run there anyway.
One note, there's this Obsidian vault um
option in the config, but it's no longer
in use.
So, for this you're going to have to
install the Obsidian app, uh which I had
already done.
Um if you watched my LM Wiki videos, you
know I've I've had this.
You're going to install this locally.
Uh it's not a heavy file.
But, then you're going to want to open
folder as a vault.
And this is going to be the main
Obsidian vault.
And this is where you need to um
this is where you want to set
in the environmental variables what the
vault path is. So, this all has to be
the same.
Okay, so once we have the the path set
up for the vault, and we can see the
empty vault here. It's right here.
There's nothing in it.
But, let's go into Hermes.
Okay, so we have the vault set up, and
we're going to do a little bit more
research. If you remember from the
previous two videos,
I had this great business idea to do
kind of enhanced AI-enhanced quotes
for
contractors. I think for now I'm going
to focus on HVAC providers.
This cuz that's where I noticed um it
was the biggest deal.
So, the previous episode we had done
some competitor research, found that my
idea was pretty much viable, I would
say.
And we wrote out a business plan. So,
now we're going to do a little bit more
research on specific providers
in the San Francisco area.
And I want some information about what
like main units or carriers that they
use.
Providers.
And then we're going to use our Obsidian
vault to
organize not only the providers, but the
main models that they use.
Here we got our providers
from Hermes.
The next prompt I said, "Could you find
the main HVAC models
um that the 10 providers provide?"
Store information about the providers
themselves and the HVAC model companies
using the Obsidian skill.
I want to use
our Obsidian skill here.
Um you see it invoked right here.
It also created a skill.
So that'll come in handy for our skills
episode.
This is local provider research.
And using Obsidian like this is useful
if you have like a large project like
this with a ton of data.
It's not a simple memory, but you need
to save this information
because it's part of a larger project,
something you're going to come back to
later.
And having it organized in an
Obsidian vault uh just makes it a lot
easier for the LLM to read. Everything's
going to be organized in markdown files
in a format that makes it very easy to
retrieve the information.
You can see as it's working here,
this is in the vault itself. It's
starting to populate
the uh the vault with this information.
All these different these are all
different files.
Tabbed about each of the the different
companies, their information.
This is one. This is kind of like the
the summary one, which has all the
research with all the links here.
And since this is in a wiki format, it
has all the cross links.
Yep, so it has This is all the HVAC
equipment.
Um it couldn't find specific models on
the websites itself, so
we'll have to dig a little bit deeper to
get that.
Um but it has the different types of
systems.
Not specific models, but
it's a good starting point.
So you can invoke it like I just did
here. Just say use Obsidian skill. Or
you can use this Obsidian
uh slash command to read, search, or
create notes in the Obsidian vault.
So this is more of a longer-term memory,
like very much more detailed on specific
topics or projects
or just domains of knowledge. But it's a
very popular and very common
memory adjacent skill.
Like I said, it's not a memory plugin
per se, but it definitely provides
the function for long-term memory.
So those are the four layers that we
walked through in this module. The
built-in memory system, which is already
pretty good.
User MD and Memory MD. The session
search from the
full session logs.
And then Honcho as kind of a
representative of the plugins.
And lastly, Obsidian, which writes
structured wiki link vault notes that
you can keep working in and it serves as
kind of a long-term
detailed memory or knowledge base for
your agent.
So there you have it. That's a breakdown
of the memory system
in Hermes agent.
We got to see how the built-in memory
system works as well as a plugin.
Uh took a little look at the memory
plugin ecosystem and then Obsidian
vault.
So I hope this was helpful. I thought it
was worth dedicating a module on this
cuz memory is such an important issue
for agents.
And one of the real frustration points
that I think a lot of agent users have
is with memory.
So it's important to touch on how it
actually works with Hermes agent and
what other options exist to kind of
enhance it
even further.
So this is going to be the end of module
three. And in the next module,
uh we're going to touch on skills. Cuz
memory is what Hermes knows, skills are
what Hermes does.
We already kind of began it with the
Obsidian skill that you saw here. And a
lot of this stuff is going to intersect
with one another, I'm sure, in the
skills
module and later modules.
You'll see a lot of the memory functions
as well, since we now have Honcho set up
and Obsidian
as well as, of course, the base.
So in the next episode, we're going to
explore skills from Hermes,
especially the custom skills
function that is really unique to Hermes
and how your Hermes agent kind of
evolves with you, as well as continue
working our HVAC enhanced quotes
project, actually creating some skills
to move this project along.
So I hope you like this module. This has
been module three of the Hermes agent
masterclass.
Thank you for watching.