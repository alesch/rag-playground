# Phase 2: Ingestion Plan

## Overview
Build the document ingestion pipeline to load compliance documents, chunk them intelligently, generate embeddings using Ollama, and store them in Supabase with metadata.

## Implementation Tasks

### 1. Configuration Module (`src/config.py`)
**Purpose**: Centralized configuration management
- Load environment variables (Supabase URL/key, Ollama settings)
- Define chunking parameters (chunk size, overlap)
- Define embedding model settings
- Manage logging configuration

### 2. Document Loader (`src/rag/ingestion/document_loader.py`)
**Purpose**: Load markdown documents from filesystem
- Read markdown files from `data/corpus/`
- Extract revision number from markdown frontmatter (version field)
- Extract document metadata (filename, type, sections)
- Preserve markdown structure (headers, lists, code blocks)
- Return structured document objects
- Raise error if version field missing in frontmatter

### 3. Chunking Logic (`src/rag/ingestion/chunker.py`)
**Purpose**: Split documents into semantic chunks
- **Markdown-aware chunking**: Split by headers while preserving context
- **Chunk size**: ~500-1000 tokens per chunk
- **Overlap**: 50-100 tokens between chunks to maintain context
- **Metadata extraction**: Section names, subsections, hierarchy, revision
- Generate unique chunk IDs
- Preserve revision number in each chunk's metadata

### 4. Embedding Pipeline (`src/rag/ingestion/embedder.py`)
**Purpose**: Generate vector embeddings using Ollama
- Initialize Ollama embedding client (mxbai-embed-large)
- Batch embedding generation for efficiency
- Handle rate limiting and errors
- Return 1024-dimensional vectors

### 5. Supabase Client (`src/infrastructure/database/supabase_client.py`)
**Purpose**: Database operations for storing embeddings with revision management
- Initialize Supabase connection
- Insert chunks with embeddings, metadata, revision, and status
- Batch insert operations with revision tracking
- Mark previous revisions as 'superseded' when inserting new revision
- Query operations to filter by status (active/superseded/archived)
- Error handling and logging
- Schema: UNIQUE(document_id, chunk_id, revision), status field

### 6. Ingestion Script (`scripts/ingest_corpus.py`)
**Purpose**: Orchestrate the full ingestion pipeline
- Load all documents from corpus folder (with revisions)
- Chunk each document (preserving revision)
- Generate embeddings for all chunks
- Store in Supabase with revision and status='active'
- Automatically mark previous revisions as 'superseded'
- Progress tracking and logging
- Summary statistics including revision information

### 7. Jupyter Notebook (`notebooks/02_ingest_documents.ipynb`)
**Purpose**: Interactive learning and experimentation
- Step-by-step walkthrough of ingestion process
- Visualize chunks and their sizes
- Compare chunking strategies
- Test embedding generation
- Validate database storage

## Testing Strategy

**Type**: Integration tests (technical implementation with managed dependencies)

1. **Document Loader**: Load files from filesystem, extract revision from frontmatter
2. **Chunker**: Split documents, preserve revision in chunk metadata
3. **Embedder**: Generate embeddings via Ollama API
4. **Supabase Client**: Store chunks, manage revisions, update status
5. **Full Pipeline**: End-to-end ingestion with revision tracking
6. **Re-ingestion**: Test that new revisions mark old ones as superseded
7. **Validation**: Query database to verify active chunks only

## Success Criteria

- ✅ All 4 corpus documents successfully ingested with revisions
- ✅ Chunks properly sized (500-1000 tokens)
- ✅ Embeddings generated (1024 dimensions)
- ✅ Metadata preserved (source, section, tags, revision)
- ✅ ~50-100 total chunks in database with status='active'
- ✅ Re-ingesting document marks old revisions as 'superseded'
- ✅ Can query and retrieve only active chunks from Supabase
- ✅ UNIQUE constraint on (document_id, chunk_id, revision) enforced

## Key Learning Points

- How markdown-aware chunking preserves document structure
- Trade-offs between chunk size and retrieval accuracy
- How to batch process embeddings efficiently
- Understanding vector storage in pgvector

## Implementation Order

1. Start with `config.py` - foundation for all other modules
2. Build `document_loader.py` - test with one document
3. Implement `chunker.py` - experiment with chunk sizes
4. Create `supabase_client.py` - test database connection
5. Build `embedder.py` - generate embeddings for test chunks
6. Integrate everything in `ingest_corpus.py`
7. Create interactive notebook for learning and experimentation
