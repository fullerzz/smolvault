from fastapi import FastAPI, UploadFile
from rich import print

from smolvault.clients.database import DatabaseClient
from smolvault.models import FileUpload

db_client = DatabaseClient()
app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/file/upload/")
async def upload_file(file: UploadFile) -> FileUpload:
    print(file)
    contents = await file.read()
    if file.filename is None:
        raise ValueError("Filename is required")
    file_upload = FileUpload(name=file.filename, size=len(contents), content=contents)
    # TODO: Upload to S3 using aws client
    # TODO: Add metadata to database
    return file_upload


@app.get("/file/{name}")
async def get_file(name: str) -> dict[str, str]:
    return {"name": name}


@app.get("/file/{name}/metadata")
async def get_file_metadata(name: str) -> dict[str, int | str | list[str]]:
    return {"name": name, "size": 100, "tags": ["tag1", "tag2"]}


@app.get("/files/")
async def get_files() -> list[dict[str, str]]:
    return [{"name": "file1"}, {"name": "file2"}]


@app.get("/files/search/")
async def search_files(query: str) -> list[dict[str, str]]:
    return [{"name": "file1"}, {"name": "file2"}]
