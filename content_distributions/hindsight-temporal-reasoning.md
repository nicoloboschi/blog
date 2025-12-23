# Social Media - Temporal Reasoning: "When It Happened" vs "When You Learned It"

## Twitter/X

### Option 1 - Single (Problem → Solution)
```
Most memory systems store ONE timestamp per memory.

Problem: "Alice got married last June" stored in January.

→ Timestamp it January? "What happened in June?" fails
→ Timestamp it June? "What did we discuss recently?" fails

You need both.

Hindsight tracks two dimensions:
• Occurrence: when it happened
• Mention: when you learned it

[link]
```

### Option 2 - Single (Short)
```
"What did I learn last week about events from last month?"

This query is impossible with single-timestamp memory.

Hindsight tracks:
• When it happened (occurrence)
• When you learned it (mention)

+48 points on temporal reasoning benchmarks.

[link]
```

### Option 3 - Single (Technical hook)
```
weight = exp(−Δt / σₜ)

This formula links memories by temporal proximity in Hindsight's knowledge graph.

Events a day apart → strong connection
Events months apart → weak connection

Enables queries like "What was happening around Alice's promotion?"

[link]
```

### Option 4 - Thread (Deep dive)
```
1/5
Every memory system I've seen makes the same mistake: one timestamp per memory.

Here's why that breaks temporal queries 🧵

2/5
Scenario: User tells agent in January "Alice got married last June"

If you timestamp it January (when stored):
→ "What happened in June?" fails

If you timestamp it June (when it happened):
→ "What did we discuss recently?" fails

3/5
Hindsight tracks TWO temporal dimensions:

• Occurrence interval (τₛ, τₑ): when the event happened
• Mention timestamp (τₘ): when you learned it

Same memory, two timestamps. Both queries now work.

4/5
It also builds temporal links in the knowledge graph:

weight = exp(−Δt / σₜ)

Events close in time stay connected. Ask "What was happening around Alice's promotion?" and it finds temporally adjacent memories.

5/5
Result on LongMemEval benchmarks:

Full-context baseline: 31.6%
Hindsight: 79.7%

+48 points from tracking two timestamps instead of one.

Technical breakdown: [link]
```

### Option 5 - Thread (Story format)
```
1/4
I kept hitting the same wall building agent memory.

User: "Alice got married last June" (said in January)

Me: *timestamps it January*

Later: "What happened in June?" → nothing found

🤦

2/4
The fix seems obvious - timestamp it June instead.

But then: "What did we discuss recently?" → nothing found

The January conversation is now 6 months old according to my memory system.

Single timestamp = impossible trade-off.

3/4
Hindsight's solution:

Track both.
• Occurrence: June 2024 (when it happened)
• Mention: January 2025 (when you learned it)

Add temporal graph links between memories (exponential decay by distance).

Now multi-hop temporal queries work too.

4/4
"What was Bob working on when Alice got married?"

→ Find Alice's marriage date
→ Retrieve Bob's activities from that period
→ Graph traversal respects temporal proximity

31.6% → 79.7% on temporal reasoning benchmarks.

[link]
```

---

## LinkedIn

### Option 1 (Technical story)
```
I kept running into the same problem building agent memory: temporal queries that should work but don't.

User says in January: "Alice got married last June"

If you timestamp this as January (when stored):
→ "What happened to Alice in June 2024?" won't find it

If you timestamp it as June (when it happened):
→ "What did we discuss recently?" won't find it

Neither option works. You need both.

Hindsight tracks two temporal dimensions for each memory:

1. Occurrence interval (τₛ, τₑ): When the event actually happened
2. Mention timestamp (τₘ): When the fact was recorded

Now both queries work.

Beyond filtering, it builds temporal links in the knowledge graph:

weight = exp(−Δt / σₜ)

Events close in time stay strongly connected. This enables queries like "What was happening around Alice's promotion?" - the system finds the promotion, then spreads activation to temporally adjacent memories.

On LongMemEval's temporal reasoning category:
• Full-context baseline: 31.6%
• Hindsight: 79.7%

48-point improvement from tracking two timestamps instead of one.

Technical breakdown: [link]
```

### Option 2 (Problem-focused)
```
Single-timestamp memory creates an impossible trade-off.

Scenario: User tells agent in January 2025 that "Alice got married last June"

Option A: Timestamp as January 2025
→ Query "What happened in June 2024?" fails
→ The marriage happened in June, but memory says January

Option B: Timestamp as June 2024
→ Query "What did we discuss recently?" fails
→ Recent conversation is now 6 months old

Hindsight solves this by tracking both:
• Occurrence: when the event happened (June 2024)
• Mention: when you learned it (January 2025)

Add temporal graph links between memories (exponential decay by time distance), and you can answer:
• "What happened in June?" → filters by occurrence
• "What did we discuss yesterday?" → filters by mention
• "What was Bob doing when Alice got married?" → multi-hop temporal reasoning

This took temporal reasoning from 31.6% to 79.7% on benchmarks.

[link]
```
