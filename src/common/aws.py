from __future__ import annotations

import logging
import os
import pathlib
import shutil
from typing import Tuple

import boto3
from botocore.exceptions import NoCredentialsError

logger = logging.getLogger(__name__)


def get_boto3_session() -> boto3.session.Session:
    profile = os.getenv("AWS_PROFILE")
    region = os.getenv("AWS_REGION")
    try:
        if profile:
            return boto3.Session(profile_name=profile, region_name=region)
        return boto3.Session(region_name=region)
    except NoCredentialsError as exc:
        raise RuntimeError("AWS credentials not configured") from exc


def parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    if not s3_uri.startswith("s3://"):
        raise ValueError("S3 URI must start with s3://")
    parts = s3_uri[5:].split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix


def s3_upload_dir(local_dir: str | pathlib.Path, s3_uri: str) -> None:
    session = get_boto3_session()
    s3 = session.resource("s3")
    bucket_name, prefix = parse_s3_uri(s3_uri)
    local_path = pathlib.Path(local_dir)
    if not local_path.exists():
        raise FileNotFoundError(f"Local directory {local_dir} not found")
    for file_path in local_path.rglob("*"):
        if file_path.is_file():
            rel = file_path.relative_to(local_path)
            key = f"{prefix.rstrip('/')}/{rel.as_posix()}"
            logger.info("Uploading %s to s3://%s/%s", file_path, bucket_name, key)
            s3.Object(bucket_name, key).upload_file(str(file_path))


def s3_download_dir(s3_uri: str, local_dir: str | pathlib.Path) -> None:
    session = get_boto3_session()
    s3 = session.resource("s3")
    bucket_name, prefix = parse_s3_uri(s3_uri)
    bucket = s3.Bucket(bucket_name)
    local_path = pathlib.Path(local_dir)
    if local_path.exists():
        shutil.rmtree(local_path)
    local_path.mkdir(parents=True, exist_ok=True)
    for obj in bucket.objects.filter(Prefix=prefix.rstrip("/") + "/"):
        target = local_path / pathlib.Path(obj.key).relative_to(prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Downloading s3://%s/%s to %s", bucket_name, obj.key, target)
        bucket.download_file(obj.key, str(target))
