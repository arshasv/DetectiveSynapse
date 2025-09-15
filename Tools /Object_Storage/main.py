import os
import logging
from contextlib import asynccontextmanager
from typing import Annotated
from urllib.parse import unquote

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Path
from fastapi.responses import Response

from Object_storage.base import AbstractStorage
from Object_storage.minio_setup import MinIOStorage as Storage  # MinIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

storage: AbstractStorage = Storage()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await storage.health():
        raise RuntimeError("Storage backend is unhealthy")
    yield

app = FastAPI(title="File Upload & Download API", lifespan=lifespan)

async def get_storage() -> AbstractStorage:
    return storage


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    st: Annotated[AbstractStorage, Depends(get_storage)] = ...,
):
    if not file.filename:
        raise HTTPException(400, "Filename missing")

    content = await file.read()
    reference = await st.upload(
        bucket=os.getenv("STORAGE_BUCKET", "uploads"),
        key=file.filename,
        data=content,
        length=len(content),
        content_type=file.content_type,
    )
    return {"reference": reference, "filename": file.filename, "size": len(content)}


@app.get("/download/{bucket}/{filename:path}")
async def download_file(
    bucket: str = Path(...),
    filename: str = Path(...),
    st: Annotated[AbstractStorage, Depends(get_storage)] = ...,
):
    decoded_filename = unquote(filename)
    if not await st.exists(bucket=bucket, key=decoded_filename):
        raise HTTPException(404, f"File not found: {bucket}/{decoded_filename}")

    content, content_type = await st.download(bucket=bucket, key=decoded_filename)
    headers = {
        "Content-Disposition": f'attachment; filename="{decoded_filename.split("/")[-1]}"'
    }
    return Response(
        content=content,
        media_type=content_type or "application/octet-stream",
        headers=headers,
    )