import os
import json
import pandas as pd
from tqdm import tqdm
from src.utils import load_iclr_data, read_paper_text
from src.reviewer import ReviewerAgent

# Configuration
MODELS = [
    ("openai/gpt-4o", "GPT-4o"),
    ("anthropic/claude-3.5-sonnet", "Claude-3.5"),
    ("openai/gpt-4o-mini", "GPT-4o-mini")
]

OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_experiment(limit=10):
    print("Loading data...")
    df = load_iclr_data(limit=limit)
    if df.empty:
        print("No data found!")
        return

    print(f"Loaded {len(df)} papers.")

    # Initialize Agents
    agents = [ReviewerAgent(model_id, name) for model_id, name in MODELS]

    results = []

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing Papers"):
        paper_id = row['paper_id']
        file_path = row['text_path']
        ground_truth_decision = row['decision']
        
        # Ground truth score might be in columns 0-6 (individual ratings)
        # Calculate average human score if possible
        human_scores = []
        for col in df.columns:
            if str(col).isdigit(): # Assuming columns '0', '1', etc. are scores
                try:
                    val = float(row[col])
                    if not pd.isna(val):
                        human_scores.append(val)
                except:
                    pass
        avg_human_score = sum(human_scores) / len(human_scores) if human_scores else None

        try:
            paper_text = read_paper_text(file_path, max_tokens=15000)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        paper_result = {
            "paper_id": paper_id,
            "ground_truth_decision": ground_truth_decision,
            "ground_truth_score": avg_human_score,
            "reviews_round_0": {},
            "reviews_round_1": {}
        }

        # --- Round 0: Initial Review ---
        round_0_reviews = []
        for agent in agents:
            review = agent.review(paper_text)
            paper_result["reviews_round_0"][agent.name] = review
            round_0_reviews.append(review)
        
        # --- Round 1: Debate/Update ---
        for i, agent in enumerate(agents):
            # Agent sees others' reviews (excluding their own, or including? 
            # Usually strictly others, but seeing own is implicit context)
            other_reviews = [r for j, r in enumerate(round_0_reviews) if j != i]
            
            updated_review = agent.update_review(paper_text, round_0_reviews[i], other_reviews)
            paper_result["reviews_round_1"][agent.name] = updated_review

        results.append(paper_result)
        
        # Incremental save
        with open(os.path.join(OUTPUT_DIR, "experiment_results_partial.json"), 'w') as f:
            json.dump(results, f, indent=2)

    # Final Save
    with open(os.path.join(OUTPUT_DIR, "experiment_results.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Flatten for CSV
    flat_data = []
    for r in results:
        base = {
            "paper_id": r["paper_id"], 
            "gt_decision": r["ground_truth_decision"],
            "gt_score": r["ground_truth_score"]
        }
        
        # Add Round 0 scores
        scores_0 = []
        for name, rev in r["reviews_round_0"].items():
            base[f"score_0_{name}"] = rev.get("score")
            scores_0.append(rev.get("score", 0))
        base["avg_score_0"] = sum(scores_0) / len(scores_0) if scores_0 else 0
        
        # Add Round 1 scores
        scores_1 = []
        for name, rev in r["reviews_round_1"].items():
            base[f"score_1_{name}"] = rev.get("score")
            scores_1.append(rev.get("score", 0))
        base["avg_score_1"] = sum(scores_1) / len(scores_1) if scores_1 else 0
        
        flat_data.append(base)

    pd.DataFrame(flat_data).to_csv(os.path.join(OUTPUT_DIR, "experiment_results.csv"), index=False)
    print("Experiment Complete. Results saved.")

if __name__ == "__main__":
    run_experiment(limit=10) # Start small
