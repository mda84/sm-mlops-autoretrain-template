from __future__ import annotations

import os
from pathlib import Path

from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.steps import ProcessingStep


def create_evaluate_step(session, role: str, model_path: str, test_s3: str, output_prefix: str, instance_type: str):
    processor = ScriptProcessor(
        command=["python3"],
        image_uri="763104351884.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1",
        role=role,
        instance_count=1,
        instance_type=instance_type,
        sagemaker_session=session,
    )
    code_path = os.path.join(Path(__file__).parent, "evaluate_script.py")
    step = ProcessingStep(
        name="Evaluate",
        processor=processor,
        inputs=[
            ProcessingInput(source=model_path, destination="/opt/ml/processing/model"),
            ProcessingInput(source=test_s3, destination="/opt/ml/processing/test"),
        ],
        outputs=[
            ProcessingOutput(source="/opt/ml/processing/output", destination=output_prefix),
        ],
        code=code_path,
        property_files=[
            PropertyFile(
                name="EvaluationMetrics",
                output_name="metrics",
                path="metrics.json",
            )
        ],
    )
    return step
