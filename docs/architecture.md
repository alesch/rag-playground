## Architecture Design

### Core Components

1. **Document Ingestion Pipeline** - Load and chunk compliance documentation
2. **Embedding & Storage** - Generate embeddings and store in Supabase pgvector
3. **Retrieval System** - Query relevant context using semantic search
4. **LLM Generation** - Generate accurate answers using LangChain
5. **Orchestration** - Coordinate workflow with LangGraph

### Technology Stack

- **Database**: Supabase (PostgreSQL + pgvector extension)
- **Embeddings**: OpenAI text-embedding-3-small (or open-source alternatives)
- **LLM**: OpenAI GPT-4 / GPT-3.5-turbo (or open-source alternatives)
- **Framework**: LangChain + LangGraph
- **Language**: Python 3.11+
- **Development**: Jupyter notebooks for pedagogical exploration
