# Social Media - Not all context is equal: hierarchical memory for AI agents

## Twitter/X (2-liners)

### Option 1 (Structural problem)
```
Flat context is why agents repeat themselves inconsistently. Every query re-synthesizes from scratch.

Hierarchical context: check curated knowledge first, consolidated patterns second, raw facts last. [link]
```

### Option 2 (The gap)
```
LangChain weights by recency. LlamaIndex merges chunks. MemGPT pages context.

None solve the canonical knowledge problem: which facts are authoritative vs which are just noise. [link]
```

### Option 3 (Scale problem)
```
RAG works fine for 100 documents. Breaks at 10,000 when your agent can't tell the difference between official policies and random observations.

Not all context deserves equal priority. [link]
```

### Option 4 (Belief formation)
```
Retrieval returns facts. Reasoning forms beliefs. Beliefs should evolve with evidence.

Most agent memory stops at retrieval. That's why they feel stateless. [link]
```

### Option 5 (Production reality)
```
Production agents need canonical answers for canonical questions and fresh synthesis for new queries.

Flat context gives you one or the other. Hierarchical context gives you both. [link]
```

---

## LinkedIn (2-liners)

### Option 1 (Canonical knowledge problem)
```
At 10,000+ memories, agents can't distinguish between official policies and random observations. Everything is just "similar embeddings."

Hierarchical context solves this: curated knowledge checks first, consolidated patterns second, raw facts last. [link]
```

### Option 2 (Consistency vs freshness)
```
Production agents need canonical answers for repeated questions and fresh synthesis for new queries. Flat context gives you one or the other.

Hierarchical memory gives you both. That's the difference between demos and production. [link]
```

### Option 3 (Belief formation)
```
Most agent memory stops at retrieval. Find relevant chunks, stuff into context, generate response. Stateless.

Hierarchical context enables persistent beliefs with evolving confidence. That's closer to learning than anything that just retrieves. [link]
```

### Option 4 (Scale breaks flat context)
```
RAG works fine at 100 documents. At scale, your agent re-synthesizes company policy from scattered meeting notes every time someone asks.

Not all context is equal. Hierarchy enforces that structurally. [link]
```

### Option 5 (What frameworks miss)
```
LangChain weights by recency. LlamaIndex merges chunks. MemGPT pages context. All valuable, none solve the canonical knowledge problem.

Which facts are authoritative vs which are just observations? That's where hierarchy matters. [link]
```

### Option 6 (Production requirement)
```
Agents that can't maintain consistent reasoning across queries get screenshot and called out. "Wait, you said something different yesterday."

Hierarchical context: mental models for canonical answers, observations for patterns, facts for freshness. [link]
```

---

## LinkedIn (Full version - if you want longer form)

```
I was building an AI project manager for Vectorize that answered planning and process questions.

Team member asks: "What's our sprint planning process?"

First answer: "We do two-week sprints with planning on Mondays and retros on Fridays"

Two hours later, same question.

Second answer: "Sprint planning happens at the start of each two-week cycle, typically Monday mornings, with retrospectives on Friday afternoons"

Same meaning. Different phrasing. The user notices. "Wait, which one is it?"

This isn't a hallucination. The facts are correct. But the LLM re-synthesizes from raw chunks every time, and synthesis isn't deterministic. You get variations.

For internal tools where users ask the same questions repeatedly, this breaks trust. For customer-facing agents, it's worse - users share screenshots showing your agent contradicting itself.

The fundamental issue: **RAG treats all context equally.** A carefully curated policy document and a casual Slack message from three months ago have the same priority. Just "similar embeddings."

You can't solve this with better prompts. "Be consistent" doesn't work when the agent has no memory of previous answers. You can't solve it with better retrieval - semantic search doesn't know which facts are canonical.

**Hindsight 0.4.0 solves this with a knowledge hierarchy:**

**Mental Models** (curated summaries) → **Observations** (auto-consolidated patterns) → **Raw Facts** (foundation)

When reflect runs, it checks sources in that priority order.

For "sprint planning process," I create a mental model with the canonical answer. Every query checks it first. Same answer every time. Consistency.

But ask about a new feature request that just came in? No mental model exists, so reflect uses recent facts. Freshness.

**The hierarchy gives you both.**

Mental models are curated - you create them when you need consistency. Observations are automatic - they emerge from accumulated facts about team members, patterns, entities.

Example from the Vectorize PM agent:

I created a mental model for "Feature Prioritization Framework" (user demand, technical complexity, strategic value). Every planning decision checks this first.

But I let observations handle team member work patterns. Store facts about how Sarah works, her strengths, blockers she hits, and Hindsight auto-generates observations. These update as sprints progress.

When asked "Should we prioritize the batch operations API or improved documentation next sprint?" the agent:
1. Checks mental model for prioritization criteria
2. Reviews observations about past feature launches and team capacity
3. Retrieves raw facts: 15 users asking for batch API, 8 for docs, team at 80% capacity
4. Applies mission ("ship what users need, balance speed with debt") and disposition (empathy: 4)
5. Synthesizes recommendation

The agent recommended documentation first - not because docs had more requests (they didn't), but because the hierarchy enabled reasoning across levels: team capacity, past patterns showing docs reduce support load, and empathy for both user frustration and team bandwidth.

**The provocative claim:** we're obsessed with retrieval quality when we should focus on belief formation.

Every RAG system talks about better embeddings, hybrid search, reranking. That's table stakes. The hard problem isn't finding relevant facts - it's deciding which facts are canonical, how they relate to accumulated beliefs, and how the agent's reasoning evolves over time.

Hindsight's hierarchical context with persistent opinions is closer to actual learning than anything that just retrieves and returns. When an agent can say "My confidence in this recommendation increased from 0.6 to 0.8 over three weeks because of these five new pieces of evidence," that's not retrieval. That's belief formation.

The benchmark numbers back this up: 91.4% on LongMemEval, outperforming full-context GPT-4o. But more interesting than the accuracy is the mechanism - the agent isn't just remembering better, it's reasoning with accumulated beliefs.

**The trade-offs:**

Mental models can go stale - you need to maintain them like documentation. Observations sometimes consolidate incorrectly (LLMs have opinions about what matters). The hierarchy adds indirection for simple queries.

But for production agents where users expect consistent answers and reasoning that matures over time, that's worth it.

Full breakdown with code examples, comparisons to LangChain/LlamaIndex/Letta, and the opinion evolution system: [link]
```
