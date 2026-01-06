# Phase 3: Retrieval Plan

## Goal
Implement similarity search to find relevant document chunks for a given query.

## Architecture
Create a separate `Retriever` class that:
- Takes a query string
- Generates an embedding for the query
- Searches for similar chunks in the database
- Returns ranked results with similarity scores

## Components

### 1. Retriever Module
**Location**: `src/retrieval/retriever.py`

Responsibilities:
- Accept natural language queries
- Coordinate embedding generation and database search
- Return ranked search results

### 2. Database Search Method
**Location**: `src/database/supabase_client.py`

Add vector similarity search using pgvector's cosine distance operator.

## TDD Test Plan

| Test | Description | Status |
|------|-------------|--------|
| 1 | Search returns similar chunks | ✅ |
| 2 | Results ordered by similarity | ⏭️ Skipped |
| 3 | Respects top_k limit | |
| 4 | Only returns active chunks (not superseded) | |
| 5 | Respects similarity threshold | |

### Test 2 Skipped - Rationale
Ordering is guaranteed by pgvector's `ORDER BY embedding <=> query_embedding` in the SQL function.
The ordering logic lives in the database, not in Python code we wrote.
Testing ordering in a mock would only test the mock, not our actual code.

## Files to Create/Modify

- `src/retrieval/__init__.py` - new
- `src/retrieval/retriever.py` - new
- `src/database/supabase_client.py` - add search method
- `tests/test_retriever.py` - new
