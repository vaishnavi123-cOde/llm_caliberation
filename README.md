# LLM Calibration Study

A comparative evaluation of calibration quality in Groq (Llama 3.3 70B) and Gemini 2.0 Flash across 300 multiple-choice questions spanning 11 knowledge domains.

## Overview

This project measures how well language models know when they are wrong. It uses standard calibration metrics -- accuracy, average confidence, Expected Calibration Error (ECE), and overconfidence score -- to quantify the alignment between a model's self-reported confidence and its actual correctness.

## Results Summary

| Metric              | Groq (Llama 3.3 70B) | Gemini 2.0 Flash |
|---------------------|-----------------------|-------------------|
| Accuracy            | 0.6733                | 0.5767            |
| Average Confidence  | 0.8769                | 0.8391            |
| ECE                 | 0.2076                | 0.2624            |
| Overconfidence      | 0.8613                | 0.8680            |

Both models exhibit significant overconfidence. Groq achieves higher accuracy and lower ECE. The 90-100% confidence bin for Gemini achieves only 28% accuracy, indicating that the model is most unreliable precisely when it expresses highest confidence.

## Research Artifacts

- `category_metrics.csv` -- accuracy, confidence, ECE, and overconfidence per research category (Factual Knowledge, Mathematical Reasoning, Logical Reasoning)
- `error_analysis.csv` -- error classification (hallucination, calculation error, logical error, incomplete answer, confidence miscalibration) for every incorrect response
- `significance_analysis.md` -- McNemar's test, chi-square test, and bootstrap confidence intervals comparing both models
- `research_findings.md` -- key findings, model strengths and weaknesses, practical implications
- `threats_to_validity.md` -- academic discussion of dataset, model, and evaluation limitations
- `related_work.md` -- literature review covering Guo et al., Naeini et al., Kadavath et al., and others
- `paper.pdf` -- publication-style report with sections from Abstract to Future Work
- `REPRODUCIBILITY.md` -- instructions for reproducing all results
- `AUDIT_REPORT.md` -- complete audit confirming no mock or simulated data was used
- `REAL_RESULTS_VERIFICATION.md` -- evidence that all outputs are from real API calls

## Setup

```bash
pip install -r requirements.txt
```

## API Keys

Groq and Gemini API keys are required to re-run model evaluation.

```bash
export GROQ_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"
```

On Windows PowerShell:

```powershell
$env:GROQ_API_KEY = "your-key-here"
$env:GEMINI_API_KEY = "your-key-here"
```

## Usage

```bash
# Run full evaluation on all models
python pipeline.py

# Run on specific models
python pipeline.py --models groq gemini

# Change number of questions
python pipeline.py --num-questions 300

# Generate research-quality analysis from saved outputs
python research_quality_analysis.py
```

## Project Structure

```
├── pipeline.py                  # Main evaluation pipeline
├── research_quality_analysis.py # Statistical tests, error analysis, plots, paper
├── config.py                    # Model and output configuration
├── generate_report.py           # Report generation
├── data/
│   └── dataset.py               # 300-question benchmark
├── models/
│   ├── base.py                  # Abstract model client
│   ├── gemini.py                # Gemini API client
│   └── groq.py                  # Groq API client
├── metrics/
│   └── calibration.py           # ECE, overconfidence, temperature scaling
├── visualization/
│   └── plots.py                 # Reliability diagrams and comparison plots
├── outputs/                     # Result CSVs, plots
└── report/                      # Generated reports and paper
```

## How It Works

Each question is formatted as a zero-shot prompt asking the model to answer with a letter and a confidence percentage. Responses are parsed to extract the chosen answer and numerical confidence. Metrics are computed across 10 equally-spaced confidence bins using standard calibration literature conventions.

## Limitations

- 300 questions from a curated set may not reflect real-world distribution
- Confidence is self-reported as text, not derived from model logits
- Only two model snapshots are compared at a single point in time
- Multiple-choice scoring does not capture partial knowledge

## License

This project is for research and educational purposes.
