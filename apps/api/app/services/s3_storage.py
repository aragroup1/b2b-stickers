import uuid
from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config
from loguru import logger

from app.config import settings


class S3Storage:
    """AWS S3 / Cloudflare R2 object storage."""

    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.client = session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,  # Cloudflare R2 if set, else AWS S3
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.S3_BUCKET

    def _full_key(self, key: str) -> str:
        """Namespace keys under S3_KEY_PREFIX so this project can safely share a
        bucket with other projects (e.g. POD) without key collisions."""
        prefix = (settings.S3_KEY_PREFIX or "").strip("/")
        return f"{prefix}/{key}" if prefix else key

    async def upload(self, local_path: str, key: Optional[str] = None) -> str:
        if key is None:
            ext = Path(local_path).suffix
            key = f"uploads/{uuid.uuid4()}{ext}"
        full = self._full_key(key)
        self.client.upload_file(local_path, self.bucket, full)
        logger.info(f"Uploaded s3://{self.bucket}/{full}")
        return key

    async def get_presigned_url(self, key: str, expiry: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": self._full_key(key)},
            ExpiresIn=expiry,
        )

    def public_url(self, key: str) -> str:
        """Permanent public URL for an uploaded object.

        Requires the bucket to be publicly readable (R2 public bucket / custom
        domain, or an S3 public bucket / CDN) via S3_PUBLIC_BASE_URL. Falls back
        to an *expiring* presigned URL if that isn't configured, with a warning.
        """
        full = self._full_key(key)
        base = settings.S3_PUBLIC_BASE_URL.rstrip("/")
        if base:
            return f"{base}/{full}"
        logger.warning("S3_PUBLIC_BASE_URL not set — returning an EXPIRING presigned URL")
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": full},
            ExpiresIn=86400 * 7,
        )

    def is_configured(self) -> bool:
        """True when a bucket is set (storage usable). Lets callers no-op gracefully."""
        return bool(self.bucket)

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=self._full_key(key))
            return True
        except Exception:
            return False

    async def upload_bytes(self, data: bytes, key: str, content_type: str = "image/jpeg") -> str:
        full = self._full_key(key)
        self.client.put_object(Bucket=self.bucket, Key=full, Body=data, ContentType=content_type)
        logger.info(f"Uploaded s3://{self.bucket}/{full}")
        return key
