# Statistical Significance Analysis

All tests use the existing paired outputs in `outputs/results_groq.csv` and `outputs/results_gemini.csv`.

## McNemar's Test

McNemar's test is the most appropriate accuracy comparison here because both models answered the same questions.

| Outcome | Count |
|---|---:|
| Both correct | 107 |
| Both incorrect | 32 |
| Groq correct, Gemini incorrect | 95 |
| Gemini correct, Groq incorrect | 66 |

Statistic: 4.8696  
p-value: 0.027024  
Significant at alpha = 0.05: Yes

## Chi-Square Test

This treats the two model result sets as two accuracy proportions.

| Model | Correct | Incorrect |
|---|---:|---:|
| Groq | 202 | 98 |
| Gemini | 173 | 127 |

Statistic: 5.5751  
p-value: 0.018218  
Significant at alpha = 0.05: Yes

## Bootstrap Confidence Intervals

Non-parametric paired bootstrap with 10000 resamples.

| Quantity | Mean Difference (Groq - Gemini) | 95% CI |
|---|---:|---:|
| Accuracy | 0.0967 | [0.0167, 0.1767] |
| ECE | -0.0528 | [-0.1348, 0.0250] |
| Average confidence | 0.0378 | [0.0216, 0.0540] |

## Conclusion

The observed Groq-Gemini accuracy difference is statistically significant across all three criteria at alpha = 0.05. The conclusion is based only on the saved Gemini and Groq outputs.
