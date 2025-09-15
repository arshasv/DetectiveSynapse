import os
from io import BytesIO
from typing import Optional, Tuple

from minio import Minio
from minio.error import S3Error

from Object_storage.base import AbstractStorage


class MinIOStorage(AbstractStorage):
    def __init__(self) -> None:
        self.client = Minio(
            endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
            secure=False,
        )
        self.bucket = os.getenv("STORAGE_BUCKET", "uploads")

    async def upload(
        self,
        *,
        bucket: str,
        key: str,
        data: bytes,
        length: int,
        content_type: Optional[str] = None,
    ) -> str:
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
            self.client.put_object(
                bucket, key, BytesIO(data), length=length, content_type=content_type
            )
            return f"/{bucket}/{key}"
        except S3Error as exc:
            raise RuntimeError(str(exc)) from exc

    async def download(self, *, bucket: str, key: str) -> Tuple[bytes, Optional[str]]:
        try:
            resp = self.client.get_object(bucket, key)
            data = resp.read()
            ctype = resp.headers.get("content-type")
            return data, ctype
        except S3Error as exc:
            if exc.code == "NoSuchKey":
                raise FileNotFoundError(key)
            raise

    async def exists(self, *, bucket: str, key: str) -> bool:
        try:
            self.client.stat_object(bucket, key)
            return True
        except S3Error as exc:
            return exc.code != "NoSuchKey"

    async def health(self) -> bool:
        return self.client.bucket_exists(self.bucket)