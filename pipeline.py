import os
import json
import argparse
from typing import Dict, List
from tqdm import tqdm
import pandas as pd

from config import Config
from data.dataset import CalibrationDataset
from models import GeminiClient, GroqClient
from metrics.calibration import compute_all_metrics, apply_temperature_scaling
from visualization.plots import CalibrationPlotter


def get_model_client(model_name: str):
    api_key = Config.get_api_key(model_name)
    info = Config.MODELS[model_name]

    if model_name == "gemini":
        return GeminiClient(api_key=api_key, api_url=info["api_url"])
    elif model_name == "groq":
        return GroqClient(api_key=api_key, api_url=info["api_url"])
    else:
        raise ValueError(f"Unknown model: {model_name}")


def evaluate_model(
    model_name: str,
    dataset: CalibrationDataset,
    output_dir: str,
) -> pd.DataFrame:
    client = get_model_client(model_name)
    records: List[Dict] = []

    print(f"\n{'='*60}")
    print(f"Evaluating {model_name.title()}")
    print(f"{'='*60}")

    for i in tqdm(range(len(dataset)), desc=f"{model_name.title()}"):
        item = dataset[i]
        prompt = CalibrationDataset.format_prompt(item["question"], item["options"])

        response_text, confidence = client.query(prompt)
        model_answer = client.extract_answer(response_text, item["options"])
        is_correct = int(model_answer == item["answer"])

        records.append({
            "question": item["question"],
            "ground_truth": item["answer"],
            "model_answer": model_answer,
            "confidence": round(confidence, 4),
            "correct": is_correct,
            "category": item["category"],
        })

    df = pd.DataFrame(records)

    csv_path = os.path.join(output_dir, f"results_{model_name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved results to {csv_path}")

    return df


def run_pipeline(models: List[str] = None, num_questions: int = 300):
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    dataset = CalibrationDataset(num_questions=num_questions, seed=Config.SEED)
    dataset.save(os.path.join(Config.OUTPUT_DIR, "dataset.json"))
    print(f"Loaded dataset with {len(dataset)} questions across {len(dataset.get_categories())} categories.")

    if models is None:
        models = list(Config.MODELS.keys())

    all_results: Dict[str, pd.DataFrame] = {}
    all_metrics: Dict[str, Dict] = {}

    for model_name in models:
        df = evaluate_model(model_name, dataset, Config.OUTPUT_DIR)
        all_results[model_name] = df
        metrics = compute_all_metrics(df)
        all_metrics[model_name] = metrics

        print(f"\n{model_name.title()} Metrics:")
        print(f"  Accuracy:          {metrics['accuracy']:.4f}")
        print(f"  Avg Confidence:    {metrics['average_confidence']:.4f}")
        print(f"  ECE:               {metrics['ece']:.4f}")
        print(f"  Overconfidence:    {metrics['overconfidence']:.4f}")

        # Apply temperature scaling calibration
        calibrated_df, optimal_temp = apply_temperature_scaling(df)
        cal_metrics = compute_all_metrics(calibrated_df)
        cal_csv = os.path.join(Config.OUTPUT_DIR, f"results_{model_name}_calibrated.csv")
        calibrated_df.to_csv(cal_csv, index=False)
        print(f"  --- After Temperature Scaling (T={optimal_temp:.2f}) ---")
        print(f"  Avg Confidence:    {cal_metrics['average_confidence']:.4f}")
        print(f"  ECE:               {cal_metrics['ece']:.4f}")
        print(f"  Overconfidence:    {cal_metrics['overconfidence']:.4f}")

    # Save combined metrics
    metrics_df = pd.DataFrame(all_metrics).T
    metrics_path = os.path.join(Config.OUTPUT_DIR, "metrics_summary.csv")
    metrics_df.to_csv(metrics_path)
    print(f"\nMetrics summary saved to {metrics_path}")

    # Generate plots
    plotter = CalibrationPlotter(output_dir=Config.OUTPUT_DIR)
    plot_paths = []

    for model_name, results in all_results.items():
        path = plotter.plot_reliability_diagram(results, model_name)
        plot_paths.append(path)

    path = plotter.plot_confidence_vs_accuracy(all_results)
    plot_paths.append(path)

    path = plotter.plot_model_comparison(all_metrics)
    plot_paths.append(path)

    path = plotter.plot_accuracy_vs_confidence_scatter(all_results)
    plot_paths.append(path)

    print(f"\nGenerated {len(plot_paths)} plots in {Config.OUTPUT_DIR}/")
    for p in plot_paths:
        print(f"  {p}")

    return all_results, all_metrics


def main():
    parser = argparse.ArgumentParser(description="LLM Calibration Study Pipeline")
    parser.add_argument("--models", nargs="+", default=["groq", "gemini"],
                        help="Models to evaluate")
    parser.add_argument("--num-questions", type=int, default=300,
                        help="Number of questions to evaluate")
    args = parser.parse_args()

    run_pipeline(models=args.models, num_questions=args.num_questions)


if __name__ == "__main__":
    main()
