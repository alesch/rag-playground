# Code Reorganization Plan

## Goal
Reorganize codebase into clear concentric circles based on dependencies, from innermost (domain) to outermost (experiments).

## Current Problems
- Modules scattered across unclear boundaries
- Domain logic mixed with infrastructure
- RAG components spread across multiple directories
- Unclear dependency flow

## Proposed Structure

### Layer 1: Domain (Innermost - Pure Business Logic)
**Location:** `src/domain/`
- `models.py` - Questionnaire, Question, Answer, Citation, RunConfig (no changes)
- `stores/questionnaire_store.py` - Move from `domain/questionnaire_store.py`
- `stores/run_store.py` - Move from `domain/run_store.py`
- `stores/evaluation_store.py` - Move from `evaluation/evaluation_store.py`

**Rule:** Domain has ZERO dependencies on outer layers. Only depends on database interfaces.

### Layer 2: Infrastructure (Database)
**Location:** `src/infrastructure/database/`
- Move entire `database/` folder here
- `base.py`, `sqlite_client.py`, `supabase_client.py`, `factory.py`

**Rule:** Pure infrastructure. No business logic.

### Layer 3: RAG System
**Location:** `src/rag/`
- `rag_system.py` - Move from `generation/rag_system.py`
- `retriever.py` - Move from `retrieval/retriever.py`
- `ingestion/` - Move entire folder from `ingestion/`
  - `chunker.py`
  - `document_loader.py`
  - `embedder.py`

**Rule:** RAG components grouped together. Depends on domain models + infrastructure.

### Layer 4: Application (Orchestration + Evaluation)
**Location:** `src/application/`
- `orchestration/orchestrator.py` - Move from `orchestration/orchestrator.py`
- `runners/questionnaire_runner.py` - Move from `domain/questionnaire_runner.py`
- `evaluation/` - Move from `evaluation/`
  - `evaluator.py`
  - `metrics.py`

**Rule:** Coordinates domain + RAG. No experiments.

### Layer 5: Experiments (Outermost)
**Location:** `src/experiments/` (or keep in `scripts/`)
- `run_experiments.py` - Move from `scripts/run_experiments.py`

**Rule:** Uses everything. Top-level use case.

### Utilities & Config
**Location:** Keep at `src/` root
- `config.py`
- `utils/`

## Migration Steps

### Step 1: Create New Directory Structure
- Create `src/infrastructure/database/`
- Create `src/rag/ingestion/`
- Create `src/domain/stores/`
- Create `src/application/orchestration/`
- Create `src/application/runners/`
- Create `src/application/evaluation/`
- Create `src/experiments/` (optional)

### Step 2: Move Files (Git mv)
- Move database files to `infrastructure/database/`
- Move RAG components to `rag/`
- Move stores to `domain/stores/`
- Move orchestration to `application/orchestration/`
- Move evaluation to `application/evaluation/`
- Move questionnaire_runner to `application/runners/`

### Step 3: Update All Imports
- Update import statements in all files
- Update test imports
- Update scripts imports

### Step 4: Run Tests
- Verify all 87 tests still pass
- Fix any broken imports

### Step 5: Clean Up
- Delete empty old directories
- Update documentation
- Commit changes

## Alternative: Minimal Reorganization

If full reorganization is too disruptive, consider minimal changes:
1. Move stores to `domain/stores/`
2. Merge `generation/` and `retrieval/` into `rag/`
3. Rename `orchestration/` to `application/`
4. Keep everything else as-is

## Decision Points

1. **Should experiments stay in scripts/ or move to src/experiments/?**
   - Pro scripts: Clear separation of runnable scripts
   - Pro src/experiments: Everything in src, clearer architecture

2. **Should we rename folders or keep current names?**
   - Current: database, domain, generation, retrieval, orchestration, evaluation
   - Proposed: infrastructure, domain, rag, application

3. **How aggressively should we reorganize?**
   - Option A: Full reorganization (this plan)
   - Option B: Minimal (just group related modules)
   - Option C: Defer until after performance tuning complete

## Risks

- Breaking imports across entire codebase
- Time-consuming to update all references
- May introduce bugs if not careful
- Interrupts current TDD work on ExperimentRunner

## Recommendation

**Defer until after Phase 6 Component 3 (Performance Tuning) is complete.**

Reason:
- Currently mid-TDD on ExperimentRunner
- Have working experiments to run tonight
- Reorganization is large, risky change
- Better to complete current feature first, then refactor

After experiments complete:
- Do minimal reorganization (Option B)
- Group rag/, move stores/, rename orchestration/
- Keep impact small and focused
