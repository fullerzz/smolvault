import logging
import pathlib

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        logger.info("Created CacheManager with cache directory %s", self.cache_dir)

    def file_exists(self, filename: str) -> bool:
        file_path = self.cache_dir / filename
        return file_path.exists()

    def save_file(self, filename: str, data: bytes) -> str:
        file_path = self.cache_dir / filename
        with file_path.open("wb") as f:
            f.write(data)
        return file_path.as_posix()

    def delete_file(self, local_path: str) -> None:
        file_path = pathlib.Path(local_path)
        file_path.unlink(missing_ok=True)
