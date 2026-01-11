# Phase 5.6: Persistence Layer

**Goal**: Replace in-memory storage with a relational database (SQLite initially, switchable to Supabase/Postgres).

**Technology**: SQLAlchemy (ORM)

## Architecture

We will implement the **Repository Pattern** implicitly by upgrading the existing Store classes.
The `RunStore` and `QuestionnaireStore` will no longer hold `dict`s; they will execute SQL queries via SQLAlchemy.

### Data Models (SQLAlchemy)

We will define these in `src/database/schema.py`.

1.  **Questionnaires Table**
    *   `id` (PK, String)
    *   `name`
    *   `description`
    *   `source_file`
    *   `status`

2.  **Questions Table**
    *   `id` (PK, String) - e.g., "ikea:Q1.1"
    *   `questionnaire_id` (FK -> Questionnaires)
    *   `question_id` (String) - e.g., "Q1.1"
    *   `text`
    *   `section`
    *   `sequence` (Int)

3.  **Runs Table**
    *   `id` (PK, String)
    *   `name`
    *   `description`
    *   `status`
    *   `created_at`
    *   **Config Fields**: `llm_model`, `llm_temperature`, `chunk_size`, etc.

4.  **Answers Table**
    *   `id` (PK, String)
    *   `run_id` (FK -> Runs)
    *   `question_id` (FK -> Questions)
    *   `status` (Enum: SUCCESS, FAILURE)
    *   `answer_text` (Text, nullable)
    *   `error_message` (Text, nullable)
    *   `citations` (JSON/JSONB) - Snapshot of citations
    *   `retrieved_chunks` (JSON/JSONB) - Snapshot of chunks
    *   `metrics` (JSON/JSONB) - embedding, generation_time

## Implementation Plan

### Step 1: Dependencies & Configuration
*   Add `sqlalchemy` to `requirements.txt`.
*   Update `src/config.py` to include `DATABASE_URL` (default: `sqlite:///complaila.db`).
*   Create `src/database/session.py` for engine and session handling.

### Step 2: Schema Definition (TDD)
*   Create `tests/test_schema.py`.
*   Implement `src/database/schema.py`.
*   Verify tables are created in SQLite.

### Step 3: Refactor QuestionnaireStore
*   Update `src/domain/questionnaire_store.py`.
*   Inject SessionFactory or use a global session manager.
*   Update `tests/test_questionnaire_store.py` to use `sqlite:///:memory:` for isolation.

### Step 4: Refactor RunStore
*   Update `src/domain/run_store.py`.
*   Map `AnswerSuccess` and `AnswerFailure` to/from the `Answers` table rows.
*   Update `tests/test_run_store.py` to use `sqlite:///:memory:`.

### Step 5: Integration
*   Verify `QuestionnaireRunner` still works (it uses the stores, so it should be agnostic).
*   Run full suite.

## Supabase Support
*   Since Supabase provides a Postgres connection string, we just need to change `DATABASE_URL` in `.env` to point to Supabase.
*   We will assume `psycopg2` or `asyncpg` might be needed later for Postgres, but `sqlalchemy` handles the abstraction.
