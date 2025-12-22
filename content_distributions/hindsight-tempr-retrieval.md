# Social Media - Beyond Vector Search: How TEMPR Combines 4 Retrieval Strategies

## Twitter/X

### Option 1 (Problem → Solution)
```
Vector search fails on:
- Proper nouns ("Alice Chen" matches "Bob Smith")
- Multi-hop queries ("What does Alice's company build?")
- Temporal queries ("What happened last week?")

TEMPR runs 4 strategies in parallel:
→ Semantic (concepts)
→ BM25 (exact terms)
→ Graph (entity traversal)
→ Temporal (date filtering)

Results fuse via Reciprocal Rank Fusion. Memories found by multiple strategies rank highest.

This is how we made Hindsight the state-of-the-art for memory for ai agents.

[link]
```

### Option 2 (Technical hook)
```
RRF(memory) = Σ 1/(k + rank_i(memory))

This formula fuses 4 retrieval strategies without score calibration.

Semantic search finds concepts.
BM25 finds exact names.
Graph traversal follows entity connections.
Temporal search filters by date.

Cross-encoder reranks the top candidates.

Wrote about how TEMPR retrieval works in Hindsight:
[link]
```

### Option 3 (Short)
```
Why vector-only RAG fails:
- "Alice Chen" might match "Bob Smith"
- Can't traverse entity relationships
- No date filtering

TEMPR: 4 parallel strategies + RRF fusion + cross-encoder rerank.

+44 points on LongMemEval benchmarks.

[link]
```

---

## LinkedIn

### Option 1 (Technical story)
```
Vector similarity is not enough for agent memory.

I've been digging into Hindsight's retrieval system (TEMPR) and it runs 4 strategies in parallel:

1. Semantic search - conceptual matching via embeddings
2. BM25 - exact term matching for proper nouns and technical terms
3. Graph traversal - follows entity connections for multi-hop reasoning
4. Temporal search - parses dates and filters by time ranges

Results fuse using Reciprocal Rank Fusion:

RRF(memory) = Σ 1/(k + rank)

No score calibration needed. Memories appearing in multiple strategies get boosted.

Then a cross-encoder (ms-marco-MiniLM) reranks the top candidates.

On LongMemEval, this approach scored 83.6% vs 39.0% for full-context baseline. That's a 44.6-point improvement.

Each strategy catches what others miss:
- "Find TensorFlow mentions" → BM25 (exact match)
- "What does Alice's company do?" → Graph (multi-hop)
- "Updates from last spring" → Temporal (date filter)
- "Alice's job" → Semantic (paraphrase)

Wrote a technical breakdown: [link]
```

### Option 2 (Problem-focused)
```
Vector search works great until it doesn't.

Queries that break semantic-only retrieval:
- Proper nouns: "Alice Chen" might match "Bob Smith" because both are names
- Multi-hop: "What does Alice's company build?" needs entity traversal
- Temporal: "What happened last spring?" needs date parsing, not similarity

Hindsight's TEMPR runs 4 retrieval strategies in parallel, fuses with Reciprocal Rank Fusion, and reranks with a cross-encoder.

The result: +44 points on LongMemEval benchmarks.

Technical breakdown of how it works: [link]
```
