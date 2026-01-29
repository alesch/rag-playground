# Performance Tuning Roadmap

**Goal**: Systematically optimize RAG pipeline performance using data-driven experimentation

**Reference**: Phase 6 Component 3 in progress.md

---

## Current Baseline

**Configuration** (from config.py and run_evaluation.py):
- Chunk size: 800 tokens (~4000 chars)
- Chunk overlap: 100 tokens (~200 chars)
- Retrieval top_k: 5
- Similarity threshold: 0.0
- LLM: llama3.2, temperature: 0.8
- Embeddings: mxbai-embed-large (1024 dims)

**Metrics**:
- Need baseline evaluation run first
- Tracking: Answer Relevancy (semantic similarity to ground truth)

---

## Optimization Strategy

### 1. Establish Baseline Performance

**Actions**:
- Run evaluation with current default parameters
- Document baseline metrics (mean answer relevancy)
- Save baseline run ID for comparison

**Why**: Need objective baseline before making changes

---

### 2. Optimize Retrieval Parameters

**Hypothesis**: Retrieval quality directly impacts answer quality

**Parameters to tune**:
- `top_k`: Number of chunks retrieved (currently 5)
  - Test values: 3, 5, 7, 10
  - Trade-off: More context vs noise
- `similarity_threshold`: Minimum similarity score (currently 0.0)
  - Test values: 0.0, 0.3, 0.5, 0.7
  - Trade-off: Precision vs recall

**Test Approach**:
- Grid search: test combinations systematically
- Compare answer relevancy scores
- Track retrieval metrics (if available)

---

### 3. Optimize Chunking Strategy

**Hypothesis**: Chunk size/overlap affects retrieval precision and context quality

**Parameters to tune**:
- `chunk_size`: Target tokens per chunk (currently 800)
  - Test values: 500, 800, 1000, 1500
  - Smaller chunks: more precise retrieval, less context
  - Larger chunks: more context, less precise matching
- `chunk_overlap`: Overlap between chunks (currently 100)
  - Test values: 50, 100, 200
  - More overlap: better context continuity, more redundancy

**Test Approach**:
- Re-ingest corpus with different chunk parameters
- Run evaluation for each configuration
- Compare answer quality and retrieval precision

**Note**: Requires re-ingestion, so test after retrieval param optimization

---

### 4. Optimize LLM Prompts

**Hypothesis**: Prompt engineering improves answer quality and format

**Current prompt** (from generator.py):
```
You are a compliance assistant. Answer the question using ONLY the provided context.
If the answer cannot be found in the context, say "I cannot find this information in the documentation."

Context:
[numbered chunks]

Question: {query}

Answer:
```

**Areas to improve**:
- Add explicit instruction for conciseness
- Emphasize accuracy over completeness
- Guide citation usage (if needed)
- Test different system/assistant role descriptions

**Test Approach**:
- Modify prompt templates in generator.py
- Run evaluation for each variant
- Compare answer relevancy and qualitative review

---

### 5. Test Different LLM Models

**Hypothesis**: Model choice affects answer quality

**Available models** (via Ollama):
- llama3.2 (current)
- mistral
- phi3
- deepseek (if available on system)

**Parameters**:
- temperature: 0.8 (current) vs 0.3 (more deterministic) vs 1.0 (more creative)

**Test Approach**:
- Run evaluation with different model/temperature combos
- Compare answer relevancy
- Consider speed/resource trade-offs

---

## Implementation Notes

### Testing Framework
- Use `run_evaluation.py` with command-line arguments
- Store all runs in database for comparison
- Track run metadata: config parameters, timestamp, metrics

### Evaluation Criteria
- **Primary**: Mean answer relevancy (semantic similarity to ground truth)
- **Secondary**: Manual review of answer quality
- **Tertiary**: Execution time, resource usage

### Parameter Tracking
All tuning parameters are stored in `RunConfig`:
- llm_model, llm_temperature
- retrieval_top_k, similarity_threshold
- chunk_size, chunk_overlap
- embedding_model, embedding_dimensions

### Experimentation Workflow
1. Modify parameters (config.py or CLI args)
2. Re-ingest if chunking changes (scripts/ingest.py)
3. Run evaluation (scripts/run_evaluation.py)
4. Record results in tracking spreadsheet or notes
5. Identify best configuration
6. Update config.py defaults

---

## Success Criteria

- [ ] Baseline metrics established
- [ ] At least 3 retrieval parameter combinations tested
- [ ] At least 2 chunking strategies tested
- [ ] At least 2 prompt variants tested
- [ ] Best configuration identified and documented
- [ ] Mean answer relevancy improved by >10% (aspirational)
- [ ] Config.py updated with optimized defaults

---

## Next Steps

1. Run baseline evaluation
2. Start with retrieval parameter tuning (fastest, no re-ingestion)
3. Progress to chunking optimization (requires re-ingestion)
4. Fine-tune prompts and LLM settings
5. Document findings in evaluation report
