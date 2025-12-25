import pathlib

from src.common.hashing import compute_dataset_fingerprint
from src.data.generate_dummy import generate_dummy_dataset


def test_fingerprint_stable(tmp_path: pathlib.Path):
    generate_dummy_dataset(tmp_path, 50, "classification", seed=1)
    fp1 = compute_dataset_fingerprint(tmp_path)
    fp2 = compute_dataset_fingerprint(tmp_path)
    assert fp1 == fp2
