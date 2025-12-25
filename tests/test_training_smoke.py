import pathlib

from src.data.generate_dummy import generate_dummy_dataset
from src.model.train import train_model


def test_training_smoke(tmp_path: pathlib.Path):
    meta = generate_dummy_dataset(tmp_path, 200, "classification", seed=2)
    model, metrics = train_model(tmp_path / "data.csv", tmp_path / "data.csv", "classification", epochs=1)
    assert "accuracy" in metrics or "rmse" in metrics
