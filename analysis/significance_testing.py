import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy.stats import chi2_contingency, binom_test
from scipy.special import comb


def run_mcnemar_test(results_groq: pd.DataFrame, results_gemini: pd.DataFrame) -> dict:
    paired = results_groq.merge(results_gemini, on="question", suffixes=("_groq", "_gemini"))
    n_both_correct = ((paired["correct_groq"] == 1) & (paired["correct_gemini"] == 1)).sum()
    n_both_wrong = ((paired["correct_groq"] == 0) & (paired["correct_gemini"] == 0)).sum()
    n_groq_only = ((paired["correct_groq"] == 1) & (paired["correct_gemini"] == 0)).sum()
    n_gemini_only = ((paired["correct_groq"] == 0) & (paired["correct_gemini"] == 1)).sum()

    n_discordant = n_groq_only + n_gemini_only
    if n_discordant == 0:
        p_value = 1.0
    else:
        k = min(n_groq_only, n_gemini_only)
        n = n_discordant
        p_value = 2 * sum(comb(n, i) * (0.5 ** n) for i in range(k + 1))
        p_value = min(p_value, 1.0)

    stat = ((n_groq_only - n_gemini_only) ** 2) / max(n_discordant, 1)

    result = {
        "test": "McNemar's Test",
        "statistic": round(stat, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < 0.05,
        "both_correct": int(n_both_correct),
        "both_wrong": int(n_both_wrong),
        "groq_only_correct": int(n_groq_only),
        "gemini_only_correct": int(n_gemini_only),
        "interpretation": (
            "Groq and Gemini accuracies are statistically different"
            if p_value < 0.05
            else "No statistically significant difference in accuracies"
        ),
    }
    return result


def run_chi_square_test(results_groq: pd.DataFrame, results_gemini: pd.DataFrame) -> dict:
    n_groq_correct = results_groq["correct"].sum()
    n_groq_total = len(results_groq)
    n_gemini_correct = results_gemini["correct"].sum()
    n_gemini_total = len(results_gemini)

    contingency = np.array([
        [n_groq_correct, n_groq_total - n_groq_correct],
        [n_gemini_correct, n_gemini_total - n_gemini_correct],
    ])

    chi2, p, dof, expected = chi2_contingency(contingency, correction=True)

    result = {
        "test": "Chi-Square Test (Yates' Correction)",
        "statistic": round(chi2, 4),
        "p_value": round(p, 6),
        "significant": p < 0.05,
        "degrees_of_freedom": int(dof),
        "contingency_table": contingency.tolist(),
        "interpretation": (
            "Proportions differ significantly between models"
            if p < 0.05
            else "No significant difference in proportions"
        ),
    }
    return result


def bootstrap_confidence_intervals(
    results_groq: pd.DataFrame,
    results_gemini: pd.DataFrame,
    n_bootstrap: int = 10000,
    alpha: float = 0.05,
) -> dict:
    rng = np.random.RandomState(42)
    n = len(results_groq)

    groq_accs = []
    gemini_accs = []
    diff_accs = []

    groq_confs = []
    gemini_confs = []
    diff_confs = []

    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, n)
        g_boot = results_groq.iloc[idx]
        ge_boot = results_gemini.iloc[idx]

        g_acc = g_boot["correct"].mean()
        ge_acc = ge_boot["correct"].mean()
        g_conf = g_boot["confidence"].mean()
        ge_conf = ge_boot["confidence"].mean()

        groq_accs.append(g_acc)
        gemini_accs.append(ge_acc)
        diff_accs.append(g_acc - ge_acc)
        groq_confs.append(g_conf)
        gemini_confs.append(ge_conf)
        diff_confs.append(g_conf - ge_conf)

    def ci(arr):
        lower = np.percentile(arr, 100 * alpha / 2)
        upper = np.percentile(arr, 100 * (1 - alpha / 2))
        return round(lower, 4), round(upper, 4)

    result = {
        "test": "Bootstrap Confidence Intervals",
        "n_bootstrap": n_bootstrap,
        "confidence_level": f"{(1-alpha)*100:.0f}%",
        "groq_accuracy_ci": ci(groq_accs),
        "gemini_accuracy_ci": ci(gemini_accs),
        "accuracy_difference_ci": ci(diff_accs),
        "groq_confidence_ci": ci(groq_confs),
        "gemini_confidence_ci": ci(gemini_confs),
        "confidence_difference_ci": ci(diff_confs),
        "interpretation": (
            "Accuracy difference is statistically significant"
            if (ci(diff_accs)[0] > 0 or ci(diff_accs)[1] < 0)
            else "Accuracy difference may not be statistically significant"
        ),
    }
    return result


def run_significance_analysis(results_groq: pd.DataFrame, results_gemini: pd.DataFrame, output_dir: str):
    import os
    os.makedirs(output_dir, exist_ok=True)

    mcnemar = run_mcnemar_test(results_groq, results_gemini)
    chi_sq = run_chi_square_test(results_groq, results_gemini)
    bootstrap = bootstrap_confidence_intervals(results_groq, results_gemini)

    # Write significance_analysis.md
    md = f"""# Statistical Significance Analysis

## 1. McNemar's Test

McNemar's test evaluates whether the two models differ in their paired accuracy outcomes (correct/incorrect per question).

| Metric | Value |
|--------|-------|
| Test Statistic (χ²) | {mcnemar["statistic"]} |
| p-value | {mcnemar["p_value"]} |
| Significant at α=0.05? | {'**YES**' if mcnemar['significant'] else 'No'} |

**Contingency:**

|  | Gemini Correct | Gemini Wrong |
|---|----------------|--------------|
| **Groq Correct** | {mcnemar['both_correct']} | {mcnemar['groq_only_correct']} |
| **Groq Wrong** | {mcnemar['gemini_only_correct']} | {mcnemar['both_wrong']} |

**Interpretation:** {mcnemar['interpretation']}

## 2. Chi-Square Test (Yates' Correction)

Tests whether the proportion of correct answers differs between the two independent samples.

| Metric | Value |
|--------|-------|
| Test Statistic (χ²) | {chi_sq["statistic"]} |
| Degrees of Freedom | {chi_sq["degrees_of_freedom"]} |
| p-value | {chi_sq["p_value"]} |
| Significant at α=0.05? | {'**YES**' if chi_sq['significant'] else 'No'} |

**Contingency Table:**

|  | Correct | Incorrect |
|---|---------|-----------|
| **Groq** | {chi_sq['contingency_table'][0][0]} | {chi_sq['contingency_table'][0][1]} |
| **Gemini** | {chi_sq['contingency_table'][1][0]} | {chi_sq['contingency_table'][1][1]} |

**Interpretation:** {chi_sq['interpretation']}

## 3. Bootstrap Confidence Intervals

Non-parametric bootstrap (n={bootstrap['n_bootstrap']}) with {bootstrap['confidence_level']} confidence intervals.

| Metric | Groq | Gemini | Difference (Groq - Gemini) |
|--------|------|--------|---------------------------|
| Accuracy CI | {bootstrap['groq_accuracy_ci'][0]:.4f} – {bootstrap['groq_accuracy_ci'][1]:.4f} | {bootstrap['gemini_accuracy_ci'][0]:.4f} – {bootstrap['gemini_accuracy_ci'][1]:.4f} | {bootstrap['accuracy_difference_ci'][0]:.4f} – {bootstrap['accuracy_difference_ci'][1]:.4f} |
| Confidence CI | {bootstrap['groq_confidence_ci'][0]:.4f} – {bootstrap['groq_confidence_ci'][1]:.4f} | {bootstrap['gemini_confidence_ci'][0]:.4f} – {bootstrap['gemini_confidence_ci'][1]:.4f} | {bootstrap['confidence_difference_ci'][0]:.4f} – {bootstrap['confidence_difference_ci'][1]:.4f} |

**Interpretation:** {bootstrap['interpretation']}
"""
    md_path = os.path.join(output_dir, "significance_analysis.md")
    with open(md_path, "w") as f:
        f.write(md)
    print(f"Significance analysis saved to {md_path}")

    # Print summary
    print("\n=== Statistical Significance ===")
    print(f"  McNemar p={mcnemar['p_value']:.6f} ({mcnemar['interpretation']})")
    print(f"  Chi-Square p={chi_sq['p_value']:.6f} ({chi_sq['interpretation']})")
    print(f"  Bootstrap acc diff 95% CI: {bootstrap['accuracy_difference_ci'][0]:.4f} to {bootstrap['accuracy_difference_ci'][1]:.4f}")

    return {"mcnemar": mcnemar, "chi_square": chi_sq, "bootstrap": bootstrap}
