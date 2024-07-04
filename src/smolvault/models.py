import hashlib
import urllib.parse
from datetime import datetime
from functools import cached_property
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, computed_field


class FileUploadDTO(BaseModel):
    name: str
    size: int
    content: bytes
    upload_timestamp: str = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")).isoformat())
    tags: str  # comma separataed tags

    @computed_field  # type: ignore
    @cached_property
    def file_sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()

    @computed_field  # type: ignore
    @cached_property
    def link(self) -> str:
        return f"http://pi.local:1234/file/{urllib.parse.quote_plus(self.name)}"


class FileMetadata(BaseModel):
    name: str = Field(alias="file_name")
    size: int
    upload_timestamp: str
    link: str
    file_sha256: str
    cs_tags: str | None = Field(default=None, exclude=True)

    @computed_field  # type: ignore
    @cached_property
    def tags(self) -> list[str] | None:
        return self.cs_tags.split(",") if self.cs_tags else None
