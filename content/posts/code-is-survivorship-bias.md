+++
date = '2026-02-18T10:00:00+01:00'
draft = true
title = 'Code is survivorship bias'
tags = ["engineering", "distributed-systems", "vibe-engineering"]
+++

**TL;DR**: Code only shows what was kept, not what was tried and rejected. In high-performance systems, the invisible decisions - the things explicitly *not* done - are often the most important ones. Vibe engineering makes it easy to clone the visible structure but impossible to inherit the failures that shaped it.

---

There's a thing that happens when you read a production codebase for the first time: you see structure, patterns, naming conventions, design choices. It looks coherent. It looks like the engineers knew what they were doing from the start.

They didn't. Nobody does.

What you're looking at is survivorship bias. Every line in that repo exists because somebody decided to keep it. The three other approaches that were tried before it, the PRs that got reverted after causing production incidents, the architectural decisions that were explicitly ruled out - none of that is there. It got pruned.

## What code doesn't tell you

Take a distributed messaging system. The code shows a simple in-memory buffer that flushes to disk every 200ms. Clean. Readable. Nothing special.

What the code doesn't show:

- They tried Redis for this buffer. Worked great until a network partition caused message duplication at the consumer side that was invisible until it wasn't. They ripped it out and never went back.
- The 200ms flush interval isn't arbitrary. 100ms caused too many IOPs on smaller instances. 500ms made the data loss window during crashes unacceptable. 200ms is the negotiated result of that pain.
- There's no write-ahead log on a specific path because they had one and it made replay logic during crash recovery 40x more complicated. The simplicity is intentional.

None of this lives in the code. Some of it's in a post-mortem from 18 months ago. Some lives in the head of the engineer who spent three days debugging the Redis partition issue. Some is just gone.

## Where vibe engineering goes wrong

Vibe engineering - prompting AI to generate production-looking code - lowered the barrier to having code dramatically. You can spin up a distributed cache, a message queue, or a rate limiter in an afternoon. The code looks like it was written by someone experienced. The patterns are there. The structure is reasonable.

But it carries zero institutional memory.

The problem isn't that AI-generated code is bad. A lot of it is quite good. The problem is that it creates a generation of engineers who look at a working codebase and think "I understand this system." Because the code is readable, the logic is followable, and AI can explain every line.

What they can't see: why that backpressure mechanism exists, why that specific circuit breaker configuration, why eventual consistency is used in exactly those three places and nowhere else. That knowledge isn't in the code. It's in the failures that forced those choices.

So they clone the structure and miss the entire point.

## The negative decisions that matter most

In high-performance systems, I've noticed that the most important decisions are the negative ones. Not "we use X" but "we explicitly don't do Y here."

- We don't allow unbounded queues in this component (because we had one and it cascaded into a full system OOM under load)
- We don't cache this endpoint (because caching it caused stale reads during a specific race condition that took two weeks to debug)
- We don't write to this table from more than one service (because we tried and ended up with contention that killed throughput at 10k req/s)
- We don't use distributed transactions here (because two-phase commit latency made the 99th percentile unacceptable, and the consistency guarantees weren't worth it)

These decisions are architecture. They're constraints that protect the system from known failure modes. And they are almost never written down explicitly.

ADRs (Architecture Decision Records) exist partly to solve this. But even with ADRs, negative decisions are underdocumented. It's much easier to write "we chose Kafka because it handles high throughput" than "we chose not to use RabbitMQ because we hit a dead-letter queue management issue at 50k msg/s that was going to require significant custom logic." The second one requires admitting the failed attempt.

## The replication trap

Here's what vibe engineering makes dangerously easy: you can read a high-performance system's code and generate something that looks structurally identical in a few hours. Same patterns, same abstractions, similar naming. An AI can even explain why each piece is there.

But you've just built the version of that system before any production incidents.

The original system went through six months of incidents, hotfixes, architectural pivots, and quiet reversions before it looked the way it does today. Those aren't visible in the final state. What you've replicated is the skeleton without any of the scar tissue.

And then you hit production. The system starts behaving in ways that seem random. Weird latency spikes, edge-case failures, cascading issues that look unrelated. You start debugging.

You're about to repeat every mistake the original team already made. Except you don't have their post-mortems, and you don't know what you don't know.

## This is a knowledge transfer problem

I think part of the reason this gets ignored is that software engineering culture has always been bad at documenting failures. We write documentation for APIs, for setup procedures, for system design. We rarely write "here's what we tried that didn't work and specifically why."

Code reviews focus on the positive: does this solve the problem, is it clean, does it test well. They rarely surface "wait, we already tried this approach in 2023, let me pull the post-mortem."

The institutional knowledge about negative decisions lives in the oldest engineers on the team, in Slack threads from three years ago, in post-mortems that aren't linked from anywhere. When those engineers leave, a lot of that knowledge evaporates. And with vibe engineering, we now have a fast path to rebuilding systems without any of it.

---

Reading code isn't the same as understanding a system. In high-performance systems, the code you can see is the easy part. The hard part is the graveyard of approaches that didn't work - and understanding why they failed is what actually makes someone able to build reliable systems at scale.

In my opinion, vibe engineering doesn't solve this problem. It just makes it cheaper to create the illusion of understanding it.
