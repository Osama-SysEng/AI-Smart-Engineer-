"""Storage service abstraction."""
import os
import shutil
import re
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Abstract storage service supporting local and S3."""

    def __init__(self):
        self.settings = get_settings()
        self.storage_type = self.settings.STORAGE_TYPE
        self.base_path = Path(self.settings.STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, document_id: str) -> str:
        """Save uploaded file and return path."""
        if self.storage_type == "local":
            return await self._save_local(file, document_id)
        elif self.storage_type == "s3":
            return await self._save_s3(file, document_id)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    async def _save_local(self, file: UploadFile, document_id: str) -> str:
        """Save to local filesystem."""
        # Organize by date
        from datetime import datetime
        now = datetime.now()
        subdir = self.base_path / f"{now.year}/{now.month:02d}"
        subdir.mkdir(parents=True, exist_ok=True)

        filename = file.filename or "upload"
        ext = Path(filename).suffix.lower()
        if ext not in {e.lower() for e in self.settings.ALLOWED_EXTENSIONS}:
            raise ValueError(f"File type not allowed: {ext}")

        max_bytes = self.settings.MAX_FILE_SIZE_MB * 1024 * 1024
        filepath = (subdir / f"{document_id}{ext}").resolve()
        if subdir.resolve() not in filepath.parents:
            raise ValueError("Invalid storage path")

        total = 0
        with open(filepath, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    f.close()
                    filepath.unlink(missing_ok=True)
                    raise ValueError(f"File exceeds maximum size of {self.settings.MAX_FILE_SIZE_MB} MB")
                f.write(chunk)

        logger.info("File saved locally", path=str(filepath), size=total)
        return str(filepath)

    async def _save_s3(self, file: UploadFile, document_id: str) -> str:
        """Save to S3."""
        import boto3
        s3 = boto3.client("s3")
        bucket = self.settings.AWS_S3_BUCKET
        key = f"documents/{document_id}/{file.filename}"

        content = await file.read(self.settings.MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
        if len(content) > self.settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File exceeds maximum size of {self.settings.MAX_FILE_SIZE_MB} MB")
        s3.put_object(Bucket=bucket, Key=key, Body=content)

        logger.info("File saved to S3", bucket=bucket, key=key)
        return f"s3://{bucket}/{key}"

    def get_file(self, path: str) -> bytes:
        """Get file content."""
        if self.storage_type == "local":
            with open(path, "rb") as f:
                return f.read()
        elif self.storage_type == "s3":
            import boto3
            s3 = boto3.client("s3")
            bucket, key = path.replace("s3://", "").split("/", 1)
            response = s3.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()

    def delete_file(self, path: str) -> bool:
        """Delete file."""
        try:
            if self.storage_type == "local":
                os.remove(path)
            elif self.storage_type == "s3":
                import boto3
                s3 = boto3.client("s3")
                bucket, key = path.replace("s3://", "").split("/", 1)
                s3.delete_object(Bucket=bucket, Key=key)
            return True
        except Exception as e:
            logger.error("Failed to delete file", error=str(e), path=path)
            return False
