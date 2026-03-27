+++
date = '2026-01-30T10:00:00+01:00'
draft = false
title = 'Local, long term memory for OpenClaw agents'
description = "Hindsight's OpenClaw integration adds local, free long-term memory to your agents using auto-recall instead of unreliable tool-based retrieval."
tags = ["AI", "agents", "memory", "hindsight", "openclaw", "LLM"]
+++

**TL;DR**: Hindsight's OpenClaw integration gives your agents persistent memory that runs entirely on your machine, reuses the LLMs you're already paying for, and costs nothing extra. All data stays local - no third-party services, no additional API calls, no vendor lock-in.

---

## The Tool-Based Memory Problem

Most agent frameworks give memory to models as a tool - a function the LLM can call to search past conversations. The implementation looks like this:

```typescript
tools: [{
  name: "search_memory",
  description: "Search through conversation history",
  parameters: { query: "string" }
}]
```

The model receives this tool alongside others (web search, calculator, etc.) and decides when to use it. In theory, the model should call `search_memory` whenever it needs context from past interactions. In practice, this fails regularly.

Why? In our testing, **models don't use memory tools consistently**. They'll use web search tools reliably because "search the web" is a clear action. But deciding "I should check my memory before responding" requires metacognitive reasoning about what the model knows vs doesn't know. LLMs don't have reliable self-awareness of their knowledge gaps.

The result: agents that technically have memory but rarely access it. Users mention something important, the fact gets stored, and then the agent never retrieves it when needed. The memory system works perfectly - but it's invisible to the agent because the model forgot to call the tool.

## Memory as Context, Not Tools

The architectural fix: inject relevant memory automatically before every agent turn. Instead of asking the model "do you need memory?", you always provide recent, relevant context.

```python
# Tool-based (unreliable)
system_prompt + user_message + tools=[search_memory]

# Auto-recall (reliable)
system_prompt + <hindsight_memories>[relevant memories]</hindsight_memories> + user_message
```

This shifts memory from optional to automatic. The model doesn't need to realize it should check memory - the memory is already there.

The tradeoff: you're injecting context on every turn, which consumes tokens. But for conversational agents, this cost is worth the reliability gain. Better to spend 500 tokens on auto-injected context than have a model that ignores 10,000 stored facts because it didn't call a tool.

I think this is similar to how human memory works - you don't consciously decide "let me search my memories about this person" before talking to them. Relevant memories surface automatically as context for the conversation.

## Hindsight's OpenClaw Integration: Local, Free, and Zero Additional Cost

We released [Hindsight's OpenClaw integration](https://hindsight.vectorize.io/sdks/integrations/openclaw) today. OpenClaw (CLI: `clawdbot`) is an agent framework for building conversational bots across multiple platforms - Telegram, WhatsApp, Slack. The integration implements auto-recall with an embedded daemon approach.

The setup:

```bash
export OPENAI_API_KEY="sk-your-key"  # Your existing LLM key
clawdbot config set 'agents.defaults.models."openai/gpt-4o-mini"' '{}'
clawdbot plugins install @vectorize-io/hindsight-openclaw
clawdbot gateway
```

That's it. On first run, the plugin downloads `hindsight-embed` via `uvx`, starts a daemon, and initializes an embedded PostgreSQL instance. The plugin is free and open source (MIT licensed).

For full installation instructions and configuration options, see the [OpenClaw integration documentation](https://hindsight.vectorize.io/sdks/integrations/openclaw). If you're using an AI coding assistant, you can ask it to install the plugin for you.

**Auto-capture**: After each agent turn, the conversation is stored in your local PostgreSQL instance and processed asynchronously. Facts, entities, and relationships are extracted in the background without blocking the response.

**Auto-recall**: Before processing a message, up to 1024 tokens (balancing context relevance against token cost) of relevant memories are injected into context using `<hindsight_memories>` tags. The system ranks memories by semantic similarity and recency, surfacing the most relevant context for the current conversation.

The memories are injected as JSON with full metadata:

```xml
<hindsight_memories>
[
  {
    "chunk_id": "openclaw_default-session_12",
    "context": "",
    "document_id": "default-session",
    "id": "5f55f684-e6f5-46e3-9f5c-043bdf005511",
    "mentioned_at": "2026-01-30T11:07:33.211396+00:00",
    "occurred_end": "2025-01-29T23:14:30+00:00",
    "occurred_start": "2025-01-29T23:14:30+00:00",
    "tags": [],
    "text": "User prefers JSON responses for technical data. | When: 2026-01-30 | Involving: User",
    "type": "world"
  }
]
</hindsight_memories>
```

**Reuses your existing LLM**: The memory operations use whatever LLM provider you already configured for clawdbot. Already paying for OpenAI? The memory system uses that same API key. Running Ollama locally? Memory processing runs locally too. No separate memory API, no additional costs.

## The Embedded Daemon Architecture: Everything Local

The technical design uses a standalone daemon process that manages memory infrastructure on your machine:

**Single daemon, multiple agents**: All memory banks share one PostgreSQL instance running inside `hindsight-embed`. Isolation is handled through separate tables per bank ID. The 'openclaw' bank is created automatically when you start using it.

**Auto-managed lifecycle**: The daemon runs on port 8889. It can be configured to shut down after idle timeout or run indefinitely. The plugin handles start/stop automatically - you never interact with the daemon directly.

**Zero external dependencies**: PostgreSQL is embedded via [pg0](https://github.com/vectorize-io/pg0), a single-binary PostgreSQL distribution. No separate database installation, no cloud database, no connection strings, no credential management. Everything runs locally.

**Reuses your LLM provider**: The embed daemon works with whatever LLM you're already using with OpenClaw - OpenAI, Anthropic, Gemini, Groq, or Ollama. It reads from the same environment variables:

```bash
export OPENAI_API_KEY="sk-your-key"
# or
export ANTHROPIC_API_KEY="sk-ant-your-key"
# or
export GEMINI_API_KEY="your-key"
# or just run Ollama locally (no API key needed)
```

The daemon uses these for fact extraction and memory operations. You're not signing up for a separate memory service or paying for additional API access. If you're running Ollama, the entire stack - agent, memory, LLM - runs on your machine with zero external calls.

## Why Local-First Matters

Unlike hosted memory services (Mem0, Zep, etc.), Hindsight runs entirely local. The embedded daemon approach eliminates both operational complexity and external dependencies:

**Your data stays local**: All conversations, facts, entities, and relationships are stored in PostgreSQL running on your machine. Nothing is sent to third-party memory services. You own your data completely.

**No additional costs**: Traditional memory-as-a-service charges per API call, per GB stored, or per user. Hindsight is free and open source (MIT). The embedded daemon reuses whatever LLM provider you've already configured with clawdbot - OpenAI, Anthropic, Gemini, Groq, or Ollama. You pay only for the LLM calls you're already making. No hidden costs, no usage limits, no upsells.

**No vendor lock-in**: Your memory is stored in standard PostgreSQL. Export it anytime with `hindsight-embed memory export`. Switch to a different memory system? Your data is already in a portable format.

**Works offline (with Ollama)**: If you're running Ollama locally, the entire stack runs offline. No internet dependency beyond the initial plugin download.

**No infrastructure setup**: Traditional memory systems require deploying a database, configuring connection strings, managing credentials. With `hindsight-embed`, you run one command and everything is handled locally. The same setup works on macOS, Linux, and Windows.

This matters for teams that want to minimize external dependencies. Every third-party service is a potential failure point, a privacy concern, and an ongoing cost. Local-first means you're in control.

## Tool-Based vs Auto-Recall in Practice

To clarify the difference, here's the same scenario with both approaches:

**Tool-based memory**:
```
User: I prefer JSON responses
Agent: [Stores preference]
User: Give me the weather
Agent: The weather in San Francisco is sunny, 72°F
  (model didn't call search_memory, so it forgot the JSON preference)
```

**Auto-recall**:
```
User: I prefer JSON responses
Agent: [Stores preference]
User: Give me the weather
Agent sees:
<hindsight_memories>
[{"text": "User prefers JSON responses. | When: 2026-01-30 | Involving: User", "type": "world", ...}]
</hindsight_memories>
Agent: {"location": "San Francisco", "condition": "sunny", "temp": 72}
  (preference automatically injected, model uses it)
```

The tool-based approach requires the model to realize "I should check preferences before responding." The auto-recall approach injects preferences automatically, so the model doesn't need to remember to remember.

---

Agent memory doesn't need to be another SaaS dependency. The shift to automatic recall solves the reliability problem, while the local-first architecture solves the cost and privacy problems. Everything runs on your machine, reuses the LLM you're already paying for, and gives you full control over your data. Free, open source, and zero vendor lock-in.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight) | [OpenClaw integration docs](https://hindsight.vectorize.io/sdks/integrations/openclaw)
