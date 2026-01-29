+++
date = '2026-01-29T10:00:00+01:00'
draft = true
title = 'Building agentic reflect: reasoning through iteration in Hindsight 0.4.0'
tags = ["AI", "agents", "memory", "hindsight", "LLM", "reflect"]
+++

**TL;DR**: Hindsight's reflect operation isn't just retrieval - it's agentic reasoning that iterates through a knowledge hierarchy. Mental models get checked first, then observations, then raw facts. Mission statements, directives, and disposition traits shape how the agent interprets evidence and forms beliefs.

---

## Reflect vs Recall: Different Operations

I see people confuse recall and reflect all the time. They're both about getting information from memory, but they serve completely different purposes.

**Recall** is pure retrieval. You ask a question, the TEMPR system searches (semantic + keyword + graph + temporal strategies), and you get back matching memories. No reasoning, no interpretation, just ranked results.

**Reflect** is reasoning. It retrieves memories like recall does, but then applies the agent's personality to synthesize a response. The agent doesn't just return facts - it thinks through them, forms conclusions, and generates beliefs with confidence scores.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Recall: get raw memories
results = client.recall(
    bank_id="my-bank",
    query="What does Alice do?",
    budget="high"
)

for r in results.results:
    print(f"[{r.type}] {r.text}")
# Output:
# [world] Alice works at Google
# [world] Alice is switching to a startup
# [experience] Discussed Alice's career plans on Dec 15

# Reflect: get reasoned interpretation
answer = client.reflect(
    bank_id="my-bank",
    query="Should I ask Alice to join our team?",
    context="hiring for a senior backend engineer role",
    budget="high"
)

print(answer.text)
# Output: (synthesized reasoning based on disposition)
# "Alice could be a strong fit. She's planning to leave Google
# for a startup environment, which aligns with our company stage.
# However, I don't have information about her backend experience
# or salary expectations. I'd verify her technical skills match
# our Python/PostgreSQL stack before proceeding."
```

Notice the difference. Recall gave me facts. Reflect gave me analysis.

## The Knowledge Hierarchy

Here's what changed in 0.4.0 that makes reflect more powerful: the **knowledge hierarchy**.

When reflect runs, it checks sources in priority order:

**Mental Models → Observations → Facts**

This isn't just organizational - it fundamentally changes how the agent reasons.

### Mental Models: Curated Summaries

Mental models are user-created summaries for common queries. Instead of re-synthesizing the same knowledge every time, you create a mental model once and the agent uses it consistently.

Think of them as cached reasoning. If you constantly ask "What's our hiring policy?", you don't want the agent to re-derive the answer from scattered facts each time. Create a mental model with the canonical answer, and reflect will use it.

Mental models sit at the top of the hierarchy. When reflect runs, it checks mental models first. If a relevant model exists, that takes priority over everything else.

### Observations: Automatic Consolidation

Observations are automatically generated entity summaries. When you accumulate enough facts about Alice, Hindsight synthesizes them into a coherent observation.

Example observation about Alice:
> "Alice is a software engineer at Google specializing in ML. She joined in 2020 and is planning to move to a startup. She prefers smaller teams and has experience with Python and TensorFlow."

Observations sit below mental models but above raw facts. If there's no mental model for the query, reflect checks observations next.

The key difference from mental models: observations are automatic. You don't create them - they emerge from accumulated evidence. Mental models are curated. You create them deliberately.

### Raw Facts: The Foundation

World facts and experiences are the foundation. "Alice works at Google", "I discussed Python with Alice", etc.

If there's no mental model and no relevant observation, reflect uses raw facts. But even then, it doesn't just return them - it reasons over them.

## Why This Hierarchy Matters

The hierarchy solves a fundamental problem: **consistency vs freshness**.

Without hierarchy, every reflect call re-synthesizes answers from raw facts. That's flexible but inconsistent. Ask the same question twice, get slightly different answers. Not ideal for production agents.

With hierarchy, you get both:
- Mental models provide consistency for established knowledge
- Observations consolidate patterns as they emerge
- Raw facts ensure you never lose detail

The agent becomes predictable without becoming rigid.

## Agentic Iteration: How Reflect Actually Works

This is where it gets interesting. Reflect doesn't just do a single LLM call. It iterates.

The pipeline looks like this:

1. **Memory Retrieval**: TEMPR searches across all four strategies (semantic, keyword, graph, temporal) and returns relevant memories prioritized by the hierarchy

2. **Profile Integration**: Loads the bank's personality profile - mission, directives, and disposition traits (skepticism, literalism, empathy)

3. **Multi-Stage Reasoning**: The LLM doesn't just generate a response. It reasons through the evidence, considering the mission statement and disposition traits

4. **Opinion Formation**: If the agent reaches a conclusion, it stores that as an opinion with a confidence score

5. **Belief Evolution**: Future reflects can update opinion confidence if new evidence arrives

This is what "agentic" means. The agent doesn't passively retrieve and return. It actively interprets, forms beliefs, and evolves those beliefs over time.

## Custom Prompts Through Configuration

You shape how reflect reasons by configuring three things: **mission**, **directives**, and **disposition**.

### Mission: What to Prioritize

The mission is a natural language statement that tells the agent what knowledge matters.

```python
client.create_bank(
    bank_id="my-bank",
    background="I am a senior software architect with 15 years of distributed systems experience.",
    mission="Prioritize technical accuracy and production reliability over bleeding-edge trends"
)
```

Now when you reflect, the agent interprets evidence through that lens. If you ask "Should we use Kubernetes?", the mission influences whether the answer focuses on operational complexity or ecosystem maturity.

### Directives: Hard Rules

Directives are non-negotiable constraints. The agent must follow them.

Examples:
- "Never recommend specific stocks"
- "Always cite sources when making factual claims"
- "Do not discuss competitor pricing"

These work like guardrails. The agent can reason freely, but it can't violate directives.

### Disposition: Soft Influence

Disposition traits shape interpretation style without forcing specific conclusions.

```python
client.create_bank(
    bank_id="skeptical-bank",
    background="Technical advisor",
    disposition={
        "skepticism": 4,   # 1-5 scale: high skepticism
        "literalism": 4,   # 1-5 scale: strict interpretation
        "empathy": 2       # 1-5 scale: low empathy
    }
)

client.create_bank(
    bank_id="optimistic-bank",
    background="Technical advisor",
    disposition={
        "skepticism": 2,   # 1-5 scale: low skepticism
        "literalism": 2,   # 1-5 scale: flexible interpretation
        "empathy": 4       # 1-5 scale: high empathy
    }
)
```

Give both banks the same facts about a new technology. The skeptical bank will emphasize risks and unknowns. The optimistic bank will emphasize potential and opportunities.

Same evidence, different reasoning, shaped by disposition.

## Multi-Hop Reasoning

Here's where the hierarchy really pays off: multi-hop queries.

Simple query: "What does Alice do?"
- Check observations about Alice
- Return synthesized profile

Complex query: "Which of our contacts would be good for a DevOps role at a Series A startup?"
- Retrieve observations about known contacts
- Cross-reference with facts about their preferences (startup vs enterprise, team size preferences)
- Consider experiences from past conversations about career goals
- Synthesize recommendations with reasoning

The agent doesn't just match keywords. It connects pieces of knowledge across the hierarchy.

```typescript
const { HindsightClient } = require('@vectorize-io/hindsight-client');

const client = new HindsightClient({ baseUrl: 'http://localhost:8888' });

// Multi-hop query requiring synthesis
const answer = await client.reflect(
    'hiring-bank',
    'Who should I reach out to for our DevOps position?',
    {
        budget: 'high',  // thorough search
        context: 'Series A startup, Kubernetes-heavy stack, 5-person team'
    }
);

console.log(answer.text);
// The agent will:
// 1. Find people with DevOps experience (facts)
// 2. Check if any prefer small teams (observations)
// 3. Consider past conversations about job searching (experiences)
// 4. Synthesize recommendations based on alignment
```

This is reasoning, not retrieval. The answer doesn't exist anywhere in the memory bank. The agent constructs it by connecting evidence.

## When to Use Reflect vs Recall

I use this heuristic:

**Use recall when** you need facts for your own prompt building. You're constructing context for another LLM call, you want raw memories, or you're filtering by specific memory types.

**Use reflect when** you want the agent's opinion. You need recommendations, analysis, or personality-consistent responses. The agent's disposition should influence the answer.

Example: building a customer support agent.

```python
# Recall: gather relevant support tickets and docs
tickets = client.recall(
    bank_id="support-history",
    query=user_question,
    types=["world", "experience"],
    budget="high",
    max_tokens=2048
)

docs = client.recall(
    bank_id="product-docs",
    query=user_question,
    budget="high",
    max_tokens=2048
)

# Build context for your LLM
context = format_memories(tickets.results + docs.results)
response = your_llm_call(user_question, context)
```

vs

```python
# Reflect: let the agent reason directly
answer = client.reflect(
    bank_id="support-agent",
    query=user_question,
    context="customer support interaction",
    budget="high"
)

response = answer.text
```

The recall approach gives you control. You format the prompt, choose the LLM, handle the reasoning.

The reflect approach delegates to the agent. It uses its configured personality, checks the knowledge hierarchy, and generates a response.

I prefer recall when building complex multi-step workflows. I prefer reflect when I want consistent, personality-driven responses.

## Budget Parameter: Search Depth

Both recall and reflect have a `budget` parameter: `"low"`, `"mid"`, or `"high"`.

This controls how thoroughly TEMPR searches the memory bank. Low budget does shallow graph traversal and minimal re-ranking. High budget does deep traversal and extensive cross-encoder re-ranking.

For reflect specifically:
- Low budget: fast responses, good for simple queries
- Mid budget: balanced, good default
- High budget: thorough reasoning, use for complex multi-hop queries

I typically use low for conversational interactions (latency matters) and high for analysis tasks (thoroughness matters).

## Opinion Evolution

Here's something subtle but important: reflect creates **persistent opinions**.

When the agent reasons to a conclusion, that conclusion gets stored as an opinion with a confidence score. Future reflects can reference that opinion.

If new evidence arrives that contradicts the opinion, the confidence score decreases. If supporting evidence arrives, confidence increases.

Example flow:

1. Reflect: "Should we use PostgreSQL for this project?"
   - Agent forms opinion: "PostgreSQL is well-suited for this use case" (confidence: 0.8)
   - Opinion gets stored

2. Retain new fact: "The team lacks PostgreSQL expertise"
   - Opinion gets updated: "PostgreSQL is technically suitable but may slow us down" (confidence: 0.6)

3. Reflect again: "Should we use PostgreSQL?"
   - Agent references the existing opinion
   - Considers new evidence
   - Updates conclusion: "PostgreSQL fits the use case but training costs should be factored in" (confidence: 0.65)

This is fundamentally different from stateless RAG. The agent builds persistent beliefs that evolve with evidence.

## Practical Example: Technical Advisor

Let me show a complete example of building a technical advisor agent.

```python
from hindsight_client import Hindsight
from datetime import datetime

client = Hindsight(base_url="http://localhost:8888")

# Create a bank with specific personality
client.create_bank(
    bank_id="tech-advisor",
    background="Senior architect with experience in distributed systems, databases, and production operations",
    mission="Prioritize production reliability, operational simplicity, and team expertise over hype",
    disposition={
        "skepticism": 4,   # Question vendor claims
        "literalism": 3,   # Balanced interpretation
        "empathy": 3       # Consider team impact
    }
)

# Store context about the team and project
client.retain(
    bank_id="tech-advisor",
    content="Our team has 3 backend engineers, all experienced with Python and PostgreSQL. No Kubernetes experience.",
    context="team composition",
    timestamp=datetime.now()
)

client.retain(
    bank_id="tech-advisor",
    content="Project requirements: 100k users, standard CRUD app, tight 3-month deadline",
    context="project scope",
    timestamp=datetime.now()
)

# Ask for architecture advice
answer = client.reflect(
    bank_id="tech-advisor",
    query="Should we deploy on Kubernetes or use a simpler platform?",
    context="architecture decision for new project",
    budget="high"
)

print(answer.text)
```

The agent will reason through:
- Team expertise (no Kubernetes experience)
- Project scope (standard CRUD, tight deadline)
- Mission (prioritize operational simplicity)
- Disposition (skeptical of complex solutions)

The output will likely recommend against Kubernetes given the constraints, not because Kubernetes is bad, but because it doesn't fit this specific context.

That's agentic reasoning. Same agent, different facts, different recommendation.

---

In my opinion, the reflect system in 0.4.0 is what makes Hindsight actually useful for production agents. The hierarchy ensures consistency without rigidity. The disposition system enables personality without prompt engineering. The opinion evolution creates persistent beliefs that mature with evidence.

It's not just memory retrieval. It's memory-grounded reasoning.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
