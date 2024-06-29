from sqlmodel import Field, Session, SQLModel, create_engine

from smolvault.models import FileUploadDTO


class FileMetadata(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_name: str
    file_sha256: str
    object_key: str
    link: str
    upload_timestamp: str
    tags: str | None = None
    local_path: str | None = None
    cache_timestamp: int | None = None


class DatabaseClient:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///file_metadata.db", echo=True)
        SQLModel.metadata.create_all(self.engine)

    def add_metadata(self, file_upload: FileUploadDTO, key: str) -> None:
        file_metadata = FileMetadata(
            file_name=file_upload.name,
            file_sha256=file_upload.file_sha256,
            object_key=key,
            link=file_upload.link,
            upload_timestamp=file_upload.upload_timestamp,
            tags=file_upload.cs_tags,
        )
        with Session(self.engine) as session:
            session.add(file_metadata)
            session.commit()
