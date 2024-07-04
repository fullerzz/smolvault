from collections.abc import Sequence

from sqlmodel import Field, Session, SQLModel, create_engine, select

from smolvault.models import FileUploadDTO


class FileMetadataRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_name: str
    file_sha256: str
    size: int
    object_key: str
    link: str
    upload_timestamp: str
    tags: str | None = None
    local_path: str | None = None
    cache_timestamp: int | None = None


class DatabaseClient:
    def __init__(self, db_filename: str) -> None:
        self.engine = create_engine(f"sqlite:///{db_filename}", echo=True)
        SQLModel.metadata.create_all(self.engine)

    def add_metadata(self, file_upload: FileUploadDTO, key: str) -> None:
        file_metadata = FileMetadataRecord(
            file_name=file_upload.name,
            file_sha256=file_upload.file_sha256,
            size=file_upload.size,
            object_key=key,
            link=file_upload.link,
            upload_timestamp=file_upload.upload_timestamp,
            tags=file_upload.cs_tags,
        )
        with Session(self.engine) as session:
            session.add(file_metadata)
            session.commit()

    def get_all_metadata(self) -> Sequence[FileMetadataRecord]:
        with Session(self.engine) as session:
            statement = select(FileMetadataRecord)
            results = session.exec(statement)
            return results.fetchall()

    def get_metadata(self, filename: str) -> FileMetadataRecord | None:
        with Session(self.engine) as session:
            statement = select(FileMetadataRecord).where(FileMetadataRecord.file_name == filename)
            return session.exec(statement).first()
