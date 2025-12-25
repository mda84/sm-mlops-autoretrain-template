from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet


def create_condition_step(evaluate_step, metric_name: str, threshold: float, register_step):
    cond = ConditionGreaterThanOrEqualTo(
        left=JsonGet(
            step_name=evaluate_step.name,
            property_file=evaluate_step.property_files[0],
            json_path=f"metrics.{metric_name}",
        ),
        right=threshold,
    )
    return ConditionStep(
        name="MetricThresholdCheck",
        conditions=[cond],
        if_steps=[register_step],
        else_steps=[],
    )
