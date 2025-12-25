from aws_cdk import Stack, aws_cloudwatch as cloudwatch
from constructs import Construct


class MonitoringStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, project_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.log_alarm = cloudwatch.Alarm(
            self,
            "PlaceholderAlarm",
            metric=cloudwatch.Metric(
                namespace="MLOpsTemplate",
                metric_name="DummyMetric",
                period=cloudwatch.Duration.minutes(5),
            ),
            threshold=1,
            evaluation_periods=1,
        )
