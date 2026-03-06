# Social media distribution: Not all agents are the same

## Twitter

Every agent framework treats a style preference and a file diff identically.

That's the bug.

Real agents need two memory layers:
- Task context → expires when the task ends
- User knowledge → accumulates over months, has to stay accurate

The hard part isn't storing user knowledge.
It's knowing when it silently became wrong.

Two failure modes depending on how you store it:

→ Time-decay on raw observations: can't tell if a preference changed or just aged out
→ Consolidated beliefs: handles contradictions, but wrong summaries are authoritative and untraceable

The harder problem: "context drift"
A user led a 3-person team. 4 months later they ran a 20-person org.
Nothing contradicted anything. Memory was confidently wrong for months.

That's not contradiction detection. That's entity state reasoning — and almost no system does it at write-time.

The unsolved part: a memory system that can say "I think this is still true, but I'm not sure."

[link]

---

## LinkedIn

I spent time debugging why an AI assistant kept giving subtly wrong advice to a user.

The memory said they led a three-person team. They'd been running a twenty-person org for four months.

Nothing in the new conversations contradicted anything old. Team size just never came up again. Every response was calibrated to a context that had stopped existing.

WTF moment: this isn't a storage problem. It's a reasoning problem. And almost no agent framework is built to handle it.

The real issue: most agents treat a style preference and a file diff identically — same vector store, same retrieval, same injection. But these are two different memory layers with completely different quality bars.

Task context expires. User knowledge has to stay accurate over months. Conflating them is the root cause of most interaction agent failures.

I wrote about the actual failure modes — time-decay vs. consolidation, why "contradiction detection" is the wrong frame for context drift, the write-time vs. query-time tradeoff, and what it would actually mean for a memory system to express uncertainty about its own beliefs.

[link]
