import json
import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt

RESULTS_PATH = "results/experiment_results.json"
OUTPUT_DIR = "results/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_text_content(review_json):
    if not review_json:
        return ""
    # Try to get the most substantive text field
    # Round 0 usually has 'weaknesses' or 'reasoning'
    # Round 1 usually has 'argument', 'reasoning', 'main_review', 'arguments'
    
    candidates = []
    
    # Priority keys
    keys = ['weaknesses', 'reasoning', 'argument', 'main_review', 'arguments']
    
    for k in keys:
        if k in review_json:
            val = review_json[k]
            if isinstance(val, list):
                candidates.append(" ".join(val))
            else:
                candidates.append(str(val))
    
    # Join all found text to get a comprehensive representation
    return " ".join(candidates)

def analyze_diversity():
    if not os.path.exists(RESULTS_PATH):
        print("Results file not found.")
        return

    with open(RESULTS_PATH, 'r') as f:
        data = json.load(f)

    sims_0 = []
    sims_1 = []

    vectorizer = TfidfVectorizer(stop_words='english')

    for paper in data:
        r0 = paper['reviews_round_0']
        r1 = paper['reviews_round_1']
        
        # Get texts for Round 0
        texts_0 = [get_text_content(r0[agent]) for agent in r0]
        # Get texts for Round 1
        texts_1 = [get_text_content(r1[agent]) for agent in r1]
        
        # Ensure we have non-empty texts
        texts_0 = [t for t in texts_0 if t.strip()]
        texts_1 = [t for t in texts_1 if t.strip()]


        # Compute Similarity Round 0
        try:
            tfidf_0 = vectorizer.fit_transform(texts_0)
            pairwise_0 = cosine_similarity(tfidf_0)
            # Get upper triangle values (excluding diagonal)
            vals_0 = pairwise_0[np.triu_indices(len(texts_0), k=1)]
            sims_0.extend(vals_0)
        except ValueError:
            pass # Empty vocab or similar issue

        # Compute Similarity Round 1
        try:
            tfidf_1 = vectorizer.fit_transform(texts_1)
            pairwise_1 = cosine_similarity(tfidf_1)
            vals_1 = pairwise_1[np.triu_indices(len(texts_1), k=1)]
            sims_1.extend(vals_1)
        except ValueError:
            pass

    avg_sim_0 = np.mean(sims_0) if sims_0 else 0
    avg_sim_1 = np.mean(sims_1) if sims_1 else 0
    
    print(f"Average Pairwise Text Similarity (Round 0): {avg_sim_0:.4f}")
    print(f"Average Pairwise Text Similarity (Round 1): {avg_sim_1:.4f}")
    
    # Plot
    plt.figure(figsize=(6, 6))
    data_plot = pd.DataFrame({
        'Round': ['Round 0'] * len(sims_0) + ['Round 1'] * len(sims_1),
        'Cosine Similarity': list(sims_0) + list(sims_1)
    })
    
    sns.boxplot(data=data_plot, x='Round', y='Cosine Similarity')
    plt.title("Content Homogenization: Text Similarity of Weaknesses")
    plt.ylim(0, 1)
    
    output_path = os.path.join(OUTPUT_DIR, "diversity_change.png")
    plt.savefig(output_path)
    print(f"Diversity plot saved to {output_path}")

if __name__ == "__main__":
    analyze_diversity()
