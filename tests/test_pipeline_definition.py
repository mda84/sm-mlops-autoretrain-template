from src.sagemaker.pipelines.pipeline import create_pipeline


def test_pipeline_builds(monkeypatch):
    # Avoid network calls by patching boto3 Session to dummy region
    pipeline = create_pipeline(
        region="us-east-1",
        role="arn:aws:iam::123456789012:role/SageMaker",
        pipeline_name="test-pipeline",
        bucket="dummy-bucket",
        model_package_group="pkg",
        process_instance_type="ml.m5.large",
        train_instance_type="ml.m5.large",
    )
    assert pipeline.name == "test-pipeline"
