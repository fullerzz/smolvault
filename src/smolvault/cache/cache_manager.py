import pathlib


class CacheManager:
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = pathlib.Path(cache_dir)

    def file_exists(self, filename: str) -> bool:
        file_path = self.cache_dir / filename
        return file_path.exists()

    def save_file(self, filename: str, data: bytes) -> str:
        file_path = self.cache_dir / filename
        with file_path.open("wb") as f:
            f.write(data)
        return file_path.as_posix()

    def delete_file(self, filename: str) -> None:
        file_path = self.cache_dir / filename
        if file_path.exists():
            file_path.unlink()
