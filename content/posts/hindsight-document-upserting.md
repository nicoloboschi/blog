+++
date = '2025-12-22T18:00:00+01:00'
draft = false
title = 'Document upserting: keeping evolving conversations fresh'
tags = ["AI", "agents", "memory", "hindsight", "retrieval"]
+++

**TL;DR**: Memory systems that only append create duplicates when information changes. Hindsight's `document_id` parameter enables upsert semantics - same ID updates existing memories, new ID creates new ones. This keeps your memory bank consistent without manual deduplication.

---

## The Append-Only Problem

Most memory systems work like append-only logs. Every `retain()` call adds new memories. Nothing ever updates.

This breaks down fast in real conversations:

```
Day 1: User says "I work at Acme Corp"
Day 5: User says "I just started at NewStartup"
```

With append-only, you now have two conflicting facts. Query "Where does the user work?" and you might get either answer - or worse, both. The system has no way to know that the second statement supersedes the first.

In my experience, this is one of the first issues that surfaces when you deploy an agent with long-term memory. Information changes. People update their preferences. Projects evolve. Facts become outdated.

## Document ID as Upsert Key

Hindsight solves this with `document_id` - an optional identifier you pass to `retain()`. The behavior is simple:

- **Same document_id**: Completely replaces all memories from the previous call
- **New document_id**: Creates new memories (normal append behavior)
- **No document_id**: Auto-generates one, effectively always append

```python
from hindsight_client import Hindsight

with Hindsight(base_url="http://localhost:8888") as client:
    # First retention - creates memories
    client.retain(
        bank_id="user-profile",
        document_id="employment-info",
        messages=[
            {"role": "user", "content": "I work at Acme Corp as a senior engineer"}
        ]
    )

    # Same document_id - replaces previous memories
    client.retain(
        bank_id="user-profile",
        document_id="employment-info",
        messages=[
            {"role": "user", "content": "I just joined NewStartup as CTO"}
        ]
    )

    # Query returns only the updated info
    results = client.recall(
        bank_id="user-profile",
        query="Where does the user work?"
    )
    # Returns: NewStartup as CTO (not Acme Corp)
```

The old memories about Acme Corp are gone. No duplicates. No conflicts.

## Why Full Replacement?

You might wonder why Hindsight replaces all memories under a document_id rather than merging them. The reasoning comes down to fact extraction.

When you call `retain()`, Hindsight doesn't store your raw messages. It extracts atomic facts, entities, and relationships. A single conversation might generate dozens of interconnected memories.

Attempting to merge new facts with old ones creates several problems:

1. **Conflict resolution is ambiguous**: If old facts say "works at Acme" and new facts say "works at NewStartup", which wins? You need full context to decide.

2. **Temporal consistency breaks**: Facts extracted together have temporal relationships. Mixing facts from different extraction passes loses this coherence.

3. **Graph integrity suffers**: The knowledge graph links facts to each other. Partial updates can leave dangling edges or contradictory paths.

Full replacement is deterministic. Same input, same output. You always know exactly what memories exist under a document_id.

## Use Cases

### Evolving Conversation Sessions

The most common use case: updating memories as a conversation progresses.

```python
# Use conversation/session ID as document_id
session_id = "conv-abc-123"

# After each user message, re-retain the full conversation
client.retain(
    bank_id="agent-memory",
    document_id=session_id,
    messages=conversation_history  # Full history, not just latest
)
```

Each retention replaces the previous extraction. As the conversation evolves, so does the memory - without accumulating outdated interpretations.

### Document Sync

If you're ingesting external documents that update periodically (wikis, docs, specs), use the document path or ID:

```python
def sync_document(doc_path: str, content: str):
    client.retain(
        bank_id="knowledge-base",
        document_id=f"doc:{doc_path}",
        messages=[{"role": "system", "content": content}]
    )
```

Re-running sync with updated content replaces old facts. No need to track what changed.

### User Profile Updates

User preferences and profile data change over time:

```python
def update_user_profile(user_id: str, profile_text: str):
    client.retain(
        bank_id="user-profiles",
        document_id=f"profile:{user_id}",
        messages=[{"role": "user", "content": profile_text}]
    )
```

Each profile update keeps memories current without manual cleanup.

## What About Historical Accuracy?

A reasonable concern: if memories get replaced, don't you lose history?

It depends on what you need. Document upserting is for **current state** - what's true now. If you need **change history** - what was true before - use different document_ids:

```python
# Versioned approach for audit trails
version = datetime.now().isoformat()
client.retain(
    bank_id="audit-log",
    document_id=f"profile:{user_id}:v{version}",
    messages=[...]
)
```

Or keep the latest in one document and append history to another:

```python
# Current state (upsert)
client.retain(
    bank_id="user-data",
    document_id=f"current:{user_id}",
    messages=[profile_data]
)

# Historical record (append)
client.retain(
    bank_id="user-data",
    document_id=f"history:{user_id}:{timestamp}",
    messages=[profile_data]
)
```

## The Implementation

Under the hood, document_id maps to a stable identifier in the database. When you call `retain()` with an existing document_id:

1. All facts, entities, and graph edges from the previous document are marked for deletion
2. New extraction runs on the provided messages
3. New facts are inserted with the same document_id
4. Old facts are removed in a single transaction

This is fast - the extraction pipeline is optimized for real-time use cases. For most conversations, retention completes in hundreds of milliseconds.

By default, `retain()` runs synchronously - you call it and wait for completion. This is what you want when memories must be available immediately for the next query. But when you're batch-ingesting documents or don't need instant availability, you can run it asynchronously:

```python
# Sync (default) - blocks until complete
client.retain(bank_id="my-bank", document_id="doc-1", messages=[...])

# Async - returns immediately, processing happens in background
client.retain(bank_id="my-bank", document_id="doc-1", messages=[...], retain_async=True)
```

The upsert happens atomically either way. Queries during the update see either the old state or the new state, never a partial mix.

The graph connections get rebuilt from scratch. If the new content mentions the same entities, fresh relationship edges are created. If entities are no longer mentioned, their edges from this document disappear (though the entities themselves persist if referenced by other documents).

## Practical Considerations

**Choose document_ids carefully.** They're your update granularity. Too coarse (one ID for everything) and you can't update selectively. Too fine (one ID per message) and you lose the upsert benefit.

**Full conversation retention works best.** Rather than retaining individual messages, retain the full conversation with each update. This lets extraction see full context and produce more accurate facts.

**Idempotency is built-in.** Retaining the same content with the same document_id produces the same memories. Safe to retry on failure.

---

Document upserting is a simple concept with significant practical impact. In my experience building agents with long-term memory, data staleness is a constant battle. The `document_id` pattern - explicit identifiers for upsert semantics - handles the common case cleanly without complex deduplication logic.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
