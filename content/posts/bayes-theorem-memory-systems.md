+++
date = '2026-02-16T18:00:00+01:00'
draft = true
title = 'Building memory systems on Bayes theorem'
tags = ["AI", "agents", "memory", "hindsight", "LLM", "bayes"]
+++

**TL;DR**: Bayes' theorem says beliefs are probabilities that update with new evidence. Hindsight implements this by storing immutable facts and maintaining mutable observations that evolve as new data arrives. This creates a memory system where the agent's understanding of the world gets refined continuously instead of being fixed.

---

## The Theorem

Bayes' theorem answers a simple question: given new evidence, how much should you update your belief about something?

The formula itself is straightforward: P(A|B) = P(B|A) × P(A) / P(B). But the concept matters more than the math. You start with a prior belief-your initial assumption about how the world works. Then you encounter evidence. Bayes' theorem tells you how to combine your prior with that evidence to form an updated belief, called the posterior.

The key insight is that beliefs aren't binary. They're probabilities. You don't believe smoking is "safe" or "unsafe"-you have a probability estimate based on available evidence. When a new study comes out, you don't flip your belief completely. You update your probability based on the strength of the evidence and your prior assumption.

Multiple studies accumulate. Each one shifts your posterior a bit further. Eventually, the weight of evidence becomes strong enough that your prior gets overwhelmed. Your belief changes because the data forced it to change.

This is rationality. Not fixed opinions, but continuously refined probability estimates based on the best available evidence.

## The Connection to Memory

When I read that tweet about Bayes' theorem, I realized we'd accidentally built a memory system that follows this exact pattern.

Hindsight collects raw events as immutable facts. Meeting notes, API logs, user feedback, conversation history-everything gets stored as discrete records. These facts never change. They're what happened, timestamped and permanent.

On top of those facts, Hindsight maintains observations. Observations are synthesized patterns that answer questions like "Is this project on track?" or "Does the team have enough resources?" These aren't facts-they're opinions about how the world works based on the facts we've seen.

And here's where Bayes comes in: observations are mutable. As new facts arrive, observations update.

The facts are your evidence. The observations are your beliefs. Bayes' theorem is the mechanism that decides when beliefs should change based on accumulated evidence.

## Priors and Posteriors in Agent Memory

In traditional Bayesian reasoning, you start with a prior-your initial belief before seeing evidence. Where do priors come from in a memory system?

In Hindsight, the system forms initial observations based on the first few facts it sees. If you retain three facts saying "Team requested additional engineers," the consolidation process synthesizes an observation: "Team resource-constrained."

That's your prior. It's based on limited evidence-just those three facts. The system has formed an initial belief about how the world works.

Now more facts arrive. "Team missed sprint deadline." "PM extended timeline by two weeks." "Stakeholder expressed concerns about delivery date."

Each fact is new evidence. The consolidation process re-evaluates the observation. Does the new evidence support the prior? Contradict it? Introduce nuance?

The observation evolves: "Team resource constraints causing timeline delays."

More evidence: "Backend API spec changed twice, frontend waiting on final endpoints."

The observation updates again: "Team timeline delays caused by unstable API requirements, not just resource constraints."

The prior ("resource-constrained team") got refined into a more accurate posterior ("delayed by API instability") because the evidence forced the update. The system didn't hold onto its initial belief. It changed its mind as data accumulated.

## Why Immutable Facts Matter

Bayes' theorem only works if you can trust your evidence. If the evidence itself keeps changing, you can't build reliable probability estimates.

This is why Hindsight separates facts from observations. Facts are immutable. Once stored, they never change. You can't edit what someone said in a meeting or what timestamp an event occurred. The raw data is locked.

Observations, by contrast, are completely mutable. They're derived from facts, so they can change whenever the underlying evidence changes or new evidence arrives.

This separation is critical. If everything were mutable, you'd have no stable ground truth. If everything were immutable, you couldn't synthesize new understanding as patterns emerge.

The design mirrors scientific method. Lab results (facts) are recorded exactly as observed and don't change. Scientific theories (observations) evolve as new lab results accumulate. You don't go back and alter old experimental data to fit new theories. You update the theory based on the complete body of evidence.

## Strength of Evidence

Not all evidence carries equal weight in Bayesian updating. A single data point shouldn't dramatically shift your belief if you already have strong prior evidence. But accumulating data points from the same source should.

Hindsight tracks this through evidence chains. Each observation maintains bidirectional links to the facts that support it. When you retrieve an observation, you can see exactly which facts contributed to that belief.

If an observation is based on thirty supporting facts, it carries more weight than an observation based on three facts. The agent can evaluate strength of evidence by inspecting the evidence chain depth.

When contradictory facts arrive, the consolidation process compares evidence strength. If you have an observation "Project on track for Q1 delivery" supported by five facts, and then three new facts arrive saying "Missed three consecutive milestones," the evidence ratio matters. Three contradicting facts might not immediately override five supporting facts-but they shift the probability. The observation might update to "Project timeline at risk despite earlier progress."

This is Bayesian updating in practice. The posterior doesn't just flip because you saw one contradicting piece of evidence. It adjusts proportionally based on the relative strength of new vs. existing evidence.

## Real-Time vs. Eventual Consistency

Pure Bayesian reasoning assumes you update your belief immediately when new evidence arrives. In agent memory systems, that creates a latency problem.

If consolidation runs synchronously-blocking the retain operation until observations update-every write becomes expensive. You're paying multiple LLM calls and database operations before the retain completes. For production systems handling hundreds of retains per minute, that's a dealbreaker.

Hindsight runs consolidation asynchronously. When you retain new facts, they're stored immediately and the retain operation returns. Consolidation happens in the background, updating observations as it processes the evidence queue.

This introduces eventual consistency. Your observations lag behind the most recent facts by seconds or minutes, depending on consolidation throughput. The system's beliefs about the world are slightly out of date.

In my opinion, this tradeoff is correct for most agent workloads. Real-time belief updates aren't necessary when the agent can still access raw facts during the consolidation window. The most recent data is available-it just hasn't been synthesized into observations yet.

The analogy holds: scientists don't update their theories in real-time every time a new lab result comes in. They batch evidence, analyze patterns, then update their understanding. The delay between data collection and theory refinement doesn't invalidate the process. It makes it practical.

## Why This Matters for Agents

Retrieval-augmented generation typically works by dumping facts into the prompt and hoping the LLM synthesizes patterns in real-time. That works for simple queries. It breaks down when you need to reason over weeks of accumulated data.

Imagine an agent managing a software project. Over three weeks, it retains 200 facts: sprint updates, bug reports, code reviews, stakeholder conversations, team meetings. When you ask "Is this project on track?", traditional RAG retrieves the top 30 facts by relevance score and passes them to the LLM.

Those 30 facts might include: "Team requested more engineers" (week 1), "API spec changed" (week 2), "Stakeholder concerned about timeline" (week 3). The LLM has to synthesize the pattern from scratch every query. Sometimes it connects the dots. Sometimes it misses the relationship between API instability and timeline concerns.

With Bayesian observations, the synthesis happened asynchronously over the three weeks. By week 3, there's an observation: "Project timeline at risk due to unstable API requirements causing engineering delays." That observation is based on 40 supporting facts, not just the 3 that scored highest in retrieval.

When you query "Is this project on track?", the agent retrieves the observation directly. It gets a pre-computed, evidence-backed answer instead of hoping the LLM synthesizes correctly from limited context.

The observation also provides the evidence chain. If the agent needs to drill deeper-"Why are API requirements unstable?"-it follows the links from observation → supporting facts → source documents. That's hierarchical reasoning: start with synthesis, drill into details only when necessary.

## Where It Breaks

Bayesian updating assumes rational evidence evaluation. LLMs are not perfectly rational.

Consolidation can synthesize incorrect observations. The model might misinterpret facts, hallucinate relationships that don't exist, or miss important contradictions. When that happens, the bad observation pollutes future retrieval until consolidation runs again and hopefully corrects it.

I've seen observations that directly contradict the supporting facts. The LLM was asked to synthesize patterns from five facts, and instead of combining them coherently, it invented a sixth fact and built the observation around that. The evidence chain shows five real facts, but the observation text includes claims not present in any of them.

Debugging requires tracing the evidence chain manually. You retrieve the observation, follow the links to supporting facts, and figure out which combination triggered the bad synthesis. Sometimes the facts are correct but the pattern recognition failed. Sometimes a fact was extracted incorrectly during retain and the observation inherited that error.

Another failure mode: rapid contradictory facts. If two opposing facts arrive before consolidation runs, it sees both simultaneously. It's supposed to synthesize a coherent posterior, but sometimes it hedges: "Project may be delayed OR may meet original deadline." That's useless for decision-making.

Eventual consistency lag can also cause problems. If consolidation stalls-slow LLM, high retain volume, service interruption-facts accumulate without synthesis. When consolidation catches up, it processes batches of 50+ facts at once. The observations jump multiple states instead of evolving smoothly. You lose the incremental Bayesian updates and get discrete jumps.

## Conclusion

Building memory systems on Bayes' theorem means separating immutable evidence from mutable beliefs. Hindsight stores facts as permanent records and observations as evolving patterns. As new facts arrive, observations update through background consolidation that mirrors Bayesian posterior calculation.

The tradeoff is eventual consistency for better retrieval. Pre-computed synthesis beats hoping the LLM connects the dots from raw facts every query. And evidence chains provide auditability that confidence scores don't.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
