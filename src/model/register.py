from __future__ import annotations

import json
from typing import Dict

import boto3

from src.common.logging import configure_logging

logger = configure_logging(__name__)


def register_model(model_package_group: str, model_data_url: str, metrics: Dict[str, float], role_arn: str, region: str | None = None) -> str:
    sm = boto3.client("sagemaker", region_name=region)
    metadata_props = [{"Name": k, "Value": str(v)} for k, v in metrics.items()]
    response = sm.create_model_package(
        ModelPackageGroupName=model_package_group,
        ModelMetrics={"ModelQuality": {"Statistics": {"ContentType": "application/json", "S3Uri": model_data_url}}},
        InferenceSpecification={
            "Containers": [
                {
                    "Image": "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:2.2.0-cpu-py310-ubuntu20.04",
                    "ModelDataUrl": model_data_url,
                }
            ],
            "SupportedContentTypes": ["text/csv", "application/json"],
            "SupportedResponseMIMETypes": ["application/json"],
        },
        ModelApprovalStatus="PendingManualApproval",
        MetadataProperties={"AdditionalProperties": json.dumps(metadata_props)},
        RoleArn=role_arn,
    )
    arn = response["ModelPackageArn"]
    logger.info("Registered model package %s", arn)
    return arn
