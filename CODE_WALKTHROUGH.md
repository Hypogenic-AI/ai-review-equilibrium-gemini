# Code Walkthrough: AI Reviewing Equilibrium

This document provides a technical overview of the codebase for the AI Reviewing Equilibrium project.

## Directory Structure
*   `src/`: Contains all source code.
*   `results/`: Stores output JSON/CSV files and generated plots.
*   `datasets/`: Contains the ICLR paper data.

## Key Modules

### 1. `src/reviewer.py`: The Agent Class
The `ReviewerAgent` class is the core abstraction for an LLM reviewer.
*   **Initialization**: Takes a `model_name` (e.g., `openai/gpt-4o`) and a `system_prompt`. This allows easy creation of different personas (e.g., "Harsh Critic").
*   **`review(paper_text)`**: 
    *   Constructs a zero-shot prompt asking for a structured JSON review.
    *   Expects keys: `summary`, `strengths`, `weaknesses`, `score`, `decision`.
    *   Handles API calls via `OpenAI` client (pointing to OpenRouter).
*   **`update_review(paper_text, previous_review, other_reviews)`**:
    *   The core "Debate" function.
    *   Injects the full text of peer reviews into the prompt.
    *   Asks the model to "re-evaluate" and "adjust if they raise valid points".

### 2. `src/experiment.py`: The Main Loop
This script orchestrates the debate process.
*   **Data Loading**: Uses `utils.load_iclr_data` to fetch paper texts and ground truth decisions.
*   **Agent Setup**: Instantiates 3 agents (`GPT-4o`, `Claude-3.5`, `GPT-4o-mini`).
*   **Round 0**: Iterates through papers, getting independent reviews from each agent.
*   **Round 1 (Debate)**: 
    *   For each agent, it gathers the reviews from the *other* two agents.
    *   Calls `update_review` to get the post-debate score.
*   **Serialization**: Saves intermediate results to `results/experiment_results.json` to prevent data loss.

### 3. `src/utils.py`: Data Utilities
*   **`load_iclr_data`**: Parses the `ratings_subset.tsv` and matches paper IDs to the raw text files in `iclr_parsed/`.
*   **`read_paper_text`**: Reads the raw text and performs truncation (default 15k tokens) to ensure the prompt fits within standard context windows.

### 4. `src/experiment_calibrated.py`
A variation of the main experiment that:
*   Injects a specific "Harsh Critic" system prompt.
*   Runs only Round 0 to test the impact of the persona on score distribution.

### 5. `src/analyze_*.py` Scripts
*   **`analyze_debate.py`**: Extracts qualitative reasoning changes.
*   **`analyze_diversity.py`**: Computes TF-IDF cosine similarity between reviews.
*   **`compare_sota.py`**: Merges our results with the SOTA baseline CSVs and computes correlations.

## Reproducibility
The entire pipeline is sewn together in `run_all.sh`, which executes these scripts in logical order.
