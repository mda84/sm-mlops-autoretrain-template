from __future__ import annotations

import json
import os
import pathlib
import time
from typing import Dict, Literal, Tuple

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.common.logging import configure_logging
from src.common.metrics import classification_metrics, regression_metrics
from src.model.nn import SimpleMLP

logger = configure_logging(__name__)

ProblemType = Literal["classification", "regression"]


def load_data(csv_path: str | pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(csv_path)
    y = df["label"].values
    X = df.drop(columns=["label"]).values.astype(np.float32)
    return X, y


def train_model(
    train_csv: str | pathlib.Path,
    val_csv: str | pathlib.Path,
    problem_type: ProblemType,
    epochs: int = 5,
    batch_size: int = 64,
    lr: float = 1e-3,
    seed: int = 42,
) -> Tuple[SimpleMLP, Dict[str, float]]:
    torch.manual_seed(seed)
    np.random.seed(seed)

    X_train, y_train = load_data(train_csv)
    X_val, y_val = load_data(val_csv)
    input_dim = X_train.shape[1]
    output_dim = 1 if problem_type == "regression" or len(np.unique(y_train)) == 2 else len(np.unique(y_train))
    model = SimpleMLP(input_dim=input_dim, output_dim=output_dim, problem_type=problem_type)
    criterion = nn.MSELoss() if problem_type == "regression" else nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train))
    val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)

    best_val = float("inf")
    best_state = None
    patience, patience_counter = 2, 0

    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            preds = model(batch_x)
            if problem_type == "regression":
                loss = criterion(preds.squeeze(), batch_y.float())
            else:
                if preds.shape[1] == 1:
                    loss = criterion(preds.squeeze(), batch_y.float())
                else:
                    loss = criterion(preds, batch_y.long())
            loss.backward()
            optimizer.step()

        val_loss = 0.0
        model.eval()
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                preds = model(batch_x)
                if problem_type == "regression":
                    val_loss += criterion(preds.squeeze(), batch_y.float()).item()
                else:
                    if preds.shape[1] == 1:
                        val_loss += criterion(preds.squeeze(), batch_y.float()).item()
                    else:
                        val_loss += criterion(preds, batch_y.long()).item()
        val_loss /= len(val_loader)
        logger.info("Epoch %s validation loss %.4f", epoch, val_loss)
        if val_loss < best_val:
            best_val = val_loss
            best_state = model.state_dict()
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter > patience:
                logger.info("Early stopping at epoch %s", epoch)
                break

    if best_state:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        train_preds = model(torch.tensor(X_train, dtype=torch.float32))
        val_preds = model(torch.tensor(X_val, dtype=torch.float32))
    if problem_type == "regression":
        metrics = regression_metrics(y_val, val_preds.squeeze().numpy())
    else:
        if output_dim == 1:
            train_pred_labels = (train_preds.squeeze().numpy() > 0.5).astype(int)
            val_pred_labels = (val_preds.squeeze().numpy() > 0.5).astype(int)
        else:
            train_pred_labels = np.argmax(train_preds.numpy(), axis=1)
            val_pred_labels = np.argmax(val_preds.numpy(), axis=1)
        metrics = classification_metrics(y_val, val_pred_labels)
        metrics["train_accuracy"] = float(classification_metrics(y_train, train_pred_labels)["accuracy"])
    return model, metrics


def save_artifacts(model: SimpleMLP, metrics: Dict[str, float], output_dir: str | pathlib.Path) -> None:
    out_path = pathlib.Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_path / "model.pt")
    with open(out_path / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Train baseline model")
    parser.add_argument("--train-csv", required=True)
    parser.add_argument("--val-csv", required=True)
    parser.add_argument("--problem-type", choices=["classification", "regression"], default="classification")
    parser.add_argument("--output-dir", default="artifacts/run-default")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    run_id = args.run_id or f"run-{int(time.time())}"
    output_dir = pathlib.Path(args.output_dir) / run_id
    model, metrics = train_model(args.train_csv, args.val_csv, args.problem_type, epochs=args.epochs)
    save_artifacts(model, metrics, output_dir)
    logger.info("Saved artifacts to %s", output_dir)


if __name__ == "__main__":
    main()
