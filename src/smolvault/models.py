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
    user_id: int
    upload_timestamp: str = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")).isoformat())
    tags: str | None  # comma separated tags

    @computed_field  # type: ignore
    @cached_property
    def file_sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()

    @computed_field  # type: ignore
    @cached_property
    def link(self) -> str:
        return f"http://pi.local:8000/file/original?filename={urllib.parse.quote_plus(self.name)}"

    @computed_field  # type: ignore
    @cached_property
    def tags_list(self) -> list[str]:
        if self.tags is None or self.tags == "":
            return []
        parts = self.tags.split(",")
        return [part.strip() for part in parts]


class FileTagsDTO(BaseModel):
    tags: list[str]

    @computed_field  # type: ignore
    @cached_property
    def tags_str(self) -> str:
        combined_tags = ""
        for tag in self.tags:
            combined_tags += tag.strip() + ","
        return combined_tags[:-1]


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
