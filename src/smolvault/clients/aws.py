from typing import Any

import boto3

from smolvault.models import FileUploadDTO


class S3Client:
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.session = boto3.Session()
        self.client = self.session.client("s3")
        self.bucket = self.session.resource("s3").Bucket(bucket_name)

    def upload(self, data: FileUploadDTO) -> str:
        key = data.name
        self.bucket.put_object(Key=key, Body=data.content)
        return key

    def download(self, key: str) -> Any:
        response = self.client.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket_name, Key=key)
