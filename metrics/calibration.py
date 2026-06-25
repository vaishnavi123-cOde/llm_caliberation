import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy.optimize import minimize_scalar


def compute_accuracy(results: pd.DataFrame) -> float:
    return results["correct"].astype(float).mean()


def compute_average_confidence(results: pd.DataFrame) -> float:
    return results["confidence"].mean()


def compute_ece(
    results: pd.DataFrame, n_bins: int = 10
) -> float:
    confidences = results["confidence"].values
    correct = results["correct"].astype(float).values

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        lower = bin_boundaries[i]
        upper = bin_boundaries[i + 1]
        in_bin = (confidences > lower) & (confidences <= upper)
        if upper == 1.0:
            in_bin = in_bin | (confidences == 1.0)

        bin_size = in_bin.sum()
        if bin_size > 0:
            bin_acc = correct[in_bin].mean()
            bin_conf = confidences[in_bin].mean()
            ece += (bin_size / len(confidences)) * abs(bin_acc - bin_conf)

    return ece


def compute_overconfidence(results: pd.DataFrame) -> float:
    mask = results["correct"].astype(bool)
    incorrect = results[~mask]
    if len(incorrect) == 0:
        return 0.0
    overconfidence = incorrect["confidence"].mean()
    return overconfidence


def compute_all_metrics(results: pd.DataFrame) -> Dict[str, float]:
    acc = compute_accuracy(results)
    avg_conf = compute_average_confidence(results)
    ece = compute_ece(results)
    overconf = compute_overconfidence(results)

    return {
        "accuracy": round(acc, 4),
        "average_confidence": round(avg_conf, 4),
        "ece": round(ece, 4),
        "overconfidence": round(overconf, 4),
    }


def compute_calibration_curve(results: pd.DataFrame, n_bins: int = 10):
    confidences = results["confidence"].values
    correct = results["correct"].astype(float).values

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    bin_accs = []
    bin_confs = []
    bin_counts = []

    for i in range(n_bins):
        lower = bin_boundaries[i]
        upper = bin_boundaries[i + 1]
        in_bin = (confidences > lower) & (confidences <= upper)
        if upper == 1.0:
            in_bin = in_bin | (confidences == 1.0)
        count = in_bin.sum()
        bin_counts.append(count)
        if count > 0:
            bin_accs.append(correct[in_bin].mean())
            bin_confs.append(confidences[in_bin].mean())
        else:
            bin_accs.append(0.0)
            bin_confs.append(0.0)

    return bin_confs, bin_accs, bin_counts


def temperature_scale(confidences: np.ndarray, temperature: float) -> np.ndarray:
    logits = np.log(np.clip(confidences, 1e-7, 1 - 1e-7) / (1 - np.clip(confidences, 1e-7, 1 - 1e-7)))
    scaled_logits = logits / temperature
    return 1 / (1 + np.exp(-scaled_logits))


def find_optimal_temperature(
    confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10
) -> float:
    def objective(T):
        scaled = temperature_scale(confidences, T)
        bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        for i in range(n_bins):
            lower = bin_boundaries[i]
            upper = bin_boundaries[i + 1]
            in_bin = (scaled > lower) & (scaled <= upper)
            if upper == 1.0:
                in_bin = in_bin | (scaled == 1.0)
            bin_size = in_bin.sum()
            if bin_size > 0:
                bin_acc = correct[in_bin].mean()
                bin_conf = scaled[in_bin].mean()
                ece += (bin_size / len(confidences)) * abs(bin_acc - bin_conf)
        return ece

    result = minimize_scalar(objective, bounds=(0.1, 10.0), method="bounded")
    return result.x


def apply_temperature_scaling(
    results: pd.DataFrame, temperature: float = None
) -> Tuple[pd.DataFrame, float]:
    confidences = results["confidence"].values
    correct = results["correct"].values

    if temperature is None:
        temperature = find_optimal_temperature(confidences, correct)

    scaled = temperature_scale(confidences, temperature)
    results = results.copy()
    results["confidence"] = np.round(scaled, 4)
    return results, temperature
