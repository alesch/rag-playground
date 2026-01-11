# TDD Progress Tracker

**Last Updated**: 2026-01-10
**Current Status**: Phase 5.6 Persistence Layer IN PROGRESS

---

## Phase 5.6: Persistence Layer

### Component 1: Infrastructure
**Status**: Pending
- [ ] Add `sqlalchemy` dependency
- [ ] Configure database engine (SQLite/Postgres)
- [ ] Create session management

### Component 2: Schema Definition
**Status**: Pending
- [ ] Define `questionnaires`, `questions`, `runs`, `answers` tables
- [ ] Verify schema creation in SQLite

### Component 3: Stores Refactoring
**Status**: Pending
- [ ] Refactor `QuestionnaireStore` to use SQL repository
- [ ] Refactor `RunStore` to use SQL repository
- [ ] Update tests to use in-memory DB

---

## Phase 6: Refinement & Optimization

### Component 1: Evaluation Pipeline
**Status**: Pending
- [ ] Implement metrics (Precision, Recall, Answer Relevancy)
- [ ] Automate evaluation against `model_comparison.csv` ground truth

### Component 2: Orchestration Refinement
**Status**: Pending
- [ ] Integrate LangGraph state management (if needed)
- [ ] Implement conditional routing (e.g., "Not Found" -> Retry/Web Search)

### Component 3: Performance Tuning
**Status**: Pending
- [ ] Optimize chunk sizes and overlap
- [ ] Tune retrieval `top_k` and similarity thresholds
- [ ] Refine LLM prompts