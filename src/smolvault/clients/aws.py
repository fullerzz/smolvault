from typing import Any

import aioboto3

from smolvault.models import FileUploadDTO


class S3Client:
    def __init__(self, bucket: str) -> None:
        self.session = aioboto3.Session()
        self.bucket: str = bucket

    async def upload(self, data: FileUploadDTO) -> str:
        async with self.session.client("s3") as s3:
            key = data.name
            await s3.put_object(Bucket=self.bucket, Key=key, Body=data.content)
            return key

    async def download(self, key: str) -> Any:
        async with self.session.client("s3") as s3:
            response = await s3.get_object(Bucket=self.bucket, Key=key)
            return await response["Body"].read()
