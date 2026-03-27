+++
date = '2026-02-16T10:00:00+01:00'
draft = false
title = 'It was never about the code'
description = "A coworker rebuilt my two weeks of UI work with Claude in one weekend. The grief was real, but it revealed: the code was never the point."
tags = ["AI", "career", "personal"]
+++

In May 2025, I spent two weeks building the UI for a project we were launching at Vectorize. The product had a dataplane, backend services, the whole stack-but I was focused on the UI layer. It wasn't a massive feature, but it was mine. I knew every component, every state transition, every edge case I'd handled. I spent evenings working through React components and Tailwind classes-web dev isn't my thing, but it's part of the job and I get by. I made sure the data flow was clean, organized the file structure the way I wanted it.

Then my coworker took my UI and rebuilt it with Claude in one weekend.

Same UI functionality. Better design. Cleaner component structure. And it took him maybe 12 hours total, most of which was probably spent iterating on prompts.

The project became an internal tool shortly after, so none of this particularly mattered in the grand scheme of things. But something about that moment broke me in a way I didn't expect.

## The five stages of grief over a UI component

**Denial**: "It's probably buggy. There's no way it handles all the edge cases. I spent two weeks on this for a reason."

I opened the PR. The code was... fine. Actually, it was good. All the edge cases I'd worried about were handled. The component architecture made sense. The state management was cleaner than mine.

**Anger**: "This is bullshit. I *owned* that code. I built it from scratch. You can't just... replace it like that."

I didn't say this out loud, obviously. But I felt it. This territorial rage about code I'd written. Like someone had painted over my artwork. The fact that it was *better* made it worse.

**Bargaining**: "Okay, but he had to use AI. I did it by hand. That counts for something, right? Anyone can just prompt an AI. Real engineering is..."

Real engineering is what? Typing more characters? Taking longer? This argument fell apart immediately, but I clung to it anyway.

**Depression**: "If this can be done in a weekend with Claude, what was the point of my two weeks? What's the point of any of this?"

This is where it got dark. Nine years of my career flashed by. All those nights I came home satisfied because I'd fixed a tricky bug or shipped a feature. All those times I felt accomplished because I'd written good code.

Was all of that just... replaceable?

**Acceptance**: "Wait. Why did I even care about the code in the first place?"

And this is where everything shifted.

## The uncomfortable realization

I spent those two weeks on the UI because we were launching a product at Vectorize. The UI was a means to an end. The actual goal was solving the problem: how do we let users interact with this system effectively?

The code wasn't the point. It never was.

But I'd convinced myself over nine years that coding *was* the point. I'd come home from work feeling accomplished because I solved a distributed systems problem with elegant code. I thought the satisfaction came from the elegance, from the craft of coding itself.

It didn't. The satisfaction came from solving the technical challenge. The code was just the tool I used to get there.

Believing it intellectually and *feeling* it viscerally are different things. That weekend in May, watching my two weeks of work get replaced, I felt it.

## The tool changed, the challenge didn't

My coworker who rebuilt the UI in a weekend-he still had to solve the same problem I did. He still had to understand what the UI needed to do, what edge cases existed, how state should flow, what the user interactions should be.

He just used a different tool to express the solution. He prompted Claude instead of typing React components. But the actual engineering work-understanding the problem space, designing the solution, validating it handles edge cases-that was identical.

The code was never the hard part. It was just the most time-consuming part.

Now that AI can write code faster than humans, the time-consuming part became trivial. And what's left is the actual challenge: understanding systems, solving technical problems, making architectural decisions.

Which, it turns out, is what I actually enjoyed all along.

## The craft argument

A week after the UI rebuild, I was reviewing another PR. Someone had used Claude to generate a data validation layer. The code worked, tests passed, but I found myself leaving comments about "better" ways to structure it.

Then I stopped. Why did I care? The validation worked. Edge cases were covered. It solved the problem.

I was clinging to craft. The idea that there's value in *how* you write code, not just *that* it works. That understanding things at a deep level, writing elegant solutions-that's what separates real engineers from prompt writers.

But when I thought about the problems I'd actually solved in my career, the craft was never the goal. It was a prerequisite. You need to understand how databases work to design a good sharding strategy. But the value isn't in the understanding-it's in the strategy that emerges from it.

If a better tool solves the problem faster, the craft becomes irrelevant. The ego wants to believe years of typing syntax makes you valuable. The market just cares about solved problems.

That stings to write.

And it led me to the harder question: if the craft doesn't matter, what was I even doing all these years?

## The identity crisis

The hardest part wasn't accepting that AI can code. It was accepting that I'd built my identity around something that was always just a tool.

"I'm a software engineer" meant "I write code" in my head. When someone asked what I do, I'd talk about programming languages, frameworks, technical problems I'd solved through code.

Now I barely code. And I had to confront: if I'm not writing code, what am I?

The answer took months to settle into: I'm someone who solves technical problems. Sometimes that involves writing code. Sometimes it involves prompting AI. Sometimes it involves designing systems, debugging production issues, or making architectural decisions.

The code was never the identifier. The problem-solving was.

---

I don't code much anymore. Mostly prompting Claude, reviewing what it generates. And I'm having more fun than I did in those nine years of "loving coding."

That doesn't mean I'm not involved. I still test everything. When I'm working on Hindsight, I run the code, verify the behavior, understand what it's doing. The AI writes it, but I'm the one who has to know if it actually solves the problem. The difference is I'm spending time on the verification and problem-solving, not typing syntax.

In my opinion, most engineers who say "code was more fun before" are grieving identity, not coding. The grief is real-those two weeks on the UI mattered because I made it. But the making was never the point. The solving was.
