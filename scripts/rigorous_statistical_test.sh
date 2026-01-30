#!/bin/bash
# Option 2: Rigorous Statistical Testing
# Multiple trials of baseline and optimized configs on full questionnaire
# Estimated time: 1-2 hours
# Run overnight or when you can leave laptop unattended

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/rigorous_test_$(date +%Y%m%d_%H%M%S).log"

# Configuration
NUM_TRIALS=3  # Number of trials per configuration
QUESTIONNAIRE="sample_questionnaire"

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "  OPTION 2: RIGOROUS STATISTICAL TESTING"
log "=========================================="
log "Questionnaire: $QUESTIONNAIRE (50 questions)"
log "Trials per config: $NUM_TRIALS"
log "Total runs: $((NUM_TRIALS * 2)) (${NUM_TRIALS}x baseline + ${NUM_TRIALS}x optimized)"
log "Estimated time: 1-2 hours"
log "Log file: $LOG_FILE"
log "Started at: $(date +'%Y-%m-%d %H:%M:%S')"
log "=========================================="
log ""

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Run baseline trials
log "PHASE 1: BASELINE CONFIGURATION TRIALS"
log "Config: temp=0.8, top_k=5, threshold=0.0"
log "=========================================="
for i in $(seq 1 $NUM_TRIALS); do
    log ""
    log ">>> Baseline Trial $i/$NUM_TRIALS <<<"
    log "Started at: $(date +'%H:%M:%S')"
    
    time python -u "$SCRIPT_DIR/run_evaluation.py" \
        --questionnaire "$QUESTIONNAIRE" \
        --temp 0.8 \
        --threshold 0.0 \
        --top-k 5 \
        --name "Statistical - Baseline Trial $i" \
        2>&1 | tee -a "$LOG_FILE"
    
    log "✅ Baseline Trial $i complete at $(date +'%H:%M:%S')"
    
    # Small pause between trials
    sleep 2
done

log ""
log "=========================================="
log "PHASE 1 COMPLETE - All baseline trials done"
log "=========================================="
log ""

# Run optimized trials
log "PHASE 2: OPTIMIZED CONFIGURATION TRIALS"
log "Config: temp=0.3, top_k=5, threshold=0.3"
log "=========================================="
for i in $(seq 1 $NUM_TRIALS); do
    log ""
    log ">>> Optimized Trial $i/$NUM_TRIALS <<<"
    log "Started at: $(date +'%H:%M:%S')"
    
    time python -u "$SCRIPT_DIR/run_evaluation.py" \
        --questionnaire "$QUESTIONNAIRE" \
        --temp 0.3 \
        --threshold 0.3 \
        --top-k 5 \
        --name "Statistical - Optimized Trial $i" \
        2>&1 | tee -a "$LOG_FILE"
    
    log "✅ Optimized Trial $i complete at $(date +'%H:%M:%S')"
    
    # Small pause between trials
    sleep 2
done

log ""
log "=========================================="
log "  ALL TRIALS COMPLETE!"
log "=========================================="
log "Completed at: $(date +'%Y-%m-%d %H:%M:%S')"
log ""

# Calculate statistics using the tested Python module
log "Calculating statistics..."
log ""

python "$SCRIPT_DIR/calculate_trial_statistics.py" \
    --baseline-pattern "Statistical - Baseline Trial%" \
    --optimized-pattern "Statistical - Optimized Trial%" \
    --num-trials $NUM_TRIALS \
    2>&1 | tee -a "$LOG_FILE"

log ""
log "Full log saved to: $LOG_FILE"
log ""
log "View all runs with:"
log "  python scripts/compare_runs.py"
