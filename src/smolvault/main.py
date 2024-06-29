from fastapi import FastAPI

from smolvault.models import FileUpload

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/file/upload/")
async def read_item(file: FileUpload) -> FileUpload:
    return file


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
