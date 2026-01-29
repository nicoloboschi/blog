# Social Media - Hindsight 0.4.0: Mental Models

## Twitter/X

### Option 1 (The consistency problem)
```
Your agent answers "What's our refund policy?" today → one answer
Tomorrow, same facts → slightly different phrasing

For recurring questions where consistency matters, this variability is a problem.

Mental models in Hindsight 0.4.0: pre-computed, user-curated answers that bypass LLM processing.

Same query = exact same response. Every time.

[link]
```

### Option 2 (The cost problem)
```
Recurring questions burn tokens every time.

Agent gets asked about Redis vs Memcached → full reflect, LLM call, token cost
Same question tomorrow → same reasoning, same cost

Multiply by hundreds of queries per day. It adds up.

Mental models: compute once, serve forever. Zero LLM calls after creation.

[link]
```

### Option 3 (Priority hierarchy)
```
Hindsight 0.4.0 memory hierarchy:

Mental Models (pre-computed, curated)
    ↓
Observations (auto-synthesized patterns)
    ↓
Raw Facts (full reasoning)

Curate the 20% of queries that are 80% of traffic.
Let observations handle the long tail.

[link]
```

### Option 4 (Auto-refresh)
```
Mental models can get stale as new facts come in.

"What are our Redis practices?" was answered before you learned about SSPL licensing concerns.

Solution: auto-refresh triggers.

Set `refresh_after_consolidation: true` and the mental model updates in the background when observations change.

[link]
```

### Option 5 (When to use)
```
Mental models vs observations:

Use mental models when:
• Recurring questions (asked 100+ times)
• Stable answers (policies, FAQs)
• Need manual review (compliance, legal)
• Consistency critical

Let observations handle:
• Emerging patterns
• Long-tail queries
• Contextual reasoning

Control vs automation.

[link]
```

---

## LinkedIn

### Option 1 (Support agent scenario)
```
I was debugging a customer support agent that was burning through tokens on recurring questions.

"What's your refund policy?"
"How do I return something?"
"What's the return process?"

Same question, different phrasing. Each time: full reflect operation, LLM call, token cost. Asked hundreds of times per day.

The answer should be curated and consistent. You don't want variability in compliance-sensitive responses. But the agent was reasoning to the same conclusion every time, with slight differences in phrasing.

Standard solution: cache by query string. But that breaks immediately. "What's the return process?" and "How do I return something?" won't match.

In Hindsight 0.4.0, we added mental models - pre-computed, user-curated summaries that sit at the top of the memory hierarchy.

You define a source query: "What is our refund and return policy?"
The system runs reflect once, stores the result.
Future queries that semantically match retrieve the pre-computed content instantly. No LLM call. No variability. No per-query token cost.

Mental Models → Observations → Raw Facts

Mental models for high-traffic, curated knowledge. Observations for automatic pattern consolidation. Raw facts for everything else.

You can enable auto-refresh triggers so mental models update in the background when new facts arrive. Or keep them static for compliance-reviewed content that needs manual approval.

For the support agent, we curated 15 mental models covering ~80% of query traffic. Token costs dropped significantly. Latency improved. Consistency was guaranteed.

Pre-compute the knowledge you serve repeatedly. Let the system reason over the long tail.

[link]
```

### Option 2 (Technical advisor scenario)
```
A technical advisor agent that fields questions about infrastructure decisions.

"Should we use Redis or Memcached?"
"What's the Redis story?"
"Is Redis good for caching?"

Gets asked 3-4 times per week. Each time, the agent reasons through facts about Redis performance, licensing, operational complexity. Burns tokens. Takes seconds.

The problem: for frequently asked questions with relatively stable answers, you're paying repeatedly for the same reasoning.

Caching by query string doesn't work - semantic variation is too high. Returning stale answers when facts update is worse. You need something that's pre-computed but stays current.

Hindsight 0.4.0 introduces mental models.

Create a mental model with a source query: "What are best practices for Redis in production?"
The system runs reflect once, stores the response.
Future queries retrieve the pre-computed content instantly - no LLM processing.

Set `refresh_after_consolidation: true` to auto-refresh when observations update. New fact arrives about SSPL licensing concerns? The mental model regenerates in the background.

Mental models sit at the top of Hindsight's hierarchy:
Mental Models (curated, instant) → Observations (auto-synthesized) → Raw Facts (full reasoning)

Use mental models for the 20% of queries that account for 80% of traffic. Let observations handle long-tail questions automatically.

For the technical advisor, we curated ~10 mental models covering common topics. Queries that used to take 2-3 seconds now return in milliseconds. Token usage dropped by 60% on those paths.

In my opinion, the mental model vs observation decision comes down to control vs automation. If you need to review the answer, use a mental model. If the system can synthesize reliably, let observations handle it.

[link]
```

### Option 3 (Shorter, cost-focused)
```
Recurring questions in agent systems burn tokens unnecessarily.

I was tracking costs for an internal AI PM that answers questions about team processes, project status, common blockers. Same ~20 questions account for 70% of traffic.

Each query: full reflect operation, LLM synthesis, token cost. Answers vary slightly between calls - same facts, different phrasing.

For policies, FAQs, curated knowledge - this variability isn't acceptable. You want consistent responses. But caching by query string doesn't work with semantic variation.

Hindsight 0.4.0 adds mental models: user-curated, pre-computed summaries that bypass LLM processing during reflect.

Define a source query, system runs reflect once, stores the result. Future queries retrieve instantly - no LLM call, no tokens, no variability.

Hierarchy: Mental Models → Observations → Raw Facts

Mental models for high-traffic, curated topics. Observations for automatic consolidation. Raw facts for long-tail reasoning.

Auto-refresh triggers keep them current: when observations update, mental models regenerate in the background.

For the AI PM, curating 18 mental models covered ~70% of query volume. Token costs dropped significantly. Latency improved. Responses became deterministic.

Compute once, serve forever. Use mental models for the queries you answer repeatedly.

[link]
```

---

## Notes

**Key angles:**
- Consistency problem (variability in responses for recurring questions)
- Cost problem (token burn on repeated reasoning)
- Performance problem (latency for high-traffic queries)
- Control (curated answers vs automatic synthesis)

**Technical hooks:**
- Priority hierarchy (Mental Models → Observations → Facts)
- Auto-refresh mechanisms
- Zero LLM calls after creation
- Semantic matching (not string caching)

**Use cases to emphasize:**
- Customer support (policies, FAQs)
- Technical advisors (recurring infrastructure questions)
- Internal AI PM (team processes, common questions)
- Compliance/legal (reviewed content that must be consistent)
