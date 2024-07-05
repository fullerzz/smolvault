import os


class CacheManager:
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = cache_dir

    def file_exists(self, filename: str) -> bool:
        return os.path.exists(os.path.join(self.cache_dir, filename))

    def save_file(self, filename: str, data: bytes) -> str:
        file_path = os.path.join(self.cache_dir, filename)
        with open(file_path, "wb") as f:
            f.write(data)
        return file_path
