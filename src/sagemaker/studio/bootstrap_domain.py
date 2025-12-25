from __future__ import annotations

import boto3

from src.common.logging import configure_logging

logger = configure_logging(__name__)


def ensure_studio_domain(domain_name: str, region: str | None = None):
    sm = boto3.client("sagemaker", region_name=region)
    domains = sm.list_domains()["Domains"]
    for dom in domains:
        if dom["DomainName"] == domain_name:
            logger.info("Studio domain %s already exists", domain_name)
            return dom
    logger.info("Studio domain %s not found - create manually as needed", domain_name)
    return None
