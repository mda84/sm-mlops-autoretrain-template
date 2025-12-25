from aws_cdk import Duration, RemovalPolicy, Stack, aws_s3 as s3
from constructs import Construct


class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, project_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = f"{project_name}-{env_name}"
        self.bucket = s3.Bucket(
            self,
            "DataBucket",
            bucket_name=bucket_name,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ExpireOldArtifacts",
                    enabled=True,
                    expiration=Duration.days(90),
                )
            ],
        )
