# Orchestration Component Roadmap

**Component**: Orchestrator
**Module**: `src/orchestration/orchestrator.py`
**Test File**: `tests/test_orchestrator.py`
**Status**: Planning

---

## Overview

Build a LangGraph-based orchestrator that coordinates the RAG pipeline:
- **Input**: Question(s) from compliance questionnaires
- **Process**: Retrieve relevant chunks → Generate answer with citations
- **Output**: Formatted answers with source attribution

## Component Interfaces

### Retriever (existing)
```python
retriever.search(query: str, top_k: int = 5) -> List[SearchResult]
```

### Generator (existing)
```python
generator.generate(query: str, top_k: int = 5) -> GeneratedAnswer
```

### Orchestrator (to build)
```python
orchestrator.answer(question: str) -> GeneratedAnswer
orchestrator.process_questionnaire(questions: List[str]) -> List[GeneratedAnswer]
```

---

## Test Scenarios

### Test 1: Answer single question end-to-end
**Given** an orchestrator with retriever and generator
**When** `answer("What authentication methods does finanso support?")` is called
**Then** returns a `GeneratedAnswer` with answer text and citations

### Test 2: Process multiple questions as batch
**Given** an orchestrator and a list of 3 questions
**When** `process_questionnaire(questions)` is called
**Then** returns a list of 3 `GeneratedAnswer` objects in order

### Test 3: Handle retrieval with no results
**Given** an orchestrator with a retriever that returns empty results
**When** `answer("Unknown topic question")` is called
**Then** returns graceful "not found" response without LLM call

### Test 4: Handle LLM failure gracefully
**Given** an orchestrator with an LLM that raises an exception
**When** `answer(question)` is called
**Then** raises appropriate error or returns error response

### Test 5: State flows correctly through LangGraph nodes
**Given** a LangGraph workflow with retrieve and generate nodes
**When** a question is processed
**Then** state contains retrieved chunks before generation node executes

---

## LangGraph Architecture

### State Definition
```python
class RAGState(TypedDict):
    question: str
    retrieved_chunks: List[SearchResult]
    answer: Optional[GeneratedAnswer]
    error: Optional[str]
```

### Nodes
1. **retrieve_node**: Calls `retriever.search(state["question"])`
2. **generate_node**: Calls `generator.generate()` with retrieved context

### Graph Flow
```
START → retrieve_node → generate_node → END
```

### Future Extensions (Phase 6)
- Conditional routing for answer refinement
- Multi-step reasoning for complex questions
- Retry logic for transient failures

---

## Implementation Notes

- Generator already handles empty retrieval results internally
- Tests should use existing mock fixtures (`mock_supabase_client`, `mock_llm`)
- Keep orchestrator thin - delegate logic to existing components
- Focus on state management and error handling

---

## Dependencies

- Retriever: `src/retrieval/retriever.py` (complete)
- Generator: `src/generation/generator.py` (complete)
- LangGraph: `langgraph>=0.2.0` (installed)

---

## Test Order (TDD Sequence)

1. Test 1 - Basic single question flow (happy path)
2. Test 3 - Empty retrieval handling (edge case)
3. Test 4 - LLM failure handling (error case)
4. Test 2 - Batch processing (feature extension)
5. Test 5 - LangGraph state verification (integration)
