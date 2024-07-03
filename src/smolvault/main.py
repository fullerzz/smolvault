import os
from typing import Any

from fastapi import FastAPI, UploadFile

from smolvault.clients.aws import S3Client
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.models import FileMetadata, FileUploadDTO

db_client = DatabaseClient(db_filename=os.environ["SMOLVAULT_DB"])
s3_client = S3Client(bucket=os.environ["SMOLVAULT_BUCKET"])
app = FastAPI(debug=True)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/file/upload/")
async def upload_file(file: UploadFile) -> dict[str, Any]:
    contents = await file.read()
    if file.filename is None:
        raise ValueError("Filename is required")
    file_upload = FileUploadDTO(name=file.filename, size=len(contents), content=contents)
    object_key = await s3_client.upload(data=file_upload)
    db_client.add_metadata(file_upload, object_key)
    # TODO: Return 201 status code
    return file_upload.model_dump(exclude={"content"})


@app.get("/file/{name}")
async def get_file(name: str) -> dict[str, str]:
    return {"name": name}


@app.get("/file/{name}/metadata")
async def get_file_metadata(name: str) -> FileMetadataRecord | None:
    return db_client.select_metadata(name)


@app.get("/files/")
async def get_files() -> list[FileMetadata]:
    raw_metadata = db_client.get_all_metadata()
    print(raw_metadata, locals())
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.get("/files/search/")
async def search_files(query: str) -> list[dict[str, str]]:
    return [{"name": "file1"}, {"name": "file2"}]
