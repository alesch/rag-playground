# Roadmap: Retrieved Chunks Normalization

This roadmap defines the plan for moving retrieved chunks from a JSON blob in the `answers` table to a dedicated normalized table.

## Context
Currently, `RetrievedChunk` objects are serialized to JSON and stored in `answers.retrieved_chunks_json`. Normalizing this allows for better analytics, performance, and data integrity.

## Proposed Schema: `retrieved_chunks`

| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `answer_id` | TEXT | REFERENCES answers(id) ON DELETE CASCADE |
| `document_id` | TEXT | NOT NULL |
| `chunk_id` | TEXT | NOT NULL |
| `revision` | INTEGER | NOT NULL |
| `content` | TEXT | snapshot for audit |
| `similarity_score` | REAL | |
| `rank` | INTEGER | |

## TDD Cycles

### Cycle 1: basic Persistence (Persist & Load)
- [ ] **RED**: Create test verifying that saving an answer results in records in the `retrieved_chunks` table.
- [ ] **GREEN**: Update `SQLiteClient` schema and `RunStore` persistence/loading logic.
- [ ] **REFACTOR**: Ensure clean mapping between `RetrievedChunk` dataclass and SQL.

### Cycle 2: Data Integrity
- [ ] **RED**: Create test verifying that deleting an Answer or a Run cascades to the `retrieved_chunks` table.
- [ ] **GREEN**: Verify SQLite native cascade execution.

### Cycle 3: Deprecation of JSON
- [ ] **RED**: Ensure all existing tests pass while JSON column is still present but unused.
- [ ] **GREEN**: Remove `retrieved_chunks_json` from schema and all associated code in `RunStore`.
- [ ] **REFACTOR**: Update documentation and completion status.
