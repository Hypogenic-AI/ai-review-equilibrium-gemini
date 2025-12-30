import json

# Pricing (approx per 1M tokens)
# Date: Late 2024 / Early 2025 estimates
PRICES = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60}
}

# Usage Assumptions
PAPER_LENGTH = 15000  # tokens
REVIEW_LENGTH = 500   # tokens

def calculate_cost():
    print("=== COST ANALYSIS (Per Paper) ===\n")
    
    # 1. Single Agent (GPT-4o)
    cost_single = (PAPER_LENGTH / 1e6 * PRICES['gpt-4o']['input']) + \
                  (REVIEW_LENGTH / 1e6 * PRICES['gpt-4o']['output'])
    
    print(f"1. Single Agent (GPT-4o):")
    print(f"   Input: {PAPER_LENGTH} toks, Output: {REVIEW_LENGTH} toks")
    print(f"   Cost: ${cost_single:.4f}")
    
    # 2. Debate (Our Config: GPT-4o, Claude 3.5, Mini) - 2 Rounds
    # Round 0: 3 separate reviews
    cost_r0 = 0
    for model in ["gpt-4o", "claude-3-5-sonnet", "gpt-4o-mini"]:
        cost_r0 += (PAPER_LENGTH / 1e6 * PRICES[model]['input']) + \
                   (REVIEW_LENGTH / 1e6 * PRICES[model]['output'])
    
    # Round 1: Each agent sees paper + 2 other reviews (approx 1000 toks context)
    context_r1 = PAPER_LENGTH + (2 * REVIEW_LENGTH)
    cost_r1 = 0
    for model in ["gpt-4o", "claude-3-5-sonnet", "gpt-4o-mini"]:
        cost_r1 += (context_r1 / 1e6 * PRICES[model]['input']) + \
                   (REVIEW_LENGTH / 1e6 * PRICES[model]['output'])
                   
    total_debate = cost_r0 + cost_r1
    
    print(f"\n2. Debate (3 Agents, 2 Rounds):")
    print(f"   Round 0 Cost: ${cost_r0:.4f}")
    print(f"   Round 1 Cost: ${cost_r1:.4f}")
    print(f"   Total Cost:   ${total_debate:.4f}")
    print(f"   Ratio vs Single: {total_debate/cost_single:.1f}x")
    
    # 3. SOTA Ensemble (5 x GPT-4o, Single Pass assumed for lower bound comparison)
    # The AI Scientist paper uses 'reflection' which adds steps, but let's just do simple Ensemble 5
    cost_ensemble = 5 * cost_single
    
    print(f"\n3. Simple Ensemble (5 x GPT-4o):")
    print(f"   Total Cost:   ${cost_ensemble:.4f}")
    
    # ROI Metric: Correlation gain per dollar?
    # Single: 0.33 corr / $0.04
    # Debate: 0.36 corr (Calibrated) / $0.15
    
    print(f"\n--- Efficiency Analysis ---")
    print(f"Cost per 1% Correlation Point:")
    print(f"   Single (Corr 0.33): ${cost_single/33:.5f}")
    print(f"   Debate (Corr 0.36): ${total_debate/36:.5f}")
    
    return {
        "single": cost_single,
        "debate": total_debate,
        "ensemble": cost_ensemble
    }

if __name__ == "__main__":
    calculate_cost()
