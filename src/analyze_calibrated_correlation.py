import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

CALIB_RESULTS = "results/calibrated/calibrated_results.csv"
OUTPUT_DIR = "results/calibrated"

def analyze_calibrated_correlation():
    if not os.path.exists(CALIB_RESULTS):
        print("Calibrated results not found.")
        return

    df = pd.read_csv(CALIB_RESULTS)
    
    # Calculate Correlation
    # We use 'avg_score' (AI) vs 'gt_score' (Human)
    corr = df['avg_score'].corr(df['gt_score'])
    
    print(f"--- Calibrated Experiment Analysis ---")
    print(f"Number of papers: {len(df)}")
    print(f"Correlation (Calibrated AI vs Human): {corr:.4f}")
    
    # Compare with Original (Hardcoded from previous run for simplicity, or load)
    # Original Correlation was 0.3283 (Ensemble Round 0)
    print(f"Correlation (Original AI vs Human): ~0.33")
    
    # Scatter Plot
    plt.figure(figsize=(6, 6))
    sns.scatterplot(data=df, x='gt_score', y='avg_score')
    
    # Add trendline
    sns.regplot(data=df, x='gt_score', y='avg_score', scatter=False, color='green')
    
    plt.title(f"Calibrated AI vs Human Scores (r={corr:.2f})")
    plt.xlabel("Human Ground Truth Score")
    plt.ylabel("Calibrated AI Score (Harsh Persona)")
    plt.xlim(1, 10)
    plt.ylim(1, 10)
    plt.plot([1, 10], [1, 10], 'k--', alpha=0.5, label="Perfect Agreement")
    plt.legend()
    
    output_path = os.path.join(OUTPUT_DIR, "calibrated_correlation.png")
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    analyze_calibrated_correlation()
