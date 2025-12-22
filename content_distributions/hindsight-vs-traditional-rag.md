# Social Media - Hindsight vs Traditional RAG: What You Actually Get

## Twitter/X

### Option 1 (Problem framing)
```
Vector search can't answer: "Was Alice affected by any infrastructure issues?"

Your KB has:
- Alice leads Project Atlas
- Project Atlas uses Kubernetes
- Kubernetes had an outage Tuesday

RAG retrieves chunks about Alice OR infrastructure. Misses the connection.

Hindsight traverses: Alice → Project Atlas → Kubernetes → outage

Graph + entity resolution + temporal parsing. Not just embeddings.

[link]
```

### Option 2 (Technical summary)
```
What Hindsight adds over RAG:

Semantic search: both have it
+ BM25 keyword: exact names, technical terms
+ Graph traversal: multi-hop entity connections
+ Temporal parsing: "last spring" → date range filter

+ Entity resolution across conversations
+ Persistent opinions with confidence scores
+ Memory type separation (world/experience/opinion)

Complexity justified when you need it.

[link]
```

---

## LinkedIn

### Option 1 (Story format)
```
I spent years building RAG systems. Chunk documents, embed them, retrieve top-k by similarity.

It works well for static Q&A. "What's the refund policy?" finds the right section.

But semantic similarity has blind spots:

"What did Alice Chen say about the API redesign?"
→ Vector search finds chunks about API redesign. But "Alice Chen" needs exact matching, not semantic similarity.

"What happened last spring?"
→ Vector search has no concept of time. Can't parse date expressions.

"Was Alice affected by infrastructure issues?"
→ Can't traverse Alice → her project → the Kubernetes cluster → the outage.

Hindsight runs four retrieval strategies in parallel: semantic + BM25 keyword + graph traversal + temporal parsing. Results merge via reciprocal rank fusion.

In my opinion, the retrieval layer gets less attention than it deserves. Model improvements dominate the conversation, but how you structure and retrieve memory changes what's possible.

Full comparison: [link]
```

### Option 2 (Technical comparison)
```
RAG vs Hindsight - what's actually different:

Traditional RAG:
- Chunk documents
- Embed into vectors
- Retrieve top-k by cosine similarity
- Stateless (no memory between queries)

Hindsight:
- Four parallel retrieval strategies (semantic, keyword, graph, temporal)
- Entity resolution across conversations ("Alice" = "Alice Chen" = "Alice C.")
- Knowledge graph with entity/temporal/semantic/causal edges
- Memory types: world facts, experiences, opinions, entity observations
- Persistent opinions that evolve with evidence

Concrete example where it matters:

Query: "What happened with Project Atlas last quarter?"

RAG: Finds chunks semantically similar to "Project Atlas" and maybe containing "quarter"

Hindsight:
1. Parses "last quarter" into date range
2. Retrieves facts with occurrence time in that range
3. Traverses entity connections to Project Atlas
4. Returns temporally-filtered, entity-aware results

When to use which:

RAG: Static docs, simple Q&A, no entity tracking needed
Hindsight: Conversational agents, temporal queries, multi-hop reasoning, consistent agent personality

The complexity trade-off is real. Hindsight runs more machinery. Worth it when you need multi-hop reasoning, temporal queries, or persistent agent personality.

[link]
```
