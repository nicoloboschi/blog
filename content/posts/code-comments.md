+++
date = '2025-11-05T15:05:30+01:00'
draft = false
title = 'Code Comments: Humans vs Agentic Code'
tags = ["AI", "coding-agents", "best-practices"]
+++

**TL;DR**: Code comments function as prompt boosters for agentic coding systems. When AI agents generate docs (javadoc, pydoc, docstrings), keeping them reduces feedback loops from 5-6 iterations to 1-2. Comments became the primary mechanism for context injection in AI-assisted development.

---

For decades, the software industry has been told that comments are a code smell. "Good code documents itself," they said. "If you need comments, your code isn't clean enough," they preached.

I believed this religiously. Robert C. Martin's *Clean Code* became my bible, particularly Chapter 4 on comments: "The proper use of comments is to compensate for our failure to express ourself in code." I spent years having conversations with junior developers about why their comments were redundant, showing them how to make their code clearer instead. I championed the idea that comments were technical debt.

And then AI coding agents arrived and forced me to question everything.

## The Old Testament of Clean Code

The anti-comment movement had solid reasoning. Comments lie. They rot. They become outdated the moment someone refactors the code without updating them. Everyone has seen this:

```python
# Increment the counter by 1
counter = counter + 2  # Someone changed this but forgot the comment
```

The solution was self-documenting code:

```python
# Bad
x = d * 24  # Convert days to hours

# Good
hours = days * HOURS_PER_DAY
```

This made sense. Code is the source of truth. Comments are just noise that gets out of sync. Write expressive code, and comments become unnecessary.

The industry took this to heart. Code reviews became comment-free zones. PRs with extensive comments were met with suggestions to "just make the code clearer." Comments became a last resort, especially in legacy codebases or distributed systems where the code could live in different repos and teams don't have time to document each nuance.

## Enter the AI Agents

Fast forward to 2024-2025. AI coding agents arrived, and here's the thing nobody talks about: **they don't just read comments-they generate them**.

When Claude Code writes a function, it adds docstrings. When it implements a class, it includes documentation. When it creates an API endpoint, it documents parameters and return types.

I used to delete all of that. "Clean code doesn't need comments," I'd think, and strip out the AI-generated docs.

Then I ran some experiments. Keeping AI-generated documentation reduced my feedback loops from 5-6 iterations to 1-2. The agent's own comments helped it understand the codebase better in the next session.

What I discovered: **code comments are essentially prompt boosters for agentic coding systems**. Every docstring, every inline comment, every parameter description is additional context that gets injected into the agent's prompt when it reads the code. More context = better responses = fewer iterations.

## What's Actually New: API Documentation is Valuable Again

Constraint comments-explaining why a batch size is 500 or a timeout is 30s-those were always good practice. That's not what changed.

What changed: **javadoc, pydoc, and API docs went from noise to signal**.

Ten years ago, this felt redundant:

```python
def calculate_user_score(user_id: str, time_range: tuple[datetime, datetime]) -> float:
    """
    Calculate the engagement score for a user within a time range.

    Args:
        user_id: Unique identifier for the user
        time_range: Tuple of (start_time, end_time) for the calculation period

    Returns:
        Float between 0.0 and 100.0 representing the engagement score

    Raises:
        UserNotFoundError: If the user_id doesn't exist
        InvalidTimeRangeError: If end_time is before start_time
    """
    # implementation
```

I would have deleted all of that. Type hints show the parameters. The function name is clear. Why repeat yourself?

But now this tells the agent:
- Score scale is 0-100
- time_range format
- What exceptions to handle

Without it, the agent guesses. Gets it wrong. More iterations.

More examples:

```java
/**
 * Processes payment transactions with idempotency guarantees.
 *
 * @param transactionId Must be a valid UUID v4
 * @param amount Positive decimal, max 2 decimal places, represents USD
 * @param idempotencyKey Client-provided key for request deduplication.
 *                       Same key within 24h returns cached response.
 * @return PaymentResult with transaction_id and status
 * @throws InsufficientFundsException if account balance < amount
 * @throws DuplicateTransactionException if idempotencyKey was used within 24h
 *                                        but with different parameters
 */
public PaymentResult processPayment(String transactionId, BigDecimal amount, String idempotencyKey) {
    // implementation
}
```

```typescript
/**
 * Fetches user data from cache with fallback to database.
 *
 * Cache TTL: 5 minutes
 * Database timeout: 3 seconds
 *
 * @param userId - User's unique identifier (UUID format)
 * @returns Promise resolving to User object or null if not found
 * @throws DatabaseTimeoutError if DB query exceeds 3s
 * @throws CacheConnectionError if Redis is unavailable (non-fatal, falls back to DB)
 */
async function getUserData(userId: string): Promise<User | null> {
    // implementation
}
```

Before, this felt like overhead to me. Now it's the difference between getting it right on the first try or going back and forth multiple times.

The kicker: **the agent generates this documentation itself**. I just had to stop deleting it.

## Comments as Prompt Engineering

Here's the technical reality: when an agentic coding system like Claude Code works on your codebase, it's not reading code the way a compiler does. It's building a context window from multiple sources:

1. The code itself (syntax, structure, types)
2. The surrounding files and imports
3. **Comments and documentation** (the often-overlooked prompt booster)

That third component is doing more work than most engineers realize. Comments are essentially inline prompt engineering. When I write:

```python
def process_batch(records: List[Record], batch_size: int = 500) -> ProcessResult:
    """
    Process records in batches to avoid OOM on 2GB heap instances.

    Batch size of 500 was empirically determined from load testing.
    Larger batches (1000+) cause GC pauses >2s. Don't increase without
    upgrading instance types and rerunning load tests.

    Args:
        records: List of Record objects to process
        batch_size: Number of records per batch (default: 500)

    Returns:
        ProcessResult containing success count and failed record IDs
    """
    # implementation
```

This documentation isn't just for future maintainers. It's **actively shaping the agent's behavior in the current session**. When the agent sees this and I ask it to "optimize the batch processing," it knows:
- Don't suggest increasing batch size (I already tested that)
- The 500 limit is tied to infrastructure constraints
- Any optimization needs to work within these constraints

Without the comment, the agent's first suggestion is almost always "increase the batch size to 1000 for better throughput." With the comment, it skips that dead end and suggests actual improvements like parallel batch processing or streaming.

This is prompt engineering at the code level. I'm preloading the agent's context with constraints, failed experiments, and institutional knowledge before it even starts thinking about the problem.

## The Feedback Loop Mechanics

The difference in iteration count isn't subtle. Here's what I measured across multiple projects:

**Documented codebase** (with AI-generated docs preserved):
- Session 1: Agent writes function with docstring
- Session 2: Agent needs to call that function
- Agent reads docstring, understands parameter constraints, exception handling, return types
- Generates correct code on first try
- **Result: 1-2 iterations to working code**

**Undocumented codebase** (my old "clean code" approach):
- Session 1: Agent writes function, I delete docstring
- Session 2: Agent needs to call that function
- Agent infers from type hints but misses:
  - That UUID must be v4 specifically
  - That null return means "not found" vs error
  - That certain exceptions are non-fatal
- First attempt has subtle bugs
- I explain what was wrong
- Agent fixes it
- Still has issues with edge cases
- More back-and-forth
- **Result: 5-6 iterations, explaining the same constraints the agent documented in Session 1**

The documentation the agent generates becomes its own memory across sessions. Delete it, and you're forcing the agent to rediscover context every time.

## The Irony

I spent years telling others to remove javadoc and docstrings. "The code speaks for itself." I championed *Clean Code*'s anti-comment philosophy.

Now I'm keeping all the docs the AI generates. Actually asking it to add more when it doesn't.

## Conclusion

Code comments went from anti-pattern to optimization technique. Not because the code changed, but because the audience changed.

When humans were the only readers, comments competed with self-documenting code. Type hints, clear naming, and good structure could communicate intent. Comments were redundant overhead.

But agentic coding systems don't just read code-they build context windows from everything available. Comments function as prompt boosters, injecting constraints and institutional knowledge directly into the agent's reasoning process. This isn't a minor optimization. My measurements consistently show 3-4x fewer iterations with documented code.

The workflow shift is subtle but important:
- **Before**: Write code → Delete redundant comments → Ship
- **Now**: Write code → Let agent generate docs → Keep them → Ship

The documentation the agent generates becomes infrastructure for future AI sessions. It's a form of machine-to-machine communication that happens to be human-readable.

Looking forward, I expect this pattern to evolve. Right now, comments are static prompt boosters. But agentic systems could start generating richer metadata-execution traces, performance characteristics, common bug patterns-that further optimizes the feedback loop. The documentation layer might become the primary interface between human intent and machine execution.

For now, the practical takeaway: treat AI-generated documentation as first-class code artifacts, not byproducts to clean up.
