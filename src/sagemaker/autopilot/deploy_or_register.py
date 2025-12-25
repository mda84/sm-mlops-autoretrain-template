from __future__ import annotations

from typing import Dict

import boto3

from src.common.logging import configure_logging

logger = configure_logging(__name__)


def register_candidate(candidate: Dict[str, str], model_package_group: str, role_arn: str, region: str | None = None) -> str:
    sm = boto3.client("sagemaker", region_name=region)
    response = sm.create_model_package(
        ModelPackageGroupName=model_package_group,
        ModelPackageDescription="AutoPilot selected model",
        InferenceSpecification={
            "Containers": [
                {
                    "Image": candidate.get("Image", "763104351884.dkr.ecr.us-east-1.amazonaws.com/xgboost:1"),
                    "ModelDataUrl": candidate["model_artifacts"],
                }
            ],
            "SupportedContentTypes": ["text/csv", "application/json"],
            "SupportedResponseMIMETypes": ["application/json"],
        },
        ModelApprovalStatus="PendingManualApproval",
        CertifyForMarketplace=False,
    )
    arn = response["ModelPackageArn"]
    logger.info("Registered candidate model package %s", arn)
    return arn
