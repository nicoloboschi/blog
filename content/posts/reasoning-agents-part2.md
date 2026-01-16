+++
date = '2025-11-18T14:30:00+01:00'
draft = true
title = 'Building reasoning agents: the READ agent (part 2)'
tags = ["AI", "agents", "llm", "implementation"]
+++

**TL;DR**: This post covers how to implement the READ-only reasoning agent-the memory system with agent-controlled search depth, conflict resolution, and operational query tools with JSON-to-SQL. Part 1 covered the architecture, Part 3 covers the execution layer.

---

In Part 1, I explained why reasoning agents should be READ-only and separate from execution. Now let's talk about how to build the READ agent.

The reasoning agent has two core tools:
1. **Agent memory**: Query unstructured data (policies, docs, conversations)
2. **Operational queries**: Query structured data (customers, orders, tickets)

This post covers both. Part 3 covers the execution layer that receives decisions and acts.

## Agent Memory: The World Model

The agent memory is a unified store for everything unstructured. This isn't a vector database with a fixed schema-it's a world model the reasoning agent can query with control over how the search happens.

### The Interface

```python
class AgentMemory:
    def query(self,
              prompt: str,
              depth: str = "balanced") -> MemoryResult:
        """
        Natural language query over all unstructured data

        Args:
            prompt: What to search for
            depth: Search depth strategy
                - "quick": Return immediately (~100-500ms, may miss context)
                - "balanced": Standard search with traversal (~500-2000ms)
                - "deep": Exhaustive search (~2-5s, thorough)
        """
        pass

    def store(self, content: str, metadata: dict = None):
        """Store new information with timestamp and source"""
        pass
```

### Memory System Architecture

Before diving into search depth and conflict resolution, here's how the memory system actually works under the hood.

The memory system has four layers:

**Storage Layer**: Hybrid persistence combining multiple databases based on data characteristics:
- Vector database (Pinecone, Weaviate, Qdrant) for semantic search over unstructured content
- Graph database (Neo4j, DGraph) for relationship traversal (policy → exception → approval flow)
- Traditional database (Postgres, MySQL) for structured metadata and timestamps

Why multiple databases? Different query patterns require different structures. Semantic search ("find similar policies") needs vectors. Relationship traversal ("what policies reference this exception?") needs graphs. Temporal queries ("what changed since last week?") need indexed timestamps.

**Query Processing Layer**: Translates natural language queries into execution plans:

```python
class QueryProcessor:
    def process(self, prompt: str, depth: str) -> QueryPlan:
        # Parse natural language to structured query
        parsed = self.llm.parse_query(prompt)

        # Determine which databases to query
        plan = QueryPlan()
        if parsed.needs_semantic_search:
            plan.add_step("vector_db", parsed.semantic_query)
        if parsed.needs_relationship_traversal:
            plan.add_step("graph_db", parsed.graph_query, hops=self._depth_to_hops(depth))
        if parsed.needs_temporal_filter:
            plan.add_step("metadata_db", parsed.time_filter)

        return plan
```

The query processor decides which databases to hit and in what order based on the prompt. "Find refund policies updated in November" might query metadata DB first (temporal filter), then vector DB (semantic search on results).

**Conflict Detection Layer**: Runs during query execution, comparing information sources:

```python
class ConflictDetector:
    def detect(self, results: list[Source]) -> list[Conflict]:
        conflicts = []

        # Group by topic using semantic similarity
        topic_groups = self._cluster_by_topic(results)

        for topic, sources in topic_groups.items():
            # Check for contradictions
            if self._has_contradictions(sources):
                conflicts.append(Conflict(
                    topic=topic,
                    sources=sources,
                    reason=self._explain_contradiction(sources)
                ))

        return conflicts
```

This layer doesn't resolve conflicts-it just flags them with metadata (timestamps, source types, authors). The reasoning agent handles resolution based on business logic.

**Completeness Measurement**: Estimates whether the search returned sufficient context:

```python
class CompletenessEstimator:
    def estimate(self, query: str, results: list[Source], depth: str) -> float:
        # Check coverage
        coverage = self._calculate_coverage(query, results)

        # Check if we hit search limits
        hit_limit = self._hit_budget_limit(depth)

        # Check semantic gaps
        gaps = self._find_semantic_gaps(query, results)

        if hit_limit and gaps:
            return 0.4  # Low completeness - needed to stop early with gaps
        elif gaps:
            return 0.7  # Some gaps but not budget-constrained
        else:
            return 1.0  # Complete
```

Completeness is a heuristic, not ground truth. The system estimates: "Did I return enough information to answer this query?" If completeness is low, the reasoning agent knows to query again with `depth="deep"`.

### Search Depth: Agent-Controlled Parameters

I said `top_k` is suboptimal. But there ARE still parameters-they're just different:

**Search depth** (not top_k): Trade latency for information thoroughness. The reasoning agent decides based on context:
- Quick answer needed? Use `depth="quick"`
- Complex decision? Use `depth="deep"`
- Most queries? Use `depth="balanced"` (default)

The memory system implements this by controlling:
- How many relationship hops to traverse (quick=1, balanced=2-3, deep=exhaustive)
- How much "time" to spend on semantic search
- Whether to check multiple embedding spaces or just one

**Information quantification**: Instead of "return 10 results," the memory system returns information until it hits a threshold:
- Character budget (e.g., "return up to 5,000 characters of relevant info")
- Relevance threshold (e.g., "stop when similarity drops below 0.7")
- Time budget (e.g., "spend max 2 seconds searching")

The reasoning agent doesn't specify these directly. The memory system uses them internally based on the `depth` parameter.

### How the Agent Learns to Tune Depth

Initially, you hardcode heuristics:

```python
def choose_depth(self, query_context: dict) -> str:
    if query_context["user_waiting"]:
        return "quick"
    elif query_context["high_value_decision"]:
        return "deep"
    else:
        return "balanced"
```

Over time, make it adaptive:

```python
class AdaptiveReasoningAgent:
    def choose_depth(self, query_context: dict) -> str:
        # Start with heuristic
        depth = self._initial_heuristic(query_context)

        # Learn from past: if similar queries needed deeper search, adjust
        similar_past = self._find_similar_queries(query_context)
        if similar_past and similar_past.needed_retry_with_deeper:
            depth = self._increase_depth(depth)

        return depth
```

The agent tracks: "When I used `quick` for this type of query, did I need to go back and query again with `deep`?"

**What happens when it chooses wrong?** The memory result includes a `completeness` indicator:

```python
class MemoryResult:
    information: str
    sources: list[Source]
    conflicts: list[Conflict]
    completeness: float  # 0.0-1.0
    suggested_followup: Optional[str]
```

If the agent chooses `quick` but completeness=0.4, it knows to query again with `deep`.

### Handling Conflicting Information

Conflicting information gets returned-both versions:

```python
class Conflict:
    topic: str
    sources: list[Source]
    reason: str

class Source:
    content: str
    timestamp: datetime
    source_id: str
    confidence: float
```

Example:

```python
result = memory.query("What's our refund policy?", depth="balanced")

# Might contain:
# sources: [
#   Source("Policy doc 2024-01-15: No refunds after 30 days", ...),
#   Source("CEO email 2024-11-01: Extended to 60 days for Q4", ...)
# ]
# conflicts: [Conflict(topic="refund_window", ...)]
```

The reasoning agent sees both sources with timestamps and decides: "The November email is more recent, use 60-day policy."

**When business logic is more complex than timestamps:**

```python
def resolve_conflict(self, conflict: Conflict) -> Source:
    if conflict.topic == "refund_policy":
        # Official policy docs beat emails
        official = [s for s in conflict.sources if s.source_type == "policy_document"]
        if official:
            return official[0]

        # CEO overrides
        ceo = [s for s in conflict.sources if s.author_role == "CEO"]
        if ceo:
            return max(ceo, key=lambda s: s.timestamp)

        # Default: newest
        return max(conflict.sources, key=lambda s: s.timestamp)
```

This is why the reasoning agent does the resolving-business logic varies by domain.

**Advanced: Storing conflict resolutions**. When the reasoning agent resolves conflicts, you can store those in a decision log:

```python
if result.conflicts:
    resolution = self.llm.resolve_conflict(result.conflicts[0])
    self.decision_log.store({
        "conflict": result.conflicts[0],
        "resolution": resolution,
        "reasoning": "Used most recent policy dated 2024-11-01"
    })
```

Next time, the agent can check: "How did we resolve this before?"

### Memory Queries in the Agent Loop

Memory queries happen INSIDE the reasoning agent's loop. The agent doesn't query once and decide-it queries, reasons, queries again, iterates:

```python
class ReasoningAgent:
    def process_request(self, user_request: str):
        context = {"request": user_request}

        while not self._has_enough_context(context):
            # Query memory based on current understanding
            if self._needs_policy_context(context):
                policy = self.memory.query("relevant policies", depth="balanced")
                context["policy"] = policy

            # Found conflicts? Query for clarification
            if policy.conflicts:
                clarification = self.memory.query(
                    f"Which policy is current: {policy.conflicts[0].topic}?",
                    depth="deep"
                )
                context["policy_clarification"] = clarification

            # Reason about whether we have enough
            reasoning = self.llm.reason(context)
            if reasoning.needs_more_info:
                continue
            else:
                break

        return self._make_decision(context)
```

The agent might query memory 3-5 times in one request, each time refining based on what it learned.

## Operational Queries: Scoped Tools

Instead of 20 narrow functions (`get_user`, `list_orders`), give the reasoning agent **domain-scoped query tools** with clear boundaries but maximum flexibility:

```python
class QueryTickets:
    """Query support tickets - scoped to tickets domain"""
    def query(self, query_description: dict) -> list[dict]:
        """
        Agent provides JSON, tool converts to SQL
        Examples:
        - {"filters": {"status": "open", "priority": "high"}}
        - {"filters": {"customer_id": 456}, "aggregate": "count"}
        """
        sql = self._json_to_sql(query_description, allowed_tables=["tickets"])
        return self._execute_read_only(sql)

class QueryCustomers:
    """Query customer data - scoped to customers domain"""
    def query(self, query_description: dict) -> list[dict]:
        sql = self._json_to_sql(query_description, allowed_tables=["customers"])
        return self._execute_read_only(sql)
```

**Why scoped tools?**
- **Clear boundaries**: Agent can query tickets, not everything
- **Maximum flexibility within scope**: Any query pattern within the domain
- **Better context management**: Focused tool descriptions

### The Flexibility/Control Trade-off

You have three options:

**Option 1: Direct SQL** (max flexibility, less control)
```python
def query(self, sql: str) -> list[dict]:
    return self._execute_read_only(sql)
```

**Option 2: Scoped JSON-to-SQL** (balanced)
```python
def query(self, query_description: dict) -> list[dict]:
    sql = self._json_to_sql(query_description, allowed_tables=["tickets"])
    return self._execute_read_only(sql)
```

**Option 3: Fixed endpoints** (max control, no flexibility)
```python
def get_ticket(self, ticket_id: int) -> dict: ...
def list_open_tickets(self, limit: int) -> list[dict]: ...
```

**Recommendation**: Start with Option 2 (scoped JSON-to-SQL) for most use cases. It balances flexibility with control.

### The JSON-to-SQL Engineering Challenge

JSON-to-SQL is not straightforward. Expect these challenges:

**Complex joins**:
```python
query = {
    "base_table": "customers",
    "joins": [{"table": "orders", "on": "customers.id = orders.customer_id"}],
    "aggregates": [{"field": "orders.id", "operation": "count"}]
}
```

Your converter needs to handle join ordering, aggregation logic, GROUP BY properly.

**Query optimization**: The agent might specify inefficient patterns. Your converter needs optimization logic-recognize anti-patterns, rewrite for performance.

**Schema evolution**: When you add columns, does your JSON schema break? You need versioning and backwards compatibility.

**Security validation**: Preventing injection attacks. Your converter must parameterize queries, validate filter values, sanitize inputs.

**Practical approach**: Use existing libraries (SQLAlchemy, Prisma, Kysely). Expect 2-4 weeks of engineering for a robust converter.

**Alternative**: If this seems overwhelming, start with Option 3 (fixed endpoints). Once you understand query patterns, generalize to JSON-to-SQL.

## Conclusion

The READ-only reasoning agent needs two tools:

**Memory system**: Agent-controlled search depth (`quick`/`balanced`/`deep`), conflict resolution with business logic, iterative retrieval in the agent loop. Implementation requires hybrid storage (vector + graph + metadata), query processing, conflict detection, and completeness measurement.

**Operational queries**: Scoped JSON-to-SQL tools that balance flexibility with control. Start with fixed endpoints if JSON-to-SQL complexity is overwhelming. The engineering work-joins, optimization, schema evolution, security-is non-trivial.

Both tools are READ-only. The reasoning agent gathers context and makes decisions but never writes. Part 3 covers the execution layer-a separate loop that receives decisions, validates them, and acts with proper controls.

At [Vectorize.io](https://vectorize.io), we're building memory systems that agents can control and operational query tools with the right flexibility/control balance. More on that soon.
