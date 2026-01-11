# Phase 5.5: Domain Module

**Goal**: Model the core domain (questionnaires and answers) with persistence and comparison support.

**Module**: `src/domain/`

**Naming**:
- `run` = config + answers grouping
- `domain` = module name (models questionnaires & answers)

---

## TDD Implementation Order

### Component 1: QuestionnaireStore (5 tests)
Module: `src/domain/questionnaire_store.py`

1. Save and retrieve questionnaire by ID
2. Save batch of questions with sequence
3. Import from markdown file (reuse existing regex)
4. List questionnaires filtered by status
5. Handle duplicate questionnaire ID (upsert or error)

### Component 2: RunStore (6 tests)
Module: `src/domain/run_store.py`

1. Create run with full config snapshot
2. Save answer with retrieved chunks
3. Save answer with citations
4. Get all answers for an run
5. Get specific answer by run + question
6. List runs filtered by status

### Component 3: QuestionnaireRunner (4 tests)
Module: `src/domain/runner.py`

1. Run answer_set for single question
2. Run answer_set for full questionnaire
3. Capture query embedding in trace
4. Handle generation errors gracefully

---

## Verification After implementation:

1. Import questionnaire
2. Trigger a run to get answers
3. Query results
