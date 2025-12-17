# Hindsight Blog Series Plan

Instructions: 
- Full documentation: https://hindsight.vectorize.io/llms-full.txt
- Only use piece of code from the documentation - do not make up any code
- Hindsight paper: https://arxiv.org/html/2512.12818v1 - refer to the paper and get information from here also
- No marketing bs - keep the narrative simple and humble - do not make strong assumptions
- Always include reference to [Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight) at the end of each post

## Core Concepts
- [x] **Retain, Recall, Reflect: The Three Operations of Agent Memory** - Deep-dive into what each operation does, when to use which, with code examples → `hindsight-retain-recall-reflect.md` (draft)
- [x] **Memory Types: World, Experience, Opinion, Observations** - How Hindsight categorizes memories and why it matters → `hindsight-memory-types.md` (draft)
- [x] **Opinions with Confidence Scores: How Agents Form Beliefs** - The opinion evolution mechanism, evidence accumulation → `hindsight-opinions-confidence-scores.md`

## Architecture / Engineering
- [x] **Beyond Vector Search: How TEMPR Combines 4 Retrieval Strategies** - Semantic + BM25 + Graph + Temporal, reciprocal rank fusion, cross-encoder reranking → `hindsight-tempr-retrieval.md` (draft)
- [x] **Token Budgets vs Top-K: A Better Way to Fill Context Windows** - Why token-based retrieval beats arbitrary limits → `hindsight-token-budgets.md` (draft)
- [x] **Rich Fact Extraction: Preserving Narrative, Not Just Statements** - How Hindsight captures emotions, reasoning chains, causal relationships → `hindsight-rich-fact-extraction.md`
- [ ] **Entity Resolution Without Training Data** - Name similarity (50%) + co-occurrence (30%) + temporal proximity (20%), the 0.6 threshold

## Practical / How-To
- [ ] **Per-User Memory Banks: Building Personalized AI Assistants** - Isolated memory per user, code walkthrough
- [ ] **Combining Personal Memory with Shared Knowledge** - Multi-bank architecture pattern
- [ ] **Adding Memory to Your OpenAI Agent** - Integration guide with code
- [ ] **Disposition Traits: Tuning Skepticism, Literalism, and Empathy** - Practical effects of each trait on agent behavior

## Comparisons
- [ ] **Hindsight vs Traditional RAG: What You Actually Get** - Multi-hop reasoning, temporal filtering, entity understanding vs pure vector similarity
- [ ] **When Vector Search Falls Short** - Concrete examples where semantic-only retrieval fails

---

## Notes
- Each post should be standalone but can reference others
- Code examples in Python
- Keep posts short and technical, no fluff
- Source: https://hindsight.vectorize.io/llms-full.txt
