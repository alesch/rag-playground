# TDD Progress Tracker

**Last Updated**: 2026-01-23
**Current Status**: Phase 6 Component 1 COMPLETED

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

### Component 3: Performance Tuning

**Status**: Pending

- [ ] Optimize chunk sizes and overlap
- [ ] Tune retrieval `top_k` and similarity thresholds
- [ ] Refine LLM prompts

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
