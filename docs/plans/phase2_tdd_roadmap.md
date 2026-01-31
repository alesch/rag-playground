# Phase 2 TDD Roadmap: Document Ingestion Pipeline

**Type**: Technical Implementation (Infrastructure)  
**Test Approach**: Integration tests with real dependencies  
**Implementation Style**: Single test at a time with RED→GREEN→REFACTOR cycles

---

## Component 1: Document Loader
**Module**: `src/rag/ingestion/document_loader.py`  
**Test File**: `tests/test_document_loader.py`

1. Load single markdown file and extract frontmatter fields (version, title, tags)
2. Generate document_id by slugifying title
3. Load all corpus documents
4. Raise error when required frontmatter fields are missing (version or title)

---

## Component 2: Chunker
**Module**: `src/rag/ingestion/chunker.py`  
**Test File**: `tests/test_chunker.py`

1. Split document by markdown headers preserving context
2. Respect maximum chunk size limit
3. Apply overlap between consecutive chunks
4. Generate unique chunk IDs and preserve revision in metadata
5. Handle minimum chunk size constraint

---

## Component 3: Embedder
**Module**: `src/rag/ingestion/embedder.py`  
**Test File**: `tests/test_embedder.py`

1. Generate 1024-dimensional embedding for text via Ollama
2. Batch embed multiple texts maintaining order
3. Raise error when Ollama service unavailable
4. Validate and reject empty input text

---

## Component 4: Supabase Client
**Module**: `src/infrastructure/database/supabase_client.py`  
**Test File**: `tests/test_supabase_client.py`

1. Initialize connection with credentials
2. Insert chunk with content, embedding, revision, and status
3. Batch insert multiple chunks efficiently
4. Enforce UNIQUE constraint on (document_id, chunk_id, revision)
5. Allow different revisions of same chunk_id
6. Mark previous revisions as superseded when inserting new revision
7. Query and filter chunks by status

---

## Component 5: Full Pipeline Integration
**Module**: `scripts/ingest_corpus.py`  
**Test File**: `tests/test_ingestion_pipeline.py`

1. Ingest single document end-to-end with all pipeline steps
2. Re-ingest document with new revision, marking old as superseded
3. Ingest all corpus documents with progress tracking
4. Validate chunk quality (size, embeddings, metadata)

---

## Implementation Order

1. Document Loader
2. Chunker
3. Embedder
4. Supabase Client
5. Full Pipeline

Each test: RED→GREEN→REFACTOR before next test.

---

## Prerequisites

- Python venv activated
- Ollama running locally
- Supabase credentials configured
- Corpus files have version frontmatter
- Database schema includes revision and status fields
