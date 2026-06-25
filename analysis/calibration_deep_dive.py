import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from typing import Dict, List

from metrics.calibration import compute_calibration_curve, compute_accuracy, compute_average_confidence, compute_ece
from analysis.category_analysis import build_question_index


def plot_per_category_reliability(results: Dict[str, pd.DataFrame], question_index: Dict[str, str], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    categories = sorted(set(question_index.values()))
    models = list(results.keys())

    for cat in categories:
        cat_questions = {q for q, c in question_index.items() if c == cat}
        n_cat = sum(1 for q in question_index.values() if q == cat)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f"Calibration for '{cat}' (n={n_cat})", fontsize=14)

        for idx, model_name in enumerate(models):
            ax = axes[idx]
            subset = results[model_name][results[model_name]["question"].isin(cat_questions)]
            if len(subset) < 5:
                ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
                ax.set_title(f"{model_name.title()}")
                continue

            bin_confs, bin_accs, bin_counts = compute_calibration_curve(subset)
            acc = compute_accuracy(subset)
            conf = compute_average_confidence(subset)
            ece = compute_ece(subset)

            ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect Calibration")
            ax.plot(bin_confs, bin_accs, "o-", linewidth=2, markersize=6, color="C0")
            for i, (x, y, c) in enumerate(zip(bin_confs, bin_accs, bin_counts)):
                ax.fill_betweenx([0, y], x - 0.04, x + 0.04, alpha=0.15, color="C0")
                if c > 0:
                    ax.annotate(str(c), (x, y), textcoords="offset points", xytext=(0, 8), fontsize=8, ha="center")

            ax.set_xlabel("Confidence")
            ax.set_ylabel("Accuracy")
            ax.set_title(f"{model_name.title()} (acc={acc:.3f}, ECE={ece:.4f})")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)

        plt.tight_layout()
        path = os.path.join(output_dir, f"reliability_{cat.lower().replace(' ', '_')}.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {path}")


def plot_confidence_histograms(results: Dict[str, pd.DataFrame], question_index: Dict[str, str], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    categories = sorted(set(question_index.values()))

    for cat in categories:
        cat_questions = {q for q, c in question_index.items() if c == cat}
        n_cat = sum(1 for q in question_index.values() if q == cat)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        fig.suptitle(f"Confidence Histogram: '{cat}' (n={n_cat})", fontsize=14)

        for idx, model_name in enumerate(results.keys()):
            ax = axes[idx]
            subset = results[model_name][results[model_name]["question"].isin(cat_questions)]
            if len(subset) == 0:
                continue

            correct = subset[subset["correct"] == 1]
            incorrect = subset[subset["correct"] == 0]

            ax.hist(correct["confidence"], bins=10, alpha=0.6, color="green", label=f"Correct (n={len(correct)})")
            ax.hist(incorrect["confidence"], bins=10, alpha=0.6, color="red", label=f"Incorrect (n={len(incorrect)})")
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Count")
            ax.set_title(f"{model_name.title()}")
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)

        plt.tight_layout()
        path = os.path.join(output_dir, f"histogram_{cat.lower().replace(' ', '_')}.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {path}")


def plot_per_category_bar_chart(all_metrics_by_category: Dict[str, pd.DataFrame], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    models = list(all_metrics_by_category.keys())
    categories = sorted(set(c for m in models for c in all_metrics_by_category[m]["category"]))
    metrics = ["accuracy", "ece"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x = np.arange(len(categories))
    width = 0.3

    for mi, metric in enumerate(metrics):
        ax = axes[mi]
        for i, model_name in enumerate(models):
            df = all_metrics_by_category[model_name]
            values = [df[df["category"] == c][metric].values[0] if c in df["category"].values else 0 for c in categories]
            ax.bar(x + i * width, values, width, label=model_name.title(), alpha=0.8)
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(categories, rotation=30, ha="right")
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.set_title(f"Per-Category {metric.replace('_', ' ').title()}")
        ax.legend()
        ax.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "category_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_error_distribution(error_df: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    models = error_df["model"].unique()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    for idx, model in enumerate(models):
        ax = axes[idx]
        subset = error_df[error_df["model"] == model]
        error_counts = subset["error_type"].value_counts()
        colors = ["#e74c3c", "#f39c12", "#3498db", "#9b59b6", "#95a5a6"][:len(error_counts)]
        ax.bar(error_counts.index, error_counts.values, color=colors, alpha=0.8)
        for i, (etype, count) in enumerate(error_counts.items()):
            ax.text(i, count + 0.5, str(count), ha="center", fontsize=10)
        ax.set_title(f"{model.title()} Error Distribution")
        ax.set_ylabel("Count")
        ax.set_xlabel("Error Type")
        ax.tick_params(axis="x", rotation=25)
        ax.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "error_distribution.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_error_vs_confidence(error_df: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    models = error_df["model"].unique()
    error_types = error_df["error_type"].unique()

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(error_types))
    width = 0.3

    for i, model in enumerate(models):
        subset = error_df[error_df["model"] == model]
        means = [subset[subset["error_type"] == et]["confidence"].mean() if len(subset[subset["error_type"] == et]) > 0 else 0 for et in error_types]
        ax.bar(x + i * width, means, width, label=model.title(), alpha=0.8)

    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(error_types, rotation=25)
    ax.set_ylabel("Average Confidence")
    ax.set_title("Confidence by Error Type")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "error_confidence.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def run_calibration_deep_dive(results: Dict[str, pd.DataFrame], error_df: pd.DataFrame, output_dir: str):
    question_index = build_question_index()

    print("\n=== Calibration Deep Dive ===")
    plot_per_category_reliability(results, question_index, output_dir)
    plot_confidence_histograms(results, question_index, output_dir)
    plot_error_distribution(error_df, output_dir)
    plot_error_vs_confidence(error_df, output_dir)

    # Compute per-category metrics for bar chart
    from analysis.category_analysis import compute_category_metrics
    metrics_by_model = {}
    for model_name, df in results.items():
        metrics_by_model[model_name] = compute_category_metrics(df, question_index)

    plot_per_category_bar_chart(metrics_by_model, output_dir)
