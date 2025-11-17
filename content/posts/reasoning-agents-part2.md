+++
date = '2025-11-17T14:30:00+01:00'
draft = false
title = 'Building Reasoning Agents: Memory, Queries, and Execution (Part 2)'
tags = ["AI", "agents", "llm", "implementation"]
+++

**TL;DR**: This post covers how to implement reasoning agents-the memory system with agent-controlled search depth, operational query tools with JSON-to-SQL, and the execution layer with proper handoff and error handling. Part 1 covered the architecture and when to use it.

---

In Part 1, I explained why reasoning agents should be READ-only and separate from execution. Now let's talk about how to build them.

The reasoning agent has two core tools:
1. **Agent memory**: Query unstructured data (policies, docs, conversations)
2. **Operational queries**: Query structured data (customers, orders, tickets)

Then it hands off decisions to an **execution layer** that validates and acts.

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

## The Execution Layer

The reasoning agent decides what should happen. The execution layer makes it happen. These are separate agent loops.

### LLM-Based or Workflow Engine?

**Both, depending on complexity:**

For simple actions (send email, update field), use workflow engines:
```python
if decision["action"] == "send_reminder_email":
    temporal_client.start_workflow(SendReminderEmailWorkflow, args=decision)
```

For complex actions requiring reasoning (decide refund amount with rules), use another LLM-based agent:
```python
if decision["action"] == "process_refund":
    execution_agent = RefundExecutionAgent(permissions=["write_to_payments"])
    result = execution_agent.execute(action="process_refund", context=decision)
```

**Hybrid**: Use LLM agent to interpret the decision and decide which workflow to trigger.

### Parsing Decisions and Handling Ambiguity

The reasoning agent submits decisions as structured data, but these decisions might be ambiguous or incomplete. The execution layer needs validation logic before acting.

**Decision parsing**:

```python
class ExecutionLayer:
    def parse_decision(self, decision: Decision) -> ExecutionPlan:
        # Validate required fields
        if not self._validate_required_fields(decision):
            return ValidationError("Missing required parameters")

        # Check parameter types and constraints
        if decision.action == "process_refund":
            if not isinstance(decision.parameters.get("amount"), (int, float)):
                return ValidationError("amount must be numeric")
            if decision.parameters["amount"] <= 0:
                return ValidationError("amount must be positive")

        # Parse into execution plan
        return ExecutionPlan(
            action=decision.action,
            validated_parameters=self._validate_and_cast(decision.parameters),
            idempotency_key=self._generate_idempotency_key(decision)
        )
```

**Handling ambiguity**: Sometimes the reasoning agent's decision is underspecified. The execution layer can either:

1. **Reject and request clarification**:
```python
if decision.action == "send_email" and not decision.parameters.get("template_id"):
    return ExecutionResult(
        status="requires_clarification",
        error="Missing template_id for email. Available templates: reminder, receipt, followup"
    )
```

2. **Apply defaults with logging**:
```python
if not decision.parameters.get("priority"):
    decision.parameters["priority"] = "normal"
    self.audit_log.record("Applied default priority=normal")
```

3. **Use another LLM call to resolve**:
```python
if self._is_ambiguous(decision):
    clarified = self.clarification_agent.resolve(decision, context=decision.context)
    return self.execute(clarified)
```

Which strategy depends on risk. For low-risk actions (send notification), apply defaults. For high-risk actions (process payment), reject and request clarification.

**Versioning decisions**: As the reasoning agent evolves, decision format changes. The execution layer needs to handle multiple versions:

```python
class ExecutionLayer:
    def parse_decision(self, decision: Decision) -> ExecutionPlan:
        if decision.version == "1.0":
            return self._parse_v1(decision)
        elif decision.version == "2.0":
            return self._parse_v2(decision)
        else:
            return ValidationError(f"Unsupported decision version: {decision.version}")

    def _parse_v1(self, decision: Decision) -> ExecutionPlan:
        # Legacy format: action parameters were flat
        return ExecutionPlan(action=decision.action, params=decision.parameters)

    def _parse_v2(self, decision: Decision) -> ExecutionPlan:
        # New format: action parameters grouped by service
        return ExecutionPlan(
            action=decision.action,
            params=self._restructure_v2_params(decision.parameters)
        )
```

This versioning allows gradual migration. Old reasoning agents submit v1.0 decisions, new ones submit v2.0, execution layer handles both.

### Handoff Format

Use structured formats with versioning:

```python
class Decision(BaseModel):
    """Reasoning agent output"""
    action: str
    parameters: dict
    context: dict  # Why this decision
    confidence: float
    reasoning: str
    version: str = "1.0"

class ExecutionResult(BaseModel):
    """Execution layer response"""
    status: Literal["success", "failed", "pending", "requires_approval"]
    execution_id: str
    result: Optional[dict]
    error: Optional[str]
    retry_after: Optional[int]
```

### Error Handling

```python
result = self.execution_api.submit(decision)

if result.status == "failed":
    if result.error == "insufficient_funds":
        return self._escalate_to_human(decision, result.error)
    elif result.error == "temporary_service_outage":
        if result.retry_after:
            sleep(result.retry_after)
            return self.execution_api.submit(decision)
    else:
        self._log_error(decision, result)
        return self._escalate_to_human(decision, result.error)
```

### Learning from Failures

The reasoning agent can track execution failures:

```python
class ReasoningAgent:
    def __init__(self):
        self.failure_log = []

    def make_decision(self, context: dict) -> Decision:
        # Check: have I failed on similar context before?
        similar_failures = self._find_similar_failures(context)
        if similar_failures:
            constraints = self._extract_constraints_from_failures(similar_failures)
            decision = self.llm.reason(context, avoid=constraints)
        else:
            decision = self.llm.reason(context)
        return decision

    def handle_execution_result(self, decision: Decision, result: ExecutionResult):
        if result.status == "failed":
            self.failure_log.append({
                "context": decision.context,
                "decision": decision,
                "error": result.error
            })
```

This turns execution failures into training signal.

**Limitation**: This adds complexity. Many systems start without it and manually tune based on failure analysis. Implement after the basic architecture works.

## Operations: Monitoring, Debugging, Costs

Building the architecture is half the work. Operating it in production requires different tooling.

### Monitoring

**Reasoning agent metrics**:
- Query latency per layer (memory: avg 500ms, operational DB: avg 300ms)
- Memory completeness distribution (how often does agent retry with deeper search?)
- Conflict detection rate (how often does memory return conflicting info?)
- Decision confidence distribution (are decisions consistently high confidence or variable?)

```python
class ReasoningAgentMetrics:
    def record_query(self, query_type: str, latency_ms: int, completeness: float):
        self.metrics.histogram("query_latency_ms", latency_ms, tags={"type": query_type})
        self.metrics.gauge("query_completeness", completeness, tags={"type": query_type})

    def record_decision(self, decision: Decision):
        self.metrics.histogram("decision_confidence", decision.confidence)
        self.metrics.counter("decisions_by_action", tags={"action": decision.action})
```

**Execution layer metrics**:
- Execution success rate by action type
- Validation failure rate (how often are decisions rejected?)
- Human approval rate (what percentage requires human-in-the-loop?)
- Retry rate and eventual success after retry

Track these separately for reasoning vs execution. Different SLOs, different alerting thresholds.

### Debugging

When the reasoning agent makes bad decisions, debugging requires reconstructing the context:

```python
class DebugTrace:
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.queries = []
        self.decisions = []

    def record_query(self, query: str, results: MemoryResult):
        self.queries.append({
            "timestamp": datetime.now(),
            "query": query,
            "depth": results.depth,
            "completeness": results.completeness,
            "sources": [s.source_id for s in results.sources],
            "conflicts": results.conflicts
        })

    def record_decision(self, decision: Decision, context: dict):
        self.decisions.append({
            "timestamp": datetime.now(),
            "action": decision.action,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "context_summary": self._summarize_context(context)
        })

    def export(self) -> dict:
        return {
            "request_id": self.request_id,
            "queries": self.queries,
            "decisions": self.decisions,
            "total_latency_ms": self._calculate_total_latency()
        }
```

Store these traces in a debugging database (Elasticsearch, ClickHouse). When a decision goes wrong, query: "Show me all queries and intermediate reasoning for request X."

**Replay capability**: Once you have traces, you can replay requests:

```python
def replay_request(trace: DebugTrace, modified_memory: Optional[AgentMemory] = None):
    agent = ReasoningAgent(memory=modified_memory or original_memory)

    # Replay with same queries
    for query_record in trace.queries:
        result = agent.memory.query(query_record["query"], depth=query_record["depth"])

        # Compare results
        if result != query_record["original_result"]:
            print(f"Divergence detected in query: {query_record['query']}")
            print(f"Original: {query_record['original_result']}")
            print(f"Replay: {result}")
```

This helps debug: "If I update the memory with corrected policy, does the agent make the right decision?"

### Cost Estimates

Reasoning agents are expensive. LLM calls add up quickly.

**Per-request cost breakdown**:
- Memory queries: 3-5 LLM calls for query parsing/processing (~$0.01-0.05 per request)
- Reasoning: 1-2 LLM calls for decision-making (~$0.02-0.10 per request)
- Execution clarification: 0-1 LLM calls if needed (~$0-0.05 per request)
- **Total: $0.03-0.20 per request**

At 10,000 requests/day: $300-2,000/day = $9,000-60,000/month.

Compare to tool-heavy approach:
- 1-2 LLM calls total (tool selection + response generation)
- **Total: $0.01-0.03 per request**

At 10,000 requests/day: $100-300/day = $3,000-9,000/month.

**The reasoning agent costs 3-10x more**. This is acceptable when better decisions justify the cost (customer support with high refund values, complex enterprise sales workflows). Not acceptable for high-volume low-value use cases (simple notifications, basic routing).

**Cost optimization strategies**:
1. Cache memory queries (same query within 5 minutes returns cached result)
2. Use smaller models for query parsing (Haiku instead of Sonnet)
3. Batch operational queries when possible
4. Implement query result deduplication (if two queries return overlapping sources, reuse)

Example caching:

```python
class CachedMemory:
    def __init__(self, memory: AgentMemory, ttl_seconds: int = 300):
        self.memory = memory
        self.cache = {}
        self.ttl = ttl_seconds

    def query(self, prompt: str, depth: str) -> MemoryResult:
        cache_key = f"{prompt}:{depth}"

        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return result

        result = self.memory.query(prompt, depth)
        self.cache[cache_key] = (result, time.time())
        return result
```

With caching, cost drops 30-50% for repeated queries.

## Conclusion

Building reasoning agents requires:

**Memory system**: Agent-controlled search depth, conflict resolution with business logic, iterative retrieval in the agent loop.

**Operational queries**: Scoped JSON-to-SQL tools that balance flexibility with control. Acknowledge the engineering complexity-joins, optimization, schema evolution, security.

**Execution layer**: Separate loop (LLM agent or workflow engine) with structured handoff, error handling, and optional learning from failures.

This is months of engineering work. Start simple:
1. Build basic memory system with fixed `depth` heuristics
2. Start with fixed query endpoints, generalize to JSON-to-SQL later
3. Use workflow engine for execution, add learning later

The architecture is sound, but implementation has real complexity. Don't underestimate it.

At [Vectorize.io](https://vectorize.io), we're hitting these problems directly-building memory systems that agents can control, handling operational queries with the right flexibility/control balance, managing execution with proper validation. We'll be releasing solutions for these challenges soon.
