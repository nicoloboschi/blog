+++
date = '2025-12-23T10:00:00+01:00'
draft = false
title = 'Temporal reasoning: "when it happened" vs "when you learned it"'
tags = ["AI", "agents", "memory", "hindsight", "retrieval"]
+++

**TL;DR**: Most memory systems track only when information was stored. Hindsight tracks two temporal dimensions - when events occurred and when you learned about them. This enables queries like "what did I learn last week about events from last month?".

---

## The Single Timestamp Problem

Standard memory systems attach one timestamp to each memory: when it was stored. This creates an impossible trade-off.

Consider this scenario:

```
January 15, 2025: User tells agent "Alice got married last June"
```

If you timestamp this as January 2025 (when stored), the query "What happened to Alice in June 2024?" won't find it. The memory's timestamp doesn't match the query's time range.

If you timestamp it as June 2024 (when it happened), the query "What did I tell you last week?" won't find it either. Recent information becomes unsearchable by recency.

Neither option works. You need both.

## Two Temporal Dimensions

Hindsight tracks each memory with distinct temporal metadata:

1. **Occurrence interval (τₛ, τₑ)**: When the event actually happened
2. **Mention timestamp (τₘ)**: When the fact was recorded

For "Alice got married last June" stored in January:
- Occurrence: June 2024
- Mention: January 15, 2025

Now both queries work:
- "What happened to Alice in June 2024?" → Matches occurrence interval
- "What did we discuss recently?" → Matches mention timestamp

Some facts don't have occurrence times. "Alice prefers coffee over tea" is a general preference - no specific date when it "happened". Hindsight handles this by leaving the occurrence interval null while still tracking when you learned it.

## Temporal Search in TEMPR

Hindsight's retrieval system (TEMPR) runs four strategies in parallel: semantic, keyword, graph, and temporal. The temporal strategy parses natural language time expressions and filters memories accordingly.

The parsing works in two stages:

1. **Rule-based normalization** for common patterns: "yesterday", "last week", "June 2024", "Q3 2023"
2. **Seq2seq fallback** for complex expressions: "the spring before Alice joined Google", "around when we launched the product"

Once parsed into a time interval, the search filters memories whose occurrence periods overlap that range. Memories temporally closer to the query's timeframe score higher.

Example queries and what they match:

| Query | Temporal Parse | Filters By |
|-------|----------------|------------|
| "What happened last spring?" | March-May 2024 | Occurrence |
| "What did I tell you yesterday?" | Dec 22, 2025 | Mention |
| "Events from Q3 before we discussed them" | July-Sep + mention after | Both |

## Temporal Links in the Memory Graph

Beyond search filtering, Hindsight builds temporal connections between memories in its knowledge graph. Memories close in time get weighted edges:

```
weight = exp(−Δt / σₜ)
```

Where Δt is the time difference and σₜ controls decay rate. Events a day apart stay strongly connected. Events months apart have weak links.

This enables graph traversal that respects temporal proximity. When you ask "What was happening around Alice's promotion?", the system finds the promotion event, then spreads activation to temporally adjacent memories - team changes, project launches, conversations from that period.

Causal reasoning benefits too. "What led to the product delay?" requires finding events *before* the delay and connected to it. Temporal edges combined with causal edges let the graph retrieval surface the right context.

## Practical Impact

The dual-timestamp approach solves several real problems I've encountered building agent memory:

**Historical accuracy with recent relevance**: When a user updates information ("Actually, Alice left Google in March, not April"), the new fact has a fresh mention timestamp but corrects a past occurrence. Queries about recent conversations find the correction; queries about March events find the updated date.

**Time-scoped knowledge bases**: In a support agent scenario, you might retain documentation updates with their publish dates (occurrence) while tracking when each was ingested (mention). "What changed in v2.3?" uses occurrence; "What docs did we add this week?" uses mention.

**Temporal consistency in multi-hop queries**: For "What was Bob working on when Alice joined?", the system needs to find Alice's join date, then retrieve Bob's activities from that period. Without occurrence tracking, this requires the LLM to do temporal math on free-text dates - unreliable at best.

## Code Example

Temporal reasoning is automatic - you don't configure it explicitly. When you store and query memories, Hindsight handles the temporal dimensions:

```python
from hindsight_client import Hindsight

with Hindsight(base_url="http://localhost:8888") as client:
    # Store with explicit occurrence metadata (optional)
    client.retain(
        bank_id="my-bank",
        messages=[
            {
                "role": "user",
                "content": "Alice got promoted to Senior Engineer last March"
            }
        ],
    )

    # Query by occurrence time - finds March events
    results = client.recall(
        bank_id="my-bank",
        query="What happened with Alice in March 2024?",
    )

    # Query by mention time - finds recently discussed topics
    results = client.recall(
        bank_id="my-bank",
        query="What did we discuss in our last conversation?",
    )

    # Complex temporal reasoning
    results = client.recall(
        bank_id="my-bank",
        query="What was the team working on before Alice's promotion?",
    )
```

The temporal strategy runs alongside semantic, keyword, and graph search. Results matching multiple strategies rank higher through RRF fusion.

---

Two timestamps instead of one. It's a simple change in data model that enables an entire class of queries that single-timestamp systems can't handle. In my experience, temporal questions are among the most common in conversational memory - and the most frustrating when they fail.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
