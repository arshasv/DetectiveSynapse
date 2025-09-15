from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Tuple

class AbstractStorage(ABC):
    """
    Storage-agnostic interface.
    """

    @abstractmethod
    async def upload(
        self,
        *,
        bucket: str,
        key: str,
        data: BinaryIO,
        length: int,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload bytes and return a stable reference (URL / path / etag).
        """
        ...

    @abstractmethod
    async def download(
        self,
        *,
        bucket: str,
        key: str,
    ) -> Tuple[bytes, Optional[str]]:
        """
        Download file and return (content, content_type).
        """
        ...

    @abstractmethod
    async def exists(
        self,
        *,
        bucket: str,
        key: str,
    ) -> bool:
        """
        Check if file exists.
        """
        ...

    @abstractmethod
    async def health(self) -> bool:
        """
        Lightweight health-check.
        """
        ...