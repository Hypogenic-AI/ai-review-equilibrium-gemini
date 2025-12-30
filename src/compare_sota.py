import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

MY_RESULTS = "results/experiment_results.csv"
SOTA_RESULTS = "datasets/AI-Scientist-ICLR/llm_reviews/gpt-4o-2024-05-13_temp_0_1_reflect_5_ensemble_5_pages_all.csv"
OUTPUT_DIR = "results/comparison"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def compare_sota():
    print("Loading datasets...")
    if not os.path.exists(MY_RESULTS):
        print("My results not found.")
        return
    
    df_mine = pd.read_csv(MY_RESULTS)
    
    try:
        df_sota = pd.read_csv(SOTA_RESULTS)
    except FileNotFoundError:
        print(f"SOTA file not found at {SOTA_RESULTS}")
        return

    # SOTA CSV column structure needs inspection. 
    # Usually 'title' or 'paper_id' or 'forum'.
    # Let's try to match by 'paper_id' (my file) vs whatever is in theirs.
    # The filenames in `iclr_parsed` are the IDs. 
    
    print(f"My papers: {len(df_mine)}")
    print(f"SOTA papers: {len(df_sota)}")
    
    # Check SOTA columns
    print("SOTA columns:", df_sota.columns.tolist())
    
    # Assuming SOTA has a column for ID. If not, we might need to map titles.
    # But wait, utils.py used the filename as ID.
    # Let's hope SOTA has the ID.
    
    # Merge
    # df_mine: paper_id, gt_score, avg_score_1 (Consensus)
    # df_sota: paper_id, Overall (SOTA Score)
    
    # Filter SOTA to only relevant columns
    df_sota_clean = df_sota[['paper_id', 'Overall']].rename(columns={'Overall': 'sota_score'})
    
    merged = pd.merge(df_mine, df_sota_clean, on='paper_id', how='inner')
    
    if merged.empty:
        print("No overlapping papers found! Check IDs.")
        # Debug: print sample IDs
        print("Mine IDs:", df_mine['paper_id'].head().tolist())
        print("SOTA IDs:", df_sota['paper_id'].head().tolist())
        return

    print(f"Overlapping papers: {len(merged)}")
    
    # Metrics
    # Correlation with GT
    corr_mine = merged['avg_score_1'].corr(merged['gt_score'])
    corr_sota = merged['sota_score'].corr(merged['gt_score'])
    
    print(f"Correlation (My Debate Consensus): {corr_mine:.4f}")
    print(f"Correlation (SOTA Reflection Ensemble): {corr_sota:.4f}")
    
    # Plot
    plt.figure(figsize=(8, 6))
    sns.barplot(x=['Debate (Ours)', 'SOTA (Reflection)'], y=[corr_mine, corr_sota], palette=['blue', 'orange'])
    plt.title("Correlation with Human Scores (n=10)")
    plt.ylabel("Pearson Correlation")
    plt.ylim(-0.2, 1.0)
    plt.axhline(0, color='black', linewidth=0.8)
    
    output_path = os.path.join(OUTPUT_DIR, "method_comparison.png")
    plt.savefig(output_path)
    print(f"Comparison plot saved to {output_path}")
    
    # Save comparison data
    merged.to_csv(os.path.join(OUTPUT_DIR, "comparison_data.csv"), index=False)

if __name__ == "__main__":
    compare_sota()
