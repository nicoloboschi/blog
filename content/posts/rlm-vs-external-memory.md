+++
date = '2026-02-09T10:00:00+01:00'
draft = false
title = 'RLM is half a paradigm'
tags = ["AI", "agents", "memory", "LLM", "RLM"]
+++

**TL;DR**: RLM excels at within-session context management through prompt-as-variable decomposition. But it's blind to cross-session knowledge - no persistence, entity tracking, temporal reasoning, or opinion evolution. Production agents need both: RLM for massive single-session inputs, external memory for knowledge that accumulates over weeks/months.

---

## What RLM Actually Is

Here's the operational model: put an LLM (GPT-5, Qwen3-Coder) in a Python REPL, store the prompt as a Python variable instead of feeding it to the model, and let the model write code to navigate it.

The key is the iterative loop:
1. Model writes Python code to explore/analyze the prompt
2. REPL executes, returns output
3. Model sees the output, adjusts strategy
4. Model writes more code based on what it learned
5. Repeat until the answer emerges

This might look like:

```python
# Turn 1: Model peeks at the prompt structure
print(prompt[:200])
# Output: "timestamp,user_id,action,metadata\n2024-01..."

# Turn 2: Realizes it's a CSV, changes strategy completely
df = parse_csv(prompt)
print(df.columns, len(df))
# Output: ['timestamp', 'user_id', 'action', 'metadata'], 50000 rows

# Turn 3: Sees 50K rows, decides aggregation is better than summarization
actions_by_user = df.groupby('user_id')['action'].value_counts()
summary = query_lm(str(actions_by_user.head(100)), "identify patterns")

# Turn 4: Uses those patterns to focus the final query
final = query_lm(f"Given patterns: {summary}, analyze: {df[relevant_cols].head(500)}")
```

It's iterative code-based decomposition. The model sees intermediate results and adapts, rather than executing a predetermined plan. That's more expressive than fixed orchestration patterns.

## Why This Matters (And The Numbers Back It Up)

The paper's own authors admit: "the idea of multiple LM calls in a single system is not new - in a broad sense, this is what most agentic scaffolds do."

Their distinction: agents use human-designed decomposition, RLM lets the model decide by writing code. That's a workflow difference rather than a new architecture - but here's what matters: **the performance gains**.

RLM(GPT-5) scores 91.33% on BrowseComp+ vs CodeAct+BM25 at 51%. On OOLONG-Pairs, base GPT-5 gets 0.04 F1, RLM gets 58.00. These are 30-40 point improvements over standard agentic coding baselines.

The prompt-as-variable design clearly outperforms within a session. But this advantage is confined to within-session tasks - which is exactly where external memory systems are blind.

## The One Thing That Actually Matters

The "is this just agentic coding?" debate has a precise answer: yes, RLM is agentic coding. The model writes Python, calls sub-LMs, iterates in a loop. The pattern is familiar.

But it's not *just* agentic coding - there's one specific difference that explains the 40-point performance gaps.

In standard agentic coding (CodeAct, ReAct), the prompt goes into the model's attention. The context window fills up. Context rot kicks in. In RLM, the prompt stays outside as a Python variable. The root LM's context window stays clean - it only ever sees the small slices it chooses to look at.

That's the distinction. Not recursion, not sub-agents, not code execution - those are all things agents already do. The novel part is **where the context lives**: outside the neural network, accessible only through code.

That one design choice is why RLM handles 10M tokens while CodeAct chokes at 272K.

So when someone says "it's just subagents" - they're right about the pattern and wrong about the performance. The prompt-as-variable insight is doing real work.

## What Agent Systems Already Do

Now compare RLM to what production agent systems have been doing:

**Tool-using agents (Claude Code, Codex, Cursor, Devin):**
- Agent decides which tools to call via reasoning
- Spawns subagents for subtasks (Claude Code spawns specialized agents for exploration, planning, etc.)
- Stores intermediate state in files or memory
- Aggregates results from tool outputs
- Terminates when task completes

**External memory systems:**
- Maintain knowledge graphs and vector stores
- Retrieve relevant context via hybrid search (semantic + keyword + graph + temporal)
- Form persistent observations that evolve with evidence
- Handle entity resolution and temporal reasoning
- Persist across sessions

RLM's REPL approach does the first (subagent decomposition) but not the second (persistent memory across sessions). Every RLM invocation starts from scratch.

## The Actual Problem RLM Solves

To be fair: RLM does solve one specific problem well.

**Context rot within a single task.** When you have a 10M token document and need to reason over it, standard approaches fail:
- Feeding it all to attention layers: hits context limits
- RAG retrieval: might miss relevant passages
- Fixed chunking: arbitrary boundaries lose coherence

RLM's prompt-as-variable approach lets the model decide how to chunk and which parts to focus on. That's genuinely useful.

But framing this as "the paradigm of 2026" oversells it. This is a workflow optimization for within-session context management. It doesn't address:
- Cross-session persistence (knowledge accumulated over weeks/months)
- Belief formation (opinions that evolve with evidence)
- Entity tracking (same person mentioned across contexts)
- Temporal reasoning ("what happened before the reorg?")

Those require external memory, which RLM doesn't provide.

## What Production Agents Actually Need

| What | RLM | Agent + External Memory |
|------|-----|-------------------------|
| **Within-session decomposition** | REPL-based code for chunking | Tool calls for subtasks |
| **Subtask execution** | `query_lm()` calls | Subagent spawning (same thing) |
| **Persistent memory** | None (session-only) | Knowledge graphs, vector stores, opinions |
| **Entity tracking** | No | Yes (canonical entity resolution) |
| **Temporal reasoning** | No | Yes (time-based retrieval) |
| **Cross-session beliefs** | No | Yes (opinions evolve with evidence) |
| **Debuggability** | REPL trace visible | Tool call logs |
| **Flexibility** | REPL + arbitrary Python | Configurable tool/memory stack |

## The Complementary Architecture: What Each System Actually Solves

Imagine building an AI project manager for a distributed systems team. The divide between RLM and external memory becomes clear:

**Within a single planning session (RLM's strength):**

You need to analyze an 8M token repository, review 500 GitHub issues, and extract constraints from 200 pages of design docs - all in one session to make an architectural decision.

RLM handles this beautifully. The model writes Python to navigate the context space, focusing on relevant sections without hitting context limits. Standard attention would fail at 272K tokens. RAG might miss critical connections. RLM lets the model decide how to chunk and where to recurse.

**Across three months of operation (where RLM goes blind):**

Now the agent needs to remember Sarah consistently finishes tasks early, recall why you chose PostgreSQL over MySQL in October, update confidence that "batch API is the right next feature" as evidence accumulates, and answer "what blockers came up before the last deployment?"

RLM can't do any of this. It's session-only. Every conversation starts from zero knowledge.

This requires external memory with:

**Entity resolution:** Alice = Alice Chen = Alice C. (canonical entities tracked across contexts)

**Temporal indexing:** Facts tagged with occurrence time + mention time. "Before the merger" gets parsed into date ranges.

**Opinion evolution:** Beliefs with confidence scores. Supporting evidence increases confidence, contradictions decrease it. The agent develops judgment over time.

**Knowledge hierarchy:** Mental models (curated summaries) → observations (auto-consolidated patterns) → raw facts (detail preservation)

This structured persistence is what external memory systems provide. As a reference architecture, Hindsight implements these patterns for production agents. RLM doesn't.

**The paradigm isn't one or the other - it's both.** [Prime Intellect frames RLM](https://www.primeintellect.ai/blog/rlm) as enabling "long-horizon tasks spanning weeks to months" but misses that long-horizon requires accumulated knowledge, not just within-session context navigation.

## The Honest Take

In my opinion, RLM is excellent within-session engineering packaged as a paradigm shift.

The prompt-as-variable approach genuinely solves context rot for massive single-session inputs. That's valuable. But it's one piece of the puzzle, not the whole paradigm.

Production agents will use:
- **RLM-style decomposition** for within-session context navigation
- **External memory** for cross-session knowledge persistence

They're complementary, not competing.

Calling RLM "the paradigm of 2026" oversells what it does and ignores what it doesn't. The honest framing: RLM solves within-session context beautifully. External memory solves cross-session knowledge. You need both.

---

**Sources:**
- [Recursive Language Models paper](https://arxiv.org/abs/2512.24601)
- [Prime Intellect: RLM paradigm of 2026](https://www.primeintellect.ai/blog/rlm)
- [HackerNews: "Isn't this just subagents?"](https://news.ycombinator.com/item?id=46475395)
- [RLM limitations and security concerns](https://bdtechtalks.com/2026/01/26/recursive-language-models/)
- [MIT CSAIL: Recursive Language Models](https://venturebeat.com/orchestration/mits-new-recursive-framework-lets-llms-process-10-million-tokens-without)
