# RAG Evaluation Metrics

This document explains the metrics used to evaluate the Complaila RAG system.

## Retrieval Metrics

These metrics evaluate the performance of the vector search and retrieval component.

### 1. Precision @ K

**"Of the top K documents I retrieved, how many are actually useful?"**

* **Focus**: Quality and noise reduction.
* **Why it matters**: If `top_k=5` and only 1 document is relevant, your LLM prompt is 80% full of "noise." This can confuse the model or cause it to exceed its context window with irrelevant data.
* **Formula**: `(Relevant Documents in Top K) / K`
* **Example**: You ask "What is your MFA policy?". The system retrieves 5 chunks. 2 are about MFA, 3 are about the office cafeteria. **Precision@5 = 2/5 (0.4)**.

### 2. Recall @ K

**"Out of all the relevant documents that exist in the database, how many did I manage to find in my top K?"**

* **Focus**: Completeness.
* **Why it matters**: If there are 3 different documents that together explain the "MFA policy," and you only found 1, the LLM might give an incomplete or partially incorrect answer.
* **Formula**: `(Relevant Documents in Top K) / (Total Relevant Documents in Database)`
* **Example**: There are 3 chunks in your database that mention MFA. Your search finds 2 of them. **Recall = 2/3 (0.66)**.

### 3. MRR (Mean Reciprocal Rank)

**"How high up in the list is the *first* relevant document?"**

* **Focus**: Ranking effectiveness.
* **Why it matters**: Most RAG systems prioritize the first few documents. MRR tells you if your vector search is successfully putting the "best" answer at the very top.
* **Formula**: `1 / (Rank of first relevant document)`
* **Example**:
  * If the 1st document is relevant: `1/1 = 1.0` (Perfect)
  * If the 1st is wrong, but the 2nd is relevant: `1/2 = 0.5`
  * If the 1st and 2nd are wrong, but the 3rd is relevant: `1/3 = 0.33`

---

## Generation Metrics

These metrics evaluate the final answer produced by the LLM.

### Answer Relevancy

**"Does the generated answer actually address the user's question with correct information?"**

* **Focus**: Accuracy and Semantic Similarity.
* **Implementation**: Evaluated by comparing the generated answer against a "ground truth" using semantic similarity (embeddings) or an LLM judge.
* **Why it matters**: A system can have perfect retrieval but still fail if the LLM hallucinates or fails to synthesize the retrieved information correctly.

---

## Summary Table

| Metric | Goal | High Score Means... |
| :--- | :--- | :--- |
| **Precision** | Minimize Noise | The LLM isn't reading junk. |
| **Recall** | Maximize Knowledge | The LLM has all the facts it needs. |
| **MRR** | Optimize Ranking | The most relevant fact is at the top. |
| **Answer Relevancy** | Semantic Accuracy | The answer is factually correct and relevant to the user's query. |
