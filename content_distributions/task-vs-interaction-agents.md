# Social media: Not all agents are the same

---

## Twitter — versions

**V1**
Task agents and interaction agents look the same from the outside. They're not.

Latency, retrieval quality, and even knowing *what* to retrieve work completely differently.

Using the same stack for both is a mistake that fails silently.

[link]

---

**V2**
"Retrieve broadly and let the model sort it out" works for task agents.

For personalization agents it quietly breaks — wrong context, no feedback signal, trust eroding one response at a time.

Wrote about the three things that actually differ: [link]

---

**V3**
For a task agent, retrieval misses are loud — tests fail, code breaks.

For an interaction agent, retrieval misses are silent — the response looks fine, the user just slowly stops trusting it.

Same stack, very different failure modes. [link]

---

**V4**
"Fix this bug" → obvious retrieval query.

"Recommend something for dinner" → dietary restrictions? past orders? time of day? budget signals?

The query itself is the hard part for interaction agents. [link]

---

## LinkedIn — versions

**V1**
Most agent stacks are designed for task agents — do a job, return a result.

When teams reuse the same stack for personalization or assistants, the system doesn't break. It just works noticeably worse, and the gap is hard to pin on memory.

Three things that behave differently: latency budgets, retrieval quality standards, and knowing what to retrieve at all.

[link]

---

**V2**
Task agents fail loudly. Code doesn't compile, tests fail, the agent retries.

Interaction agents fail silently. Wrong context produces a plausible response. No signal. The user just stops trusting the product.

That asymmetry alone should change how you build memory for each.

[link]

---

**V3**
The hardest part of building personalization agents isn't storing user knowledge.

It's knowing which slice of it matters for *this specific request, right now* — and retrieving it fast, with no feedback loop to tell you when you got it wrong.

[link]
