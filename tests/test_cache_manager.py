from pathlib import Path

from smolvault.cache.cache_manager import CacheManager


def test_create_cache_manager_dir_not_exists(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    assert cache_dir.exists() is False
    cache_mgr = CacheManager(cache_dir.as_posix())
    assert cache_mgr.cache_dir == cache_dir
    assert cache_mgr.cache_dir.exists()


def test_create_cache_manager_dir__exists(tmp_path: Path) -> None:
    cache_dir = tmp_path / "existing_cache"
    cache_dir.mkdir()
    cache_mgr = CacheManager(cache_dir.as_posix())
    assert cache_mgr.cache_dir == cache_dir
