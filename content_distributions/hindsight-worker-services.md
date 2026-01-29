# Social Media - Worker Services: Running Background Memory Tasks at Scale

## Twitter/X

### Option 1 (Architecture split)
```
Your agent memory is slow at scale.

The problem: API processes handle both queries AND background extraction.
The fix: Dedicated workers.

API pods → query serving
Worker pods → fact extraction, consolidation, opinion formation

Scale independently.
Deploy via Helm in 1 command.

[link]
```

### Option 2 (Production scaling numbers)
```
Running Hindsight in production at scale:

Default: Internal worker (fine for most deployments)
Scale up: 3+ dedicated worker pods
Database: 150 connection pool for high concurrency
LLM: 32 concurrent calls max (prevents rate limits)

Workers claim tasks atomically from shared queue.
Scale workers without touching API layer.

[link]
```

### Option 3 (When to use workers)
```
When do you need dedicated Hindsight workers?

Don't need:
→ <100 conversations/min
→ No bulk ingestion

Need:
→ Hundreds of agents
→ Thousands of messages/min
→ Batch document pipelines
→ Background jobs starving queries

Workers isolate workloads so extraction can't kill serving.

[link]
```

---

## LinkedIn

### Option 1 (Story format)
```
We hit a wall at 500 concurrent agents.

The symptom: API timeouts. Database connection pool saturated. Background extraction jobs competing with query serving for resources.

The pattern I've seen before in distributed systems: everything in one process works until it doesn't. Then you split workloads.

With Hindsight, the split is natural:

API layer:
- Serves recall/reflect queries
- Returns immediately on async operations
- Handles user-facing latency requirements

Worker layer:
- Processes batch_retain operations
- Runs observation consolidation
- Handles opinion formation
- Can scale independently

Deploy via Helm:
```bash
helm install hindsight oci://ghcr.io/vectorize-io/charts/hindsight \
  --set worker.enabled=true \
  --set worker.replicaCount=3
```

Three workers running, API layer freed up, connection pool no longer saturated.

But scaling workers exposed another bottleneck: database connections.

Each recall uses 2-4 connections (semantic search, graph traversal, reranking). Three workers processing 10 tasks each = 30 concurrent operations = ~120 connections. Default pool size: 20.

The fix:
```bash
HINDSIGHT_API_DB_POOL_MAX_SIZE=150
```

Calculate it: (workers × batch_size × connections_per_task) + API concurrency. Set pool size accordingly.

Next bottleneck: LLM rate limits. Workers making parallel extraction calls hitting provider throttling. Solution: global concurrency limit.

```bash
HINDSIGHT_API_LLM_MAX_CONCURRENT=32
```

All workers collectively won't exceed 32 concurrent LLM calls. Prevents cascading failures when the provider starts throttling.

Result: 500 agents, thousands of messages per minute, API latency stable, workers processing in the background.

Full deployment guide: [link]
```

### Option 2 (Direct technical value)
```
Scaling Hindsight to production workloads: dedicated workers.

By default, the API process runs an internal worker that polls for background tasks every 500ms. This works fine for most deployments - dozens of conversations per minute, occasional bulk ingestion.

It breaks down when:
- You're ingesting thousands of documents simultaneously
- Background jobs compete with query serving for database connections
- You need different scaling for ingestion vs retrieval

The solution: separate worker pods.

Architecture:
- API layer serves queries only
- Worker pods claim tasks from shared queue
- Each workload scales independently
- Task claiming is atomic (no duplicate processing)

Configuration that matters:

Database connections:
```bash
HINDSIGHT_API_DB_POOL_MAX_SIZE=100
```
Calculate as: (workers × batch_size × 4 connections_per_task) + API concurrency

LLM concurrency:
```bash
HINDSIGHT_API_LLM_MAX_CONCURRENT=32
```
Global limit prevents rate limit cascades across all workers

Worker tuning:
```bash
HINDSIGHT_API_WORKER_BATCH_SIZE=10  # Tasks per poll cycle
HINDSIGHT_API_WORKER_MAX_RETRIES=3  # Before marking failed
```

For large memory banks (millions of facts), retrieval algorithm matters:
- link_expansion (default): <100ms, fast graph expansion
- mpfp: 500ms+, thorough multi-hop reasoning
- bfs: simple but less effective

Stick with link_expansion unless debugging retrieval quality.

Performance tuning involves two independent dimensions:
- Budget (search depth): low | mid | high
- Max tokens (result size): 2048 | 4096 | 8192

Most queries work fine with budget="mid" and max_tokens=4096.

Monitoring metrics:
- Task queue depth (growing = workers can't keep up)
- Task processing time (spikes = database/LLM issues)
- Retry rate (high = systemic failures)
- DB connection pool utilization (near 100% = need more connections)

Workers let you scale memory operations independently from query serving. Deploy them when throughput demands isolation.

Technical breakdown: [link]
```

### Option 3 (Problem → WTF moment → Solution)
```
The problem: Your agent memory is slow.

You're running 200 agents. Each processes 50 conversations per day. That's 10,000 messages requiring fact extraction, entity linking, observation synthesis.

All happening in the API process. Background jobs compete with query serving. Database connection pool saturated. LLM concurrency limits hit. Timeouts everywhere.

The WTF moment: scale horizontally, add more API replicas, problem gets worse.

More replicas = more internal workers = more competition for shared resources (database, LLM provider). Connection pool thrashes. Rate limits cascade. The system falls over.

The fix: dedicated workers.

Separate pods that only process background tasks:
- batch_retain operations
- observation consolidation
- opinion formation

API layer only serves queries. Workers scale independently.

Deploy:
```bash
helm install hindsight oci://ghcr.io/vectorize-io/charts/hindsight \
  --set worker.enabled=true \
  --set worker.replicaCount=3
```

Three workers running. Queue depth drops. API latency stabilizes.

But you need to tune connection pooling:
```bash
HINDSIGHT_API_DB_POOL_MAX_SIZE=150
```

And LLM concurrency:
```bash
HINDSIGHT_API_LLM_MAX_CONCURRENT=32
```

Result: workers handle the heavy processing, API stays responsive, each workload scales independently.

This is the standard distributed systems pattern - split by workload type when a single process can't keep up.

Full guide to worker deployment: [link]
```
