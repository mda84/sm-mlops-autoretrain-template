import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_key = value.strip("${}")
        return os.getenv(env_key, "")
    if isinstance(value, str) and "${" in value:
        parts = value.split("${")
        base = parts[0]
        env_part = parts[1].split("}")[0]
        rest = parts[1].split("}")[1]
        return base + os.getenv(env_part, "") + rest
    if isinstance(value, dict):
        return {k: resolve_env(v) for k, v in value.items()}
    return value


@dataclass
class ProjectConfig:
    project_name: str
    aws_region: str
    s3_bucket_name: str
    sagemaker_execution_role_arn: str
    model_package_group_name: str
    default_tags: dict
    environment_name: str

    @classmethod
    def load(cls, path: str | Path, tags_path: str | Path | None = None) -> "ProjectConfig":
        raw = load_yaml(path)
        tags = load_yaml(tags_path) if tags_path else {}
        raw["default_tags"] = raw.get("default_tags", {})
        if raw["default_tags"] == "${tags}":
            raw["default_tags"] = tags
        resolved = {k: resolve_env(v) for k, v in raw.items()}
        return cls(**resolved)
