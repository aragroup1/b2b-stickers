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
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.S3_BUCKET

    async def upload(self, local_path: str, key: Optional[str] = None) -> str:
        if key is None:
            ext = Path(local_path).suffix
            key = f"uploads/{uuid.uuid4()}{ext}"
        self.client.upload_file(local_path, self.bucket, key)
        logger.info(f"Uploaded s3://{self.bucket}/{key}")
        return key

    async def get_presigned_url(self, key: str, expiry: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiry,
        )
