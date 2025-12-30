# Resources Catalog

## Summary
This document catalogs all resources gathered for the "AI Reviewing Equilibrium" research project.

## Papers
Total papers downloaded: 5

| Title | Authors | Year | File |
|-------|---------|------|------|
| ReviewerGPT | Liu & Shah | 2023 | `papers/2306.00622_ReviewerGPT.pdf` |
| The AI Scientist | Lu et al. | 2024 | `papers/2408.06292_AI_Scientist.pdf` |
| The AI Scientist v2 | Yamada et al. | 2025 | `papers/2504.08066_AI_Scientist_v2.pdf` |
| MMReview | Gao et al. | 2025 | `papers/2508.14146_MMReview.pdf` |
| Multiagent Debate | Du et al. | 2023 | `papers/2305.14325_Multiagent_Debate.pdf` |

## Datasets
Total datasets prepared: 2

| Name | Source | Content | Location |
|------|--------|---------|----------|
| AI-Scientist ICLR | SakanaAI | ICLR ratings & parsed papers | `datasets/AI-Scientist-ICLR/` |
| ReviewerGPT NeurIPS | ReviewerGPT | Checklist & error data | `datasets/ReviewerGPT-NeurIPS/` |

## Code Repositories
Total repositories cloned: 4

| Name | Purpose | Location |
|------|---------|----------|
| ReviewerGPT | Baseline error detection | `code/ReviewerGPT/` |
| AI-Scientist | Automated review pipeline | `code/AI-Scientist/` |
| AI-Scientist-v2 | VLM review pipeline | `code/AI-Scientist-v2/` |
| MultiAgentDebate | Debate methodology | `code/MultiAgentDebate/` |

## Resource Gathering Notes
-   **Challenge**: Large HuggingFace datasets for peer review (e.g., `Review-5K`) were gated or had script issues.
-   **Workaround**: Extracted relevant datasets directly from the `AI-Scientist` and `ReviewerGPT` codebases, which contain high-quality, task-specific data.
-   **Gap**: The `MultiAgentDebate` repo seems to be the website source; the core logic might need to be re-implemented or found in the `AI-Scientist` (which uses similar concepts) or inferred from the paper.

## Recommendations for Experiment Design
1.  **Primary Dataset**: `datasets/AI-Scientist-ICLR` provides a realistic benchmark for matching human review scores.
2.  **Baselines**: Use the `AI-Scientist` single-agent reviewer (GPT-4o) as the baseline.
3.  **Experiment**: Implement a multi-agent wrapper around the `AI-Scientist` reviewer function to test if "Debate" (consensus) improves the correlation with human scores compared to the single agent.
