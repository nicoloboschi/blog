+++
date = '2025-11-19T14:30:00+01:00'
draft = true
title = 'Building reasoning agents: the execution layer (part 3)'
tags = ["AI", "agents", "llm", "implementation"]
+++

**TL;DR**: The execution layer receives decisions from the reasoning agent, validates them, and acts with proper controls. This post covers LLM vs workflow engines, handling ambiguity, error handling, and operational concerns like monitoring and cost optimization. Part 2 covered the READ-only reasoning agent.

---

In Part 2, I covered the reasoning agent's tools: agent memory and operational queries. Now let's talk about what happens after the reasoning agent makes a decision.

The reasoning agent is READ-only. It gathers context, reasons, and submits decisions. The execution layer validates and acts. These are separate loops with different permissions, different criticality, and different failure modes.

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

The execution layer completes the reasoning agent architecture:

**Decision validation**: Parse and validate decisions before acting. Handle ambiguity with rejection, defaults, or clarification calls depending on risk.

**Execution options**: Use workflow engines for simple actions, LLM agents for complex ones, or hybrid approaches.

**Operations**: Monitor reasoning and execution separately. Build debug traces for replay capability. Understand cost implications-reasoning agents cost 3-10x more than tool-heavy approaches.

This is significant engineering work. Start with workflow engines for execution and manual debugging. Add LLM-based execution and automated tracing as the system matures.

At [Vectorize.io](https://vectorize.io), we're hitting these problems directly-building memory systems that agents can control, handling operational queries with the right flexibility/control balance, managing execution with proper validation. We'll be releasing solutions for these challenges soon.
