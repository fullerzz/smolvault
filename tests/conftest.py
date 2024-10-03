import os
import pathlib
from collections.abc import Generator
from datetime import datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

import boto3
import pytest
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from polyfactory.pytest_plugin import register_fixture
from sqlmodel import SQLModel, create_engine

from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.main import app
from smolvault.models import FileMetadata

from .factories import UserFactory

user_factory_fixture = register_fixture(UserFactory, name="user_factory")


class TestDatabaseClient(DatabaseClient):
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///test.db", echo=False, connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(self.engine)


@pytest.fixture(scope="module")
def anyio_backend() -> Literal["asyncio"]:
    return "asyncio"


@pytest.fixture
def db_client() -> TestDatabaseClient:
    return TestDatabaseClient()


@pytest.fixture
def user(user_factory: UserFactory, db_client: TestDatabaseClient) -> tuple[str, str]:
    user = user_factory.build()
    db_client.add_user(user)
    return user.username, user.password.get_secret_value()


@pytest.fixture(scope="module")
def client() -> AsyncClient:
    app.dependency_overrides[DatabaseClient] = TestDatabaseClient
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest.fixture
async def access_token(client: AsyncClient, user: tuple[str, str]) -> str:
    username, password = user
    response = await client.post(
        "/token",
        data={"username": username, "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def _aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"  # noqa: S105
    os.environ["AWS_SECURITY_TOKEN"] = "testing"  # noqa: S105
    os.environ["AWS_SESSION_TOKEN"] = "testing"  # noqa: S105
    os.environ["AWS_DEFAULT_REGION"] = "us-west-1"


@pytest.fixture
def aws(_aws_credentials: None) -> Generator[S3Client, Any, None]:
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture
def _test_bucket(aws: S3Client) -> None:
    client = boto3.client("s3")
    client.create_bucket(
        ACL="private",
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "us-west-1"},
    )
    client.get_waiter("bucket_exists").wait(Bucket="test-bucket")


@pytest.fixture
def _bucket_w_camera_img(_test_bucket: None) -> None:
    client = boto3.client("s3")
    with pathlib.Path("tests/mock_data/camera.png").open("rb") as f:
        client.put_object(Bucket="test-bucket", Key="camera.png", Body=f.read())


@pytest.fixture(scope="session")
def camera_img() -> bytes:
    with pathlib.Path("tests/mock_data/camera.png").open("rb") as f:
        return f.read()


@pytest.fixture(scope="session")
def neon_gas_station_img() -> bytes:
    with pathlib.Path("tests/mock_data/neon vintage gas station.png").open("rb") as f:
        return f.read()


@pytest.fixture
def file_metadata_record() -> FileMetadataRecord:
    return FileMetadataRecord(
        file_name="camera.png",
        file_sha256="ddf2ef1fce9d6289051b8415d9b6ace81743288db15570179e409b3169055055",
        size=19467,
        object_key="camera.png",
        link="http://pi.local:8000/file/original?filename=camera.png",
        upload_timestamp=datetime.now(ZoneInfo("UTC")).isoformat(),
        tags="camera,photo",
    )


@pytest.fixture
def file_metadata(file_metadata_record: FileMetadataRecord) -> FileMetadata:
    return FileMetadata.model_validate(file_metadata_record.model_dump())
