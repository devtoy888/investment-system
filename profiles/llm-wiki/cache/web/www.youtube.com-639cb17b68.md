![Thumbnail (1920x1080)](https://i.ytimg.com/vi/_6DtQkDpcEs/maxresdefault.jpg)
# [Hermes Agent Masterclass: 8. Subagents & Delegation](https://www.youtube.com/watch?v=_6DtQkDpcEs)

**Visibility**: Public
**Uploaded by**: [Tonbi's AI Garage](https://www.youtube.com/@TonbisAIGarage)
**Uploaded at**: 2026-06-26
**Published at**: 
**Length**: 33:27
**Views**: 4575
**Likes**: 164
**Category**: Science & Technology

## Description

```
Module 8 of the Hermes Agent Masterclass: instead of one agent grinding through everything in series, spawn a tree of sub-agents that work in parallel — on cheaper models — and hand back just the answer.

Sign up for my FREE weekly newsletter, where I spill my unfiltered thoughts on the latest AI news, cool research, and projects I'm building: https://www.onchainaigarage.com/

🐦 Follow Tonbi on X for real-time AI x blockchain updates! https://x.com/tonbistudio

If Cron is one agent stretched across time, this module is the other axis: many agents running at once. I cover why delegation matters (it fixes context poisoning and serial slowness by giving each child a clean isolated context and running them in parallel), the delegate_task tool and the "subagents know nothing" rule that trips everyone up, and how to scope each child's tools tightly. The big practical win is cheap children, strong parent — routing the token-heavy grunt work to a cheaper model while the parent keeps a strong one for orchestration and synthesis, which I measure live in a solo-vs-sub-agents cost comparison. I also dig into control (delegation depth, orchestrator roles, and the new background=true flag for async) and, importantly, when NOT to delegate. It all builds to a three-level research tree — fanning out to 3 orchestrators and 9 workers, then synthesizing it all back into one report.

Resources:
🔗 Hermes Agent: https://github.com/NousResearch/hermes-agent

Timestamps:
0:00 - Module 8: sub-agents and delegation
2:21 - Why delegate: context poisoning + serial slowness
3:42 - The delegate_task tool + a live demo
9:07 - "Sub-agents know nothing" + scoping tools
11:12 - Cheap children, strong parent (cost saving)
13:30 - Parallelization: batch mode + concurrency
15:02 - Demo: solo vs sub-agents (cost comparison)
20:47 - Control: depth, orchestrators, sync vs async
25:44 - The 3-level research tree, live

What would you fan out across a fleet of sub-agents? Let me know in the comments. Module 9 is on profiles and the Kanban board — many isolated Hermes instances collaborating on durable work. Subscribe and hit the bell so you don't miss it! 🦐✨

#HermesAgent #SubAgents #MultiAgent #AIAgents #AgenticWorkflows #Delegation #AITools #Automation #Masterclass
```

## Transcript

Welcome back to Hermes' Agent
Masterclass, module eight, sub-agents
and delegation.
Getting towards the end of this series,
but we're getting to some real deep,
complicated topics that I think will
really unlock a lot of great features of
Hermes' Agent.
So, in the last module we talked about
Cron and automation. And Cron is just
one agent running on a clock, work
stretched across time.
This module is the other axis, many
agents running at once,
work fanned out across workers.
So, by the end you'll have a parent
agent that spawns a three-level tree of
researchers, runs nine of them in
parallel, and synthesizes it all back
into one clean answer.
So, here's the why. A single agent loop
has two hard limits.
One, its context window fills up with
intermediate junk, every tool call,
every retry, every dead end from a long
subtask, all sitting in the window,
degrading quality.
And two,
it does everything in a series.
10 researchers take 10 times as long.
So, delegation fixes all of this.
You spin up a child
with a clean, isolated context. It works
in parallel and hands it back only the
summary.
So, the parent agent never sees all the
mess and work that went on underneath.
So, this is going to be our roadmap
and the keyword here is going to be
delegation. Delegate
and the specific delegate task tool and
the one rule that trips up everyone.
Then we're going to talk about
parallelization
using batch concurrency and the agents
monitor.
We're going to discuss control cuz
there's a lot of ways you can control
and customize your delegation tasks and
sub-agents in Hermes' Agent using depth,
sync versus async, and when not to use
sub-agents at all.
And lastly, we're going to do a
three-level research tree
for a real research task
all on video.
So, let's get started.
And if you like this video, please
consider supporting the channel by
joining Team Garage,
which will give you early access to
videos,
or Team Garage Max, where you will get
exclusive videos each week, as well as
many other perks.
I'd like to continue providing as much
free valuable content as possible, as
well as better experiments on different
hardware. So, these memberships will
really make it possible.
So, part one, why delegate to begin
with? So, there's two problems and one
tool to address them.
And having this mental model makes
everything else obvious.
So, here are the two problems, and
anyone who who's been using agents for a
long time has encountered these.
On the left here in the red, context
poisoning.
So, picture a real subtask, debug a
failing test suite, refactor 30 files,
run deep research across a dozen
sources.
If you do that in the main loop, every
single bit of that, the tool output, the
false starts, it all lands in the
parent's context window and stays there.
The window fills, and the model gets
worse as it fills.
I imagine we've all had the experience
of
a model working great when we start out
on a task, but as that context window
fills, it starts to make mistakes, maybe
even starts to hallucinate.
So, context window management is very
important.
And the other issue is serial slowness.
And
for this, if you're researching 10
things
one at a time,
it's obviously going to be 10 times the
wall clock,
cuz a single loop can only do one thing
at a time.
So, delegation fixes both of these
issues at once. You get clean, isolated
contexts, and you have them running in
parallel.
That's kind of the whole purpose and
pitch behind sub agents.
So, you may be asking, what is a sub
agent? A sub agent is just a fresh agent
your agent hands a brief to and gets a
report back from.
So, the parent, which is your main agent
that you're working with, the one you're
chatting with in the TUI or in whatever
messaging platform you're using.
This parent agent will delegate a brief.
And the brief is just a goal plus a
context.
Go into that a little bit more later.
But then the child, which is the sub
agent, is a fresh agent, a brand new
agent instance. It has its own
conversation, its own terminal session,
scoped tool set, its own iteration
budget. It works alone in that clean
room and runs to completion.
And only its final summary returns to
the parent.
So, intermediate reasoning, tool calls,
retries, none of that actually enters
the parent's context. That's not a side
effect, that's the whole point. The
whole
advantage of using the sub agent
process.
The parent stays small and fast no
matter how messy the child's work was.
So, think of it like a manager and a
worker. You hand off a brief, you get a
report back. You're not sitting in the
room watching every keystroke.
So, how do you actually hand off that
brief?
That brings us to part two, delegation,
and specifically the delegate task tool.
So, as I said, the the key tool here is
called delegate task.
And in its simplest form, it takes goal,
context, and then tool sets.
So, this will spawn a child sub agent,
and it'll have the goal,
you know, in this case, debug why off
test fail,
context, which is very important.
It has to be the actual command, the
actual error, the file online, the
project root, the stack,
all the details that are needed to
actually perform
uh the task and achieve the goal,
and then the tool sets, which are scoped
uh just for the purpose of that one sub
agent.
This child will run isolation and return
a structured summary.
What it did, what it found, and what
changed.
So, in practice, the agent often decides
to delegate on its own
uh when task is big and parallelizable.
You don't necessarily have to call out
this by hand,
but knowing the shape of it is important
because then you can control what it's
really doing.
I'm in Hermes agent, you can see right
here.
Um and I'm telling it to delegate sub
agents
to check the quants used for all quant
models
uh tested in this experiment.
So, this will give us uh just a quick
look of how sub agents work.
And you'll often find it using this
skill autonomous coding agents,
uh which is a skill that Hermes often
uses for
uh sub agents.
You can see um
it delegated three of them to check the
experiments.
And three is the default, so that's the
tool call right there delegate task.
So, we'll be able to see how they work
if you do {slash} agents here.
You can see background delegations one
running,
and this will
see three parallel sub agents here.
And the main agent is idle cuz we're
just having the sub agents work right
now.
And you can see even as the sub agents
are working
down here, this is the the context
window. It's not filling up because
the the parent who I'm talking to right
here,
their context window is staying clean
and not filling up with whatever work
the parallel sub agents are are working
on right now. You can also see in the
uh desktop app,
they have a nice visualization here that
you can actually see see the sub agents
working.
So, these are the same three
um that were working.
You see they're analyzing for the quant
family model quants.
Um but this is a nice nice way to
visualize it as well in the desktop app.
And you you can see
if you click this, you can see it as
well. It's kind of like a smaller
version.
You can see that they're working what
they're doing, read file, searching
files.
Okay, so the sub agents finished and we
could see
these are the models tested. It shows us
all the the quants used for the
uh quant family.
Uh mostly Q4, which makes sense.
And there you go, much faster work done
with those sub agents rather than doing
this one at a time
uh just with my main agent.
And you could see I asked it to send the
exact summaries that each sub agent sent
to the parent and you could see this is
exactly what it sent. So this is sub
agent one saying it inspected
these files, these directories. Uh this
is what it found.
And that was it. No task blocking issue.
So that's the whole summary.
It's basically just this data, right?
There's no
uh longer strings of tool sets used or
any kind of errors or any other issues,
just this summary. You can see sub agent
two, same thing. It says exactly what it
sent.
It says exactly what task it ran and
what it found for all the data. Sub
agent three did the same thing
and found different
uh models and then sent the summary. So
this is the three different summaries
that the sub agents sent to my main
agent
in order to uh which it synthesized and
then ended up with this one.
So there you go.
So key thing to understand here is that
sub agents know nothing.
And this is the number one delegation
mistake.
And it follows straight from isolate to
context. So a bad example of a task is
just like goal equals fix the error.
So the child has a brand new context, no
parent history. The error, it has no
idea. So a good type of goal for a sub
agent is very specific. You know, fix
the type error in API handlers.py
line 47.
So that has the full stack, the cause,
the project root, the Python version,
everything it needs just in one call.
The sub-agent is just a stranger that
you brief once. If it's not in goal or
it's it's not in context, um it doesn't
exist.
So, if you watch module 7, kind of the
same discipline as the cron prompt, cuz
it's a fresh session, there's no memory,
so you have to write it all down.
So, there's the two things you can
control here,
what the child can reach and what it's
forbidden from.
You can see the different tool set
patterns here.
You want to try to give it the least
amount of tools as possible for whatever
task you're giving it.
Fewer tools means less context to use.
It also just means less possibility for
it to do something it shouldn't be
doing.
So, for code work, debugging, edits,
builds, you're going to need at least
terminal and then file.
For research, fact-checking, and doc
lookups, you're going to need web.
And for read-only analysis review with
no execution, you only need file. You
don't need terminal use.
And the child can never exceed the
parent's surface, so the tool sets the
so the tool sets intersect.
And blocked relief children, there's a
This is a kind of a hard block list for
the leaf children by default.
Delegation, clarify, memory, send
message, code execution. So, there's no
recursion by default. There's no asking
the user, no writing a shared memory, no
firing off a Telegram message, no
sandbox escape.
So, if the subtask needs any of those,
you do it in the parent. So, people hit
this and get confused, so it's important
to to note this.
So, another great reason to use
sub-agents is this cheap children,
strong parent. And this is cost-saving,
which is always a a big topic for us,
right?
You can route every child, every
sub-agent through a different and
cheaper model.
So, there's a couple ways you can do
this. You can do this directly in the
config, uh but recently, you can also do
this in the dashboard, which is probably
easier for most.
If you go to your Hermes Agent dashboard
here, go down to config, you could see
all the different sessions, but if you
go to delegation, this is where the sub
agent stuff lives, and you could see I
don't have anything set right now, but
you can set the model and the provider.
So, you could see my default model is
going to be the GLM 5.2, and I'm using
new portal. Um and they show you all the
prices here if you do Hermes models.
So, 5.2 is still pretty cheap, right?
0.95, 95 cents
uh for input. But, say I want to do
something even cheaper for the sub
agents,
uh let's try the Nemotron 3. That's even
cheaper, only 9 cents.
So, I'm going to use that cheaper model
as the the sub agent.
For this, you don't have to go down to
config.
Uh you can see my general is this one,
the new
uh new portal GLM 5.2. Go down to
delegation.
And it's actually for new, it's just
new.
Or Neus.
Keep getting different
comments saying it's pronounced one way
or the other.
And then for model, I could just do
this, Nvidia Nemotron 3.
Super. So, this
will make sure all of the child sub
agents are using this Nemotron 3 cheaper
model.
So, you can set this up so that the
children do token heavy grunt work on a
cheaper model. Um and then parents keep
a stronger model, which might be a
little bit more expensive, for
orchestration and then synthesis.
So, the expensive context will stay
tiny, and you don't have all of that
work, research work, or whatever work is
being done by the sub agents costing you
a lot uh with the more expensive model.
And the important thing here is that
it's one delegation model for the whole
child fleet. So, there's no like per
task model differentiation
when it comes to sub agents.
Uh then you're for that, you're going to
need to get into like the Kanban and
then profiles, which will be in the next
video.
So, part three is about parallelization.
Try to listen for how many times I
butcher that word.
Uh but this is talking about uh batch
mode concurrency and one screen to watch
the whole fan out. So, we just saw this
with uh my example
uh doing the research on those quan
uh quan model quants. But, you can set
uh a list list of tasks
and you pass them as an array
in delegate task. This happens under the
hood. You don't need to do this
manually. Just to show you have a mental
model what actually is happening when
you ask your your agent to do this.
So, you have three research ta- each
with its own goal and tool set and they
run in parallel through a thread pool.
So, the results come back sorted by
input index, so the order is stable. And
if you interrupt the parent or send a
new message, all the children are
canceled as well.
And the default concurrency is three.
Three sub agents.
And a batch bigger than the limit
errors. It doesn't queue or drop tasks.
So, you need to raise the limit or batch
smaller.
So, the cost win here is pretty
significant. Reinforcement of why this
is the cheap way to do big work.
Nine research children doing the to-
token heavy work on a cheap model that's
only going to cost you cents. The parent
on the strong model only sees the nine
summaries and that's small. So, net 80%
of the token volume runs cheap
and the strong model touches a thin
slice. So, you have
them working in parallel and also very
cheap. So, let me show a little bit of a
demo here.
I'm going to have a research task that
has three different branches.
In the first one, I'm just going to have
the main parent agent
uh do the whole research task
top to bottom. And then in the
comparison, I'm going to have it use sub
agents on a cheaper model. And like I
said, I'm going to keep the parent as
the GLM model and the sub agents as the
cheaper Nematron and we'll see the
difference in the cost.
Okay, so first we're going to have the
main agent do this and you can see we're
using GLM 5.2.
And we're going to say conduct research
on advanced stats and ML tech-
techniques for soccer.
Sorry, I'm American. I'll call I'll call
it soccer.
Uh research three topics. What data
exists for major soccer leagues? What
advanced statistics exist and what
existing use cases of machine learning
techniques exist for soccer data? Do not
use sub agents for this task. You must
conduct all the research yourself.
Produce a summary of findings at the
end. So I'm telling it not to use sub
agents cuz I want the comparison. So
this is the research task. It's all
going to be done by the main agent. And
I'm going to track how much it cost
as well as how long it takes.
And then we're going to do basically the
same prompt except using sub agents and
doing a different sport.
Okay, the task is complete. It took a
little over 9 minutes.
And we can see
this is the report it gave me. Quite
comprehensive actually.
Uh not not surprising. GLM 5.2 is a
excellent model.
Uh so it had really good
reporting here.
So that is the the report. We got
everything. Advanced statistics and ML
techniques from soccer.
And has the full report. So yeah, great
report. But the stats we're interested
right now are 9 minutes, little over 9
minutes it took. And we can see the
spend here.
This is all the work he was doing with
the GLM 5.2
and it cost us
around 66 cents.
Around 66 cents. So we're going to do
the same task and see if we can do it
faster and for cheaper than we did with
this.
Okay, so I started a new session
and I gave it the same task
uh
except I said please use sub agents for
this task.
So, we're going to be using the
subagents, which like I said
has the um
the Nemotron, the cheaper one.
Instead of the GLM, it's close to 10
times cheaper, so
curious to see the difference in cost
and certainly in terms of time. You can
see it's preparing delegate task tool
here.
And we should be able to see them
working
uh once they begin.
Okay, so the three subagents are now
running in parallel.
See agents. We should be able to see
what they're doing. Yep, you can see
them running now.
Um and these are the different topics.
It broke it up into these three
different
areas.
So, we should be able to see um their
progress through this {slash} agent
agents command.
Okay, you can see one has completed its
task.
And the two others are still running.
And you can see here in the portal
you can see the Nemotron starting to
show up.
Very small amount so far, but
should start coming in.
Okay, so the subagents finished their
work and we got back our very
comprehensive report here
about uh soccer and machine learning
techniques.
You can see it has all the data sources,
advanced soccer statistics, everything
that we had in the previous summary as
well. Looks just as comprehensive if not
more so.
Our previous uses as well, so very
comprehensive.
Um in terms of quality of the research
and report, I think it did good. The
Nemotron's a pretty good model for
research.
And you can see the actual time it spent
um it was around 10 minutes roughly,
maybe a little bit less. So, I think
yeah, the work it did was
around 9 minutes as well. So, time-wise
it wasn't a big difference between this
and the just the main agent running it
all. I think that would change if you're
doing a lot more research. We were only
using three agents, three sub-agents
here. If you had a a larger, it's
obviously going to scale cuz if you're
having,
you know, 6, 9, 12, 100 different
sub-agents running,
that that's where you're really going to
see the advantage of parallelism.
Uh but for this one, we can definitely
see the difference in cost. So, this was
just the period when it was the
sub-agents were running it and you can
kind of see by the usage
how it worked cuz in here you could see
the Nemotron
being used and then
this green is the GLM, so that's when
the the main agent was receiving the
report
or the summary from the sub-agent.
And you could see the final one over
here.
So, the total cost of this ended up
being 13 cents.
So, yeah, around five times cheaper
just using this setup and we got the
same quality of a report in the same
amount of time, basically.
So, I hope you can see how using this
kind of setup with cheaper models
in the sub-agent doing the grunt work
and then paying for the strong model
only for judgment and synthesizing all
the information that it receives, as
well as running orchestration.
And in this little example right here,
we saw a a cost savings of five times
that we had without using sub-agents.
So, pretty significant.
The part four is about control,
um depth, durability, and knowing when
not to use delegation.
So, the key thing here is that depth is
an opt-in
by default.
Sub-agents are going to run in a flat
tree.
A parent at depth zero spawns the
children at depth one, and the children
cannot delegate any further than that.
So, this is the default setting, max
spawn depth is one.
And that's deliberate. It stops runaway
recursive delegation
that would waste you a lot of time and a
lot of tokens.
Now, perhaps for your workflow, you want
to go deeper though.
And there is way to do that.
You can do role equals orchestrator. You
can spawn a child with this
uh which lets the child delegate its own
workers.
But you need to raise uh max spawn depth
to at least two
or three plus if you want to really go
deeper.
Uh there's also kill switch orchestrator
enabled equals false.
And this forces every child back to a
leap globally.
So, you really want to be careful and
intentional here. At depth three with
three concurrent children per level,
you can reach three times three times
three.
So, 27 concurrent leaves, concurrent
uh subagents basically.
And each level multiplies the spend. So,
you want to raise depth intentionally,
only when you really need it.
So, there's two execution modes and the
distinction really matters. By default,
delegate task is synchronous.
And it runs inside the parent's turn and
blocks until the child is finished.
And it's not durable. If you interrupt
the parent, the children are canceled
and their work is discarded. However, in
the most recent update uh from last
week,
you can set delegate task background
true and this returns a handle now.
So, the child runs in the background and
outlives the current turn
and its result reenters the conversation
as the new turn when it finishes.
So, the whole API here for async is just
this one flag, background true.
There's no separate async or checker
collect tools, so
keep that in mind. And background
subagents are single session, so they
die when the session ends. They're not
cron durable.
For work that has to survive the session
or run on a schedule, that's where
you're going to want to use cron job or
terminal in the background, which is
what we covered in the previous module.
So, the great thing about Hermes agent
is how customizable it is and how many
different tools it has.
And it's fun to play around, but we can
sometimes overdo it, as I know I I have
tendency to do that.
You really want to pick the right skill
for the job that you're giving it.
So, single loop, this is for sequential
dependent steps, which needs memory,
clarify, send message.
This is when the steps are sequential
and really depend on each other.
So,
this works well for under around 50
turns, and this is really what most of
us will probably using day-to-day.
Delegate task is for independent
subtasks that need reasoning, isolated
long traces, parallel fanout, and cheap
model grunt work.
Cron job, which must be durable,
outlive the turn or run on a schedule,
which we talked about in the previous
uh video.
There's also execute code, which is
mechanical, deterministic, multi-step
pipelines where no reasoning or LM
really is needed. So,
the skill isn't just put more agents on
the task, right? It's knowing when a
fresh child beats one more turn or when
a cron or a script beats both.
You may think, "Let me just throw a
thousand agents or subagents at a task."
But,
that's not always the best job. And in
fact, a lot of times, it's it's not.
It's going to create more problems than
it will fix.
So, one more quick contrast. Um for
delegate task, it is in process and
ephemeral.
Um summary only, and these children
sub agents will die if the parent is
interrupted. That's perfect for what you
just saw, like a fan out where you kick
it off and just watch it finish.
But the moment your work has crossed
agent boundaries and has to survive
restarts,
where a human might need to comment or
unblock something mid-flight,
you've kind of outgrown this and that's
when you want to reach for something
like the Kanban board.
A durable mini pro multi-profile board
where named agents collaborate on on
persistent tasks. So that's a whole
topic and that's going to be in our next
video, uh
module nine.
But for today, just know this line, when
work has to outlast a session, you
graduate from delegate task to something
like the board.
So lastly, I want to kind of show you a
leveled-up version of what I just showed
you as a demo, a three-level tree. So
deep research on machine learning in
sports.
Uh this time's going to be fanned three
ways and then nine and then synthesized
back up.
So here's the structure. I wanted to
show you this three-level.
So the parent model
is going to delegate this task. And the
task is to research these three
different sports, baseball, basketball,
and football.
And for each sport, look at data
sources, advanced stat, and past machine
learning uses, similar to the task we
just did with soccer.
So while these three are children sub
agents, right, of the parent,
um for each of the sports, they're also
orchestrators.
So they're going to accept the summaries
from these kind of grandchildren, I
suppose we'll call them,
grandchildren sub agents, and then
receive the summaries, synthesize them,
and then
give them to the parent who will also
synthesize them.
So this is what makes it nest cuz you
need to change the configs a little bit.
So we We to change max spawn depth to
two.
And then the sport children spawned with
role orchestrator.
Um the three questions fit the the
default max concurrent children three.
And we're going to keep our our same
delegation model as the Nemotron, the
cheaper model. We did a good job with
the soccer one.
And then max iterations 15
per leaf. So, we don't get too uh
two in the depths here.
So, we're here in the dashboard and you
can see once again I'm in the config at
delegation. The key thing that we're
going to need to change here is max
spawn depth.
And this is by default one, but we're
going to change it to two.
Uh orchestrator enabled um was already
enabled. You can
disable or enable it there.
Um and that should be that should be it.
I'm going to move max iterations down to
15
um because we want to try to keep
focused with this.
Uh so, for this one I'm actually going
to just go with the default
on the model cuz this is going to be a
heavy-duty
research task. Um
and I know the Nemotron model can
sometimes be overloaded. So, we're just
going to do our
our default model.
So, just save that configuration.
And for this one we're going to be using
uh GPT 5.5
uh with my Codex subscription, which is
kind of my main driver
uh day-to-day in Hermes.
So, this is the
uh prompt. Research the state of machine
learning in sports. Delegate one
orchestrator per sport,
baseball, basketball, football,
and have each orchestrator delegate
three research workers.
What data exists, what advanced stats
exist, and how machine learning has been
used. Each orchestrator synthesizes its
sport, then you synthesize all three
into one report.
So, we are
You see it's spanning
three sub agents. So, these are the
orchestrators.
Right? This one is for baseball, this
basketball, this one is for
American football. Nice uh specificity
there.
So, these are going to spawn from here.
So, you can see
the desktop app is really visual. So,
it's really it's nice cuz you can see
this one which was for baseball.
This was the child sub agent that's
going to be orchestrating this. And then
it delegated to these three grandchild
sub agents
that are going to be doing research here
for each of these topics.
And you can see each of these
going like this.
So, for complicated or advanced
tasks like this
um being able to work in the desktop app
and see everything working and see if
you run into any errors or
anything like that is really useful.
And you can see it even here. 12 sub
agents we got running.
The three
main orchestrator
that have delegated task and then the
nine
grandchild sub agents.
I'm using my subscription for this so it
doesn't show, but if you're using like
an API, it'll actually show how much
tokens and how much it will cost up
here.
Uh so, that's nice as well to have.
Okay. So, all the sub agents have
reported back and we get our final
summary here. State of machine learning
in sports, baseball, basketball,
and American football.
So, this is the full summary.
Uh it's quite extensive. I won't go
through all of this, but you can see
like the sub agents did a really good
job
um
for each
category.
I have all the data, very extensive
report here.
So, and towards the end it kind of did
like a cross sports synthesis.
So, that's the that's the report.
And to be honest, this was actually my
second time running this
because you could see here
this one category I forgot to set it's
by default it's only 600.
This is child timeout seconds.
So, this kind of sets a guardrail for it
not taking too long.
But because we had two layers of it and
the child and grandchild were running
um it went beyond the 60 seconds here.
So, I had to bump it up to 12
for the second run and that's what
actually worked.
So, that's it. That's the end of module
8. Um you now have uh
you now understand why we do delegation
uh isolated contexts and parallelism,
only the summary returns.
We learned about delegate task as a
tool, single and batch
and sub agents don't nothing rule. You
got to see
uh the actual cost impact of using a
slightly more expensive main model
orchestrator model and then having the
children sub agents being on a cheaper
model.
Uh we also got to see it live in the
desktop app which makes it very visual.
And we learned about, you know, setting
role as orchestrator, setting background
as true
um and you got to see this three-level
machine learning and sports research
tree built and synthesized fully live.
So, there's a lot of ways you can kind
of customize and
design these kind of sub agent trees
depending on your exact task. A lot of
the times you're not going to have to
specifically ask for your main agent to
do it, they'll just do it automatically.
But it's good to know cuz there's a lot
of different ways you can do this
to kind of save
money and tokens as well as
design more advanced workflows if that's
what you need.
So, that's it for module eight. We're
getting towards the end of this master
class series.
Next week, module nine is going to be on
profiles. So, today we ran many agents
in one session.
Next, we're going to run many isolated
Hermes instances, separate personas,
their own memory, their own skills,
their own gateways, and we're also going
to be talking about the Kanban board
that lets them collaborate on durable
work. So, this
really unlocks a lot of advanced
autonomous uh workflows.
So, I'll see you then.
Thank you for watching.