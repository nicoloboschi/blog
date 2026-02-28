# Social Media Distribution: Code is survivorship bias

## Twitter Thread

### Hook
Code only shows what survived.

Not what was tried. Not what was rejected. Not what caused the 3am incident.

Vibe engineers read a codebase and think they understand the system. They don't.

### Pain Points
In high-performance systems, the most important decisions are invisible:

- We DON'T cache this endpoint (caused a race condition that took 2 weeks to debug)
- We DON'T allow unbounded queues here (had one, it OOM'd the cluster under load)
- We DON'T use distributed transactions (2PC latency killed the 99th percentile)
- We DON'T write to this table from multiple services (contention at 10k req/s)

None of that is in the code.

### The Problem
Every codebase is survivorship bias.

What you see: patterns, structure, design choices.
What you don't see: 6 months of incidents, reverts, and failed experiments that shaped every constraint.

Vibe engineering lets you replicate the skeleton. The scar tissue is gone.

### What happens next
You generate something structurally identical to a production system.

Then you hit production. Weird latency spikes. Cascading failures.

You're repeating every mistake the original team already made. Except you don't have their post-mortems.

### Link + Insight
Reading code ≠ understanding a system.

The hard part is the graveyard of approaches that didn't work.

[LINK]

---

## LinkedIn Post

### Story Hook
I've been reading production codebases for over a decade.

The first impression is always the same: it looks like the engineers knew what they were doing from the start.

They didn't. Nobody does.

### The Problem
What you're looking at is survivorship bias.

Every line exists because someone decided to keep it.

What's missing: the three approaches tried before it. The PRs reverted after production incidents. The architectural decisions explicitly ruled out after failures.

That's not in the code. It got pruned.

### The WTF Moment
Vibe engineering made it cheap to replicate *code structure*. You can clone a distributed cache, a message queue, a rate limiter in an afternoon.

The code looks right. The patterns are there. An AI can explain every line.

But it carries zero institutional memory.

In a real high-performance system, the most important decisions are the negative ones:

- **We don't cache this endpoint** — because we did, and it caused a race condition that took two weeks to debug
- **We don't allow unbounded queues** — because we had one, and it cascaded into a full OOM under load
- **We don't use distributed transactions here** — because 2PC latency made the 99th percentile unacceptable
- **We don't write to this table from multiple services** — because contention killed throughput at 10k req/s

None of this is in the code. Some of it's in a post-mortem from 18 months ago. Some lives in the head of the engineer who debugged the issue. Some is just gone.

### The Replication Trap
When you replicate a system with vibe engineering, you're building the version before any production incidents.

The original went through 6 months of failures, hotfixes, and quiet reversions before it looked the way it does today.

You've cloned the skeleton. The scar tissue is gone.

Then you hit production. The system starts misbehaving in ways that seem random.

You're about to repeat every mistake the original team already made. Except you don't have their post-mortems — and you don't know what you don't know.

### Conclusion
Reading code isn't the same as understanding a system.

In high-performance systems, the code you can see is the easy part. The hard part is the graveyard of approaches that didn't work.

In my opinion, vibe engineering doesn't solve this. It just makes it cheaper to create the illusion of understanding it.

[LINK]

---

## Key Themes to Emphasize
- Survivorship bias framing (memorable hook)
- Concrete negative decisions with specific failure modes
- Vibe engineering critique is nuanced — the code is fine, the context is missing
- Post-mortem culture problem (engineering is bad at documenting failures)
- Institutional memory evaporates when engineers leave

## Hashtags
### Twitter
#SoftwareEngineering #DistributedSystems #VibeEngineering #SystemDesign

### LinkedIn
#SoftwareEngineering #DistributedSystems #SystemDesign #EngineeringCulture #TechCareers
