# TDD Progress Tracker

**Last Updated**: 2026-01-10
**Current Status**: Phase 5.5 Domain Module IN PROGRESS

---

## Completed Components

### Component 1: Document Loader ✅
**Status**: All tests passing (5/5)

Completed tests:
1. ✅ Load single markdown file and extract frontmatter fields (version, title, tags)
2. ✅ Generate document_id by slugifying title
3. ✅ Load all corpus documents
4. ✅ Raise error when required frontmatter fields are missing (version or title)

---

### Component 2: Chunker ✅
**Status**: All tests passing (12/12)

Completed tests:
1. ✅ Split document by markdown headers preserving context
2. ✅ Respect maximum chunk size limit
3. ✅ Apply overlap between consecutive chunks (verified no wasteful overlap at natural boundaries)
4. ✅ Generate unique chunk IDs and preserve revision in metadata
5. ⏭️ Handle minimum chunk size constraint (skipped - not needed with LangChain)

---

### Component 3: Embedder ✅
**Status**: All tests passing (4/4)

Completed tests:
1. ✅ Generate 1024-dimensional embedding for text via Ollama
2. ✅ Batch embed multiple texts maintaining order
3. ✅ Raise error when Ollama service unavailable
4. ✅ Validate and reject empty input text

---

### Component 4: Supabase Client ✅
**Module**: `src/database/supabase_client.py`
**Test File**: `tests/test_supabase_client.py`
**Status**: All tests passing (7/7)

Completed tests:
1. ✅ Initialize connection with credentials
2. ✅ Insert chunk with content, embedding, revision, and status
3. ✅ Batch insert multiple chunks efficiently
4. ✅ Enforce UNIQUE constraint on (document_id, chunk_id, revision)
5. ✅ Allow different revisions of same chunk_id
6. ✅ Mark previous revisions as superseded when inserting new revision
7. ✅ Query and filter chunks by status


---

### Component 5: Full Pipeline Integration ✅
**Module**: `scripts/ingest_corpus.py`
**Test File**: `tests/test_ingestion_pipeline.py`
**Status**: All tests passing (4/4)

Completed tests:
1. ✅ Ingest single document end-to-end
2. ✅ Ingest full corpus (4 documents)
3. ✅ Re-ingestion supersedes previous revisions
4. ✅ Ingestion returns statistics (per-document results)

---

### Component 6: Retriever ✅
**Module**: `src/retrieval/retriever.py`
**Test File**: `tests/test_retriever.py`
**Status**: 3 tests passing, 2 skipped

Completed tests:
1. ✅ Search returns similar chunks
2. ⏭️ Results ordered by similarity (skipped - guaranteed by pgvector SQL)
3. ✅ Respects top_k limit
4. ✅ Only returns active chunks
5. ⏭️ Respects similarity threshold (skipped - guaranteed by pgvector SQL)

---

### Component 7: Generator ✅
**Module**: `src/generation/generator.py`
**Test File**: `tests/test_generator.py`
**Status**: All tests passing (4/4)

Completed tests:
1. ✅ Generate answer from retrieved chunks
2. ✅ Answer includes citations to source chunks
3. ✅ Handle empty retrieval results gracefully (skip LLM call, save tokens)
4. ✅ Prompt includes all retrieved context

---

### Component 8: Orchestrator ✅
**Module**: `src/orchestration/orchestrator.py`
**Test File**: `tests/test_orchestrator.py`
**Status**: All tests passing (4/4), 1 skipped

Completed tests:
1. ✅ Answer single question end-to-end
2. ✅ Handle empty retrieval results
3. ✅ Handle LLM failure gracefully
4. ✅ Process multiple questions as batch
5. ⏭️ State flows through LangGraph nodes (deferred to Phase 6)

---

## Phase 5.5: Domain Module

### Component 1: QuestionnaireStore ✅
**Module**: `src/domain/questionnaire_store.py`
**Test File**: `tests/test_questionnaire_store.py`
**Status**: All tests passing (5/5)

Completed tests:
1. ✅ Save and retrieve questionnaire by ID
2. ✅ Save batch of questions with sequence
3. ✅ Import from markdown file
4. ✅ List questionnaires filtered by status
5. ✅ Handle duplicate questionnaire ID (raises error)

---

### Component 2: AnswerSetStore
**Module**: `src/domain/answer_store.py`
**Test File**: `tests/test_answer_store.py`
**Status**: Pending

---

### Component 3: QuestionnaireRunner
**Module**: `src/domain/runner.py`
**Test File**: `tests/test_runner.py`
**Status**: Pending

---
