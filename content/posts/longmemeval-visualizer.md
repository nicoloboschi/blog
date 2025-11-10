+++
date = '2025-11-10T10:00:00+01:00'
draft = false
title = 'Debugging 300MB JSON Files: A LongMemEval Visualizer'
tags = ["AI", "memory", "debugging", "benchmarking"]
+++

**TL;DR**: Built a browser-based visualizer for the LongMemEval benchmark dataset because debugging a 300MB JSON file in a text editor is impossible. The tool indexes and visualizes 115K-1.5M token chat histories used to test AI memory systems.

---

I've been working on a memory system for AI Agents, and needed a way to benchmark its performance. LongMemEval is the standard benchmark for this, but there's a problem: the dataset is a 300MB JSON file with up to 1.5 million tokens of chat history per test case.

Opening that in a text editor? Good luck. Searching for specific conversations or debugging why a particular test case failed? Nearly impossible.

So I built a visualizer: [https://nicoloboschi.github.io/longmemeval-inspector/inspector.html](https://nicoloboschi.github.io/longmemeval-inspector/inspector.html)

## What is LongMemEval

LongMemEval is a benchmark that tests five core memory abilities in chat assistants:

1. **Information extraction** - Can it remember facts from previous conversations?
2. **Multi-session reasoning** - Can it connect information across multiple chat sessions?
3. **Temporal reasoning** - Does it understand when things happened and their order?
4. **Knowledge updates** - Can it update outdated information when corrected?
5. **Abstention** - Does it know when it doesn't have enough information?

The benchmark contains 500 questions embedded in realistic chat histories. The histories scale from 115,000 tokens (LongMemEval_S) to 1.5 million tokens (LongMemEval_M). For context, that's roughly the equivalent of 200-2,600 pages of text.

The goal is to simulate real-world usage where a chat assistant has months of conversation history and needs to recall specific details, reason about past interactions, and maintain consistent knowledge over time.

## The Debugging Problem

When you're building a memory system, you need to understand why it's failing specific test cases. Did it miss important information during extraction? Is the retrieval mechanism pulling the wrong sessions? Is the temporal reasoning off?

The LongMemEval dataset is structured as JSON with deeply nested conversation histories, timestamps, and metadata. A single test case can span hundreds of chat turns across multiple sessions. The entire dataset is 300MB.

Standard debugging approaches don't work:
- Text editors choke on 300MB files
- `grep` or `jq` only help if you know exactly what you're looking for
- You can't browse the conversation flow naturally
- No way to quickly jump between related sessions

In my opinion, the biggest issue is that you need to understand the narrative structure of each test case. These aren't random Q&A pairs - they're carefully constructed conversation histories where facts are introduced, referenced later, updated, or contradicted. Reading them as flat JSON misses the entire story.

## The Visualizer

The tool is a single HTML file that runs entirely locally in the browser. Everything is bundled in one file - the interface, the data, and the pre-built index. No server, no network requests, no external dependencies.

The entire 300MB dataset is embedded as a compressed JSON structure within the HTML file itself. The indexing happens at build-time, so when you open the file, you immediately have fast navigation without any processing delays.

The workflow is simple:
1. Find the specific question your memory system got wrong
2. Check the expected answer
3. Read the reasoning explaining why that's the correct answer
4. Trace back through the conversation history to see where the information was mentioned

This is the critical debugging loop. When your memory system fails a test case, you need to understand *why* that answer is correct by reading the conversation context. Then you can figure out what your memory missed - did it fail to extract the information? Pull the wrong sessions? Miss a temporal relationship?

For example, if a question asks "What restaurant did Sarah recommend in our conversation last month?" and the answer is "Bistro Stella," the visualizer shows you:
- The question
- The expected answer: "Bistro Stella"
- The reasoning: "User asked Sarah for restaurant recommendations on Oct 15. Sarah mentioned Bistro Stella as her favorite Italian place."
- The full conversation where this happened, with timestamps

Now you can debug why your memory system missed it. Maybe it didn't index that conversation. Maybe it retrieved the right conversation but the LLM didn't extract "Bistro Stella" from Sarah's response. Maybe it got confused by a later conversation about a different restaurant.

Technical approach: raw HTML/CSS/JS with no framework. The pre-indexed structure enables instant search and filtering even with 300MB of data embedded in the page.

## Why This Matters for Memory Systems

Building a memory system isn't just about RAG retrieval or storing conversation history. The hard part is understanding when to retrieve, what to retrieve, and how to reason about time and relationships between pieces of information.

LongMemEval exposes these failure modes. But without proper tooling, debugging those failures is trial and error. You make a change, run the benchmark, see scores improve or degrade, but don't understand why.

The visualizer removes that opacity. I can now:
- Quickly inspect failing test cases
- Understand the narrative structure the memory system needs to handle
- Verify that my retrieval is pulling the right context
- Debug temporal reasoning by seeing exact timestamps and session boundaries

This cut my iteration time significantly. Instead of running the full benchmark every time, I can focus on specific failure patterns, understand the root cause, make targeted improvements, and validate against those specific cases before running the full suite.

## Conclusion

The visualizer is on GitHub at [github.com/nicoloboschi/longmemeval-inspector](https://github.com/nicoloboschi/longmemeval-inspector). It's a single HTML file - clone it and open it in a browser. The repo also includes the build scripts if you want to regenerate it with updated data or customize the indexing.

If you're working on memory systems for AI or just curious about how LongMemEval is structured, it's useful. The benchmark is excellent but opaque without proper tooling. This makes it transparent.
