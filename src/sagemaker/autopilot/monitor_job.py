from __future__ import annotations

import time

import boto3

from src.common.logging import configure_logging

logger = configure_logging(__name__)


def monitor_job(job_name: str, region: str | None = None, poll: int = 30):
    client = boto3.client("sagemaker", region_name=region)
    while True:
        resp = client.describe_auto_ml_job_v2(AutoMLJobName=job_name)
        status = resp["AutoMLJobStatus"]
        sec_status = resp.get("AutoMLJobSecondaryStatus", "")
        logger.info("AutoPilot job %s status: %s %s", job_name, status, sec_status)
        if status in {"Completed", "Failed", "Stopped"}:
            break
        time.sleep(poll)
    return resp
