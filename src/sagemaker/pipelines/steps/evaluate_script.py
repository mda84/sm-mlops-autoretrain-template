import json
import os
import pandas as pd
import torch

from src.common.metrics import classification_metrics, regression_metrics
from src.model.nn import SimpleMLP


def main():
    model_path = "/opt/ml/processing/model/model.pt"
    test_path = "/opt/ml/processing/test/test.csv"
    df = pd.read_csv(test_path)
    X = df.drop(columns=["label"]).values
    y = df["label"].values
    model = SimpleMLP(input_dim=X.shape[1], output_dim=1, problem_type="classification")
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    with torch.no_grad():
        preds = model(torch.tensor(X, dtype=torch.float32))
    pred_labels = (preds.squeeze().numpy() > 0.5).astype(int)
    metrics = classification_metrics(y, pred_labels)
    os.makedirs("/opt/ml/processing/output", exist_ok=True)
    with open("/opt/ml/processing/output/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
