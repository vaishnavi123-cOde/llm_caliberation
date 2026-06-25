# Reproducibility

## Environment

- Python 3.10 or newer is recommended.
- Install dependencies with `pip install -r requirements.txt`.
- The research artifacts can be regenerated without API keys if `outputs/results_groq.csv` and `outputs/results_gemini.csv` are present.

## Data Files

The analysis uses only:

- `outputs/results_groq.csv`
- `outputs/results_gemini.csv`
- `data/dataset.py`

## Reproducing Saved-Output Analysis

Run:

```bash
bash reproduce_experiment.sh
```

This regenerates category metrics, significance tests, error analysis, visualizations, markdown reports, and `report/paper.pdf`.

## Re-running Model Evaluation

To rerun the live experiment, set provider API keys and run:

```bash
python pipeline.py --models groq gemini --num-questions 300
python research_quality_analysis.py
```

Provider-side model updates may produce different outputs, so archived CSVs should be retained for exact replication.
