from pydantic import BaseModel


class FileUpload(BaseModel):
    name: str
    size: int
    content: bytes
    tags: list[str] | None = None
