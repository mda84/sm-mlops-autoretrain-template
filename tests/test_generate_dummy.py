import pathlib

from src.data.generate_dummy import generate_dummy_dataset


def test_generate_outputs(tmp_path: pathlib.Path):
    meta = generate_dummy_dataset(tmp_path, 100, "classification", seed=1)
    assert (tmp_path / "data.csv").exists()
    assert (tmp_path / "schema.json").exists()
    assert meta.dataset_id
