+++
date = '2026-01-16T10:00:00+01:00'
draft = false
title = 'File-based agent memory: great demo, good luck in prod'
description = "File-based agent memory benchmarks well on small datasets but hits context rot, multi-hop failures, and temporal query problems in production."
tags = ["AI", "agents", "memory", "LLM", "RAG", "context-window"]
+++

**TL;DR**: The "file is all you need" movement benchmarks well because benchmarks are small. In production, you'll hit context rot, multi-hop limitations, and temporal query problems. Files are a necessary foundation - but the claim they're sufficient is marketing. (Full disclosure: I sell the opposite, so I'm biased too.)

---

## The File Hype

There's a growing consensus in the agent community: files are the universal abstraction. Store conversations in markdown. Drop API specs into text files. Let agents grep their way to knowledge.

[LlamaIndex's recent piece](https://www.llamaindex.ai/blog/files-are-all-you-need) articulates this well: instead of building complex tool ecosystems, give agents a filesystem and basic operations (read, write, search). They learn capabilities from files containing instructions. They store history in markdown. They retrieve context through file search.

[Letta's benchmark](https://www.letta.com/blog/benchmarking-ai-agent-memory) shows a filesystem-based approach hitting 74% on LoCoMo (a conversational memory benchmark) - beating specialized memory tools at 68.5%. Their argument: agents are post-trained on coding tasks, so they're good at filesystem operations. Simpler tools = better performance.

This sounds compelling. And I think it's partially correct - for small-scale scenarios.

## Why Companies Push This Narrative

Here's what I notice: every company pushing "files are all you need" happens to sell file processing infrastructure.

LlamaIndex pitches their parsing pipeline (LlamaCloud Parse, Extract, Sheets) as the missing piece. "PDFs and Excel files aren't agent-ready - we make them agent-ready." Conveniently, their solution requires their paid parsing service.

[Turso's AgentFS](https://turso.tech/blog/agentfs) proposes treating agent state like a filesystem, implemented as a SQLite database. Guess what they sell? SQLite hosting.

Even Harrison Chase (LangChain CEO) is [pushing this narrative](https://x.com/hwchase17/status/2011814697889316930): "File systems are a natural and powerful way to represent an agent's state." LangChain sells agent infrastructure - and files are simpler to build tooling around than structured memory.

This isn't necessarily bad - commercial incentives can produce useful tools. But it does mean nobody's incentivized to highlight where the filesystem metaphor breaks down.

Full disclosure: I work on [Hindsight](https://hindsight.vectorize.io), a structured memory system for agents. So I have the opposite bias - I'm incentivized to argue files aren't enough. Take what follows with that context. I'll try to stick to what I've actually observed.

## The Context Window Reality

Here's the problem nobody wants to discuss:

**LLMs have ~1M token context windows. Enterprise codebases have several million tokens.** A typical monorepo spans thousands of files. You can't stuff it all in.

[Factory.ai's analysis](https://factory.ai/news/context-window-problem) puts it clearly: "This massive gap between the context that models can hold and the context required to work with real systems is a major bottleneck."

But wait, you might say. Agentic retrieval solves this. Give the agent a file map, let it pick what to read.

Sure. Until:
- Your repo has 2,500+ files and indexing degrades
- Files over 500KB get excluded
- The agent needs multi-hop reasoning across 15 files
- Your semantic search returns irrelevant matches because code isn't prose

## Context Rot Is Real

Even within the "official" context limits, performance degrades. The research calls this ["lost in the middle"](https://arxiv.org/abs/2307.03172) - models perform best when relevant information is at the beginning or end of context, and significantly worse when it's buried in the middle. (The original paper tested 4K-16K contexts; newer models claim improvements via better position encodings, though I still observe the pattern at scale.)

This creates a U-shaped performance curve: primacy bias (remember the start), recency bias (remember the end), and a dead zone in between. The larger your context, the bigger that dead zone.

I've seen this pattern repeatedly: an agent works great on a 50-file project, then falls apart on a 500-file codebase. Not because it hit token limits, but because relevant information lands in the attention dead zone.

## The Multi-Hop Problem

File-based approaches excel at single-hop retrieval. "Find the function that handles authentication" - grep, done.

Multi-hop reasoning is different:
1. Alice leads Project Atlas
2. Project Atlas uses Kubernetes
3. Kubernetes cluster had an outage Tuesday

Query: "Was Alice affected by infrastructure issues?"

A naive filesystem search finds chunks about Alice OR infrastructure. It can't traverse the relationship chain directly.

Now, there are file-based solutions to this:
- Embeddings that capture semantic relationships
- Hierarchical file structures encoding relationships
- Agent-driven iterative search (read Alice's file, find Atlas reference, follow it)

The iterative approach works - I've used it. The agent reads about Alice, sees "Project Atlas," searches for that, finds Kubernetes, follows that trail. But it costs multiple LLM calls and search operations per query. With pre-built entity graphs, that traversal is a single lookup.

The trade-off is build-time complexity vs query-time cost. Neither is objectively better - it depends on your query patterns and latency requirements.

## File Overhead (One Data Point)

[Manus](https://manus.im) reported that their early versions used a `todo.md` file that got constantly rewritten - roughly 30% token overhead on file management.

One example doesn't prove a pattern. But it illustrates a non-obvious cost: file-based state management requires constant read-write cycles that consume context budget. Whether this generalizes depends on your access patterns.

## What I've Found Works

In my experience, the filesystem metaphor works as a foundation. Whether you need more depends on your use case.

**Where files work well:**
- Storing raw conversation history
- Holding instruction sets and API specs
- Grep-based retrieval for exact matches
- Projects under ~100K tokens total context
- Single-hop queries with clear keywords

**Where I've needed additional structure:**
- Temporal queries ("what happened last week") - files don't parse dates
- High query volumes where iterative search latency adds up
- Long-running agents where context compaction matters
- Cross-session entity consistency

I don't have controlled benchmarks proving structured memory beats files at X scale threshold. What I have is repeated experience: file-based systems work until they don't, and the failure mode is usually gradual degradation rather than hard failure.

## The Benchmark Question

File-based approaches benchmark well on LoCoMo. But LoCoMo tests retrieval from conversational histories - structured dialogues with clear speaker attribution.

What I'd want to see benchmarked:
- Retrieval accuracy at 500K+ tokens of context
- Multi-hop queries requiring 3+ relationship traversals
- Temporal queries with relative date expressions
- Query latency at different corpus sizes

Without these, 74% on LoCoMo tells us files work for conversational memory at benchmark scale. It doesn't tell us much about enterprise codebases or long-horizon agents.

The "files are all you need" crowd isn't wrong about the simplicity benefits. Post-trained models do handle filesystem operations well. But I'm skeptical that benchmark performance on small datasets predicts production behavior.

In my experience, projects that start with "we'll just use files" often add:
- Vector search for semantic retrieval
- Some form of entity tracking
- Token budget management
- Compaction strategies

You could read this as "files are a good foundation that gets extended naturally." I read it as: files alone aren't enough, and everyone quietly knows it.

## The Actual Trade-off

Files work for: small contexts (under 100K tokens), few entities, single-hop queries. Keep it simple.

Files struggle with: large codebases, enterprise knowledge bases, long-horizon memory, temporal queries, high-frequency multi-hop reasoning.

The "files are all you need" crowd optimizes for the first category and benchmarks accordingly.

---

My actual take: files are necessary but not sufficient for production agents. The "all you need" framing is marketing from companies selling file infrastructure - just as my skepticism is informed by selling structured memory.

Start with files. You'll probably add vector search, entity tracking, and compaction eventually. The question isn't whether files work - they do. It's whether "just files" scales past demos. I don't think it does, but I'd love to see benchmarks that prove me wrong.
