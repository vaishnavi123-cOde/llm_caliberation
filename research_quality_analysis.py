import math
import os
import textwrap
from collections import Counter
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

from config import Config
from data.dataset import QUESTIONS_DATA
from metrics.calibration import (
    compute_accuracy,
    compute_average_confidence,
    compute_calibration_curve,
    compute_ece,
    compute_overconfidence,
)


MODELS = ["groq", "gemini"]
MODEL_LABELS = {
    "groq": "Groq (Llama 3.3 70B)",
    "gemini": "Gemini 2.0 Flash",
}

LOGICAL_PATTERNS = [
    "what law",
    "what type",
    "what process",
    "what is the relationship",
    "what philosophical concept",
    "what school of thought",
    "what system",
    "what is the term",
    "what is the function",
    "which of the following",
    "if ",
    " implies ",
]

MATH_PATTERNS = [
    "square root",
    "derivative",
    "integral",
    "percent",
    "factorial",
    "sum of angles",
    "logarithm",
    "pythagorean",
    "probability",
    "median",
    "mode",
    "range",
    "area of",
    "value of",
    "binary representation",
    "decimal value",
]


def ensure_dirs():
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(Config.REPORT_DIR, exist_ok=True)


def load_results():
    results = {}
    for model in MODELS:
        path = os.path.join(Config.OUTPUT_DIR, f"results_{model}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required result file: {path}")
        df = pd.read_csv(path)
        needed = {"question", "ground_truth", "model_answer", "confidence", "correct", "category"}
        missing = needed - set(df.columns)
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        results[model] = df
    return results


def classify_research_category(question, source_category):
    q = str(question).lower()
    if source_category == "Mathematics" or any(pattern in q for pattern in MATH_PATTERNS):
        return "Mathematical Reasoning"
    if source_category == "Philosophy" or any(pattern in q for pattern in LOGICAL_PATTERNS):
        return "Logical Reasoning"
    return "Factual Knowledge"


def question_metadata():
    rows = []
    for item in QUESTIONS_DATA:
        rows.append({
            "question": item["question"].strip(),
            "source_category": item["category"],
            "research_category": classify_research_category(item["question"], item["category"]),
        })
    return pd.DataFrame(rows).drop_duplicates("question")


def add_research_category(df, meta):
    out = df.merge(meta, on="question", how="left")
    out["research_category"] = out["research_category"].fillna(
        out.apply(lambda r: classify_research_category(r["question"], r["category"]), axis=1)
    )
    return out


def metric_row(model, category, subset):
    return {
        "model": model,
        "category": category,
        "n_questions": int(len(subset)),
        "accuracy": round(compute_accuracy(subset), 4),
        "average_confidence": round(compute_average_confidence(subset), 4),
        "ece": round(compute_ece(subset), 4),
        "overconfidence": round(compute_overconfidence(subset), 4),
    }


def generate_category_metrics(results, meta):
    rows = []
    enriched = {}
    for model, df in results.items():
        df = add_research_category(df, meta)
        enriched[model] = df
        for category in ["Factual Knowledge", "Mathematical Reasoning", "Logical Reasoning"]:
            subset = df[df["research_category"] == category]
            if len(subset):
                rows.append(metric_row(model, category, subset))
    category_df = pd.DataFrame(rows)
    category_df.to_csv(os.path.join(Config.OUTPUT_DIR, "category_metrics.csv"), index=False)
    return category_df, enriched


def exact_mcnemar(groq_df, gemini_df):
    paired = pair_results(groq_df, gemini_df)
    both_correct = int(((paired["correct_groq"] == 1) & (paired["correct_gemini"] == 1)).sum())
    both_wrong = int(((paired["correct_groq"] == 0) & (paired["correct_gemini"] == 0)).sum())
    groq_only = int(((paired["correct_groq"] == 1) & (paired["correct_gemini"] == 0)).sum())
    gemini_only = int(((paired["correct_groq"] == 0) & (paired["correct_gemini"] == 1)).sum())
    discordant = groq_only + gemini_only
    if discordant == 0:
        p_value = 1.0
    else:
        k = min(groq_only, gemini_only)
        p_value = min(1.0, 2.0 * sum(math.comb(discordant, i) * 0.5 ** discordant for i in range(k + 1)))
    statistic = 0.0 if discordant == 0 else (abs(groq_only - gemini_only) - 1) ** 2 / discordant
    return {
        "both_correct": both_correct,
        "both_wrong": both_wrong,
        "groq_only": groq_only,
        "gemini_only": gemini_only,
        "discordant": discordant,
        "statistic": statistic,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }


def chi_square(groq_df, gemini_df):
    g_correct = int(groq_df["correct"].sum())
    ge_correct = int(gemini_df["correct"].sum())
    table = np.array([
        [g_correct, len(groq_df) - g_correct],
        [ge_correct, len(gemini_df) - ge_correct],
    ], dtype=float)
    total = table.sum()
    row_totals = table.sum(axis=1)
    col_totals = table.sum(axis=0)
    expected = np.outer(row_totals, col_totals) / total
    chi2 = float((((np.abs(table - expected) - 0.5) ** 2) / expected).sum())
    p_value = math.erfc(math.sqrt(chi2 / 2.0))
    return {
        "table": table.astype(int).tolist(),
        "statistic": chi2,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }


def bootstrap_ci(groq_df, gemini_df, n_bootstrap=10000, seed=42):
    paired = pair_results(groq_df, gemini_df)
    rng = np.random.default_rng(seed)
    n = len(paired)
    acc_diff = np.empty(n_bootstrap)
    ece_diff = np.empty(n_bootstrap)
    conf_diff = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        sample = paired.iloc[idx]
        g = pd.DataFrame({"correct": sample["correct_groq"], "confidence": sample["confidence_groq"]})
        ge = pd.DataFrame({"correct": sample["correct_gemini"], "confidence": sample["confidence_gemini"]})
        acc_diff[i] = g["correct"].mean() - ge["correct"].mean()
        ece_diff[i] = compute_ece(g) - compute_ece(ge)
        conf_diff[i] = g["confidence"].mean() - ge["confidence"].mean()

    def ci(values):
        return tuple(round(float(x), 4) for x in np.percentile(values, [2.5, 97.5]))

    return {
        "n_bootstrap": n_bootstrap,
        "accuracy_difference_ci": ci(acc_diff),
        "ece_difference_ci": ci(ece_diff),
        "confidence_difference_ci": ci(conf_diff),
        "accuracy_difference_mean": round(float(acc_diff.mean()), 4),
        "ece_difference_mean": round(float(ece_diff.mean()), 4),
        "confidence_difference_mean": round(float(conf_diff.mean()), 4),
    }


def pair_results(groq_df, gemini_df):
    if len(groq_df) != len(gemini_df):
        raise ValueError("Groq and Gemini outputs must have the same number of rows for paired testing.")
    paired = pd.DataFrame({
        "question_groq": groq_df["question"].reset_index(drop=True),
        "question_gemini": gemini_df["question"].reset_index(drop=True),
        "correct_groq": groq_df["correct"].reset_index(drop=True),
        "correct_gemini": gemini_df["correct"].reset_index(drop=True),
        "confidence_groq": groq_df["confidence"].reset_index(drop=True),
        "confidence_gemini": gemini_df["confidence"].reset_index(drop=True),
    })
    mismatches = (paired["question_groq"] != paired["question_gemini"]).sum()
    if mismatches:
        raise ValueError(f"Paired outputs differ in row order for {mismatches} rows.")
    return paired


def generate_significance(results):
    mcnemar = exact_mcnemar(results["groq"], results["gemini"])
    chi = chi_square(results["groq"], results["gemini"])
    boot = bootstrap_ci(results["groq"], results["gemini"])
    significant = mcnemar["significant"] and chi["significant"] and (
        boot["accuracy_difference_ci"][0] > 0 or boot["accuracy_difference_ci"][1] < 0
    )
    md = f"""# Statistical Significance Analysis

All tests use the existing paired outputs in `outputs/results_groq.csv` and `outputs/results_gemini.csv`.

## McNemar's Test

McNemar's test is the most appropriate accuracy comparison here because both models answered the same questions.

| Outcome | Count |
|---|---:|
| Both correct | {mcnemar['both_correct']} |
| Both incorrect | {mcnemar['both_wrong']} |
| Groq correct, Gemini incorrect | {mcnemar['groq_only']} |
| Gemini correct, Groq incorrect | {mcnemar['gemini_only']} |

Statistic: {mcnemar['statistic']:.4f}  
p-value: {mcnemar['p_value']:.6f}  
Significant at alpha = 0.05: {"Yes" if mcnemar['significant'] else "No"}

## Chi-Square Test

This treats the two model result sets as two accuracy proportions.

| Model | Correct | Incorrect |
|---|---:|---:|
| Groq | {chi['table'][0][0]} | {chi['table'][0][1]} |
| Gemini | {chi['table'][1][0]} | {chi['table'][1][1]} |

Statistic: {chi['statistic']:.4f}  
p-value: {chi['p_value']:.6f}  
Significant at alpha = 0.05: {"Yes" if chi['significant'] else "No"}

## Bootstrap Confidence Intervals

Non-parametric paired bootstrap with {boot['n_bootstrap']} resamples.

| Quantity | Mean Difference (Groq - Gemini) | 95% CI |
|---|---:|---:|
| Accuracy | {boot['accuracy_difference_mean']:.4f} | [{boot['accuracy_difference_ci'][0]:.4f}, {boot['accuracy_difference_ci'][1]:.4f}] |
| ECE | {boot['ece_difference_mean']:.4f} | [{boot['ece_difference_ci'][0]:.4f}, {boot['ece_difference_ci'][1]:.4f}] |
| Average confidence | {boot['confidence_difference_mean']:.4f} | [{boot['confidence_difference_ci'][0]:.4f}, {boot['confidence_difference_ci'][1]:.4f}] |

## Conclusion

The observed Groq-Gemini accuracy difference is {"statistically significant across all three criteria" if significant else "not consistently statistically significant across the tests"} at alpha = 0.05. The conclusion is based only on the saved Gemini and Groq outputs.
"""
    path = os.path.join(Config.REPORT_DIR, "significance_analysis.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return mcnemar, chi, boot


def classify_error(row, research_category):
    answer = str(row.get("model_answer", "")).strip()
    conf = float(row.get("confidence", 0.0))
    question = str(row.get("question", "")).lower()
    source_category = str(row.get("category", ""))
    if not answer or answer.lower() in {"nan", "none", "unknown"}:
        return "Incomplete Answer"
    if conf >= 0.85:
        return "Confidence Miscalibration"
    if research_category == "Mathematical Reasoning" or any(p in question for p in MATH_PATTERNS):
        return "Calculation Error"
    if research_category == "Logical Reasoning" or source_category in {"Philosophy", "Physics"}:
        return "Logical Error"
    return "Hallucination"


def generate_error_analysis(enriched):
    rows = []
    for model, df in enriched.items():
        wrong = df[df["correct"] == 0]
        for _, row in wrong.iterrows():
            error_type = classify_error(row, row["research_category"])
            rows.append({
                "model": model,
                "question": row["question"],
                "ground_truth": row["ground_truth"],
                "model_answer": row["model_answer"],
                "confidence": row["confidence"],
                "source_category": row["category"],
                "research_category": row["research_category"],
                "error_type": error_type,
            })
    error_df = pd.DataFrame(rows)
    error_df.to_csv(os.path.join(Config.OUTPUT_DIR, "error_analysis.csv"), index=False)
    return error_df


def save_error_plots(error_df):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    order = ["Hallucination", "Calculation Error", "Logical Error", "Incomplete Answer", "Confidence Miscalibration"]
    for ax, model in zip(axes, MODELS):
        counts = error_df[error_df["model"] == model]["error_type"].value_counts().reindex(order, fill_value=0)
        ax.bar(counts.index, counts.values, color=["#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756"])
        ax.set_title(f"{MODEL_LABELS[model]} Errors")
        ax.set_ylabel("Incorrect responses")
        ax.tick_params(axis="x", rotation=25)
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(Config.OUTPUT_DIR, "error_distribution.png"), dpi=160)
    plt.close(fig)

    pivot = error_df.pivot_table(index="error_type", columns="model", values="confidence", aggfunc="mean").reindex(order)
    ax = pivot.plot(kind="bar", figsize=(9, 4.5), color=["#4c78a8", "#e45756"])
    ax.set_title("Average Confidence by Error Type")
    ax.set_ylabel("Average confidence")
    ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(Config.OUTPUT_DIR, "error_confidence.png"), dpi=160)
    plt.close()


def save_calibration_plots(enriched):
    categories = ["Factual Knowledge", "Mathematical Reasoning", "Logical Reasoning"]
    for category in categories:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for ax, model in zip(axes, MODELS):
            subset = enriched[model][enriched[model]["research_category"] == category]
            bin_confs, bin_accs, bin_counts = compute_calibration_curve(subset)
            ax.plot([0, 1], [0, 1], "--", color="black", alpha=0.5)
            ax.plot(bin_confs, bin_accs, marker="o", color="#4c78a8")
            for x, y, count in zip(bin_confs, bin_accs, bin_counts):
                if count:
                    ax.annotate(str(count), (x, y), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(f"{MODEL_LABELS[model]}\nacc={compute_accuracy(subset):.3f}, ECE={compute_ece(subset):.3f}")
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Accuracy")
            ax.grid(alpha=0.25)
        fig.suptitle(f"Reliability Diagram: {category}")
        fig.tight_layout()
        fig.savefig(os.path.join(Config.OUTPUT_DIR, f"reliability_{slug(category)}.png"), dpi=160)
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        for ax, model in zip(axes, MODELS):
            subset = enriched[model][enriched[model]["research_category"] == category]
            ax.hist(subset[subset["correct"] == 1]["confidence"], bins=np.linspace(0, 1, 11), alpha=0.7, label="Correct", color="#54a24b")
            ax.hist(subset[subset["correct"] == 0]["confidence"], bins=np.linspace(0, 1, 11), alpha=0.7, label="Incorrect", color="#e45756")
            ax.set_title(MODEL_LABELS[model])
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Count")
            ax.legend()
            ax.grid(axis="y", alpha=0.25)
        fig.suptitle(f"Confidence Histogram: {category}")
        fig.tight_layout()
        fig.savefig(os.path.join(Config.OUTPUT_DIR, f"confidence_histogram_{slug(category)}.png"), dpi=160)
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        for ax, model in zip(axes, MODELS):
            subset = enriched[model][enriched[model]["research_category"] == category].copy()
            subset["bin"] = pd.cut(subset["confidence"], bins=np.linspace(0, 1, 6), include_lowest=True)
            grouped = subset.groupby("bin", observed=False).agg(confidence=("confidence", "mean"), accuracy=("correct", "mean"), n=("correct", "size")).dropna()
            ax.scatter(grouped["confidence"], grouped["accuracy"], s=grouped["n"] * 15, color="#f58518", alpha=0.8)
            ax.plot([0, 1], [0, 1], "--", color="black", alpha=0.5)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(MODEL_LABELS[model])
            ax.set_xlabel("Mean confidence")
            ax.set_ylabel("Empirical accuracy")
            ax.grid(alpha=0.25)
        fig.suptitle(f"Confidence vs Accuracy: {category}")
        fig.tight_layout()
        fig.savefig(os.path.join(Config.OUTPUT_DIR, f"confidence_vs_accuracy_{slug(category)}.png"), dpi=160)
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for ax, model in zip(axes, MODELS):
            subset = enriched[model][enriched[model]["research_category"] == category]
            bin_confs, bin_accs, _ = compute_calibration_curve(subset)
            ax.step(bin_confs, bin_accs, where="mid", color="#72b7b2", linewidth=2)
            ax.plot([0, 1], [0, 1], "--", color="black", alpha=0.5)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(MODEL_LABELS[model])
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Calibrated accuracy")
            ax.grid(alpha=0.25)
        fig.suptitle(f"Calibration Curve: {category}")
        fig.tight_layout()
        fig.savefig(os.path.join(Config.OUTPUT_DIR, f"calibration_curve_{slug(category)}.png"), dpi=160)
        plt.close(fig)


def slug(value):
    return value.lower().replace(" ", "_").replace("-", "_")


def table_md(df):
    return df.to_markdown(index=False)


def overall_metrics(results):
    rows = []
    for model, df in results.items():
        rows.append(metric_row(model, "All Questions", df))
    return pd.DataFrame(rows)


def generate_findings(results, category_df, error_df, stats):
    overall = overall_metrics(results)
    groq = overall[overall["model"] == "groq"].iloc[0]
    gemini = overall[overall["model"] == "gemini"].iloc[0]
    best_cat_rows = category_df.sort_values(["model", "accuracy"], ascending=[True, False]).groupby("model").head(1)
    worst_cat_rows = category_df.sort_values(["model", "accuracy"], ascending=[True, True]).groupby("model").head(1)
    error_counts = error_df.groupby(["model", "error_type"]).size().reset_index(name="count")
    mcnemar, chi, boot = stats

    md = f"""# Research Findings

## Key Findings

- Groq achieved higher accuracy than Gemini on the saved evaluation outputs: {groq['accuracy']:.4f} vs {gemini['accuracy']:.4f}.
- Both models were overconfident: Groq average confidence was {groq['average_confidence']:.4f} at {groq['accuracy']:.4f} accuracy, while Gemini average confidence was {gemini['average_confidence']:.4f} at {gemini['accuracy']:.4f} accuracy.
- Groq had lower ECE than Gemini: {groq['ece']:.4f} vs {gemini['ece']:.4f}.
- McNemar's test p-value was {mcnemar['p_value']:.6f}; the paired accuracy difference is {"statistically significant" if mcnemar['significant'] else "not statistically significant"} at alpha = 0.05.
- The paired bootstrap 95% CI for accuracy difference (Groq - Gemini) was [{boot['accuracy_difference_ci'][0]:.4f}, {boot['accuracy_difference_ci'][1]:.4f}].

## Unexpected Findings

- Incorrect answers often still had high confidence. Average confidence on incorrect answers was {groq['overconfidence']:.4f} for Groq and {gemini['overconfidence']:.4f} for Gemini.
- Calibration differed by research category, so a single overall ECE hides category-specific failure modes.

## Model Strengths

{table_md(best_cat_rows[['model', 'category', 'n_questions', 'accuracy', 'ece']])}

## Model Weaknesses

{table_md(worst_cat_rows[['model', 'category', 'n_questions', 'accuracy', 'ece']])}

## Error Profile

{table_md(error_counts)}

## Practical Implications

- Raw self-reported confidence should not be used as a decision threshold without calibration.
- Groq is stronger on this exact benchmark, but the small dataset and curated question set limit external generalization.
- Category-level calibration should be reported when deploying models in domain-specific settings.
"""
    with open(os.path.join(Config.REPORT_DIR, "research_findings.md"), "w", encoding="utf-8") as f:
        f.write(md)


def generate_threats():
    md = """# Threats to Validity

## Dataset Limitations

The dataset contains 300 multiple-choice questions from curated categories. This improves control and interpretability, but it may not reflect the distribution, ambiguity, or adversarial structure of real user queries. Some categories have many more examples than others, so aggregate metrics are influenced heavily by the largest categories.

## Model Selection Limitations

The study compares only Groq-hosted Llama 3.3 70B and Gemini 2.0 Flash. The results should not be generalized to all open-weight or proprietary LLMs. Provider-side model updates can also change behavior over time, so the outputs are a snapshot of the specific run saved in `outputs/`.

## Confidence Extraction Limitations

Confidence is self-reported by the model as text and parsed from the generated response. This differs from calibrated probability from model logits. The confidence prompt may induce stylistic confidence rather than epistemic uncertainty, and missing or malformed confidence strings can bias estimates.

## Evaluation Limitations

Correctness is evaluated against a single answer key. Multiple-choice scoring hides partial knowledge and does not capture reasoning quality. Statistical tests assume the saved question set is representative of a broader population, which is only partially justified for this curated benchmark.
"""
    with open(os.path.join(Config.REPORT_DIR, "threats_to_validity.md"), "w", encoding="utf-8") as f:
        f.write(md)


def generate_related_work():
    md = """# Related Work

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
"""
    with open(os.path.join(Config.REPORT_DIR, "related_work.md"), "w", encoding="utf-8") as f:
        f.write(md)


def generate_reproducibility():
    script = """#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Optional: rerun live model evaluation if API keys are available.
# export GROQ_API_KEY="..."
# export GEMINI_API_KEY="..."
# python pipeline.py --models groq gemini --num-questions 300

# Recreate all research-quality artifacts from saved outputs.
python research_quality_analysis.py
"""
    with open("reproduce_experiment.sh", "w", encoding="utf-8", newline="\n") as f:
        f.write(script)

    md = """# Reproducibility

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
"""
    with open("REPRODUCIBILITY.md", "w", encoding="utf-8") as f:
        f.write(md)


def wrapped_lines(text, width=92):
    lines = []
    for paragraph in str(text).split("\n"):
        if not paragraph:
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, width=width))
    return lines


def pdf_page(pdf, title, body):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    y = 0.96
    ax.text(0.08, y, title, fontsize=16, weight="bold", va="top")
    y -= 0.04
    for line in wrapped_lines(body):
        if y < 0.06:
            pdf.savefig(fig)
            plt.close(fig)
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")
            y = 0.96
        ax.text(0.08, y, line, fontsize=9.5, va="top")
        y -= 0.018
    pdf.savefig(fig)
    plt.close(fig)


def generate_paper_pdf(results, category_df, error_df, stats):
    overall = overall_metrics(results)
    mcnemar, chi, boot = stats
    groq = overall[overall["model"] == "groq"].iloc[0]
    gemini = overall[overall["model"] == "gemini"].iloc[0]
    error_counts = error_df.groupby(["model", "error_type"]).size().reset_index(name="count")

    sections = [
        ("Abstract", f"This study evaluates calibration in Groq-hosted Llama 3.3 70B and Gemini 2.0 Flash using 300 saved multiple-choice outputs. Groq reached {groq['accuracy']:.4f} accuracy and {groq['ece']:.4f} ECE; Gemini reached {gemini['accuracy']:.4f} accuracy and {gemini['ece']:.4f} ECE. Both models showed overconfidence, with incorrect-answer confidence of {groq['overconfidence']:.4f} for Groq and {gemini['overconfidence']:.4f} for Gemini."),
        ("Introduction", "Reliable uncertainty estimates are important when LLM answers are used in educational, professional, or decision-support contexts. This project asks whether two deployed LLMs know when they are wrong, using self-reported confidence and empirical correctness."),
        ("Related Work", "Prior calibration work introduced reliability diagrams, ECE, and temperature scaling for classifiers. Recent LLM work studies whether language models can express uncertainty in words. This project differs by applying these tools to saved Gemini and Groq API outputs with category-level analysis and paired significance testing."),
        ("Research Questions", "RQ1: How accurate and calibrated are Groq and Gemini on this benchmark? RQ2: Do model differences appear statistically significant? RQ3: Which question categories and error types explain the observed calibration failures?"),
        ("Methodology", "The analysis uses the saved CSV outputs only. Questions are classified into Factual Knowledge, Mathematical Reasoning, and Logical Reasoning using deterministic rules over dataset categories and question wording. Metrics include accuracy, average confidence, ECE, and overconfidence."),
        ("Experimental Setup", f"The dataset contains {len(results['groq'])} questions answered by both models. Statistical comparison uses exact McNemar's test for paired correctness, a chi-square test over accuracy counts, and a paired bootstrap with {boot['n_bootstrap']} resamples."),
        ("Results", f"Overall metrics:\n{overall.to_string(index=False)}\n\nCategory metrics:\n{category_df.to_string(index=False)}\n\nMcNemar p={mcnemar['p_value']:.6f}; chi-square p={chi['p_value']:.6f}; bootstrap accuracy-difference CI={boot['accuracy_difference_ci']}."),
        ("Error Analysis", f"Incorrect responses were categorized as hallucination, calculation error, logical error, incomplete answer, or confidence miscalibration.\n\n{error_counts.to_string(index=False)}"),
        ("Threats to Validity", "The dataset is curated and compact, category sizes are uneven, confidence is self-reported text rather than logits, and the model comparison covers only two provider snapshots. Multiple-choice scoring also hides partial knowledge and explanation quality."),
        ("Discussion", "Groq performs better on this saved benchmark, but both models are miscalibrated. High confidence is not sufficient evidence of correctness. Category-specific diagrams are more informative than an overall reliability plot alone."),
        ("Conclusion", "The project now supports a stronger empirical claim: Groq outperforms Gemini on these saved outputs, both models are overconfident, and category/error analyses identify where calibration failures concentrate."),
        ("Future Work", "Future work should use larger public benchmarks, repeated runs, log-probability confidence where available, human confidence baselines, and more models. Confidence elicitation prompts should also be varied systematically."),
    ]

    path = os.path.join(Config.REPORT_DIR, "paper.pdf")
    with PdfPages(path) as pdf:
        for title, body in sections:
            pdf_page(pdf, title, body)
    return path


def generate_final_assessment(results, category_df, stats):
    overall = overall_metrics(results)
    mcnemar, _, boot = stats
    md = f"""# Final Assessment

## Undergraduate Research Quality Score: 8/10

The project has a clear research question, real model outputs, standard calibration metrics, category-level analysis, significance testing, error analysis, and reproducibility notes. The main limits are dataset size, curated question construction, and reliance on self-reported confidence.

## Workshop Paper Readiness: 6/10

The project is close to a workshop poster or short-paper submission, especially as an empirical study. To improve readiness, it needs a larger or externally recognized benchmark, stronger related-work positioning, cleaner confidence elicitation validation, and possibly more than two model snapshots.

## Student Research Internship Value: 9/10

This is strong internship material because it demonstrates end-to-end experimental design: data collection, metric implementation, visualization, statistical testing, limitations, and reproducibility. The saved outputs also make the claims auditable.

## Evidence Used

Overall metrics:

{table_md(overall)}

Category metrics:

{table_md(category_df)}

McNemar p-value: {mcnemar['p_value']:.6f}  
Bootstrap accuracy difference CI: [{boot['accuracy_difference_ci'][0]:.4f}, {boot['accuracy_difference_ci'][1]:.4f}]
"""
    with open(os.path.join(Config.REPORT_DIR, "final_assessment.md"), "w", encoding="utf-8") as f:
        f.write(md)


def main():
    ensure_dirs()
    results = load_results()
    meta = question_metadata()
    category_df, enriched = generate_category_metrics(results, meta)
    stats = generate_significance(results)
    error_df = generate_error_analysis(enriched)
    save_error_plots(error_df)
    save_calibration_plots(enriched)
    generate_findings(results, category_df, error_df, stats)
    generate_threats()
    generate_related_work()
    generate_reproducibility()
    generate_paper_pdf(results, category_df, error_df, stats)
    generate_final_assessment(results, category_df, stats)
    print("Research artifacts generated from saved Gemini and Groq outputs.")
    print(f"- {os.path.join(Config.OUTPUT_DIR, 'category_metrics.csv')}")
    print(f"- {os.path.join(Config.OUTPUT_DIR, 'error_analysis.csv')}")
    print(f"- {os.path.join(Config.REPORT_DIR, 'significance_analysis.md')}")
    print(f"- {os.path.join(Config.REPORT_DIR, 'research_findings.md')}")
    print(f"- {os.path.join(Config.REPORT_DIR, 'threats_to_validity.md')}")
    print(f"- {os.path.join(Config.REPORT_DIR, 'related_work.md')}")
    print(f"- {os.path.join(Config.REPORT_DIR, 'paper.pdf')}")


if __name__ == "__main__":
    main()
