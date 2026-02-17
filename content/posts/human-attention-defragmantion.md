+++
date = '2026-02-13T10:00:00+01:00'
draft = false
title = 'Human attention defragmentation: flow, fatigue, and AI coding'
tags = ["AI", "career", "personal", "productivity"]
+++

**TL;DR**: AI coding tools don't just accelerate output - they fragment attention in ways traditional programming never did.

---

Something shifted a few months into using AI coding tools heavily. The output kept going up - more PRs, more features shipped, more projects moving simultaneously. But at some point I realized I couldn't fully explain any of them. Not in the way I used to be able to explain code I'd written myself. I knew what each project was *supposed* to do. I didn't have the same grip on what it *actually* did.

That gap felt small at first. It's not.

## What deep work used to cost

Programming, done properly, is expensive to start and hard to stop. Getting into a real working state - holding a distributed system or a complex algorithm in your head all at once - takes 20-30 minutes of undisturbed ramp-up. Once there, you're in flow: everything is present, the experiment is clear, the code and the mental model stay in sync. It's also genuinely exhausting. After a few hours you hit a wall. You stop, not because you decided to, but because you were done.

That wall was a feature, not a bug. The acute fatigue was a circuit breaker. It told you clearly: this session is over. And the flow state itself - the meditative depth of actually building something - was the part of engineering that felt like craft. The part that made you feel like you'd made something that was yours.

## The ownership gap

Here's what I found harder to articulate than the productivity angle: when you write code, you *own* it. Not legally - mentally. You made decisions about how it works, why it works that way, what trade-offs you accepted. Ask yourself about it a week later and you'll know. That ownership is how engineers build intuition: you make small decisions continuously, they accumulate, and over time you develop a model of the systems you work in that goes beyond what's documented.

I've had the experience of being asked about a service I'd "built" with Claude and realizing my mental model was two weeks stale. I'd reviewed the PR, approved it, moved on, and the system had kept evolving without me staying inside it. The code was correct. My understanding of it wasn't. That's not a failure of the tools - it's a failure of presence. But the tools make that failure easy to fall into.

In my opinion, this is what most engineers mean when they say something "feels off" with AI-assisted development. Not nostalgia for writing boilerplate. The loss of accumulated ownership - the kind that makes a codebase feel legible and the work feel like yours.

## The attention fragmentation

The structural problem is what happens during model execution. You're idle. Not resting - idle. Your brain doesn't pause while the model writes a service; it looks for something productive to fill the gap. So you open another project. Then another. You have three agents running in parallel, each in a different codebase. The output is real, but your presence in each is thin. You're routing, not building - checking in on threads, reading diffs, sending the next instruction, moving on. Overnight runs add another layer: somewhere in the background there's a task finishing, possibly drifting, possibly stuck on something a single clarifying message would fix.

You end up with a lot of output and a shallow relationship to all of it.

## The signal that disappears

The subtler consequence is fatigue that doesn't announce itself.

With focused programming, exhaustion was legible. A few hours of real work and the wall arrived clearly: time to stop. That signal was useful - it had information in it. When you're in orchestrator mode across multiple parallel threads, the signal disappears. The cognitive load per unit of time is lower, so you can keep going well past any reasonable stopping point without hitting the specific tiredness of deep work. But you're accumulating something else the whole time - a slow erosion of sharpness and interest that only becomes obvious in retrospect, usually when you realize you've been working all day and have nothing you understand deeply to show for it.

## What actually helps

The fix isn't going back to writing everything manually - that's neither the point nor a realistic option. The adjustment is more specific.

When the model is running, I stay in the source code instead of switching to another project. I read what it wrote, understand what it's about to do, and when it finishes I'm already oriented - the next instruction comes from actual understanding. This also removes the idle gap that makes context-switching tempting. When I'm actively reading and thinking about the code, I'm not idle; I'm participating.

The distinction between "reviewing diffs" and "being in the code" matters more than I expected. When I read what Claude writes, modify parts directly, and send back specific instructions - "redo this function like this, not that" - the engagement stays close enough to flow that it doesn't feel like supervision. It feels like collaboration. The ownership accumulates again because I'm making small decisions continuously instead of approving blocks of output.

One project at a time is the other half. Parallelization looks like leverage but for anything non-trivial it's diffusion: spreading thin across multiple contexts instead of being deep in one.

## Conclusion

I don't think the tools are the problem. The default workflow that emerges from them is. Nothing in the tooling forces you to run four sessions in parallel or hand off architectural decisions you haven't thought through - that's just the path of least resistance.

In my opinion, the adjustment is less about tool usage and more about presence.

Stay an engineer inside your own codebase - not just a director of what it becomes.
