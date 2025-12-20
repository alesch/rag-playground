## Database Schema

### Table: `document_chunks`

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT NOT NULL,              -- Logical document identifier
    chunk_id TEXT NOT NULL,                 -- Unique chunk identifier
    revision INTEGER NOT NULL,              -- Document revision number
    status TEXT NOT NULL DEFAULT 'active',  -- Status: 'active', 'superseded', 'archived'
    content TEXT NOT NULL,                  -- Chunk text content
    embedding vector(1024),                 -- Ollama mxbai-embed-large dimension
    metadata JSONB,                         -- Flexible metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(document_id, chunk_id, revision)
);

-- Create index for vector similarity search
CREATE INDEX ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create indexes for metadata filtering
CREATE INDEX idx_document_id ON document_chunks(document_id);
CREATE INDEX idx_metadata ON document_chunks USING gin(metadata);
```

### Metadata Schema

```json
{
    "source_file": "01_technical_infrastructure.md",
    "document_type": "technical",
    "section": "Security Controls",
    "subsection": "Authentication",
    "tags": ["security", "authentication", "mfa"],
    "last_updated": "2024-01-15",
    "chunk_index": 0,
    "total_chunks": 5,
    "revision_note": "Added MFA implementation details"
}
```
