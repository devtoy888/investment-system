![Thumbnail (1920x1080)](https://i.ytimg.com/vi/KPsMThlFb8Y/maxresdefault.jpg)
# [Hermes Agent Masterclass: 9. Profiles & Kanban](https://www.youtube.com/watch?v=KPsMThlFb8Y)

**Visibility**: Public
**Uploaded by**: [Tonbi's AI Garage](https://www.youtube.com/@TonbisAIGarage)
**Uploaded at**: 2026-07-03
**Published at**: 
**Length**: 31:05
**Views**: 9361
**Likes**: 342
**Category**: Science & Technology

## Description

```
Module 9 of the Hermes Agent Masterclass: run several completely separate Hermes agents on one machine — each with its own memory, model, and phone number — then put them on a shared Kanban board to work as a team.

Sign up for my FREE weekly newsletter, where I spill my unfiltered thoughts on the latest AI news, cool research, and projects I'm building: https://www.onchainaigarage.com/

🐦 Follow Tonbi on X for real-time AI x blockchain updates! https://x.com/tonbistudio

Last module's sub-agents were ephemeral helpers inside one session — this module goes bigger and permanent with profiles: fully isolated Hermes agents, each with its own config, model, memory, skills, gateway, and persona. I cover what a profile actually is (and why it exists — you can't run two agents off one Hermes home), the three ways to create, clone, switch, and delete them, running multiple gateways at once so different profiles live in different messaging apps, and the honest caveat that a profile isolates state but does NOT sandbox your computer. Then the Kanban board: a durable SQLite-backed way to route one goal across multiple profiles by their descriptions, surviving restarts with a human able to unblock tasks mid-flight. It all builds to a live 3-profile team — researcher, coder, and writer — that takes one goal and completes a small project on its own.

Resources:
🔗 Hermes Agent: https://github.com/NousResearch/hermes-agent

Timestamps:
0:00 - Module 9: profiles, multi-instance, Kanban
2:58 - What a profile really is (vs a sub-agent)
6:19 - Creating profiles: CLI, dashboard, desktop app
11:07 - Switching, cloning, and deleting profiles
13:21 - Running many gateways at once (+ the token-lock rule)
16:15 - Profiles isolate state, they don't sandbox
17:34 - Packaging & sharing a whole agent
18:48 - The Kanban board: durable multi-profile teamwork
23:29 - Building a 3-profile team live

What would your agent team look like — which profiles would you spin up? Let me know in the comments. Module 10 is the finale: security, because we've now built agents that touch files, run shell, and spend money. Subscribe and hit the bell so you don't miss it! 🦐✨

#HermesAgent #MultiAgent #Kanban #AIAgents #AgenticWorkflows #Profiles #Automation #AITools #Masterclass
```

## Transcript

Welcome back to Hermes Agent
Masterclass.
We're now on module 9, profiles,
multi-instance, and Kanban.
Getting towards the end, this is our
penultimate
uh video.
And we've been discussing more
complicated use cases for Hermes Agent,
including automation, and this one today
is quite a big one on that topic.
So, in the last module, we learned how
to make an agent split itself into a
team for the length of a task using the
delegate task ephemeral children all
inside one session. Today, we go bigger
and more permanent. You're going to run
many separate Hermes Agents on one
machine,
each with its own brain, its own memory,
its own phone number,
and then hand them a shared board so
they can actually work together as a
team.
And this is what you're going to really
need for more complicated uh agentic
workflows.
So, by the end of this video, um you'll
know what a profile really is, how to
spin them up and clone and switch
between them, how to run a bunch of them
live at once, plus one honest caveat you
need to hear.
And then we're going to talk about the
Kanban board, a durable way to make your
profiles collaborate. And we're going to
build a real three-agent team that
routes one goal across all three.
So, in module 8, uh sub-agents shared
the parent's setup. They were ephemeral,
in session, and when they
and when the turn ended, you only kept a
summary. A profile is the opposite. It's
a whole separate Hermes Agent.
The term profile kind of downplays it
cuz it's a lot more than that. It has
its own config, its own model, its own
memory and skills, its own gateway. So,
it's not a setting.
It's a full second installation's worth
of state. And the Kanban board is what
turns that pile of profiles into a team.
Durable work routed by skill that
survives a restart. Sub-agents share a
brain for a task. Profiles have their
own, permanently.
So, this is the road map Uh um uh for
today's video.
First, we're going to talk about what a
profile actually is, then we're going to
create one together,
use clone and switch, and then we're
going to run many gateways at once.
Then, we're going to coordinate them on
the Kanban board, and then build a
proper workflow with multi-agent,
multi-profile setup.
So, we're going to go from one isolated
agent to a team that routes work among
itself. Let's get started.
And if you like this video, please
consider following me on X at Toby
Studio. I'll often be posting short
videos on the latest AI news and agent
features, as well as more in-depth
written post and articles. Also, sign up
for my free weekly newsletter, which I
write by hand and release every Friday.
Here, you'll see my honest thoughts
about the latest AI news, models,
research, and get a sneak peek of new
projects I'm working on
before they're announced anywhere else.
Sign up on onchainaigarage.com.
Link is in the description.
So, part one, isolate. Before you can
run a team, you need to know what one
team member is.
So, there's two ideas, and then we're
going to start running.
So, what is a profile? Under the hood, a
profile is pretty simple, and the
simplicity is really the whole trick.
It's fully isolated Hermes home.
It has its own directory with its own
everything. You can see here, this is
kind of an example.
In your .hermes directory, under
profiles, you have whatever the name of
the profile is, then the config.env,
soul, memory, session, skills, cron,
logs, workspace, everything
that your normal Hermes agent has.
And each profile also has its own home,
so that uh
the profile's npm or git state doesn't
bleed into another's.
And this is the same basic format that
you get from the default Hermes agent
when you install it for the first time.
A profile just gives you another full
copy of it. So, everything you learned
about config, memory, skills in the
earlier modules in this master class, it
all applies just to each profile.
But, it should be noted that the default
profile, which is what you just
installed when you start install Hermes
Agent, that is just in the .hermes
uh directory directly. It's not a
separate profile. It's not under
profile/default or anything like that.
And you can't delete or rename it.
So, for instance, for mine,
um I'm on a Windows machine. So, it's
going to be usually the default location
where this is installed is under your
users, whatever your username is, under
appdata, which may be hidden.
Um and then local, Hermes, and then it
has all of the files. And you can see
like the .env here,
um the config file. These are all for
the default profile. But, if I click on
profiles here, I have a couple different
So, like let's check X Researcher.
And if I look down here,
like it's bigger here.
Um so, this is the X Researcher profile.
You can see it has all the same files,
the .env, config, everything separate
soul as well. So, that is all under the
specific profile. And you see that it
has all the directories, separate cron
jobs, memories, plans, skills. So,
everything that you would have in your
default.
So, to
kind of differentiate from what we were
talking about in the last video, it's
not a sub agent. It's a whole Hermes.
The sub agent that we talked about in
the last video, it borrows the parent's
setup, the child sub agent. It's
ephemeral, it's in-session, summary
only, and it dies on interrupt. It's
just a helper inside of one agent's turn
when you want to do kind of parallel
work.
On the right is the profile, and it has
its own model, memory, skills, gateway,
persona, phone number even.
Um it's persistent, and it runs its own
process. It's a different agent
entirely, basically.
So, look in this red box down here.
Um and this is the reason this feature
kind of had to exist. If you try to run
two agents off the same Hermes home,
it would corrupt
the SQLite database. You'd have two
gateways fighting over it. Um and it
would end up just with corruption. So,
profiles are exactly the right fixed.
One sealed home per concurrent agent
throw state bleed.
So, a sub agent is a helper inside of
one agent. A profile is a completely
second agent.
So, let's make one. And there's a couple
different ways we can do this. It used
to just be from the CLI, but now there's
a couple different options.
So, the traditional way is just Hermes
profile create and then the name of a
profile.
So, let's do this. This is in
um my terminal. Do Hermes
Hermes profile
create coder.
And you can see profile
coder created at um the same directory
that I just showed you before, right?
/hermes/profiles/coder.
And it comes with the bundled skills
synced and you can do coder setup.
Just coder setup, no Hermes there.
And now you can configure it however
you'd like to do.
So, you can set up whatever model you're
using for it.
And there we go. Ready to go.
So, you can just use coder chat
instead of your normal Hermes chat.
And this will specifically open the same
TUI uh just using the coder profile.
There you can see
uh we opened it up. I I chose this um
step 3.7 flash.
It's a free model right now.
Uh but you see profiles/coder
has the tools and skills. It doesn't
have anything cuz it's pretty much blank
right now.
But there you go. I just said hello.
Can I help you with today?
And, um, you just work with it as you
usually would in the TUI. And it will,
right here, it'll have the name of the
profile.
If you do {slash} profile in the TUI,
it'll show you what profile you're
working with.
And it'll show you the location of the
files.
Like I said, there's a few ways you can
do this. If we do the Hermes dashboard,
and we can open this up in the
dashboard.
We come down here to profiles. This will
have all of your profiles that you, uh,
have worked on. And you can see all the
information about it.
So, this is pretty convenient. You just
do this. You can change the model, edit
the soul, edit the description, manage
skills and tools,
um, rename it even,
right in this nice little web UI.
And you can see which one is active, uh,
right here.
You can also create a
create a new profile just right here.
You can use clone config from to select
which other config,
uh, or rather which other profile you
want to clone the config from.
You can choose none, of course, if you
want to be blank. Or default, if you
just want to be a clone of your main
agent.
So, I could do, name it clone one, clone
from default.
Uh,
clone of my main.
You can choose inherit from
or select which model you want. We're
just going to inherit it. So, advanced
options, you can clone everything,
which means all the memories, skills,
sessions, state. Or if you just want to
clone the config. So, you can really
decide how much you want from it.
You just create it.
It needs lowercase. I don't think they
do.
Okay, no numbers.
There we go.
So, it's just going to create it
right here.
Okay, and you can see the clone was
here.
And uh we created it. So, it's a clone
of the main here. You can see it got the
model and also the skills
that my default has, whereas these ones
have other numbers of skills, you can
see.
So, they make it very easy. Um you could
also do this build one, which is more
advanced if you want to add more like
specific models, specific skills,
specific MC keys, you can use this build
function in the dashboard.
Um it's also pretty useful if you want
to make a more specific
uh profile.
So, the third way I'm going to show you
how to make a
um
profile is through the desktop app. This
is the desktop app. Down here, you'll
see all the different profiles. You'll
see the clone one we just made, uh
coder, which we just made as well, and
some of the other ones I previously had.
And the desktop app makes it super easy
to make
profiles. You just do new profile here,
and then you can just create it. Same
thing basically that you saw in the web
app. You can clone it as well.
Um and then optionally, you can add a
soul MD to give it a soul.
So, very similar and very easy to create
profiles just here
in the desktop app.
You can also do manage profiles down
here, and this will give you all of
them. Like you can see the clone one.
Um it shows you the model, the skills.
You can rename it, you can delete it.
Um or you can add it right here, down
here.
So, there's a couple different ways you
can target which profile you want to
work with. You can use this uh {slash} p
or double {slash} profile. This is ad
hoc in any position in the CLI.
So, you could do this like Hermes
{slash} p coder chat,
uh Hermes chat profile coder, like that.
And then profile use is going to be used
when you want to
switch the active profile to a different
one.
Like if I want to do Hermes profile, use
uh clone.
It switched it to clone, so now if I
just do the normal Hermes chat,
here we go. It opened up and you could
see down here it opens up with clone,
not as my default.
So if you want to do this in the web UI,
you can just go here very simply, click
on the three dots, set this one as
active.
And there we go. That's pretty easy,
probably the easier one.
If you want to do it in the web UI, and
also if you want to do it in the desktop
app here, just very simply click
um on
whichever profile you have. So like I
just clicked clone, and now I'm using
clone. See, it's kind of there's a
border around it. So it makes it super
easy, several different ways you can do
it. You don't want to use terminal, if
you do want to use terminal, you can
easily switch and work with your
different profiles and edit them and
manage them.
So lastly, um if you have a profile that
you were working with, experimenting
with, and now you're kind of done with
it, you perhaps broke it, you can delete
it very simply. Hermes
profile delete
clone.
And you could see
uh profile clone deleted.
You won't be able to delete it if your
desktop app is working though. You could
see I ran into an error up here.
Um so if the desktop app is open, you
have to close it if you want to delete
your clone, otherwise you'll run into an
error cuz technically the clone is still
working, it's locked.
And you can see in our
uh web app,
you can see in the web dashboard here,
clone is gone.
Uh let's delete another one here.
Delete our coder.
Same thing, you can just delete it here
quite simply. There you go.
So a couple different ways you can make,
use, or delete
profiles.
Okay, part three.
Run many at once, and this is where
pilot profiles becomes a pile of agents
actually running.
So, talking about gateway and messaging
apps therefore the headline is that each
profile can run its own gateway with its
own bot token. So, on one machine you
can have a coder living in Slack and
then your assistant living in Telegram
at the same time. These could be two
independent gateway processes with no
shared state.
And should be clear that token locks
point if you point two profiles at the
same bot token
and the second gateway is blocked.
Here, let me show you this.
Let me show you this. I'm going to start
the gateway here.
And we're going to do this profile X
researcher
gateway.
So, you just do X researcher gateway.
This is going to be the profile I'm
going to be running.
And so, this one is connected to this
Telegram bot and you can see this is
Bulls.
Um said hello, how how can I help you
today?
Uh what profile are you on?
It should be able to know.
There you go. X researcher profile which
is using Rock under the hood as a model.
So, let me try a different profile.
And I'm going to keep this gateway
running for the X researcher but I'm
going to start in a different terminal.
And here I'm going to do I created this
other
profile called writer.
The writer gateway.
And you can see here in writer, this is
a new bot that I made.
Um I said hello, hello, I'm Hermes your
AI assistant
for research, writing, coding,
automations.
Um let me ask it what profile are you
on?
There you go. The writer Hermes profile.
So, that worked. I had two different
gateways running. So, I was able to
contact and message two different
profiles. But, what if I still have the
X researcher profile running
under the gateway, and then I try to
start another gateway, which uses the
same
Telegram bot, it also uses bowls,
uh which is what the default profile
will do. So, if I just do Hermes
Gateway,
you can already see there's a lot of
text here, but right here is the
keyword. It says, "For Telegram Telegram
bot token already in use." And it has
the process right here. So, it says very
clearly, "Stop the other gateway first."
So, it's not going to work
trying to run two gateways using the
same token. So, I can still message
bowls, but he's still running under the
X researcher profile, see? Still on X
researcher, no change. So, whichever one
you ran first is going to get priority
to the messaging platform. And then the
second one's just going to error out
like this one did. And just for
clarification,
it's important to note that profiles
isolate state. They do not sandbox your
computer. Profiles get persistent
services like anything else. Coder
gateway install will give you a Hermes
gateway coder systemd or a launchd
service
as it's supervised in Docker. Each runs
on its own.
And this is what we kind of talked about
in module two.
But, it's it's important to note that a
profile will also have config, memory,
and sessions. It does not restrict file
system access
by default. If you're using a local
backend, coder can still read your
entire disk. So, soul.md will guide
behavior, it does not enforce
boundaries.
If you want real isolation, um you're
going to want to use this terminal. cwd
to pin a working directory plus a
sandbox backend using Docker or SSH from
module two.
So, profiles are not workspaces, and
they're not sandboxes.
So, you can't just have a profile in
your local back end and think that it's
completely sandboxed.
What you can do is kind of limit the
tool usage and skills that it has to try
to limit that.
But, a profile on itself is not, you
know, isolated in any real way.
So, one more thing before we get to the
Kanban board, and this is somewhat of a
newer feature,
is that you can package an entire agent
and hand it to someone else. I think
this is
pretty cool, actually. So, you can use,
for instance, Hermes profile export
coder or whatever the profile is going
to be.
Um it's going to create a uh .tar.gz
snapshot, and then you just use import
to restore. So, you have your whole
working config portable. So, you can
actually design basically a whole agent
on your own and then export it anywhere
you want it.
And um right here you can see
distributions. This Hermes profile
install and then uh
whatever the profile is
using the slash slash alias flag,
that installs the whole agent. So, you
get the sole config, skills, cron, MCP
from a Git repo. So, being able to share
a whole agent, basically, is pretty
cool.
So, as I said, you could build an agent
once and then share it as a repo. But, I
think as time goes on, we're going to be
wanting to create these whole agents and
then share them as kind of
packaged digital employees, almost,
because by distributing this as a GitHub
repo, uh like I said before, you have
everything that you need, basically, for
it to come up and start working.
So, part four is on the Kanban board.
So far, every profile has been a solo
act. This is how they collaborate,
durably. It's graduation from the
delegate task
tool you learned last week.
So, let me connect it with the last
video.
Delegate task was in process, ephemeral
children, summary only, and dies if the
parent gets interrupted. It's great for
fan out, this research right now.
It's a fork you watch finish.
Right the Kanban board. This is durable,
multi-profile, survives restarts.
Um a human can comment and unblock a
task mid-flight.
It's a team you hand a project to.
So, you want to reach for the sub agents
when you when the work fits in one
session and you're just watching it. You
want to reach for something like the
Kanban board when the work has to cross
agents and survive a restart.
And how do you see it? Go on the
dashboard here.
And we go down to Kanban.
And this is what it looks like.
And here's a mental model for how the
board works. It's basically a pipeline.
So, a goal goes on the board, right?
An auxiliary model, the Kanban
decomposer, fans it out into child
tasks. Each child is routed to the best
fit profile by its description.
And the gateway's dispatcher loop runs
each one as that profile until it's
done.
So, two things to lock down here. The
board is a durable SQLite file.
And
you could find it here at kanban.db
where the assignee is a profile.
And the assignee of a task is a profile,
not a person. So, that's the whole
conceptual leap.
And it bears mentioning again, routing
happens by description. That's why those
one-line roles you set
at create time really matter.
Um they are used for this. The router
reads the descriptions, not the names.
And to head off a common
uh mix-up, the model that builds the
task graph is Kanban decomposer. The
profile describer is a different
auxiliary model that just auto writes
those descriptions.
So, one writes the labels, the other
reads them to route.
So, there's a couple different ways you
can operate the Kanban board.
From the CLI, you can just do Hermes
Kanban create.
And then
do whatever the the goal is and then
assign it to a certain profile.
You can use Hermes Kanban decompose with
an ID
to fan a goal out.
Uh you could also use Hermes Kanban list
show assign dispatch.
And then you can also use Hermes Kanban
swarm
uh with whatever your goal is.
And you can use workers and then set the
the profiles for the workers verifier
set it, synthesizer set it. So this is
kind of a more advanced for a whole
agent swarm if you want that.
So on the worker side the agents don't
shell out to Hermes Kanban. They get a
gated Kanban tool set. Kanban show
create complete block comment. They
update the board through tools never by
shelling to Hermes Kanban.
So they only get to touch the board
through these tools.
So if you want a very in-depth look at
the Kanban board I did a like a full
video um this one the ultimate
multi-agent workflow with Hermes agent
Kanban board. So check this out. This is
around a month ago but I did a very
in-depth look at the Kanban board.
Uh but for this masterclass let me show
you
um
just a little bit. You could see these
are some of the old tasks that were
done. And in them down here you can
scroll down. You could see the exact
tools that he used. This is Kanban it's
cut off but this is Kanban show.
Um these are the tools that I was just
talking about and then when it's done
Kanban CO here but that's Kanban
complete. So we're going to see this in
action a little bit but you can see here
the different cards or areas.
Uh triage
to do's waiting on dependencies
scheduled so waiting on a known time
delay or scheduled follow up. Ready is
when the dependencies have been
satisfied. And to assign a profile to
dispatch. In progress is what has been
claimed by a worker and is being worked
on right now.
Blocked is when there's something that
needs a human input. So the task itself
is blocked until you come and unlock it.
And then review at the end. And then
when everything is done, you can see
here in the done section.
So, a common question may be, can you
set a model per task? Uh no. A task runs
on its assignee profile's model. There's
no per task model override.
So, if you want to use a different model
on a specific task, you need to route it
through a different profile. You just
need to create a profile for that
specific task, and then you can have a
specific model to run it.
Okay, so I'm going to do a small demo
here of the Kanban board. Like I said,
if you want a real in-depth look, look
at that uh older video.
So, here's the team I put together.
Research researcher,
the web long context model.
Uh description's going to be resources
and docs, writes findings. Coder, which
is going to be terminal and file code
model.
Implements and test from a spec. And
then writer, which you saw before,
going to be a cheaper model, and the
description will be turn findings and
code into clear write up.
Okay, so first things first, I created
those three profiles. You can see
researcher here and the description.
Uh resources and docs, writes findings.
Same thing writer, and then I have coder
here.
So, I set the models for
uh researcher and coder
as uh the default GPT 5.5. And writer is
going to be using a slightly cheaper
one, the GLM 5.2 model.
This is where you're able to really uh
customize the profiles and select models
and also skills that fit the profile for
whatever task you're giving it. So, very
simply, I'm just saying, "Hermes, this
is in the terminal. Hermes, Kanban
create
research ML in sports, prototype an
approach, and write it up."
So, there it created um this one. This
is the specific board.
And let's see it work.
Back on the Kanban board, you can see
this is the task I gave it.
So, it needs an assignee. I could do it
right here in the the Kanban board
itself, or we can just do this.
You do Hermes Kanban decompose and then
the ID.
So, we're going to set this up um and
you do Hermes Kanban create
with the goal. We're going to do
research ML in sports prototype and
approach and write it up.
And then you need this triage flag to
put it in triage and that'll spark the
auto decompose, which will assign it to
appropriate profiles.
You see it created this. This is the
ID of this uh Kanban board.
You see it moved here into the triage
section.
So, you can manually decompose this so
it'll break into different tasks and
different profiles. Um or if you have
auto decompose on your config, uh it
should do it automatically.
You can also, if you click on it here,
you can do decompose right here or
specify if you want to give to specific
profiles.
Okay, so I clicked uh decompose and you
can see it automatically broken up into
what is ready right now, research back
tool ML applications in sports, and this
is by the researcher profile.
And then
um
uh the default has the the main task.
And then you can see coder here and
writer. So, it automatically broke it
into those profiles without me
specifying it.
And that's uh just the decompose
decompose function.
So, I have orchestration on auto.
So, the orchestration profile is just my
default, uh but you can also alter this
as well if you want.
So, something like gets stuck like I had
this one's kind of stuck in the ready
here. If you just click nudge
dispatcher, it'll move it to progress if
there's any kind of issue like that.
So, we can see this is now in progress.
This is the researcher. Okay, you can
see it's starting to work here.
You can see up here I had an issue with
the the model.
Um but I I changed the model and then
simply send it back
um to ready and then
put it back into progress and it kind of
restarts the task and it starts moving
like this.
So, let's just let it work. It'll do
this all automatically.
Um once the research is done,
it'll start building prototype and then
write a clear report for me.
Okay, you can see the researcher
finished.
Done with the research, handed off
uh to the coder.
Okay, you can see
our research is done.
And then we just handed it off to the
coder, which is starting to build
small ML prototype.
Okay, so you see the coder
um got into the block section. It needs
my
my help here. So, the review is
required. Built and verified the soccer
match outcome
uh machine learning prototype awaiting
human approval approval before marking
the code task as done. So, this
gets the human in the loop to check the
code here and then
to unblock this,
you just simply click unblock.
And you can see here is completing.
And our last
um task here, the writer profile, is in
progress now.
Starting to work.
Okay, so you can see all three tasks are
done.
And we look in the directory here.
This is what the coder built for me,
this Python script
for the prototype.
I can see here it some nice coding for
me.
And then the writer wrote out this
report for me. These are all in their
own workspaces. In the Kanban, you could
obviously direct it to put it into a
certain, you know, workspace or
directory that you want. Uh but that's
it. You can see all the data here.
So, that's the Kanban board. It's um one
goal. You can decompose it, route it to
three profiles based on their skill
automatically. I didn't specify that.
This is durable. The board survives a
restart. So, even if the gateway is
killed, you can bring it back and the
work can resume at any time. You can
unblock things that get blocked. Uh
human in the loop, like you saw before.
You can comment on a card, block, or
unblock a task mid-flight.
So, delegate task and sub-agents is a 4K
watch finish. Kanban is a team that you
hand a project to and can step into.
So, that's it uh for this module nine on
profiles and the Kanban board. I think
we all learned what a profile is. It's a
fully isolated Hermes
with its own config, model, memory,
skills, gateway, persona. Uh we learned
about using create and clone and use.
Um we also talked about the profile
builder that you saw in the dashboard as
well as in the desktop app. Showed about
uh many gateways at once so that
different profiles can run different
messaging apps.
And then showed you about how you can
share a whole agent using export,
import, and then get distributions. And
then we looked at the Kanban board.
A durable multi-profile routed by
description.
Um and you saw that three-profile team
built a little project on its own.
So, that's going to be it for this
video.
Coming towards the end, module 10 next
week. It's going to be our finale.
And the topic of that is going to be
security cuz we've learned a lot about
Hermes agent, what you can do with it.
And we built a whole team of agents that
can touch files, shell accounts, and
spend money. So, we need to take a whole
module to talk about security cuz it's
very important uh topic when you're
dealing with agents because as powerful
as these workflows and agents can be,
they could also be quite destructive if
you're not careful.
That's going to be module 10 next week.
And this is going to be it for this
video. So, please leave a comment. Let
me know your thoughts.
Like the video, please like leave a
like.
Uh please subscribe and I'll see you in
the next video.
Thank you for watching.