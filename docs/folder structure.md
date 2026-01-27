## Project Structure

```
complaila/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   ├── corpus/                          # Source compliance documents
│   │   ├── 01_technical_infrastructure.md
│   │   ├── 02_soc2_documentation.md
│   │   ├── 03_iso27001_documentation.md
│   │   └── 04_operational_procedures.md
│   └── questionnaires/                  # Sample customer questions
│       └── sample_questionnaire.md
├── src/
│   ├── __init__.py
│   ├── config.py                        # Configuration management
│   ├── database/
│   │   ├── __init__.py
│   │   ├── supabase_client.py          # Supabase connection & operations
│   │   └── schema.sql                   # pgvector table schema
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── document_loader.py          # Load markdown documents
│   │   ├── chunker.py                  # Text chunking strategies
│   │   └── embedder.py                 # Generate embeddings
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── vector_search.py            # Semantic search operations
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── prompts.py                  # Prompt templates
│   │   └── answer_generator.py         # LLM generation logic
│   └── orchestration/
│       ├── __init__.py
│       └── rag_graph.py                # LangGraph workflow
├── notebooks/
│   ├── 01_setup_database.ipynb
│   ├── 02_ingest_documents.ipynb
│   ├── 03_test_retrieval.ipynb
│   ├── 04_generate_answers.ipynb
│   └── 05_full_pipeline.ipynb
├── scripts/
│   ├── ask.py                          # Simple CLI for querying the RAG system
│   ├── ingest_corpus.py                # Ingest all documents into the vector store
│   ├── ingest_questionnaire.py         # Ingest a questionnaire for processing
│   ├── run_evaluation.py               # Run RAG evaluation metrics
│   ├── import_ground_truth.py          # Import ground truth data for evaluation
│   └── entrypoint.sh                   # Docker entrypoint (starts Ollama)
└── tests/
    ├── __init__.py
    ├── test_chunker.py
    ├── test_retrieval.py
    └── test_generation.py
```
