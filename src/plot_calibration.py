import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_comparison():
    # Load data
    df_orig = pd.read_csv("results/experiment_results.csv")
    df_calib = pd.read_csv("results/calibrated/calibrated_results.csv")
    
    # Calculate means
    mean_human = df_orig['gt_score'].mean()
    mean_orig_ai = df_orig['avg_score_0'].mean()
    mean_calib_ai = df_calib['avg_score'].mean()
    
    print(f"Human Mean: {mean_human:.2f}")
    print(f"Original AI Mean: {mean_orig_ai:.2f}")
    print(f"Calibrated AI Mean: {mean_calib_ai:.2f}")
    
    # Create DataFrame for plotting
    data = pd.DataFrame({
        "Reviewer Type": ["Human", "AI (Original)", "AI (Calibrated)"],
        "Average Score": [mean_human, mean_orig_ai, mean_calib_ai]
    })
    
    plt.figure(figsize=(8, 6))
    sns.barplot(data=data, x="Reviewer Type", y="Average Score", palette=["gray", "red", "green"])
    plt.axhline(y=mean_human, color='gray', linestyle='--', label="Human Ground Truth")
    plt.title("Effect of 'Harsh Critic' Persona on Review Scores")
    plt.ylim(0, 10)
    plt.ylabel("Average Score (1-10)")
    
    output_path = "results/calibrated/score_comparison.png"
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    plot_comparison()
