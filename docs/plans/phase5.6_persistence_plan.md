# Phase 5.6: Persistence Layer (SQLite Native)

**Goal**: Replace in-memory storage with persistent SQLite storage using native `sqlite3`.

**Constraint**: No ORM (SQLAlchemy) to keep complexity low. No immediate Supabase requirement.

## Architecture

We will implement a `RelationalClient` (or extend `SQLiteClient`) to handle standard relational data, separating it from the Vector data if cleaner, or combining them since they share the same SQLite file (`complaila.db`).

Given we already have `src/infrastructure/database/sqlite_client.py` managing the connection and file, we should extend it or create a companion repository layer.

### Data Schema (SQL)

We will add these tables to `src/infrastructure/database/schema.sql`:

1.  **questionnaires**
    *   `id` TEXT PRIMARY KEY
    *   `name` TEXT
    *   `description` TEXT
    *   `source_file` TEXT
    *   `status` TEXT

2.  **questions**
    *   `id` TEXT PRIMARY KEY
    *   `questionnaire_id` TEXT REFERENCES questionnaires(id)
    *   `question_id` TEXT
    *   `text` TEXT
    *   `section` TEXT
    *   `sequence` INTEGER

3.  **runs**
    *   `id` TEXT PRIMARY KEY
    *   `name` TEXT
    *   `status` TEXT
    *   `created_at` TIMESTAMP
    *   `config_json` TEXT (Store all config fields as JSON to handle schema evolution easily)

4.  **answers**
    *   `id` TEXT PRIMARY KEY
    *   `run_id` TEXT REFERENCES runs(id)
    *   `question_id` TEXT REFERENCES questions(id)
    *   `is_success` BOOLEAN
    *   `answer_text` TEXT
    *   `error_message` TEXT
    *   `citations_json` TEXT
    *   `retrieved_chunks_json` TEXT
    *   `meta_json` TEXT (timings, embedding, etc.)

## Implementation Plan

### Step 1: Database Initialization
*   Update `src/infrastructure/database/schema.sql` (if it exists) or create it.
*   Update `SQLiteClient` in `src/infrastructure/database/sqlite_client.py` to execute this schema on init.

### Step 2: Questionnaire Persistence
*   Refactor `QuestionnaireStore` to take a `db_client` dependency.
*   Implement SQL queries for `save_questionnaire`, `save_questions`, `get_questionnaire`, `get_questions`.
*   Update tests to use `SQLiteClient(":memory:")`.

### Step 3: Run Persistence
*   Refactor `RunStore` to take a `db_client` dependency.
*   Implement SQL queries for `save_run`, `save_answer`, `get_run`, `get_answers`.
    *   *Note*: Will need to serialize/deserialize the JSON fields.
*   Update tests to use `SQLiteClient(":memory:")`.

### Step 4: Verification
*   Run full test suite.