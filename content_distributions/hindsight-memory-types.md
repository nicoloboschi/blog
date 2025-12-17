# Social Media - Memory Types in Hindsight: World, Experience, Opinion, Observation

## Twitter/X

### Option 1 (Problem → Solution)
```
Vector databases treat everything the same. Just embeddings.

But "Alice works at Google" and "I discussed Python with Alice" aren't the same kind of memory.

Hindsight separates:
- World: external facts
- Experience: what you did
- Opinion: beliefs with confidence
- Observation: entity profiles

Filter retrieval by epistemic type. Ask "what do I know?" vs "what have I done?" and get different results.

[link]
```

### Option 2 (Technical)
```
How Hindsight categorizes agent memory:

World → "Alice works at Google" (third-person facts)
Experience → "I recommended Python to Alice" (first-person history)
Opinion → "Alice is a strong hire" (0.72 confidence)
Observation → auto-generated entity profiles

Opinions evolve with evidence. High skepticism = slower confidence growth.

Different memory types, different retrieval filters.

[link]
```

### Option 3 (Short hook)
```
Your RAG system can't tell facts from opinions from experiences.

Hindsight can.

Four memory types. Filter by what you actually need. Stop treating "I know X" the same as "I did X."

[link]
```

---

## LinkedIn

### Option 1 (Cognitive angle)
```
Humans don't remember "Alice works at Google" the same way they remember "I told Alice about Python."

One is semantic memory. The other is episodic. Different brain systems. Different retrieval patterns.

RAG flattens everything into "similar text chunks." No distinction between fact, experience, or belief.

Hindsight keeps the epistemic structure:

World: objective facts ("Alice works at Google")
Experience: agent's own history ("I discussed Python with Alice")
Opinion: beliefs with confidence scores that evolve over time
Observation: auto-synthesized entity profiles

Why does this matter?

"What do I know about Alice?" → Returns world facts
"What have I discussed with Alice?" → Returns experiences
"What do I think about Alice?" → Returns opinions with confidence

Different questions deserve different memory types.

The confidence scores on opinions are particularly useful. An opinion might start at 0.85 and drop to 0.55 when contradictory evidence arrives. The agent's beliefs become traceable.

Full breakdown of each type: [link]
```

### Option 2 (Practical)
```
Building AI agents with memory? Here's what I learned about memory categorization.

Standard approach: everything goes into a vector database. Query returns "most similar" chunks.

Problem: when you ask "what have I discussed with the user?", you get facts mixed with past interactions mixed with old conclusions. No distinction.

Hindsight organizes memory into four types:

1. World - External facts the agent learned
2. Experience - What the agent actually did
3. Opinion - Beliefs with confidence scores (0.0-1.0)
4. Observation - Auto-generated entity summaries

Practical difference: you can filter retrieval by type.

Building a factual response? Filter to World.
Summarizing past interactions? Filter to Experience.
Showing certainty levels? Query Opinions.
Need a quick entity profile? Grab the Observation.

Opinions are the interesting part. They only form during reasoning (reflect()), not storage (retain()). And confidence changes as evidence accumulates.

Wrote about how each type works and when to use them: [link]
```
