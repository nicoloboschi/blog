+++
date = '2025-12-14T10:00:00+01:00'
draft = false
title = 'Retain, Recall, Reflect: The Three Operations of Agent Memory'
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Hindsight has three operations. Retain stores content and extracts facts. Recall retrieves memories using four search strategies. Reflect reasons over memories with disposition-influenced personality. Each serves a different purpose in the agent loop.

---

## The Problem

LLM agents forget everything between sessions. You can stuff context into prompts, but that doesn't scale. RAG helps, but vector search alone misses entity relationships, temporal context, and doesn't form persistent beliefs.

Hindsight solves this with three operations: **Retain**, **Recall**, and **Reflect**.

## Retain: Store and Extract

Retain takes unstructured content and turns it into searchable memory. It's not just storage - an LLM extracts facts, identifies entities, and builds knowledge graph connections.

```python
from hindsight_client import Hindsight
from datetime import datetime

client = Hindsight(base_url="http://localhost:8888")

# Store a conversation
client.retain(
    bank_id="user-123",
    content="Alice mentioned she's switching from Google to a startup next month. She's excited about the smaller team.",
    context="casual conversation about career",
    timestamp=datetime(2024, 12, 15),
)
```

**What happens under the hood:**
- Extracts facts: "Alice works at Google", "Alice is joining a startup", "Alice prefers smaller teams"
- Identifies entities: Alice (person), Google (company)
- Captures temporal info: event happening "next month" relative to December 2024
- Builds graph connections between Alice and Google

**Key parameters:**
- `content`: The raw text to store
- `context`: Guides extraction - "career conversation" vs "technical discussion" affects what gets extracted
- `timestamp`: When the event occurred (not when you're storing it)
- `document_id`: Reusing the same ID replaces previous content (upsert behavior)

Use Retain after every conversation turn, when ingesting documents, or whenever you learn something the agent should remember.

## Recall: Multi-Strategy Search

Recall retrieves memories. Unlike basic RAG, it runs four search strategies in parallel and fuses results:

1. **Semantic**: Conceptual similarity (paraphrasing, synonyms)
2. **Keyword (BM25)**: Exact name and term matching
3. **Graph**: Entity relationships, indirect connections
4. **Temporal**: Date parsing, time-range filtering

```python
results = client.recall(
    bank_id="user-123",
    query="What's happening with Alice's career?",
    budget="high",
    max_tokens=4096,
    types=["world", "experience"],
)

for r in results.results:
    print(f"[{r.type}] {r.text}")
```

Output:
```
[world] Alice is leaving Google for a startup
[world] Alice prefers smaller teams
[experience] Discussed Alice's career change on Dec 15
```

**Key parameters:**
- `query`: Natural language question
- `budget`: Search depth - `"low"` (fast), `"mid"` (balanced), `"high"` (thorough)
- `max_tokens`: Token budget for results, not arbitrary top-k
- `types`: Filter by memory type - `["world", "experience", "opinion"]`

The token budget is important. Instead of "give me top 10 results", you say "fill up to 4096 tokens with the best matches". This integrates cleanly with context window management.

## Reflect: Reason with Personality

Reflect combines recall with disposition-influenced reasoning. It retrieves relevant memories, applies the bank's personality traits, and generates a response grounded in evidence.

```python
answer = client.reflect(
    bank_id="user-123",
    query="Should I ask Alice to join our startup?",
    context="we're building a dev tools company, need senior engineers",
    budget="low",
)

print(answer.text)
```

Output might be:
> Based on what I know about Alice, she could be a good fit. She's already planning to leave Google for a startup environment and has expressed preference for smaller teams. However, I don't have information about her specific technical skills or salary expectations. Consider discussing the role details with her directly.

**Disposition traits** shape how the agent reasons:
- **Skepticism** (1-5): Trusting vs questioning claims
- **Literalism** (1-5): Flexible vs exact interpretation
- **Empathy** (1-5): Detached vs emotionally attuned

A high-skepticism bank might add: "Though I'd verify her actual start date before making plans."

Reflect also persists opinions. If the agent concludes "Alice is a strong candidate", that belief gets stored and influences future queries.

## When to Use Each

| Operation | Use When | Example |
|-----------|----------|---------|
| **Retain** | You have new information to store | After each conversation turn, document ingestion |
| **Recall** | You need facts to build a prompt | Before generating a response, fact-checking |
| **Reflect** | You need reasoned conclusions | Recommendations, decisions, personality-consistent responses |

## Typical Agent Loop

```python
from hindsight_client import Hindsight

def agent_turn(user_message: str, bank_id: str):
    with Hindsight(base_url="http://localhost:8888") as client:
        # 1. Store the user's message
        client.retain(
            bank_id=bank_id,
            content=f"User said: {user_message}",
            context="conversation",
        )

        # 2. Recall relevant context
        results = client.recall(
            bank_id=bank_id,
            query=user_message,
            budget="high",
            max_tokens=2048,
        )

        # 3. Build prompt with memories
        context = "\n".join([r.text for r in results.results])

        # 4. Generate response (your LLM call)
        response = generate_response(user_message, context)

        # 5. Store the response
        client.retain(
            bank_id=bank_id,
            content=f"I responded: {response}",
            context="conversation",
        )

        return response
```

Or use Reflect for disposition-influenced reasoning:

```python
def agent_turn_with_personality(user_message: str, bank_id: str):
    with Hindsight(base_url="http://localhost:8888") as client:
        # Store input
        client.retain(bank_id=bank_id, content=f"User: {user_message}")

        # Reflect generates the response directly
        answer = client.reflect(
            bank_id=bank_id,
            query=user_message,
            budget="low",
        )

        return answer.text
```

## Memory Types

Hindsight categorizes memories into four types:

| Type | What It Is | Example |
|------|-----------|---------|
| `world` | Objective facts received | "Alice works at Google" |
| `experience` | Agent's own interactions | "I discussed Python with Alice" |
| `opinion` | Beliefs with confidence | "Python excels for ML" (0.85) |
| `observation` | Synthesized entity profiles | Auto-generated summaries about tracked entities |

You can filter by type in Recall to get only facts (`world`) or only the agent's experiences (`experience`).

---

Three operations, each with a clear purpose. Retain stores, Recall retrieves, Reflect reasons. The rest is just parameters.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
