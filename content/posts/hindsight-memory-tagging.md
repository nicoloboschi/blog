+++
date = '2026-01-26T12:00:00+01:00'
draft = true
title = 'Memory tagging in Hindsight: organizing and filtering at scale'
tags = ["AI", "agents", "memory", "hindsight", "LLM", "production"]
+++

**TL;DR**: Tags in Hindsight enable visibility scoping for filtering memories during recall and reflect. They're essential for multi-tenant systems where one memory bank serves multiple users. Tags work at item and document level, with flexible matching strategies.

---

## The Problem: Shared Banks, Isolated Views

Here's a scenario I've run into when building agent systems: you have a shared memory bank with documentation, policies, and historical data. But each user should only see their own conversations and preferences.

The naive solution? Create separate banks per user. But that's wasteful - you're duplicating shared documentation across every user's bank. Plus, managing hundreds or thousands of banks becomes an operational nightmare.

Tags solve this by adding visibility scoping within a single bank. You store everything in one place but filter what's visible during retrieval. User Alice only sees memories tagged for her. Shared documentation has no user-specific tags, so everyone sees it.

This is the classic namespace problem, solved at the memory layer.

## Two Levels of Tagging

Hindsight supports tags at two granularities:

### Item-Level Tags

When you store individual memories, you can tag them:

```python
client.retain(
    bank_id="support-system",
    content="Alice prefers Python examples in responses",
    tags=["user:alice", "preference"]
)

client.retain(
    bank_id="support-system",
    content="Bob requested Java documentation",
    tags=["user:bob", "request"]
)
```

Each fact gets its own tag set. This is useful when facts have different visibility requirements within the same content.

### Document-Level Tags

When storing multiple items in batch, you can tag the entire document:

```python
client.retain_batch(
    bank_id="support-system",
    items=[
        {"content": "Alice asked about async patterns"},
        {"content": "Discussed coroutines vs threads"},
        {"content": "Recommended asyncio for I/O-bound tasks"}
    ],
    document_id="conversation_2026-01-28",
    tags=["user:alice", "conversation", "technical"]
)
```

Every item in that batch inherits the document tags. This is cleaner when an entire conversation or document shares the same visibility scope.

In my experience, document-level tags work better for conversational agents where you're retaining full exchanges. Item-level tags are useful when extracting mixed-visibility facts from a single source.

## Filtering During Recall

The `recall()` operation supports tag-based filtering with two matching strategies:

```python
# Match ANY of the specified tags
results = client.recall(
    bank_id="support-system",
    query="What did the user ask about async?",
    tags=["user:alice", "conversation"],
    tags_match="any"
)
```

With `tags_match="any"`, memories tagged with either `user:alice` OR `conversation` are included. This is useful when you want broad retrieval across related categories.

```python
# Match ALL specified tags
results = client.recall(
    bank_id="support-system",
    query="What preferences does the user have?",
    tags=["user:alice", "preference"],
    tags_match="all"
)
```

With `tags_match="all"`, only memories with both `user:alice` AND `preference` tags are returned. This narrows results to the intersection of categories.

The matching strategy changes what you get back. I typically use `any` for discovery queries ("show me everything related to this user") and `all` for precise filtering ("only preferences for this user").

## Filtering During Reflect

The same filtering applies to `reflect()`:

```python
answer = client.reflect(
    bank_id="support-system",
    query="What does the user prefer for code examples?",
    tags=["user:alice"],
    tags_match="all"
)
```

During reflect, the agent only reasons over memories matching the tag criteria. This is critical for multi-tenant systems - you don't want Alice's preferences leaking into Bob's responses.

The difference between recall and reflect with tags:
- **Recall**: Returns filtered memories directly
- **Reflect**: Uses filtered memories as context for LLM reasoning

Reflect gives you semantic answers based on scoped knowledge. Recall gives you the raw facts within that scope.

## Tags and the Memory Hierarchy

Hindsight's retrieval hierarchy is mental models → observations → facts. Tags filter at all levels during both recall and reflect.

Here's how it works in practice:

**Facts with tags:**
```python
client.retain(
    bank_id="product-system",
    content="Customer 4721 reported slow query performance",
    tags=["customer:4721", "issue"]
)

client.retain(
    bank_id="product-system",
    content="Customer 4721 uses PostgreSQL 14.2",
    tags=["customer:4721", "infrastructure"]
)
```

**Observations synthesized from tagged facts:**

When observations form automatically after `retain()`, they consolidate facts. But observations don't explicitly inherit tags in the current implementation - the documentation doesn't specify tag propagation through the hierarchy.

What this means: if you filter by `tags=["customer:4721"]` during recall, you get the tagged facts. But observations synthesized from those facts might not appear unless they were explicitly tagged during creation.

In my opinion, this is an area where the tagging model could be clearer. I've found it safer to tag at the fact level and let recall handle filtering, rather than relying on tag inheritance through observations.

**Mental models with tags:**

Mental models are user-created summaries. You define them explicitly via API, and you can tag them:

```python
client.create_mental_model(
    bank_id="product-system",
    name="customer_profile_4721",
    query="customer:4721",
    tags=["customer:4721", "profile"]
)
```

This mental model would only surface during reflect if the tags match. Mental models bypass LLM synthesis, so they're the fastest retrieval path - and tagging them ensures they only appear in the right contexts.

## Timestamp Support: Another Dimension

Tags handle visibility scoping. Timestamps handle temporal scoping.

When you retain memories, you can specify when the event happened:

```python
from datetime import datetime

client.retain(
    bank_id="support-system",
    content="Alice reported login issues",
    timestamp=datetime(2026, 1, 15, 14, 30),
    tags=["user:alice", "issue"]
)
```

Hindsight tracks two temporal dimensions:
1. **When it happened** - The event timestamp you provide
2. **When you learned it** - Automatically tracked at retention time

This matters for queries like "What issues did Alice report in January?" The timestamp ensures temporal accuracy even when facts are learned later.

Combining tags and timestamps gives you two-dimensional filtering: scope by visibility, scope by time. This is essential for production systems where you need to answer questions like "What did this specific user do last week?"

## Tagging Strategies I've Used

Based on building multi-tenant agent systems, here are patterns that work:

### User Isolation
```python
tags=["user:{user_id}", "conversation"]
```

Every user interaction gets tagged with their ID. Shared documentation has no user tags, so it's visible to everyone.

### Feature Flagging
```python
tags=["feature:advanced", "public"]
```

Tag memories by feature availability. Users with access to advanced features see those memories during reflect. Others don't.

### Privacy Levels
```python
tags=["privacy:public"]
tags=["privacy:internal"]
tags=["privacy:restricted"]
```

Different privacy tiers for compliance. GDPR-sensitive data gets `privacy:restricted` and is only accessed when explicitly needed.

### Session Scoping
```python
tags=[f"session:{session_id}", f"user:{user_id}"]
```

Tag by both session and user. This lets you filter for "everything in this conversation" or "everything for this user across all conversations."

### Department/Role Scoping
```python
tags=["dept:engineering", "role:admin"]
```

In enterprise systems, scope by organizational structure. Only engineering sees engineering-specific memories. Admins see everything.

## Tag Naming Conventions

I've settled on these conventions:

1. **Use colons for namespacing**: `category:value` (e.g., `user:alice`, `privacy:internal`)
2. **Keep tags lowercase**: Avoids case-sensitivity issues during filtering
3. **Use hyphens for multi-word values**: `feature:multi-tenant` not `feature:multi_tenant`
4. **Be consistent with plurals**: Either always `user:` or always `users:`, not both

The namespace prefix matters because you'll eventually have hundreds of tags. Without structure, you'll end up with `alice`, `user_alice`, `alice_user`, and `user:alice` all meaning the same thing.

Consistency is more important than the specific convention. Pick one and enforce it at the application layer.

## Migration Patterns

If you're adding tags to an existing memory bank, you have a few options:

### Retrospective Tagging via Metadata

If you stored metadata during retention, you can use it to reconstruct tags:

```python
# Original retention without tags
client.retain(
    bank_id="system",
    content="Alice prefers Python",
    metadata={"user_id": "alice", "type": "preference"}
)

# Later, use metadata to filter
results = client.recall(
    bank_id="system",
    query="user preferences",
    metadata_filter={"user_id": "alice"}
)
```

This doesn't give you tag filtering at the Hindsight layer, but you can filter results in your application.

### Re-retention with Tags

For critical systems, you might re-retain memories with proper tags:

```python
# Retrieve existing memories
old_memories = client.recall(bank_id="system", query="*", limit=1000)

# Re-retain with tags
for memory in old_memories:
    user_id = extract_user_from_metadata(memory)
    client.retain(
        bank_id="system",
        content=memory.content,
        tags=[f"user:{user_id}"],
        timestamp=memory.timestamp
    )
```

This creates tagged duplicates. You'd then delete the old bank and use the new one. Not elegant, but sometimes necessary for production migrations.

### Parallel Banks During Migration

Run both old (untagged) and new (tagged) banks simultaneously. Direct new traffic to the tagged bank. Gradually migrate historical data. Switch cutover when the new bank has sufficient coverage.

This is the safest approach for live systems where downtime isn't acceptable.

## When Not to Use Tags

Tags add cognitive overhead. Here are cases where I skip them:

**Single-tenant systems**: If one agent serves one user, tags are overkill. Just use one bank.

**Homogeneous visibility**: If all memories have the same access rules, tags don't help. Use multiple banks instead.

**Over-tagging**: Don't tag everything. Tags are for filtering, not for semantic classification. "Python", "technical", "documentation" as tags won't help filtering - that's what embeddings handle during semantic search.

## Production Considerations

In production, tags affect query performance. Every tag filter adds a constraint to the retrieval query. With thousands of tags and millions of memories, this matters.

A few things I've noticed:

1. **Tag cardinality**: Low-cardinality tags (like `privacy:public`) filter faster than high-cardinality tags (like `session:abc123`). Database indexes work better with repeated values.

2. **Tag combination**: Filtering by one tag is fast. Filtering by five tags with `tags_match="all"` gets slower. Keep tag sets small for frequent queries.

3. **Mental models for hot paths**: If you're repeatedly querying the same scope (like "latest customer profile"), create a mental model tagged for that customer. It's pre-computed, so there's no LLM synthesis cost.

4. **Batch tagging**: Use document-level tags when possible. It's faster than tagging individual items, and it's cleaner in the database.

## Conclusion

Tags are namespaces for memory visibility. They let you store everything in one bank but filter what each user, session, or context sees. For multi-tenant systems, they're essential.

The pattern I use: tag by user/session for isolation, tag by privacy level for compliance, tag by feature for access control. Keep tag names consistent. Use document-level tags for conversations, item-level tags for mixed-visibility content.

In my opinion, tags are one of those features that seem simple until you start scaling. At 100 memories, they're optional. At 100,000 memories across 1,000 users, they're mandatory.

---

Learn more: [Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
