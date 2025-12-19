## Key Technical Concepts

### 1. RAG Fundamentals

**What is RAG?**
Retrieval-Augmented Generation combines information retrieval with language generation. Instead of relying solely on the LLM's parametric knowledge, RAG retrieves relevant context from a knowledge base.

**RAG Pipeline**:
1. Query → Embed query
2. Retrieve → Find similar vectors
3. Augment → Add context to prompt
4. Generate → LLM produces answer

### 2. Vector Embeddings

**Purpose**: Convert text into numerical vectors that capture semantic meaning

**Key Properties**:
- Similar text → Similar vectors (closer in vector space)
- Enables semantic search beyond keyword matching
- Dimension typically 384-1536 (depends on model)
- **This project uses**: Ollama mxbai-embed-large (1024 dimensions)

### 3. Chunking Strategies

**Fixed-Size Chunking**:
- Split by token/character count
- Simple but may break semantic boundaries
- Good for: uniform content

**Semantic Chunking**:
- Split by paragraphs, sections, or semantic breaks
- Preserves context
- Good for: structured documents like markdown

**Recommended Approach**: Markdown-aware chunking (split by headers, preserve structure)

### 4. Similarity Search

**Metrics**:
- **Cosine Similarity**: Measures angle between vectors (common choice)
- **L2 Distance**: Euclidean distance
- **Inner Product**: Dot product similarity

**Indexing**:
- **IVFFlat**: Approximate nearest neighbor, faster but less accurate
- **HNSW**: Hierarchical navigable small world, more accurate but slower

### 5. Prompt Engineering for RAG

**Template Structure**:
```
System: You are a compliance expert answering questionnaires.

Context: {retrieved_chunks}

Question: {user_question}

Instructions:
- Answer based on the provided context
- Cite specific sources
- If information is not in context, say so
- Use formal, professional tone
- Format response in markdown
```
