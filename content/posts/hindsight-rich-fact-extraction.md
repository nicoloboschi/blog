+++
date = '2025-12-15T15:00:00+01:00'
draft = false
title = 'Rich fact extraction: preserving narrative, not just statements'
description = "Why sentence-level RAG chunks lose context. Hindsight extracts 2-5 narrative facts per conversation, preserving reasoning chains and causal relationships."
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Traditional RAG fragments text into isolated statements, losing context. Hindsight extracts 2-5 narrative facts per conversation that preserve emotions, reasoning chains, and causal relationships. The context parameter guides what gets extracted.

---

## The Fragmentation Problem

Most RAG systems chunk text and store isolated statements. A conversation like:

> "Alice and Bob discussed naming their summer party playlist. Bob suggested 'Summer Vibes' because it's catchy, but Alice wanted something unique. They ultimately decided on 'Beach Beats' for its playful tone."

Gets fragmented into:
- "Bob suggested Summer Vibes"
- "Alice wanted something unique"
- "They decided on Beach Beats"

Query "Why did they choose Beach Beats?" and you might get "They decided on Beach Beats" - which answers nothing. The reasoning chain is gone.

## Narrative Extraction

Hindsight takes a different approach. Instead of sentence-level fragments, it uses coarse-grained chunking to produce 2-5 comprehensive facts per conversation. Each fact is narrative and self-contained, preserving the pragmatic flow.

From the same conversation, Hindsight extracts something like:

> "Alice and Bob chose 'Beach Beats' as their summer party playlist name. Bob initially suggested 'Summer Vibes' for its catchiness, but Alice preferred something unique. They settled on 'Beach Beats' because of its playful tone."

One fact. Complete context. The reasoning chain survives.

## What Gets Extracted

Hindsight captures multiple dimensions beyond surface statements:

| Dimension | Example |
|-----------|---------|
| **Core facts** | Alice joined Google in spring |
| **Emotional context** | She was thrilled about the opportunity |
| **Reasoning chains** | She chose it specifically for research opportunities |
| **Causal relationships** | The research focus caused her excitement |

From "Alice joined Google last spring and was thrilled about the research opportunities," a later query "Why did Alice join Google?" returns meaningful context - not just "Alice joined Google."

## The Extraction Pipeline

Under the hood, retain() runs content through six processing steps:

1. **Coreference resolution** - Identifies entity mentions across turns ("she" → "Alice")
2. **Temporal normalization** - Converts "last week" into absolute timestamps
3. **Participant attribution** - Determines who said what
4. **Reasoning preservation** - Maintains explicit justifications and cause-effect links
5. **Fact classification** - Assigns to world facts, experiences, opinions, or observations
6. **Entity extraction** - Identifies people, organizations, locations, products, concepts

Each extracted fact includes temporal ranges, confidence scores (for opinions), and embeddings for multi-modal retrieval.

## Context Guides Extraction

The `context` parameter isn't just metadata - it shapes what gets extracted.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Same content, different contexts
content = "Alice mentioned she's leaving Google. The team dynamics changed after the reorg."

# Career-focused extraction
client.retain(
    bank_id="advisor",
    content=content,
    context="career discussion"
)
# Extracts: Alice is leaving Google, potentially due to organizational changes

# Team dynamics focus
client.retain(
    bank_id="advisor",
    content=content,
    context="team health assessment"
)
# Extracts: Team dynamics shifted after reorganization, causing departures
```

Context tells the memory bank what to focus on and how to interpret ambiguous content. "Career discussion" emphasizes Alice's decision. "Team health assessment" emphasizes the organizational impact.

## Causal Links

Hindsight explicitly tracks cause-effect relationships. The knowledge graph maintains:

- **Causal links** - X caused Y, X enabled Y, X prevented Y
- **Semantic links** - Conceptually similar facts across time
- **Entity links** - Indirect connections through shared participants
- **Temporal links** - Proximity-weighted connections (exponential decay)

This means queries like "Why did Alice leave?" can trace through reasoning chains, not just pattern-match on keywords.

## World Facts vs Experiences

The extraction distinguishes between two fundamental categories:

| Type | What It Is | Example |
|------|------------|---------|
| **World** | Objective information received | "Alice works at Google" |
| **Experience** | Agent's own interactions | "I discussed Python with Alice" |

World facts are things the agent learned. Experiences are things the agent participated in. This distinction matters for retrieval - sometimes you want objective facts, sometimes you want interaction history.

```python
# Get only objective facts
results = client.recall(
    bank_id="advisor",
    query="Where does Alice work?",
    types=["world"]
)

# Get interaction history
results = client.recall(
    bank_id="advisor",
    query="What have I discussed with Alice?",
    types=["experience"]
)
```

## Why This Matters

I think the difference between fragment-based and narrative-based extraction becomes obvious at query time. Fragment-based systems return statements. Narrative-based systems return understanding.

Ask "What's the relationship between Alice and Bob's project?" A fragment system might return:
- "Alice works on the project"
- "Bob works on the project"

A narrative system returns:
- "Alice and Bob collaborate on the project. Alice handles backend architecture while Bob focuses on ML integration. They've had disagreements about the data pipeline approach but resolved them in favor of Bob's streaming design."

Same underlying data. Dramatically different utility.

---

The extraction layer is where memory quality is won or lost. Narrative preservation means queries return context, not fragments. That's what makes downstream reasoning possible.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
