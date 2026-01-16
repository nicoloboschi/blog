# Social Media - File Is All You Need? The Scaling Problem Nobody Talks About

## Twitter/X

### Option 1 (Balanced take)
```
"Files are all you need" for AI agents

- Letta: 74% on LoCoMo with filesystem tools
- LlamaIndex: drop instructions in text files
- Harrison Chase: "File systems are a natural and powerful way to represent agent state"

It works. At benchmark scale.

What I'd want to see tested:
- 500K+ token contexts
- Multi-hop queries (3+ relationship hops)
- Temporal expressions ("last week")
- Query latency at scale

Files are a good foundation. Whether you need more depends on your use case.

Full disclosure: I build structured memory tools. I have the opposite bias.

[link]
```

### Option 2 (Both-sides framing)
```
Everyone pushing "files are all you need" sells file processing.
Everyone pushing "you need structured memory" sells structured memory.

(I'm in the second camp. Bias acknowledged.)

What I actually know:
- Files work great under ~100K tokens
- Iterative agent search handles multi-hop (costs latency)
- Temporal queries need date parsing (files don't help)
- Context rot is real at 256K+

What I don't have:
- Controlled benchmarks proving where files fail
- Data on exact scale thresholds

Start simple. Add complexity when you hit actual problems.

[link]
```

### Option 3 (Question framing)
```
The "files are all you need" benchmarks:
- LoCoMo: conversational retrieval
- Test size: benchmark scale

What's missing:
- Enterprise codebase scale (millions of tokens)
- Multi-hop reasoning benchmarks
- Temporal query handling
- Latency at different corpus sizes

74% on LoCoMo doesn't tell us about production at scale.

Neither does my anecdotal experience that files stop working.

We need better benchmarks. Until then, it's all vibes and commercial incentives.

[link]
```

---

## LinkedIn

### Option 1 (Honest framing)
```
There's a growing consensus: files are all you need for AI agent memory.

Letta shows 74% accuracy on LoCoMo using filesystem tools. LlamaIndex argues agents should learn from instruction files. Harrison Chase (LangChain) says "file systems are a natural and powerful way to represent agent state."

Store conversations in markdown. Grep your way to knowledge.

I've been skeptical of this. But I realized I should acknowledge something:

Every company pushing "files are all you need" sells file processing infrastructure.
Every company pushing "you need structured memory" sells structured memory.

I work on Hindsight - a structured memory system. I have the opposite bias.

So what do I actually know vs what am I speculating?

What I've observed directly:
- Files work well under ~100K tokens
- Iterative agent search can handle multi-hop queries (costs multiple LLM calls)
- Temporal queries ("what happened last week") need date parsing - files don't help here
- Context rot is real - models degrade past ~256K tokens even within "official" limits

What I don't have:
- Controlled benchmarks proving structured memory beats files at specific thresholds
- Data on exact scale where file approaches break

The LoCoMo benchmark tests conversational retrieval at benchmark scale. It doesn't tell us about enterprise codebases or long-horizon agents.

My take: files are a good foundation. Whether you need additional structure depends on your query patterns, scale, and latency requirements. Start simple, add complexity when you hit actual problems.

[link]
```

### Option 2 (Technical nuance)
```
The multi-hop query problem in AI agents:

"Was Alice affected by infrastructure issues?"

Your knowledge:
- Alice leads Project Atlas
- Project Atlas uses Kubernetes
- Kubernetes had an outage Tuesday

A naive file search finds chunks about Alice OR infrastructure. Can't traverse the chain.

But there are file-based solutions:
1. Embeddings capturing semantic relationships
2. Hierarchical file structures
3. Agent-driven iterative search (read Alice's file → find Atlas → follow reference)

The iterative approach works. I've used it. The agent follows the trail across files. But it costs multiple LLM calls per query.

With pre-built entity graphs, that traversal is a single lookup.

The trade-off: build-time complexity vs query-time cost.

File-based iterative search:
+ Simpler to implement
+ No entity extraction pipeline
- Higher latency per query
- More LLM calls

Structured graphs:
+ Fast traversal
+ Single lookup for multi-hop
- Build-time complexity
- Entity resolution challenges

Neither is objectively better. It depends on query patterns and latency requirements.

Start with files. Measure where you hit limits. Add structure where it actually helps.

[link]
```
