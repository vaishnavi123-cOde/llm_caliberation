# Related Work

## Guo et al. (2017), "On Calibration of Modern Neural Networks"

Problem: Modern neural networks can be accurate while producing poorly calibrated probabilities.

Methodology: The paper evaluates calibration with reliability diagrams and Expected Calibration Error, and studies post-hoc calibration methods such as temperature scaling.

Limitations: The work focuses on conventional classifiers rather than self-reported natural-language confidence from LLMs.

Project difference: This project applies the same calibration vocabulary to API LLM outputs and model-verbalized confidence, not softmax probabilities.

Source: https://arxiv.org/abs/1706.04599

## Naeini et al. (2015), "Obtaining Well Calibrated Probabilities Using Bayesian Binning"

Problem: Classifier probability outputs are often miscalibrated even when classification accuracy is acceptable.

Methodology: The paper introduces Bayesian Binning into Quantiles and formalizes calibration evaluation with binned probability estimates.

Limitations: It predates current LLMs and assumes conventional probabilistic classifier outputs.

Project difference: This project uses ECE-style binned evaluation for LLM verbal confidence on multiple-choice QA.

Source: https://ojs.aaai.org/index.php/AAAI/article/view/9602

## Kadavath et al. (2022), "Language Models (Mostly) Know What They Know"

Problem: It is unclear whether language models can estimate whether their own answers are correct.

Methodology: The authors evaluate language models on answer correctness and confidence-related self-evaluation across tasks.

Limitations: Results depend on model family, prompting style, and task design.

Project difference: This project compares two deployed API models on a compact benchmark and adds category-level error and significance analysis.

Source: https://arxiv.org/abs/2207.05221

## Lin et al. (2022), "Teaching Models to Express Their Uncertainty in Words"

Problem: Users often need uncertainty communicated in language rather than hidden in logits.

Methodology: The paper studies how models express calibrated uncertainty through natural-language statements.

Limitations: Natural-language uncertainty remains prompt-sensitive and can differ from actual correctness probabilities.

Project difference: This project elicits numeric confidence percentages and evaluates them with reliability diagrams and ECE.

Source: https://arxiv.org/abs/2205.14334

## Xiong et al. (2023), "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs"

Problem: Confidence elicitation for LLMs is difficult because verbalized probabilities can be unstable and miscalibrated.

Methodology: The paper compares elicitation strategies and evaluates confidence quality across LLM tasks.

Limitations: Findings vary by prompt, model, and benchmark; no single elicitation method solves calibration.

Project difference: This project keeps a simple confidence-percentage prompt and focuses on a transparent, reproducible two-model comparison.

Source: https://arxiv.org/abs/2306.13063

## Zhang et al. (2024), "Calibrating the Confidence of Large Language Models by Eliciting Fidelity"

Problem: RLHF-aligned language models may express confidence that is higher than their empirical correctness.

Methodology: The paper decomposes confidence into question uncertainty and answer fidelity, then evaluates a plug-and-play confidence estimation method on multiple-choice QA datasets.

Limitations: The approach introduces additional elicitation structure and evaluation assumptions, and results may vary across model families and task domains.

Project difference: This project does not introduce a new calibration method; it audits saved Gemini and Groq outputs with standard empirical calibration metrics and significance testing.

Source: https://arxiv.org/abs/2404.02655

## How This Project Differs Overall

Most prior work studies either classifier probabilities, large benchmark suites, or confidence elicitation methods in isolation. This project is narrower but practical: it takes real saved Gemini and Groq outputs, reports category-specific calibration, tests whether model differences are statistically significant, and provides reproducible artifacts for a student-scale empirical study.
