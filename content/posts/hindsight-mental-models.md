+++
date = '2026-01-25T12:00:00+01:00'
draft = false
title = 'What learning actually means for AI agents'
description = "Raw fact retrieval breaks down when agents need to learn from experience, adapt to change, and infer conclusions from scattered signals across time."
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Storing and retrieving raw facts works for simple Q&A, but agents that run over time need more. They need to learn from experience, adapt when things change, and connect scattered dots. That requires thinking about memory differently.

---

## Where retrieval breaks down

We built an internal AI PM to help track projects, summarize standups, and answer questions about what's happening across teams. It has access to everything - Slack messages, meeting notes, Linear tickets, design docs, past decisions.

Ask it "what's the status of Project X?" and it retrieves relevant docs and gives you a summary. That works. But ask it "which projects are at risk?" and it struggles. The signals are there - timeline slips, engineers requesting transfers, shorter weekly updates - but no single document says "this project is at risk." The agent retrieves pieces. It doesn't connect them.

Or ask about a decision made six months ago, and it might retrieve the original proposal without noticing the follow-up thread where the team reversed course. The information is all there. The agent just doesn't know which parts are still current.

This is where I started thinking about what memory actually needs to do beyond store-and-retrieve.

There's a growing recognition of this problem. Foundation Capital recently wrote about [context graphs](https://foundationcapital.com/context-graphs-ais-trillion-dollar-opportunity/) as the next evolution beyond RAG - the idea that AI systems need to map relationships between information, not just retrieve isolated documents. Traditional RAG treats data as disconnected chunks. Context graphs establish connections, enabling agents to reason across related information rather than hoping the right pieces get retrieved together.

I think they're pointing at the right problem. The question is what capabilities you actually need to solve it.

## Three capabilities beyond retrieval

There are three capabilities that raw fact retrieval doesn't give you:

1. **Learning** - Getting better with experience
2. **Adaptation** - Handling change and stale information
3. **Inference** - Connecting scattered dots into conclusions

These aren't cleanly separable. Inference about project risk requires temporal reasoning. Learning patterns requires connecting dots. They blur together in practice. But they're useful frames for understanding where retrieval breaks down.

Before I go deeper on each one, here's what they have in common: they all require the memory system to do work in the background - synthesizing patterns, tracking validity windows, forming hypotheses - rather than just storing facts and hoping the right ones get retrieved.

## Inference: the signals nobody stated

Let me start with the clearest example from the AI PM.

A project isn't flagged as at-risk. Nobody has raised concerns. But over the past month: the weekly updates got shorter and vaguer. The timeline slipped twice. Two senior engineers requested transfers to other teams. The PM hasn't scheduled the next milestone review. The tech lead mentioned "scope concerns" in a 1:1 but didn't escalate.

No single fact says "this project is in trouble." But together, these signals paint a clear picture. An experienced manager would see it immediately. The AI PM returns them as separate items - if it retrieves them at all, since none of them match a search for "project risk."

The challenge: you can't search for the conclusion directly because nobody stated it. You have to notice that certain facts, which individually seem unrelated, fit together.

Same pattern with team health. An engineer hasn't announced anything, but they've asked about equity vesting schedules, started declining optional meetings, mentioned "exploring options" in a casual chat. Individually, noise. Together, a signal that someone might be leaving.

Or technical debt. No ticket says "this system is becoming unmaintainable." But bug fix times are trending up, the same components keep breaking, three different engineers have asked about refactoring in the past month. The pattern is there if you can see it.

**Why retrieval can't solve this.** The signals are spread across time, across contexts, across interaction types. They don't cluster in any obvious way. Retrieval might find each piece if you searched the exact right terms. But the synthesis - recognizing that these scattered pieces connect - requires something else.

**What inference actually requires.** The memory system needs to watch for patterns as facts accumulate. Background processes that notice "this project's signals match patterns I've seen in projects that failed." When you ask about risk, the synthesis is already there - with the evidence chain that supports it.

When the agent says "high risk," you need to see: timeline slipped (March 3), updates got shorter (March 10), two engineers transferred (March 15), milestone review not scheduled (March 22). Each signal with a timestamp and source. Without this, the conclusion is a black box. With it, you can verify, override, or update.

## Learning: getting better over time

After a hundred questions, is the AI PM better than it was after ten? With raw fact retrieval, usually no. It has more facts, but it performs roughly the same.

It's answered hundreds of questions about project status, blockers, decisions. Each answer gets stored somewhere. But when a similar question comes in, it retrieves a few past responses and reasons from scratch. It doesn't notice that questions about "deployment blockers" almost always involve the same three infrastructure teams. It doesn't learn that "scope creep" issues in this org usually trace back to unclear product requirements. Every question is a new puzzle, even when the pattern has appeared fifty times.

Same with meeting summaries. After summarizing hundreds of standups, it should know that when someone says "I'm blocked on review," the blocker is usually a specific team. It should recognize that "making progress" often means "stuck but not admitting it" in certain project contexts. It should learn the org's vocabulary and patterns. Instead, every standup is processed in isolation.

The cost: slower answers, inconsistent responses, senior people getting pulled into questions the agent should handle by now.

**What learning actually requires.** The system needs to watch facts accumulate and synthesize them into patterns. "Deployment blockers usually involve the platform team" emerges from seeing fifty similar questions. This means running background processes that detect recurring patterns and compress them into retrievable generalizations - not on every query, but continuously as data builds up.

The difference shows up in behavior. An agent that learns converges toward better performance - fewer steps, better answers, less escalation. An agent that just retrieves stays flat.

## Adaptation: handling change

Information gets stale. People move teams, decisions get reversed, priorities shift, projects get cancelled. The AI PM with a year of accumulated facts will have some that are outdated.

Naive retrieval treats everything as equally current. The agent might retrieve a decision from last year and a contradictory update from yesterday without knowing which to trust.

This happens constantly. Someone asks "who owns the payments integration?" The agent retrieves three different answers from different time periods - because ownership changed twice. Without temporal awareness, it can't tell which one is current.

Or someone asks about the API design for a feature. The agent retrieves the original RFC, the revised proposal, and the implementation doc - all with different answers. Which one reflects what actually got built?

It gets harder with fuzzy timing. "We're revisiting this in Q2." "The new process takes effect after the reorg." "We'll finalize this after the offsite." The agent needs to reason about whether the change has happened yet.

Someone asks about a migration that was announced for "early 2026." It's now February 2026. Is it done? The agent has the announcement but no explicit "migration complete" update. It needs to reason about whether "early 2026" has passed, whether there's any indication of delay.

**What adaptation actually requires.** Temporal awareness. When did we learn this? When might it change? Is there newer information that supersedes it?

The system needs to track validity windows. Some facts are permanent (company founding date), some are transient (who's on vacation), some have fuzzy boundaries (decisions announced for "after the reorg"). Background processes should flag when retrieved facts might be stale, when newer contradictory information exists, when announced changes have likely taken effect.

## What this requires from a memory system

To summarize - four things enable these capabilities:

1. **Continuous consolidation** - Background synthesis of patterns as facts accumulate
2. **Temporal tracking** - Validity windows on facts, staleness detection, supersession awareness
3. **Evidence chains** - Every conclusion linked to specific supporting facts with timestamps
4. **Layered retrieval** - Synthesized patterns first, raw facts as fallback, staleness flags when needed

## The tradeoffs

This isn't free. Background consolidation requires compute. Synthesis can be wrong - the system might detect patterns that don't generalize. Evidence chains add storage overhead. Temporal tracking adds complexity.

The tradeoffs are worth it when:
- The agent handles >1000 interactions and you're not seeing quality improvements
- Information changes frequently and users complain about stale answers
- You need to explain why the agent reached a conclusion (debugging, trust)
- People keep spotting patterns the agent misses

If your agent handles one-off queries against a static knowledge base, retrieval is probably sufficient. Don't overcomplicate it.

## What we're building

These are the problems Hindsight is designed to solve. The three capabilities I described - learning, adaptation, inference - map directly to how we think about memory:

- **Consolidation** synthesizes patterns from accumulated facts in the background
- **Temporal tracking** knows when facts might be stale and what supersedes what
- **Evidence chains** link every conclusion back to specific supporting facts with timestamps

We're rolling out these capabilities in the next releases. The goal is agents that actually get smarter over time, not just accumulate more facts to search through.

---

Raw facts are the foundation. Learning, adaptation, and inference are what make agents useful for real work - and that difference shows up in answer quality, response times, and the number of questions that need human escalation.
