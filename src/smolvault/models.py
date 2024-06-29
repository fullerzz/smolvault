from datetime import datetime

from pydantic import BaseModel


class FileUpload(BaseModel):
    name: str
    size: int
    content: bytes
    tags: list[str] | None = None


class FileMetadata(BaseModel):
    file_name: str
    file_sha256: str
    object_key: str
    link: str
    upload_timestamp: datetime
    tags: list[str] | None
    local_path: str | None
    cache_timestamp: datetime | None
