import json
import os
from typing import Annotated

import chardet
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import Response

from smolvault.clients.aws import S3Client
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.models import FileMetadata, FileUploadDTO

db_client = DatabaseClient(db_filename=os.environ["SMOLVAULT_DB"])
s3_client = S3Client(bucket_name=os.environ["SMOLVAULT_BUCKET"])
app = FastAPI(debug=True)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/file/upload/")
async def upload_file(file: Annotated[UploadFile, File()], tags: Annotated[str, Form()]) -> Response:
    contents = await file.read()
    if file.filename is None:
        raise ValueError("Filename is required")
    file_upload = FileUploadDTO(name=file.filename, size=len(contents), content=contents, tags=tags)
    object_key = s3_client.upload(data=file_upload)
    db_client.add_metadata(file_upload, object_key)
    return Response(
        content=json.dumps(file_upload.model_dump(exclude={"content"})), status_code=201, media_type="application/json"
    )


@app.get("/file/{name}")
async def get_file(name: str) -> Response:
    record = db_client.get_metadata(name)
    if record is None:
        return Response(content=json.dumps({"error": "File not found"}), status_code=404, media_type="application/json")
    content = s3_client.download(record.object_key)
    return Response(content=content, status_code=200, media_type=chardet.detect(content)["encoding"])


@app.get("/file/{name}/metadata")
async def get_file_metadata(name: str) -> FileMetadataRecord | None:
    return db_client.get_metadata(name)


@app.get("/files/")
async def get_files() -> list[FileMetadata]:
    raw_metadata = db_client.get_all_metadata()
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.get("/files/search/")
async def search_files(query: str) -> list[dict[str, str]]:
    return [{"name": "file1"}, {"name": "file2"}]
