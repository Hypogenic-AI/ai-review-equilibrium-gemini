import json
import os

def get_reasoning(review_json):
    if not review_json:
        return "N/A"
    # Try common keys
    for key in ['reasoning', 'argument', 'main_review', 'arguments']:
        if key in review_json:
            val = review_json[key]
            if isinstance(val, list):
                return " ".join(val)
            return str(val)
    return "N/A"

def analyze_debate_qualitative():
    results_path = "results/experiment_results.json"
    if not os.path.exists(results_path):
        print("No results file found.")
        return

    with open(results_path, 'r') as f:
        data = json.load(f)

    changed_cases = 0
    print("=== QUALITATIVE ANALYSIS OF DEBATE DYNAMICS ===\n")

    for paper in data:
        paper_id = paper['paper_id']
        r0 = paper['reviews_round_0']
        r1 = paper['reviews_round_1']

        # Check for score changes
        changes = []
        for agent_name in r0:
            s0 = r0[agent_name].get('score')
            s1 = r1[agent_name].get('score')
            
            # Extract reasoning robustly
            reason0 = get_reasoning(r0[agent_name])
            reason1 = get_reasoning(r1[agent_name])
            
            if s0 != s1:
                changes.append((agent_name, s0, s1, reason0, reason1))

        if changes:
            changed_cases += 1
            print(f"--- Paper {paper_id} (GT Decision: {paper['ground_truth_decision']}) ---")
            for agent, s0, s1, reason0, reason1 in changes:
                print(f"[{agent}] Score: {s0} -> {s1}")
                print(f"  Reason 0: {reason0[:200]}..." if len(reason0)>200 else f"  Reason 0: {reason0}")
                print(f"  Reason 1: {reason1[:200]}..." if len(reason1)>200 else f"  Reason 1: {reason1}")
                print("")
            print("------------------------------------------------\n")

    print(f"Total papers with score changes: {changed_cases} / {len(data)}")

if __name__ == "__main__":
    analyze_debate_qualitative()
