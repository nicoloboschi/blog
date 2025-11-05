+++
date = '2025-11-05T15:05:30+01:00'
draft = false
title = 'Code Comments: Humans vs Agentic Code'
tags = ["AI", "coding-agents", "best-practices"]
+++

**TL;DR**: AI agents generate docs (javadoc, pydoc, docstrings) as they code. I used to delete them. Keeping them cuts feedback loops from 5-6 iterations to 1-2. The takeaway: let agents document themselves rather than writing code for them.

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

Before, this felt like overhead. Now it's the difference between getting it right on the first try or going back and forth multiple times.

The kicker: **the agent generates this documentation itself**. I just had to stop deleting it.

## The Irony

I spent years telling developers to remove javadoc and docstrings. "The code speaks for itself." I championed *Clean Code*'s anti-comment philosophy.

Now I'm keeping all the docs the AI generates. Actually asking it to add more when it doesn't.

## Conclusion

The pattern: AI agents generate docs as they code. I keep them now.

My measurements show 1-2 iteration loops with docs vs 5-6 without.

The simple takeaway: let the agent document itself. When it generates javadoc, pydoc, or docstrings, those become context for its next session. Delete them, and it has to rediscover everything.

Maybe in the future, we'll let agentic tools build up their own understanding through the documentation they generate, rather than trying to write code specifically for them.
