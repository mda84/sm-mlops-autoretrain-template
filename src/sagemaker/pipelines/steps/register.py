from sagemaker.workflow.model_step import ModelStep
from sagemaker.workflow.steps import CacheConfig


def create_register_step(model, model_data: str, role: str, model_package_group: str, approval_status: str = "PendingManualApproval"):
    return ModelStep(
        name="RegisterModel",
        model=model,
        model_data=model_data,
        cache_config=CacheConfig(enable_caching=True, expire_after="30d"),
        approval_status=approval_status,
        model_package_group_name=model_package_group,
        model_metrics=None,
        role=role,
    )
