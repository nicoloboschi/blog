# Social Media - Document Upserting: Keeping Evolving Conversations Fresh

## Twitter/X

### Option 1 - Single (Problem → Solution)
```
Most memory systems are append-only.

Day 1: "I work at Acme"
Day 5: "I joined NewStartup"

Query "Where does user work?" → could return either. Or both.

Hindsight's document_id enables upsert:
• Same ID → replaces old memories
• New ID → appends normally

No duplicates. No conflicts.

[link]
```

### Option 2 - Single (Code-focused)
```
One parameter changes everything in agent memory:

retain(
    document_id="session-123",  # ← this
    messages=[...]
)

Same document_id = full replacement
New document_id = append

Your memories stay current as conversations evolve.

[link]
```

### Option 3 - Single (Pain point hook)
```
Built an agent with long-term memory?

You'll hit this problem fast: information changes, but append-only memory only grows.

User updates their job? Now you have two conflicting facts.

Solution: document_id for upsert semantics.

Same ID replaces. Different ID appends.

[link]
```

### Option 4 - Thread (Deep dive)
```
1/4
First issue everyone hits with agent memory: data staleness.

User says "I work at Acme" on day 1.
User says "I joined NewStartup" on day 5.

Append-only memory now has both. Query might return either.

2/4
The fix: document_id as an upsert key.

retain(
    document_id="user-profile",
    messages=[...]
)

Same document_id → replaces all previous memories
Different document_id → normal append

3/4
Why full replacement instead of merge?

Memories aren't raw text. They're extracted facts, entities, graph edges.

Partial merges break:
• Conflict resolution (which fact wins?)
• Temporal consistency
• Graph integrity

Full replacement is deterministic.

4/4
Practical patterns:

• Conversation sessions: retain full history with session ID
• Document sync: use doc path as document_id
• User profiles: replace on each update

Idempotent by design. Safe to retry.

[link]
```

### Option 5 - Single (Technical simplicity)
```
Upsert for agent memory in one line:

document_id="profile:user-123"

Same ID = update
New ID = insert

Conversations evolve. Profiles change. Documents update.

Your memories stay current without manual deduplication.

[link]
```

---

## LinkedIn

### Option 1 (Story → Problem → Solution)
```
First production issue I hit with agent memory: conflicting facts.

User tells agent on Monday: "I work at Acme Corp"
User tells agent on Friday: "I just started at NewStartup"

Query "Where does the user work?" might return either answer. Or both. The system has no way to know the second statement supersedes the first.

Append-only memory systems create this problem constantly. Information changes. Preferences evolve. Facts become outdated.

Hindsight solves this with document_id - an upsert key:

• Same document_id → completely replaces previous memories
• New document_id → normal append behavior

retain(
    document_id="employment-info",
    messages=[{"role": "user", "content": "I just joined NewStartup as CTO"}]
)

Old Acme Corp memories are gone. No duplicates. No conflicts.

The key insight: don't try to merge facts. Hindsight extracts atomic facts, entities, and graph edges from each retention. Partial merges break conflict resolution and graph integrity.

Full replacement is deterministic. Same input, same output. You always know exactly what memories exist under a document_id.

Use cases that work well:
• Evolving conversation sessions (retain full history each time)
• Document sync (use file path as document_id)
• User profile updates (replace on each change)

[link]
```

### Option 2 (Problem-focused)
```
Memory systems that only append create a hidden problem: data staleness.

Every retain() adds new memories. Nothing updates. Nothing replaces.

This breaks down in real conversations:

Day 1: "I work at Acme Corp"
Day 5: "I just started at NewStartup"

Now you have two conflicting employment facts. Query "Where does the user work?" and retrieval might return:
→ Just Acme (wrong, outdated)
→ Just NewStartup (correct, but got lucky)
→ Both (confusing, contradictory)

The solution is document_id as an upsert key:

retain(
    document_id="user-employment",
    messages=[current_info]
)

Same document_id = full replacement
Different document_id = append

Why full replacement instead of smart merging? Because memories aren't raw text - they're extracted facts, entities, and graph relationships. Partial merges create:
• Ambiguous conflict resolution
• Broken temporal consistency
• Dangling graph edges

Full replacement is atomic and deterministic.

Practical patterns:
• Use session ID for evolving conversations
• Use file path for document sync
• Use entity ID for profile updates

Simple concept. Significant practical impact.

[link]
```

### Option 3 (Short and punchy)
```
Append-only memory breaks when information changes.

User updates their job? Two conflicting facts.
User changes preference? Old one still there.
Document updates? Previous version lingers.

Hindsight's fix: document_id for upsert semantics.

Same ID replaces. Different ID appends.

No deduplication logic. No conflict resolution. Just clean, current memories.

[link]
```
