import json
import logging
import pathlib
import sys
import urllib.parse
from logging.handlers import RotatingFileHandler
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response

from smolvault.auth import User, get_current_user
from smolvault.cache.cache_manager import CacheManager
from smolvault.clients.aws import S3Client
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.config import Settings, get_settings
from smolvault.models import FileMetadata, FileTagsDTO, FileUploadDTO

logging.basicConfig(
    handlers=[RotatingFileHandler("app.log", maxBytes=100_000, backupCount=10), logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="smolvault")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


settings: Settings = get_settings()
s3_client = S3Client(bucket_name=settings.smolvault_bucket)
cache = CacheManager(cache_dir=settings.smolvault_cache)


@app.get("/")
async def read_root(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@app.post("/file/upload")
async def upload_file(
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
    file: Annotated[UploadFile, File()],
    tags: str | None = Form(default=None),
) -> Response:
    contents = await file.read()
    if file.filename is None:
        logger.error("Filename not received in request")
        raise ValueError("Filename is required")
    file_upload = FileUploadDTO(name=file.filename, size=len(contents), content=contents, tags=tags)
    logger.info("Uploading file to S3 with name %s", file_upload.name)
    object_key = s3_client.upload(data=file_upload)
    db_client.add_metadata(file_upload, object_key)
    return Response(
        content=json.dumps(file_upload.model_dump(exclude={"content", "tags"})),
        status_code=201,
        media_type="application/json",
    )


@app.get("/file/original")
async def get_file(
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)], filename: str, background_tasks: BackgroundTasks
) -> Response:
    record = db_client.get_metadata(filename)
    if record is None:
        logger.info("File not found: %s", filename)
        return Response(content=json.dumps({"error": "File not found"}), status_code=404, media_type="application/json")
    if record.local_path is None or cache.file_exists(record.file_name) is False:
        logger.info("File %s not found in cache, downloading from S3", filename)
        content = s3_client.download(record.object_key)
        record.local_path = cache.save_file(record.file_name, content)
        record.cache_timestamp = int(pathlib.Path(record.local_path).stat().st_mtime)
        logger.info("Saved file %s at time %d", record.local_path, record.cache_timestamp)
        background_tasks.add_task(db_client.update_metadata, record)
    logger.info("Serving file %s from cache", record.file_name)
    return FileResponse(path=record.local_path, filename=record.file_name)


@app.get("/file/{name}/metadata")
async def get_file_metadata(
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)], name: str
) -> FileMetadata | None:
    record: FileMetadataRecord | None = db_client.get_metadata(urllib.parse.unquote(name))
    if record:
        return FileMetadata.model_validate(record.model_dump())
    return None


@app.get("/files")
async def get_files(db_client: Annotated[DatabaseClient, Depends(DatabaseClient)]) -> list[FileMetadata]:
    raw_metadata = db_client.get_all_metadata()
    logger.info("Retrieved %d records from database", len(raw_metadata))
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.get("/files/search")
async def search_files(db_client: Annotated[DatabaseClient, Depends(DatabaseClient)], tag: str) -> list[FileMetadata]:
    raw_metadata = db_client.select_metadata_by_tag(tag)
    logger.info("Retrieved %d records from database with tag %s", len(raw_metadata), tag)
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.patch("/file/{name}/tags")
async def update_file_tags(
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)], name: str, tags: FileTagsDTO
) -> Response:
    record: FileMetadataRecord | None = db_client.get_metadata(name)
    if record is None:
        return Response(content=json.dumps({"error": "File not found"}), status_code=404, media_type="application/json")

    record.tags = tags.tags_str
    db_client.update_metadata(record)
    file_metadata = FileMetadata.model_validate(record.model_dump())
    return Response(
        content=json.dumps({"message": "Tags updated successfully", "record": file_metadata.model_dump()}),
        status_code=200,
        media_type="application/json",
    )


@app.delete("/file/{name}")
async def delete_file(
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)], name: str, background_tasks: BackgroundTasks
) -> Response:
    record: FileMetadataRecord | None = db_client.get_metadata(name)
    if record is None:
        return Response(content=json.dumps({"error": "File not found"}), status_code=404, media_type="application/json")
    s3_client.delete(record.object_key)
    db_client.delete_metadata(record)
    if record.local_path:
        background_tasks.add_task(cache.delete_file, record.local_path)
    return Response(
        content=json.dumps({"message": "File deleted successfully", "record": record.model_dump()}),
        status_code=200,
        media_type="application/json",
    )
