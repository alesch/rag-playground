-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create compliance_documents table
CREATE TABLE IF NOT EXISTS compliance_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id TEXT NOT NULL,              -- Logical document identifier
    chunk_id TEXT NOT NULL,                 -- Unique chunk identifier
    content TEXT NOT NULL,                  -- Chunk text content
    embedding vector(1024),                 -- Ollama mxbai-embed-large dimension
    metadata JSONB,                         -- Flexible metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(document_id, chunk_id)
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS compliance_documents_embedding_idx 
ON compliance_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create indexes for metadata filtering
CREATE INDEX IF NOT EXISTS idx_document_id ON compliance_documents(document_id);
CREATE INDEX IF NOT EXISTS idx_metadata ON compliance_documents USING gin(metadata);
