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
    tags: str | None  # comma separated tags

    @computed_field  # type: ignore
    @cached_property
    def file_sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()

    @computed_field  # type: ignore
    @cached_property
    def link(self) -> str:
        return f"http://pi.local:1234/file/{urllib.parse.quote_plus(self.name)}"

    @computed_field  # type: ignore
    @cached_property
    def tags_list(self) -> list[str]:
        if self.tags is None or self.tags == "":
            return []
        parts = self.tags.split(",")
        return [part.strip() for part in parts]


class FileMetadata(BaseModel):
    name: str = Field(alias="file_name")
    size: int
    upload_timestamp: str
    link: str
    file_sha256: str
    tags: str | None = Field(default=None, exclude=True)

    @computed_field  # type: ignore
    @cached_property
    def tags_list(self) -> list[str] | None:
        if self.tags is not None:
            parts = self.tags.split(",")
            return [part.strip() for part in parts]
