from __future__ import annotations

import json
import pathlib
from typing import Dict, Literal

import numpy as np
import pandas as pd
import torch

from src.common.logging import configure_logging
from src.common.metrics import classification_metrics, regression_metrics
from src.model.nn import SimpleMLP

logger = configure_logging(__name__)


def load_model(model_path: str | pathlib.Path, input_dim: int, output_dim: int, problem_type: str) -> SimpleMLP:
    model = SimpleMLP(input_dim=input_dim, output_dim=output_dim, problem_type=problem_type)
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    return model


def evaluate(model: SimpleMLP, csv_path: str | pathlib.Path, problem_type: Literal["classification", "regression"]) -> Dict[str, float]:
    df = pd.read_csv(csv_path)
    X = df.drop(columns=["label"]).values.astype(np.float32)
    y = df["label"].values
    with torch.no_grad():
        preds = model(torch.tensor(X, dtype=torch.float32))
    if problem_type == "regression":
        metrics = regression_metrics(y, preds.squeeze().numpy())
    else:
        if preds.shape[1] == 1:
            pred_labels = (preds.squeeze().numpy() > 0.5).astype(int)
        else:
            pred_labels = np.argmax(preds.numpy(), axis=1)
        metrics = classification_metrics(y, pred_labels)
    return metrics


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate model")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--test-csv", required=True)
    parser.add_argument("--problem-type", choices=["classification", "regression"], default="classification")
    parser.add_argument("--input-dim", type=int, required=True)
    parser.add_argument("--output-dim", type=int, required=True)
    parser.add_argument("--output-metrics", default="metrics.json")
    args = parser.parse_args()
    model = load_model(args.model_path, args.input_dim, args.output_dim, args.problem_type)
    metrics = evaluate(model, args.test_csv, args.problem_type)
    pathlib.Path(args.output_metrics).write_text(json.dumps(metrics, indent=2))
    logger.info("Evaluation metrics saved to %s", args.output_metrics)


if __name__ == "__main__":
    main()
