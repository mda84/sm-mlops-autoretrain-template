from __future__ import annotations

import argparse
import json
from typing import Optional

from src.common.config import ProjectConfig, load_yaml, resolve_env
from src.sagemaker.pipelines.pipeline import create_pipeline


def upsert_pipeline(config_path: str = "configs/project.yaml", pipeline_config_path: str = "configs/pipeline.yaml"):
    project = ProjectConfig.load(config_path, tags_path="configs/tags.yaml")
    pipeline_cfg = load_yaml(pipeline_config_path)
    pipeline = create_pipeline(
        region=project.aws_region,
        role=project.sagemaker_execution_role_arn,
        pipeline_name=pipeline_cfg["pipeline_name"],
        bucket=project.s3_bucket_name,
        model_package_group=project.model_package_group_name,
        process_instance_type=pipeline_cfg["process_instance_type"],
        train_instance_type=pipeline_cfg["train_instance_type"],
    )
    definition = pipeline.definition()
    return definition


def start_pipeline_execution(dataset_s3: str, problem_type: str, metric_threshold: float, config_path: str = "configs/project.yaml", pipeline_config_path: str = "configs/pipeline.yaml"):
    project = ProjectConfig.load(config_path, tags_path="configs/tags.yaml")
    pipeline_cfg = load_yaml(pipeline_config_path)
    pipeline = create_pipeline(
        region=project.aws_region,
        role=project.sagemaker_execution_role_arn,
        pipeline_name=pipeline_cfg["pipeline_name"],
        bucket=project.s3_bucket_name,
        model_package_group=project.model_package_group_name,
        process_instance_type=pipeline_cfg["process_instance_type"],
        train_instance_type=pipeline_cfg["train_instance_type"],
    )
    execution = pipeline.start(
        parameters={
            "DatasetS3Uri": dataset_s3,
            "ProblemType": problem_type,
            "MetricThreshold": metric_threshold,
            "ApprovalStatus": pipeline_cfg.get("model_approval_status", "PendingManualApproval"),
        }
    )
    return execution.arn


def describe_execution(execution_arn: str, config_path: str = "configs/project.yaml", pipeline_config_path: str = "configs/pipeline.yaml"):
    project = ProjectConfig.load(config_path, tags_path="configs/tags.yaml")
    pipeline_cfg = load_yaml(pipeline_config_path)
    pipeline = create_pipeline(
        region=project.aws_region,
        role=project.sagemaker_execution_role_arn,
        pipeline_name=pipeline_cfg["pipeline_name"],
        bucket=project.s3_bucket_name,
        model_package_group=project.model_package_group_name,
        process_instance_type=pipeline_cfg["process_instance_type"],
        train_instance_type=pipeline_cfg["train_instance_type"],
    )
    return pipeline.describe_execution(execution_arn)


def cli():
    parser = argparse.ArgumentParser(description="Manage SageMaker pipeline")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("upsert")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--dataset-s3", required=True)
    run_parser.add_argument("--problem-type", default="classification")
    run_parser.add_argument("--metric-threshold", type=float, default=0.7)

    args = parser.parse_args()
    if args.command == "upsert":
        definition = upsert_pipeline()
        print(definition)
    elif args.command == "run":
        arn = start_pipeline_execution(args.dataset_s3, args.problem_type, args.metric_threshold)
        print(arn)


if __name__ == "__main__":
    cli()
