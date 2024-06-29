from typing import Any

import aioboto3

from smolvault.models import FileUpload

session = aioboto3.Session()


class S3Client:
    def __init__(self, bucket: str) -> None:
        self.bucket: str = bucket

    async def upload(self, key: str, data: FileUpload) -> None:
        async with session.client("s3") as s3:
            await s3.put_object(Bucket=self.bucket, Key=key, Body=data)

    async def download(self, key: str) -> Any:
        async with session.client("s3") as s3:
            response = await s3.get_object(Bucket=self.bucket, Key=key)
            return await response["Body"].read()
