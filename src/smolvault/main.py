import json
import logging
import os
import urllib.parse
from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from smolvault.cache.cache_manager import CacheManager
from smolvault.clients.aws import S3Client
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.models import FileMetadata, FileTagsDTO, FileUploadDTO

logging.basicConfig(
    level=logging.DEBUG, filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


db_client = DatabaseClient(db_filename=os.environ["SMOLVAULT_DB"])
s3_client = S3Client(bucket_name=os.environ["SMOLVAULT_BUCKET"])
cache = CacheManager(cache_dir=os.environ["SMOLVAULT_CACHE"])
app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/file/upload")
async def upload_file(file: Annotated[UploadFile, File()], tags: str | None = Form(default=None)) -> Response:
    contents = await file.read()
    if file.filename is None:
        raise ValueError("Filename is required")
    file_upload = FileUploadDTO(name=file.filename, size=len(contents), content=contents, tags=tags)
    object_key = s3_client.upload(data=file_upload)
    db_client.add_metadata(file_upload, object_key)
    return Response(
        content=json.dumps(file_upload.model_dump(exclude={"content", "tags"})),
        status_code=201,
        media_type="application/json",
    )


@app.get("/file/{name}")
async def get_file(name: str) -> FileResponse | Response:
    record = db_client.get_metadata(urllib.parse.unquote(name))
    if record is None:
        return Response(content=json.dumps({"error": "File not found"}), status_code=404, media_type="application/json")
    if record.local_path is None:
        content = s3_client.download(record.object_key)
        record.local_path = cache.save_file(record.file_name, content)
        record.cache_timestamp = int(os.path.getmtime(record.local_path))
        db_client.update_metadata(record)

    return FileResponse(path=record.local_path, filename=record.file_name)


@app.get("/file/{name}/metadata")
async def get_file_metadata(name: str) -> FileMetadata | None:
    record: FileMetadataRecord | None = db_client.get_metadata(urllib.parse.unquote(name))
    if record:
        return FileMetadata.model_validate(record.model_dump())
    return None


@app.get("/files")
async def get_files() -> list[FileMetadata]:
    raw_metadata = db_client.get_all_metadata()
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.get("/files/search")
async def search_files(tag: str) -> list[FileMetadata]:
    raw_metadata = db_client.select_metadata_by_tag(tag)
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.patch("/file/{name}/tags")
async def update_file_tags(name: str, tags: FileTagsDTO) -> Response:
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
async def delete_file(name: str) -> Response:
    record: FileMetadataRecord | None = db_client.get_metadata(name)
    if record is None:
        return Response(content=json.dumps({"error": "File not found"}), status_code=404, media_type="application/json")
    s3_client.delete(record.object_key)
    db_client.delete_metadata(record)
    return Response(
        content=json.dumps({"message": "File deleted successfully", "record": record.model_dump()}),
        status_code=200,
        media_type="application/json",
    )
