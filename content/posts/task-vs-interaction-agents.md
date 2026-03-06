+++
date = '2026-03-04T10:00:00+01:00'
draft = false
title = 'Not all agents are the same: task agents vs interaction agents'
tags = ["AI", "agents", "memory", "LLM", "personalization"]
+++

> **TL;DR**: Task agents and interaction agents have fundamentally different memory requirements. Latency budgets, retrieval quality bars, and even the question of *what to retrieve at all* behave differently enough that sharing the same stack is a mistake - and it fails in ways that are hard to attribute.

***

Most agent frameworks are built around task agents: do a job, return a result. When teams reuse the same stack for interaction agents (personalization, assistants, support), the problems don't show up as outages or errors. The system "works"; it just works noticeably worse than it should, and the gap is hard to pin on memory.

***

## Two kinds of agents

**Task agents** exist to complete a discrete job. Coding agents, research agents, data pipeline runners. The output is a PR, a report, a processed dataset. The conversation ends when the task ends.

**Interaction agents** exist to maintain a relationship over time. Personalization engines, personal assistants, customer support, coaching. They're not judged on one output but on how well the experience holds up over weeks or months.

The boundary is blurry. A coding agent that learns your style has interaction-agent properties. A support bot that dies after one session is basically a task agent with a chat UI. But the ends of the spectrum really do have different requirements.

***

## Latency

Task agents are async by design. A coding agent that takes 10 minutes to ship a feature is fine - you context-switch and come back. Memory retrieval can be slow, re-ranking can be expensive; it barely matters.

Interaction agents live inside real-time conversation. Memory retrieval runs before every response, on every message, for every concurrent user. The latency budget is tight and the cost compounds at scale. Expensive per-query steps - cross-encoder re-ranking, graph traversals, multi-hop lookups - that are totally reasonable for a task agent become hard to justify when they're happening thousands of times per second.

That creates pressure toward retrieval paths that are fast *by construction*. Not just fast after you micro-optimize for one query pattern, but structurally fast - pre-indexed, pre-aggregated, and designed for low latency.

***

## Search quality

For task agents, retrieval quality requirements are surprisingly forgiving. You're indexing a static, versioned corpus - a codebase, a document set, a database. Queries are well-scoped. If retrieval misses something important, the agent often gets told: the code doesn't compile, the test fails, the dashboard is wrong. There's a feedback signal.

Interaction agents retrieve from user knowledge - preferences, history, context, relationships. Two things make the quality bar much higher.

First, there's usually no feedback loop. A bad retrieval still produces a plausible response. The agent has no idea it pulled the wrong thing. The user gets an answer that fits *some* version of their profile, just not the current one. The failure is invisible.

Second, injecting irrelevant or stale user context is actively harmful in a way that missing a file in a codebase isn't. If you miss a relevant file, the output might be incomplete. If you inject a four-month-old preference into a personalization system, the output is confidently wrong in a way that erodes trust.

We had a user whose memory said they led a three-person team. In reality, they'd been running a twenty-person org for four months. Nothing contradicted anything - team size just never came up again. Every response was calibrated to a context that no longer existed. Retrieval was "working." The quality bar was just wrong for the problem.

***

## Knowing *what* to retrieve

This is the hardest difference, and it's the one most frameworks don't touch.

For a task agent, the retrieval query is usually obvious. "Fix this bug" → retrieve the relevant file, the error, the related tests. The task itself tells you what to look for. Retrieval is a fairly straightforward function of the input.

For an interaction agent, the retrieval query is a judgment call. A user says "recommend something for dinner." What do you retrieve? Dietary restrictions? Past orders? Current location? Time of day? Preferred cuisines? Budget signals from past behavior? All of the above?

The right answer depends on which aspects of the user's profile matter *for this specific request, right now* - and that's not derivable from the text alone. Task agents retrieve from a narrow, known space. Interaction agents retrieve from a multi-dimensional user model where relevance is contextual and changes every turn.

Most systems paper over this by retrieving broadly and letting the model sort it out. That works until the context window fills with low-signal user history, latency blows out, or the model starts hallucinating preferences that were never retrieved because they were ranked below the cutoff.

The bet I think is worth making: retrieval relevance is a write-time problem. If you structure what you know about the user during ingestion - categorizing facts, tagging by domain, tracking which attributes matter for which kinds of requests - the retrieval query at turn time becomes simpler and more reliable. You're not doing a broad similarity search over everything the user has ever said. You're querying a structured model that already knows which facts belong in which contexts.

The tradeoff is real. Write-time structure forces you to make inferences early, before you have much signal, and wrong inferences are harder to debug than wrong chunks. But broad retrieval at query time has its own failure mode: it scales poorly, and the model's ability to filter noise degrades as user history grows. At production scale, I think investing in write-time structure is the more defensible position.

***

## Error tolerance

Task agents fail loudly. Code doesn't compile, tests fail, dashboards 500. The agent sees the error and retries. Memory mistakes are often recoverable within the same session.

Interaction agents fail silently. Wrong context about a user still produces a coherent response. There's no built-in signal - the agent doesn't know it misfired, and the user often can't tell *why* it feels off until trust is already damaged.

This asymmetry should shape what you build. Task agent retrieval can afford to be approximate - misses are visible, recoverable, and don't compound across time. Interaction agent retrieval needs to be precise - a wrong retrieval doesn't just taint one response, it shifts the perceived relationship.

***

## What this implies for tooling

Task-agent tooling is mature. File systems, terminals, code interpreters, RAG over static corpora - that stack is well-understood.

Interaction-agent tooling is still catching up. The preference/memory layer - extracting, storing, and deduplicating user facts - is mostly solved at a basic level.

The harder problem is deciding *which subset* of those facts matters for *this* request, returning it fast, with no feedback loop to tell you when you got it wrong. Most stacks still punt that to "retrieve broadly and let the LLM deal with it (until the context window runs out)." 
That's the part that's still worth solving.
