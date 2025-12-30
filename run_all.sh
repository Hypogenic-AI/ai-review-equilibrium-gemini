#!/bin/bash
set -e

echo "========================================================"
echo "STARTING FULL REPRODUCTION OF 'AI REVIEWING EQUILIBRIUM'"
echo "========================================================"

# Activate Environment
source .venv/bin/activate
export PYTHONPATH=.

echo "[1/7] Running Main Experiment (Debate Loop)..."
python src/experiment.py

echo "[2/7] Running Calibration Experiment (Harsh Critic)..."
python src/experiment_calibrated.py

echo "[3/7] Analyzing Debate Dynamics (Qualitative)..."
python src/analyze_debate.py > results/debate_analysis.txt

echo "[4/7] Running Improvement Experiment (Editor Agent)..."
python src/experiment_improvement.py

echo "[5/7] Analyzing Diversity (Text Similarity)..."
python src/analyze_diversity.py

echo "[6/7] Comparing with SOTA (Reflection Ensemble)..."
python src/compare_sota.py

echo "[7/7] Aggregating Final Metrics..."
python src/aggregate_metrics.py

echo "[8/8] Analyzing Cost & Efficiency..."
python src/analyze_cost.py

echo "========================================================"
echo "REPRODUCTION COMPLETE!"
echo "Check 'results/final_summary.json' and 'REPORT.md'."
echo "========================================================"
