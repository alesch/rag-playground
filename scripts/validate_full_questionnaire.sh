#!/bin/bash
# Option 1: Quick Validation - Run optimized config on full questionnaire
# Estimated time: 15-20 minutes
# Run when you can leave laptop for 20 minutes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/validation_full_questionnaire_$(date +%Y%m%d_%H%M%S).log"

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "  OPTION 1: FULL QUESTIONNAIRE VALIDATION"
log "=========================================="
log "Questionnaire: sample_questionnaire (50 questions)"
log "Configurations to test: 2 (baseline + optimized)"
log "Estimated time: 15-20 minutes"
log "Log file: $LOG_FILE"
log "=========================================="
log ""

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Test 1: Baseline configuration (temp=0.8, threshold=0.0)
log "[1/2] Running BASELINE on full questionnaire..."
log "Config: temp=0.8, top_k=5, threshold=0.0"
time python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire sample_questionnaire \
    --temp 0.8 \
    --threshold 0.0 \
    --top-k 5 \
    --name "Full Q - Baseline (temp=0.8, thresh=0.0)" \
    2>&1 | tee -a "$LOG_FILE"
log "✅ Baseline complete"
log ""

# Test 2: Optimized configuration (temp=0.3, threshold=0.3)
log "[2/2] Running OPTIMIZED on full questionnaire..."
log "Config: temp=0.3, top_k=5, threshold=0.3"
time python "$SCRIPT_DIR/run_evaluation.py" \
    --questionnaire sample_questionnaire \
    --temp 0.3 \
    --threshold 0.3 \
    --top-k 5 \
    --name "Full Q - Optimized (temp=0.3, thresh=0.3)" \
    2>&1 | tee -a "$LOG_FILE"
log "✅ Optimized complete"
log ""

log "=========================================="
log "  VALIDATION COMPLETE!"
log "=========================================="
log ""
log "View results with:"
log "  python scripts/compare_runs.py"
log ""
log "Full log saved to: $LOG_FILE"

# Show results summary
log "Fetching results..."
python "$SCRIPT_DIR/compare_runs.py" 2>&1 | tee -a "$LOG_FILE"
