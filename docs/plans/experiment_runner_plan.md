# Experiment Runner Plan

**Goal**: Testable Python code for overnight experiments

**Why**: 3-question test showed +10.7% but full questionnaire showed -1.47%. Need to validate orchestration before 8-hour overnight runs.

---

## Architecture

### `src/experiments/run_experiments.py`

**ExperimentRunner**
- Takes: questionnaire_id, ground_truth_run_id, **orchestrator**, db_client
- Uses existing `RunConfig` domain model (no new ExperimentConfig needed)
- `run_experiment(config)` → returns (run_id, metrics)
- `run_experiments(configs, trials_per_config)` → returns dict of results

**Key Design**: Pass orchestrator directly (real or mock), following existing `QuestionnaireRunner` pattern

---

## Tests: What We Will Test

### `tests/test_experiment_runner.py`

**Test 1: Happy path**
- Mock orchestrator returns 50 fake answers
- Run single experiment
- Verify: returns run_id and metrics dict

**Test 2: Partial completion**
- Mock completes only 49/50 questions
- Verify: evaluation succeeds with 49 questions

**Test 3: Mid-questionnaire failure**
- Mock fails on question 25
- Verify: saves 24 answers, evaluates partial results

**Test 4: Multiple experiments, one fails**
- 3 configs, #2 fails
- Verify: #1 and #3 complete, #2 recorded as failed

**Test 5: Multiple trials**
- 2 configs × 3 trials
- Verify: returns 6 results

**Test 6: Persistence**
- Mock database
- Verify: save_run(), save_answer(), save_report() called

---

## Revised Configurations

**Baseline wins** (temp=0.8, thresh=0.0 beats temp=0.3, thresh=0.3)

Strategy: Small variations around baseline

1. Baseline - temp=0.8, k=5, thresh=0.0
2. Temp 0.6 - temp=0.6, k=5, thresh=0.0  
3. Temp 0.5 - temp=0.5, k=5, thresh=0.0
4. Threshold 0.1 - temp=0.8, k=5, thresh=0.1
5. Threshold 0.2 - temp=0.8, k=5, thresh=0.2
6. Top-K 7 - temp=0.8, k=7, thresh=0.0
7. Top-K 10 - temp=0.8, k=10, thresh=0.0

**Overnight**: 7 configs × 3 trials = 21 experiments (~8 hours)

---

## Implementation Decisions

1. **Database**: Use `:memory:` SQLite (matches existing QuestionnaireRunner tests)
2. **Configuration**: Test these 7 configs (sufficient for initial analysis)
3. **Error handling**: Retry up to 3 times per question on failure
4. **Trials**: 3 trials per config (21 total experiments)
