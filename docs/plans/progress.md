# Phase 2 TDD Progress Tracker

**Last Updated**: 2026-01-05
**Current Status**: Full Pipeline Integration IN PROGRESS 🔄

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

**Key Implementation Details**:
- SupabaseClient class with credential validation
- Connection verification via `is_connected()` method
- ChunkKey dataclass for composite key (document_id, chunk_id, revision)
- ChunkRecord dataclass using composition (contains ChunkKey + data)
- `insert_chunk()` method accepts ChunkRecord, auto-supersedes previous active revisions
- `batch_insert_chunks()` method for efficient bulk inserts
- `delete_chunk()` method accepts ChunkKey for test cleanup
- `get_chunk_revisions()` returns `Dict[int, ChunkRecord]`
- `query_chunks_by_status()` returns `List[ChunkRecord]` filtered by status
- `_row_to_chunk_record()` helper to reconstruct ChunkRecord from DB row
- `_prepare_chunk_data()` helper method to reduce duplication
- Pytest module-scoped client fixture
- Table name extracted from config (CHUNKS_TABLE)
- JSON parsing for embedding vectors returned as strings from Supabase

---

## In Progress

### Component 5: Full Pipeline Integration 🔄
**Module**: `scripts/ingest_corpus.py`
**Test File**: `tests/test_ingestion_pipeline.py`
**Status**: In progress (3/4 tests passing)

Completed tests:
1. ✅ Ingest single document end-to-end
2. ✅ Ingest full corpus (4 documents)
3. ✅ Re-ingestion supersedes previous revisions

Remaining tests:
4. ⏳ Ingestion returns statistics

**Key Implementation Details**:
- `IngestionResult` dataclass for single document results
- `CorpusIngestionResult` dataclass for corpus results
- `ingest_document()` loads, chunks, embeds, and stores a single document
- `ingest_corpus()` processes all documents in a directory
- `_process_document()` helper eliminates duplication
- `_build_chunk_records()` helper for ChunkRecord construction
- Batch operations: `generate_embeddings()` + `batch_insert_chunks()`
- `batch_insert_chunks()` auto-supersedes previous active revisions
- Renamed `batch_embed` to `generate_embeddings` for clarity

**Test Performance Optimizations**:
- `MockSupabaseClient` in conftest.py for in-memory database testing
- `mock_embeddings` fixture returns deterministic fake embeddings
- `mock_database` fixture patches SupabaseClient in ingest_corpus module
- Integration tests run in ~0.5s instead of ~116s (230x speedup)
- Supabase client tests still hit real database for full validation

---
