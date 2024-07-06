import logging
from typing import Any

import boto3

from smolvault.config import get_settings
from smolvault.models import FileUploadDTO

logging.basicConfig(
    level=logging.INFO, filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self, bucket_name: str) -> None:
        logger.debug(f"Creating S3 client for bucket {bucket_name}")
        self.settings = get_settings()
        self.bucket_name = bucket_name
        self.session = boto3.Session()
        self.client = self.session.client("s3")
        self.bucket = self.session.resource("s3").Bucket(bucket_name)

    def upload(self, data: FileUploadDTO) -> str:
        logger.debug(f"Uploading file {data.name} to S3")
        key = data.name
        self.bucket.put_object(Key=key, Body=data.content)
        return key

    def download(self, key: str) -> Any:
        logger.debug(f"Downloading file {key} from S3")
        response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        logger.info("File downloaded successfully")
        return response["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket_name, Key=key)
        logger.info(f"Deleted file {key} from S3")
