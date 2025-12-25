from aws_cdk import Stack, aws_sagemaker as sagemaker
from constructs import Construct


class SageMakerStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, project_name: str, execution_role, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        group_name = f"{project_name}-group"
        self.model_package_group = sagemaker.CfnModelPackageGroup(
            self,
            "ModelPackageGroup",
            model_package_group_name=group_name,
            model_package_group_description="Model package group for auto-retrain template",
        )

        # Optional Studio domain placeholder
        # Additional Studio setup can be added via context flags if desired.
