from aws_cdk import Duration, Stack, aws_events as events, aws_events_targets as targets, aws_lambda as _lambda
from constructs import Construct


class EventBridgeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        project_name: str,
        bucket,
        lambda_role,
        sagemaker_role,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_fn = _lambda.Function(
            self,
            "TriggerLambda",
            code=_lambda.Code.from_asset("../../src"),
            handler="sagemaker.triggers.lambda_handler.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            timeout=Duration.minutes(5),
            role=lambda_role,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "PIPELINE_NAME": f"{project_name}-pipeline",
                "SAGEMAKER_ROLE_ARN": sagemaker_role.role_arn,
            },
        )

        schedule_rule = events.Rule(
            self,
            "MonthlyRetrainRule",
            schedule=events.Schedule.rate(Duration.days(30)),
        )
        schedule_rule.add_target(targets.LambdaFunction(lambda_fn))

        s3_rule = events.Rule(
            self,
            "S3DatasetRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket": {"name": [bucket.bucket_name]}},
            ),
        )
        s3_rule.add_target(targets.LambdaFunction(lambda_fn))
