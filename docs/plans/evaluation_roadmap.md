# Phase 6: Evaluation Pipeline Roadmap

Focus: Implement and automate RAG evaluation metrics.

## Test Scenarios

### Metric Calculations

- **Precision@K**:
  - Given: A list of retrieved document IDs and a list of expected document IDs.
  - When: Calculating Precision@K.
  - Then: Return the ratio of relevant documents in the top K.
- **Recall@K**:
  - Given: A list of retrieved document IDs and a list of expected document IDs.
  - When: Calculating Recall@K.
  - Then: Return the ratio of expected documents that were found in the top K.
- **Answer Relevancy**:
  - Given: A generated answer and a ground truth answer.
  - When: Calculating semantic similarity using embeddings.
  - Then: Return a score between 0 and 1.

### Automated Evaluation

- **Execution**:
  - Given: A CSV file with ground truth questions and answers.
  - When: Running the evaluator.
  - Then: Generate a report with metrics for each question and overall averages.

## Implementation Plan

1. **src/evaluation/metrics.py**: Pure functions for calculating metrics.
2. **src/evaluation/evaluator.py**: Component to coordinate running questions through the RAG and computing metrics.
3. **Evaluation CLI/Notebook**: Tools for users to run evaluations.
