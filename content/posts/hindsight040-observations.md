+++
date = '2026-01-27T18:00:00+01:00'
draft = false
title = 'From facts to insights: how observations work in Hindsight'
description = "Observations consolidate scattered facts into synthesized patterns via async LLM processing, with traceable evidence chains and mission-driven consolidation."
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Observations consolidate multiple facts into synthesized patterns via background LLM processing. They track evidence chains to supporting facts, run asynchronously to avoid blocking retain operations, and support separate LLM providers for cost optimization.

---

## The Fragment Problem

Agent memory systems that only retrieve facts fail to synthesize patterns. After ingesting meeting notes, stakeholder emails, and sprint retrospectives for weeks, querying about a specific project returns 40+ disconnected facts: scope changed in requirements review, backend team reported API delays, PM requested timeline extension, frontend blocked on API spec, stakeholder questioned delivery date.

Each fact is accurate. But there's no consolidation. The LLM receiving these fragments in the prompt must synthesize on every query. Sometimes it connects the pattern-project slipping due to API integration bottleneck. Sometimes it misses the signal entirely because relevant facts didn't score high enough in retrieval.

### Alternative Approaches

You could solve this with deeper reasoning in the critical path. Instead of just retrieving facts and passing them to the LLM, run a multi-step reasoning loop: retrieve facts, identify relationships, retrieve connected facts, synthesize patterns, validate against additional context, then generate the response.

This works. It produces better synthesis than single-pass retrieval. But it happens during the recall or reflect operation, which means every query waits for multiple LLM calls and retrieval rounds. A query that should take 200ms now takes 10-15 seconds-multiple LLM inference cycles plus retrieval operations compound quickly. For user-facing applications, that latency is unacceptable. For high-throughput agent systems processing hundreds of queries per minute, the cost becomes prohibitive both in time and money.

The other option is accepting that synthesis happens in the prompt. Retrieve 40 facts about the project, dump them in the context window, and trust the LLM to connect the dots. This is what most RAG systems do. It's fast-single retrieval operation, single LLM call. But reliability depends on retrieval quality. If the API spec change fact scores lower than the deadline extension fact, the LLM might miss the integration bottleneck pattern. You're also burning context window tokens on raw facts instead of consolidated insights.

### The Pre-Computation Solution

Observations take a different approach: run consolidation asynchronously after facts are stored, not during retrieval. When you retain information about a project status update, consolidation runs in the background analyzing how new facts relate to existing observations. By the time you query for that project, synthesis is already done.

This moves the expensive multi-step reasoning out of the critical path. Queries don't wait for pattern analysis-they retrieve pre-computed observations. The consolidation cost is amortized across all future queries instead of paid on every retrieval.

The tradeoff is eventual consistency. Observations aren't immediately available after retaining facts. For systems where synthesis can happen asynchronously (project tracking, knowledge base consolidation, agent learning), this works well. The most recent facts are still available as raw memories during the consolidation window, ensuring no data loss-just a delay before synthesis appears.

## Observations as a Memory Type

Hindsight stores facts in a knowledge graph with temporal metadata and entity relationships. Retrieval uses four strategies in parallel: semantic search, keyword matching, graph traversal, and temporal filtering.

Observations are synthesized knowledge extracted from multiple facts via LLM-based pattern recognition. They're stored as a distinct memory type alongside world and experience facts.

When you retain information about a team requesting more engineers, then later retain that the same team missed a sprint deadline, then later the PM mentions the API integration spec keeps changing, consolidation recognizes a pattern: team blocked by unstable API contract causing velocity issues.

Individual facts capture discrete events. Observations capture the trajectory. The system doesn't just store "Team requested more headcount" and separately "Team missed deadline." It synthesizes: "Team velocity degraded due to unstable API integration requirements."

## Consolidation Mechanism

Consolidation triggers after retain operations complete. The pipeline has five stages:

First, fact extraction runs on the incoming content via LLM. This produces individual world or experience memories depending on whether the content describes external events or agent actions.

Second, the system loads related observations based on entity overlap and semantic similarity. The HINDSIGHT_API_CONSOLIDATION_BATCH_SIZE parameter controls how many memories get loaded per batch during this phase. Default is 50 memories.

Third, pattern recognition analyzes whether newly extracted facts align with existing observations, contradict them, or form entirely new patterns. This is LLM-intensive-it requires reasoning across multiple facts to identify emergent patterns.

Fourth, the system either creates new observation records or updates existing ones. Updates include adding new evidence links and potentially revising the observation text to reflect evolved understanding.

Fifth, observations are stored with bidirectional references. Each observation maintains links to supporting fact IDs, and facts maintain back-references to observations they support.

The HINDSIGHT_API_ENABLE_OBSERVATIONS flag controls whether consolidation runs at all. Default is true. Consolidation runs asynchronously by default-retain operations return immediately and consolidation happens in the background. This is critical for production systems where retain latency matters more than immediate observation availability.

### Separate LLM Provider Configuration

Consolidation workloads differ from extraction and retrieval. Extraction needs speed. Consolidation needs deeper reasoning over larger context windows. The system supports dedicated LLM configuration for consolidation operations via HINDSIGHT_API_CONSOLIDATION_LLM_PROVIDER, HINDSIGHT_API_CONSOLIDATION_LLM_MODEL, HINDSIGHT_API_CONSOLIDATION_LLM_API_KEY, and HINDSIGHT_API_CONSOLIDATION_LLM_BASE_URL.

If consolidation-specific variables aren't set, the system falls back to general HINDSIGHT_API_LLM_* settings. This lets you route different operations to different providers based on their strengths. For example, you might run consolidation on Llama 3.1 70B via Groq for extremely fast inference since consolidation runs async and you care more about throughput than per-request latency. Meanwhile, reflect operations use Gemini 2.0 Flash for better reasoning quality where response accuracy matters more than raw speed. The async nature of consolidation means you can use slower but cheaper models without impacting user-facing latency.

## Evidence Tracking

Observations maintain bidirectional links to supporting facts. Each observation stores references to the fact IDs that contributed to its synthesis. When you retrieve an observation stating "Feature development blocked by unclear requirements," the system provides links to the supporting facts: PM requested clarification three times, design team waiting on wireframe approval, engineering unable to estimate complexity.

The evidence-based approach differs from confidence scores used in some agent memory systems. Instead of storing "Redis is excellent for caching (confidence: 0.85)" where the number indicates belief strength, observations store traceable links to the facts that led to the synthesis. Evidence is verifiable. Confidence scores aren't.

The evidence chain is auditable. If an observation seems incorrect, you can inspect the supporting facts to understand why the system made that connection. You can also traverse in the opposite direction-given a fact, find which observations it supports.

Retrieval supports filtering by memory type through the types parameter. You can request only world and experience facts, only observations, or all memory types. Default behavior returns all types.

## Why Keep Raw Facts?

If observations provide consolidated synthesis, why maintain raw facts at all? Three reasons.

First, observations are lossy by design. When consolidation synthesizes "Project delayed due to unstable API requirements" from five separate facts, those facts contain details that don't make it into the observation: which specific endpoints changed, who requested the changes, exact scope modifications, meeting timestamps where decisions were discussed. Raw facts preserve granularity that observations deliberately discard.

Second, the reflect operation's agentic iteration uses the evidence chain for deeper research. When an agent encounters an observation during reasoning, it can follow the evidence links back to supporting facts for verification or additional context. The agent can then go further-from facts to source documents if document_id references exist. This enables drill-down: observation → supporting facts → source documents. The agent starts with high-level synthesis and digs into specifics only when necessary.

Third, observations are eventually consistent. When you retain new facts, consolidation runs asynchronously. The most recent information exists only as raw facts until consolidation completes. For queries requiring the absolute latest data, raw facts provide ground truth. An observation might state "Feature development blocked by unclear requirements" based on facts from yesterday, but a new fact retained ten minutes ago shows requirements were finalized and approved. The observation will update during next consolidation, but raw facts have the current state now.

This is why the memory hierarchy exists: Mental Models → Observations → Raw Facts. The system prioritizes synthesized knowledge during reflect operations but maintains raw facts for verification, drill-down, and recency guarantees.

## Observation Evolution

Observations update as new facts arrive. The consolidation process classifies incoming facts relative to existing observations as supporting, contradicting, or unrelated.

Supporting facts add to the evidence set without changing the observation text. If an observation states "ML model integration requires additional infrastructure" and you retain another meeting where the team discussed compute costs, the fact gets linked as additional evidence.

Contradictory facts trigger refinement. The system doesn't discard the observation-it updates the text to reflect the evolved understanding. Consider a three-stage progression:

At T1, you retain that the new LLM-powered search feature improved user engagement by 30%. Consolidation creates observation: "LLM search feature driving engagement gains."

At T2, you retain that API costs spiked 5x and exceed budget projections. This contradicts the simple "engagement gains" narrative. Consolidation refines to: "LLM search improved engagement but API costs exceed budget by 400%."

At T3, you retain that the team switched to a cheaper model with 10% accuracy loss. The observation updates: "LLM search feature downgraded to lower-cost model after budget overrun."

The observation captures temporal progression. Vector search would return "LLM search improved engagement 30%" and "Switched to cheaper model" as disconnected facts with no causal relationship. Observations preserve the journey from initial success through cost issues to compromise.

## Mission-Driven Consolidation

The memory bank's mission parameter influences what patterns get synthesized during consolidation. Mission describes the bank's purpose and provides context for which relationships matter.

Consider the same facts stored in two banks with different missions. A delivery tracking bank with mission "Monitor project timelines and blockers" retains facts: backend API spec changed twice, frontend team waiting for final endpoints, PM extended deadline by 2 weeks, stakeholder expressed concerns about launch date.

A team health bank with mission "Identify collaboration issues and process problems" retains the same facts.

The delivery tracking bank synthesizes: "Project delayed due to unstable API requirements pushing timeline back."

The team health bank synthesizes: "Cross-team communication breakdown between backend and frontend causing rework."

Same underlying facts. Different consolidation based on what patterns align with each bank's stated purpose. The mission acts as a filter determining which relationships warrant observation creation.

Note that disposition traits-skepticism, literalism, empathy-only affect reflect operations, not consolidation. Disposition shapes how observations get interpreted during reasoning, not how they get created from facts.

## Retrieval and the Memory Hierarchy

Hindsight uses TEMPR (Temporal-Entity-Multi-Path-Retrieval) for recall operations. Four parallel retrieval strategies run simultaneously:

Semantic retrieval uses embedding similarity to find memories close to the query in vector space. BM25 keyword matching finds memories sharing significant terms with the query. Graph traversal follows entity relationships to discover connected memories. Temporal filtering prioritizes memories based on recency and time-based relevance.

Results from all four strategies are merged via reciprocal rank fusion, then reranked using a cross-encoder neural model. Memories appearing in multiple strategies score higher-consensus across retrieval methods indicates stronger relevance.

Observations participate in all four strategies. They have embeddings for semantic search, keywords for BM25, entity links for graph traversal, and timestamps for temporal filtering. From the retrieval system's perspective, observations are memories like any other.

During reflect operations, the system checks sources in a priority hierarchy: Mental Models → Observations → Raw Facts. Mental models are user-curated summaries covered in the next post. When mental models don't exist for a query, observations take precedence over raw facts.

Observations pack more context per token than raw facts. An observation synthesizing five facts delivers more information than retrieving those five facts individually. For queries with tight token budgets, this matters.

The budget parameter controls graph traversal depth and overall retrieval thoroughness. Low budget runs fast (~50ms) with focused results. Mid budget balances coverage and latency (~100ms). High budget enables deep graph exploration at the cost of higher latency (~300ms+).

## Performance Characteristics

### Async Consolidation Latency

Consolidation runs asynchronously-retain operations return immediately while consolidation happens in the background. This means observations synthesized from newly retained facts aren't immediately available for retrieval. If you retain information about a project status update and immediately query for patterns about that project, the new observation may not exist yet.

Consolidation typically completes within seconds for banks with thousands of facts. The delay depends on batch size, number of related observations that need loading, and LLM latency. This async behavior is essential for production systems where retain throughput matters. The tradeoff is eventual consistency-observations lag behind the most recently retained facts by the consolidation duration.

### Batch Processing

HINDSIGHT_API_CONSOLIDATION_BATCH_SIZE controls how many memories get loaded during the observation loading phase of consolidation. Default is 50 memories per batch.

Higher batch sizes reduce database round trips for banks with many related facts. If you're consolidating information about a project with hundreds of associated facts, batch size 100-200 can improve throughput. The tradeoff is higher memory usage per consolidation job.

Lower batch sizes reduce memory footprint but increase database query count. For banks with sparse fact distributions-most entities have fewer than 50 facts-default batch size is optimal.

### LLM Cost Structure

Consolidation runs incrementally-one LLM call per newly retained fact. When you retain a new fact, consolidation analyzes it against existing observations, decides whether to create a new observation or update an existing one, then stores the result. That fact is marked as processed and won't trigger consolidation again.

This is near real-time. A bank with 1000 facts doesn't require reprocessing all 1000 facts. Only new facts trigger consolidation. The CONSOLIDATION_BATCH_SIZE parameter controls how many related observations and facts get loaded as context when processing each new fact-not how many facts get processed per cycle.

Token consumption scales with the context loaded per consolidation run. If you have an entity with hundreds of related facts and observations, loading them all as context for pattern analysis produces large prompts. This is why consolidation supports dedicated LLM configuration-you can route consolidation to cheaper models like GPT-4o-mini or Claude Haiku while using more expensive models for time-sensitive recall and reflect operations.

Cost optimization: use smaller models for consolidation since it runs async and latency is less critical. Tuning CONSOLIDATION_BATCH_SIZE can reduce context size but risks missing relevant patterns. Disabling observations entirely (HINDSIGHT_API_ENABLE_OBSERVATIONS=false) eliminates consolidation costs for banks that don't need synthesis.

## What Breaks

Early versions ran multiple synthesis mechanisms in parallel. Opinions tracked beliefs with confidence scores. Entity summaries consolidated per-entity knowledge. The problem: they conflicted constantly. An observation would synthesize "Project timeline slipping due to API changes" while an opinion stated "Project on track for delivery" with 0.7 confidence. The agent was giving itself contradictory information.

The deeper issue was fragmented synthesis. Opinions formed during reflect operations based on whatever facts retrieval happened to surface. Entity summaries consolidated per-entity but weren't connected to broader patterns. Raw facts sat disconnected from both. Query for a project and you'd get an opinion about timeline risk, an entity summary about the team, and raw facts about recent changes-no unified view.

We tried reconciliation-having consolidation check for conflicting opinions and merge them. That made things worse. The reconciliation logic itself was LLM-based and introduced another failure mode: the LLM trying to resolve conflicts between synthesized knowledge produced even more hallucinated patterns.

Consolidation can produce incorrect observations. The LLM might misinterpret facts, synthesize relationships that don't exist, or miss important contradictions. When this happens, the observation pollutes future retrieval until consolidation runs again and hopefully fixes it.

Debugging wrong observations requires tracing the evidence chain. You retrieve the observation, follow the links to supporting facts, and figure out which fact or combination of facts caused the bad synthesis. Sometimes the facts themselves are correct but the pattern recognition failed. Sometimes a fact was extracted incorrectly during retain and the observation inherited that error.

The worst case for eventual consistency lag is when consolidation stalls. If the consolidation LLM is slow or unavailable, new facts accumulate without being synthesized. Banks with high retain volume can build up hundreds of unconsolidated facts. When consolidation finally catches up, it processes them in batches, which can produce observations that jump multiple states at once instead of evolving smoothly.

Edge case: what if two contradictory facts arrive in rapid succession before consolidation runs? The consolidation sees both simultaneously and has to decide which represents current state. It usually picks the more recent timestamp, but if timestamps are identical or missing, the LLM might synthesize a "conflicting information" observation instead of picking a side. You end up with observations that hedge: "Project may be delayed OR may meet original deadline." Not useful.

---

Observations consolidate facts in the background instead of during queries. They track evidence chains instead of confidence scores. They run asynchronously to avoid blocking retain operations. And they break in ways you only discover after running them in production.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
