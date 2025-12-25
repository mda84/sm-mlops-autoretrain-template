from __future__ import annotations

import pathlib
import tarfile
from typing import Dict

import torch

from src.model.nn import SimpleMLP


def build_inference_files(model_dir: pathlib.Path) -> None:
    code_dir = model_dir / "code"
    code_dir.mkdir(parents=True, exist_ok=True)
    (code_dir / "requirements.txt").write_text("torch\npandas\nnumpy\n")
    inference_code = """
import json
import os
import io
import numpy as np
import pandas as pd
import torch
from src.model.nn import SimpleMLP

def model_fn(model_dir):
    state_dict = torch.load(os.path.join(model_dir, "model.pt"), map_location="cpu")
    # Default to 10 features; for production use model metadata.
    model = SimpleMLP(input_dim=10, output_dim=1, problem_type=os.environ.get("PROBLEM_TYPE", "classification"))
    model.load_state_dict(state_dict)
    model.eval()
    return model

def input_fn(input_data, content_type):
    if content_type == "text/csv":
        df = pd.read_csv(io.StringIO(input_data), header=None)
        return torch.tensor(df.values, dtype=torch.float32)
    payload = json.loads(input_data)
    arr = np.array(payload["data"], dtype=np.float32)
    return torch.tensor(arr)

def predict_fn(data, model):
    with torch.no_grad():
        preds = model(data)
    return preds.numpy().tolist()

def output_fn(prediction, accept):
    return json.dumps({"predictions": prediction})
"""
    (code_dir / "inference.py").write_text(inference_code)


def export_model_artifacts(model_path: str | pathlib.Path, output_path: str | pathlib.Path) -> pathlib.Path:
    model_dir = pathlib.Path(output_path)
    model_dir.mkdir(parents=True, exist_ok=True)
    torch.save(torch.load(model_path, map_location="cpu"), model_dir / "model.pt")
    build_inference_files(model_dir)
    tar_path = model_dir / "model.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(model_dir / "model.pt", arcname="model.pt")
        tar.add(model_dir / "code/inference.py", arcname="code/inference.py")
        tar.add(model_dir / "code/requirements.txt", arcname="code/requirements.txt")
    return tar_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export model to SageMaker format")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--output-dir", default="artifacts/export")
    args = parser.parse_args()
    export_model_artifacts(args.model_path, args.output_dir)
