import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List

from data.dataset import QUESTIONS_DATA
from metrics.calibration import compute_accuracy, compute_average_confidence, compute_ece, compute_overconfidence

FACTUAL_CATEGORIES = {"Science", "History", "Literature", "Geography", "Technology", "Philosophy", "Astronomy", "Biology", "Chemistry", "Physics"}
MATH_CATEGORIES = {"Mathematics"}

def classify_question(q: dict) -> str:
    cat = q["category"]
    if cat in MATH_CATEGORIES:
        return "Mathematical Reasoning"
    return "Factual Knowledge"

def build_question_index() -> Dict[str, str]:
    idx = {}
    for q in QUESTIONS_DATA:
        text = q["question"].strip()
        idx[text] = classify_question(q)
    return idx

def compute_category_metrics(results: pd.DataFrame, question_index: Dict[str, str]) -> pd.DataFrame:
    rows = []
    for cat in sorted(set(question_index.values())):
        cat_questions = {q for q, c in question_index.items() if c == cat}
        mask = results["question"].isin(cat_questions)
        subset = results[mask]
        if len(subset) == 0:
            continue
        n = len(subset)
        acc = compute_accuracy(subset)
        avg_conf = compute_average_confidence(subset)
        ece = compute_ece(subset)
        overconf = compute_overconfidence(subset)
        rows.append({
            "model": "N/A",
            "category": cat,
            "n_questions": n,
            "accuracy": round(acc, 4),
            "average_confidence": round(avg_conf, 4),
            "ece": round(ece, 4),
            "overconfidence": round(overconf, 4),
        })
    return pd.DataFrame(rows)


def run_category_analysis(model_results: Dict[str, pd.DataFrame], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    question_index = build_question_index()

    all_rows = []
    for model_name, df in model_results.items():
        cat_df = compute_category_metrics(df, question_index)
        cat_df["model"] = model_name
        all_rows.append(cat_df)

    combined = pd.concat(all_rows, ignore_index=True)
    csv_path = os.path.join(output_dir, "category_metrics.csv")
    combined.to_csv(csv_path, index=False)
    print(f"Category metrics saved to {csv_path}")

    # Print summary
    print("\n=== Category-Based Analysis ===")
    for _, row in combined.iterrows():
        print(f"  {row['model']:8s} | {row['category']:22s} | n={row['n_questions']:3d} | acc={row['accuracy']:.4f} | conf={row['average_confidence']:.4f} | ece={row['ece']:.4f} | overconf={row['overconfidence']:.4f}")

    return combined
