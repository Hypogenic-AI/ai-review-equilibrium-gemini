import os
import json
import pandas as pd
from src.reviewer import ReviewerAgent
from src.utils import read_paper_text

# Configuration
PAPER_ID = "MWQCPYSJRN" # One of the papers that had a score change (6->7) and was rejected by humans
HARSH_SYSTEM_PROMPT = """You are a strict, critical reviewer for ICLR."""

def run_improvement_experiment():
    print(f"Running Improvement Experiment on Paper {PAPER_ID}...")
    
    # Load original result to get critique
    with open("results/experiment_results.json", 'r') as f:
        data = json.load(f)
    
    paper_data = next((p for p in data if p['paper_id'] == PAPER_ID), None)
    if not paper_data:
        print("Paper not found in results.")
        return

    # Extract Consensus Weaknesses (from Round 1)
    weaknesses = []
    for agent, review in paper_data['reviews_round_1'].items():
        if 'weaknesses' in review:
            weaknesses.extend(review['weaknesses'])
    
    critique_text = "\n".join([f"- {w}" for w in weaknesses[:5]]) # Top 5 weaknesses
    print("Consensus Critique extracted.")

    # Load Paper Text
    # We need the path. Let's cheat and look up from the CSV or just scan
    import glob
    files = glob.glob(f"datasets/AI-Scientist-ICLR/iclr_parsed/{PAPER_ID}.txt")
    if not files:
        print("Text file not found.")
        return
    
    original_text = read_paper_text(files[0])
    
    # 1. Editor Agent: Improve Abstract/Intro
    print("Asking Editor Agent to improve text...")
    
    # Use direct client to avoid JSON restriction of ReviewerAgent
    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_KEY") or os.getenv("OPENROUTER_API_KEY"),
    )
    
    improve_prompt = f"""
Here is a scientific paper text (truncated).
Critics have pointed out the following weaknesses:
{critique_text}

Please REWRITE the Abstract and Introduction (first ~500 words) to address these critiques.
Output ONLY the rewritten text.
"""
    
    messages = [
        {"role": "system", "content": "You are an expert scientific editor."},
        {"role": "user", "content": improve_prompt + "\n\nPAPER TEXT:\n" + original_text[:4000]}
    ]
    
    resp = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=messages
    )
    improved_intro = resp.choices[0].message.content

    
    # Construct "Improved" Paper Text (Naively replace start)
    # This is a bit hacky but sufficient to test the concept
    improved_paper_text = improved_intro + "\n\n" + original_text[2000:] # rough slice
    
    # 2. Re-evaluate with Harsh Critic
    print("Re-evaluating with Harsh Critic...")
    critic = ReviewerAgent("openai/gpt-4o", "HarshCritic", system_prompt=HARSH_SYSTEM_PROMPT)
    
    print("--- Original Score ---")
    rev_orig = critic.review(original_text)
    print(f"Score: {rev_orig.get('score')}")
    print(f"Reasoning: {rev_orig.get('reasoning')}")

    print("--- Improved Score ---")
    rev_imp = critic.review(improved_paper_text)
    print(f"Score: {rev_imp.get('score')}")
    print(f"Reasoning: {rev_imp.get('reasoning')}")
    
    # Save result
    result = {
        "paper_id": PAPER_ID,
        "original_score": rev_orig.get('score'),
        "improved_score": rev_imp.get('score'),
        "critique_used": critique_text,
        "improvement_text": improved_intro[:500]
    }
    
    with open("results/improvement_experiment.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_improvement_experiment()
