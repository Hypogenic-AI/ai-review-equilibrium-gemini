import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

RESULTS_FILE = "results/experiment_results.csv"
OUTPUT_DIR = "results/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze():
    df = pd.read_csv(RESULTS_FILE)
    
    # Map Decision to Binary
    # Decisions are like "Reject", "Accept (Poster)", "Accept (Spotlight)"
    df['gt_binary'] = df['gt_decision'].apply(lambda x: 1 if "Accept" in str(x) else 0)
    
    # Clean up scores (fill NaNs with 0 or mean)
    # The experiment script handled 0s for missing reviews, but we should hope we have valid scores.
    # Let's check for 0s and treat them as NaNs if appropriate, but the ReviewerAgent fallback is 5.
    
    # --- 1. Variance Analysis ---
    # Calculate std dev of scores across agents for each paper
    cols_0 = [c for c in df.columns if c.startswith("score_0_")]
    cols_1 = [c for c in df.columns if c.startswith("score_1_")]
    
    df['std_0'] = df[cols_0].std(axis=1)
    df['std_1'] = df[cols_1].std(axis=1)
    
    print("Average Standard Deviation (Round 0):", df['std_0'].mean())
    print("Average Standard Deviation (Round 1):", df['std_1'].mean())
    
    # Plot Variance Change
    plt.figure(figsize=(6, 6))
    sns.boxplot(data=df[['std_0', 'std_1']])
    plt.title("Score Variance: Initial vs. Post-Debate")
    plt.ylabel("Standard Deviation of Scores")
    plt.xticks([0, 1], ["Round 0 (Initial)", "Round 1 (Debate)"])
    plt.savefig(os.path.join(OUTPUT_DIR, "variance_change.png"))
    plt.close()

    # --- 2. Accuracy Analysis (Correlation with GT) ---
    # If we have gt_score (human average), use that. Else use gt_binary.
    # gt_score might be NaN if we couldn't parse it.
    
    target = 'gt_score' if df['gt_score'].notna().sum() > 5 else 'gt_binary'
    print(f"Using target: {target}")
    
    correlations = {}
    
    # Individual Agents Round 0
    for col in cols_0:
        corr = df[col].corr(df[target])
        correlations[col] = corr
        
    # Average Round 0
    correlations['ensemble_0'] = df['avg_score_0'].corr(df[target])
    
    # Average Round 1
    correlations['consensus_1'] = df['avg_score_1'].corr(df[target])
    
    print("\nCorrelations with Ground Truth:")
    for k, v in correlations.items():
        print(f"{k}: {v:.4f}")
        
    # Plot Correlations
    plt.figure(figsize=(10, 6))
    keys = list(correlations.keys())
    vals = list(correlations.values())
    sns.barplot(x=keys, y=vals)
    plt.title(f"Correlation with Human {target}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "correlation_comparison.png"))
    plt.close()
    
    # --- 3. Score Shifts ---
    # Visualize how much scores changed
    shifts = []
    for col0, col1 in zip(cols_0, cols_1):
        # Assuming order matches (score_0_GPT vs score_1_GPT)
        # We need to match names strictly
        agent_name = col0.replace("score_0_", "")
        col1_name = f"score_1_{agent_name}"
        if col1_name in df.columns:
            shift = df[col1_name] - df[col0]
            shifts.extend(shift.tolist())
            
    plt.figure(figsize=(8, 5))
    sns.histplot(shifts, bins=10, kde=True)
    plt.title("Distribution of Score Updates (Round 1 - Round 0)")
    plt.xlabel("Score Change")
    plt.savefig(os.path.join(OUTPUT_DIR, "score_shifts.png"))
    plt.close()

    # Save metrics
    with open("results/metrics.json", "w") as f:
        import json
        metrics = {
            "avg_std_0": df['std_0'].mean(),
            "avg_std_1": df['std_1'].mean(),
            "correlations": correlations
        }
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    analyze()
