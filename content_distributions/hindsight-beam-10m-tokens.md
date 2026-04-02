# Social Media Distribution - BEAM 10M Token Benchmark

## Twitter

### Option 1: Benchmark death angle
**Hook:**
Memory benchmarks died when context windows hit 1M tokens.

`context.append(all_messages)` passes LoComo and LongMemEval. No retrieval. No architecture. Just brute force.

**Pain points:**
BEAM fixes this — tests at 10M tokens where context-stuffing physically can't work:
• No model has a 10M context window
• Attention degrades way before that scale
• You actually have to decide what matters

**Introduce Hindsight:**
Hindsight at 10M tokens: 64.1%
Next best: 40.6%
RAG baseline: 24.9%

The gap comes from architecture: 4 parallel retrieval strategies, pre-computed observations, entity resolution across millions of tokens.

**Link:**
Why I think scores below 1M are noise → [blog link]

### Option 2: Architecture angle
**Hook:**
At 500K tokens, every memory system scores similarly.

At 10M tokens, RAG scores 24.9%. Hindsight scores 64.1%.

The difference is what happens between ingestion and retrieval.

**Pain points:**
RAG at 10M tokens:
• Embedding search retrieves every mention of "deadline" instead of the one that matters
• Chunk boundaries split reasoning from conclusion
• LLM reconstructs context from raw fragments — sometimes hits, often misses

**Introduce Hindsight:**
Hindsight runs 4 retrieval strategies in parallel (semantic + keyword + graph + temporal), pre-computes observations in the background, resolves entities across 10M tokens.

Not marginal differences. Structural ones.

**Link:**
[blog link]

---

## LinkedIn

### Option 1: Story → Problem → WTF → Solution

I spent months watching memory benchmarks become meaningless.

LoComo, LongMemEval — designed when 128K context was the frontier. They tested whether your system could retrieve the right fact from conversation history.

Then 1M context windows shipped. And `context.append(all_messages)` started passing these benchmarks. No retrieval pipeline. No entity resolution. Just dump everything in the prompt.

BEAM fixes this. It tests at 10 million tokens — where context-stuffing physically cannot work.

Results at the 10M tier:
→ Hindsight: 64.1%
→ Next best (Honcho): 40.6%
→ RAG baseline: 24.9%

23.5 points over second place. Not incremental — structural.

The gap comes from things that don't matter at 500K but become critical at 10M:
• 4 retrieval strategies running in parallel (semantic + keyword + graph + temporal)
• Pre-computed observations that synthesize patterns before queries happen
• Entity resolution across millions of tokens of history

Any benchmark that fits inside a context window is testing the wrong thing. The 10M tier is where memory architecture actually gets evaluated.

Full breakdown → [blog link]

### Option 2: Technical direct

Query: "What did Alice say about the deadline after the API spec changed?"

At 500K tokens, dump everything in the prompt. The model sees it all. Done.

At 10M tokens, that breaks. Now you need:
• Keyword search to nail "Alice" as a proper noun
• Temporal filtering to resolve "after the API spec changed" to a date range
• Graph traversal to connect Alice → her team → the API dependency
• Pre-computed synthesis so you're not hoping the LLM connects 5 scattered facts

No single retrieval strategy handles all three dimensions. Most systems only have one.

BEAM benchmark, 10M token tier:
Hindsight: 64.1% | Honcho: 40.6% | RAG: 24.9%

If your memory system only gets tested below 1M tokens, you're not testing memory. You're testing context window size.

[blog link]
