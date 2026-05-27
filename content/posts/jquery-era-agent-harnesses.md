+++
date = '2026-05-27T08:00:00+01:00'
draft = false
title = "We're in the jQuery era of AI. Who'll be the React of agents?"
description = "Agent harnesses today look like jQuery in 2006: pragmatic abstractions over a primitive whose surface keeps expanding. Nobody has built the React of agents yet."
tags = ["AI", "agents", "harness", "MCP", "skills", "engineering"]
+++

**TL;DR**: Current agent harnesses are what jQuery was in 2006: pragmatic abstractions over an unstable primitive. The "React of agents" doesn't exist yet, and the obstacle isn't model instability - it's an open-ended capability surface that keeps expanding. I think that's fine.

---

I've been working with agent harnesses for about a year and the whole thing keeps feeling familiar. The fragmentation, the plugin ecosystems, the half-stable standards, the "rip it out in six months" energy. The comparison I keep coming back to is the web in 2006 - I was 9 then so I didn't live through it, but the pattern is hard to miss once you've read enough about how that era played out.

## What 2006 actually looked like

If you weren't writing JavaScript back then, the picture was this. The DOM was inconsistent across browsers. IE6, IE7, Firefox 2, Safari 2, Opera 9 - each one had its own attribute-access quirks, event model, and rendering bugs. You couldn't just call `addEventListener` and trust it. You wrote twenty lines of branching to do what should have been one line.

Then a bunch of libraries showed up at almost the same time:

- **Prototype.js** - extended native objects, gave you `$` and Ajax helpers.
- **MooTools** - class-based, extended natives more aggressively.
- **jQuery** - selectors, chainable methods, event normalization.
- **YUI** - Yahoo's heavy framework.
- **Dojo** - kitchen-sink, IBM-leaning.

All five solved the same problem from different angles. None of them were "right." They were all pragmatic abstractions over a primitive that was still misbehaving.

The reason jQuery won wasn't elegance. It won because it stayed thin and didn't try to turn the DOM into something it wasn't. `$('.foo').addClass('bar')` mapped cleanly to "do this DOM thing, but everywhere it works." The other libraries reached too far.

And then React showed up, and within a few years the whole DOM-manipulation paradigm was legacy. Not because jQuery was bad. Because someone proposed a completely different abstraction - state → virtual DOM → render - that made the browser's mess somebody else's problem. The shape of that move matters.

## Where we are now

Look at the harness landscape today. Off the top of my head: Claude Code, Codex CLI, Cursor, Aider, OpenCode, Cline, Continue, Roo, Windsurf, Gemini CLI, Antigravity, Kiro. Every one of them is solving the same problem: the model can't run a long task on its own, so wrap it in something.

They share the same skeleton - ReAct loop, tool registry, context manager, approval gates, some kind of memory hook. Someone could argue that skeleton *is* the emerging abstraction. I think that's mistaking shape for substance. Every harness has a tool registry, but the load-bearing decisions - how many tools, how to route them, when to compact context, what to keep across turns - are capability bets baked into each one, and those don't port. The boring parts are shared. The interesting parts aren't.

Each harness picks a slightly different shape of "what the model is good at right now."

- **Claude Code** assumes strong native tool use, runs a tight loop with explicit approval gates, leans on file-edit primitives.
- **Codex CLI** assumes well-scoped GitHub issues, runs in cloud sandboxes, ends with a PR. One task at a time.
- **Cursor** assumes a human in the loop. Stalls at ambiguous decisions, optimizes for fast feedback.
- **Aider** assumes pair-programming. Diff-edits over a small file set.

None of them are wrong. Those shapes just keep changing.

## The surface keeps expanding

The DOM in 2006 was annoying but bounded. The bugs were known. You could write a compatibility shim once and trust it for two years.

The model in 2026 isn't like that. Every quarter brings something that breaks an existing harness assumption:

- Bigger context windows (1M now, soon more) - context engineering rules get rewritten.
- Better thinking traces - the explicit self-critique step in the harness becomes redundant.
- Computer use - entirely new tool category, no harness was designed for it.
- Longer agentic horizons - the "memory hook" becomes the load-bearing layer, not an afterthought.

The memory point deserves one sentence on its own: when an agent runs for an hour, state lives in the prompt; when it runs for a week, state has to live somewhere durable, and the whole harness reorganizes around how that state gets read and written.

Each of these breaks something in current harness design. The Claude Code that shipped a year ago is not the Claude Code that ships today, and that's not just feature creep. It's the design rotating around the new primitive shape.

I think that's the part of the parallel that matters most. jQuery sat over a finite surface; harnesses sit over one that keeps expanding.

## Standards as jQuery plugins

The standards layer is where the parallel gets really tight.

jQuery had a plugin ecosystem. `$.fn.X = function() {...}`. Every problem became "find a plugin." Date pickers, sliders, validators, form helpers. The plugins were great until they collided, broke on the next jQuery release, or solved the same thing four different ways.

Today the comparable layer is:

- **MCP** - tools-as-servers. Anthropic shipped it, then it spread. Useful, but I've already seen three different opinions on how to write an MCP server properly.
- **Skills** - composable workflows. A higher-level abstraction that landed because MCP was too low-level once "skill execution" became a model capability.
- **A2A** - Google's agent-to-agent protocol. Solves the horizontal coordination problem MCP doesn't touch.
- **AGENTS.md / CLAUDE.md / .cursor/rules** - same file, different name, depending on which harness you're feeding.

Each is genuinely useful right now. None will be the final answer. They're shaped by what current models can do, and the next generation of models will reshape them.

A concrete example. When I write a tool for a coding harness, the signature usually looks something like this:

```python
def read_file(path: str, offset: int = 0, limit: int = 2000) -> str:
    """Read a file from the filesystem."""
```

The `offset` and `limit` parameters exist because the model wastes context on huge files. That's a workaround for a model limitation, not a property of the file system. When context becomes effectively free, that signature looks ridiculous. The MCP shape carries the scar tissue forward, even when the reason for it is gone.

The same dynamic shows up in skills. They exist because models got good enough at following multi-step recipes that "tool" became too granular. In two years, when models compose tools naturally, the skill abstraction might look like training wheels.

## What the React of agents would look like

I don't know. Nobody does. The structural property would be: an abstraction that doesn't change shape when the model gets better.

React works because the component model is invariant under browser improvements. Chromium can ship `<dialog>`, fix flexbox, add View Transitions - none of it changes how you write a component. The abstraction is above the noise.

A sharp reader will push back here: React itself shipped in 2013, when IE8 and IE9 still mattered and the DOM was nowhere near settled. React didn't wait for the primitive to stabilize - it routed around the instability with the virtual DOM. So why can't someone build the same shape of abstraction for agents today?

I think the answer is in the kind of instability. The DOM's surface was finite and knowable. You could enumerate the quirks: which browsers fire which events, which CSS properties render wrong, which methods don't exist. The virtual DOM worked because it sat over an ugly but bounded surface. You could write a shim because you knew exactly what to shim.

Model capability is open-ended. Computer use didn't exist a year ago. Long-horizon agentic behavior didn't exist. 10M context didn't exist. You can't shim a capability that hasn't been invented yet, because the shape of the next one isn't predictable. Every six months the surface area expands, and the new piece doesn't fit cleanly into anything written before it.

A "React of agents" still needs to sit above the model. Not just invariant under bigger context windows or cheaper tool calls - invariant under capabilities that haven't been invented yet. That sounds almost paradoxical, and that's the obstacle. Today's harnesses are glued to the current capability profile, and nobody can pre-absorb a capability whose shape isn't known.

I've thought about what direction it could come from. Maybe "agent contracts" - a typed declaration of what the agent does, with the runtime compiling the loop, tools, and context strategy for whatever model it's pointed at. Maybe a graph-shaped state machine where the agent is the graph and the harness compiles it differently per backend. Both feel plausible. Both also feel like 2008-era guesses about what React was going to be.

In my opinion, nobody has found it yet. The hard part isn't waiting for models to stop changing - it's compressing a surface that nobody can fully see.

## Why this is fine

The takeaway is not "stop building harnesses." jQuery was the right thing to do in 2006. It made the web shippable for a decade. People who learned jQuery did real work, shipped real products, and most of them moved to React without much pain when the time came.

Current harnesses are the same. They're the right shape for now. They're letting people ship agents that do real work. Most of them will get replaced once someone finds an abstraction that doesn't break when the next capability ships, and that's how every new abstraction goes when it sits on top of a primitive whose surface keeps growing.

The mistake I see people make is treating today's harness choices as if they're load-bearing forever. They're not. Pick the harness that lets you ship now, expect to rewrite, and don't over-invest in the standards before they stabilize.
