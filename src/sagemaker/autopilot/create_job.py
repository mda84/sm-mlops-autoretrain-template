from __future__ import annotations

import time
from typing import Literal

import boto3

from src.common.logging import configure_logging

logger = configure_logging(__name__)


def create_autopilot_job(
    job_name: str,
    s3_uri: str,
    target_column: str,
    problem_type: Literal["classification", "regression"],
    objective_metric: str,
    max_candidates: int,
    max_runtime_seconds: int,
    role_arn: str,
    output_path: str,
    region: str | None = None,
) -> str:
    client = boto3.client("sagemaker", region_name=region)
    response = client.create_auto_ml_job_v2(
        AutoMLJobName=job_name,
        AutoMLJobInputDataConfig=[
            {
                "ChannelType": "training",
                "DataSource": {"S3DataSource": {"S3Uri": s3_uri, "S3DataType": "S3Prefix"}},
                "TargetAttributeName": target_column,
            }
        ],
        OutputDataConfig={"S3OutputPath": output_path},
        AutoMLProblemTypeConfig={
            "ProblemType": problem_type,
            "TabularJobConfig": {"CandidateGenerationConfig": {"AlgorithmsConfig": []}},
        },
        AutoMLJobObjective={"MetricName": objective_metric},
        RoleArn=role_arn,
        SecurityConfig={"EnableInterContainerTrafficEncryption": False},
        TimeoutConfig={"MaxRuntimePerTrainingJobInSeconds": max_runtime_seconds},
        DataSplitConfig={"ValidationPercentage": 15, "TrainingPercentage": 70, "TestPercentage": 15},
        CandidateGenerationConfig={"AlgorithmsConfig": []},
    )
    arn = response["AutoMLJobArn"]
    logger.info("Created AutoPilot job %s", arn)
    return arn
