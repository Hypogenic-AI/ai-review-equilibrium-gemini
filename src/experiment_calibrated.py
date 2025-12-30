import os
import json
import pandas as pd
from tqdm import tqdm
from src.utils import load_iclr_data, read_paper_text
from src.reviewer import ReviewerAgent

# Configuration: Use the same models but with a HARSH system prompt
HARSH_SYSTEM_PROMPT = """You are a strict, critical reviewer for ICLR, a top-tier machine learning conference. 
You are known for maintaining very high standards. 
- You should use the full scoring range (1-10).
- The average paper should receive a 4 or 5. 
- Scores of 7 or 8 should be reserved for clear acceptances.
- Scores of 9 or 10 are extremely rare.
- Be skeptical of empirical claims without rigorous proof.
"""

MODELS = [
    ("openai/gpt-4o", "GPT-4o-Harsh", HARSH_SYSTEM_PROMPT),
    ("anthropic/claude-3.5-sonnet", "Claude-3.5-Harsh", HARSH_SYSTEM_PROMPT),
    ("openai/gpt-4o-mini", "GPT-4o-mini-Harsh", HARSH_SYSTEM_PROMPT)
]

OUTPUT_DIR = "results/calibrated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_calibrated_experiment(limit=5):
    print("Loading data for calibrated experiment...")
    df = load_iclr_data(limit=limit)
    if df.empty:
        print("No data found!")
        return

    # Initialize Agents with Harsh Prompt
    agents = [ReviewerAgent(model_id, name, system_prompt=prompt) for model_id, name, prompt in MODELS]

    results = []

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing Papers (Calibrated)"):
        paper_id = row['paper_id']
        file_path = row['text_path']
        ground_truth_decision = row['decision']
        
        # Calculate Ground Truth Score
        human_scores = []
        for col in df.columns:
            if str(col).isdigit():
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
        }

        # --- Round 0: Initial Review Only (Testing Persona) ---
        for agent in agents:
            review = agent.review(paper_text)
            paper_result["reviews_round_0"][agent.name] = review
            
        results.append(paper_result)

    # Save Results
    with open(os.path.join(OUTPUT_DIR, "calibrated_results.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Flatten for CSV
    flat_data = []
    for r in results:
        base = {
            "paper_id": r["paper_id"], 
            "gt_decision": r["ground_truth_decision"],
            "gt_score": r["ground_truth_score"]
        }
        scores = []
        for name, rev in r["reviews_round_0"].items():
            base[f"score_{name}"] = rev.get("score")
            scores.append(rev.get("score", 0))
        base["avg_score"] = sum(scores) / len(scores) if scores else 0
        flat_data.append(base)

    csv_path = os.path.join(OUTPUT_DIR, "calibrated_results.csv")
    pd.DataFrame(flat_data).to_csv(csv_path, index=False)
    print(f"Calibrated Experiment Complete. Results saved to {csv_path}")

if __name__ == "__main__":
    run_calibrated_experiment(limit=10) # Run on same 10 if possible for direct comparison
