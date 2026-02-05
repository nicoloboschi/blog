+++
date = '2026-02-05T10:00:00+01:00'
draft = false
title = 'Not all context is equal: hierarchical memory for AI agents'
tags = ["AI", "agents", "memory", "hindsight", "LLM", "reflect"]
+++

**TL;DR**: Not all context is equal. A curated company policy shouldn't have the same priority as a random Slack message from three months ago. Hindsight's three-tier hierarchy - mental models, observations, raw facts - ensures agents check canonical knowledge first. This solves RAG's consistency problem but requires maintaining mental models.

---

## The Consistency Problem

I was building an AI project manager for Vectorize that answered planning and process questions. Standard RAG setup: embed everything, retrieve relevant chunks, stuff into context, generate response.

Team member asks: "What's our sprint planning process?"

First answer: "We do two-week sprints with planning on Mondays and retros on Fridays"

Same person, two hours later, same question.

Second answer: "Sprint planning happens at the start of each two-week cycle, typically Monday mornings, with retrospectives on Friday afternoons"

Same meaning. Different phrasing. The user notices. "Wait, which one is it?"

This isn't a hallucination problem. The facts are correct. But the LLM re-synthesizes from raw chunks every time, and synthesis isn't deterministic. You get variations.

For internal tools where users ask the same questions repeatedly, this breaks trust. For customer-facing agents, it's worse - users share screenshots showing your agent contradicting itself.

The fundamental issue: RAG treats all context equally. A carefully curated policy document from yesterday and a casual Slack message from three months ago have the same priority. Just "similar embeddings." The LLM has to figure out what matters every single time.

You can't solve this with better prompts. "Be consistent" doesn't work when the agent has no memory of previous answers. You can't solve it with better retrieval - semantic search doesn't know which facts are canonical.

This is a structural problem, not a prompt engineering problem.

## How Others Handle This

Before explaining Hindsight's approach, let's look at how existing frameworks tackle consistency:

**LangChain** uses [multi-factor prioritization](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) combining semantic relevance, time decay for recency, and importance flags. This helps, but it's still flat - all memories are fundamentally the same type, just with different scores. No structural distinction between canonical knowledge and raw observations.

**LlamaIndex** offers [hierarchical retrieval with auto-merging](https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/) where leaf nodes recursively merge into parent nodes. But this is document chunking hierarchy (small chunks roll up to big chunks), not knowledge abstraction. It helps with context but doesn't solve the "which facts are canonical" problem.

**Letta/MemGPT** introduced a [two-tier memory architecture](https://docs.letta.com/guides/agents/memory/) inspired by operating systems: in-context memory (RAM) and out-of-context archival memory (disk). This solves the context window problem through virtual memory paging, but it's about what fits in context, not which knowledge takes priority during reasoning.

None of these systems structurally distinguish between curated knowledge ("our sprint planning process") and emergent patterns ("Sarah finishes tasks early consistently") and raw facts ("Sarah mentioned she's blocked on API integration"). They handle memory management but not knowledge hierarchy.

## The Hierarchy

Hindsight 0.4.0 introduced a knowledge hierarchy to solve this:

**Mental Models → Observations → Raw Facts**

When reflect runs, it checks sources in that priority order.

**Mental models** are user-curated summaries for queries that need consistent answers. You create them explicitly. "Sprint planning process" gets a mental model, and every query about sprint planning checks it first. Same answer every time.

**Observations** are automatically synthesized entity profiles. Accumulate five facts about a team member's work patterns? Hindsight generates an observation summarizing what it knows. These sit below mental models but above raw facts.

**Raw facts** are the foundation - world facts and experiences extracted during retain(). Detail preservation.

Think about how you actually organize knowledge. Sprint planning process? You have a canonical answer in your head. You don't re-derive it from scattered Slack messages. That's a mental model.

Patterns about team members? You've noticed Sarah consistently finishes tasks early and Alex needs more detailed specs. That's an observation - consolidated from multiple sprints.

Specific facts? Sarah mentioned she's blocked on the API integration. That's a raw fact.

The hierarchy mirrors this. Canonical knowledge at the top, emergent patterns in the middle, raw detail at the bottom.

```
┌─────────────────────────────────────────┐
│ Query: "What's our sprint planning process?" │
└──────────────┬──────────────────────────┘
               │
               ▼
         ┌───────────┐
         │  MENTAL   │ ◄─── Check first
         │  MODELS   │      (Curated summaries)
         └─────┬─────┘
               │ Found? Return with consistency
               │ Not found? ↓
         ┌─────▼─────┐
         │OBSERVATIONS│ ◄─── Check second
         │           │      (Auto-consolidated)
         └─────┬─────┘
               │ Found? Use consolidated view
               │ Not found? ↓
         ┌─────▼─────┐
         │ RAW FACTS │ ◄─── Check last
         │           │      (Foundation)
         └─────┬─────┘
               │
               ▼
      Apply disposition traits
      Synthesize response
      Form/update opinions
```

The hierarchy fundamentally changes what the agent treats as canonical during reasoning.

## Performance: The Numbers

According to [benchmark data independently reproduced](https://github.com/vectorize-io/hindsight) by Virginia Tech and The Washington Post, Hindsight with an open-source 20B model achieved 83.6% overall accuracy (up from 39% baseline) and outperformed full-context GPT-4o on long-horizon conversational memory benchmarks. Scaling further pushed Hindsight to **91.4% on LongMemEval** and **89.61% on LoCoMo** (versus 75.78% for the strongest prior open system).

These benchmarks test long-term memory accuracy, not consistency specifically. But the architecture that enables accuracy - structured knowledge with priority ordering - is the same one that provides consistency. When the system knows which knowledge is canonical, it returns both accurate and consistent answers.

## How Reflect Uses the Hierarchy

Here's the key difference from standard RAG:

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Standard recall: returns raw memories, flat priority
results = client.recall(
    bank_id="vectorize-pm",
    query="What's Sarah working on?",
    budget="high"
)

for r in results.results:
    print(f"[{r.type}] {r.text}")
# [world] Sarah is finishing the mental models feature
# [world] Sarah typically completes tasks ahead of schedule
# [experience] Discussed Sarah's bandwidth in standup yesterday

# Reflect: hierarchical reasoning
answer = client.reflect(
    bank_id="vectorize-pm",
    query="Can Sarah take on the batch operations API next sprint?",
    context="sprint planning, considering team capacity",
    budget="high"
)

print(answer.text)
# "Sarah could be a good fit for the batch API work. She's wrapping up
# mental models and consistently finishes early. However, the batch API
# is a larger scope than her typical tasks. I'd verify she has enough
# context on our API architecture and pair her with Mike initially."
```

Reflect doesn't only retrieve - it reasons through the hierarchy:

1. Check mental models (are there any curated summaries about task assignment criteria?)
2. Check observations (what patterns exist about Sarah's work style and capacity?)
3. Pull raw facts if needed (specific current tasks, stated bandwidth)
4. Apply personality traits (mission, directives, disposition)
5. Synthesize response

The hierarchy ensures curated knowledge takes priority over random facts. That's what gives you consistency.

## Opinion Evolution: The Underrated Feature

Here's what makes this more than just layered caching: reflect creates **persistent opinions** that evolve.

When the agent reasons to a conclusion, that conclusion gets stored as an opinion with a confidence score. Future reflects can reference and update that opinion.

Example over three months:

**Week 1:** Reflect on "Should we use PostgreSQL for this project?"
- Checks mental model about database selection criteria
- Reviews facts about project requirements
- Forms opinion: "PostgreSQL is well-suited" (confidence: 0.8)
- Opinion gets stored

**Week 3:** Retain new fact: "The team lacks PostgreSQL expertise"
- System updates opinion: "PostgreSQL is technically suitable but training costs matter" (confidence: 0.6)

**Week 5:** Reflect again: "Should we use PostgreSQL?"
- Checks mental model (criteria still valid)
- References existing opinion (confidence: 0.6)
- Considers new evidence
- Updates: "PostgreSQL fits the use case but we need to factor in ramp-up time" (confidence: 0.65)

**Month 3:** After team training completes
- New facts about team gaining PostgreSQL competence
- Opinion confidence rises: "PostgreSQL is the right choice and team is ready" (confidence: 0.85)

This is fundamentally different from stateless RAG. The agent builds beliefs that mature with evidence. Confidence scores track how certain the agent is, and contradictory evidence lowers confidence while supporting evidence raises it.

What does this look like after three months of operation? Imagine an agent that's accumulated 50 opinions across different technical decisions, team dynamics, and project patterns. When you ask "Should we adopt GraphQL for the new API?", the agent doesn't just retrieve facts about GraphQL. It references its opinion about API complexity (confidence: 0.75, formed from past migrations), its opinion about team learning capacity (confidence: 0.8, updated weekly), and its opinion about timeline pressure (confidence: 0.7, evolving with project status).

The agent's reasoning becomes richer over time because it's not starting from scratch with each query. It has accumulated beliefs - some strong, some weak - that guide how it interprets new evidence. An agent on day one might say "GraphQL could work." An agent three months later, with 50 evolved opinions, says "GraphQL fits our API needs, but given our current timeline pressure (confidence: 0.7) and the team's learning curve on our last major change (confidence: 0.8), we should phase it in gradually."

That's the longitudinal payoff. The agent doesn't just remember facts - it develops judgment.

## Mental Models vs Observations: When to Use Each

Example: feature prioritization at Vectorize.

I created a mental model for "Feature Prioritization Framework" with explicit criteria (user demand, technical complexity, strategic value). Every planning decision checks this first. Consistency.

But I let observations handle team member work patterns. Store facts about how each person works, their strengths, blockers they hit, and Hindsight generates observations automatically. These update as sprints progress.

Mental models for principles that shouldn't change. Observations for knowledge that should evolve with evidence.

## The Trade-offs

The hierarchy isn't free. Three problems I've hit:

**Mental models can go stale.** If you create a mental model for sprint planning process and the process changes, you need to manually update it. There's no automatic invalidation. The agent will keep using the old mental model until you fix it.

Solution: treat mental models like documentation. They need maintenance. If knowledge is rapidly evolving, use observations instead.

**Observations consolidate incorrectly sometimes.** I've seen cases where Hindsight generates an observation that emphasizes the wrong aspects of an entity. Five facts about a team member's work patterns, but the observation focuses on the least important one.

This happens because observation generation is an LLM call, and LLMs have opinions about what matters. If the generated observation is wrong, you can't easily fix it - observations are auto-generated.

Workaround: if an entity or pattern is critical, create a mental model instead. More control, less automatic.

**The hierarchy adds indirection.** Simple queries now check three layers before returning an answer. For queries where you know the answer is in raw facts, this feels like overhead. Reflect has a `budget` parameter to control search depth, but you're still paying for the hierarchy check.

In my opinion, these trade-offs are worth it for production agents where consistency matters. But if you're building something exploratory where fresh answers matter more than consistency, flat RAG might be simpler.

## Shaping How the Hierarchy Gets Interpreted

Three settings control how reflect interprets the hierarchy: mission, directives, and disposition.

**Mission** tells the agent what knowledge to prioritize:
```python
client.create_bank(
    bank_id="vectorize-pm",
    mission="Ship high-quality features that users actually need, balance speed with technical debt"
)
```

**Directives** are hard rules that can't be violated:
- "Never recommend specific stocks"
- "Always cite sources when making claims"

**Disposition** shapes interpretation style:
```python
disposition={
    "skepticism": 4,   # 1-5: high skepticism
    "literalism": 3,   # 1-5: balanced interpretation
    "empathy": 3       # 1-5: consider team impact
}
```

Same hierarchy, different disposition → different conclusions. High skepticism emphasizes risks. Low skepticism emphasizes opportunities.

This is how you get personality without prompt engineering. The hierarchy provides structure. Disposition provides style.

## Practical Example

Building an AI project manager for Vectorize:

```python
from hindsight_client import Hindsight
from datetime import datetime

client = Hindsight(base_url="http://localhost:8888")

# Create bank with personality
client.create_bank(
    bank_id="vectorize-pm",
    background="Project manager at Vectorize with experience shipping developer tools",
    mission="Ship high-quality features that users actually need, balance speed with technical debt",
    disposition={
        "skepticism": 3,
        "literalism": 3,
        "empathy": 4
    }
)

# Store facts about team and current sprint
client.retain(
    bank_id="vectorize-pm",
    content="Engineering team is at 80% capacity. Sarah and Alex are wrapping up the mental models feature. Mike is working on observation auto-refresh.",
    context="sprint capacity",
    timestamp=datetime.now()
)

client.retain(
    bank_id="vectorize-pm",
    content="Customer requests: 15 users asking for batch operations API, 8 users asking for better docs on opinion evolution, 3 users asking for GraphQL support.",
    context="feature requests",
    timestamp=datetime.now()
)

# Ask for prioritization advice
answer = client.reflect(
    bank_id="vectorize-pm",
    query="Should we prioritize the batch operations API or improved documentation next sprint?",
    context="sprint planning for next two weeks",
    budget="high"
)

print(answer.text)
```

What happens:
1. Reflect searches for mental models about prioritization criteria (if any exist)
2. Checks observations about past feature launches and team capacity patterns
3. Retrieves raw facts about current capacity and customer requests
4. Applies mission ("ship what users need, balance speed with debt") and disposition (empathy: 4)
5. Synthesizes recommendation

Output will likely recommend documentation first:
- Facts show 15 batch API requests vs 8 docs requests, but team at 80% capacity
- Mission balances user needs with sustainable shipping
- High empathy disposition considers both user frustration and team bandwidth
- Observation from past sprints: documentation has higher ROI for reducing support load

Same agent, different capacity or request ratios → different recommendation. Adaptive reasoning grounded in consistent principles.

## When to Use Recall vs Reflect

Use **recall** when you need raw memories for your own prompt building. You're constructing context, filtering by memory types, or feeding another LLM. You control the reasoning.

Use **reflect** when you want hierarchical reasoning with personality. The agent checks mental models first, falls back to observations, applies disposition traits, and synthesizes a response.

I prefer recall for complex multi-step workflows where I need control. I prefer reflect for consistent, personality-driven responses.

## The Provocative Claim

Here's what I think the industry gets wrong: we're obsessed with retrieval quality when we should be focused on belief formation.

Every RAG system talks about better embeddings, hybrid search, reranking. That's table stakes. The hard problem isn't finding relevant facts - it's deciding which facts are canonical, how they relate to accumulated beliefs, and how the agent's reasoning should evolve over time.

Hindsight's hierarchical context with persistent opinions is, in my opinion, closer to actual learning than anything that just retrieves and returns. When an agent can say "My confidence in this recommendation has increased from 0.6 to 0.8 over three weeks because of these five new pieces of evidence," that's not retrieval. That's belief formation.

The benchmark numbers back this up: [91.4% on LongMemEval](https://github.com/vectorize-io/hindsight), outperforming full-context GPT-4o. But more interesting than the accuracy is the mechanism - the agent isn't just remembering better, it's reasoning with accumulated beliefs.

Is this actual learning? I think it's closer than stateless RAG. The agent's outputs change not just because new facts arrived, but because its beliefs evolved in response to evidence. That's the difference between a database with a search interface and a system that forms judgment.

---

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight) | [Benchmarks](https://github.com/vectorize-io/hindsight) | [RAG consistency research](https://arxiv.org/abs/2510.04392) | [LangChain](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) | [LlamaIndex](https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/) | [Letta/MemGPT](https://docs.letta.com/guides/agents/memory/)
