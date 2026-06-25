import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from metrics.calibration import compute_calibration_curve


class CalibrationPlotter:
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        plt.rcParams.update({"font.size": 12, "figure.dpi": 150})

    def plot_reliability_diagram(
        self, results: pd.DataFrame, model_name: str, n_bins: int = 10
    ):
        bin_confs, bin_accs, bin_counts = compute_calibration_curve(results, n_bins)

        fig, ax = plt.subplots(figsize=(8, 8))

        # Perfect calibration line
        ax.plot([0, 1], [0, 1], "--", color="gray", label="Perfect calibration")

        # Reliability bars
        gap_bars = np.array(bin_accs) - np.array(bin_confs)
        colors = ["#e74c3c" if g < 0 else "#2ecc71" for g in gap_bars]
        ax.bar(bin_confs, bin_accs, width=0.09, color=colors, alpha=0.7, edgecolor="black", label="Model calibration")

        # Accuracy line
        ax.plot(bin_confs, bin_accs, "o-", color="#3498db", linewidth=2)

        ax.set_xlabel("Confidence", fontsize=14)
        ax.set_ylabel("Accuracy", fontsize=14)
        ax.set_title(f"Reliability Diagram — {model_name.title()}", fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(loc="lower right")
        ax.grid(alpha=0.3)

        path = os.path.join(self.output_dir, f"reliability_{model_name}.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_confidence_vs_accuracy(
        self, all_results: dict
    ):
        fig, ax = plt.subplots(figsize=(10, 6))

        marker_pool = ["o", "s", "^", "D", "v", "P", "*", "X"]
        color_pool = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#f39c12", "#1abc9c", "#e67e22", "#2c3e50"]

        for idx, (model_name, results) in enumerate(all_results.items()):
            sorted_conf = np.sort(results["confidence"].values)
            sorted_acc = np.cumsum(results.loc[results["confidence"].argsort(), "correct"].values) / np.arange(1, len(results) + 1)

            ax.plot(sorted_conf, sorted_acc, marker=marker_pool[idx], color=color_pool[idx],
                    markersize=3, linestyle="-", linewidth=1.5, alpha=0.8, label=model_name.title())

        ax.set_xlabel("Confidence (sorted)", fontsize=14)
        ax.set_ylabel("Cumulative Accuracy", fontsize=14)
        ax.set_title("Confidence vs. Accuracy", fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(alpha=0.3)

        path = os.path.join(self.output_dir, "confidence_vs_accuracy.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_model_comparison(
        self, all_metrics: dict
    ):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        metrics_list = ["accuracy", "average_confidence", "ece", "overconfidence"]
        titles = ["Accuracy", "Average Confidence", "Expected Calibration Error (ECE)", "Overconfidence Score"]
        colors_metric = [("#3498db", "#2980b9"), ("#2ecc71", "#27ae60"),
                         ("#e74c3c", "#c0392b"), ("#f39c12", "#d68910")]

        model_names = list(all_metrics.keys())
        metric_names = list(all_metrics[model_names[0]].keys())

        for ax, metric, title, (c1, c2) in zip(axes.flat, metrics_list, titles, colors_metric):
            values = [all_metrics[m][metric] for m in model_names]
            bars = ax.bar(model_names, values, color=c1, edgecolor=c2, linewidth=1.5)

            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f"{val:.3f}", ha="center", va="bottom", fontsize=11)

            ax.set_title(title, fontsize=14)
            ax.set_ylabel("Score", fontsize=12)
            ax.set_ylim(0, max(1.0, max(values) * 1.2))
            ax.grid(axis="y", alpha=0.3)

        fig.suptitle("Model Comparison — Calibration Metrics", fontsize=18)
        fig.tight_layout(rect=[0, 0, 1, 0.96])

        path = os.path.join(self.output_dir, "model_comparison.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_accuracy_vs_confidence_scatter(
        self, all_results: dict
    ):
        n = len(all_results)
        cols = min(n, 4)
        rows = (n + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 6*rows))
        axes = axes.flatten() if n > 1 else [axes]

        for ax, (model_name, results) in zip(axes, all_results.items()):
            conf = results["confidence"].values
            correct = results["correct"].values

            ax.scatter(conf[correct], correct[correct], alpha=0.4, color="#2ecc71",
                       s=30, label="Correct", edgecolors="none")
            ax.scatter(conf[~correct], correct[~correct], alpha=0.4, color="#e74c3c",
                       s=30, label="Incorrect", edgecolors="none")

            ax.set_xlabel("Confidence", fontsize=12)
            ax.set_ylabel("Correct", fontsize=12)
            ax.set_title(f"{model_name.title()}", fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(-0.1, 1.1)
            ax.legend(fontsize=10)
            ax.grid(alpha=0.3)

        for ax in axes[len(all_results):]:
            ax.set_visible(False)

        fig.suptitle("Confidence vs. Accuracy — Per Model", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.93])

        path = os.path.join(self.output_dir, "accuracy_vs_confidence_scatter.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path
