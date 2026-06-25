import pandas as pd
import numpy as np
import re
import os
from typing import Dict, List, Tuple
from data.dataset import QUESTIONS_DATA


def build_question_map() -> Dict[str, dict]:
    qmap = {}
    for q in QUESTIONS_DATA:
        text = q["question"].strip()
        qmap[text] = q
    return qmap


def classify_error(question_text: str, ground_truth: str, model_answer: str, category: str) -> str:
    text = question_text.strip().lower()
    gt = str(ground_truth).strip()
    ma = str(model_answer).strip()

    # No answer given
    if not ma or ma == "":
        return "Incomplete Answer"

    # Check for calculation errors
    calc_patterns = [
        "square root", "x ", " + ", " - ", " * ", " / ", "percent",
        "divided by", "factorial", "derivative", "integral", "logarithm",
        "area of", "volume of", "sum of angles", "median", "mode", "range",
        "probability", "cos(", "sin(", "tan(", "gcd", "lcm",
    ]
    if any(p in text for p in calc_patterns):
        return "Calculation Error"

    # Check for logic/reasoning errors
    logic_patterns = [
        "which of the following", "what type of", "what is the term for",
        "what law", "what process", "what is the relationship",
        "if", "then", "therefore", "because", "implies",
    ]
    if any(p in text for p in logic_patterns):
        # Check if model gave a plausible-sounding but wrong answer
        if ma and ma.lower() not in text.lower():
            return "Logical Error"

    # Categories that are primarily factual recall
    factual_categories = {"Science", "History", "Literature", "Geography", "Technology",
                          "Philosophy", "Astronomy", "Biology", "Chemistry", "Physics",
                          "Factual Knowledge"}
    if category in factual_categories:
        return "Hallucination"

    return "Logical Error"


def run_error_analysis(results_groq: pd.DataFrame, results_gemini: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    os.makedirs(output_dir, exist_ok=True)
    qmap = build_question_map()

    all_records = []
    for model_name, df in [("groq", results_groq), ("gemini", results_gemini)]:
        incorrect = df[df["correct"] == 0].copy()
        for _, row in incorrect.iterrows():
            q_text = row["question"]
            q_info = qmap.get(q_text.strip(), {})
            cat = q_info.get("category", row.get("category", "Unknown"))
            error_type = classify_error(q_text, row["ground_truth"], row["model_answer"], cat)

            all_records.append({
                "model": model_name,
                "question": q_text,
                "ground_truth": row["ground_truth"],
                "model_answer": row["model_answer"],
                "confidence": row["confidence"],
                "category": cat,
                "error_type": error_type,
            })

    error_df = pd.DataFrame(all_records)
    csv_path = os.path.join(output_dir, "error_analysis.csv")
    error_df.to_csv(csv_path, index=False)
    print(f"Error analysis saved to {csv_path}")

    # Print summary
    print("\n=== Error Analysis ===")
    for model in ["groq", "gemini"]:
        subset = error_df[error_df["model"] == model]
        print(f"\n  {model.title()} ({len(subset)} errors):")
        for etype in ["Hallucination", "Calculation Error", "Logical Error", "Incomplete Answer", "Confidence Miscalibration"]:
            count = (subset["error_type"] == etype).sum()
            if count > 0:
                avg_conf = subset[subset["error_type"] == etype]["confidence"].mean()
                print(f"    {etype:22s}: {count:3d} errors, avg confidence={avg_conf:.4f}")

    return error_df
