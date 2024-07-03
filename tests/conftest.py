import os
from collections.abc import Generator
from typing import Any

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from smolvault.main import app


@pytest.fixture(scope="session")
def env_vars() -> dict[str, str]:
    return {
        "SMOLVAULT_DB": "test.db",
        "SMOLVAULT_BUCKET": "test-bucket",
    }


@pytest.fixture(scope="session")
def _aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"  # noqa: S105
    os.environ["AWS_SECURITY_TOKEN"] = "testing"  # noqa: S105
    os.environ["AWS_SESSION_TOKEN"] = "testing"  # noqa: S105
    os.environ["AWS_DEFAULT_REGION"] = "us-west-1"


@pytest.fixture()
def aws(_aws_credentials: None) -> Generator[S3Client, Any, None]:
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture()
def _test_bucket(aws: S3Client) -> None:
    client = boto3.client("s3")
    client.create_bucket(
        ACL="private", Bucket="test-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-1"}
    )
    client.get_waiter("bucket_exists").wait(Bucket="test-bucket")


@pytest.fixture()
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def camera_img() -> bytes:
    with open("tests/mock_data/camera.png", "rb") as f:
        return f.read()
