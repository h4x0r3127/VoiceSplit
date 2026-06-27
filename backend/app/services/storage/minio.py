import io
import asyncio
from datetime import timedelta
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.services.storage.base import StorageService
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MinioStorageService(StorageService):
    def __init__(self) -> None:
        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self._bucket = settings.MINIO_BUCKET

    def ensure_bucket_exists(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                logger.info("minio_bucket_created", bucket=self._bucket)
            else:
                logger.debug("minio_bucket_exists", bucket=self._bucket)
        except S3Error as exc:
            logger.error("minio_bucket_init_failed", error=str(exc))
            raise

    async def upload_file(self, key: str, data: BinaryIO, size: int, content_type: str) -> str:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.put_object(
                self._bucket, key, data, size, content_type=content_type
            ),
        )
        logger.info("minio_upload_complete", key=key, size=size)
        return key

    async def download_file(self, key: str) -> bytes:
        loop = asyncio.get_event_loop()

        def _download() -> bytes:
            response = self._client.get_object(self._bucket, key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        data = await loop.run_in_executor(None, _download)
        logger.info("minio_download_complete", key=key, bytes=len(data))
        return data

    async def download_to_path(self, key: str, local_path: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.fget_object(self._bucket, key, local_path),
        )
        logger.info("minio_download_to_path", key=key, local_path=local_path)

    async def upload_from_path(self, key: str, local_path: str, content_type: str) -> str:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.fput_object(
                self._bucket, key, local_path, content_type=content_type
            ),
        )
        logger.info("minio_upload_from_path", key=key, local_path=local_path)
        return key

    async def get_presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            lambda: self._client.presigned_get_object(
                self._bucket, key, expires=timedelta(seconds=expires_seconds)
            ),
        )
        return url

    async def delete_file(self, key: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.remove_object(self._bucket, key),
        )
        logger.info("minio_delete_complete", key=key)

    async def file_exists(self, key: str) -> bool:
        loop = asyncio.get_event_loop()

        def _stat() -> bool:
            try:
                self._client.stat_object(self._bucket, key)
                return True
            except S3Error:
                return False

        return await loop.run_in_executor(None, _stat)
