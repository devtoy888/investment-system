![Thumbnail (1920x1080)](https://i.ytimg.com/vi/L3WdVeMaYZM/maxresdefault.jpg)
# [Hermes Agent Masterclass: 4. Skills](https://www.youtube.com/watch?v=L3WdVeMaYZM)

**Visibility**: Public
**Uploaded by**: [Tonbi's AI Garage](https://www.youtube.com/@TonbisAIGarage)
**Uploaded at**: 2026-05-25
**Published at**: 
**Length**: 41:19
**Views**: 9973
**Likes**: 272
**Category**: Science & Technology

## Description

```
Module 4 of the Hermes Agent Masterclass — how skills work in Hermes, including the ones the agent writes for itself.

Sign up for my FREE weekly newsletter, where I spill my unfiltered thoughts on the latest AI news, cool research, and projects I'm building: https://www.onchainaigarage.com/

🐦 Follow Tonbi on X for real-time AI x blockchain updates! https://x.com/tonbistudio

Memory was what Hermes knows. Skills are what Hermes does. This module opens up the skill system: the anatomy of a SKILL.md file (front matter + body, why the description is the picker hint that decides whether the skill ever fires), the progressive-disclosure pattern that lets Hermes ship 80+ bundled skills without bloating the context window, a tour through five of the most-useful categories (research / GitHub / MLOps / productivity / creative), the full picture of where skills actually come from — bundled, official-optional, the Hugging Face community index that's surfaced automatically inside `hermes skill browse`, plus Anthropic / OpenAI / Lobe Hub tabs and direct-URL drops — and the auto-written ones the agent generates after complex multi-tool turns, which then live alongside everything else as "procedural memory." Closes with the Curator (v12 feature, v13 upgrades) that grades, prunes, and consolidates skills on a 7-day cycle, and a live build of a custom `unit-lookup` skill that consumes the HVAC Obsidian vault from Module 3 and produces enhanced-quote markdown cards.

💻 Tonbi's GitHub: https://github.com/tonbistudio
🌐 Portfolio: https://www.tonbistudio.com

Resources:
🔗 Nous Research bundled-skills directory (browseable): https://github.com/NousResearch/hermes-agent/tree/main/skills
🔗 Module 1, 2, 3 of the Hermes Agent Masterclass:
🔗 Creative skills standalone (Manim / P5JS / TouchDesigner MCP): https://youtu.be/JX2RYeKugrc

Timestamps:
0:00 - Intro: memory is what Hermes knows, skills are what it does
2:00 - SKILL.md anatomy and progressive disclosure
6:30 - Bundled skill tour: research, GitHub, MLOps, productivity, creative
23:00 - Where skills come from: hubs, Hugging Face, marketplaces
25:30 - Agent-written skills as procedural memory
31:00 - The Curator: grading, pruning, consolidating, pinning
34:30 - Building the unit-lookup skill for the HVAC project
38:30 - Wrap up and what's next

Coming Next:
Module 5 — models and providers. We've been running on whatever main model was set back in Module 1; next episode takes that apart properly. 20+ provider tour, smart routing and cost-tiered fallback chains, the fresh SuperGrok OAuth integration with 1M-token context, Grok 4, and the OpenAI-compatible local proxy that turns a Claude Pro or ChatGPT Pro subscription into an endpoint Codex can hit, plus a quick auxiliary-models recap for anyone who skipped the standalone video. 👀

Which Hermes skill have you actually used the most — research, GitHub, one of the creative ones, or have you been writing your own? If the Curator has done anything interesting to your skill library (or anything unwanted), drop the details in the comments. If this masterclass series is useful, please like, subscribe, and hit the bell for Module 5! 🦐✨

#HermesAgent #HermesMasterclass #AgentSkills #AITools #LocalLLM #Manim #P5JS #TouchDesigner #
```

## Transcript

So, welcome back to Hermes Agent
Masterclass. This is module four and
this is is going to be on skills,
which are a critical part of any agent.
If you watched module three, you know
that Hermes remembers. It has built-in
memory, session search, Honcho,
Obsidian, other types of memory plugins
as well.
Memories is what Hermes knows. Skills
are what Hermes does.
And the agent already has skills. When
you install Hermes, it already has
around 80 of them in this Hermes/skills
file directory.
And those are just ready to go from the
start.
But there's also a lot of optional
skills and skills you can actually build
and develop yourself, as well as the
auto skill function that Hermes is kind
of known for.
So, this is going to be today's video
and in today we're going to be talking
about the
structure of a skill.
I'm going to show you a couple of the
kind of bundled skills in different cat-
categories, show you what they do,
and then I'm going to show you where to
find them,
or develop them on your own.
And then we're going to talk a little
bit about the skills curator, which is a
newer function.
And lastly, we're going to build using
our enhanced
uh quote project that I've been building
on from episode to episode. We're going
to use a skill that'll be helpful for
that project.
And if you like this video, please
subscribe to my free weekly newsletter
where I give my honest thoughts about
the week's AI news that I can't share
here, as well as interesting research
and papers that I found, and what
projects I've been building behind the
scenes. There's a link in the
description, or go to
onchainaigarage.com.
Every word is written by me, mistakes
and all. So, if you're sick of AI slop
articles or all hype with no substance,
subscribe and give AI Garage Weekly a
shot. Now, back to the video. Part one
is the anatomy of a skill.md
Because the thing is, a skill is its
skill.md. That is the base form of any
skill. It's the one file you need to
actually have a skill.
And it's just a plain markdown file.
There's no registration, no build step,
no compiler. The agent just reads it
like instructions.
So, you can see kind of a breakdown of
how this looks like in your directories.
It'll be under your slash
Hermes.Hermes.slashskills
slash whatever category it happens to
be. This one is research and then
archive, which is the name of this
skill.
So, you can look inside this directory
and see you're always going to see, like
I said, a skill MD file. This is the
skill itself.
And then, there are other kind of
optional
directories.
There's a reference directory for
context that the agent can pull on
demand. Templates for boilerplate.
Scripts for executable helpers and
assets for binary stuff.
So, if you drop this skill directory
into the Hermes slash skills directory,
this skill exists. The next time the
agent boots, or if you run reload
skills, it's there and you can use it.
So, looking a little closer on the skill
MD file, this is the front matter that
it has. And there's two required fields.
The name. This is archive.
And then, a description. Search archive
papers by keyword, author, category, or
ID.
There's a bunch of other um kind of
optional ones. There's platforms,
version, metadata tags, a bunch of other
stuff.
You can see if you want to see all of
the bundled skills, this is the
uh new research GitHub Hermes agent
where you install it to begin with, but
you can just actually come here and look
at all of the skills and all the
specific skill MD files. So, this is the
archive skill as well.
So, this is the front matter you can
see. It has description, version,
author, license, platforms, and then
metadata.
You can kind of take a look at what it
has down here. This is all going to vary
based on the skill itself. Only these
first two items are required.
But, you'll see items like when to use,
procedure, pitfalls, verification.
And the agent will read that this body
on demand.
So, the key thing about description here
is that description is the picker hint.
It's what the agent sees in the skills
list.
The when to use
instruction in the body section is an
expanded trigger context that the agent
reads after it's already picking up this
skill. So, if you have a concrete
description, the skill will fire
whenever you want to use it.
If you have a vague description, the
skill never gets picked and the body
section never matters. So, very
important to make sure that the
description here is very clear and
accurate to what the skill does, so that
the agent can actually pick it up.
Give you another quick example. This is
the Google Workspace skill, the
skill.md,
which comes bundled. The description
very clear, right? Gmail, calendar,
drive, docs, sheets via gwscli or
Python. So, it tells you exactly what
platforms it's going to be useful for.
And you can look down and you see it has
references, scripts that help execute
code, and then first-time setup,
and some triage. A lot of times skill.md
files will have this kind of
troubleshooting element as well.
So, you can see all of the instructions
there.
So, here's the thing that makes the
whole system work, and it's called
progressive disclosure.
If you take a look at the red
uh naive approach,
which would be to load all 80-plus skill
bodies into context every turn, which
obviously creates token bloat. You can't
ship 80 skills that way. So, the Hermes
approach,
here in the green you can see, the agent
only sees the title and description in
something called a skills list. When it
picks a skill, only that skill's body
load. Everything else stays on disk,
which is necessary
to keep the context reasonable.
And once again, this is why the
description is so important in your
skill.md file.
If it's too vague, it'll never get
picked cuz that's the only thing your
agent can see.
Now, let's start looking into more
actual skills that come with your Hermes
agent.
They're always adding more, so this is
as of
version 14, I believe we're up to.
And these are all 24 categories, you can
see.
It's around 80 different bundled skills.
It's a little closer look, but some of
these you'll probably never touch if
it's not relevant to what you're doing.
Uh others you'll be using every day.
So, you can take a second, take a look
at all these here.
And like I said, you can check the
GitHub. You see on the side here under
the skills directory, you have all of
these different categories as well.
So, you can look into
these skills if you want to see if they
can help be helpful for you.
But for today's masterclass, we're just
going to
look at five of them.
Uh creative, GitHub,
ML Ops, productivity, and research.
So, this is research category.
And there's a bunch of others, but
research is a key function for almost
everybody working with agents, right? We
need to read papers,
read markets,
and just generally do research. A lot of
my Chrome jobs are all based around
research.
Here are a couple of them. Archive,
which I talked about before. This hits
the free archive API. Archive is uh for
research papers.
LLM Wiki, and this is the Karpathy-style
Wiki. It works as an Obsidian vault.
And uh blog watcher here. It tracks RSS,
summarize new posts.
Polymarket, uh which pulls prediction
market data, and research paper writing.
So, this does structured paper drafting
with citations.
And there are lots of other optional
skills as well.
Okay, so I'm going to show you this
skill
um here with my Hermes agent
and I'm going to ask it
uh research recent papers about
recursive
reasoning models.
And you can see it automatically goes to
a couple skills here. Skill one is this
archive, which I showed you before
and then paper summary, which is another
skill
uh to read some of these
and then
give me a summary here.
And while it's doing that, if you want
to check out your skills that you have
uh Hermes dashboard here
you can see them all in one easy place.
Here, this is the web dashboard that
just runs locally. If you go to the side
here in the skills
you can kind of see all this
um skills you have on this specific
Hermes agent. So, if I went down to
research here
I could see
um that I have archive and then paper
summary is also another research skill
which summarizes academic papers from
Hugging Face or archive.
So, this is another way kind of see what
you have on your specific Hermes agent.
Because sometimes you may not It might
just create skills without you really
realizing unless you're looking closely
at all the tool calls or it may install
some skills it needs based on whatever
task you give it.
Okay, so it's producing my answer now
just to show you that it actually
worked. These are all the different uh
papers that it came back.
So, those skills just help with this
kind of research doing it faster and
more efficiently
finding the proper information
and making sure it doesn't fall into any
kind of
common problems or issues.
So, the next section we're going to kind
of look at is the GitHub and dev
uh categories. And obviously, if you're
doing any kind of development work,
you're going to be using GitHub a lot.
So having these kind of skills are very
useful just to manage manage your GitHub
repos.
So this is kind of combining kind of
cheating here, but two categories the
GitHub and software development which
has a lot of different kind of
development related uh skills you can
use.
Uh but for this category, you can see
here we have GitHub PR workflow.
And this is the headline full life cycle
branch through merge in one skill,
really useful. GitHub code review and
GitHub repo management that kind of
round out different uh GitHub
skills to review diffs or issues or
anything like that. Then uh on the
software development side, we have
systematic debugging
which is hypothesis-driven diagnostic
methodology.
Writing plans which makes an agent emit
a plan before code which is very big for
kind of complicated large-scale tasks or
projects.
Sub-agent-driven development is for
delegation patterns.
And all the GitHub ones use the GHCLI
when it's available.
But they'll fall back to the Git plus
REST API if not. So they work on any
machine with Git.
So I have here I have this GitHub repo,
uh one of my older ones on Turbo Quant.
So let's give it this.
So I said, "Can you check um this the
Turbo Quant PyTorch repo and tell me any
outstanding issues?" And you can already
see it's checking
using these skills right here, the
GitHub issues.
And then code base inspection skills.
So these are kind of the GitHub just an
example of GitHub skills that you could
use.
And if you look here,
uh GitHub issues.
We look here, GitHub issues.
And skill MD see see see what it does.
Create triage label assign GitHub
issues.
So that is cuz I specifically asked
about GitHub issues and have this nice
little management skill to view and
create issues,
manage issues. Yeah, so it has a lot of
instructions for all of these.
And there you go. It gave me all the
results, all the open issues.
And
um what needs to be done for all of
them. So, you can see recommended action
list. And this is all using the
GitHub issues skill.
So, next one I want to look at is one
that perhaps most people may not need,
but I do a lot of kind of local LLM
operations. So, ML ops, machine learning
operations is an area, lots of skills
that I use. And if you're running local
LLMs, which I know a lot of people are,
with Hermes agent,
uh you're going to be using some of
these skills, certainly.
There's not a ton in terms of uh bundled
skills. Most of them are going to be has
very lean core bundled. Most of them are
actually going to be kind of optional
skills cuz there's so many different
options you can go with
machine learning ops. And if we look at
the
the ML ops directory on uh the new
research GitHub, you can see they're
categorized even further into
evaluation, hugging face hub, inference
models, research, training, vector
databases. So, a lot of when you see my
machine learning
uh videos, a lot of those are based on
training
training skills.
And we can see these are optional ones,
but uh
PFT PFT accelerate, PyTorch, Symbo. Um
so, you're going to use a lot of these
if you're doing any kind of local
training or fine-tuning or stuff like
that.
So, if you want to see full like a full
training section, you can check out my
machine learning episodes. I use lots of
those skills. But just for this, I'm
going to see
if I do, can you find three model
options for running a local model on my
RTX 3060 locally using llama.cpp?
Okay, you see it did use the llama dash
cpp skill.
Uh which is one of the the machine
learning op
skills. You can see it's down here under
inference.
Uh you go ML ops
inference and then llama.cpp
or /cpp.
Uh which is
the one way, perhaps the best way to run
local models with a lot of different
modifications and stuff like that.
So, this is the skill.
Um it can be used for actual inference,
but in this case we're just doing repo
discovery, which was kind of my question
asking for a model that would fit me
well.
So, you see here it came back with the
answer fairly quickly.
Uh so, the best default quant 3 8-bit.
So, this is
the model it recommends and gives me
different kind of options of how to run
it. See, running it here with flash
attention.
So, this was more kind of a
research-based question, but like I
said, you can do training
uh fine-tuning any kind of
machine learning
uh
tasks locally
uh with Hermes Agent. It's really good
for that. There's a lot of different
skills for it.
So, the next category we're going to
look at is productivity and this is for
business systems, documents, workflows.
This is a lot of what you would probably
use
in your day-to-day work. A lot of times
when we're talking about agents and
agentic workflows, a lot of it is just
about efficiency and productivity,
right? So, definitely look into what
skills fall under this category. You see
a couple here, Google Workspace does
Gmail, Calendar, Drive, Sheets, Stocks
through Python.
Uh Notion here uh has a full overhaul in
the most recent version
for a new developer platform, but you
can read and write Notion pages and
databases. Very useful if you use that
in your work teams.
And then there's linear.
Uh this is for issues, project cycles
via linear's graph QL API. Uh nano PDF
is for doing uh PDF manipulation
locally. PowerPoint and OCR and
documents are both for document related
work.
So, as our example, I think we're going
to try to use this PowerPoint tool.
And you can see the full skill here, the
PowerPoint skill. Once again, this is
their GitHub.
Uh but you could see
this is the preview
of the the skill.md file.
Tells you when to use it.
Basically, anytime you're trying to
create a a PowerPoint file, or not even
create, just read it or analyze it,
anything.
You can see what it has.
Design ideas.
Avoid common mistakes. These are really
useful in skills
because if the model or agent doesn't
know this stuff, it's very easy to fall
into these kind of common mistakes.
And you see everything here.
Very detailed instructions for how to
manipulate
PowerPoint files. So, let's go back into
Hermes.
And the prompt I'm giving it is, can you
turn this into a PowerPoint
presentation? And I'm giving it this
markdown file. This was my original
concept file for the
Infinite Humans Among AI um game
experiment I did.
If you look into
um
the the PowerPoint skill itself, you see
the skill.md file, but this also has
kind of this optional scripts
uh directory, which I talked about
earlier. Not every skill's going to have
this, but this will have some helper
scripts, some executables. These are all
Python
Python files.
Um like this one adds a slide.
This one cleans
uh, the material, the files. So, having
these kind of helper scripts as well is
very helpful.
And you can see back in Hermes here, the
first thing it did is it used the skill
PowerPoint, which is what we were
talking about.
Okay, so it generated it. So, let's take
a look at it very quickly. See what we
got.
There we go. We got a, um,
a PowerPoint presentation.
Uh, kind of basic. If I was going to
actually use this for a presentation, I
would tweak some of the visuals, but you
can see it took that, which was just a
markdown file, didn't have anything
visual inside of it, and kind of it
actually did try to create some visuals
and stuff.
So, that's a nice little skill. There's
a couple different ways to make slides.
I usually just do like an HTML slides,
but if you specifically want PowerPoint,
uh, it's a nice skill to have.
So, the last category we're going to
look at is creative, and this is
animation, diagrams, generative,
directly relevant to anyone doing visual
content. It's kind of the most fun, uh,
group of skills.
If you want to take a look, I did a
specific video about Manim video here,
um, P5.js and TouchDesigner MCP. So,
check out my other on my YouTube channel
if you want to take a look at those.
They're all pretty good, but just to run
down a couple of these. Manim video, um,
if you looked at my other YouTube video,
but it creates kind of video explainers
out of just a text or prompt. Uh,
Excalidraw, which is programmatic
hand-drawn diagrams. I used that
actually in the, um, LM Wiki Obsidian
video as well.
It's pretty nice.
P5.js creates really nice like art from
a single slide or anything you give it.
Um, it created a really nice thumbnail
for me.
ComfyUI, which is Stable Diffusion via
ComfyUI's official CI CLI and REST. This
is one of the newer ones. Um, up I might
do a video on comfy UI
in the near future. So, look out for
that. Touch designer like I said I did
this
in that other video and it creates kind
of really cool
video effects and it's kind of difficult
to use. It's kind of a advanced tool but
if you learn how to use it you can
create really cool stuff. Humanizer
which is strip AI-isms from generated
text always necessary if you're doing a
lot of AI written text if you don't want
a thousand M dashes everywhere.
So, for today I'm going to try I think
I'm going to try this pixel art one. I
haven't done that. I want to try
something I haven't done yet. So, we're
going to try to create pixel art from my
PFP.
So, just the prompt here is can you turn
this and that's the the path to the
my PFP PNG file into pixel art. So,
we'll see
if it's able to do that.
And yep, it called the
pixel art skill. Interesting, there must
have been other
pixel art skills. In just a second we
can look at this cuz ambiguous skill
name. That's pretty interesting cuz
there were three skills probably in the
description that refer to pixel art. Um
but then it specified creative which is
the name of the category in the official
skills and then pixel art.
Um cleaner
do SNES classic.
Just looking in the GitHub
of it you can see pixel art
here as one of the the skills.
Can convert any image into a retro pixel
art and then optionally animate it.
It's interesting. So, it has these This
is another one that has scripts. This
one actually has references as well.
This references file which is path
named palettes. Interesting. So, this is
is of the
the different palettes based on the
type. We did Super NES.
Um but there's different artistic
palettes that goes with.
Interesting. So, the scripts as well,
this has a bunch of different Python
scripts that are going to be used
uh to do different functions.
And you see pixel art video as well.
This is the main skill file though.
When to use, this also has a when to
use. User wants retro pixel art.
User asks for NES styling, stuff like
that. And it has the full workflow. So,
you can kind of see here through all
these examples, what's in the skill.md
file is just instructions.
And there's probably some kind of
um
pitfalls, yeah. So, this one also has
kind of like a pitfalls troubleshooting,
things to avoid, gotchas, stuff like
that, which seems pretty common in skill
files.
Okay, it's done. It's pretty quick
actually, this one.
Let's see if it looks decent.
There we go. It is pixelated.
This probably looks better um if it's
not an illustration like this cuz mine
was all already kind of basic
basic lines, but it definitely is
pixelated. If you can zoom in here and
see.
It's more of that kind of style,
especially in the hair you can kind of
see it more.
There you go.
So, that is the creator. And so, there's
a ops optional categories as well.
And you can see this is how you install
an optional skill. These are the ones
that don't come with it. Some example
are blockchain,
uh finance,
health, security, and there's a bunch of
them.
And we're going to get more into how to
find these, but you can look in this um
{slash} skills list.
And there's 17 optional categories total
that aren't covered in the uh ones
you'll find up here in the uh GitHub.
So, part three of this video is going to
be about the skills hub, and this is
where skills come from. So, we just
walked through bundled and optional
skills, and now I'm going to show you
the full picture. Every place skill can
land in your Hermes install, including
one source that gets overlooked, which
is the agent itself.
So, this is where skills come from. And
the one we just saw was the bundled
skills. There's also official optional.
So, these are opt-in extras maintained
by the Hermes repo. So, you can trust
them more than you would just any random
skill.
There's skills.sh, which is Vercel's
public skill library.
And you can search that from the CLI.
There's GitHub taps, which is kind of
interesting. In version 4, they added
this huggingface/skills,
which is really useful. But, they have
default taps as well. OpenAI skills,
Anthropic skills,
a lot of the major providers. And the
huggingface skills is pretty big itself,
because the community skill index on
huggingface surfaces automatically in
your Hermes skill browse without any
kind of config. Um and you can your own
and you can add your own skill taps
uh with just Hermes skill skills tap
add.
There's also well-known marketplaces,
sites like uh
sites that publish well-known/skills
is a discoverable source. So, you have
claw hub,
uh lobe hub, claw marketplace.
Many of us, when we were first starting
out with open claw,
uh before we found Hermes, would use
claw hub. That was kind of one of the
first skill marketplaces. But, now
there's a ton of options out there.
And of course, you can just do a direct
URL or just drop the folder in, like I
said. These are all just directories.
So, if you have a skill directory, you
can just drop it into your Hermes. But,
obviously, you want to be very careful.
There's been a lot of concern, and
rightfully so, about, you know, a
injection and malicious skills. So, I
try to I try to be more conservative and
stick to the bundled and stuff that I
know comes from a reasonably official
source. If it's something that looks
interesting, but doesn't come from one
of these sources, I try to make actually
make the skill myself instead of just
dropping it in or try to trust something
that I'm not exactly 100% sure about.
So, the install pattern is the same for
every source. You do Hermes skill browse
and then you can install.
And there is a security scan that'll run
automatically, but then the skill will
be enabled and you have to do this
/reload skills, which does a hot reload
without having to restart your Hermes
agent. You can just do it while you're
still working there.
And of course, there's one more source.
The agent writes its own and this is
really a unique aspect of Hermes agent
and what really attracted people to it
when it was first released. So, the
agent writes skills, too.
So, you probably heard it, too, about
the kind of evolving nature of a Hermes
agent and it's really cool, but kind of
still underappreciated, I would say. So,
the agent can actually write skills and
this is super useful.
So, this is not as a separate mode that
you have to enable, not as a feature you
have to turn out on.
It's just how the agent works. So, you
can look here on the left side,
this how it works section.
So, the agent has a skill managed tool
and it can
it's just a tool that the agent can call
like web search or file write. And the
actions are create, patch, edit, or
delete. Um and a couple file management
actions for skills with multiple files.
So, after every turn, Hermes spawns a
background review fork and this got
substantially better in version 12.
Uh it's rubric graded and it's scoped
strictly to memory and skills tools. So,
it can't sprawl into spell shell access
or web.
And [snorts]
that inherits the parent's provider and
model, so it's not using some cheap
fallback. So, the fork reads the
trajectory of what just happened and
asks, "Was this reusable? Is there a
skill here?"
So, if yes, it writes a new skill.md
to the Hermes
uh {slash} skills file directory.
And as of version three, it gets marked
agent created,
which matters because the curator can
prune unpinned agent created skills more
aggressively than the ones you wrote
yourself.
So, the right panel here in purple is
when the
when this is triggered. So, when it
fires,
and the docs are pretty specific about
when it fires. So, complex tasks, five
or more tool calls completed
successfully,
recovery,
agent hits errors and figured out a
working path,
correction,
the user pushed back, and the agent
updated its approach,
uh or just a novel workflow it figured
out that's worth saving.
And this is key. The docs call this the
agent's procedural memory.
So, both skills that come from the hubs
we talked about or from the agent's
self-created skills, they both end up in
the Hermes {slash} skills folder
and are both managed by the curator, who
we're going to talk to talk about next.
So, if you've watched my videos, you've
seen my Hermes agent create a bunch of
different skills, but let's take a
closer look at some of them.
Um this is
the skill it created called Hermes
{dash}board plugin development. And if
you watched my video about me creating
Hermes dashboard plugins, this is the
skill it made.
You can see I didn't tell it to write
it. It just did it automatically as we
were building that project.
Um and this was for building a Hermes
web dashboard plugin.
You can see the description here, very
specific, build and verify Hermes web uh
dashboard plugins, including front end
tab bundles,
fast API plugin APIs, scripts, MCP back,
read-only data sources, and dashboard
smoke tests. So, this was in the
process, when to use, and
you can see it's fairly specific.
Uh
use this skill when building, reviewing,
or debugging a Hermes web dashboard
plugin.
So, it has all the instructions that you
would need.
Uh recommended workflows,
open-source release checklist. So, a lot
of this stuff
is very specific to that one
uh project.
But, if I were to build a new plugin, it
could use this skill
um when it's doing that.
It's really helpful cuz especially if
you're doing very similar tasks or
projects like this,
to actually go and learn all these
instructions,
um
to do it over and over again, it's just
going to take a ton of time and a ton of
tokens. If you're paying
per token, it's going to cost you a lot
of money.
But, having these skills already built
in,
um
just makes it a lot more efficient and a
lot quicker.
So, in part four, we're going to just
talk briefly on plugins.
There's some kind of confusion what
plugins are versus skills sometimes.
There's have been a lot of changes in
plugins recently as well, so I think
this will evolve over time.
But, plugins are just another way to
kind of level up your Hermes agent, give
it more capabilities.
So, there are three types and many
different backends that you can use. So,
plugin types
based on the docs, and like I said, this
can change, but there's general memory
providers, which we talked about in the
last video, and then context engines.
And these are the specialized backend
slots. Uh image gen, model providers,
platforms, video gen.
A lot of these were in the the config,
if you remember us setting up like what
my image gen was going to be.
So, skills are a separate subsystem.
Plugins can bundle them, but skills are
their own thing. So, I asked Hermes
itself, "What's the difference between
skills and plugins?" And there's some
crossover here,
but the short version is that skills
teach the agent how to do something.
Plugins add new software, UI, API
capabilities to Hermes itself.
So, just going back to what I said at
the beginning, a skill is mainly just
instructions.
So, here's the procedure, commands,
caveats, and verification steps. There
are some scripts and stuff involved,
like we saw earlier.
Uh but it's mainly at its core just
instructions, whereas a plugin is an
executable product surface.
So, here's new code that Hermes loads,
and it loads whatever it is, UI, backend
routes, other kind of integrations. So,
so there's a little bit more to it.
So, if it changes an agent's knowledge,
then make a skill. If it changes Hermes'
actual capabilities and interface, make
a plugin.
So, I hope that clarified. This has been
a question myself as well. I'll have a
good idea for a project or some kind of
tool for Hermes agent, and I won't know,
should this be a skill, should this be a
plugin, should it be something else
completely?
So, it's important to keep that kind of
distinction in mind.
Okay, so part five is the curator, and
this is a new
feature that landed in version 12 of
Hermes agent, and they enhanced it even
more in version 13. It's an autonomous
skill maintenance.
It the agent maintains its own skill
library on a schedule, and it's pretty
cool.
So, these are the things that it does.
It grades, prunes, and consolidates.
Uh you can see here,
it grades every skill in your library
against a rubric. It then prunes the
dead skills,
uh anything that hasn't been called
recently and isn't pinned.
And then it consolidates related skills
that have drifted towards duplicating
each other. Especially if you use your
Hermes agent a lot, it'll sometimes
create very similar skills.
So, this consolidate is really nice to
kind of merge those so you don't have
like a bunch of
custom skills that all kind of do
similar stuff.
So, the default uh frequency is a 7-day
cycle.
Um and this runs on the gateway's cron
ticker.
So, per run reports lambs in the uh logs
{slash} curator.
And it's configured under
auxiliary.curator
in the configuration file. So, it's the
same way you do configure any auxiliary
slot. You can pick a model in the Hermes
model
uh for the curator.
And the version three additions were
that it made uh the manual run
synchronous,
which matters because before that if you
ran Hermes curator run, you'd wait for
the next tick to see the results.
So, now Hermes curator run returns when
it's done. Plus, the operator uh
subcommands archive, prune, list
archive, status, pin.
You can drive everything from the
command line. So, they really upgraded
it in the 13 version.
Uh so, look over here in the green box,
you can see pin what you care about, and
this is important.
Um it's a important for safety. Bundled
skills and hub installed skills are
gated, so the curator can't touch them.
And that's kind of a defense mechanism.
Custom skills, including the one the
agent writes itself, can be pinned with
Hermes curator pin.
And this will lock them away from any
kind of modification by the curator.
If it's something important you don't
want the curator to touch,
uh you can just pin it there.
And then it'll be just ignored or left
alone by the curator.
If you do Hermes curator status, you can
kind of see
what it's done.
Um I've only had two runs on this
cuz I don't usually have this agent
running 24/7.
But here you can actually see a summary
of what changed.
Um my Hermes didn't change anything, but
you can see what it's done.
So, that's all about the curator and the
other skills in Hermes agent. So, in the
last part here, we're going to actually
try to build a skill.
So, the skill's going to be called unit
lookup and it's going to consume the
HVAC vault we built in the previous
module.
This is going to be the spec we're
working on.
The name is going to be unit lookup. The
inputs are going to be the model number,
uh contractor name, contractor quoted
price.
It's going to search the Obsidian vault.
If it's not found in the vault,
we're going to use web lookup specs,
writes a new vault node, image search
for the unit photo,
and compose markdown cards with specs,
brand notes,
price, image, and the output is going to
be the markdown card.
And this is going to be important cuz
this is going to be part of the enhanced
quote
itself. So, this skill, cuz we're going
to be doing this
task over and over again,
having this as a skill will be really
useful.
So, this is the actual written out spec
file. So, this is what I'm going to
prompt it. So, you can see the whole
thing. It's kind of long.
I'm just saying it to create a new
skill.
It's going to be under the business
category, unit lookup for the HVAC unit
research, and it's going to take in,
like I said, these general things, and
this is the procedure
based on the vaults.
Uh so, this is just the quote
based on the spec that I just showed
you.
So, there it is.
I put in the prompt, so now Hermes is
going to work on creating the skill.
You can see it's actually using a skill
to create the skill, Hermes agent skill
authoring,
which is another another skill it has.
Okay, so it's done. You can see it
created the skill.
And this is what it looks like, an
actual skill MD
format. You see name, unit lookup,
description,
use when the user provides an HVAC unit
model number, contractor name, and
quoted install price, and wants a strict
markdown quote card
uh with the unit specs, etc.
So, this is the full scale. You see also
has a one to use
section.
And the procedure, the instructions. So,
let's actually try to use this
and see how well it works. This also has
a pitfalls section like a lot of the
skills do.
There we go. So, let's try it out. So,
I'm just going to give it the prompt,
"Please check the model carrier this
number
and create a unit card for it." So,
let's see how well
the skill you is
to do this.
And you can see right away use the skill
business {slash} unit lookup, which is
the one we just created.
Also using the skill Obsidian.
And that's for the Obsidian, the
knowledge base that we created in the
last episode.
Okay, so this model wasn't in the the
vault.
So, it created it. It did the research
it needed to do and created the data and
actually put it into the vault so that
we can reuse it. It also created this
kind of markdown card file
that has all the information about this
specific unit.
Here's the card itself.
Here's a better look at it. Um so, this
has all the data
about the brand, SEER, tonnage,
technology,
brand notes, and everything
uh that you would want to see from it
with the sources as well.
So, the idea would be to process a bunch
of these different models basically that
fit anything
that the company I'm working with
carries and then automatically create
these cards that have all the
information and data
so that you can create those kind of
enhanced quotes.
So, this would be a really useful,
reusable skill for this kind of business
idea.
And you can see if I want to make sure
that the curator doesn't touch this, I
just do Hermes
curator
in
and then feed category business {slash}
unit lookup.
Curator responds pinned, the skill will
bypass auto transitions. So, I can make
sure that this skill is not touched. So,
two quick notes before we wrap up here.
So, something about the scope is that um
skill can be limited by platform,
by the operating system, so it'll hide
the skill on incompatible operating
systems.
Another thing, you can enable disable
each skill per CLI, Telegram, Discord,
etc. So, say you don't want to use any
of the heavy machine learning skills in
Telegram, uh you can make that specific
uh to just the CLI, and you could just
do that through Hermes skill, the
interactive to UI.
And other thing, uh agentskills.io,
Hermes skill MD format is compatible
with this standard, and the readme
states this explicitly, and the skill
tool code calls it out.
So, the unit lookup skill that we just
created, the same file can run in Claude
code or Cursor, Code X, other agents on
that standard. So, your skills are kind
of a portable IP. If you build a really
great workflow in Hermes agent, and you
switch agents or want to try it out in a
different type of agent harness, your
skill can go with you, and that's really
helpful.
So, that's going to be my module on
skills. Um very important part of any
agent, and Hermes agent has a lot of
really cool and unique features around
skills that I hopefully explained well
enough. Uh we talked about what a skill
MD file is. We looked at some of the
bundled skills, as well as some of the
optional ones. Took a quick look at
plugins.
Uh talked about
custom skills that your Hermes agent
will make automatically.
Talked about the curator, and also we
created our own skill here that we're
going to keep using in future videos.
So, this has been the module on skills,
and for module five it's going to be
models and providers.
Until now we've been running on whatever
the main model I set up back in module
one.
So module five is going to take that
apart. We're going to really look into
the 20 plus providers smart routing for
cost tiered work, fallback chains,
and plus a lot of the big stuff that
came in the most recent version. Super
Grok OAuth with 1 million token context
for Grok 1.3 and
the OpenAI compatible local proxy that
turns your Claude Pro or Claude or
ChatGPT Pro subscription into an
endpoint for Codex
to hit. Plus we're going to quickly
touch on the auxiliary models as well
for anyone who didn't see my dedicated
video on that. So a lot of interesting
elements and features around models and
providers we're going to talk about in
the next episode.
So I hope you enjoyed this module on
skills.
If you're watching this on YouTube,
please subscribe, leave a like,
leave a comment,
and I'll see you in module five of my
Hermes agent masterclass.