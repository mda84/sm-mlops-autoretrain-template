from __future__ import annotations

from pathlib import Path

from sagemaker.pytorch import PyTorch
from sagemaker.workflow.steps import TrainingStep


def create_training_step(
    session,
    role: str,
    train_s3: str,
    val_s3: str,
    output_prefix: str,
    instance_type: str,
    problem_type: str,
) -> TrainingStep:
    estimator = PyTorch(
        entry_point="train.py",
        source_dir=str(Path(__file__).parent.parent.parent / "model"),
        role=role,
        instance_count=1,
        instance_type=instance_type,
        framework_version="2.2",
        py_version="py310",
        hyperparameters={"problem_type": problem_type, "epochs": 3},
        sagemaker_session=session,
    )
    step = TrainingStep(
        name="Train",
        estimator=estimator,
        inputs={
            "train": train_s3,
            "val": val_s3,
        },
        cache_config=None,
    )
    return step
