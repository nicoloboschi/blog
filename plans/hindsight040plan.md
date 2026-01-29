# Hindsight 0.4.0 Technical Blog Series Plan

**Context**: Technical deep-dive series following the announcement blog at https://hindsight.vectorize.io/blog/learning-capabilities

**Instructions**:
- Full documentation: https://hindsight.vectorize.io/llms-full.txt
- Only use code from the documentation - do not make up any code
- Hindsight paper: https://arxiv.org/html/2512.12818v1
- No marketing bs - keep the narrative simple and humble
- Always include reference to [Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight) at the end of each post

---

## Post 1: "Hindsight 0.4.0: from facts to insights: how observations work"
**Status**: ✅ Complete
**File**: `content/posts/hindsight040-observations.md`
**Focus**: Deep dive into the automatic knowledge consolidation system

**Topics to cover**:
- How observations synthesize knowledge from multiple facts
- Evidence tracking vs old confidence scores (migration from 0.3.0)
- The automatic trigger after `retain()` calls
- Evolution tracking - how observations capture knowledge journeys, not just current states
- How mission statements influence observation generation
- Migration from opinions/entity summaries to observations
- Implementation details: when observations are created vs updated

**Target**: 2000-2500 words with Python/TypeScript examples

---

## Post 2: "Hindsight 0.4.0: mental models: pre-computed knowledge for instant recall"
**Status**: Planned
**Focus**: User-curated summaries and key-value lookup system

**Topics to cover**:
- Why mental models solve the latency/consistency problem
- Creation via API with source queries
- Auto-refresh mechanisms when observations update
- Priority hierarchy during reflect: mental models → observations → facts
- Use cases: when to use mental models vs let observations handle it
- Performance implications and cost savings (no LLM calls)
- User-reviewed quality control vs automatic synthesis

**Target**: 2000-2500 words with API examples

---

## Post 3: "Hindsight 0.4.0: building agentic reflect: reasoning through iteration"
**Status**: Planned
**Focus**: The new reflect system's architecture and how it differs from 0.3.0

**Topics to cover**:
- How the new reflect differs from 0.3.0 (deeper agentic iteration)
- Agentic iteration for deeper reasoning
- The hierarchy: mental models → observations → facts
- Custom prompts for memory extraction
- Real-world examples of complex queries requiring multi-hop reasoning
- When to use reflect vs recall

**Target**: 2000-2500 words with implementation examples

---

---

## Post 4: "Hindsight 0.4.0: memory tagging: organizing and filtering at scale"
**Status**: Planned
**Focus**: Memory tagging system for better organization

**Topics to cover**:
- Label and filter memories during recall/reflect
- Tagging strategies for different use cases
- How tags work with the hierarchy (mental models, observations, facts)
- MCP retain tool timestamp support
- Migration patterns for existing memory banks
- Best practices for tag naming and structure
- Custom prompts for memory extraction with tags

**Target**: 2000-2500 words with practical examples

---

## Post 5: "Hindsight 0.4.0: worker services: running background memory tasks at scale"
**Status**: Planned
**Focus**: Production deployment patterns for distributed systems

**Topics to cover**:
- Worker service architecture for background tasks
- When to use workers vs inline processing
- Background operations: batch_retain, form_opinion, reinforce_opinion, observation regeneration
- Backup/restore tooling
- Large memory bank performance (graph/MPFP retrieval fixes)
- Offline migrations for air-gapped environments
- Delete memory bank capability
- Monitoring and operations

**Target**: 2000-2500 words with deployment examples

---

## Post 7 (Optional): "Hindsight 0.4.0: directives: compliance framework for agent memory"
**Status**: Planned
**Focus**: Hard constraints for compliance, privacy, and safety

**Topics to cover**:
- What directives are vs disposition traits
- Absolute requirements during reflect operations
- Compliance, privacy, and safety use cases
- Creating and managing directives via API
- Real-world examples: GDPR compliance, PII handling
- Integration with mental models and observations

**Target**: 1500-2000 words (shorter, focused post)
