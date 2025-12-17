# Social Media - Rich Fact Extraction: Preserving Narrative, Not Just Statements

## Twitter/X

### Option 1 (Problem → Solution)
```
Traditional RAG fragments conversations into isolated statements.

"Why did they choose X?" returns "They chose X."

The reasoning chain is gone.

Hindsight extracts 2-5 narrative facts per conversation:
- Preserves emotions
- Keeps reasoning chains
- Maintains causal links
- Self-contained context

Query returns understanding, not fragments.

[link]
```

### Option 2 (Concrete example)
```
Same text, two RAG approaches:

Fragment-based:
- "Bob suggested Summer Vibes"
- "They decided on Beach Beats"

Narrative-based:
- "Alice and Bob chose 'Beach Beats' for its playful tone. Bob suggested 'Summer Vibes' for catchiness, but Alice wanted unique."

Query "why Beach Beats?" → one returns nothing useful, one answers the question.

[link]
```

### Option 3 (Technical)
```
Hindsight's extraction pipeline:

1. Coreference resolution ("she" → "Alice")
2. Temporal normalization ("last week" → date)
3. Participant attribution
4. Reasoning preservation
5. Fact classification (world/experience/opinion)
6. Entity extraction

Output: 2-5 narrative facts with causal links, not 50 fragments.

[link]
```

---

## LinkedIn

### Option 1 (Story format)
```
I built a RAG system that could tell me "Alice works at Google" but couldn't answer "Why did Alice join Google?"

The problem: traditional chunking fragments conversations into isolated statements. Context disappears. Reasoning chains break.

From "Alice joined Google last spring and was thrilled about the research opportunities," my system stored:
- "Alice joined Google"
- "Alice was thrilled"

Two disconnected facts. The causal relationship between research opportunities and her decision? Gone.

Hindsight takes a different approach.

Instead of sentence-level fragments, it extracts 2-5 narrative facts per conversation. Each fact is self-contained and preserves:
- Emotional context
- Reasoning chains
- Causal relationships
- Participant attribution

The same input becomes: "Alice joined Google in spring, specifically choosing it for the research opportunities, which excited her."

One fact. Complete context. Query "why did Alice join?" and you get an actual answer.

The extraction layer is where memory quality is won or lost.

Technical deep-dive: [link]
```

### Option 2 (Direct value)
```
Your RAG system returns statements. It should return understanding.

The difference is in extraction.

Traditional approach:
- Fragment text into sentences
- Store isolated statements
- Query returns "Alice joined Google"

Narrative approach (Hindsight):
- Extract 2-5 comprehensive facts per conversation
- Preserve reasoning chains and causal links
- Query returns "Alice joined Google for research opportunities, which excited her"

Under the hood, Hindsight runs 6 extraction steps:
1. Coreference resolution
2. Temporal normalization
3. Participant attribution
4. Reasoning preservation
5. Fact classification
6. Entity extraction

The context parameter guides what to focus on - same content with "career discussion" vs "team health assessment" extracts different emphasis.

Fragment-based systems answer "what." Narrative-based systems answer "why."

Full breakdown: [link]
```
