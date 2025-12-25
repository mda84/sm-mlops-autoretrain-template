import os

from src.sagemaker.pipelines.run_pipeline import start_pipeline_execution
from src.sagemaker.autopilot.create_job import create_autopilot_job


def lambda_handler(event, context):
    action = os.getenv("TRIGGER_MODE", "pipeline")
    dataset_s3 = event.get("detail", {}).get("object", {}).get("key")
    bucket = os.getenv("BUCKET_NAME")
    if dataset_s3 and not dataset_s3.startswith("s3://"):
        dataset_s3 = f"s3://{bucket}/{dataset_s3}"

    if action == "autopilot":
        job_name = f"autopilot-{os.getenv('ENV', 'dev')}"
        role = os.getenv("SAGEMAKER_ROLE_ARN")
        create_autopilot_job(
            job_name=job_name,
            s3_uri=dataset_s3,
            target_column="label",
            problem_type="classification",
            objective_metric="Accuracy",
            max_candidates=3,
            max_runtime_seconds=3600,
            role_arn=role,
            output_path=f"s3://{bucket}/autopilot/{job_name}",
            region=os.getenv("AWS_REGION", "us-east-1"),
        )
    else:
        start_pipeline_execution(
            dataset_s3=dataset_s3,
            problem_type="classification",
            metric_threshold=0.7,
        )
    return {"status": "triggered"}
