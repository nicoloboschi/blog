# Social Distribution — "That's not how you do business"

## Twitter

Thread:

**Tweet 1 (Hook + Pain)**

A company scored 99% on an AI memory benchmark last week.

2 million views. Trending everywhere.

Then they said it was a "social experiment."

Here's why that's worse than just gaming the benchmark 🧵

**Tweet 2 (The problem)**

How they got 99%:
- 8 parallel prompt variants, correct if ANY got it right
- 70 seconds latency per query
- 12+ agents doing what 1 could do
- Benchmark only has 115k tokens (fits in one context window now)

None of this works in production. None of it.

**Tweet 3 (The stunt)**

Their defense: "we left signs" — a funny acronym, an April 1st release date.

But the original post was written to be taken seriously. Architecture diagrams. Comparison tables. "Fundamentally shifts what is possible."

2M people took it at face value. The follow-up reached a fraction of that.

**Tweet 4 (What we did)**

Same week, we launched Agent Memory Benchmark.

Hindsight v0.4.19 on AMB — single-query, no ensemble tricks:
→ LoComo: 92.0%
→ LongMemEval: 94.6%
→ LifeBench: 71.5%
→ PersonaMem: 86.6%

Open harness, reproducible results, new agentic datasets. No stunts.

**Tweet 5 (CTA)**

You don't fix a trust problem by breaking trust.

You fix it with open methodology, reproducible results, and measuring what matters in production.

AMB is live: agentmemorybenchmark.ai
Repo: github.com/vectorize-io/agent-memory-benchmark

Run it against your system. Open issues if something's off.

---

## LinkedIn

I work on agent memory systems every day. Last week, something happened in this space that I think deserves a direct response.

A company published a blog post claiming ~99% accuracy on LongMemEval — the standard agent memory benchmark. It went viral. 2 million views. People were genuinely excited.

Then the next day, they said it was a "social experiment." A stunt to prove benchmarks can be gamed.

Here's my problem with this:

The 2 million people who saw the original post didn't see the follow-up. Most of them now believe agent memory is "solved." That's the message that stuck.

The technical reality? Their system ran 12+ agents per query, took 70 seconds per retrieval, and used an evaluation method where 8 different prompt variants ran in parallel — "correct" if ANY of the 8 got the right answer. That's not evaluation. That's maximizing your luck.

You don't fix a trust problem by breaking trust. You don't prove benchmarks are broken by gaming one and celebrating how viral it went.

The same week, we launched Agent Memory Benchmark (AMB). No stunts.

Hindsight v0.4.19 on AMB — single-query, no ensemble tricks:
- LoComo: 92.0%
- LongMemEval: 94.6%
- LifeBench: 71.5%
- PersonaMem: 86.6%

Open harness, reproducible methodology, new agentic datasets. Submit your system to a benchmark you don't control — that's the bar.

AMB is live → agentmemorybenchmark.ai
