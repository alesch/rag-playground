## Project Structure

```
complaila/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── corpus/                          # Source compliance documents
│   └── questionnaires/                  # Sample customer questions
├── src/
│   ├── __init__.py
│   ├── config.py                        # Configuration management
│   ├── domain/
│   │   ├── models.py                    # Domain entities (Question, Answer, etc.)
│   │   └── stores/                      # Persistence for domain entities
│   │       ├── questionnaire_store.py
│   │       ├── run_store.py
│   │       └── evaluation_store.py
│   ├── infrastructure/
│   │   └── database/                    # DB clients (SQLite, Supabase)
│   │       ├── sqlite_client.py
│   │       ├── supabase_client.py
│   │       └── factory.py
│   ├── rag/                             # RAG core components
│   │   ├── rag_system.py                # Main RAG answering logic
│   │   ├── retriever.py                 # Vector retrieval logic
│   │   └── ingestion/                   # Data processing pipeline
│   │       ├── document_loader.py
│   │       ├── chunker.py
│   │       └── embedder.py
│   ├── application/                     # Coordination and higher-level logic
│   │   ├── orchestration/               # Workflow management (Orchestrator)
│   │   ├── runners/                     # Specialized execution flows
│   │   └── evaluation/                  # RAG evaluation metrics and logic
│   ├── experiments/                     # Research and performance tuning
│   │   └── run_experiments.py
│   └── utils/                           # Shared utilities
│       └── cli.py
├── scripts/                             # CLI entry points
│   ├── ask.py                          # Question answering CLI
│   ├── tuning.py                       # Performance tuning (runs experiments)
│   ├── run_evaluation.py               # Evaluation runner
│   ├── ingest_corpus.py                # Data loading script
│   └── ...                             # Other specialized scripts
└── tests/                               # Test suite
```
