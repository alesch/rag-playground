# Scripts Directory

This directory contains various utility scripts for interacting with the Complaila RAG system, managing data, and running evaluations.

## 🛠 Core Scripts

### `run_evaluation.py`

The primary script for automated testing. It runs a full questionnaire through the RAG pipeline, persists the results to the database, and compares them against the established ground truth.

**Usage:**

```bash
python scripts/run_evaluation.py --model llama3.2 --top-k 5
```

- `--model`: (Optional) The Ollama model to use.
- `--name`: (Optional) A custom name for the run.
- `--top-k`: (Optional) Number of chunks to retrieve.

---

### `ask.py`

An interactive CLI for manual testing and exploration. Allows for single questions or processing a questionnaire without database persistence.

**Usage:**

```bash
python scripts/ask.py "What is the encryption policy?"
python scripts/ask.py  # Enters interactive mode
```

*Note: This script does NOT save answers to the database.*

---

### `ingest_corpus.py`

Processes raw documents in the `data/corpus` directory and stores their embeddings in the vector database.

**Usage:**

```bash
python scripts/ingest_corpus.py
```

---

## 🏗 Data Management & Setup

### `import_ground_truth.py`

Parses external reference answers (e.g., from NotebookLM) in `tests/output-notebookLM.md` and imports them into the database as a "Ground Truth" run. This also ensures the `questions` and `questionnaires` tables are populated.

**Usage:**

```bash
python scripts/import_ground_truth.py
```

### `ingest_questionnaire.py`

Imports a markdown questionnaire into the database, preserving section titles and question ordering.

**Usage:**

```bash
python scripts/ingest_questionnaire.py data/questionnaires/sample_questionnaire.md
```

---

### `reset_evaluation_data.py`

A utility script to "hard reset" evaluation data in the database. Use this to delete questionnaires and runs if you need to perform a clean re-import.

**Usage:**

```bash
python scripts/reset_evaluation_data.py
```
