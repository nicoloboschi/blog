+++
date = '2025-12-24T10:00:00+01:00'
draft = false
title = 'Background Operations: What Happens After retain()'
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Hindsight's retain() is fast and synchronous by default - memories are searchable immediately. For bulk ingestion scenarios, optional async mode lets you fire-and-forget while background workers handle batch processing, opinion formation, and observation regeneration.

---

## Sync by Default, Async When You Need It

By default, `retain()` runs synchronously and fast - the extraction pipeline is optimized for real-time use. Most conversations complete in hundreds of milliseconds, and memories are searchable immediately after the call returns.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Synchronous (default) - blocks until fully processed
client.retain(
    bank_id="my-agent",
    messages=[
        {"role": "user", "content": "Alice is moving from Google to Stripe next month."}
    ]
)
# Memories are now searchable immediately
```

The pipeline that runs on each retain:

1. **Fact extraction**: LLM parses content into discrete facts
2. **Entity identification**: Finds or creates entity nodes
3. **Graph connections**: Links facts to entities
4. **Opinion handling**: Checks if new facts affect existing opinions
5. **Observation regeneration**: Updates entity summaries if needed

For bulk ingestion scenarios where you don't need immediate availability, async mode lets you fire-and-forget:

```python
# Async - returns immediately, processing happens in background
client.retain(
    bank_id="my-agent",
    messages=[...],
    retain_async=True  # Optional async mode
)
```

## retain_batch: Bulk Ingestion

For high-volume scenarios - document ingestion, conversation history import, log processing - calling `retain()` in a loop is inefficient. `retain_batch()` groups multiple items into a single request.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Batch multiple items
items = [
    {
        "content": "Meeting notes from standup: discussed Q1 roadmap",
        "context": "team meeting",
        "timestamp": "2024-12-18T09:00:00Z"
    },
    {
        "content": "Alice mentioned she's leaving Google for Stripe",
        "context": "casual conversation",
        "timestamp": "2024-12-18T10:30:00Z"
    },
    {
        "content": "Reviewed pull request #432 - needs refactoring",
        "context": "code review",
        "timestamp": "2024-12-18T14:00:00Z"
    },
]

client.retain_batch(bank_id="my-agent", items=items, retain_async=True)
```

What changes with batching:

- **Single network roundtrip** instead of N calls
- **Grouped queue submission**: Items enter the processing queue together
- **Shared LLM context**: The extraction model can see relationships across items in the same batch

The last point matters. If three items mention "Alice," the extraction model processes them with that context, improving entity resolution accuracy.

In my experience, batch sizes between 10-50 items hit the sweet spot. Beyond 50, you start hitting context window limits on the extraction model.

## form_opinion: When Beliefs Are Born

Opinions don't come from `retain()`. They emerge during `reflect()` when the agent reasons to conclusions.

The flow:

```
reflect() called
    ↓
Recall retrieves relevant memories
    ↓
LLM reasons over evidence
    ↓
Response generated
    ↓
[Background] Opinion extraction runs
    ↓
New opinions stored with confidence scores
```

```python
# Facts about Redis exist in memory...

response = client.reflect(
    bank_id="tech-advisor",
    query="Should we use Redis for our caching layer?",
    context="building high-traffic API",
    budget="mid"
)

# Response returned to user immediately
print(response.text)

# Background: opinion forms
# "Redis is well-suited for high-traffic caching workloads" (confidence: 0.82)
```

The opinion formation happens asynchronously after the response is returned. A dedicated worker:

1. Parses the reflect response for conclusive statements
2. Classifies them as opinion-worthy (subjective, belief-expressing)
3. Assigns initial confidence based on evidence strength
4. Links opinions to relevant entities (Redis, in this case)
5. Stores in the opinion table

Initial confidence calculation considers:
- **Evidence density**: More supporting facts → higher confidence
- **Source reliability**: Recent facts weighted higher
- **Disposition**: High-skepticism banks start with lower confidence

Opinion formation runs as part of the `reflect()` call, so opinions are available in subsequent recalls.

## reinforce_opinion: Beliefs Evolve

When new facts arrive that relate to existing opinions, the reinforcement pipeline activates. This is the mechanism behind evolving beliefs.

```
retain() stores new fact
    ↓
[Background] Fact extraction
    ↓
Entity linking identifies related opinions
    ↓
Each related opinion enters reinforcement queue
    ↓
LLM classifies relationship:
    - REINFORCE: +confidence
    - WEAKEN: -confidence
    - CONTRADICT: -confidence (2x), revise text
    - NEUTRAL: no change
```

Concrete example:

```python
# Existing opinion: "Redis is excellent for caching" (0.85)

# New fact arrives
client.retain(
    bank_id="tech-advisor",
    content="Redis Labs changed licensing to SSPL. Many companies prohibit SSPL in production environments.",
    timestamp=datetime(2024, 3, 21)
)

# Background reinforcement process:
# 1. Extracts fact: "Redis uses SSPL license, problematic for some orgs"
# 2. Links to entity: Redis
# 3. Finds opinion: "Redis is excellent for caching" (0.85)
# 4. Classifies: CONTRADICT
# 5. Adjusts: confidence → 0.65
# 6. Revises text: "Redis is effective for caching but SSPL licensing may be problematic for some organizations"
```

The 2x multiplier on contradictions is deliberate. In my opinion, contradictory evidence should carry more weight than confirmatory evidence - it's the Popperian falsification principle applied to agent beliefs.

The reinforcement worker also handles **opinion merging**. If multiple opinions converge on the same topic, they can be consolidated:

```
Opinion A: "Python is good for ML" (0.75)
Opinion B: "Python excels at data science" (0.80)
                    ↓
Merged: "Python is well-suited for ML and data science workloads" (0.82)
```

## Observation Regeneration

Observations are synthesized entity profiles. They're not created during retain - they're regenerated when an entity accumulates enough facts.

The trigger conditions:

1. Entity has ≥ 5 facts (minimum for meaningful summary)
2. New facts added since last observation
3. Regeneration interval passed (prevents thrashing)

```
New fact stored about entity "Alice"
    ↓
Check: Alice fact count ≥ 5? Yes (now 8)
    ↓
Check: New facts since last observation? Yes (2 new)
    ↓
Check: Regeneration cooldown passed? Yes
    ↓
Queue observation regeneration for "Alice"
    ↓
[Worker] Collect all Alice facts
    ↓
[Worker] LLM synthesizes into coherent profile
    ↓
Store/update observation
```

```python
# After multiple retains about Alice...

results = client.recall(
    bank_id="my-agent",
    query="Tell me about Alice",
    include_entities=True,
    max_entity_tokens=500
)

# Observation returned:
# "Alice is a software engineer transitioning from Google to Stripe.
#  She specializes in infrastructure and is enthusiastic about payments
#  systems. Previously worked on distributed systems at Google."
```

The cooldown prevents excessive regeneration when facts arrive in bursts. If you `retain_batch` 20 items about Alice, you don't want 20 regeneration jobs.

## Monitoring Async Operations

When using async mode (`retain_async=True`), you can monitor processing status:

```python
status = client.get_bank_status(bank_id="my-agent")

print(f"Pending extractions: {status.pending_extractions}")
print(f"Pending opinions: {status.pending_opinion_jobs}")
print(f"Pending observations: {status.pending_observations}")
```

This is useful during bulk ingestion to track progress or wait for completion before running queries on the newly ingested data.

## When to Use Async Mode

Sync mode (the default) works well for most use cases - it's fast and gives you immediate consistency. But async mode shines in specific scenarios:

**Bulk ingestion**: When importing thousands of documents or conversation histories, async lets you submit everything quickly without waiting for each extraction.

**Fire-and-forget logging**: If you're logging agent interactions where immediate recall isn't needed, async reduces latency in the main request path.

**High-throughput pipelines**: When processing streams of data where you need maximum ingestion rate and can tolerate eventual consistency.

For typical agent loops where you retain a conversation and might recall from it in the same session, sync mode is the right choice - memories are available immediately.

---

Sync by default, async when you need it. For bulk ingestion use `retain_batch()` with `retain_async=True`. Opinion formation happens after `reflect()`, opinion reinforcement triggers when new facts relate to existing beliefs, and observation regeneration keeps entity profiles current. The pipeline is fast enough for real-time use, with optional async mode for high-throughput scenarios.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
