# TDD Progress Tracker

**Last Updated**: 2026-01-10
**Current Status**: Phase 5.6 Persistence Layer IN PROGRESS

---

## Phase 5.6: Persistence Layer

### Component 1: Schema & Initialization
**Status**: Pending
- [ ] Define SQL schema for domain tables
- [ ] Update `SQLiteClient` to initialize domain tables

### Component 2: QuestionnaireStore (SQL)
**Status**: Pending
- [ ] Refactor store to use `SQLiteClient`
- [ ] Implement SQL CRUD operations

### Component 3: RunStore (SQL)
**Status**: Pending
- [ ] Refactor store to use `SQLiteClient`
- [ ] Implement SQL CRUD operations
- [ ] Handle JSON serialization for complex fields

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