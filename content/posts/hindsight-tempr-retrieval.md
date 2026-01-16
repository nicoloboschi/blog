+++
date = '2025-12-16T11:00:00+01:00'
draft = false
title = 'Beyond vector search: how TEMPR combines 4 retrieval strategies'
tags = ["AI", "agents", "memory", "hindsight", "retrieval", "RAG"]
+++

**TL;DR**: TEMPR runs four retrieval strategies in parallel - semantic, keyword, graph, and temporal - then fuses results with Reciprocal Rank Fusion and reranks with a cross-encoder. Memories matching multiple strategies rank highest. On LongMemEval, this approach improved accuracy by 44.6 points over full-context baselines.

---

## The Problem with Vector-Only Search

Vector similarity works well for paraphrasing and conceptual matches. But it fails on:

- **Proper nouns**: "Alice Chen" might match "Bob Smith" because both are names
- **Indirect relationships**: "What does Alice's company do?" requires traversing Alice → Company → Products
- **Temporal queries**: "What happened last spring?" needs date filtering, not just semantic similarity

TEMPR solves this by running four retrieval strategies in parallel and fusing results.

## The Four Strategies

### 1. Semantic Search (Vector Similarity)

Standard embedding-based retrieval. Query and memories are encoded as vectors, scored by cosine similarity:

```
score = v_query · v_memory / (||v_query|| ||v_memory||)
```

Uses HNSW indexing via pgvector. Good for conceptual matches - "Alice's job" finds "Alice works as a software engineer" even without keyword overlap.

### 2. Keyword Search (BM25)

Full-text search using BM25 ranking over a GIN index. No embeddings involved - pure term frequency and inverse document frequency.

Best for:
- Proper nouns: "Google", "Alice Chen", "MIT"
- Technical terms: "PostgreSQL", "TensorFlow", "CUDA"
- Specific identifiers: error codes, product names, version numbers

You never miss results that mention exact terms.

### 3. Graph Traversal (Spreading Activation)

The memory graph connects entities through relationships. Graph retrieval uses breadth-first search with activation propagation - activation spreads along edges with decay.

Causal and entity edges get higher propagation weights (`μ(ℓ) > 1`), prioritizing explanatory connections.

Example: "What does Alice do?" → Alice (entity) → Google (employer) → Google's products (via company edge)

This enables multi-hop reasoning that neither semantic nor keyword search can handle.

### 4. Temporal Search

Parses time expressions and filters by occurrence dates. Uses hybrid parsing:
- Rule-based date normalization for common patterns
- Lightweight seq2seq fallback for complex expressions

Handles queries like "What happened last spring?" or "meetings from Q3 2024" by filtering memories against time intervals.

## Reciprocal Rank Fusion

After parallel execution, four ranked lists need merging. TEMPR uses Reciprocal Rank Fusion (RRF):

```
RRF(memory) = Σ 1/(k + rank_i(memory))
```

Where `rank_i` is the memory's position in each strategy's list, and `k` is a constant (typically 60).

Why RRF over score averaging?
- **No calibration needed**: Raw scores from different strategies aren't comparable
- **Robust to missing items**: If a memory doesn't appear in one list, it just contributes nothing
- **Rewards consensus**: Memories found by multiple strategies get boosted

A memory ranked #1 in two strategies beats a memory ranked #1 in one strategy.

## Cross-Encoder Reranking

RRF produces a fused ranking, but it's still based on individual strategy positions. The final step applies a neural cross-encoder (ms-marco-MiniLM-L-6-v2).

Unlike embeddings that encode query and memory separately, cross-encoders jointly encode both and output a relevance score. This models rich query-memory interactions learned from supervised ranking data.

The pipeline: 4 strategies → RRF fusion → top candidates → cross-encoder rerank → final results.

## Why This Works

Each strategy catches what others miss:

| Query Type | Best Strategy | Why Others Fail |
|-----------|---------------|-----------------|
| "What's Alice's job?" | Semantic | Paraphrasing |
| "Find mentions of TensorFlow" | BM25 | Exact term match |
| "What does Alice's company build?" | Graph | Multi-hop reasoning |
| "Updates from last week" | Temporal | Date filtering |

Memories matching multiple strategies rank highest. If "Alice works at Google as an ML engineer" appears in semantic (job query), BM25 (Google), and graph (Alice entity) results, it gets boosted by RRF.

## Benchmark Results

From the [Hindsight paper](https://arxiv.org/abs/2512.12818):

**LongMemEval**:
- Full-context baseline: 39.0%
- Hindsight (20B model): 83.6% (+44.6 points)
- Hindsight (larger models): 89.0-91.4%

**LoCoMo**:
- Hindsight: 83.18-89.61%
- Memobase: 75.78%
- Zep: 75.14%

The multi-strategy approach consistently outperforms single-strategy baselines.

## Using TEMPR in Code

You don't configure TEMPR directly - it runs automatically on every `recall()`. The `budget` parameter controls search depth:

```python
from hindsight_client import Hindsight

with Hindsight(base_url="http://localhost:8888") as client:
    # Low budget: faster, fewer candidates per strategy
    results = client.recall(
        bank_id="my-bank",
        query="What does Alice do at Google?",
        budget="low",
    )

    # High budget: thorough, more candidates, better for complex queries
    results = client.recall(
        bank_id="my-bank",
        query="What projects has Alice's team shipped since joining?",
        budget="high",
    )
```

The four strategies run in parallel, results fuse via RRF, and the cross-encoder reranks. You get the final ranked list.

---

Four strategies, each catching different query patterns. RRF fuses without calibration. Cross-encoder polishes the ranking. The result is retrieval that handles proper nouns, multi-hop reasoning, and temporal queries - not just semantic similarity.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
