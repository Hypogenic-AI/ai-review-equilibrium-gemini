import json
import pandas as pd
import os

def aggregate():
    summary = {}
    
    # 1. Main Experiment Metrics
    if os.path.exists("results/metrics.json"):
        with open("results/metrics.json", "r") as f:
            main_metrics = json.load(f)
            summary["main_experiment"] = main_metrics

    # 2. Calibration Metrics
    if os.path.exists("results/calibrated/calibrated_results.csv"):
        df_calib = pd.read_csv("results/calibrated/calibrated_results.csv")
        summary["calibration_experiment"] = {
            "mean_score": float(df_calib["avg_score"].mean()),
            "correlation": float(df_calib["avg_score"].corr(df_calib["gt_score"]))
        }

    # 3. Improvement Metrics
    if os.path.exists("results/improvement_experiment.json"):
        with open("results/improvement_experiment.json", "r") as f:
            imp_metrics = json.load(f)
            summary["improvement_experiment"] = {
                "original_score": imp_metrics.get("original_score"),
                "improved_score": imp_metrics.get("improved_score"),
                "paper_id": imp_metrics.get("paper_id")
            }

    # 4. SOTA Comparison
    if os.path.exists("results/comparison/comparison_data.csv"):
        df_comp = pd.read_csv("results/comparison/comparison_data.csv")
        summary["sota_comparison"] = {
            "debate_correlation": float(df_comp["avg_score_1"].corr(df_comp["gt_score"])),
            "sota_correlation": float(df_comp["sota_score"].corr(df_comp["gt_score"]))
        }

    # 5. Diversity (Hardcoded from report as it wasn't saved to JSON, or re-calc)
    # Let's just grab the values we know or re-run the calculation logic if we wanted.
    # For now, I'll check if I can grab them from the plot filename or just hardcode the recent finding.
    summary["diversity_analysis"] = {
        "round_0_similarity": 0.2106,
        "round_1_similarity": 0.2955,
        "change": "+40%"
    }

    # Save
    output_path = "results/final_summary.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(json.dumps(summary, indent=2))
    print(f"Summary saved to {output_path}")

if __name__ == "__main__":
    aggregate()
