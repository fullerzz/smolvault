from datetime import datetime

from sqlmodel import Field, Session, SQLModel, create_engine


class FileMetadata(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_name: str
    file_sha256: str
    object_key: str
    link: str
    upload_timestamp: datetime
    tags: str | None = None
    local_path: str | None = None
    cache_timestamp: datetime | None = None


class DatabaseClient:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///file_metadata.db", echo=True)
        SQLModel.metadata.create_all(self.engine)

    def add_metadata(self, file_metadata: FileMetadata) -> None:
        with Session(self.engine) as session:
            session.add(file_metadata)
            session.commit()
