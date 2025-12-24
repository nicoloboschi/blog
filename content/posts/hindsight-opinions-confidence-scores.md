+++
date = '2025-12-13T14:00:00+01:00'
draft = false
title = 'Opinions with Confidence Scores: How Agents Form Beliefs'
tags = ["AI", "agents", "memory", "hindsight", "LLM"]
+++

**TL;DR**: Hindsight agents form opinions during reflect operations, storing beliefs with confidence scores from 0 to 1. Evidence accumulates over time, reinforcing or weakening opinions. Disposition traits shape how the same facts lead to different conclusions.

---

## The Problem with Stateless Agents

Most LLM agents have no persistent opinions. Ask them the same question twice with slightly different context, and you get contradictory answers. They don't accumulate expertise or develop consistent perspectives.

Hindsight introduces **opinions** - beliefs that form during reasoning, persist across sessions, and evolve as evidence accumulates. Each opinion carries a confidence score reflecting how firmly the agent holds that view.

## What Opinions Are

Opinions are a memory type distinct from facts. In Hindsight's taxonomy:

| Type | Nature | Example |
|------|--------|---------|
| `world` | Objective facts received | "Redis uses BSD license" |
| `experience` | Agent's interactions | "I discussed caching with Alice" |
| `opinion` | Beliefs with confidence | "Redis is excellent for caching" (0.85) |

The confidence score is the key differentiator. It's a float between 0 and 1 representing belief strength:
- **High (0.8-1.0)**: Strong, well-evidenced belief
- **Mid (0.4-0.7)**: Moderate or tentative view
- **Low (0.0-0.3)**: Weak, easily revisable

An opinion isn't just what the agent thinks - it's what the agent thinks *and how sure it is*.

## How Opinions Form

Opinions emerge during `reflect()` operations. When the agent reasons about a query, it may generate conclusions that get stored as opinions.

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# Store some facts first
client.retain(
    bank_id="tech-advisor",
    content="Redis is an in-memory data store. It's open source under BSD license. Used by Twitter, GitHub, Pinterest for caching.",
    context="technical documentation"
)

# Reflect triggers opinion formation
response = client.reflect(
    bank_id="tech-advisor",
    query="Should I use Redis for our caching layer?",
    context="building a high-traffic web application",
    budget="mid"
)

print(response.text)
# Output: Based on the evidence, Redis is a strong choice for caching.
# It's battle-tested at scale (Twitter, GitHub, Pinterest) and the BSD
# license provides flexibility. For a high-traffic web app, the in-memory
# architecture delivers the performance you need.
```

Behind the scenes, Hindsight forms an opinion like:

```
Opinion: "Redis is excellent for high-traffic caching workloads"
Confidence: 0.85
Entities: [Redis]
```

This happens asynchronously - opinions don't appear in the reflect response directly. They influence *future* reflect calls.

## The Reinforcement Mechanism

Opinions aren't static. New evidence can strengthen, weaken, or contradict them. Hindsight classifies each new piece of evidence:

| Classification | Effect |
|----------------|--------|
| **Reinforce** | Confidence increases (capped at 1.0) |
| **Weaken** | Confidence decreases moderately |
| **Contradict** | Confidence decreases sharply (2x normal adjustment) |
| **Neutral** | No change |

For contradictions, the opinion text itself may be revised.

### Example: Opinion Evolution Over Time

Consider how an opinion about Redis might evolve:

```python
from datetime import datetime

# Day 1: Initial facts
client.retain(
    bank_id="tech-advisor",
    content="Redis is open source under BSD license. Very permissive.",
    timestamp=datetime(2024, 1, 1)
)

# Agent reflects and forms opinion with ~0.85 confidence:
# "Redis is excellent for production use"

# Day 30: License change
client.retain(
    bank_id="tech-advisor",
    content="Redis changed to SSPL license. Not OSI-approved. Some companies prohibit SSPL in production.",
    timestamp=datetime(2024, 1, 30)
)

# Opinion confidence drops to ~0.65
# The contradiction triggers revision:
# "Redis is good for caching but licensing may be a concern for some organizations"

# Day 45: Community response
client.retain(
    bank_id="tech-advisor",
    content="Valkey fork launched as BSD-licensed Redis alternative. Linux Foundation backing. Drop-in compatible.",
    timestamp=datetime(2024, 2, 15)
)

# Opinion updates again (~0.80):
# "Redis is good for caching; consider Valkey if SSPL licensing is problematic"
```

The agent's recommendation evolves naturally. It doesn't flip-flop randomly - it adjusts based on evidence weight. The confidence score tells you how settled the view is.

## Disposition Shapes Opinion Formation

Two agents with identical facts can form different opinions based on their disposition. Three traits matter:

| Trait | Low (1) | High (5) |
|-------|---------|----------|
| **Skepticism** | Trusting, accepts claims readily | Questions everything, demands evidence |
| **Literalism** | Flexible interpretation | Strict, exact interpretation |
| **Empathy** | Detached, fact-focused | Considers emotional/social context |

The same remote work study might produce:

**Low skepticism bank**: "Remote work improves productivity based on the Stanford study"

**High skepticism bank**: "Some evidence suggests remote work may improve productivity, though the Stanford study has methodological limitations worth considering"

Both see the same facts. Disposition determines how those facts translate into beliefs.

### Setting Disposition

```python
# Create a skeptical, literal advisor
client.create_bank(
    bank_id="cautious-advisor",
    disposition={
        "skepticism": 4,    # Questions claims
        "literalism": 4,    # Strict interpretation
        "empathy": 2        # Fact-focused
    }
)

# Create a trusting, empathetic advisor
client.create_bank(
    bank_id="supportive-advisor",
    disposition={
        "skepticism": 2,    # More trusting
        "literalism": 2,    # Flexible
        "empathy": 4        # Considers context
    }
)
```

## Using Opinions in Retrieval

Sometimes you want opinions, sometimes you don't.

```python
# Factual query - exclude opinions
facts = client.recall(
    bank_id="tech-advisor",
    query="What license does Redis use?",
    types=["world"]  # Only objective facts
)

# Advisory query - include opinions
advice = client.recall(
    bank_id="tech-advisor",
    query="What should I use for caching?",
    types=["world", "opinion"]  # Facts + beliefs
)
```

For factual questions ("What is X?"), opinions might inject subjectivity you don't want. For recommendations ("Should I use X?"), opinions carry the agent's accumulated judgment.

## Why This Matters

Traditional RAG returns documents. It doesn't have beliefs. Every query is independent.

With opinion memory:

1. **Consistency**: The agent maintains coherent views across conversations
2. **Evolution**: Beliefs update naturally as evidence accumulates
3. **Transparency**: Confidence scores reveal uncertainty
4. **Personality**: Disposition makes agents feel less like search engines

An agent that's been tracking a technology for months will have nuanced opinions that a fresh RAG query can't match. It remembers the license change, the community response, the performance benchmarks - and has synthesized these into a perspective.

---

Opinions are trajectories, not snapshots. They start somewhere, gather evidence, and adjust. The confidence score is your window into how settled or uncertain the agent's view is.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
