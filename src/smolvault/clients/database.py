import sqlite3

from smolvault.models import FileMetadata

# https://sqlmodel.tiangolo.com


class Database:
    def __init__(self) -> None:
        self.con = sqlite3.connect("file_metadata.db")
        self.create_table()

    def create_table(self) -> None:
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata
                (file_name TEXT NOT NULL PRIMARY KEY UNIQUE,
                object_key TEXT UNIQUE NOT NULL,
                file_sha256 TEXT NOT NULL,
                upload_timestamp INTEGER NOT NULL,
                tags TEXT,
                local_path TEXT,
                cache_timestamp INT,
                link TEXT)
                STRICT
        """)
        self.con.commit()

    def add_metadata(self, file_metadata: FileMetadata) -> None:
        self.con.execute(
            """
            INSERT INTO file_metadata
                (file_name, object_key, file_sha256, upload_timestamp, tags, local_path, cache_timestamp, link)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                file_metadata.file_name,
                file_metadata.object_key,
                file_metadata.file_sha256,
                file_metadata.upload_timestamp,
                file_metadata.tags,
                file_metadata.local_path,
                file_metadata.cache_timestamp,
                file_metadata.link,
            ),
        )
        self.con.commit()

    def list_all_metadata(self) -> list[FileMetadata]:
        cursor = self.con.execute("SELECT * FROM file_metadata")
        return [FileMetadata(*row) for row in cursor.fetchall()]
