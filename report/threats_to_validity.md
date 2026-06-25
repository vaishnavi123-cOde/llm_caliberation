# Threats to Validity

## Dataset Limitations

The dataset contains 300 multiple-choice questions from curated categories. This improves control and interpretability, but it may not reflect the distribution, ambiguity, or adversarial structure of real user queries. Some categories have many more examples than others, so aggregate metrics are influenced heavily by the largest categories.

## Model Selection Limitations

The study compares only Groq-hosted Llama 3.3 70B and Gemini 2.0 Flash. The results should not be generalized to all open-weight or proprietary LLMs. Provider-side model updates can also change behavior over time, so the outputs are a snapshot of the specific run saved in `outputs/`.

## Confidence Extraction Limitations

Confidence is self-reported by the model as text and parsed from the generated response. This differs from calibrated probability from model logits. The confidence prompt may induce stylistic confidence rather than epistemic uncertainty, and missing or malformed confidence strings can bias estimates.

## Evaluation Limitations

Correctness is evaluated against a single answer key. Multiple-choice scoring hides partial knowledge and does not capture reasoning quality. Statistical tests assume the saved question set is representative of a broader population, which is only partially justified for this curated benchmark.
