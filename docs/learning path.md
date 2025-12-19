## Learning Modules (Jupyter Notebooks)

### Module 1: Database Setup (`01_setup_database.ipynb`)

**Learning Objectives**:
- Set up Supabase project
- Enable pgvector extension
- Create tables with proper schema
- Understand vector similarity search (cosine, L2, inner product)

**Topics Covered**:
- PostgreSQL vector operations
- Indexing strategies (IVFFlat, HNSW)
- Schema design for RAG systems

### Module 2: Document Ingestion (`02_ingest_documents.ipynb`)

**Learning Objectives**:
- Load markdown documents
- Implement chunking strategies (semantic vs fixed-size)
- Generate embeddings using OpenAI API
- Store vectors in pgvector with metadata

**Topics Covered**:
- Text chunking best practices
- Embedding models comparison
- Metadata design for filtering
- Batch processing strategies

### Module 3: Retrieval Testing (`03_test_retrieval.ipynb`)

**Learning Objectives**:
- Implement similarity search queries
- Test different retrieval strategies
- Compare embedding models
- Evaluate retrieval quality (precision, recall)

**Topics Covered**:
- Semantic search vs keyword search
- Hybrid retrieval approaches
- Re-ranking strategies
- Retrieval evaluation metrics

### Module 4: Answer Generation (`04_generate_answers.ipynb`)

**Learning Objectives**:
- Design prompt templates for compliance Q&A
- Implement RAG pattern with LangChain
- Handle context window limitations
- Format markdown responses

**Topics Covered**:
- Prompt engineering for accuracy
- Context stuffing vs refinement
- Citation and source attribution
- Markdown formatting in LLM output

### Module 5: LangGraph Orchestration (`05_full_pipeline.ipynb`)

**Learning Objectives**:
- Build stateful workflow with LangGraph
- Handle multi-step reasoning
- Implement answer refinement loops
- Process full questionnaires end-to-end

**Topics Covered**:
- LangGraph state management
- Conditional edges and routing
- Error handling and retries
- Batch processing questionnaires
