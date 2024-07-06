from collections.abc import Sequence

from sqlmodel import Field, Session, SQLModel, create_engine, select

from smolvault.config import get_settings
from smolvault.models import FileUploadDTO


class FileMetadataRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_name: str = Field(index=True)
    file_sha256: str
    size: int
    object_key: str
    link: str
    upload_timestamp: str
    tags: str | None
    local_path: str | None = None
    cache_timestamp: int | None = None


class FileTag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tag_name: str = Field(index=True)
    file_id: int | None = Field(default=None, foreign_key="filemetadatarecord.id")


class DatabaseClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.engine = create_engine(f"sqlite:///{self.settings.smolvault_db}", echo=True)
        SQLModel.metadata.create_all(self.engine)

    def add_metadata(self, file_upload: FileUploadDTO, key: str) -> None:
        file_metadata = FileMetadataRecord(
            file_name=file_upload.name,
            file_sha256=file_upload.file_sha256,
            size=file_upload.size,
            object_key=key,
            link=file_upload.link,
            upload_timestamp=file_upload.upload_timestamp,
            tags=file_upload.tags,
        )
        with Session(self.engine) as session:
            session.add(file_metadata)
            session.commit()
            for tag in file_upload.tags_list:
                session.add(FileTag(tag_name=tag, file_id=file_metadata.id))
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

    def select_metadata_by_tag(self, tag: str) -> Sequence[FileMetadataRecord]:
        with Session(self.engine) as session:
            statement = (
                select(FileMetadataRecord)
                .where(FileTag.file_id == FileMetadataRecord.id)
                .where(FileTag.tag_name == tag)
            )
            results = session.exec(statement)
            return results.fetchall()

    def update_metadata(self, record: FileMetadataRecord) -> None:
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)

    def delete_metadata(self, record: FileMetadataRecord) -> None:
        with Session(self.engine) as session:
            session.delete(record)
            session.commit()
            statement = select(FileTag).where(FileTag.file_id == record.id)
            tags = session.exec(statement)
            for tag in tags:
                session.delete(tag)
            session.commit()
