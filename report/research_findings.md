# Research Findings

## Key Findings

- Groq achieved higher accuracy than Gemini on the saved evaluation outputs: 0.6733 vs 0.5767.
- Both models were overconfident: Groq average confidence was 0.8769 at 0.6733 accuracy, while Gemini average confidence was 0.8391 at 0.5767 accuracy.
- Groq had lower ECE than Gemini: 0.2076 vs 0.2624.
- McNemar's test p-value was 0.027024; the paired accuracy difference is statistically significant at alpha = 0.05.
- The paired bootstrap 95% CI for accuracy difference (Groq - Gemini) was [0.0167, 0.1767].

## Unexpected Findings

- Incorrect answers often still had high confidence. Average confidence on incorrect answers was 0.8613 for Groq and 0.8680 for Gemini.
- Calibration differed by research category, so a single overall ECE hides category-specific failure modes.

## Model Strengths

| model   | category          |   n_questions |   accuracy |    ece |
|:--------|:------------------|--------------:|-----------:|-------:|
| gemini  | Factual Knowledge |           228 |     0.5921 | 0.253  |
| groq    | Logical Reasoning |            33 |     0.697  | 0.2175 |

## Model Weaknesses

| model   | category               |   n_questions |   accuracy |    ece |
|:--------|:-----------------------|--------------:|-----------:|-------:|
| gemini  | Mathematical Reasoning |            39 |     0.5128 | 0.3107 |
| groq    | Mathematical Reasoning |            39 |     0.641  | 0.2194 |

## Error Profile

| model   | error_type                |   count |
|:--------|:--------------------------|--------:|
| gemini  | Calculation Error         |      12 |
| gemini  | Confidence Miscalibration |      77 |
| gemini  | Hallucination             |      27 |
| gemini  | Logical Error             |      11 |
| groq    | Calculation Error         |       6 |
| groq    | Confidence Miscalibration |      63 |
| groq    | Hallucination             |      26 |
| groq    | Logical Error             |       3 |

## Practical Implications

- Raw self-reported confidence should not be used as a decision threshold without calibration.
- Groq is stronger on this exact benchmark, but the small dataset and curated question set limit external generalization.
- Category-level calibration should be reported when deploying models in domain-specific settings.
