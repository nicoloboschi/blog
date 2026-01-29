+++
date = '2026-01-28T10:00:00+01:00'
draft = true
title = 'Stop reasoning to the same answer twice'
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Mental models are pre-computed, user-curated summaries that sit at the top of Hindsight's memory hierarchy. They bypass LLM processing during reflect operations, delivering instant, consistent responses for recurring queries while letting you control exactly how certain topics are answered.

---

## The Latency-Consistency Problem

Reflect operations are powerful - they let agents reason over accumulated knowledge to generate contextual answers. But that reasoning comes with costs: LLM calls add latency, token usage adds expense, and synthesized responses can vary between calls.

Ask an agent "What are our team's communication preferences?" today and get one answer. Ask tomorrow with the same facts and get a slightly different phrasing. For recurring questions where consistency matters - policies, FAQs, curated guidelines - this variability is a problem.

I've seen this play out in a few scenarios. A customer support agent that needs to explain the same refund policy hundreds of times. A technical advisor that gets asked about Redis vs Memcached every few days. An internal AI PM that answers "how do standups work here?" multiple times per week. Each time, the agent burns tokens reasoning to the same conclusion.

The naive fix: cache responses by query string. But that breaks the moment someone rephrases the question. "How does the team communicate?" and "What's the team's communication style?" should return the same curated answer, but string matching won't catch that.

## Mental Models: User-Curated Summaries

Mental models solve this by letting you pre-compute answers to source queries. You define a query, Hindsight runs reflect once, and the result gets stored as a mental model. When future reflect operations touch that topic, the pre-computed content is returned instantly - no LLM call, no synthesis, no variability.

The API is straightforward:

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Create a mental model
result = client.create_mental_model(
    bank_id="my-agent",
    name="Team Communication Preferences",
    source_query="How does the team prefer to communicate?",
    tags=["team", "communication"]
)
```

This triggers a reflect operation with the source query. The response gets stored along with metadata about which facts were used. Now when someone asks about team communication, the mental model is checked first.

The `name` field is just a human-readable identifier. The actual matching happens at the semantic level - similar queries to the source query will retrieve this mental model, so you don't need exact string matches.

## Priority Hierarchy: Mental Models First

During reflect operations, Hindsight checks sources in priority order:

**Mental Models → Observations → Raw Facts**

Mental models are checked first. If a relevant mental model exists, its content is used directly. If not, the system falls back to observations (automatically synthesized entity summaries), and finally to raw facts for full LLM reasoning.

This hierarchy is deliberate. Mental models represent your highest-confidence, manually reviewed knowledge. Observations are automatically consolidated patterns. Raw facts are the foundation requiring the most processing.

In my opinion, this layering is what makes the system practical. You curate mental models for the 20% of queries that account for 80% of your traffic. The remaining 80% of long-tail queries still get handled by automatic consolidation and reasoning.

## Auto-Refresh: Staying Current

Mental models can become stale as new facts accumulate. If your curated answer to "What are our Redis practices?" was formed before you learned about SSPL licensing concerns, it needs updating.

The solution: automatic refresh triggers.

```python
client.update_mental_model(
    bank_id="my-agent",
    mental_model_id=mental_model_id,
    trigger={"refresh_after_consolidation": True}
)
```

With `refresh_after_consolidation: true`, the mental model automatically refreshes whenever observations are updated. This happens in the background - the agent continues using the existing mental model until the refresh completes.

When to enable auto-refresh:
- **Real-time dashboards**: Current metrics, status updates
- **Evolving preferences**: Team norms that shift over time
- **Technical guidance**: Best practices that change as you learn

When to disable it:
- **Curated policies**: Require manual review before changes
- **FAQs**: Controlled messaging for consistency
- **Legal content**: Changes need approval workflows

You can also manually refresh at any time:

```python
client.refresh_mental_model(
    bank_id="my-agent",
    mental_model_id=mental_model_id
)
```

This re-runs the source query and updates the content. The old version remains available until the refresh completes, preventing gaps.

## When to Use Mental Models

Mental models are not a replacement for observations or raw facts. They're a tool for specific scenarios where you need control.

**Good fits for mental models:**

1. **Recurring questions with stable answers**: "What's our refund policy?" doesn't change daily
2. **Curated knowledge requiring review**: You want a human to approve what gets said
3. **High-traffic queries**: Pre-computing saves cost when asked hundreds of times
4. **Consistency-critical topics**: Compliance, legal, official policies

**Let observations handle:**

1. **Emerging patterns**: Things you're still learning about
2. **Long-tail queries**: Rarely asked, not worth manual curation
3. **Contextual reasoning**: Questions that need fresh synthesis each time
4. **Exploratory answers**: When variation is acceptable

I think the mental model vs observation decision comes down to control vs automation. If you need to review and approve the answer, use a mental model. If the system can synthesize it reliably, let observations handle it.

## Performance and Cost Implications

Mental models bypass LLM processing during reflect. That has concrete implications:

**Latency**: Retrieving a mental model is a simple lookup - milliseconds instead of seconds. For high-traffic scenarios, this matters. An agent answering hundreds of support questions per hour saves meaningful time.

**Token costs**: Each reflect call with full reasoning burns tokens. Pre-computing via mental models means you pay once during creation, then serve infinite queries at near-zero cost.

**Consistency**: LLM outputs have inherent variability. Mental models eliminate that - the same query returns the exact same content every time. For compliance-sensitive contexts, this consistency is critical.

The tradeoff: storage overhead and refresh compute. Each mental model stores its content plus metadata about source facts. Automatic refresh triggers still run LLM calls in the background. But for high-traffic queries, the amortized cost is significantly lower than on-demand synthesis.

## Reviewing and Managing Mental Models

Mental models are user-curated, which means they need review workflows.

List all mental models:

```python
mental_models = client.list_mental_models(bank_id="my-agent")

for mm in mental_models:
    print(f"{mm.name}: last refreshed {mm.last_refreshed_at}")
```

Get a specific mental model to review its content:

```python
mental_model = client.get_mental_model(
    bank_id="my-agent",
    mental_model_id=mental_model_id
)

print(f"Content: {mental_model.content}")
print(f"Source facts: {mental_model.reflect_response.sources}")
```

The `reflect_response` includes the full evidence chain - which facts were used to generate the content, with timestamps and entity links. This transparency lets you audit why the mental model says what it says.

If a mental model becomes obsolete:

```python
client.delete_mental_model(
    bank_id="my-agent",
    mental_model_id=mental_model_id
)
```

## Implementation Notes

Some practical details from working with mental models:

**Tagging for organization**: Use tags to group related mental models. `tags=["policy", "customer-facing"]` lets you filter when listing or managing mental models at scale.

**Source query design**: The source query should be representative of how users will actually ask. If people ask "What's the return process?" and "How do I return something?" but your source query is "Describe return procedures," the matching might be weaker. I test source queries by running them manually first.

**Refresh concurrency**: The system limits concurrent mental model refreshes (default: 8). If you have hundreds of mental models all triggering refresh simultaneously, they'll queue. For production deployments, tune `HINDSIGHT_API_MENTAL_MODEL_REFRESH_CONCURRENCY` based on your LLM rate limits.

**Max tokens**: You can limit mental model content length with the `max_tokens` parameter. This is useful when you need concise summaries that fit into specific UI constraints or token budgets.

---

Mental models sit at the top of Hindsight's knowledge hierarchy, providing instant, consistent answers for recurring queries. They're best used for high-traffic questions where you need control over the response, while observations handle automatic consolidation for long-tail queries. Auto-refresh keeps them current, and the pre-computed approach eliminates per-query LLM costs. Use them when consistency and latency matter more than dynamic synthesis.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
