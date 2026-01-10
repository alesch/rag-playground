## Architecture Design

### Core Components

1. **Document Ingestion Pipeline** - Load and chunk compliance documentation
2. **Embedding & Storage** - Generate embeddings and store in SQLite (local) or Supabase (cloud)
3. **Retrieval System** - Query relevant context using semantic search
4. **LLM Generation** - Generate accurate answers using LangChain
5. **Orchestration** - Coordinate workflow with LangGraph

### Technology Stack

- **Database**: SQLite (default) or Supabase (PostgreSQL + pgvector extension)
- **Embeddings**: Ollama mxbai-embed-large (1024 dimensions)
- **LLM**: Ollama llama3.1 (or other local models like mistral, phi3)
- **Framework**: LangChain + LangGraph
- **Language**: Python 3.11+
- **Development**: Jupyter notebooks for pedagogical exploration
- **Local LLM Runtime**: Ollama (free, no API keys required)
