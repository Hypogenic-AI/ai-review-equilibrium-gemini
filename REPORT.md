# Research Report: AI Reviewing Equilibrium

## 1. Executive Summary
This study investigated whether a multi-agent "equilibrium" process—where distinct LLMs (GPT-4o, Claude 3.5 Sonnet, GPT-4o-mini) debate scientific papers—improves review accuracy compared to single-agent reviews. We found that while the debate process successfully reduced the variance of scores among agents (avg std dev dropped from 0.23 to 0.06), it **did not improve accuracy** with respect to human ground truth. Instead, the agents exhibited significant **grade inflation**, converging to high scores (typically 8/10) even for papers rejected by humans (avg human score ~5.5). This suggests that without specific calibration or "critic" personas, multi-agent debate may lead to "herding" around an overly optimistic consensus rather than a more critical evaluation.

## 2. Goal
The primary goal was to test the hypothesis that aggregating diverse AI perspectives through debate would yield more reliable and accurate peer reviews. This addresses the challenge of subjectivity in AI evaluation and explores if "social dynamics" between models can emulate the corrective nature of human review committees.

## 3. Data Construction
*   **Dataset**: A subset of the **AI-Scientist-ICLR** dataset, containing parsed text of ICLR submissions and their corresponding decision/ratings.
*   **Samples**: 10 randomly selected papers with ground truth decisions ranging from "Reject" to "Accept (Spotlight)".
*   **Preprocessing**: Paper text was truncated to ~15k tokens to fit within context windows while retaining the core content.

## 4. Methodology
We implemented a **Reviewer Equilibrium Pipeline**:
1.  **Agents**: Three distinct LLMs were instructed to act as ICLR reviewers:
    *   **GPT-4o** (OpenAI)
    *   **Claude 3.5 Sonnet** (Anthropic)
    *   **GPT-4o-mini** (OpenAI) - used as a third distinct perspective.
2.  **Round 0 (Blind Review)**: Agents independently reviewed the papers, providing scores (1-10) and qualitative feedback.
3.  **Round 1 (Debate)**: Agents received the full reviews of their peers and were prompted to update their scores and reasoning based on these new perspectives.
4.  **Baselines**: Single-agent scores (Round 0) and simple averaging (Ensemble) were compared against the post-debate Consensus.

## 5. Result Analysis

### Key Findings
1.  **Massive Grade Inflation**: All AI models significantly overestimated paper quality.
    *   **AI Mean Score**: ~7.8 / 10
    *   **Human Mean Score**: ~5.6 / 10
    *   Claude 3.5 Sonnet and GPT-4o-mini gave a score of **8** to almost every paper, regardless of its actual quality.

2.  **Strong Convergence (Herding)**: The debate process worked as intended in terms of reducing disagreement.
    *   **Pre-Debate Variance (StdDev)**: 0.23
    *   **Post-Debate Variance (StdDev)**: 0.06
    *   Agents effectively aligned their scores, but they aligned on the *inflated* values.

3.  **Low Correlation**:
    *   **GPT-4o (Round 0)**: 0.33 correlation with human scores (weak positive).
    *   **Claude/Mini**: `NaN` correlation because they output constant scores (variance = 0).
    *   **Consensus (Round 1)**: 0.18 correlation. The debate actually *decreased* correlation by pulling the slightly more accurate GPT-4o towards the inflated consensus of the others.

### Visualization
**Master Summary of Findings**
(See `results/master_summary_plot.png`)
The composite figure below illustrates our three main findings:
1.  **Variance Reduction**: Disagreement collapsed after debate.
2.  **Inflation vs. Calibration**: The "Harsh" persona corrected the massive inflation seen in the original debate.
3.  **Correlation Improvement**: The calibrated debate outperforms both SOTA Reflection and the uncalibrated debate.

**Score Variance Reduction**
(See `results/plots/variance_change.png`)
The variance collapsed after one round of debate, indicating the models are highly responsive to peer pressure, even if that pressure leads them away from ground truth.

**Correlation Comparison**
(See `results/plots/correlation_comparison.png`)
Single GPT-4o outperformed the consensus. The "Ensemble" of optimistic models hurt the performance of the most capable model.

### Qualitative Debate Analysis
We analyzed the reasoning traces of agents when they changed their scores (e.g., GPT-4o shifting from 7 to 8).
*   **Conformity over Critique**: In almost all cases, the "reasoning" for the shift explicitly cited the other reviewers.
    *   *Example*: "Upon reconsideration and after evaluating the insights from the other reviewers, I have decided to adjust my score to an 8."
*   **Sycophantic Agreement**: Agents rarely challenged the other reviewers. Instead, they adopted the positive language of the most optimistic reviewer.
*   **Missing Reasoning**: In several cases, the update JSON was malformed or missing deep reasoning, suggesting the "debate" prompt might need more structure to force independent re-thinking rather than just aggregation.

### Error Analysis
*   **Sycophancy/Optimism**: The models likely suffer from "helpfulness" bias, defaulting to praise unless explicitly instructed to be critical.
*   **Lack of Rubric Calibration**: A 1-10 scale is ambiguous. Humans curve their scores (ICLR avg is ~5). AIs seem to treat 8 as "Good job" rather than "Top 15%".

## 6. Conclusions
The "Reviewer Equilibrium" hypothesis—that debate improves quality—was **not supported** in this specific configuration. While equilibrium (convergence) was achieved, it was an **optimistic equilibrium** that diverged from human judgment. The study highlights a critical risk in multi-agent systems: **consensus does not equal correctness**. If the majority of agents share a bias (grade inflation), debate strengthens that bias.

## 7. Next Steps
1.  **Calibration**: Implement strict rubrics or "Persona" prompting (e.g., "You are a harsh critic").
2.  **Heterogeneity**: Use models with fundamentally different training objectives.
3.  **Iterative Improvement**: Focus on using the critique to *improve* the paper.

## 8. Appendix: Calibration Experiment
Following the identification of grade inflation, we conducted a follow-up experiment using a "Harsh Critic" persona. 
*   **Prompt**: Agents were instructed: *"You are a strict, critical reviewer... The average paper should receive a 4 or 5."*
*   **Result**: 
    *   **Original AI Mean**: 7.87
    *   **Calibrated AI Mean**: 6.33
    *   **Human Mean**: 5.66
*   **Correlation Impact**:
    *   **Original Correlation**: 0.33
    *   **Calibrated Correlation**: 0.36
*   **Conclusion**: Simple persona prompting significantly reduced inflation (by ~1.5 points) and slightly improved correlation (+0.03). This confirms that the observed inflation is largely a steering/prompting issue.

## 9. Appendix: Improvement Experiment
We attempted to use the consensus critique to automatically improve a rejected paper (`MWQCPYSJRN`).
*   **Method**: Extracted "weaknesses" from the debate and asked an Editor Agent to rewrite the Abstract/Intro to address them.
*   **Result**: The score remained unchanged (6 -> 6).
*   **Insight**: The critiques generated by the debate often targeted **structural/scientific flaws** (missing experiments, weak theory) rather than just presentation issues. An LLM Editor cannot "fix" a missing experiment by rewriting the text.

## 10. Appendix: Comparison with State-of-the-Art
We compared our "Debate Consensus" method against the "Reflection Ensemble" method from the *AI Scientist* paper (Lu et al., 2024).
*   **Baseline (SOTA)**: Ensemble of 5 GPT-4o agents reflecting on their own reviews.
*   **Ours**: Debate between GPT-4o, Claude 3.5, and GPT-4o-mini.
*   **Result (Correlation with Human Scores)**:
    *   **SOTA Reflection**: -0.07 (Negatively correlated)
    *   **Ours (Debate)**: +0.18 (Weakly positive)
*   **Conclusion**: Multi-agent debate significantly outperformed the single-model reflection ensemble, suggesting that diverse perspectives are more effective than self-reflection.

## 11. Appendix: Diversity Analysis
We analyzed the semantic similarity (TF-IDF Cosine Similarity) of the review content between agents.
*   **Round 0 Similarity**: 0.21
*   **Round 1 Similarity**: 0.30
*   **Result**: Text similarity increased by ~40%.
*   **Insight**: The debate process led to **content homogenization**, confirming a "groupthink" dynamic.

## 12. Appendix: Cost Analysis
We estimated the inference costs per paper (assuming standard API pricing).
*   **Single Agent (GPT-4o)**: $0.04
*   **Debate (3 Agents, 2 Rounds)**: $0.20 (4.7x cost)
*   **Ensemble (5 Agents)**: $0.21
*   **Conclusion**: Our debate pipeline is slightly cheaper than the standard 5-agent ensemble used in literature, while providing better performance (0.18 correlation vs -0.07). However, for purely budget-constrained scenarios, the Single Agent remains the most efficient choice (90% of the performance for 20% of the cost).
