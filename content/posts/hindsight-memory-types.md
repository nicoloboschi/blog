+++
date = '2025-12-17T12:00:00+01:00'
draft = false
title = 'Memory Types in Hindsight: World, Experience, Opinion, Observation'
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Hindsight organizes memories into four types that mimic human cognition. World stores external facts. Experience records what the agent did. Opinion holds beliefs with confidence scores. Observation synthesizes entity profiles. Each type has different creation paths and retrieval uses.

---

## Why Categorize Memory?

Vector databases treat everything the same - just embeddings with metadata. But humans don't remember "Alice works at Google" the same way they remember "I told Alice about Python" or "I think Alice would be a good hire."

Hindsight separates these into distinct types because they serve different purposes in reasoning:
- Facts inform decisions
- Experiences provide context
- Opinions guide judgment
- Observations consolidate entity knowledge

This separation lets you filter retrieval by epistemic category. When you ask "what do I know about Alice?", you might want facts. When you ask "what have I discussed with Alice?", you want experiences. Different questions, different memory types.

## The Four Types

### World: Third-Person Facts

World memories are objective facts about external reality. Things the agent learned but didn't participate in.

Examples:
- "Alice works at Google"
- "PostgreSQL supports vector operations"
- "The meeting is scheduled for Tuesday"
- "Revenue grew 15% last quarter"

**How they're created:** During `retain()`, the LLM extracts facts from content. When the fact describes something external (people, places, events, data), it gets tagged as `world`.

**Key characteristic:** No agent involvement. These are statements that would be true regardless of who's observing them. The agent is a recorder, not a participant.

### Experience: First-Person History

Experiences record what the agent itself did or witnessed directly. This is the agent's autobiography.

Examples:
- "I recommended Python to Bob"
- "I scheduled a meeting with Alice for Tuesday"
- "User asked me about database optimization"
- "I clarified the API requirements with the team"

**How they're created:** When `retain()` processes content that includes the agent's actions or direct involvement, those facts get tagged as `experience`.

**Key characteristic:** The agent is the subject or a direct participant. "I did X" rather than "X happened."

Why does this matter? Consider two queries:
- "What do I know about Python?" → Might return world facts about Python
- "What have I discussed about Python?" → Returns experiences where Python came up

An agent with only world facts is a knowledge base. An agent with experiences has context about its own interactions.

### Opinion: Beliefs with Confidence

Opinions are beliefs the agent forms through reasoning, with explicit confidence scores that evolve over time.

Examples:
- "Python is excellent for ML" (confidence: 0.85)
- "Alice would be a good fit for the team" (confidence: 0.72)
- "This codebase needs refactoring" (confidence: 0.60)

**How they're created:** Opinions form **only** during `reflect()`, not during `retain()`. When the agent reasons over accumulated evidence and reaches conclusions, those conclusions become opinions.

**Key characteristic:** Opinions have confidence scores that change. If evidence supports the belief, confidence increases. Contradictory evidence decreases it. A single opinion might evolve:

1. Initial: "Python is best for ML" (0.85)
2. After contradictory evidence: "Python is strong for ML but Rust handles performance-critical workloads better" (0.72)

This is where **disposition traits** come in. A high-skepticism agent requires more evidence to reach high confidence. A low-skepticism agent forms opinions quickly. The same facts can lead to different opinions depending on the bank's disposition.

```python
# Create a bank with high skepticism
client.create_bank(
    bank_id="my-bank",
    background="I am a senior software architect with 15 years of
               distributed systems experience.",
    disposition={
        "skepticism": 4,   # 1-5 scale
        "literalism": 4,   # 1-5 scale
        "empathy": 2       # 1-5 scale
    }
)

# Reflect generates opinions influenced by disposition
answer = client.reflect(
    bank_id="my-bank",
    query="What should I know about Alice?",
    budget="low",  # "low", "mid", or "high"
    context="preparing for a meeting"
)

print(answer.text)
```

### Observation: Entity Profiles

Observations are automatically synthesized summaries about specific entities. Rather than storing scattered facts, Hindsight consolidates what it knows about important entities.

Example for entity "Alice":
> Alice is a software engineer at Google specializing in ML. She joined in 2020 and is planning to move to a startup. She prefers smaller teams and has experience with Python and TensorFlow.

**How they're created:** Automatically during background processing. When an entity accumulates enough facts (minimum five), Hindsight generates a unified observation. These regenerate as new facts arrive.

**Key characteristic:** You don't create these directly. They emerge from accumulated world facts and experiences about specific entities.

This handles the "consolidation problem." Without observations, querying "tell me about Alice" might return five separate snippets. With observations, you get a coherent profile.

## Creation Paths

| Type | Created During | How |
|------|---------------|-----|
| **World** | `retain()` | LLM extracts third-person facts |
| **Experience** | `retain()` | LLM extracts agent-involved facts |
| **Opinion** | `reflect()` | Agent reasons to conclusions |
| **Observation** | Background | Auto-generated from entity facts |

Important: You don't choose the type when calling `retain()`. The LLM determines whether extracted facts are world or experience based on content. Opinions only form through `reflect()`.

## Filtering by Type

When calling `recall()`, you can filter by memory type:

```python
# Basic recall prints type alongside each result
results = client.recall(
    bank_id="my-bank",
    query="What does Alice do?",
)

for r in results.results:
    print(f"{r.text} (type: {r.type})")
```

Filter to specific types:

```python
# Only world facts and opinions
results = client.recall(
    bank_id="my-bank",
    query="What does Alice do?",
    types=["world", "opinion"]
)

# Only world facts and experiences
results = client.recall(
    bank_id="my-bank",
    query="query",
    types=["world", "experience"]
)
```

For entity observations, use `include_entities`:

```python
response = client.recall(
    bank_id="my-bank",
    query="What does Alice do?",
    max_tokens=4096,
    include_entities=True,
    max_entity_tokens=500
)

if response.entities:
    for entity in response.entities:
        print(f"Entity: {entity.name}")
```

## When Type Filtering Matters

**Building prompts:** If you're building a prompt for factual Q&A, filter to `world`. If you're building context for a follow-up conversation, include `experience`.

**Avoiding hallucination:** An agent might "remember" an opinion as a fact. By separating types, you can explicitly tell your LLM: "These are facts. These are my past opinions. Treat them differently."

**Entity lookups:** When you need a quick summary of a person or company, fetch `observation` type directly rather than piecing together scattered facts.

**Confidence tracking:** Only `opinion` type has confidence scores. If you need to show certainty levels or track belief evolution, query opinions specifically.

## The Cognitive Parallel

In my opinion, the reason this categorization works is because it mirrors how humans actually organize memory:

- **Semantic memory** (world) - General knowledge about the world
- **Episodic memory** (experience) - Personal events and interactions
- **Beliefs** (opinion) - Conclusions drawn from evidence
- **Mental models** (observation) - Synthesized understanding of entities

Traditional RAG flattens all of this into "similar text chunks." Hindsight preserves the epistemic structure, which means retrieval can be more precise and reasoning can distinguish between what the agent knows versus what it did versus what it believes.

---

Four types, each with a purpose. Filter by type to get exactly what you need. Let opinions evolve with evidence. Trust observations for entity summaries.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
