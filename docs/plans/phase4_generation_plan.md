# Phase 4: Generation Plan

## Goal
Implement answer generation using retrieved chunks and LLM (Ollama llama3.1).

## Architecture
Create a `Generator` class that:
- Takes a query and retrieved chunks
- Formats a prompt with context
- Calls LLM for answer generation
- Returns answer with citations

## Components

### 1. Generator Module
**Location**: `src/generation/generator.py`

Responsibilities:
- Coordinate retrieval and LLM calls
- Format prompts with context
- Parse responses and extract citations

### 2. Prompt Templates
**Location**: `src/generation/prompts.py`

Simple prompt template for compliance Q&A.

## TDD Test Plan

| Test | Description | Status |
|------|-------------|--------|
| 1 | Generate answer from retrieved chunks | |
| 2 | Answer includes citations to source chunks | |
| 3 | Handle empty retrieval results gracefully | |
| 4 | Prompt includes all retrieved context | |

## Test Strategy
- Mock LLM responses (return fixed strings)
- Mock retriever (use MockSupabaseClient)
- Tests verify prompt formatting and citation extraction
- NOT testing LLM quality (external dependency)

## Files to Create/Modify

- `src/generation/__init__.py` - new
- `src/generation/generator.py` - new
- `src/generation/prompts.py` - new
- `tests/test_generator.py` - new
