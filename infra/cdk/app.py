#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.s3_stack import S3Stack
from stacks.iam_stack import IamStack
from stacks.sagemaker_stack import SageMakerStack
from stacks.pipeline_stack import PipelineStack
from stacks.eventbridge_stack import EventBridgeStack
from stacks.monitoring_stack import MonitoringStack


app = cdk.App()

env_name = app.node.try_get_context("env") or "dev"
project_name = app.node.try_get_context("project") or "sm-mlops-autoretrain-template"

s3_stack = S3Stack(app, f"{project_name}-s3", env_name=env_name, project_name=project_name)
iam_stack = IamStack(
    app, f"{project_name}-iam", env_name=env_name, project_name=project_name, bucket=s3_stack.bucket
)

sm_stack = SageMakerStack(
    app,
    f"{project_name}-sagemaker",
    env_name=env_name,
    project_name=project_name,
    execution_role=iam_stack.sagemaker_role,
)

pipeline_stack = PipelineStack(
    app,
    f"{project_name}-pipeline",
    env_name=env_name,
    project_name=project_name,
    bucket=s3_stack.bucket,
    execution_role=iam_stack.sagemaker_role,
)

event_stack = EventBridgeStack(
    app,
    f"{project_name}-events",
    env_name=env_name,
    project_name=project_name,
    bucket=s3_stack.bucket,
    lambda_role=iam_stack.lambda_role,
    sagemaker_role=iam_stack.sagemaker_role,
)

MonitoringStack(
    app,
    f"{project_name}-monitoring",
    env_name=env_name,
    project_name=project_name,
)

app.synth()
