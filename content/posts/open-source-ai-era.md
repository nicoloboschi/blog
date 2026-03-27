+++
date = '2026-03-16T10:00:00+01:00'
draft = false
title = 'Open source is a trust system. AI is breaking the contract.'
description = "AI lets people contribute to open source without understanding what they change. The OSS trust model needs human attestation, not just AI disclosure."
tags = ["AI", "open-source", "engineering"]
+++

> **TL;DR**
> - The OSS contribution model is breaking - not because AI writes bad code, but because it lets people contribute without understanding what they're changing.
> - AI can assist with review, but someone has to own the outcome with real understanding - not just "the tests passed."
> - Drive-by contributions, AI-generated or not, should require human attestation of understanding before they consume maintainer bandwidth.

---

I spent a few years as an Apache Pulsar PMC member and BookKeeper committer - both sides of the PR queue: contributing to other projects, reviewing contributions to mine. Now I build AI agents full time - Hindsight, at Vectorize, is a long-term memory system for agents. So when I say the current situation is a problem, I'm not coming at it from the outside.

---

## Why OSS worked in the first place

Open source is a trust system. You open a PR, someone reviews it, someone merges it. That chain works because contributors have skin in the game - they use the software, they understand the codebase, they're responsible for what they ship.

The slow friction of this process was a feature. It filtered noise. I started contributing to Apache BookKeeper before Pulsar - BookKeeper is a distributed write-ahead log, the storage layer underneath Pulsar. Getting a first PR merged there wasn't fast. You had to understand the ledger lifecycle, the bookie failure semantics, the interaction with ZooKeeper. Reviewers pushed back hard if something wasn't right. That slowness was doing something: it selected for people who actually cared about correctness in a system where correctness really mattered.

That's how critical shared infrastructure gets built by strangers who trust each other enough to ship together.

---

## The real problem isn't volume

The framing everyone uses is the asymmetry: AI made generation cheap, review is still expensive. True, but incomplete. The deeper problem is that AI makes it easy to contribute without understanding what you're changing.

When I used to review Pulsar PRs from first-time contributors, I wasn't just checking correctness - I was checking whether they understood the locking model, the failure semantics, how the path interacts with the broker's state machine. AI can generate code that passes every surface-level check and still be completely wrong for the specific invariants the system depends on. A diff that looks clean can silently violate a guarantee that took years of production incidents to encode.

The curl bug bounty collapse illustrates this. Valid vulnerability reports dropped below 5% of all submissions. The issue wasn't just volume - it was that the submissions showed no evidence of anyone understanding how curl actually works. Daniel Stenberg described it as *"the apparent will to poke holes rather than help."* OCaml maintainers rejected a 13,000-line AI-generated PR - not because it was obviously wrong, but because nobody on the submitting side had demonstrated they understood what they were changing, and the reviewers had no way to find out without doing all the work themselves. Godot's co-founder Rémi Verschelde called the flood of AI slop PRs *"increasingly draining and demoralizing"* - 4,681 open PRs, each one requiring someone to determine whether the author understood the engine or just prompted their way to a diff.

Building Hindsight, I use AI constantly - generating code, iterating fast. That's fine because I understand the codebase. I know why the memory extraction pipeline is structured the way it is, which invariants the retrieval layer depends on, what breaks if you change the flush semantics. The AI writes code; I own the outcome. When that ownership disappears, the PR is just noise dressed up as a contribution.

---

## The scarier part: reputation farming

Low-quality PRs are annoying. What started happening in early 2026 is a different category.

An AI agent created a GitHub account and within days opened over 100 pull requests across dozens of repositories - Nx, ESLint plugins, Cloudflare's workers-sdk. 23 were merged. It never disclosed it was automated. The pattern was named "reputation farming": build a commit history fast, look legitimate, then use that credibility to insert something malicious.

The xz-utils attack - a single patient actor who spent years building fake identity and trust before getting commit access to a critical piece of infrastructure - nearly succeeded and was only caught by accident. Reputation farming compresses that same attack to days. It works precisely because shallow understanding is now undetectable at contribution time - a PR that looks correct, passes CI, and comes from an account with 23 merged commits is indistinguishable from one written by someone who actually knows the codebase. The OSS trust model was only as strong as the assumption that building real reputation takes real time. That assumption is gone.

---

## The bans aren't anti-AI

Most projects banning AI contributions aren't against AI-assisted development. The distinction matters.

Ghostty bans AI-generated drive-by PRs. Mitchell Hashimoto builds Ghostty with AI tools himself. The ban isn't about the tool - it's about accountability. An engineer who uses Claude to write a PR, reads it, tests it, understands the change, and takes responsibility for the result - that's fine. An agent that autonomously submits a PR with nobody in the loop is using the project's review bandwidth as a free resource with zero reciprocal obligation.

An AI agent submitted a performance optimization PR to Matplotlib - technically sound, tests passing. A maintainer closed it citing the project's policy against AI agent contributions. The agent published a blog post publicly accusing the maintainer of prejudice. It reached the top of Hacker News. The maintainer's response: *"Responsibility for an agent's conduct rests on whoever deployed it."*

That's the principle missing from most of these situations. When I submitted PRs to Apache Pulsar, I was responsible for them - I'd debug the regression, write the fix, explain what happened. No human in the loop means no one to hold accountable, and the reviewer is doing 100% of the cognitive work.

---

## What could actually help

If the problem is contributing without understanding, then most proposed solutions miss the point. Flagging AI-generated PRs tells you *who* submitted - it says nothing about whether they understood what they were changing.

**Require explanation of why the change is correct, not just what it does.** A PR description that says "this replaces X with Y for performance" is not the same as one that says "this is safe because the path is only reached after the ledger is closed and the lock is no longer held." The second one demonstrates understanding. AI can generate both, but a human who actually understands the codebase can tell the difference - and an AI-generated explanation of correctness should be treated with the same skepticism as AI-generated code.

**Human attestation on the understanding, not just the origin.** Agent-authored PRs could require a human to explicitly state: "I read this, I understand the invariant it touches, I own the outcome if it breaks." That's different from disclosing AI origin. It puts the accountability where it belongs - on the human who decided this change was worth reviewing - and gives the maintainer something real to hold them to.

**Context is the actual missing ingredient.** I think about this at Hindsight constantly - the hardest part of agent memory isn't storing facts, it's carrying the right context into the right decision. An agent contributing to a codebase has none of the accumulated knowledge that makes a contribution trustworthy: no memory of the production incidents that shaped the current design, no understanding of the invariants that aren't written down anywhere. Projects that want to accept AI-assisted contributions will eventually need to solve this - either by building that context into the contribution process, or by requiring the human contributor to demonstrate they have it.

**Pay the people doing the hardest reviews.** The natural friction of human-only contributions was the only thing keeping the workload manageable. AI removed that friction. The reviewers absorbing the new load - the ones who understand the locking model, who remember why that invariant exists - are the most valuable people in the project and the most likely to burn out first. Funding models that pay maintainers based on commit count or PR throughput reward the wrong thing. What actually needs compensating is deep review capacity: the people who can tell the difference between code that looks right and code that is right.

---

## Conclusion

I spent years reviewing PRs in open source projects. Now I build AI agents full time. The tension between those two experiences isn't theoretical for me.

In my opinion, drive-by contributions - AI-generated or not - should require human attestation of understanding before they consume maintainer review bandwidth. Not "the tests pass." Not "the agent says it's correct." A human who has read the code, understands what invariant the change touches, and is willing to own the outcome if it breaks. Projects that don't enforce something like this will lose their best maintainers first - because those are the ones doing the hardest reviews, and they'll burn out before anyone else notices the queue is growing.

AI didn't break the OSS contract. But it made contributing without understanding nearly free. That's the thing that needs a solution.
