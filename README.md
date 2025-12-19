# Complaila RAG Demo

## Overview

**Project Name**: complaila  
**Purpose**: A pedagogical RAG (Retrieval-Augmented Generation) system for answering compliance questionnaires  
**Primary Goal**: Learning and demonstrating RAG concepts with production-grade tools  

### Business Context

**Company**: Acme  
**Product**: finanso (SaaS accounting closing software)  
**Target Customers**: Financial institutions with strict compliance requirements (SOC-2, ISO 27001)  
**Use Case**: Automate responses to customer compliance questionnaires

---

## Architecture Design

### Core Components

1. **Document Ingestion Pipeline** - Load and chunk compliance documentation
2. **Embedding & Storage** - Generate embeddings and store in Supabase pgvector
3. **Retrieval System** - Query relevant context using semantic search
4. **LLM Generation** - Generate accurate answers using LangChain
5. **Orchestration** - Coordinate workflow with LangGraph

### Technology Stack

- **Database**: Supabase (PostgreSQL + pgvector extension)
- **Embeddings**: Ollama mxbai-embed-large (1024 dimensions)
- **LLM**: Ollama llama3.1 (or other local models like mistral, phi3)
- **Framework**: LangChain + LangGraph
- **Language**: Python 3.11+
- **Development**: Jupyter notebooks for pedagogical exploration
- **Local LLM Runtime**: Ollama (free, no API keys required)

## Success Criteria

**Pedagogical Goals**:
- Clear understanding of RAG architecture
- Hands-on experience with vector databases
- Practical knowledge of LangChain/LangGraph
- Ability to evaluate RAG systems

**Technical Goals**:
- Functional end-to-end RAG pipeline
- Accurate answers to compliance questions
- Proper source attribution
- Well-formatted markdown output

**Deliverables**:
- Complete codebase with documentation
- 5 educational Jupyter notebooks
- Demo corpus and sample questionnaire
- Evaluation report with metrics

## Documentation

Detailed documentation is available in the `docs/` folder:

- **architecture.md** - Core components and technology stack overview
- **corpus structure.md** - Demo corpus, facts about the system.
- **db schemas.md** - PostgreSQL/pgvector database schema and metadata structure
- **evaluation metrics.md** - Retrieval and generation quality metrics for RAG system evaluation
- **folder structure.md** - Complete project directory structure and file organization
- **learning path.md** - Jupyter notebook modules covering database setup, ingestion, retrieval, generation, and orchestration
- **project_plan.md** - workflow from setup to refinement
- **sample questions.md** - Test questions covering security, technical, and compliance topics
- **technical concepts.md** - Key RAG concepts including embeddings, chunking strategies, and prompt engineering

## Notes

- This is a **learning project**, not production-ready
- Focus on understanding concepts over optimization
- Experiment with different approaches
- Document what works and what doesn't
- Prioritize code readability and documentation

---

**Last Updated**: 2024-12-19  
**Version**: 1.0
