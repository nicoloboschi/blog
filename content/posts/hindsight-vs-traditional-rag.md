+++
date = '2025-12-08T10:00:00+01:00'
draft = false
title = 'Hindsight vs traditional RAG: what you actually get'
tags = ["AI", "agents", "memory", "hindsight", "LLM", "RAG"]
+++

**TL;DR**: Traditional RAG uses semantic similarity search over document chunks. Hindsight runs four retrieval strategies in parallel (semantic + keyword + graph + temporal), maintains entity relationships, handles time expressions, and forms persistent opinions. Different tools for different problems.

---

## What RAG Actually Does

Traditional RAG is straightforward:

1. Chunk your documents
2. Embed chunks into vectors
3. At query time, find the top-k most similar chunks
4. Stuff them into the LLM prompt

This works well for static document Q&A. "What's the refund policy?" finds the refund section. "How do I reset my password?" retrieves the password docs.

But semantic similarity has limits.

## Where Vector Search Falls Short

### Exact Names and Terms

Query: "What did Alice Chen say about the API redesign?"

Vector search finds chunks semantically related to "API redesign." But "Alice Chen" is a proper noun - it needs exact matching, not semantic similarity. BM25 keyword search handles this better.

### Time Expressions

Query: "What happened last spring?"

Vector search has no concept of time. It might retrieve chunks containing the word "spring" or semantically similar terms. It can't parse "last spring" into a date range and filter accordingly.

### Multi-Hop Connections

Your knowledge base contains:
- "Alice is the tech lead on Project Atlas"
- "Project Atlas uses Kubernetes"
- "The Kubernetes cluster had an outage Tuesday"

Query: "Was Alice affected by any infrastructure issues?"

Vector search retrieves chunks similar to "Alice" and "infrastructure issues." It can't traverse Alice → Project Atlas → Kubernetes → outage. That requires entity relationships and graph traversal.

## What Hindsight Does Differently

### Four Retrieval Strategies

Instead of semantic-only, Hindsight runs four searches in parallel:

| Strategy | Handles |
|----------|---------|
| **Semantic** | Conceptual similarity, paraphrasing |
| **Keyword (BM25)** | Exact names, technical terms |
| **Graph** | Entity relationships, multi-hop reasoning |
| **Temporal** | Date parsing, time-range filtering |

Results merge via reciprocal rank fusion (RRF), which doesn't require score calibration across systems. Then a cross-encoder reranks the combined results.

### Entity Resolution

Hindsight tracks entities across conversations. "Alice," "Alice Chen," and "Alice C." resolve to the same canonical entity through:
- String similarity (Levenshtein distance)
- Co-occurrence patterns
- Temporal proximity

This builds a knowledge graph where facts connect through shared entities, not just embedding proximity.

### Temporal Understanding

Every fact stores two timestamps:
- **Occurrence time**: When the event happened
- **Mention time**: When you learned about it

A fact retained in January 2025 about "Alice got married in June 2024" can answer both:
- "What did Alice do in 2024?" (occurrence-based)
- "What did I learn recently?" (mention-based)

Queries like "last spring" or "before the merger" get parsed into date ranges and matched against occurrence intervals.

### Graph Traversal

The memory graph has four edge types:
- **Entity links**: Same canonical entity
- **Temporal links**: Close in time (exponential decay)
- **Semantic links**: High embedding similarity
- **Causal links**: Cause-effect relationships

Queries trigger spreading activation across these links, surfacing indirectly connected facts that pure vector search misses.

## Concrete Example

```python
# Store facts about a project
client.retain(
    bank_id="my-bank",
    content="Alice is the tech lead on Project Atlas. Project Atlas launched in March 2024 and uses Kubernetes for orchestration.",
    context="team documentation"
)

client.retain(
    bank_id="my-bank",
    content="The Kubernetes cluster experienced a 2-hour outage on Tuesday affecting multiple services.",
    context="incident report",
    timestamp="2024-12-17"
)

# Query that requires multi-hop reasoning
results = client.recall(
    bank_id="my-bank",
    query="Was Alice affected by any recent infrastructure issues?",
    max_tokens=4096
)
```

**Traditional RAG**: Retrieves chunks about Alice OR infrastructure issues. Misses the connection.

**Hindsight**: Traverses Alice → Project Atlas → Kubernetes → outage. Returns both the team structure and the incident.

## Memory Type Separation

RAG treats everything as "document chunks." Hindsight separates:

| Type | What It Is |
|------|-----------|
| **World** | Objective facts received |
| **Experience** | Agent's own interactions |
| **Opinion** | Beliefs with confidence scores |
| **Observation** | Synthesized entity profiles |

You can filter retrieval by type. Want only objective facts? `types=["world"]`. Want the agent's formed beliefs? `types=["opinion"]`.

## Persistent Opinions

RAG is stateless. Same query, same chunks, same response (modulo LLM variance).

Hindsight forms opinions during reasoning that persist across sessions. These have confidence scores that evolve:
- Supporting evidence increases confidence
- Contradictions decrease it (with 2x penalty)

An agent that's been tracking a technology for months develops nuanced views that fresh retrieval can't replicate.

## When to Use Which

**Traditional RAG works for:**
- Static document Q&A
- Simple semantic matching
- Stateless, one-off queries
- When you don't need entity tracking or temporal reasoning

**Hindsight adds value for:**
- Conversational agents with memory
- Queries requiring temporal reasoning ("last quarter," "before the reorg")
- Multi-hop questions across entity relationships
- Applications needing consistent agent personality
- Long-horizon contexts where facts accumulate over time

## The Complexity Trade-off

Hindsight is more complex than a vector store. You're running four retrieval strategies, maintaining a knowledge graph, handling entity resolution, and managing opinion evolution.

In my opinion, the complexity is justified when your use case actually needs it. If you're building a chatbot that answers questions about static docs, RAG is simpler and works fine. If you're building an agent that remembers conversations, tracks entities over time, and should develop consistent perspectives - that's where the extra machinery pays off.

---

RAG does one thing: semantic similarity search. Hindsight does four things in parallel and maintains structured memory on top. Pick based on what your use case actually requires.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
