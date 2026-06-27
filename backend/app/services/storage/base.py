from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, key: str, data: BinaryIO, size: int, content_type: str) -> str:
        """Upload a file-like object to storage. Returns the storage key."""
        ...

    @abstractmethod
    async def download_file(self, key: str) -> bytes:
        """Download file content as bytes."""
        ...

    @abstractmethod
    async def download_to_path(self, key: str, local_path: str) -> None:
        """Download file directly to a local path."""
        ...

    @abstractmethod
    async def upload_from_path(self, key: str, local_path: str, content_type: str) -> str:
        """Upload a local file to storage by path. Returns the storage key."""
        ...

    @abstractmethod
    async def get_presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        """Generate a presigned download URL valid for expires_seconds."""
        ...

    @abstractmethod
    async def delete_file(self, key: str) -> None:
        """Delete a file from storage."""
        ...

    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Check whether a file exists in storage."""
        ...
