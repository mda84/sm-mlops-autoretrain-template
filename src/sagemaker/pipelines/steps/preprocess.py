from __future__ import annotations

import os
from pathlib import Path

from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.workflow.steps import ProcessingStep


def create_preprocess_step(
    session,
    role: str,
    input_s3_uri: str,
    output_prefix: str,
    instance_type: str,
) -> ProcessingStep:
    processor = ScriptProcessor(
        command=["python3"],
        image_uri="763104351884.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1",
        role=role,
        instance_count=1,
        instance_type=instance_type,
        sagemaker_session=session,
    )
    source_dir = str(Path(__file__).parent)
    code_path = os.path.join(source_dir, "preprocess_script.py")
    step = ProcessingStep(
        name="Preprocess",
        processor=processor,
        inputs=[ProcessingInput(source=input_s3_uri, destination="/opt/ml/processing/input")],
        outputs=[
            ProcessingOutput(source="/opt/ml/processing/output/train", destination=f"{output_prefix}/train"),
            ProcessingOutput(source="/opt/ml/processing/output/val", destination=f"{output_prefix}/val"),
            ProcessingOutput(source="/opt/ml/processing/output/test", destination=f"{output_prefix}/test"),
        ],
        code=code_path,
    )
    return step
