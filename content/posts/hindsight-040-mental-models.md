+++
date = '2026-02-03T10:00:00+01:00'
draft = false
title = 'Cache the reasoning, not the answer'
description = "Agents pay a synthesis tax re-deriving the same answers repeatedly. Mental models pre-compute consolidated knowledge for O(1) retrieval as memory evolves."
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Agents pay a synthesis tax-reasoning to the same answers hundreds of times. Semantic caching can't handle staleness or evidence chains. Mental models solve this: consolidate once, serve at O(1), auto-refresh when memory evolves. *Caching solves yesterday's answers. Mental models solve tomorrow's questions with yesterday's reasoning.*

---

## The Synthesis Tax

In December, we were running internal evals at Vectorize for a customer support agent built on Hindsight. The agent had memory of company policies, past support interactions, and resolution patterns. We ran it through a week of simulated support tickets to test recall quality and latency.

The eval results looked good - accurate answers, relevant context retrieval. But when I checked the token costs, something was off:

"What's your refund policy?" - Asked 400+ times per day
"How do I return something?" - Asked 300+ times per day
"Can I get my money back?" - Asked 200+ times per day

Same answer every time. Different phrasing, same reasoning path, same conclusion. The agent runs reflect: retrieves policy facts from memory, reasons over conditions, generates natural language response. Each query burns 1,200+ tokens and takes 2+ seconds.

The math: 480,000 tokens per day reasoning to the same conclusions. At scale pricing, that's real money. We were testing for quality, but uncovered a cost problem.

Then I realized: this isn't specific to support agents. It's any agent with long-term memory.

An AI assistant accumulated hundreds of facts about Alice over months - meeting patterns, communication preferences, project context, tool choices. Queries about that learned knowledge were just as expensive:

"How does Alice prefer to communicate?" - full reflect over dozens of observations
"What are Alice's meeting preferences?" - full reflect over dozens of facts
"Who should review this infrastructure change?" - full reflect over past team decisions

The agent learned patterns through observation:
- Alice prefers async communication, avoids morning meetings
- Deployment issues almost always involve the platform team
- Code review delays happen when Sarah is on-call

These patterns emerged from accumulated interactions. But every query triggers full reasoning over the same facts. Asked dozens of times per week. Tens of thousands of tokens per week re-deriving knowledge that was already synthesized.

## Why Naive Caching Fails

The obvious fix: cache by query string. But semantic variation kills this approach.

These should all return the same synthesized memory:
- "How does Alice prefer to communicate?"
- "What's Alice's communication style?"
- "Does Alice like meetings or async?"
- "How should I reach Alice?"

String matching won't catch that. Cache hit rate drops when users rephrase naturally.

## Why Semantic Caching Isn't Enough

Modern semantic caching solutions (Redis semantic cache, LangChain's cache layer, Momento) solve the semantic variation problem with embedding-based matching. Query comes in, compute embedding, check similarity against cached embeddings, return cached response if above threshold.

This works for static knowledge. But agent memory introduces three problems:

**1. Staleness with no semantics**: When Alice starts preferring video calls instead of Slack, the cache doesn't know which entries are now stale. You can set TTLs, but they're blind to actual knowledge changes. A cached answer from yesterday might be wrong today.

**2. No evidence chain**: The cached response is just text. You can't audit which memories produced it or when those memories were observed. If the agent says "Alice avoids morning meetings," you can't trace that back to the specific interactions that formed the pattern.

**3. Manual invalidation**: When the memory bank consolidates new observations, there's no automatic refresh trigger. You need external logic to detect related cache entries and invalidate them. Or you accept stale answers until TTL expires.

Semantic caching optimizes the retrieval problem. But memory agents have a synthesis problem - the same memories get reasoned over repeatedly, and that consolidated knowledge needs to evolve as new memories arrive.

## What About Prompt Caching or Distillation?

**Prompt caching** (e.g., Anthropic's prompt caching) reduces costs by caching the context prefix across calls. For agent memory, this means caching the retrieved facts. But you still pay for the synthesis - the LLM still reasons over those cached facts on every query and generates the response. You save on input tokens but not on output tokens or latency. The O(n) synthesis cost remains.

**Distillation** (fine-tuning a small model on your FAQ distribution) works for static knowledge domains. But agent memory evolves - new observations change what the agent knows about Alice's preferences or team patterns. You'd need continuous retraining as memory grows, which introduces its own infrastructure complexity and lag. And you lose evidence chains - the fine-tuned model can't explain which memories produced its answer.

Both techniques address cost, not the synthesis complexity or the staleness problem.

## Why CAG/RAG Don't Solve This

Context-Augmented Generation (CAG) and similar retrieval-based techniques solve a different problem. They're excellent at finding the right memories to reason over. But **retrieval is not synthesis**.

With CAG, the flow is:
1. Query comes in
2. Retrieve relevant memories (O(log n) with good indexing)
3. LLM reasons over those memories (O(n) - scales with memory count)
4. Synthesize response (O(n) - scales with retrieved facts)

Step 2 is optimized. But steps 3-4 happen on every query with the same computational cost.

For queries about Alice's communication preferences - asked dozens of times per week - CAG retrieves the same facts each time. But you still pay the synthesis tax: reasoning over dozens of observations, consolidating patterns, generating natural language.

The complexity: **O(n) per query** where n is the number of relevant memories.

What you want for recurring queries: **O(1) lookup** of pre-consolidated knowledge.

Using CAG for high-frequency memory queries is like re-reading your entire journal every time someone asks what you learned last month. The retrieval works great - you find the right pages quickly. But you still spend minutes reading and synthesizing when you already wrote a one-page summary.

## The Real Requirement

What you actually need for recurring memory queries:

**1. Semantic matching**: "How does Alice communicate?" and "What's Alice's preferred communication style?" should hit the same consolidated knowledge - no string matching, no threshold tuning.

**2. Curated and auditable**: The consolidation should be reviewable. You need to see which memories produced the answer and when they were observed. Black-box caches don't cut it.

**3. Automatic refresh with memory evolution**: When new observations arrive (Alice starts preferring video calls, team adopts new process), the consolidated knowledge updates automatically. Not manual invalidation. Not TTL guessing. Semantically-aware refresh triggers.

**4. O(1) retrieval complexity**: For recurring queries, you want constant-time lookup of pre-consolidated knowledge, not O(n) synthesis over the same memories repeatedly.

The pattern I kept seeing: 20% of memory queries account for 80% of traffic. Those high-traffic queries pull from stable, consolidated knowledge that doesn't need fresh synthesis every time. But the remaining 80% of long-tail queries still need dynamic reasoning over raw memories.

You need a layer above automatic consolidation that pre-computes answers for recurring memory queries while falling back to full reasoning for everything else.

## Pre-Computed Memory Consolidation

Mental models solve this by letting you define source queries and pre-compute answers by reasoning over accumulated memories once. You create a mental model with a query like "What are Alice's communication preferences?" - the system runs reflect over all relevant memories, synthesizes the answer, stores it. Future queries that are semantically similar retrieve the pre-computed consolidation instantly.

No LLM call. No re-synthesis from raw facts. No variability. Just a lookup.

The API is straightforward:

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Create a mental model from accumulated memories
result = client.create_mental_model(
    bank_id="alice-assistant",
    name="Alice Communication Style",
    source_query="How does Alice prefer to communicate and collaborate?",
    tags=["preferences", "communication"]
)
```

This triggers a reflect operation over Alice's accumulated memories. The system retrieves relevant facts - meeting declines, Slack response patterns, calendar preferences, past feedback about communication - reasons over them once, and stores the synthesized knowledge.

Now when queries come in like "How should I reach Alice?" or "Does Alice prefer meetings?" the mental model is checked first. The consolidated memory is returned instantly.

The `name` field is just a human-readable identifier. The actual matching happens at the semantic level - similar queries to the source query will retrieve this mental model, so you don't need exact string matches.

You can control the synthesis length with the `max_tokens` parameter:

```python
# Concise summary for quick lookups
result = client.create_mental_model(
    bank_id="alice-assistant",
    name="Alice Communication Style - Brief",
    source_query="How does Alice prefer to communicate?",
    max_tokens=150  # Short, focused answer
)

# Detailed consolidation for complex patterns
result = client.create_mental_model(
    bank_id="team-dynamics",
    name="Engineering Team Decision Process",
    source_query="How does the engineering team make technical decisions?",
    max_tokens=800  # Longer, comprehensive synthesis
)
```

This is useful when you need concise summaries for UI constraints or token budgets, versus detailed consolidations for complex knowledge patterns.

## Priority Hierarchy: Mental Models First

During reflect operations, Hindsight checks memory sources in priority order:

**Mental Models → Observations → Raw Facts**

Mental models are checked first. If a relevant mental model exists for the query, its pre-consolidated knowledge is used directly. If not, the system falls back to observations (automatically synthesized entity summaries from accumulated memories), and finally to raw facts for full LLM reasoning over individual memories.

This hierarchy is deliberate. Mental models represent pre-computed consolidations you've explicitly created - the highest level of synthesized knowledge. Observations are automatically consolidated patterns that emerge from memories. Raw facts are individual memories requiring the most processing.

This layering is what makes agent memory practical at scale. You pre-compute mental models for the 20% of memory queries that account for 80% of your traffic. The remaining 80% of long-tail queries still get handled by automatic consolidation and dynamic reasoning over raw memories.

## Auto-Refresh: Memory Evolution

Mental models can become stale as new memories accumulate. If your consolidated knowledge about "Alice's communication preferences" was formed before she changed roles and started managing a distributed team, it needs updating.

The solution: automatic refresh triggers.

```python
client.update_mental_model(
    bank_id="alice-assistant",
    mental_model_id=mental_model_id,
    trigger={"refresh_after_consolidation": True}
)
```

With `refresh_after_consolidation: true`, the mental model automatically refreshes whenever observations are updated. This happens in the background - the agent continues using the existing consolidated memory until the refresh completes with updated knowledge.

When to enable auto-refresh:
- **User preferences**: Communication styles, work patterns that evolve
- **Team dynamics**: Learned patterns about collaboration, blockers, processes
- **Behavioral insights**: Habits and preferences that shift over time

When to disable it:
- **Historical summaries**: "What happened in Q1" shouldn't change
- **Milestone consolidations**: Specific project learnings from a point in time
- **Reviewed insights**: Patterns you've manually verified and want stable

You can also manually refresh at any time:

```python
client.refresh_mental_model(
    bank_id="my-agent",
    mental_model_id=mental_model_id
)
```

This re-runs the source query and updates the content. The old version remains available until the refresh completes, preventing gaps.

## Semantic Cache vs Mental Models

| Capability | Semantic Cache (e.g., Redis, Momento) | Mental Models |
|------------|----------------------------------|---------------|
| **Semantic matching** | ✅ Embedding similarity | ✅ Embedding similarity |
| **Staleness handling** | ❌ TTL-based, blind to knowledge changes | ✅ Refresh triggers tied to memory consolidation |
| **Evidence chain** | ❌ Cached text only, no traceability | ✅ Full chain to source memories with timestamps |
| **Manual curation** | ❌ Auto-cached on first query | ✅ Explicitly defined source queries |
| **Refresh semantics** | ❌ Manual invalidation or TTL expiry | ✅ Automatic refresh when related observations update |
| **Works with evolving knowledge** | ❌ Static snapshots | ✅ Tied to memory consolidation pipeline |
| **Complexity** | O(1) lookup after cache hit | O(1) lookup for pre-computed queries |
| **Best for** | Static knowledge, API responses | Evolving agent memory, learned patterns |

The key difference: semantic caching optimizes **yesterday's answers**. Mental models let you serve **tomorrow's questions with yesterday's reasoning** - the consolidation evolves as memory grows.

## When to Use Mental Models

Mental models are not a replacement for observations or raw facts. They're a tool for specific scenarios where consolidated memory gets queried repeatedly.

**Good fits for mental models:**

1. **Recurring memory queries**: "How does Alice work?" asked 50+ times per week
2. **Consolidated user knowledge**: Patterns learned from hundreds of interactions
3. **High-traffic lookups**: Pre-computing saves cost when querying learned knowledge frequently
4. **Stable patterns**: Team dynamics, user preferences, learned behaviors that don't change daily

**Let observations handle:**

1. **Emerging patterns**: Things you're still learning about a user or context
2. **Long-tail memory queries**: Rarely asked, not worth pre-computing
3. **Contextual reasoning**: Questions needing fresh synthesis with recent context
4. **Exploratory answers**: When you want the system to reason over raw memories dynamically

The mental model vs observation decision comes down to frequency vs freshness. If you're answering the same memory query dozens of times, pre-compute it. If it's asked rarely or needs dynamic reasoning, let observations handle it.

## Performance and Cost Implications

Mental models bypass LLM synthesis during reflect. That has concrete implications for agents with long-term memory:

**Latency**: Retrieving a mental model is a simple lookup - milliseconds instead of seconds. For agents querying learned patterns frequently, this matters. An assistant answering dozens of questions about user preferences per day saves meaningful time.

**Token costs**: Each reflect call reasoning over accumulated memories burns tokens. Pre-computing via mental models means you pay once to consolidate knowledge, then serve infinite queries at near-zero cost.

**Consistency**: LLM synthesis has inherent variability. Mental models eliminate that - the same memory query returns the exact same consolidated knowledge every time. For stable learned patterns, this consistency matters.

The tradeoff: storage overhead and refresh compute. Each mental model stores consolidated knowledge plus metadata about source memories. Automatic refresh triggers still run LLM calls when memories evolve. But for high-frequency memory queries, the amortized cost is significantly lower than repeated synthesis.

---

For the personal assistant: I curated mental models covering frequently queried learned knowledge about Alice - communication preferences, work patterns, project context, tool choices. Token usage on those paths dropped significantly. Latency went from seconds to milliseconds. Responses became consistent - the same memory query returns the same consolidated knowledge every time.

The AI PM agent: Mental models for recurring queries about learned team patterns - who handles what, common blockers, decision processes. Major reduction in token costs on high-traffic memory queries. Auto-refresh keeps them current as new interactions accumulate and patterns evolve.

The pattern is clear: pre-compute consolidated knowledge for the 20% of memory queries that account for 80% of your traffic. Let observations handle long-tail reasoning over raw memories.

**Caching solves yesterday's answers. Mental models solve tomorrow's questions with yesterday's reasoning.**

## Implementation Notes

Some practical details from working with mental models:

**Tagging for organization**: Use tags to group related mental models. `tags=["preferences", "user-alice"]` lets you filter when listing or managing mental models at scale.

**Source query design**: The source query should be representative of how queries will actually come in. If people ask "How does Alice work?" and "What's Alice's style?" but your source query is "Describe Alice's professional attributes," the matching might be weaker. I test source queries by running them manually first.

**Refresh concurrency**: The system limits concurrent mental model refreshes (default: 8). If you have hundreds of mental models all triggering refresh when observations update, they'll queue. For production deployments, tune `HINDSIGHT_API_MENTAL_MODEL_REFRESH_CONCURRENCY` based on your LLM rate limits.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
