# Citation Normalization Plan

**Goal**: Refactor citation storage from a JSON blob in the `answers` table to a dedicated relational table `citations`.

## 1. Schema Definition

We will add a new table to the SQLite schema in `src/database/sqlite_client.py`.

### `citations` Table
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `answer_id` | TEXT | FOREIGN KEY -> answers(id) ON DELETE CASCADE |
| `document_id` | TEXT | Part of ChunkKey |
| `chunk_id` | TEXT | Part of ChunkKey |
| `revision` | INTEGER | Part of ChunkKey |
| `content_snippet`| TEXT | Text snippet for the citation |

**Note**: The `citations_json` column in the `answers` table will be removed.

## 2. Implementation Steps

### Step 1: Schema Update (TDD)
*   **Red**: Add a test to `tests/test_sqlite_client.py` verifying the existence of the `citations` table.
*   **Green**: Update `SQLiteClient._init_db` to include the new table and remove the old column.

### Step 2: Store Refactoring (TDD)
*   **Red**: Update `tests/test_run_store.py` to verify that citations are correctly persisted and retrieved from the new table.
*   **Green**: 
    *   Update `RunStore.save_answer_success` to perform a batch insert into `citations`.
    *   Update `RunStore._row_to_answer` to query the `answer_citations` table and reconstruct the `Citation` objects.

### Step 3: Verification
*   Verify `ON DELETE CASCADE` behavior: deleting an answer should automatically delete its citations.
*   Run full test suite to ensure no regressions in the `QuestionnaireRunner`.

## 3. Benefits
1.  **Relational Integrity**: Enforces structure on citation data.
2.  **Queryability**: Allows for SQL analysis of source usage (e.g., "Which documents are cited most often?").
3.  **Extensibility**: Makes it easier to add metadata to individual citations in the future.
