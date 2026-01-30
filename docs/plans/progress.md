# TDD Progress Tracker

**Last Updated**: 2026-01-30
**Current Status**: Phase 6 Component 3 COMPLETED

---

## Phase 5.6: Persistence Layer ✅

### Component 1: Schema & Initialization ✅

**Status**: All tests passing (7/7 in test_sqlite_client.py)

- ✅ Define SQL schema for domain tables (native SQLite)
- ✅ Update `SQLiteClient` to initialize domain tables
- ✅ Enable foreign key support

### Component 2: QuestionnaireStore (SQL) ✅

**Status**: All tests passing (5/5 in test_questionnaire_store.py)

- ✅ Refactor store to use `SQLiteClient`
- ✅ Implement SQL CRUD operations

### Component 3: RunStore (SQL) ✅

**Module**: `src/domain/run_store.py`
**Test File**: `tests/test_run_store.py` & `tests/test_run_config.py`
**Status**: All tests passing (8/8)

- ✅ Refactor store to use `SQLiteClient`
- ✅ Implement SQL CRUD operations
- ✅ Handle JSON serialization for complex fields (retrieved chunks)
- ✅ Implement immutable `RunConfig` separation and reusability

### Component 4: Citation Normalization ✅

**Status**: All tests passing (2/2 in test_citation_normalization.py)

- ✅ Create `citations` table
- ✅ Refactor `RunStore` to use relational citations instead of JSON
- ✅ Verify cascade deletion

### Component 5: Retrieved Chunks Normalization ✅

**Status**: All tests passing (2/2 in test_chunks_normalization.py)

- ✅ Create `retrieved_chunks` table
- ✅ Refactor `RunStore` to use relational chunks helper methods
- ✅ Verify cascade deletion
- ✅ Remove redundant JSON columns

---

## Phase 6: Refinement & Optimization 🚧

### Component 1: Evaluation Pipeline ✅

**Status**: Completed (Metrics, Ground Truth, and Evaluation CLI implemented)

- ✅ Implement metrics
  - ✅ Precision@K
  - ✅ Recall@K
  - ✅ MRR
  - ✅ Answer Relevancy (Semantic similarity)
- ✅ Establish and import Ground Truth (NotebookLM output with section/order preservation)
- ✅ Automate evaluation runner logic (`RAGEvaluator`)
- ✅ Create evaluation CLI tool (`run_evaluation.py`)

### Component 2: Orchestration Refinement

**Status**: Pending

- [ ] Integrate LangGraph state management (if needed)
- [ ] Implement conditional routing (e.g., "Not Found" -> Retry/Web Search)

### Component 3: Performance Tuning 🚧

**Status**: In Progress - ExperimentRunner ready, architecture refactored

**Experiments Phase:**
- [x] Create short test questionnaire (3 questions for rapid iteration)
- [x] Establish baseline metrics (Mean Relevancy: 0.8085)
- [x] Run 13 systematic experiments on retrieval and LLM parameters
- [x] Find optimal configuration (temp=0.3, threshold=0.3, top_k=5)
- [x] Achieve +10.7% quality improvement + 28% speed improvement
- [x] Update config.py with optimized defaults for llama3.2
- [x] Create validation scripts (TDD tested)
- [x] Validate on full 50-question: baseline BEATS optimized (-1.47%)
- [x] Plan revised experiment strategy (7 configs × 3 trials)

**Architecture Refactoring:**
- [x] Rename Generator → RAGSystem (better reflects purpose)
- [x] Add configuration parameters to RAGSystem (temperature, top_k, threshold)
- [x] ExperimentRunner uses RAGSystem directly (not Orchestrator)
- [x] RunConfig parameters now applied to RAG system
- [x] Mark Orchestrator for future LangGraph work
- [x] Create code reorganization plan (deferred until after experiments)
- [x] RAGSystem refactored to accept Question objects (uses section metadata)
- [x] QuestionnaireRunner bypasses Orchestrator, uses RAGSystem directly
- [x] All callers verified to use Question objects appropriately

**ExperimentRunner TDD (5/5 tests passing - READY FOR EXPERIMENTS):**
- [x] Test 1: Happy path - returns run_id, questions_answered, success
- [x] Test 2: RAG system called and answers saved to DB
- [x] Test 3: Evaluation performed and metrics returned
- [x] Test 4: Retry logic - fails 2x then succeeds on 3rd attempt
- [x] Test 5: Batch processing - 2 configs × 2 trials = 4 experiments
- [x] Refactored: Removed monkeypatching, use dependency injection with RAGSystem

**Experiment Script Ready:**
- [x] Created scripts/tuning.py (configurable for any questionnaire)
- [x] Supports --questionnaire and --trials arguments
- [x] Tests 7 configurations (baseline, 2 temp, 2 threshold, 2 top-k)
- [x] Refactored for readability (extracted helper functions)

**Next Steps:**
- [ ] Test with 3-question questionnaire (quick validation)
- [ ] Run overnight experiment suite (7 configs × 3 trials = 21 experiments, ~8 hours)
- [ ] Analyze results and update config with validated parameters
- [ ] Document final validated findings
- [ ] Code reorganization (minimal: group rag/, move stores/)

---

## Phase 7: Infrastructure & Deployment 🚧

### Component 1: DigitalOcean Setup ✅

**Status**: doctl authenticated, Python-slim Dockerfile created.

- ✅ Install and authenticate `doctl`
- ✅ Create `Dockerfile` (Python-slim) and `.dockerignore`
- ✅ Create `scripts/entrypoint.sh` for automatic Ollama startup
- ✅ Create DigitalOcean Container Registry (`alesch-registry`)
- ✅ Build lean Docker image (301 MB)
- ✅ Push image to DOCR
- ✅ Setup persistent Volume for models (20GB in NYC3)
- ✅ Create initial setup Droplet
- ✅ Download models to Volume (DeepSeek, Llama3, Gemma, etc.)
- ✅ Create data directory and upload initial DB
- [ ] Create automation scripts
