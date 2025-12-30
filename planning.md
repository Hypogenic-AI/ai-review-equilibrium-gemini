# Research Plan: AI Reviewing Equilibrium

## 1. Research Question
Can a multi-agent "equilibrium" process, involving distinct Large Language Models (LLMs) debating a scientific paper, produce review scores that correlate better with human decisions than single-agent reviews or simple ensembles?

## 2. Background and Motivation
AI-based paper reviewing is gaining traction (e.g., "The AI Scientist"), but current approaches mostly rely on single massive models (GPT-4o) or ensembles of the *same* model. Scientific review is inherently subjective and benefits from diverse perspectives. "Multi-agent Debate" has been shown to improve factuality, but its application to the subjective task of peer review—where agents must weigh novelty vs. flaws—is underexplored. We hypothesize that distinct models (GPT-4o, Claude 3.5, Gemini 1.5) have different biases and that forcing them to "debate" will lead to a more robust consensus.

## 3. Hypothesis Decomposition
*   **H1 (Diversity):** Distinct LLMs (GPT-4o, Claude, Gemini) produce reviews with lower semantic similarity and score correlation than multiple runs of the same model (temperature-based diversity).
*   **H2 (Convergence):** A multi-round debate process reduces the variance of scores among agents (seeking equilibrium).
*   **H3 (Accuracy):** The consensus score after debate correlates more strongly with ground-truth human decisions (Accept/Reject) than the initial single-agent scores or a simple average of initial scores.

## 4. Proposed Methodology

### Approach
We will implement a "Reviewer Equilibrium" pipeline using the `AI-Scientist-ICLR` dataset. We will instantiate three distinct reviewer agents. They will review papers in parallel (blind), then share their reviews, and update their assessments.

### Experimental Steps
1.  **Data Selection**: Select a random subset of 10-20 papers from `datasets/AI-Scientist-ICLR/iclr_parsed` which have ground truth in `ratings_subset.tsv`.
2.  **Agent Instantiation**:
    *   **Reviewer A**: `openai/gpt-4o`
    *   **Reviewer B**: `anthropic/claude-3.5-sonnet`
    *   **Reviewer C**: `google/gemini-pro-1.5`
    *   (Fallback: If specific keys fail, use OpenRouter for all).
3.  **Round 0 (Blind Review)**: Each agent reads the paper text and generates a review (Score 1-10, Decision, Summary, Strengths, Weaknesses).
4.  **Round 1 (Debate/Update)**: Each agent receives the full text of the *other* two reviews and is prompted: "Here are reviews from other experts. Re-evaluate your score and comments. You may maintain your position if you disagree, but adjust if they raise valid points."
5.  **Aggregation**: Calculate metrics at Round 0 and Round 1.

### Baselines
1.  **Single Agent (GPT-4o)**: Standard review (taken from Round 0 of Agent A or existing CSVs).
2.  **Simple Ensemble**: Average of Round 0 scores from A, B, and C (without debate).

### Evaluation Metrics
1.  **Agreement (Inter-Annotator)**: Standard Deviation of scores across agents (Pre vs. Post Debate).
2.  **Accuracy**: Pearson/Spearman correlation of the (aggregated) AI score with the Human Decision (0/1) or Human Score (if available).
3.  **Diversity**: Semantic similarity (embedding cosine similarity) of the "Weaknesses" section between agents.

### Statistical Analysis Plan
*   **t-test**: Compare mean absolute error (MAE) of "Debate Consensus" vs "Simple Ensemble" against Ground Truth.
*   **Variance reduction**: Check if variance significantly decreases after debate.

## 5. Timeline
*   **Phase 1 (Done)**: Planning & Resource Check.
*   **Phase 2 (10 min)**: Environment Setup (`uv`, dependencies).
*   **Phase 3 (60 min)**: Implementation (`ReviewerAgent`, `DebateLoop`).
*   **Phase 4 (60 min)**: Experiments (Run on ~20 papers).
*   **Phase 5 (30 min)**: Analysis (Correlations, Plots).
*   **Phase 6 (20 min)**: Documentation.

## 6. Potential Challenges
*   **API Costs/Limits**: 20 papers * 3 agents * 2 rounds = 120 calls. Should be within budget.
*   **Context Window**: Papers can be long. We will truncate to first ~15k tokens if needed (most models handle 128k+ now, so likely fine).
*   **Model Availability**: If one model API is flaky, we will fallback to a different provider via OpenRouter.

## 7. Success Criteria
*   Successfully running the debate loop on at least 10 papers.
*   Generating a plot showing variance reduction (or lack thereof).
*   A clear conclusion on whether debate helps accuracy.
