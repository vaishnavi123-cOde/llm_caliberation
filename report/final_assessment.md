# Final Assessment

## Undergraduate Research Quality Score: 8/10

The project has a clear research question, real model outputs, standard calibration metrics, category-level analysis, significance testing, error analysis, and reproducibility notes. The main limits are dataset size, curated question construction, and reliance on self-reported confidence.

## Workshop Paper Readiness: 6/10

The project is close to a workshop poster or short-paper submission, especially as an empirical study. To improve readiness, it needs a larger or externally recognized benchmark, stronger related-work positioning, cleaner confidence elicitation validation, and possibly more than two model snapshots.

## Student Research Internship Value: 9/10

This is strong internship material because it demonstrates end-to-end experimental design: data collection, metric implementation, visualization, statistical testing, limitations, and reproducibility. The saved outputs also make the claims auditable.

## Evidence Used

Overall metrics:

| model   | category      |   n_questions |   accuracy |   average_confidence |    ece |   overconfidence |
|:--------|:--------------|--------------:|-----------:|---------------------:|-------:|-----------------:|
| groq    | All Questions |           300 |     0.6733 |               0.8769 | 0.2076 |           0.8613 |
| gemini  | All Questions |           300 |     0.5767 |               0.8391 | 0.2624 |           0.868  |

Category metrics:

| model   | category               |   n_questions |   accuracy |   average_confidence |    ece |   overconfidence |
|:--------|:-----------------------|--------------:|-----------:|---------------------:|-------:|-----------------:|
| groq    | Factual Knowledge      |           228 |     0.6754 |               0.883  | 0.2103 |           0.8654 |
| groq    | Mathematical Reasoning |            39 |     0.641  |               0.8604 | 0.2194 |           0.8474 |
| groq    | Logical Reasoning      |            33 |     0.697  |               0.8546 | 0.2175 |           0.8498 |
| gemini  | Factual Knowledge      |           228 |     0.5921 |               0.8452 | 0.253  |           0.8792 |
| gemini  | Mathematical Reasoning |            39 |     0.5128 |               0.8235 | 0.3107 |           0.8325 |
| gemini  | Logical Reasoning      |            33 |     0.5455 |               0.8159 | 0.2821 |           0.8439 |

McNemar p-value: 0.027024  
Bootstrap accuracy difference CI: [0.0167, 0.1767]
