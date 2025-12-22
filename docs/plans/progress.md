# Phase 2 TDD Progress Tracker

**Last Updated**: 2025-12-22  
**Current Status**: Supabase Client IN PROGRESS 🔄

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

## In Progress

### Component 4: Supabase Client 🔄
**Module**: `src/database/supabase_client.py`  
**Test File**: `tests/test_supabase_client.py`  
**Status**: In progress (2/7 tests passing)

Completed tests:
1. ✅ Initialize connection with credentials
2. ✅ Insert chunk with content, embedding, revision, and status

Remaining tests:
3. ⏳ Batch insert multiple chunks efficiently
4. ⏳ Enforce UNIQUE constraint on (document_id, chunk_id, revision)
5. ⏳ Allow different revisions of same chunk_id
6. ⏳ Mark previous revisions as superseded when inserting new revision
7. ⏳ Query and filter chunks by status

**Key Implementation Details**:
- SupabaseClient class with credential validation
- Connection verification via `is_connected()` method
- `insert_chunk()` method accepts Embedding dataclass, inserts with all fields
- `delete_chunk()` helper method for test cleanup and encapsulation
- Pytest fixtures: module-scoped client, cleanup_test_chunk for setup/teardown
- Table name extracted from config (CHUNKS_TABLE)
- Embedding.vector extracted before database insert

**Latest Commits**:
- c9d719a: Suppress third-party deprecation warnings in pytest
- 6fd22b5: Refactor: Add delete_chunk helper method
- 7028466: Add insert_chunk to SupabaseClient with test

---

## Remaining Components

### Component 5: Full Pipeline Integration
**Module**: `scripts/ingest_corpus.py`  
**Test File**: `tests/test_ingestion_pipeline.py`  
**Status**: Not started

---

