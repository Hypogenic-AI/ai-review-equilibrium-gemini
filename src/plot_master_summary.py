import matplotlib.pyplot as plt
import json
import pandas as pd
import seaborn as sns
import os

def plot_master_summary():
    # Load summary data
    with open("results/final_summary.json", "r") as f:
        data = json.load(f)

    # Set up figure
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('AI Reviewing Equilibrium: Key Findings', fontsize=16)

    # --- Plot 1: Variance Reduction (Equilibrium) ---
    # Data from main_experiment
    std_0 = data['main_experiment']['avg_std_0']
    std_1 = data['main_experiment']['avg_std_1']
    
    sns.barplot(x=['Initial (Round 0)', 'Post-Debate (Round 1)'], y=[std_0, std_1], ax=axes[0], palette=['lightblue', 'blue'])
    axes[0].set_title('Finding 1: Debate Reduces Disagreement')
    axes[0].set_ylabel('Avg Standard Deviation of Scores')
    axes[0].text(0, std_0, f"{std_0:.2f}", ha='center', va='bottom')
    axes[0].text(1, std_1, f"{std_1:.2f}", ha='center', va='bottom')

    # --- Plot 2: Mean Score (Inflation vs Calibration) ---
    # Data from main (via raw calc or implicit) and calibration
    # We recall from report: Human=5.66, Orig=7.87, Calib=6.33
    # Let's use the exact values if possible, or hardcode the verified ones from the report/summary
    # Calibration is in summary, Main avg isn't explicitly in summary JSON but we know it.
    
    means = {
        'Human (GT)': 5.66,
        'AI (Original)': 7.87,
        'AI (Harsh)': data['calibration_experiment']['mean_score']
    }
    
    sns.barplot(x=list(means.keys()), y=list(means.values()), ax=axes[1], palette=['gray', 'red', 'green'])
    axes[1].set_title('Finding 2: Calibration Fixes Inflation')
    axes[1].set_ylabel('Average Score (1-10)')
    axes[1].set_ylim(0, 10)
    for i, v in enumerate(means.values()):
        axes[1].text(i, v, f"{v:.2f}", ha='center', va='bottom')

    # --- Plot 3: Correlation Comparison ---
    # Data from SOTA and Calibration
    corrs = {
        'SOTA (Reflection)': data['sota_comparison']['sota_correlation'],
        'Debate (Ours)': data['sota_comparison']['debate_correlation'],
        'Debate + Harsh': data['calibration_experiment']['correlation']
    }
    
    sns.barplot(x=list(corrs.keys()), y=list(corrs.values()), ax=axes[2], palette=['orange', 'blue', 'green'])
    axes[2].set_title('Finding 3: Debate & Persona Improve Accuracy')
    axes[2].set_ylabel('Correlation with Human Scores')
    axes[2].set_ylim(-0.2, 0.5)
    axes[2].axhline(0, color='black', linewidth=0.8)
    for i, v in enumerate(corrs.values()):
        axes[2].text(i, v if v>0 else 0, f"{v:.2f}", ha='center', va='bottom' if v>0 else 'top')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    output_path = "results/master_summary_plot.png"
    plt.savefig(output_path)
    print(f"Master plot saved to {output_path}")

if __name__ == "__main__":
    plot_master_summary()
