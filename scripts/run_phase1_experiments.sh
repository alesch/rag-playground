#!/bin/bash
# Run Phase 1 Performance Tuning Experiments
# Tests retrieval parameters and temperature variations

set -e  # Exit on error

QUESTIONNAIRE="test_questionnaire_short"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  PHASE 1 PERFORMANCE TUNING EXPERIMENTS"
echo "=========================================="
echo "Questionnaire: $QUESTIONNAIRE"
echo "Total experiments: 6"
echo "Estimated time: 6-8 minutes"
echo "=========================================="
echo ""

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Experiment Set 1: Top-K Variations
echo "[1/6] Running Exp1.1: top_k=3..."
python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire "$QUESTIONNAIRE" \
    --top-k 3 \
    --name "Exp1.1 - k=3"
echo ""

echo "[2/6] Running Exp1.2: top_k=7..."
python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire "$QUESTIONNAIRE" \
    --top-k 7 \
    --name "Exp1.2 - k=7"
echo ""

echo "[3/6] Running Exp1.3: top_k=10..."
python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire "$QUESTIONNAIRE" \
    --top-k 10 \
    --name "Exp1.3 - k=10"
echo ""

# Experiment Set 2: Similarity Threshold
echo "[4/6] Running Exp2.1: threshold=0.3..."
python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire "$QUESTIONNAIRE" \
    --threshold 0.3 \
    --name "Exp2.1 - threshold=0.3"
echo ""

echo "[5/6] Running Exp2.2: threshold=0.5..."
python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire "$QUESTIONNAIRE" \
    --threshold 0.5 \
    --name "Exp2.2 - threshold=0.5"
echo ""

# Experiment Set 3: Temperature
echo "[6/6] Running Exp3.1: temp=0.3..."
python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire "$QUESTIONNAIRE" \
    --temp 0.3 \
    --name "Exp3.1 - temp=0.3"
echo ""

# Note: Skipping temp=1.0 experiment as higher temperature tends to decrease accuracy
# If needed, uncomment below:
# echo "[7/7] Running Exp3.2: temp=1.0..."
# python "$SCRIPT_DIR/run_evaluation.py" \
#     --questionnaire "$QUESTIONNAIRE" \
#     --temp 1.0 \
#     --name "Exp3.2 - temp=1.0"
# echo ""

echo "=========================================="
echo "  ALL EXPERIMENTS COMPLETE!"
echo "=========================================="
echo ""
echo "View results with:"
echo "  python scripts/compare_runs.py"
echo ""
