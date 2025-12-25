from aws_cdk import Stack
from constructs import Construct


class PipelineStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, project_name: str, bucket, execution_role, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Pipeline is authored via CLI; stack keeps bucket and role available.
        self.bucket = bucket
        self.execution_role = execution_role
