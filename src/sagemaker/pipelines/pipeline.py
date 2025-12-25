from __future__ import annotations

from pathlib import Path
from typing import Literal

import boto3
from sagemaker.workflow.parameters import ParameterFloat, ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import PipelineSession

from src.sagemaker.pipelines.steps.condition import create_condition_step
from src.sagemaker.pipelines.steps.evaluate import create_evaluate_step
from src.sagemaker.pipelines.steps.preprocess import create_preprocess_step
from src.sagemaker.pipelines.steps.register import create_register_step
from src.sagemaker.pipelines.steps.train import create_training_step


def get_session(region: str) -> PipelineSession:
    boto_sess = boto3.Session(region_name=region)
    return PipelineSession(boto_sess)


def create_pipeline(
    region: str,
    role: str,
    pipeline_name: str,
    bucket: str,
    model_package_group: str,
    process_instance_type: str,
    train_instance_type: str,
) -> Pipeline:
    session = get_session(region)
    dataset_param = ParameterString(name="DatasetS3Uri")
    problem_type_param = ParameterString(name="ProblemType", default_value="classification")
    metric_threshold_param = ParameterFloat(name="MetricThreshold", default_value=0.7)
    approval_status_param = ParameterString(name="ApprovalStatus", default_value="PendingManualApproval")

    preprocess = create_preprocess_step(
        session=session,
        role=role,
        input_s3_uri=dataset_param,
        output_prefix=f"s3://{bucket}/runs/preprocessed",
        instance_type=process_instance_type,
    )

    train_step = create_training_step(
        session=session,
        role=role,
        train_s3=preprocess.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
        val_s3=preprocess.properties.ProcessingOutputConfig.Outputs["val"].S3Output.S3Uri,
        output_prefix=f"s3://{bucket}/runs/training",
        instance_type=train_instance_type,
        problem_type=problem_type_param,
    )

    evaluate_step = create_evaluate_step(
        session=session,
        role=role,
        model_path=train_step.properties.ModelArtifacts.S3ModelArtifacts,
        test_s3=preprocess.properties.ProcessingOutputConfig.Outputs["test"].S3Output.S3Uri,
        output_prefix=f"s3://{bucket}/runs/evaluation",
        instance_type=process_instance_type,
    )

    register_step = create_register_step(
        model=train_step.get_expected_model(),
        model_data=train_step.properties.ModelArtifacts.S3ModelArtifacts,
        role=role,
        model_package_group=model_package_group,
        approval_status=approval_status_param,
    )

    condition_step = create_condition_step(
        evaluate_step=evaluate_step,
        metric_name="accuracy",
        threshold=metric_threshold_param,
        register_step=register_step,
    )

    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[dataset_param, problem_type_param, metric_threshold_param, approval_status_param],
        steps=[preprocess, train_step, evaluate_step, condition_step],
        sagemaker_session=session,
    )
    return pipeline
