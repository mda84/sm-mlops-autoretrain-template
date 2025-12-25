from aws_cdk import Stack, aws_iam as iam
from constructs import Construct


class IamStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, project_name: str, bucket, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_arn = bucket.bucket_arn
        s3_prefix_arn = f"{s3_arn}/*"

        self.sagemaker_role = iam.Role(
            self,
            "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess"),
            ],
        )
        self.sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[s3_arn, s3_prefix_arn],
            )
        )

        self.lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
        )
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[s3_arn, s3_prefix_arn],
            )
        )
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "sagemaker:StartPipelineExecution",
                    "sagemaker:CreateAutoMLJobV2",
                    "sagemaker:DescribeAutoMLJobV2",
                ],
                resources=["*"],
            )
        )
