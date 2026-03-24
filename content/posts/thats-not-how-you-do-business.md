+++
date = '2026-03-24T13:00:00+01:00'
draft = false
title = "That's not how you do business"
tags = ["AI", "memory", "benchmarks", "engineering"]
+++

> **TL;DR**
> - Supermemory published a "~99% SOTA" memory benchmark result that was actually a stunt - and the backlash was immediate and deserved.
> - Gaming benchmarks erodes trust in an industry that already has a credibility problem. Calling it a social experiment doesn't fix that.
> - The same week, we launched Agent Memory Benchmark - open methodology, reproducible results, multi-dimensional scoring. Hindsight v0.4.19 posts its all-time best results on it.

![Supermemory blocked me on X](/images/supermemory-blocked.png)

---

On March 22nd, Supermemory published a blog post claiming they "broke the frontier in agent memory" with a ~99% score on LongMemEval. The post had all the ingredients: a cool acronym (ASMR - Agentic Search and Memory Retrieval), diagrams, multi-agent orchestration, and the bold claim that "agent memory is now (probably) a solved problem."

It went viral. 2 million views. People were sharing it, texting each other about it, news outlets picked it up. And then, predictably, the people who actually understand memory systems started pushing back.

The next day, Supermemory published a follow-up: it was a stunt. A "social experiment." They said they left signs - the acronym was a joke, the April 1st release date was a hint, "we were having fun." The ~99% result was real, they said, but not production-ready: 70 seconds of latency, 10k+ tokens per query, 12 parallel agents doing what one could do.

I think this deserves a direct response, because I work on this exact problem every day.

---

## The damage is real even if the stunt is fake

Here's the thing: it doesn't matter that it was a stunt. The 2 million people who saw the original post didn't see the follow-up. Most of them now believe that agent memory is "solved" at 99%. That's the message that stuck.

Supermemory's defense is that they "wanted to prove a point about how easy it is to game benchmarks." But you don't prove that point by... gaming a benchmark and then celebrating how viral it went. You prove it by publishing the methodology showing how anyone could game it, and proposing a better standard. The stunt part added nothing except marketing reach.

And the "signs" they left? Come on. A funny acronym and an April Fools release date aren't disclaimers. They're plausible deniability. The original blog post was written to be taken seriously - detailed architecture, comparison tables, phrases like "fundamentally shifts what is possible." If that's a parody, it's indistinguishable from the real thing. Which is exactly why 2 million people took it at face value.

---

## The actual technical problems

Let me be specific about why the result is misleading, even setting aside the stunt framing.

**The 8-variant ensemble scoring.** Their best result (98.60%) used 8 specialized prompt variants running in parallel. A question was "correct" if *any* of the 8 variants got the right answer. This is not how you evaluate a memory system. This is how you maximize the probability of getting lucky. Run enough diverse attempts and you'll converge on 100% for any retrievable answer. It tells you nothing about what a user would experience in production.

**The benchmark itself is outdated for this purpose.** LongMemEval has ~115k tokens of conversation data. Current models have million-token context windows. You can literally dump the entire dataset into context and score competitively. The benchmark was designed for an era when retrieval was hard - that era is over. Scoring high on it no longer proves your memory system is good; it proves your LLM can read.

**Latency and cost are not footnotes.** 70 seconds per query. 12+ agents running per retrieval. This isn't a tradeoff - it's a system that cannot exist in production. Mentioning this in passing while leading with "99% SOTA" is dishonest framing, even if the numbers are technically accurate.

---

## The "social experiment" defense doesn't hold

Supermemory's follow-up argues they were "tired of the benchmarking game being grifty" and wanted to show how easy it is to fool people. I get the frustration - the agent memory space has a real credibility problem with cherry-picked results and misleading comparisons.

But here's the issue: you don't fix a trust problem by breaking trust. The people who saw the original post and got excited? They didn't learn anything about benchmark methodology. They either still believe the claim or they now trust the space even less. Neither outcome helps.

The follow-up introduces "MemScore" - a multi-dimensional scoring format (quality, latency, tokens). In my opinion, the idea itself is fine. But burying it inside a "gotcha, it was a stunt!" blog post ensures it will be remembered as part of the stunt, not as a serious proposal.

If the goal was genuinely to raise the bar on memory benchmarking, the path was straightforward: publish the scoring standard, show why existing benchmarks are insufficient, provide tooling. No stunts needed. I think the stunt was marketing first, and the methodology proposal was the recovery plan when the backlash hit harder than expected.

---

## What we did instead

The same week, we launched [Agent Memory Benchmark](https://agentmemorybenchmark.ai). No stunts. No viral marketing. Just the work.

AMB exists because I think the same thing Supermemory claims to think: that existing benchmarks are insufficient and that accuracy alone is a broken metric. The difference is we built the alternative instead of proving a point by gaming the thing we claim to oppose.

AMB measures accuracy, speed, cost, and usability together - because a system that scores 90% but costs $10/user/day is not better than one at 82% for $0.10. The entire evaluation harness is open and reproducible: methodology, judge prompts, answer generation prompts, everything. The choices that look like implementation details are where results actually get made or broken - a small change to the judge prompt can swing scores by double digits. We publish all of them. And critically, AMB includes new datasets for agentic workflows, not just the chatbot recall scenarios that LongMemEval was designed for.

Hindsight v0.4.19 posts its all-time best results on AMB:

| Dataset | Accuracy |
|---|---|
| LoComo | 92.0% |
| LongMemEval | 94.6% |
| LifeBench | 71.5% |
| PersonaMem | 86.6% |

No ensemble tricks. No 8-variant best-of scoring. Single-query mode, one retrieval call, production-realistic latency. We run the same harness, against the same datasets, with the same methodology that anyone else can use. That's the point - if your system is real, you should have no problem submitting to a benchmark you didn't design and can't control.

Running 12 agents to score 99% on an outdated benchmark and then calling it a "social experiment" when the backlash hits - that's not how you do business. In my opinion, the bar is simple: submit your system to a benchmark you don't control, publish numbers you can't cherry-pick, and let engineers compare for themselves. Everything else is noise.

AMB is live at [agentmemorybenchmark.ai](https://agentmemorybenchmark.ai). The repo is at [github.com/vectorize-io/agent-memory-benchmark](https://github.com/vectorize-io/agent-memory-benchmark). Run it against your own system. If something is broken, open an issue.
