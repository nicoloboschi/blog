+++
date = '2026-01-28T14:00:00+01:00'
draft = true
title = 'Worker services: running background memory tasks at scale'
tags = ["AI", "agents", "memory", "hindsight", "LLM", "distributed-systems"]
+++

**TL;DR**: By default, Hindsight runs all background tasks in the API process - fine for most deployments. For high-throughput production systems, dedicated worker pods separate ingestion from processing, handle async batch operations, and let you scale each workload independently.

---

## Why Separate Workers Matter

In a typical agent deployment, memory operations happen inline with your application - `retain()` blocks until facts are extracted, `reflect()` waits for opinion formation. This works fine when you're handling dozens of conversations per minute.

But when you scale up - hundreds of agents, thousands of messages per minute, bulk document ingestion pipelines - you hit bottlenecks. The API process can't keep up with both serving queries and running background extraction jobs. Database connection pools saturate. LLM concurrency limits get hit.

I've run into this pattern before with distributed systems: you start with a single process doing everything, it works until it doesn't, then you split read/write paths, then you split by workload type. With Hindsight, the workload split is natural: API serving vs background processing.

Workers solve three problems:

1. **Isolation**: Extraction jobs can't starve query serving
2. **Scaling**: Add workers without touching the API layer
3. **Resource allocation**: Heavy processing gets its own compute budget

## Default: Everything Runs In-Process

By default, `HINDSIGHT_API_WORKER_ENABLED=true` - the API process runs an internal worker that polls for background tasks. This is the right choice for most deployments.

When `retain()` completes, it queues a consolidation job. The internal worker picks it up, synthesizes observations, and updates the memory graph. Same for async batch operations - they enter a queue, the worker processes them.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# API process handles everything
client.retain(
    bank_id="my-agent",
    messages=[{"role": "user", "content": "Alice joined the payments team."}]
)
# Extraction happens inline, consolidation queued for worker
```

The worker polls the database every 500ms (configurable via `HINDSIGHT_API_WORKER_POLL_INTERVAL_MS`), claims up to 10 tasks per cycle (`HINDSIGHT_API_WORKER_BATCH_SIZE`), and processes them.

This model breaks down when:
- You're ingesting thousands of documents and bulk operations saturate the API
- Background jobs compete with query serving for database connections
- You need different scaling characteristics for ingestion vs retrieval

## Dedicated Worker Deployment

For production deployments at scale, run workers as separate pods:

```bash
helm install hindsight oci://ghcr.io/vectorize-io/charts/hindsight \
  --set worker.enabled=true \
  --set worker.replicaCount=3
```

This spawns 3 worker pods alongside the API. The API continues serving queries, workers handle all background processing.

Each worker:
- Polls the same task queue as the internal worker would
- Claims tasks atomically (no duplicate processing)
- Processes async batch operations, observation consolidation, opinion formation
- Retries failed tasks up to `HINDSIGHT_API_WORKER_MAX_RETRIES` (default: 3)

You can scale workers independently:

```bash
kubectl scale deployment hindsight-worker --replicas=10
```

This is useful when you're running a bulk ingestion job - spin up workers temporarily, process the backlog, scale back down.

## Async Batch Operations

The async flag on `retain_batch()` is what makes dedicated workers valuable. Without it, you're still waiting synchronously for extraction to complete.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

items = []
for doc in documents:
    items.append({
        "content": doc.text,
        "context": doc.metadata,
        "timestamp": doc.created_at
    })

# Fire-and-forget: returns immediately
client.retain_batch(
    bank_id="document-processor",
    items=items,
    retain_async=True
)
```

What happens:
1. API receives the batch, validates schema, returns immediately
2. Batch enters the task queue as a `batch_retain` operation
3. Workers claim the job and process items in chunks
4. Extraction, entity linking, graph updates happen in the background
5. When complete, consolidation jobs queue for observation synthesis

The operation returns an `operation_id` if you need to track completion. Poll the operations endpoint to watch it move from `pending` → `completed` or `failed`.

In my experience, batch sizes between 10-50 items work well. Beyond 50, you start hitting LLM context limits during extraction since the model sees relationships across items in the same batch.

## Background Consolidation

After `retain()` completes, observation consolidation runs automatically. The worker analyzes new facts against existing observations, creates new ones when patterns emerge, refines existing ones with new evidence.

Two configuration knobs matter here:

```bash
HINDSIGHT_API_CONSOLIDATION_BATCH_SIZE=50  # Memories per batch
HINDSIGHT_API_RETAIN_OBSERVATIONS_ASYNC=false  # Sync by default
```

By default, consolidation runs synchronously during `retain()` - observations update before the call returns. This gives you immediate consistency: new facts are reflected in entity summaries right away.

For high-throughput scenarios, set `RETAIN_OBSERVATIONS_ASYNC=true`. Consolidation moves to the background, `retain()` returns faster, workers handle the synthesis.

The tradeoff: eventual consistency. Facts are searchable immediately, but observations lag. If you're querying entities right after bulk ingestion, you might see stale summaries.

I prefer sync mode for interactive agents where users expect immediate updates. Async mode for batch pipelines where you're ingesting thousands of documents and can wait for consolidation to catch up.

## Scaling Database Connections

Workers compete for database connections. Each recall operation can use 2-4 connections (semantic search, graph traversal, reranking). If you're running 3 workers processing 10 tasks each, that's 30 concurrent operations potentially consuming 120 connections.

Database connection pooling prevents saturation:

```bash
HINDSIGHT_API_DB_POOL_MIN_SIZE=5
HINDSIGHT_API_DB_POOL_MAX_SIZE=100
HINDSIGHT_API_DB_COMMAND_TIMEOUT=60
HINDSIGHT_API_DB_ACQUIRE_TIMEOUT=30
```

The guidance from the docs: for high-concurrency workloads, increase `DB_POOL_MAX_SIZE`. Each concurrent recall/think operation can use 2-4 connections.

I've hit this limit before in production. Symptoms: timeouts during database acquisition, tasks retrying repeatedly, workers logging "failed to acquire connection" errors. The fix: bump `MAX_SIZE` to match expected concurrency.

Calculate it as: `(workers × batch_size × connections_per_task) + API concurrency`. For 3 workers processing 10 tasks each with 4 connections per task, plus 20 API queries, you need ~140 connections. Set `MAX_SIZE=150` for headroom.

## LLM Concurrency Limits

Workers make parallel LLM calls during extraction, consolidation, opinion formation. Without limits, you'll hit rate limits from your LLM provider or saturate local models.

```bash
HINDSIGHT_API_LLM_MAX_CONCURRENT=32  # Global limit
HINDSIGHT_API_RECALL_MAX_CONCURRENT=32  # Per worker
HINDSIGHT_API_RECALL_CONNECTION_BUDGET=4  # DB connections per recall
```

The global limit applies across all workers and API processes. If you set `LLM_MAX_CONCURRENT=32` and run 3 workers, they collectively won't exceed 32 concurrent LLM calls.

This prevents cascading failures when your LLM provider starts throttling. Instead of all workers hammering the API and getting rate-limited, they queue requests and process within the concurrency budget.

For local models (like rerankers), there's a separate limit:

```bash
HINDSIGHT_API_RERANKER_LOCAL_MAX_CONCURRENT=4  # Prevents CPU thrashing
HINDSIGHT_API_RERANKER_MAX_CANDIDATES=300  # Pre-filters before ranking
```

I learned this the hard way: running a local reranker without concurrency limits pegs CPU, context-switches explode, throughput drops. Setting `MAX_CONCURRENT=4` keeps the system stable.

## Performance Tuning for Large Memory Banks

When memory banks grow into millions of facts, retrieval performance matters. Two areas to tune: graph retrieval algorithms and search depth.

### Graph Retrieval Algorithms

Three options via `HINDSIGHT_API_GRAPH_RETRIEVER`:

**link_expansion** (default): Fast graph expansion from semantic seeds via entity co-occurrence and causal links. Target latency under 100ms.

**mpfp**: Multi-path fact propagation with iterative traversal. More thorough, slower - useful when you need deep multi-hop reasoning.

**bfs**: Breadth-first search. Simple but less effective than link_expansion.

In my opinion, stick with `link_expansion` unless you're debugging retrieval quality issues. The performance difference is significant - 100ms vs 500ms+ on large graphs - and the quality gap is minimal for most queries.

### Retrieval Budget and Token Limits

Two independent dimensions control search performance:

```python
response = client.reflect(
    bank_id="my-agent",
    query="What are the deployment blockers?",
    budget="mid",  # low | mid | high
    max_tokens=4096  # 2048 | 4096 | 8192
)
```

**Budget** controls search depth - how many graph hops, how many candidate facts to consider. Higher budget = more thorough search = slower.

**Max tokens** controls result size - how many facts get passed to the LLM. Higher limit = more context = slower LLM processing.

These are independent. You can have `budget="high"` with `max_tokens=2048` - deep search, concise results. Or `budget="low"` with `max_tokens=8192` - shallow search, verbose results.

For most queries, `budget="mid"` and `max_tokens=4096` work well. Use `high` budget for complex multi-hop queries where you suspect relevant facts are distant in the graph.

## Monitoring Workers

When running dedicated workers, you need visibility into what they're doing. The operations endpoint shows queued and in-progress tasks:

```python
status = client.get_bank_status(bank_id="my-agent")

print(f"Pending extractions: {status.pending_extractions}")
print(f"Pending opinions: {status.pending_opinion_jobs}")
print(f"Pending observations: {status.pending_observations}")
```

This is useful during bulk ingestion - track progress, wait for completion before querying the newly ingested data.

Each worker logs task processing: claimed tasks, processing time, failures, retries. Set `HINDSIGHT_LOG_LEVEL=DEBUG` for detailed worker activity.

Metrics to watch:
- **Task queue depth**: Growing queue means workers can't keep up
- **Task processing time**: Sudden spikes indicate database or LLM issues
- **Retry rate**: High retries suggest transient failures (rate limits, timeouts)
- **Database connection pool utilization**: Near 100% means you need more connections

I set up alerts when queue depth exceeds 1000 (workers falling behind) or retry rate exceeds 10% (systemic issues). These catch problems before users notice.

## What's Not Covered Yet

The documentation doesn't include backup/restore tooling, offline migrations for air-gapped environments, or programmatic memory bank deletion. These are production features I'd expect for enterprise deployments.

For now, database backups handle disaster recovery - standard Postgres tooling works since Hindsight stores everything in relational tables and pgvector indexes.

For offline migrations (moving memory banks between air-gapped systems), you'd need to export the full graph - facts, entities, relationships, observations, opinions - and reimport. The schema is documented, but there's no official export/import tool yet.

Memory bank deletion is possible via direct database operations, but I'd prefer an API endpoint that handles cleanup properly (cascade deletes, index cleanup, task cancellation).

---

Dedicated workers separate ingestion from query serving, letting you scale each workload independently. Use the internal worker for most deployments, spin up dedicated worker pods when you hit throughput limits or need isolation. Tune database connections and LLM concurrency to match your workload. For large memory banks, stick with `link_expansion` retrieval and adjust search budget based on query complexity.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
