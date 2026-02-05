# Social Media - Hierarchical Context in Hindsight

## Twitter/X

### Option 1 (Problem → Hierarchy)
```
RAG treats all context the same. Everything's just "similar embeddings."

A curated company policy and a random fact from 3 months ago? Same priority.

Hindsight uses a knowledge hierarchy:

Mental Models (curated summaries)
→ Observations (auto-consolidated patterns)
→ Raw Facts (foundation)

reflect() checks in that order.

Consistency where you need it. Freshness everywhere else.

[link]
```

### Option 2 (Technical breakdown)
```
How Hindsight organizes knowledge:

Level 1: Mental Models
- User-created summaries
- "What's our API policy?" → always same answer
- Curated, consistent

Level 2: Observations
- Auto-generated entity profiles
- Emerge from accumulated facts
- Update as evidence grows

Level 3: Raw Facts
- World facts, experiences
- Foundation for everything

reflect() traverses top to bottom. RAG doesn't have this structure.

[link]
```

### Option 3 (Consistency problem)
```
Ask your RAG system "What's our hiring policy?" twice.

First: "Prioritize senior engineers with distributed systems experience"
Second: "We prefer candidates with distributed systems background"

Same meaning. Different phrasing. Inconsistent.

Hindsight solves this with mental models. Create once, reflect uses it consistently.

Still fresh for new queries without predefined models.

[link]
```

---

## LinkedIn

### Option 1 (Problem-solution story)
```
I was building a technical advisor agent and hit the consistency problem hard.

Ask the same question twice → slightly different answers. The LLM re-synthesizes from raw facts every time. Not ideal when users expect your agent to be consistent.

This is the fundamental trade-off with RAG: flexibility vs consistency. You can have fresh answers or predictable answers, pick one.

Hindsight 0.4.0 solves this with a knowledge hierarchy.

Three levels:

Mental Models → User-curated summaries for common queries
Observations → Auto-generated entity profiles from accumulated facts
Raw Facts → World facts and experiences (foundation)

When reflect runs, it checks sources in that priority order.

For "What's our API versioning policy?", I create a mental model:
- Versioning via URL path (/v1/, /v2/)
- OAuth2 for authentication
- Pagination required for list endpoints

Every reflect query that touches this topic gets the same canonical answer. Consistency.

But ask about a new API endpoint I just discussed? No mental model exists, so reflect uses recent facts. Freshness.

The hierarchy gives you both:
- Mental models for established knowledge (policies, standards, settled decisions)
- Observations for emerging patterns (entity profiles that consolidate as facts accumulate)
- Raw facts for everything else (detail preservation)

Mental models are curated - you create them explicitly. Observations are automatic - they emerge from evidence. Different creation paths, both are summaries.

Example: hiring criteria.

Mental model approach: Define "Senior Backend Engineer Criteria" explicitly
- 5+ years distributed systems
- Python or Go
- Production PostgreSQL
- Team leadership preferred

Observation approach: Store facts about successful hires, let Hindsight discover the pattern
- "John had 7 years distributed systems experience"
- "Sarah came from Python background"
- "Mike had deep PostgreSQL expertise"

System generates "successful backend hire patterns" observation automatically.

I use mental models for established criteria where I want consistency. I use observations when I want the system to discover patterns from evidence.

The hierarchy also enables multi-hop reasoning. Complex query: "Which contacts would be good for a DevOps role at a Series A startup?"

reflect():
1. Checks mental model for hiring criteria (if defined)
2. Finds observations about contacts with DevOps experience
3. Cross-references facts about their team size preferences
4. Considers experiences from career conversations
5. Synthesizes recommendations

The answer doesn't exist in the memory bank. The agent constructs it by connecting knowledge across hierarchy levels.

Disposition traits (skepticism, literalism, empathy) shape how the hierarchy gets interpreted. Same knowledge structure, different reasoning styles based on personality.

This is what production agents need: structured knowledge that provides consistency without rigidity.

Full breakdown with code examples: [link]
```

### Option 2 (Technical deep dive)
```
Most RAG systems flatten knowledge into "similar chunks." No distinction between:
- A carefully curated summary
- An auto-consolidated pattern
- A random fact from three months ago

Hindsight organizes context hierarchically:

Mental Models (curated summaries)
→ Observations (auto-consolidated patterns)
→ Raw Facts (foundation)

When reflect reasons, it checks sources in priority order.

Mental Models: User-created summaries for common queries

You create these explicitly when you need consistency. "What's our hiring policy?" should return the same answer every time, not LLM variations.

Example: Create a mental model for "Technology Evaluation Criteria"
1. Team expertise match
2. Operational complexity vs benefit
3. Production track record
4. Timeline constraints

Every reflect that touches tech decisions checks this first. Consistent reasoning principles.

Observations: Auto-generated entity profiles

You don't create observations. They emerge from accumulated facts.

Store five+ facts about Alice:
- Works at Google
- Specializes in ML infrastructure
- Planning to join a startup
- Prefers smaller teams
- Python and TensorFlow experience

Hindsight auto-generates observation: "Alice is a software engineer at Google specializing in ML infrastructure. Joined 2020, planning to move to startup. Prefers smaller teams, experienced with Python and TensorFlow."

Observations sit below mental models, above raw facts. If no mental model matches your query, check observations next.

Raw Facts: The foundation

World facts ("Alice works at Google") and experiences ("I discussed Python with Alice") extracted during retain().

These don't get auto-summarized. They're just facts. Detail preservation.

The hierarchy solves the consistency problem:

Without hierarchy:
- Ask "What's our API policy?" twice
- Get slightly different phrasings each time
- Same meaning, inconsistent output

With hierarchy:
- Create mental model for API policy
- Every query gets same canonical answer
- But new questions without models still use fresh facts

You become predictable without becoming rigid.

How reflect traverses the hierarchy:

1. Memory Retrieval - TEMPR searches (semantic + keyword + graph + temporal)
2. Hierarchy Check - Prioritize by level (mental models → observations → facts)
3. Profile Integration - Apply mission, directives, disposition traits
4. Multi-Stage Reasoning - LLM reasons through evidence with personality
5. Opinion Formation - Store conclusions with confidence scores
6. Belief Evolution - Update confidence as new evidence arrives

The budget parameter ("low", "mid", "high") controls how thoroughly reflect searches each level. Use low for simple queries where a mental model likely exists. Use high for complex multi-hop reasoning.

Mission, directives, and disposition shape how the hierarchy gets interpreted:
- Mission: what knowledge to prioritize
- Directives: hard rules (never violate)
- Disposition: interpretation style (skepticism, literalism, empathy on 1-5 scales)

Same hierarchy, different disposition → different reasoning. High skepticism emphasizes risks. Low skepticism emphasizes opportunities.

This is structured knowledge reasoning, not flat context retrieval.

Technical breakdown with examples: [link]
```

### Option 3 (Practical use case)
```
Building a technical advisor agent that needs consistent reasoning patterns but fresh details.

Challenge: standard RAG re-synthesizes from raw facts every time. Ask the same question twice, get slightly different answers.

Solution: Hindsight's hierarchical context.

I created three knowledge levels:

Level 1 - Mental Model: "Technology Evaluation Criteria"
- Team expertise match
- Operational complexity vs benefit
- Production track record
- Timeline constraints

This is curated knowledge I want applied consistently to all tech decisions.

Level 2 - Observations: Auto-generated from facts
After retaining facts about team composition and past projects, Hindsight generates observations about patterns. These update as new evidence arrives.

Level 3 - Raw Facts: Foundation
- "Team has 3 backend engineers, Python and PostgreSQL experience"
- "No Kubernetes experience"
- "Project: 100k users, standard CRUD, 3-month deadline"

Now when I ask: "Should we deploy on Kubernetes or use a simpler platform?"

reflect():
1. Checks mental model (Technology Evaluation Criteria) - finds it
2. Checks observations about Kubernetes decisions - finds patterns from past projects
3. Retrieves raw facts about current team and project
4. Applies mission ("prioritize operational simplicity") and disposition (skepticism: 4)
5. Synthesizes recommendation

Output: recommend against Kubernetes
Reasoning:
- Mental model prioritizes team expertise match
- Facts show no K8s experience
- Mission emphasizes operational simplicity
- High skepticism disposition questions complex solutions

Same hierarchy, different team expertise → different recommendation. Adaptive reasoning grounded in consistent principles.

The hierarchy enables:
- Consistency for established knowledge (mental models)
- Automatic consolidation of patterns (observations)
- Fresh detail when needed (raw facts)
- Personality-driven interpretation (mission + disposition)

Mental models vs observations decision:

Use mental models when:
- Need consistency across queries
- Established policy/standards
- Want human review before use

Use observations when:
- Knowledge accumulates naturally
- Want automatic consolidation
- Pattern should update with new facts

I use mental models for criteria that shouldn't drift. I use observations for entity profiles that should evolve with evidence.

This is what production agents need: structured knowledge that provides guardrails without rigidity.

Full technical breakdown: [link]
```
