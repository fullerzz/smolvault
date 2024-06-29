from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field


class FileUpload(BaseModel):
    name: str
    size: int
    content: bytes
    upload_timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    tags: list[str] | None = None
