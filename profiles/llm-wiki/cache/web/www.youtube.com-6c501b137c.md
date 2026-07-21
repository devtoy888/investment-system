![Thumbnail (1920x1080)](https://i.ytimg.com/vi/grMNnzCv2gY/maxresdefault.jpg)
# [Hermes Agent Masterclass: 7. Cron & Automation](https://www.youtube.com/watch?v=grMNnzCv2gY)

**Visibility**: Public
**Uploaded by**: [Tonbi's AI Garage](https://www.youtube.com/@TonbisAIGarage)
**Uploaded at**: 2026-06-19
**Published at**: 
**Length**: 35:55
**Views**: 4418
**Likes**: 149
**Category**: Science & Technology

## Description

```
Module 7 of the Hermes Agent Masterclass: Cron cuts the last cord — your agent runs itself on a schedule, in a fresh session, and delivers to your phone. And I'll show you how to make it cost almost nothing.

Sign up for my FREE weekly newsletter, where I spill my unfiltered thoughts on the latest AI news, cool research, and projects I'm building: https://www.onchainaigarage.com/

🐦 Follow Tonbi on X for real-time AI x blockchain updates! https://x.com/tonbistudio

Module 7 is all about Cron and automation — running Hermes Agent on a schedule with no one in the loop. I cover how Cron actually works (it lives in the always-on gateway, which ticks every 60 seconds and spins up a fresh, isolated session per job), the four ways to schedule a job (CLI, chat, TUI, and the web dashboard with one-click blueprints), and how to deliver the result anywhere — or nowhere, using the "silent" keyword. The best part is the cost engineering: no_agent mode runs a pure script for $0, and the wake-agent gate polls cheaply every couple minutes and only pays for the model when state actually changes — which I demo live with a real bug-triage job on my Agent Wikis app. Finally I chain jobs into a real pipeline with context-from (no framework needed) and build a daily traffic briefing that collects data for free all day and only spends a cent on the part a human reads.

Resources:
🔗 Hermes Agent: https://github.com/NousResearch/hermes-agent
🔗 Agent Wikis (used in the live demos): https://agentwikis.com/

Timestamps:
0:00 - Module 7: cutting the last cord with Cron
2:19 - How Cron works: the gateway tick + fresh sessions
4:06 - The 4 ways to schedule a job
6:21 - Schedule formats + the no-self-spawn safety rail
9:10 - Deliver anywhere + the "silent" keyword
11:18 - The #1 Cron mistake: fresh sessions start from zero
12:39 - Spend nothing: no_agent mode (RAM watcher)
14:50 - The wake-agent gate (live bug-triage demo)
23:12 - More cost layers: rerun scripts, lean tool sets, resilience
25:30 - Chaining jobs with context-from (daily briefing build)

What would you point a Cron job at — a daily brief, a monitor, a whole pipeline? Let me know in the comments. Module 8 is on sub-agents and the Kanban board: running many agents at once. Subscribe and hit the bell so you don't miss it! 🦐✨

#HermesAgent #Cron #Automation #AIAgents #AgenticWorkflows #AITools #SelfHosted #LocalLLM #Masterclass
```

## Transcript

Welcome to module 7 of my Hermes Agent
Masterclass, and this one is going to be
on Cron and automation. Very big topic.
A lot of interest in automation.
And Hermes Agent makes it really easy,
and there's a lot of different options
for ways to create automations.
So, module 6 was everything Hermes can
do, right? The tool catalog, MCP, the
service you can scope and trust, but
every one of those things still needed
you in the loop.
You opened a chat, you typed, the agent
did the work. So, today we really cut
the last cord.
Cron lets Hermes run itself on a
schedule in a fresh session, and deliver
the result to your phone. So, this is
what we're going to go through today.
Uh we're going to talk about how Cron
actually runs, the gateways, the fresh
sessions, the schedule, four ways to
schedule,
and how to deliver anywhere,
spend nothing. There's a lot of really
interesting cost-saving
features inside Hermes Agent when it
comes to Cron jobs. So, we'll be
exploring those, and I'll be doing some
demos with them.
Uh and then chain using context from
to wire jobs into a pipeline.
So, this is for more simple agentic
workflows, but it does work very
smoothly.
And I'll also be demoing that.
And that'll be part of this uh build
we're going to be doing, a daily traffic
briefing delivered to Telegram. So,
hopefully by the end of this video, you
have a good understanding of what Cron
jobs are,
and the different ways you can use them
to customize your agentic workflows.
And most importantly, I'm going to try
to spend this whole video not
pronouncing Cron as Crone, which is
something I did in earlier videos,
and I got many comments correcting it.
Some reason my brain wants to just
pronounce that word Cron job.
Well, the correct pronunciation is Cron
job. So, please
wish me luck during this video, as
hopefully I get to the end without
mispronouncing it.
Let's get started.
And if you like this video, please
consider supporting the channel by
joining team garage,
which will give you early access to
videos,
or team garage max, where you will get
exclusive videos each week, as well as
many other perks.
I'd like to continue providing as much
free valuable content as possible, as
well as better experiments on different
hardware. So, these memberships will
really make it possible.
So, part one is how cron works, the
gateway tick, fresh isolated sessions,
and three ways to get a job in.
So, cron in Hermes is not a separate
program. It lives inside the gateway,
the same always-on process from module
two,
that keeps your agent reachable.
Once a minute, that gateway ticks the
scheduler.
So, you can see here, this is the flow.
Every 60 seconds, the gateway wakes,
checks each job's next run time,
and for anything that's due, it starts a
fresh agent session.
A clean room, no chat history, it runs
the prompt to completion,
uh delivers the final response
to whatever channel you've set it up as,
and then archives the output to a disk.
Then it goes back to sleep for another
minute.
So, the single most important thing in
this slide is this, that the gateway
must be running.
It's the heartbeat.
Like I said, in module two, I showed you
how to use gateway uh Hermes gateway
install to make it a service,
so that it survives reboots, and there's
a grace window that catches up a job
missed during a short restart. So,
roughly half the job's interval.
But, if the machine is off all night,
um the 9:00 a.m. the 9:00 a.m. job is
simply skipped.
So, for example here, I'm in uh
terminal. You can see I'm in WSL. I did
Hermes cron status.
And you can see the gateway is not
running, so cron jobs will not fire.
So, that's what you need
uh to know, just to confirm that.
Uh but you see, I started Hermes'
Gateway.
The Gateway started up and in a
different terminal
I did the same thing, Hermes' cron
status. There you go. The Gateway is
running. Uh, no active jobs on this
specific agent.
But let's change that. Let's add some
cron jobs.
So there's several different ways you
can uh, schedule cron jobs with your
agent.
One is simply through the CLI using
Hermes uh, cron create, list, pause,
resume, run, remove, and status like you
just saw. That's just a standalone
command. And that's really uh, useful
for scripts.
Two is probably the easiest, right? Is
just in the chat.
And this is quite simple. This is in
Telegram itself. This is with Bowls.
You may remember the winner of Agent
Royals uh, Agent Trenches Royale season
1.
And this is the agent and the Telegram
bot that I have connected to that WSL
Hermes.
So I can just very simply
So I simply say, "Can you create a cron
job checking Hugging Face papers for
interesting papers about agent harnesses
and delivering me a daily report
summarizing your findings at 10:00
a.m.?"
So this is obviously the easiest way you
can do it, right?
Just simply telling your agent uh, what
you want to do.
And there you go. Very quickly the cron
job is set up.
Um,
So that's just that's through the agent
actually. And then the chat version, let
me show you that.
You're just in the TUI here. You can do
cron
and you see manage schedule task.
There's several sub commands here. You
can list them, add them, create them,
edit, pause, resume.
So like let's just list.
And you can see the one that I just
added in the
in the chat itself.
So you could also create them directly
here by by doing this create.
And then you'd say whatever you want it
to do over here.
So there's actually a fourth way, which
is if you do Hermes dashboard, and then
you have the the web dashboard open.
Uh you can go to the side here to cron,
and then you can see the scheduled job
that we just did, right?
And then we can do you can even do
create here
uh to create a custom
cron job right from the dashboard.
And you can actually choose which
profile
the cron job is under, which is really
really useful.
Um you could have different cron jobs
with different like models and different
skill sets.
Um name it with the prompt is, you know,
say what do you want it to do. You can
schedule it however often you want to do
it, choose to deliver it locally,
uh or to Telegram, which is the one I
have set up right now.
And these are all optional skills you
can use. So pretty
uh useful.
So you can create it that way. They also
have blueprints right here, which are
really useful. Like these are a lot of
the jobs
that people often want, like morning
briefing, which is kind of like a
classic cron job that people use as an
example, um uh reminder, weekly review,
topic news digest, a lot of templates
here that just are easy. You can just
one click set these up.
Hydration and movement nudge.
Could all use that.
So those are actually the four ways uh
you can create cron jobs with Hermes
agent. Very They make it very easy, as
you can see.
And there is this safety rail that they
have in place. A cron run session cannot
create more cron jobs.
So Hermes disables the scheduling tool
inside a cron executions, and that's
deliberate. It stops the job from
spawning jobs that spawn jobs and ends
up, you know, in runaway loops. So
keep that in mind as you're doing this.
So quickly, obviously if you're just
doing it with natural language chatting,
you can just say, you know, the duration
or interval
um that you want it to to be.
I you saw me right there saying every
day at 9:00 a.m. I want my cron job
delivered, but you can do um duration.
So, you could say, I want it to fire
once
after 30 minutes or so. It's kind of put
that puts it on a timer, right?
Interval, which is
a recurring, you can see in the
dashboard as well under schedule it has
this interval.
You can select the interval every 30
minutes, every 60 minutes, whatever you
have.
They also have daily, weekly, and
monthly.
They have once.
And this is important. This is a like a
cron scheduler format.
And you can see it here in the dashboard
under custom cron expression.
And this is the five-field cron
expression.
And you're going to
use this if you're not using like a
natural language.
Uh you're going to want to try to use
this format. And the when you're
speaking to it like you just saw with
natural language, the LM just reformats
it into this format on its own.
Like if I look at this is the job I just
made, right?
You could see the schedule is based on
that same format. So, it kind of
translated what I said, which is
10:00 a.m. every morning
uh to that format.
Okay, part two about scheduling and
delivery.
Uh creating a job, you just saw a couple
of examples of that.
And we have that hugging face papers
cron job we just created.
So, now you can deliver it anywhere.
This is really flexible and can be
really powerful.
So, origin sends it back where the job
was created.
So, that's the default on messaging
platforms. If we look back at my job
here in the dashboard, you can see where
it is it delivered to origin.
Cuz I created it in Telegram.
So now Boles will deliver it back to me
in Telegram.
So local writes to files only.
That's the default when you do it on the
CLI.
You could also specify which messaging
platform you want to do if you want it
to be Telegram. If you want it to be a
specific chat in Telegram.
Like I have this Hermes HQ Telegram
group. I can have it specifically
um
deliver to one of these threads if I
just put in the chat ID.
And of course if I have the the group
enabled and on the allow list.
And you can also combine these if you
want it in multiple places. Say you want
to deliver it in Telegram and Discord.
You just use a comma.
And then this all uh just sends it to
every channel that you've had
configured.
And important to note that the agent's
final response is delivered
automatically.
You do not call send message in the cron
prompt for the main delivery.
In fact if you do, Hermes will dedupe it
automatically. So just write the answer,
the schedule will ship it to you.
And then this is a interesting feature
as well using silent. Say nothing when
there's nothing. So if you have the
response output uh
use this keyword silent
the delivery is suppressed.
So the cron job will still fire, just
won't deliver anything to the channels.
So this is used often with monitoring.
Here's a good example.
Um if everything's healthy, reply with
only silent, which means the job will
will not be delivered.
But if the job itself fails, um it's
going to deliver regardless of this
using silent.
So now the single most common cron
mistake and it follows straight from the
fresh session design.
You have to keep in mind that every run
starts from zero.
So a bad prompt, a bad cron job is
something ambiguous like check on that
server issue.
Perhaps you have been working on a
server issue in a previous session,
but this is a fresh session that has no
memory of what that is.
So, to this cron job, that server issue
just doesn't mean anything.
This is a good prompt, you know, SSH
into this IP as deploy, check NGINX with
systemctl status, verify
um you know, example.com returns 200.
So, that is everything it needs, very
specific instructions, and it's all in
the prompt. It doesn't require any kind
of knowledge of other sessions at all.
So, everyone starts from zero. The
prompt plus its attached skills are the
entire briefing. If the job needs more
context than that, you feed it
deliberately. And there are three tools
to do that.
You can use a pre-run script, a work
directory,
it opens a repo,
uh or using context from
that pipes in another job's output. And
I'm going to introduce all three of
these before the end.
And that will bring us to part three,
spend nothing. And this is kind of the
most interesting part to me, cuz I don't
like to spend a lot of money.
This is really a differentiator from
Hermes Agent.
Um
if you have a naive check every 5
minutes job, you're paying for the full
model turn every 5 minutes forever,
whether anything happened or didn't
happen.
So, Hermes gives you several ways to pay
zero until something actually does.
So, this is the bluntest lever, no agent
mode.
Cuz sometimes a scheduled job doesn't
need a language model at all.
It just needs a script, and the script
is the message.
In this cron job, the schedule will run
the script on a schedule, and deliver
its standard output verbatim.
So, this doesn't require any model, no
provider, no tokens, ever.
This is a In my example here, this is
for watching RAM.
Very simple script that just checks how
much RAM is available on your machine.
And you can see how it's created here
with every 5 minutes. It's going to use
no agent, which is the key tag here.
And then it's going to run this script,
which is the RAM watcher, and it's going
to deliver to Telegram.
And this is the script itself. Very
simple. If RAM memory is over 85%, then
you're going to echo a warning.
So, this is going to be delivered
verbatim, right? So, say if RAM is at
90% for some reason,
um then it's going to echo this exact
phrase, this warning, RAM at 90%
delivered to my Telegram.
So, empty output just means it's a
silent tick. A non-zero exit gets you
an error alert.
So, a a broken watchdog can't fail
quietly.
So, this is very useful for
tasks like this that don't really
require an LLM. It just requires a very
simple script where the input and the
output are deterministic.
So, you want to use no agent uh when the
message is fully determined by the
script, right? Heartbeats, disk and
memory alerts, CI pings, you know, is
the service working? The script already
knows the exact text to send. There's
nothing for the model to think about.
So, you shouldn't be paying for that.
So, the next example, example two, is
the $0 gate.
And I'm going to show you a real demo of
this, of setting this up.
Uh but let me first explain what it is.
So, in this case, you do want the
model's reasoning, but only when there's
something to reason about. So, that's
the weak agent gate, and it's the
technique that I think can be really
useful for a lot of people.
So, similar to no agent, it's going to
be uh using a script.
And the script runs every tick cheaply
with no model. It just checks some kind
of state.
And if nothing changed, it prints wake
agent false
and the agent is skipped, cost you
nothing.
But if something did change and you do
need the agent, um it'll print wake
agent true
plus a a context blob and the agent will
wake up already knowing what's changed.
So, this is the thing to keep in mind,
right? The script runs constantly and
costs nothing to run alone.
The agent runs rarely and does the
expensive reasoning.
So, you can pull for every 2 minutes for
free and then you only pay for the model
the moment state actually moves.
So, the three common um
gates for this are if a certain file
changed, if an external flag got
dropped,
or a count in your database went up.
So, let me show you this as a real demo
and this is real. I'm going to be
setting this up right now. This is my
app agent wikis for my knowledge bases.
Here's the Hermes agent knowledge base,
uh which ironically I used
to create this video.
Uh but you can see up here I have remor
uh report a mistake.
And this is just a simple report. You
click on it and you can just report what
is wrong in whatever page you're looking
at
um because I'm still working on the the
knowledge bases
and the the workflows, so there could be
some issues with it.
And this allows the users to to tell me
when there's a problem.
So, they just put in the message, um
they put in their email if they want to,
and then just send the report. And what
[snorts] this does is it sends it to a
log that I have
on the VPS where I run this app, and I
also have a Hermes agent there.
Okay, so first things first, I created
the the bug watch
Python script. And this is the main
script the cron job's going to be
calling.
Um I had it originally written out for
Windows.
Um so, I had the agent this VPS is on a
Linux
machine.
Um, on the operating system. So, it had
to change a few things.
But, it created this Python script. So,
now we're going to create the And the
the script itself just basically checks
the log to see if there's any new
entries and
um, you could see
um, the output because there's nothing
in that uh report right now.
The the output was wake agent false.
So, now that the script is done,
uh, I need to make the cron job.
Okay, so the prompt for this, I'm going
to just do this in the chat. You can
also do this from the CLI, it might be
easier.
And you want to be very specific with
it, um, cuz this cron job
uh, requires certain things. So, this is
going to be the prompt I'm giving it
right now. Schedule a recurring cron job
for me. Don't run it now, just create
it. Name bug triage. Schedule every 2
minutes. Pre-run script bugwatch.py,
which we already did.
Um, it already exists in the scripts
directory.
Um, the work directory
uh, enable these tool sets, deliver to
Telegram.
And the job's prompt exactly
uh, a new bug or factual error report
was submitted on agent wikis.
Details are in the script context. And
this is the pre-run script, right?
This is in the case where we get a new
entry and it's going to give you that
context back.
And verify whether it's a genuine bug or
factual error, investigate the repo,
and research the web if it's a factual
claim.
Uh, if it's real, send me a short triage
report plus a proposed fix plan.
Do not change any code. If it does not
hold up, reply only with silent.
So, this is going to be the case where
if somebody
uh, submits a a mistake, but it actually
doesn't hold up
to the agent's investigation,
um,
using silent here means that it just
won't deliver this report to me
because it won't be anything that
actually needs to be fixed.
But just for this test, um I'm going to
change this to
uh new bug not verified.
Uh just for this demo so you can see uh
see the report come through Telegram.
So, I will give that right in the chat
here with Hermes.
Okay. There you go. Created the
recurring
cron job for me. This is what it is.
And we can see double-checking here in
the Telegram.
Asking Admiral, what are your current
cron jobs?
And you can see he has the bug triage
one.
So, now it's going to pull every 2
minutes and
because there's nothing in the report
right now, and hopefully we don't get
any
natural ones in the next couple minutes,
you'll be able to see that nothing gets
printed to the Telegram.
Uh nothing gets printed to the TUI.
But then I'm going to actually report a
mistake, and we're going to see see this
in action.
Okay. I went to get a coffee. Couple
minutes have passed, so I asked it how
Can you check how many times this job
has fired and the output?
Uh my agent responded, it fired two
times.
Um it's only been Yeah, like 5 minutes.
So,
it did record the output here.
The script gate returned wake agent
false, so the agent was skipped
and both times.
So,
it's only run the um
the bug watch.py gate found no reports
and skipped waking the agent both times.
So, this all cost me zero.
As the agent was never woken up.
And it's really good. Um obviously, you
can run this. I'm running this every 2
minutes. So,
it allows you to monitor that frequently
instead of like a cron job where if
you're if you're using uh LM calls every
2 minutes, you're quickly going to run
into cost issues.
Uh but let's let's actually fire it. Let
it Let it actually work and see what we
got.
Okay. So, this isn't a mistake, but um
Hermes
A is in just
announced an integration
with the official
Unreal Engine MCP.
Not a mistake, but information that is
not in it cuz it literally just got
announced. So, I'm going to send that
report.
Thanks for the report.
You're welcome.
You can see after a couple minutes the
cron job did fire here. This is in
Admiral.
Uh, verified this looks like a genuine
factual staleness bug.
Uh, does not mention Unreal Engine. It
is So, what is was able to verify that
it is a real bug. Not really a bug, but
just it just came out like an hour ago.
So, the current upstream evidence
supports the report.
Um, they checked the Hermes agent repo.
So, it has a commit
titled uh add Unreal Engine MCP.
So,
here's the proposed fix plan.
Just, you know, add a new raw source
and then update the MCP integration
wiki.
So, this is all done
autonomously. All using this wake agent
feature that Hermes has. So, I can run
this every 2 minutes pulling. Doesn't
cost me anything as long as there's no
new reports. And if there are new
reports, then that's when I do want an
agent working on it. It can do all of
this uh without me prompting it. You
know, it's all set up in the cron job
for it to do the research, verify the
report, and then give me a proposed fix
plan that I can easily just say, "Yep,
go fix it."
And in fact, if you really trusted your
agent and had this workflow really
ironed out perfectly, you could actually
have them implement the fix
um itself. Like make all these changes,
add to the file, but still not quite
fully trusting. I still want to have a
little bit of myself in the loop here.
But maybe one day I'll trust Admiral
enough to do that. There's two more cost
layers and they're basically the same
idea.
You push work off the expensive model
onto free code. So on the left here, you
can see the pre-run script again.
Uh, but this is kind of in its plain
form.
Beyond the wake decision, uh, scripts
output
gets injected into the prompt as, uh,
just context.
So you do the deterministic dat- data
gathering. You can pull an RSS feed, hit
an API, query a database
in Python for free.
Uh, and the model only has to summarize
what the script already fetched.
So you don't make the agent burn tool
calls fetching data that, uh, simple
script can just hand back.
So this is a very easy,
uh, workflow that can save you a lot on
tokens.
And on the right here in the blue,
enable tool sets,
and we talked a little bit about this in
the previous module, but you can set the
tool surface per job. So like a tiny
fetch the news job does not need, you
know, MOA, browser delegation
in its tool schema, and that kind of
context bloat
can cost extra for every single
call that you have.
If we just pin it to like web and file,
uh, the model see- sees a clean, cheap,
focused surface uh, without, you know,
wasting time and tokens on dealing with
those other tools.
So both levers really do the same thing.
They push work off the expensive model
onto the free code.
This is the last part of part three,
resilience, and it's free
uh, because you already did the work in
module five, if you remember.
The cron jobs inherit your fallback
providers, if you remember that from the
models, uh, video.
So rate limit or a server error
uh will just result in the next provider
instead of completely failing the run.
They inherit your credential pool
rotation. A throttled key rotates it to
the next one.
And you could pin a cheap model per job
for a routine digest.
And you can keep a heavy model for the
work that needs it.
And you could do this like I showed you
before, you can do per profile
cron jobs. So, if a profile has a
a specific model, uh you're going to be
able to do this a lot easier.
So, part four, chain.
You can wire jobs into a pipeline
without any like larger
multi-agent workflow.
So, here how this is how it works.
Um and it all comes from this context
from
feature.
And context from prepends an upstream
job's most recent completed output to
this one prompt.
Each stage on its own schedule.
So, here's kind of an example of how it
works. Say you have one cron job that
collects raw data, right?
Then you have job two that takes the
context from job one and runs a triage.
It scores and ranks it.
And then job three,
you can take the context from job two
and then ship it to Telegram.
Now, this is a fairly
uh simple example.
But you could see how you could use the
these different segments to create more
complicated pipelines as well.
So, that's the production pipeline. Each
stage is just a prompt, and the schedule
is the orchestration, and the output
archive is the message bus.
So, you get three prompts and two
context from links
to form a real pipe pipeline without any
framework.
Um
So, as I say here, this is many runs
over time.
Many agents at once is in uh module
eight. So, look forward to that next
week.
So, let's build this out. Uh I'm going
to show you here a daily briefing also
based on agent wikis.
And try to imagine what kind of
pipelines you can build for your own
life.
So, this is just going to be two
different jobs I'm going to be
chaining together.
And this is what's going to be collect a
no agent script, which we I just told
you about before, no agent. Uh the
script just logs the most checked
knowledge base counts every hour.
So, this should be zero, no model cuz
it's just checking a script uh that
already exists.
And then a daily briefing
using context from the collector.
And before I start just to kind of
address a question that a lot of you
might have, like why don't you just have
job one be the agent
um does the research and writes a report
and then
job two has the agent then read that
report and then do whatever analysis you
want. Why do you even need this context
from
uh feature?
And when I first read this, um I had
that kind of same question. But to
answer it, um this kind of setup using
context from from, it takes the handoff
out of the LLM's hands, and this is
really important. With those two manual
jobs, you [clears throat] you're going
to have two non-deterministic agents
being responsible for the wiring. So,
job one, the agent has to remember to
write the file to the exact right path
in the format that job two expects.
And then you have job two, the agent has
to remember to read that exact path.
So, either agent can mess that up. I
think we've all experienced that, agents
writing to the wrong path, wrong
workspace,
and just not
exactly following instructions.
So, with this setup with context from,
Hermes does the read and prepend at
runtime, not the model. So, the data
handoff becomes a guaranteed pipeline
instead of two prompts you're hoping
that the agents will will follow.
And especially important if you're using
models that are not necessarily frontier
models.
And another kind of advantage, and this
is a minor one, but the job two doesn't
need file tools in this case. The report
already arrives in their context window.
So, they don't need to use read file
call. There's no file tool set that they
need to enable.
And it's one fewer tool round trip, one
fewer thing that can go wrong, which
with these workflows, simpler is better.
And you also get uh fan in for free. So,
you can actually use multiple
uh jobs.
So, say instead of just one cron job to
start, you have three different ones
collecting different reports from
different places.
You can actually use context from with a
comma in between the jobs.
So, they can gather context from
multiple previous upstream cron jobs
easily.
If you're doing that manually, you're
going to hope that the agent reads all
these different files from these
different jobs and manages all those
different paths. So, having it directly
delivered to context obviously makes
things uh
a lot more error-proof. But,
just want to explain that a little bit
more in detail.
So, you can see the first thing, I'm
going to set up the first job here. Can
create a cron job with no agent script
that checks the most viewed wikis in
agent wikis each hour.
Okay, so I created the cron job. You can
see the mode is no agent. So, it's just
running this script, right?
And the script will just pull
all of the um the top wikis. You can see
the ones that we have for today so far.
Hermes and hyperframes on top, agent
workflows,
Llama CPP and Claude code. Some good
traffic today.
So, the second one, uh like I said, it's
going to be a daily briefing, which is
going to pull context from that job.
Uh it's going to rank the top knowledge
bases and also try to
analyze when knowledge bases are being
read more, because this is an hourly job
it's pulling from.
And then it's going to write up a little
brief for me.
And then it will simply deliver it to me
in Telegram.
Um there's going to be a wake agent gate
that skips zero traffic days.
I shouldn't have any of those, but you
can add that. And silent if there's
nothing notable.
You can also make it lean if you have a
cheap model pinned
and used enabled tool sets equals file.
You see the prompt I did for the second
one. I said uh so I want you to create a
second cron job
using context from uh this job, the
previous job I told it to make. It takes
the output and analyzes the top wikis
from that day plus any hourly trends.
Give me a tidy report delivered in
Telegram each morning at 9:00 a.m.
And you could see it created the job.
We have our second job. This is going to
be a daily one.
Delivery to Telegram.
And you can see right here uses context
from
this, which is the ID of previous cron
job.
This is kind of the chain
put in simpler terms, right? Number one
is a pure script, no LM runs hourly.
Pulls the data.
And then
number two is a daily
uh
cron job and it's fed by job one's
latest output, the latest context using
context from.
And that'll be delivered to my Telegram.
So two jobs
with one context from link.
And the nice thing is that it should
cost very little. Um the hourly
collector is zero cuz there's no model,
right? It's a no agent script. The only
thing that is running is that daily
brief, one fairly cheap LM term and only
if there's traffic cuz you can use wake
agent
to skip this entirely if there's light
traffic or no traffic on the site and
you don't need a report.
So I don't know if it'll be 1 cent, but
it will be fairly cheap. Um especially
this job doesn't require crazy
reasoning, so you could use a very cheap
model
for it or even like a local model.
So, this is the workflow. Um, it runs
every day, all day, collects its data
for free,
and only spends a cent writing the part
a human reads.
Okay, so you can see here it's been a
couple hours since I I last talked and
uh,
the hourly cron that we set up is
working fine. So, I'm just going to
trigger
the the daily report one just so you
could see what it looks like.
So, I'm just going to trigger it right
now and we will see
hopefully in Telegram the report.
Okay, so you can see this is what was
delivered in Telegram.
Um, has the overall wikis for the day.
And this is only a couple hours data, so
it's a little bit different. You can see
the notable hourly trends.
Um,
there was a spike mostly in Google Ads,
so somebody may have been doing research
with that one.
Um,
then at 2:00
uh, it mostly
cooled down
and then it rebounded led by Claude
code, so Take Away traffic is up
strongly versus yesterday.
Uh, growth is concentrated in Hermes
hyperframes
and you could see. Um, so that uses the
context from the previous job
to send me this analysis on a daily
basis. Be it on module 7 of my Hermes
agent masterclass about cron and
automation.
Or at least the simplest version of
automation.
Uh, we learned how cron works, the
gateway tick, fresh isolated sessions,
and the different ways you can create
them.
We learned about how to schedule them,
how to deliver them, and using silent.
Talked a lot about the zero cron,
um, saving
your LM usage to when you really need it
by using no agent, by using the wake
agent gate, uh, pre-run scripts, and
lean tool sets. Uh, we just saw context
from chaining
jobs into a pipeline with no kind of
underlying framework just using context
from
to have the context from a previous
job or several jobs injected directly
into the context where a a downstream
cron job.
And you watched me set up the daily
Asian Wiki's traffic briefing
delivered to Telegram for
yeah, maybe a cent, maybe a little bit
more, but not much every day.
So that's it for module 7 and module 8
is a very exciting one.
It's about sub agents.
This is another kind of topic that is
related to automation, but cron runs one
agent on a clock.
Next we're going to run many agents all
at once and using delegation, isolated
context, parallel work. We're also going
to be taking a look at the Kanban board.
Cron stretched a pipeline across time.
Sub agents fanned it out across workers.
So together they're two halves of
getting it more done without you in the
loop.
So look forward to that next week.
This is going to be the end of this
video. Please leave a comment. Let me
know
your thoughts on cron jobs and what you
have set up. What kind of
task are you using with cron jobs?
You have any cool pipelines that you're
doing?
Please leave a like and subscribe
and I'll see you in the next video.
Thank you for watching.