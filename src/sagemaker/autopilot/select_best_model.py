from __future__ import annotations

import json
from typing import Dict

import boto3

from src.common.logging import configure_logging

logger = configure_logging(__name__)


def select_best_candidate(job_name: str, region: str | None = None) -> Dict[str, str]:
    client = boto3.client("sagemaker", region_name=region)
    candidates = client.list_auto_ml_candidates(AutoMLJobName=job_name, StatusEquals="Completed")[
        "Candidates"
    ]
    if not candidates:
        raise RuntimeError("No completed candidates")
    best = sorted(candidates, key=lambda c: c["FinalAutoMLJobObjectiveMetric"]["Value"], reverse=True)[0]
    result = {
        "candidate_name": best["CandidateName"],
        "metric": best["FinalAutoMLJobObjectiveMetric"]["MetricName"],
        "value": best["FinalAutoMLJobObjectiveMetric"]["Value"],
        "model_artifacts": best["InferenceContainers"][0]["ModelDataUrl"],
    }
    with open("best_candidate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    logger.info("Best candidate %s with metric %s=%s", result["candidate_name"], result["metric"], result["value"])
    return result
