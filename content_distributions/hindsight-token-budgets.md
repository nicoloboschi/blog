# Social Media - Token Budgets vs Top-K: A Better Way to Fill Context Windows

## Twitter/X

### Option 1 (Problem → Solution)
```
Top-k retrieval is broken for LLM agents.

"Return top 10 results" gives you:
- 2K tokens if chunks are small
- 8K tokens if chunks are large
- No way to predict context consumption

Your LLM doesn't care about result counts. It cares about tokens.

Hindsight uses token budgets instead. Specify max_tokens=4096, get exactly that much relevant content.

Greedy packing: iterate ranked results until the next would exceed budget.

[link]
```

### Option 2 (Technical)
```
How Hindsight fills context windows:

1. Run 4 retrieval strategies (semantic, BM25, graph, temporal)
2. Fuse with reciprocal rank fusion
3. Rerank with cross-encoder
4. Greedy pack until token budget exhausted

No arbitrary top-k. Just: "fill 4096 tokens with the best matches"

budget="high" → deeper search
max_tokens=4096 → result size

Orthogonal controls.

[link]
```

### Option 3 (Short)
```
Stop using top-k for RAG retrieval.

Your context window is measured in tokens, not results.

Hindsight: specify max_tokens, get exactly that much relevant content. Predictable consumption. Maximum density.

[link]
```

---

## LinkedIn

### Option 1 (Problem framing)
```
I've seen this pattern in every RAG system I've worked on:

retrieve(query, top_k=10)

Then someone asks: why 10? Why not 8? Why not 15?

The answer is usually "seemed reasonable."

The real constraint isn't result count. It's your LLM's context window. And context windows are measured in tokens, not chunks.

Hindsight replaces top-k with token budgets:

recall(query, max_tokens=4096)

The system runs retrieval (semantic + keyword + graph + temporal), ranks everything, then greedy-packs results until the next one would exceed your budget.

What this gives you:
- Predictable context consumption (you know exactly what you're spending)
- Maximum information density (no wasted context space)
- Clean integration with prompt building ("retrieval gets 4K, tools get 2K")

It also separates search depth from result size:
- budget="high" means deeper graph traversal
- max_tokens=4096 means how much comes back

These are independent. Deep search, compact results. Or shallow search, generous context.

In my opinion, top-k was always a proxy for what we actually wanted. Token budgets are the real thing.

[link]
```

### Option 2 (Direct value)
```
RAG retrieval has a units problem.

Your vector DB returns "top 10 results."
Your LLM accepts "up to 128K tokens."

These don't translate cleanly. 10 results might be 2K tokens or 20K tokens depending on chunk size.

Hindsight speaks tokens natively:

recall(query, max_tokens=4096)

Selection is greedy packing: iterate through relevance-ranked memories, include each one until adding the next would exceed the budget.

You can also layer budgets:
- max_tokens=4096 for core memories
- max_entity_tokens=1000 for entity profiles
- max_chunk_tokens=500 for original source text

Total: ~5.5K tokens, precisely allocated.

No more "top-k seemed right." Just: here's my context budget, fill it with the best content.

[link]
```
