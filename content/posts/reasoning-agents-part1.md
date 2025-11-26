+++
date = '2025-11-16T14:30:00+01:00'
draft = false
title = 'The Reasoning Agent: A Different Architecture for AI Systems (Part 1)'
tags = ["AI", "agents", "llm", "architecture"]
+++

**TL;DR**: AI agents should be split into two layers-reasoning agents (READ-only, gather context and decide) and execution agents (separate loop that validates and acts). This post explains why this architecture makes sense and when to use it. Part 2 covers implementation.

---

The AI agent ecosystem is drowning in tools. Every implementation follows the same pattern: create dozens of narrow functions (`get_user`, `list_orders`, `update_status`, `process_refund`) and let the LLM orchestrate them. It feels productive until you realize you're mixing two fundamentally different concerns: reasoning and execution.

I think we need to separate these into distinct layers: **reasoning agents** that read and decide, and **execution agents** that act with proper controls.

## What Is an AI Agent?

An **AI agent** is an autonomous system that perceives its environment, reasons about it, makes decisions, and takes actions to achieve goals-typically through iterative tool use and self-correction. This is different from a simple LLM wrapper or a fixed workflow. The key property: **the agent decides what to do next based on context, not a predetermined script**.

## The Current State

Right now, there are two dominant approaches:

**LLM Workflows**: Chain prompts together with fixed logic. Predictable, testable, completely rigid. You write code like:

```python
def process_support_ticket(ticket_id: str):
    category = llm.classify(ticket)
    if category == "billing":
        return handle_billing(ticket)
    response = llm.generate_response(ticket, context)
    return response
```

This works perfectly fine for narrow, deterministic use cases. **And that's okay**. If your problem is "classify tickets and route them," you don't need an agent. A workflow with LLM components for reasoning is the right solution.

But it's not an agent-it's a pipeline with LLM components. The issue is when engineers try to scale this approach to problems that need autonomous decision-making.

**Tool-Heavy Agents**: Give the agent a toolbox of 20-30 functions and let it figure out the sequence:

```typescript
const tools = [
  {name: "get_user", description: "Retrieve user by ID"},
  {name: "get_user_orders", description: "Get all orders for a user"},
  {name: "get_order_details", description: "Get details of order"},
  {name: "update_order_status", description: "Update order status"},
  {name: "process_refund", description: "Process a refund"},
  // ... 20 more tools
];
```

This has serious problems:
- **Tool explosion**: Every operation becomes a function. Hundreds of narrow tools.
- **Context bloat**: All tool descriptions in the prompt. More tools = less reasoning space.
- **Brittleness**: Add a column? Update 10 tools. Change logic? Rewrite functions.
- **Mixed concerns**: The agent both reasons ("should I refund?") and executes ("process the refund") in the same loop.

## RAG: Built for Humans, Not Agents

The bigger issue is that RAG (Retrieval-Augmented Generation) techniques evolved for deterministic systems, not autonomous agents.

Modern RAG is sophisticated: semantic search with vector embeddings, metadata filtering, graph RAG for relationship traversal. Engineers build complex pipelines:

```python
results = rag_system.search(
    query="find billing policies for enterprise customers",
    top_k=10,
    filters={"document_type": "policy", "category": "billing"},
    rerank=True
)
```

This works for user-facing search where a human reviews results. But agents don't work like that.

**The `top_k` parameter is suboptimal for agents**. It limits number of results, not amount of information. `top_k=10` might return 10 short paragraphs (500 characters) or 10 long documents (50,000 characters). The agent doesn't know what constraint it's actually under.

What agents actually need: **context budgets** (return up to 5,000 characters) and **quality thresholds** (stop when confidence drops below X). Some modern RAG systems support these, but critically, **the developer hardcodes these parameters**, not the agent. The agent can't say "I need more context for this complex query" or "quick answer is fine for this."

**This isn't a revolution-it's a refinement**. The core insight: **let the agent control search parameters, not the developer**. Instead of hardcoding `top_k=10`, give the agent a `depth` parameter. Instead of fixing `max_depth=2`, let the agent choose based on query complexity.

In my opinion, this is an evolutionary step. The techniques (vector search, graph traversal, reranking) are still valid. The interface changes: **agent-controlled search depth** instead of **developer-hardcoded top_k**.

## The Two-Layer Architecture

So far I've talked about problems with current approaches-tool-heavy agents, RAG systems built for humans. Now let's talk about the alternative.

The core idea: **separate reasoning from execution**. The reasoning agent is READ-only-it gathers context, reasons about what should happen, and proposes actions. A separate execution layer validates and acts with proper controls. Different loops, different permissions, different failure modes.

Here's the architecture:

**Layer 1: Reasoning Agent (READ-only)**
- Queries agent memory (unstructured data: policies, docs, conversations)
- Queries operational databases (structured data: customers, orders, tickets)
- Reasons about what should happen
- Submits decisions to execution layer

**Layer 2: Execution Agent (separate loop)**
- Receives decisions from reasoning agent
- Validates with business rules
- Executes actions with proper controls (idempotency, transactions, rollbacks)
- May have human-in-the-loop for approval
- Returns results/errors to reasoning agent

The reasoning agent never writes, updates, or deletes. It's READ-only. It gathers context, reasons, and decides. The execution layer handles everything that comes with making changes to the system.

### Why Separate Loops?

**Different granularity**: Reasoning agent operates at high frequency (read, reason, decide, repeat). Execution layer operates at lower frequency (validate, execute, monitor).

**Different permissions**: Reasoning agent has READ-only access. Execution layer has WRITE permissions with strict controls, rate limits, and validation.

**Different criticality**: If the reasoning agent makes a mistake, it might give a wrong answer. If the execution layer makes a mistake, it might charge a customer twice or delete production data. The risk profiles are completely different.

**Human-in-the-loop becomes feasible**: With separation, you can deploy the reasoning agent immediately with human approval for all actions. Humans review decisions before execution. As confidence builds, you automate more. This gradual rollout isn't possible when reasoning and execution are mixed.

## When This Doesn't Work

Let me be honest about when this approach fails.

### When Tool-Heavy Is Better

**Simple, narrow domains with deterministic logic**. If your problem is "check if invoice is overdue, send reminder email," you don't need a reasoning agent. A fixed workflow with 2-3 tools is simpler, faster, and more predictable.

**High-frequency, low-latency requirements**. If you need sub-100ms responses, the reasoning agent loop might be too slow. Multiple memory queries + LLM reasoning = 500-2000ms total. Tool-heavy with cached endpoints can be much faster.

**Highly regulated environments where every query must be audited**. The flexibility of reasoning agents (arbitrary queries) makes compliance harder. Fixed endpoints are easier to audit and certify.

**When the team lacks ML/LLM expertise**. Reasoning agents require tuning prompts, understanding LLM failure modes, and handling non-determinism. Tool-heavy workflows are more accessible to traditional backend engineers.

### Failure Modes of Reasoning Agents

**Latency cost**: The agent loop queries memory 3-5 times per request. Each query: 200-500ms. Add database queries (100-500ms each) and LLM reasoning (500-1000ms), and you're looking at 2-4 seconds per request.

For interactive use cases, this is acceptable. For high-throughput batch processing, it's a problem.

**Context window limits**: The reasoning agent accumulates context in its loop. Query memory → 5k chars. Query customers → 2k chars. Query tickets → 3k chars. With a 128k context window, you have room, but for complex reasoning with many iterations, you run out.

**Non-determinism**: LLMs are non-deterministic. The reasoning agent might query memory differently on retry, prioritize different information, or make different decisions with the same inputs. For some use cases, this is unacceptable.

**Cost**: Multiple LLM calls per request add up. If you're processing 1M requests/day, the reasoning agent might cost 10-100x more than tool-heavy workflows.

**Time-series data and streaming**: The reasoning agent architecture doesn't handle streaming data well. It's designed for batch queries ("what happened in the last 30 days?") and point-in-time reasoning ("should I approve this refund now?"). For real-time anomaly detection or continuous monitoring, you need different architectures (stream processing systems like Kafka/Flink).

### When You Should Stick with Tool-Heavy

Be honest with yourself:
- **Is your domain narrow and well-defined?** → Tool-heavy is simpler
- **Do you need sub-100ms latency?** → Tool-heavy with cached endpoints
- **Is determinism critical?** → Tool-heavy with fixed logic
- **Do you have <5 engineers and limited ML expertise?** → Tool-heavy is more maintainable
- **Is cost a major concern?** → Tool-heavy uses fewer LLM calls

The reasoning agent architecture makes sense when:
- Domain is complex and evolving
- You need flexible exploration of data
- Latency tolerance is >1-2 seconds
- You have ML/LLM expertise on the team
- The value of better decisions justifies the cost

Don't cargo-cult the architecture because it's novel. Evaluate your actual requirements.

## Conclusion

Split your AI system into two layers: reasoning agents (READ-only intelligence) and execution agents (validation and action with proper controls).

The reasoning agent:
- Gathers context from memory and databases
- Reasons about what should happen
- Submits decisions

The execution layer:
- Validates decisions
- Executes with proper controls (transactions, retries, monitoring)
- May have human-in-the-loop

This isn't about building more sophisticated agent loops. It's about recognizing that reasoning and execution are fundamentally different concerns with different requirements, permissions, and failure modes.

In my opinion, tool-heavy architectures where one agent tries to do everything mix concerns, fight against LLM strengths, and struggle to scale. But I could be wrong-the tool-heavy approach might evolve in ways I haven't considered. Time will tell.

**Next**: Part 2 will cover implementation-how to build the memory system, operational query tools, and execution layer with concrete examples and engineering trade-offs.
