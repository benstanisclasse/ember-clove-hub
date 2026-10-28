"""S3-compatible object storage for generated creatives.

Works with Garage (default, self-hosted in the stack), Cloudflare R2 or AWS S3 --
switching is only a matter of ``S3_*`` environment variables. Path-style addressing
is used everywhere, which all three support.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, BinaryIO

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config import Settings, get_settings


def make_client(settings: Settings) -> Any:
    """Build a boto3 S3 client for the configured provider."""
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        region_name="auto" if settings.storage_provider == "r2" else settings.s3_region,
        aws_access_key_id=settings.s3_access_key_id.get_secret_value() or None,
        aws_secret_access_key=settings.s3_secret_access_key.get_secret_value() or None,
        config=BotoConfig(
            s3={"addressing_style": "path"},
            retries={"max_attempts": 5, "mode": "standard"},
            connect_timeout=5,
            read_timeout=60,
        ),
    )


class ObjectStore:
    """Thin wrapper over one bucket."""

    def __init__(self, settings: Settings | None = None, client: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self.bucket = self.settings.s3_bucket
        self.client = client or make_client(self.settings)

    def ping(self) -> None:
        """Raise if the bucket is unreachable or credentials are wrong."""
        self.client.head_bucket(Bucket=self.bucket)

    def ensure_bucket(self) -> bool:
        """Create the bucket if missing. Returns True if it was created."""
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return False
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") not in ("404", "NoSuchBucket", "NotFound"):
                raise
        self.client.create_bucket(Bucket=self.bucket)
        return True

    def put(self, key: str, body: bytes | BinaryIO, content_type: str) -> str:
        """Upload an object and return its URL (public if configured, else ``s3://``)."""
        self.client.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType=content_type)
        return self.url_for(key)

    def get_bytes(self, key: str) -> bytes:
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()  # type: ignore[no-any-return]

    def url_for(self, key: str) -> str:
        base = self.settings.s3_public_base_url.rstrip("/")
        return f"{base}/{key}" if base else f"s3://{self.bucket}/{key}"

    def presigned_get(self, key: str, ttl_seconds: int | None = None) -> str:
        """Time-limited download URL (for handing files to ad platforms)."""
        return self.client.generate_presigned_url(  # type: ignore[no-any-return]
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=ttl_seconds or self.settings.s3_presign_ttl_seconds,
        )


@lru_cache
def get_store() -> ObjectStore:
    return ObjectStore()
