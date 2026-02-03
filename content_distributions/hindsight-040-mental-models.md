# Social Media - Cache the reasoning, not the answer

## Twitter/X

### Option 1 (480k tokens/day)
```
480,000 tokens per day.

Same questions. Same reasoning. Same answers.

That's what we found running evals on a support agent in December.

The agent had memory. It just kept re-deriving the same knowledge on every query.

[link]
```

### Option 2 (Synthesis tax)
```
Your agent learned Alice prefers async through 40 interactions.

Every time you ask "How does Alice work?" it reasons over those 40 facts again.

50 queries/week = 50x the synthesis cost.

You're not paying for retrieval. You're paying for repeated reasoning.

[link]
```

### Option 3 (The cache problem)
```
Semantic caching doesn't solve the agent memory problem.

When Alice changes her communication style, the cache doesn't know what's stale.

When the agent says "Alice avoids meetings," you can't trace which memories produced that.

TTLs are blind. Evidence chains don't exist.

[link]
```

### Option 4 (O(n) every query)
```
CAG/RAG optimize retrieval to O(log n).

But synthesis is still O(n).

Every query: reason over memories, synthesize response.

For recurring questions about stable patterns, you're paying O(n) when you want O(1).

[link]
```

### Option 5 (Prompt caching)
```
"Use prompt caching"

That caches the input (retrieved memories).

You still synthesize the output.
You still burn LLM tokens.
You still wait seconds.

Cache the reasoning, not the answer.

[link]
```

### Option 6 (The punchline)
```
Caching solves yesterday's answers.

What you need: tomorrow's questions answered with yesterday's reasoning.

[link]
```

---

## LinkedIn

### Option 1 (The Vectorize eval story)
```
In December, we were running internal evals at Vectorize for a customer support agent built on Hindsight.

The agent had memory of company policies, past support interactions, resolution patterns. We ran it through a week of simulated support tickets to test recall quality and latency.

Eval results looked good - accurate answers, relevant retrieval. But when I checked token costs, something was wrong.

480,000 tokens per day reasoning to the same conclusions:
- "What's your refund policy?" - 400+ times/day
- "How do I return something?" - 300+ times/day
- "Can I get my money back?" - 200+ times/day

Each query: full reflect operation. Retrieve policy facts from memory, reason over conditions, generate natural language. 1,200+ tokens, 2+ seconds. Same answer every time.

We were testing for quality, but uncovered a cost problem.

Then I realized: this isn't specific to support agents. It's any agent with long-term memory.

An AI assistant with months of accumulated memories about Alice - meeting patterns, communication preferences, project context. Every query about "How does Alice work?" triggers full reasoning over dozens of observations. Tens of thousands of tokens per week re-deriving knowledge that was already synthesized.

That's the synthesis tax. Agents pay it every time they reason to the same answer.

Mental models solve this: consolidate once, serve at O(1), with automatic refresh when memory evolves.

You define a source query. System runs reflect over accumulated memories once, stores the synthesized knowledge. Future queries retrieve instantly - no LLM call, no re-synthesis, no variability.

Auto-refresh triggers keep them current: when observations update, mental models regenerate in the background.

For our support agent: mental models for ~15 recurring questions. Token costs dropped significantly. Latency went from seconds to milliseconds. Responses became deterministic.

Caching solves yesterday's answers. Mental models solve tomorrow's questions with yesterday's reasoning.

[link]
```

### Option 2 (Semantic caching critique)
```
"Why not just use semantic caching?"

Redis semantic cache, Momento, LangChain - these solve semantic variation with embedding-based matching. That's useful.

But agent memory introduces problems they can't handle:

Staleness with no semantics: When Alice starts managing a distributed team and her communication preferences change, the cache doesn't know which entries are now stale. TTLs are blind to actual knowledge changes.

No evidence chain: Cached response is just text. You can't audit which memories produced it or when they were observed. Black box.

Manual invalidation: When the memory bank consolidates new observations, there's no automatic refresh trigger. You need external logic to detect related cache entries. Or accept stale answers.

These aren't cache problems. They're synthesis problems.

Mental models solve this by tying pre-computed consolidations to the memory consolidation pipeline. Auto-refresh when observations update. Full evidence chains to source memories with timestamps. Semantic matching without manual threshold tuning.

We tested this at Vectorize. Support agent with recurring policy questions, AI assistant with learned user preferences, AI PM with team patterns.

Token costs dropped 70-85% on high-frequency memory queries. Latency: seconds to milliseconds. Responses: consistent and auditable.

The pattern is clear: pre-compute consolidated knowledge for the 20% of memory queries that are 80% of your traffic. Let observations handle long-tail reasoning over raw memories.

Cache the reasoning, not the answer.

[link]
```

### Option 3 (Shorter, O(n) vs O(1))
```
Agent memory has a synthesis tax.

Query: "How does Alice prefer to communicate?"

With CAG/RAG:
1. Retrieve relevant memories (O(log n) - fast)
2. Reason over them (O(n) - scales with memory count)
3. Synthesize response (O(n))

Retrieval is optimized. Synthesis still happens every query.

Ask 50 times per week about Alice's learned preferences? You're paying to re-derive the same knowledge 50 times.

Mental models: O(1) lookup for recurring memory queries.

Define source query → reflect over memories once → store consolidation → serve instantly

Auto-refresh when observations update. Evidence chains to source memories. No per-query synthesis cost.

Tested at Vectorize:
- Support agent with policy memory
- AI assistant with user preference patterns
- AI PM with team dynamics

Token costs dropped 70-85% on high-traffic paths. Latency: seconds to milliseconds.

Pre-compute the 20% of memory queries that are 80% of traffic. Let observations handle the long tail.

Caching solves yesterday's answers. Mental models solve tomorrow's questions with yesterday's reasoning.

[link]
```

---

## Notes

**Key angles:**
- Synthesis tax (repeated reasoning over same memories)
- Dogfooding story (December evals at Vectorize)
- Semantic caching limitations (staleness, no evidence chains, manual invalidation)
- Complexity argument (O(n) synthesis vs O(1) lookup)
- Strong punchline (caching vs mental models)

**Technical hooks:**
- Tied to memory consolidation pipeline
- Auto-refresh when observations update
- Evidence chains with timestamps
- O(1) retrieval complexity
- Semantic matching without threshold tuning

**What to dismiss:**
- Semantic caching (Redis, Momento, LangChain) - can't handle evolving memory
- Prompt caching - saves input tokens, not synthesis cost
- Distillation - requires continuous retraining, loses evidence chains
- CAG/RAG - optimizes retrieval, not synthesis

**Use cases to emphasize:**
- Agent memory (learned user preferences, team patterns)
- Support agents (policy memory, not just static FAQs)
- AI assistants (accumulated observations about users)
- AI PM (engineering team dynamics, decision patterns)
