from __future__ import annotations

import json
from typing import Dict


def schedule_rule(project_name: str) -> Dict:
    return {
        "Name": f"{project_name}-schedule",
        "ScheduleExpression": "rate(30 days)",
        "State": "ENABLED",
    }


def s3_event_rule(bucket: str, datasets_prefix: str) -> Dict:
    return {
        "Name": f"{bucket}-datasets",
        "EventPattern": json.dumps(
            {
                "source": ["aws.s3"],
                "detail-type": ["Object Created"],
                "detail": {"bucket": {"name": [bucket]}, "object": {"key": [{"prefix": datasets_prefix}] }},
            }
        ),
        "State": "ENABLED",
    }
