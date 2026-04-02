+++
date = '2026-04-02T08:00:00+01:00'
draft = false
title = 'Why 10 million tokens is the only memory benchmark that matters'
description = "Hindsight is #1 on BEAM at the 10M token tier. At that scale, context-stuffing dies and only real memory architecture survives."
tags = ["AI", "agents", "memory", "hindsight", "LLM", "benchmarks"]
+++

**TL;DR**: Memory benchmarks died when context windows hit 1M tokens - just dump everything in the prompt. BEAM tests at 10M where that trick fails. Hindsight scores 64.1% there, 58% ahead of the next system.

---

I spent months watching memory benchmarks become meaningless.

LoComo, LongMemEval - they were built when 128K was the frontier. They tested whether your system could retrieve the right fact from a few hundred thousand tokens of history. Useful, at the time.

Then Gemini shipped 1M context windows. Claude followed. And suddenly the dumbest possible strategy - `context.append(all_messages)` - started passing these benchmarks. No retrieval pipeline. No entity resolution. No temporal reasoning. Just brute-force the entire history into the prompt and let attention do the work.

The benchmarks didn't break. They just stopped measuring what they were supposed to measure. They became context window size tests wearing a memory evaluation costume.

## 10 million tokens changes the game

[BEAM](https://arxiv.org/abs/2504.01076) tests memory across tiers from 500K to 10M tokens. The lower tiers are still gameable - a 1M window covers 500K easily. But at 10M, there's nowhere to hide. No production model has that context window, and even if it did, attention degrades catastrophically long before 10M tokens. The "just stuff it all in" approach physically cannot work.

At 10M, you're forced to do the thing memory systems are supposed to do: decide what matters, store it efficiently, and retrieve precisely what a query needs. No shortcuts.

Results at the 10M tier:

| System | Score |
|--------|-------|
| **Hindsight** | **64.1%** |
| Honcho | 40.6% |
| LIGHT baseline | 26.6% |
| RAG baseline | 24.9% |

23.5 points over second place. That's not an incremental win - it's a structural one.

## Where the gap actually comes from

The 24.9% RAG baseline tells a clear story. Standard RAG - chunk, embed, retrieve top-k, stuff into prompt - barely beats random at this scale. And I think the failure mode is specific enough to explain.

Take a query like "What did Alice say about the project deadline after the API spec changed?" Standard embedding search finds chunks semantically close to "project deadline." It retrieves every mention of deadlines across 10M tokens of history. Maybe the relevant one ranks high enough, maybe it doesn't. But even if it does, the chunk boundary likely split Alice's reasoning from her conclusion. You get the statement without the cause.

Honcho at 40.6% does better - it has retrieval beyond pure embedding similarity. But the gap to Hindsight is still massive. Here's what I think drives it:

**Four retrieval strategies, not one.** Hindsight runs semantic, BM25 keyword, graph traversal, and temporal filtering in parallel, then merges results via reciprocal rank fusion. "Alice" is a proper noun - keyword search nails it where embedding search treats it as any other token. "After the API spec changed" is a temporal constraint - temporal filtering resolves it to a date range. Graph traversal connects Alice → her team → the API dependency. No single retrieval strategy handles all three dimensions of that query. Most systems only have one.

**Pre-computed observations.** This is the bigger architectural difference. When Hindsight ingests facts, a background consolidation process synthesizes observations - patterns across multiple facts. By the time you query "What's the status of Project Atlas?", the system already has a synthesized observation like "Project Atlas delayed due to unstable API requirements causing frontend blocking" with evidence links to the five specific facts that support it. RAG systems retrieve those five facts individually and hope the LLM connects them. Sometimes it does. At 10M tokens with retrieval noise from thousands of similar-looking chunks, often it doesn't.

**Entity resolution across 10M tokens.** "Alice," "Alice Chen," "Alice C." - across months of conversations, the same person gets referenced differently hundreds of times. Hindsight resolves these to canonical entities and builds a knowledge graph with typed edges (entity, temporal, semantic, causal). At 500K tokens, entity ambiguity is manageable. At 10M, without explicit resolution, your retrieval returns fragments about three different "Alices" and the LLM has no way to distinguish them.

The combination compounds. Graph traversal follows entity links to find causally related facts that embedding search misses. Temporal filtering scopes results to the right time window before semantic ranking even starts. Observations deliver pre-synthesized understanding instead of raw fragments. Each capability helps independently, but together they handle query dimensions that pure vector search fundamentally cannot.

## Why scores below 1M are noise

In my opinion, any memory benchmark that fits inside a model's context window is testing the wrong thing.

Here's the proof: at BEAM's 500K tier, the gap between systems shrinks dramatically. Context-stuffing competes with real memory architectures because the model can literally see everything. A system that spent engineering effort on entity resolution, temporal reasoning, and graph traversal scores similarly to one that just... passes all the tokens in.

That's not a memory evaluation. That's an LLM attention benchmark.

The 10M tier exists precisely because it eliminates this escape hatch. At 10M tokens, the only thing that determines your score is the quality of your memory architecture - how well you extract, how well you connect, how well you retrieve. There's no way to compensate for bad extraction by throwing more context at the model.

If you're evaluating memory systems for agents that will run in production - agents that accumulate months of interactions, thousands of conversations, millions of tokens of history - the only number that matters is the one where context-stuffing can't save you.

For Hindsight, that number is 64.1%.

---

Run BEAM against Hindsight locally, no API key needed. [Quick start](https://hindsight.vectorize.io/docs/quick-start/) | [BEAM paper](https://arxiv.org/abs/2504.01076) | [Leaderboard](https://hindsight.vectorize.io/beam/)
