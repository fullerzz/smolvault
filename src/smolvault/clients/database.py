from collections.abc import Sequence

from sqlmodel import Field, Session, SQLModel, create_engine, select

from smolvault.auth.models import NewUserDTO
from smolvault.config import get_settings
from smolvault.models import FileUploadDTO


class UserInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: str | None = None
    full_name: str | None = None


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
    user_id: int | None = Field(default=None, foreign_key="userinfo.id", index=True)


class FileTag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tag_name: str = Field(index=True)
    file_id: int | None = Field(default=None, foreign_key="filemetadatarecord.id")


class DatabaseClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.engine = create_engine(f"sqlite:///{self.settings.smolvault_db}", echo=False)
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
            user_id=file_upload.user_id,
        )
        with Session(self.engine) as session:
            session.add(file_metadata)
            session.commit()
            for tag in file_upload.tags_list:
                session.add(FileTag(tag_name=tag, file_id=file_metadata.id))
            session.commit()

    def get_all_metadata(self, user_id: int) -> Sequence[FileMetadataRecord]:
        with Session(self.engine) as session:
            statement = select(FileMetadataRecord).where(FileMetadataRecord.user_id == user_id)
            results = session.exec(statement)
            return results.fetchall()

    def get_metadata(self, filename: str, user_id: int) -> FileMetadataRecord | None:
        with Session(self.engine) as session:
            statement = (
                select(FileMetadataRecord)
                .where(FileMetadataRecord.file_name == filename)
                .where(FileMetadataRecord.user_id == user_id)
            )
            return session.exec(statement).first()

    def select_metadata_by_tag(self, tag: str, user_id: int) -> Sequence[FileMetadataRecord]:
        with Session(self.engine) as session:
            statement = (
                select(FileMetadataRecord)
                .where(FileTag.file_id == FileMetadataRecord.id)
                .where(FileTag.tag_name == tag)
                .where(FileMetadataRecord.user_id == user_id)
            )
            results = session.exec(statement)
            return results.fetchall()

    def update_metadata(self, record: FileMetadataRecord) -> None:
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)

    def delete_metadata(self, record: FileMetadataRecord, user_id: int) -> None:
        with Session(self.engine) as session:
            session.delete(record)
            session.commit()
            statement = select(FileTag).where(FileTag.file_id == record.id).where(FileMetadataRecord.user_id == user_id)
            tags = session.exec(statement)
            for tag in tags:
                session.delete(tag)
            session.commit()

    def get_user(self, username: str) -> UserInfo | None:
        with Session(self.engine) as session:
            statement = select(UserInfo).where(UserInfo.username == username)
            return session.exec(statement).first()

    def add_user(self, user: NewUserDTO) -> None:
        user_info = UserInfo(
            username=user.username,
            hashed_password=user.hashed_password,
            email=user.email,
            full_name=user.full_name,
        )
        with Session(self.engine) as session:
            session.add(user_info)
            session.commit()
            session.refresh(user_info)
