# Performance Tuning Results

**Goal**: Systematically optimize RAG pipeline parameters
**Test Questionnaire**: test_questionnaire_short (3 questions: Q1.2, Q3.2, Q6.2)
**Ground Truth**: ground_truth_notebooklm_short
**Metric**: Mean Answer Relevancy (semantic similarity, 0.0-1.0)

---

## Baseline

**Run ID**: eval-20260129-154306
**Date**: 2026-01-29

**Configuration**:
- Model: llama3.2
- Temperature: 0.8
- Top-K: 5
- Similarity Threshold: 0.0
- Chunk Size: 800
- Chunk Overlap: 100

**Results**:
- Q1.2: 0.9418
- Q3.2: 0.8851
- Q6.2: 0.8071
- **Mean: 0.8780**

---

## Experiment 1: Retrieval Top-K Optimization

### Test 1.1: top_k=3
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --top-k 3 --name "Exp1.1 - k=3"`

**Results**:
- TBD

### Test 1.2: top_k=7
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --top-k 7 --name "Exp1.2 - k=7"`

**Results**:
- TBD

### Test 1.3: top_k=10
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --top-k 10 --name "Exp1.3 - k=10"`

**Results**:
- TBD

---

## Experiment 2: Similarity Threshold

### Test 2.1: threshold=0.3
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --threshold 0.3 --name "Exp2.1 - threshold=0.3"`

**Results**:
- TBD

### Test 2.2: threshold=0.5
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --threshold 0.5 --name "Exp2.2 - threshold=0.5"`

**Results**:
- TBD

---

## Experiment 3: LLM Temperature

### Test 3.1: temp=0.3 (more deterministic)
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --temp 0.3 --name "Exp3.1 - temp=0.3"`

**Results**:
- TBD

### Test 3.2: temp=1.0 (more creative)
**Command**: `python scripts/run_evaluation.py --questionnaire test_questionnaire_short --temp 1.0 --name "Exp3.2 - temp=1.0"`

**Results**:
- TBD

---

## Summary

**Best Configuration**: TBD

**Improvement over Baseline**: TBD

**Next Steps**: TBD
